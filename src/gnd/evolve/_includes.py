"""Ownership and authenticated evolution history; resolution stays in model."""
from __future__ import annotations

from collections import Counter
from collections.abc import Mapping, Sequence

from gnd.documents import Model
from gnd.model._includes import parse_declarations
from gnd.model_index import ModelIndex

from .models import (
    ConstraintLocator,
    ElementLocator,
    EvolutionOperation,
    EvolutionProposal,
    IncludeLocator,
    IncludeSnapshot,
    RoleLocator,
    canonical_sha256,
)


class IncludeInputError(Exception):
    """An include evolution input, rather than a stale model CAS, was refused."""


def enforce_ownership(model, document, operations) -> None:
    if not isinstance(model, Model) or not isinstance(document, Mapping) or not isinstance(operations, (list, tuple)):
        raise IncludeInputError('invalid include ownership input')
    if not model.includes:
        return
    declared = parse_declarations(document)
    if [(e['id'], e['path'], e['sha256']) for e in declared] != [
            (e.id, e.path, e.sha256) for e in model._included]:
        raise IncludeInputError('include:unresolved')
    origins = {entry.composed_address: entry for entry in model._provenance}
    readonly = {entry.element_id for entry in origins.values()
                if entry.origin != 'model' and isinstance(entry.element_id, str)}
    index = ModelIndex.for_model(model)
    fact_positions = {row['id']: i for i, row in enumerate(index.iter_fact_types_shared())}
    hosts = {identifier for identifier, position in fact_positions.items()
             if origins[f'$.fact_types[{position}]'].origin != 'model'}
    occurrences, positions, constraints = Counter(), Counter(), set()
    repinning = any(isinstance(item, EvolutionOperation) and isinstance(item.locator, IncludeLocator)
                    for item in operations)
    for _, constraint, fact in index.iter_constraints_shared():
        host = fact['id'] if fact else None
        position = positions[host]
        positions[host] += 1
        address = (f'$.fact_types[{fact_positions[host]}].constraints[{position}]' if fact else
                   f'$.constraints[{position}]')
        key = (host, constraint.get('type'), canonical_sha256(constraint))
        occurrence = occurrences[key]
        occurrences[key] += 1
        if origins[address].origin != 'model':
            constraints.add((*key, occurrence))
    for operation in operations:
        if not isinstance(operation, EvolutionOperation):
            raise IncludeInputError('invalid include ownership operation')
        locator = operation.locator
        if isinstance(locator, IncludeLocator):
            continue
        target = (locator.element_id if isinstance(locator, ElementLocator) else
                  locator.fact_type_id if isinstance(locator, RoleLocator) else None)
        denied = target in readonly
        if isinstance(locator, ConstraintLocator):
            denied = (locator.host == 'fact_type' and locator.host_id in hosts or
                      (locator.host_id, locator.family, locator.canonical_before_sha256,
                       locator.duplicate_occurrence) in constraints)
            if locator.host == 'included_fact_type':
                if locator.host_id not in hosts and not repinning:
                    raise IncludeInputError('invalid owned attachment host')
                denied = False  # This locator resolves only authored attachments in replay.
        after_id = operation.after.get('id') if isinstance(operation.after, Mapping) else None
        if denied or isinstance(after_id, str) and after_id in readonly:
            raise IncludeInputError('evolve:included-element: ' + operation.reference())


_AUTHOR_FIELDS = frozenset({'provenance', 'description', 'rationale', 'remedy', 'source', 'status', 'modality'})
_SURFACES = {'object_types': 'object-type', 'fact_types': 'fact-type', 'constraints': 'constraint',
             'operations': 'operation', 'reference_populations': 'identifier-reference',
             'fact_type_constraints': 'constraint'}


def owned_impact(document, changed_ids: frozenset[str], *, all_roots=False) -> tuple:
    """Conservative semantic dependencies, with one iterative policy for every owned root."""
    if not isinstance(document, Mapping) or not isinstance(changed_ids, frozenset):
        raise IncludeInputError('invalid include impact input')
    roots = []
    for section, surface in _SURFACES.items():
        entries = document.get(section, [])
        if not isinstance(entries, (list, tuple)):
            raise IncludeInputError('invalid include impact section')
        for i, entry in enumerate(entries):
            if not isinstance(entry, Mapping):
                raise IncludeInputError('invalid include impact element')
            reference = f"{section}[{entry.get('id', i)}]"
            if section != 'fact_type_constraints':
                roots.append((reference, surface, entry, None))
            if section in {'fact_types', 'fact_type_constraints'}:
                host = entry.get('id') if section == 'fact_types' else entry.get('fact_type')
                constraints = entry.get('constraints', [])
                if not isinstance(constraints, (list, tuple)):
                    raise IncludeInputError('invalid include impact constraints')
                for j, constraint in enumerate(constraints):
                    if not isinstance(constraint, Mapping):
                        raise IncludeInputError('invalid include impact constraint')
                    identifier = constraint.get('id')
                    name = (f'owned_constraints[{identifier}]' if isinstance(identifier, str) else
                            f'$.{section}[{i}].constraints[{j}]')
                    roots.append((name, 'constraint', {'host': host, 'constraint': constraint}, host))
    if all_roots:
        return tuple((reference, surface, value) for reference, surface, value, _ in roots)
    affected = []
    for reference, surface, value, host in roots:
        stack, seen = [value], set()
        touched = isinstance(host, str) and host in changed_ids
        while stack:
            item = stack.pop()
            if isinstance(item, str):
                touched |= item in changed_ids
            elif isinstance(item, (Mapping, list, tuple)) and id(item) not in seen:
                seen.add(id(item))
                if isinstance(item, Mapping):
                    stack.extend(v for k, v in item.items() if k not in _AUTHOR_FIELDS)
                else:
                    stack.extend(item)
        if touched:
            affected.append((reference, surface, value))
    return tuple(affected)


def include_snapshots(model) -> tuple[IncludeSnapshot, ...]:
    from .models import CommittedText

    if not isinstance(model, Model):
        raise IncludeInputError('invalid include snapshot model')
    return tuple(IncludeSnapshot(id=e.id, path=e.path, sha256=e.sha256,
                                 content=CommittedText.from_text(e.raw.decode('utf-8'),
                                                                media_type='application/yaml'))
                 for e in model._included)


def historical_bytes(proposal, snapshots) -> dict[str, bytes]:
    if not isinstance(proposal, EvolutionProposal) or not isinstance(snapshots, (list, tuple, type(None))):
        raise IncludeInputError('invalid historical include input')
    selected = {operation.locator.include_id for operation in proposal.operations
                if isinstance(operation.locator, IncludeLocator)}
    values = {}
    for snapshot in snapshots or ():
        if not isinstance(snapshot, IncludeSnapshot):
            raise IncludeInputError('invalid historical include snapshot')
        if snapshot.id in selected:
            if snapshot.id in values:
                raise IncludeInputError('invalid duplicate historical include')
            values[snapshot.id] = snapshot.content.text.encode('utf-8')
    if set(values) != selected:
        raise IncludeInputError('invalid missing historical include')
    return values


def previous_bindings(document, bindings: Sequence[str]) -> dict[str, str]:
    declarations = parse_declarations(document)
    if not isinstance(bindings, (list, tuple)) or len(bindings) > 8:
        raise IncludeInputError('invalid previous include bindings')
    identifiers = sorted((e['id'] for e in declarations), key=len, reverse=True)
    values = {}
    for binding in bindings:
        if not isinstance(binding, str):
            raise IncludeInputError('invalid previous include binding')
        identifier = next((i for i in identifiers if binding.startswith(i + '=')), None)
        if identifier is None or identifier in values or not binding[len(identifier) + 1:]:
            raise IncludeInputError('invalid previous include binding')
        values[identifier] = binding[len(identifier) + 1:]
    return values


class AttachmentReplay:
    """Index authored attachment constraints once; materialize deletions only at the end."""

    def __init__(self, document):
        from collections import defaultdict

        if not isinstance(document, dict) or not isinstance(document.get('fact_type_constraints', []), list):
            raise IncludeInputError('invalid attachment replay input')
        self.document, self.rows, self.groups, self.hosts = document, [], defaultdict(list), defaultdict(list)
        self.deleted = object()
        for entry in document.get('fact_type_constraints', []):
            if not isinstance(entry, dict) or not isinstance(entry.get('constraints'), list):
                raise IncludeInputError('invalid attachment replay entry')
            ordinal = self._row(entry)
            for slot, item in enumerate(entry['constraints']):
                if not isinstance(item, dict):
                    raise IncludeInputError('invalid attachment replay constraint')
                self.groups[(entry['fact_type'], item.get('type'), canonical_sha256(item))].append((ordinal, slot))

    def _row(self, entry):
        host = entry.get('fact_type')
        if not isinstance(host, str):
            raise IncludeInputError('invalid attachment replay host')
        ordinal = len(self.rows)
        self.rows.append([entry, len(entry['constraints'])])
        self.hosts[host].append(ordinal)
        return ordinal

    def apply(self, operation):
        from bisect import insort

        from .models import EvolutionOperationKind

        if not isinstance(operation, EvolutionOperation) or not isinstance(operation.locator, ConstraintLocator):
            raise IncludeInputError('invalid attachment replay operation')
        locator, kind = operation.locator, operation.kind
        if locator.host != 'included_fact_type' or kind not in {
                EvolutionOperationKind.ADD, EvolutionOperationKind.MODIFY, EvolutionOperationKind.DELETE}:
            raise IncludeInputError('invalid attachment replay operation')
        dumped = operation.model_dump(mode='json')
        host, family = locator.host_id, locator.family
        if kind is EvolutionOperationKind.ADD:
            if self.groups[(host, family, operation.after_sha256)]:
                raise IncludeInputError('add target owned attachment already exists')
            active = self.hosts[host]
            while active and not self.rows[active[-1]][1]:
                active.pop()
            if not active:
                entry = {'fact_type': host, 'constraints': []}
                self.document.setdefault('fact_type_constraints', []).append(entry)
                self._row(entry)
            ordinal = self.hosts[host][-1]
            entry = self.rows[ordinal][0]
            slot = len(entry['constraints'])
            entry['constraints'].append(dumped['after'])
            self.rows[ordinal][1] += 1
        else:
            group = self.groups[(host, family, locator.canonical_before_sha256)]
            if locator.duplicate_occurrence >= len(group):
                raise IncludeInputError('stable locator has no owned attachment occurrence')
            ordinal, slot = group.pop(locator.duplicate_occurrence)
            entry = self.rows[ordinal][0]
            if entry['constraints'][slot] != dumped['before']:
                raise IncludeInputError('declared before value differs from owned attachment')
            if kind is EvolutionOperationKind.DELETE:
                entry['constraints'][slot] = self.deleted
                self.rows[ordinal][1] -= 1
                return None
            entry['constraints'][slot] = dumped['after']
        insort(self.groups[(host, family, operation.after_sha256)], (ordinal, slot))
        return entry['constraints'], entry['constraints'][slot]

    def finish(self):
        entries = []
        for entry, count in self.rows:
            if count:
                entry['constraints'][:] = [item for item in entry['constraints'] if item is not self.deleted]
                entries.append(entry)
        if entries:
            self.document['fact_type_constraints'] = entries
        else:
            self.document.pop('fact_type_constraints', None)


def included_delta(before, candidate) -> frozenset[str]:
    from gnd.model._includes import _ids

    def inventory(document, origins):
        by_address = {origin.composed_address: origin for origin in origins}
        result = {}
        for address, value in _ids(document):
            origin = by_address[address]
            if origin.origin != 'model':
                result[(origin.origin, origin.element_id or origin.original_address)] = (origin, value)
        return result

    old = inventory(before.model_dump(exclude={'warnings'}), before._provenance)
    new = inventory(candidate.document, candidate.origins)
    changed = set()
    semantic_ids = {origin.element_id for origin, _ in [*old.values(), *new.values()]
                    if isinstance(origin.element_id, str)}
    for key in old.keys() | new.keys():
        left, right = old.get(key), new.get(key)
        if left is not None and right is not None and left[1] == right[1]:
            continue
        for origin, value in (entry for entry in (left, right) if entry is not None):
            if isinstance(origin.element_id, str):
                changed.add(origin.element_id)
            if origin.original_address.startswith('$.constraints['):
                stack = [value]
                while stack:
                    item = stack.pop()
                    if isinstance(item, str) and item in semantic_ids:
                        changed.add(item)
                    elif isinstance(item, Mapping):
                        stack.extend(v for k, v in item.items() if k not in _AUTHOR_FIELDS)
                    elif isinstance(item, (list, tuple)):
                        stack.extend(item)
    return frozenset(changed)


def augment_radius(radius, proposal, before, candidate, changed_ids):
    from .models import BlastRadiusEntry, BlastRadiusReport

    entries = {entry.reference: entry for entry in radius.entries}
    operations = tuple(sorted(operation.operation_id for operation in proposal.operations))
    old = {ref: (surface, value) for ref, surface, value in owned_impact(before, changed_ids, all_roots=True)}
    new = {ref: (surface, value) for ref, surface, value in owned_impact(candidate, changed_ids, all_roots=True)}
    affected = {ref for doc in (before, candidate) for ref, _, _ in owned_impact(doc, changed_ids)}
    for operation in proposal.operations:
        if isinstance(operation.locator, IncludeLocator):
            reference = operation.reference()
            old[reference], new[reference] = ('model', operation.before), ('model', operation.after)
            affected.add(reference)
    for reference in affected:
        left, right = old.get(reference), new.get(reference)
        before_sha = canonical_sha256(left[1]) if left is not None else None
        after_sha = canonical_sha256(right[1]) if right is not None else None
        change = ('added' if left is None else 'deleted' if right is None else
                  'modified' if before_sha != after_sha else 'affected')
        entries[reference] = BlastRadiusEntry(
            surface=(left or right)[0], reference=reference, change=change, operation_ids=operations,
            before_sha256=before_sha, after_sha256=after_sha)
    body = radius.model_dump(mode='json', exclude={'entries', 'report_sha256'})
    body['entries'] = [entry.model_dump(mode='json') for entry in sorted(entries.values(),
                                                                       key=lambda e: (e.reference, e.surface))]
    return BlastRadiusReport(**body, report_sha256=canonical_sha256(body))


def provided_history(proposal, values):
    if values is None:
        return None
    if not isinstance(values, Mapping) or len(values) > 8:
        raise IncludeInputError('invalid previous include bytes')
    selected = {operation.locator.include_id for operation in proposal.operations
                if isinstance(operation.locator, IncludeLocator)}
    if set(values) - selected or any(not isinstance(raw, bytes) for raw in values.values()):
        raise IncludeInputError('invalid previous include bytes')
    return dict(values) or None


def exclude_input_outputs(model_path, declarations, outputs):
    """Refuse declared dependency spellings and existing aliases before writing."""
    import os
    from pathlib import Path

    inputs = {Path(model_path).parent / entry.path for entry in declarations}
    identities = set()
    for source in inputs:
        try:
            info = source.stat()
        except FileNotFoundError:
            continue
        identities.add((info.st_dev, info.st_ino))
    resolved = {source.resolve() for source in inputs}
    for output in outputs:
        if output.resolve() in resolved:
            raise IncludeInputError('include input is a publication destination')
        try:
            info = os.stat(output)
        except FileNotFoundError:
            continue
        if (info.st_dev, info.st_ino) in identities:
            raise IncludeInputError('include input aliases a publication destination')


def included_hosts(model):
    """Verified included fact-type identities for replay and proposal writers."""
    return frozenset(entry.element_id for entry in model._provenance
                     if entry.origin != 'model' and entry.composed_address.startswith('$.fact_types[')
                     and entry.composed_address.count('[') == 1)
