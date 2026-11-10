"""One resolver and admission guards for pinned version-5 model includes."""
from __future__ import annotations

import copy
import hashlib
import re
from collections.abc import Mapping
from pathlib import Path
from typing import Any, NoReturn

from ruamel.yaml.error import YAMLError

from gnd import artifacts
from gnd.documents import ElementOrigin, IncludedFile
from gnd.errors import ModelLoadError, ModelValidationError, ReferenceInputError, ValidationIssue
from gnd.model._paths import _relative
from gnd.model._validation import (
    ID_SECTIONS,
    MAX_MODEL_BYTES,
    _layer1_structural,
    parse_model_document,
    semantic_validate,
)

REASONS = ('include:declaration', 'include:path', 'include:unreadable',
           'include:size', 'include:hash-mismatch', 'include:parse',
           'include:forbidden-section', 'include:invalid-included-model',
           'include:unknown-target', 'include:collision', 'include:unresolved',
           'include:unsupported-route')
Declarations = list[dict[str, Any]]
SECTIONS = (*ID_SECTIONS[:2], 'constraints', 'deontic_notes')


def _refuse(reason, path='$', detail='') -> NoReturn:
    code = 'include:' + reason
    raise ModelValidationError([ValidationIssue(
        path=path, message=code + (': ' + detail if detail else ''), rule_id=code)])


def refuse_unresolved() -> NoReturn:
    """Refuse a consumer's include Model without matching resolver metadata."""
    _refuse('unresolved')


def declares_includes(document: object) -> bool:
    return isinstance(document, Mapping) and any(
        key in document for key in ('includes', 'fact_type_constraints'))


def parse_declarations(document: object) -> Declarations:
    if not isinstance(document, Mapping) or document.get('version') != 5:
        _refuse('declaration')
    entries = document.get('includes')
    if not isinstance(entries, list) or not 1 <= len(entries) <= 8:
        _refuse('declaration', '$.includes')
    ids = set()
    for i, entry in enumerate(entries):
        path = f'$.includes[{i}]'
        if not isinstance(entry, Mapping) or set(entry) != {'id', 'path', 'sha256'}:
            _refuse('declaration', path)
        identifier, relative, digest = (entry[k] for k in ('id', 'path', 'sha256'))
        if (not isinstance(identifier, str) or not 1 <= len(identifier) <= 128
                or identifier in ids or not isinstance(relative, str)
                or not 1 <= len(relative) <= 4096 or not isinstance(digest, str)
                or not re.fullmatch('[0-9a-f]{64}', digest)):
            _refuse('declaration', path)
        ids.add(identifier)
    if 'fact_type_constraints' in document:
        attached = document['fact_type_constraints']
        if not isinstance(attached, list) or not attached:
            _refuse('declaration', '$.fact_type_constraints')
        for i, entry in enumerate(attached):
            if (not isinstance(entry, Mapping) or set(entry) != {'fact_type', 'constraints'}
                    or not isinstance(entry['fact_type'], str) or not entry['fact_type']
                    or not isinstance(entry['constraints'], list) or not entry['constraints']):
                _refuse('declaration', f'$.fact_type_constraints[{i}]')
    return entries


def parse_included(raw: bytes, *, include_id: str, path: str) -> dict:
    try:
        doc = parse_model_document(raw, source=path)
        if isinstance(doc, dict):
            return doc
    except (ModelLoadError, UnicodeError, ValueError, TypeError, RecursionError, YAMLError):
        pass
    _refuse('parse', f'includes[{include_id}]')


def _structural(document):
    try:
        return _layer1_structural(document)
    except (TypeError, ValueError, RecursionError):
        _refuse('declaration')



def _clone(value):
    try:
        return copy.deepcopy(value)
    except RecursionError:
        _refuse('declaration', detail='container depth refused during composition')


def include_reason(error) -> str | None:
    return next((i.rule_id for i in error.issues if i.rule_id.startswith('include:')), None)

def _ids(document):
    """One shared id-bearing-kind walk, including anonymous constraint origins."""
    for section in (*ID_SECTIONS, 'constraints', 'deontic_notes'):
        for i, element in enumerate(document.get(section, [])):
            address = f'$.{section}[{i}]'
            yield address, element
            if section == 'fact_types':
                for j, constraint in enumerate(element.get('constraints', [])):
                    yield f'{address}.constraints[{j}]', constraint


def _merge(document, included, declarations):
    result = _clone(dict(document))
    origins = {address: ElementOrigin('model', address, address, element.get('id'))
               for address, element in _ids(document)}
    targets = {}
    for entry, doc in zip(declarations, included, strict=True):
        offsets = {section: len(result.get(section, [])) for section in SECTIONS}
        for section in SECTIONS:
            result.setdefault(section, []).extend(_clone(doc.get(section, [])))
        for address, element in _ids(doc):
            match = re.match(r'^\$\.([a-z_]+)\[(\d+)\](.*)$', address)
            section, index, rest = match.groups()
            composed = f'$.{section}[{int(index) + offsets[section]}]{rest}'
            origins[composed] = ElementOrigin(f"includes[{entry['id']}]", composed, address, element.get('id'))
        for i, ft in enumerate(doc.get('fact_types', [])):
            targets[ft['id']] = i + offsets['fact_types']
    result.setdefault('object_types', [])
    result.setdefault('fact_types', [])
    for i, attachment in enumerate(document.get('fact_type_constraints', [])):
        target = targets.get(attachment['fact_type'])
        if target is None:
            _refuse('unknown-target', f'$.fact_type_constraints[{i}]')
        constraints = result['fact_types'][target].setdefault('constraints', [])
        for j, constraint in enumerate(attachment['constraints']):
            address = f'$.fact_types[{target}].constraints[{len(constraints)}]'
            origins[address] = ElementOrigin('model', address,
                f'$.fact_type_constraints[{i}].constraints[{j}]', constraint.get('id'))
            constraints.append(_clone(constraint))
    seen = {}
    for address, element in _ids(result):
        identifier = element.get('id')
        if identifier is not None:
            if identifier in seen:
                prior = origins[seen[identifier]]
                current = origins[address]
                _refuse('collision', current.original_address,
                        f'{prior.origin} and {current.origin}; {address.split("[")[0]}')
            seen[identifier] = address
    return result, tuple(origins.values())


def compose(document: object, *, descriptor: int, source: str | Path):
    declarations = parse_declarations(document)
    if issues := _structural(document):
        raise ModelValidationError(issues)
    for i, entry in enumerate(declarations):
        try:
            _relative(entry['path'])
        except ReferenceInputError:
            _refuse('path', f'$.includes[{i}]')
    buffers, total = [], 0
    for i, entry in enumerate(declarations):
        path = entry['path']
        try:
            raw, _ = artifacts.read_regular_bounded_at(descriptor, path, max_bytes=MAX_MODEL_BYTES)
        except (OSError, artifacts.ArtifactError) as error:
            # Exact legacy bounded-reader spellings; no exception class changes.
            growth = f'artifact {path} grew over the {MAX_MODEL_BYTES}-byte cap'
            oversize = re.escape(f'artifact {path} is ') + rf'\d+ bytes, over the {MAX_MODEL_BYTES}-byte cap'
            size = str(error) == growth or re.fullmatch(oversize, str(error))
            _refuse('size' if size else 'unreadable', f'$.includes[{i}]')
        total += len(raw)
        if total > 32 * 1024 * 1024:
            _refuse('size', f'$.includes[{i}]')
        buffers.append(raw)
    for i, (entry, raw) in enumerate(zip(declarations, buffers, strict=True)):
        if hashlib.sha256(raw).hexdigest() != entry['sha256']:
            _refuse('hash-mismatch', f'$.includes[{i}]')
    included = [parse_included(raw, include_id=entry['id'], path=entry['path'])
                for entry, raw in zip(declarations, buffers, strict=True)]
    forbidden = ('includes', 'reference_populations', 'operations',
                 'rejected_proposals', 'fact_type_constraints')
    for entry, doc in zip(declarations, included, strict=True):
        source_doc = doc.get('source')
        if any(key in doc for key in forbidden) or (
                isinstance(source_doc, Mapping) and source_doc.get('mode') == 'unattended'):
            _refuse('forbidden-section', f'includes[{entry["id"]}]')
    for entry, doc in zip(declarations, included, strict=True):
        issues = _structural(doc)
        if not issues:
            issues = [i for i in semantic_validate(doc) if i.severity == 'error']
        if doc.get('version') not in (1, 2, 3, 4) or issues:
            detail = f'{issues[0].rule_id} at {issues[0].path}' if issues else 'version'
            _refuse('invalid-included-model', f'includes[{entry["id"]}]', detail)
    result, origins = _merge(document, included, declarations)
    metadata = tuple(IncludedFile(entry['id'], entry['path'], entry['sha256'],
                      doc['version'], doc.get('model_id'), _clone(doc.get('source')))
                     for entry, doc in zip(declarations, included, strict=True))
    return result, origins, metadata


def remap_issues(issues, origins):
    addresses = {entry.composed_address: entry for entry in origins}
    selectors = {entry.element_id: entry.composed_address for entry in origins
                 if re.fullmatch(r'\$\.fact_types\[\d+\]', entry.composed_address)}
    result = []
    for issue in issues:
        path = issue.path
        selector = re.match(r'^\$\.fact_types\[id=(.*?)\]', path)
        if selector and selector[1] in selectors:
            path = selectors[selector[1]] + path[selector.end():]
        candidates = re.findall(r'\$\.[a-z_]+\[\d+\](?:\.constraints\[\d+\])?', path)
        address = candidates[0] if candidates else ''
        entry = addresses.get(address)
        if entry is None and '.constraints[' in address:
            address = address.split('.constraints[')[0]
            entry = addresses.get(address)
        if entry is not None:
            if entry.origin == 'model' and entry.original_address == entry.composed_address:
                result.append(issue)
                continue
            prefix = '' if entry.origin == 'model' else entry.origin + ':'
            original = entry.original_address
            if selector and entry.origin != 'model':
                original = re.sub(r'^\$\.fact_types\[\d+\]',
                                  lambda _, selector=selector: f'$.fact_types[id={selector[1]}]', original)
            path = prefix + original + path[len(address):]
            issue = issue.model_copy(update={'path': path})
        result.append(issue)
    return result


def refuse_unsupported(route: str) -> NoReturn:
    _refuse('unsupported-route', detail=route)


def guard_document(document, route):
    if declares_includes(document):
        refuse_unsupported(route)


def guard_bytes(raw, *, source, route):
    if not isinstance(raw, (bytes, bytearray)):
        return
    try:
        doc = parse_model_document(raw, source=source)
    except (ModelLoadError, UnicodeError, ValueError, TypeError, RecursionError, YAMLError):
        return  # Original route retains its include-free malformed-input refusal.
    guard_document(doc, route)


def guard_path(path, route):
    try:
        with Path(path).open('rb') as handle:
            raw = handle.read(MAX_MODEL_BYTES + 1)
    except OSError:
        return  # Original route retains its missing/unreadable-input refusal.
    guard_bytes(raw, source=path, route=route)
