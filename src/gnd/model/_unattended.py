"""MG5 unattended source mode (model-growth-guardrails milestone).

A separate home inside the ``gnd.model`` package so ``_validation`` stays under
its RF6 size ceiling. ``_rule_unattended`` is registered last in
``gnd.model._validation._SEMANTIC_RULES`` and ``unattended_span_issues`` is
re-exported by ``gnd.model``. ``_validation`` registers its constraint and
provenance walks here at import time, so this module never imports
``_validation`` back.

One rule family, one walk (MG-R2). Gated on ``source.mode: unattended``, so no
model without the mode gains or loses an issue (MG-R1). The rule table is
normative in gnd-orm-core/references/representation-format.md ("Unattended
source").
"""

from __future__ import annotations

import hashlib
import re
from collections.abc import Callable, Iterator, Mapping
from typing import Any

from gnd.errors import ValidationIssue

#: The shared walks and the element label, registered by
#: ``gnd.model._validation`` once they are defined. This home never imports
#: ``_validation``: even a per-call import is a runtime edge, and the two
#: would form the cycle the RF8 graph check forbids.
_constraint_walk: Callable[[dict[str, Any]], Iterator[tuple[str, dict[str, Any]]]] | None = None
_provenance_walk: Callable[[dict[str, Any]], Iterator[tuple[str, dict[str, Any]]]] | None = None
_provenance_label: Callable[[dict[str, Any]], str] | None = None


def _iter_constraints(doc: dict[str, Any]):
    if _constraint_walk is None:
        raise RuntimeError("gnd.model._validation has not registered the constraint walk")
    return _constraint_walk(doc)


def _iter_provenance_bearing(doc: dict[str, Any]):
    if _provenance_walk is None:
        raise RuntimeError("gnd.model._validation has not registered the provenance walk")
    return _provenance_walk(doc)


def _provenance_bearing_label(element: dict[str, Any]) -> str:
    if _provenance_label is None:
        raise RuntimeError("gnd.model._validation has not registered the provenance label")
    return _provenance_label(element)


UNATTENDED_MODE = "unattended"
_SHA256_HEX = re.compile(r"[0-9a-f]{64}")  # always fullmatch: `$` admits a trailing newline (review R-F1)
_SPAN_KEYS = frozenset({"document_sha256", "start", "end", "excerpt_sha256"})
_UNATTENDED_SPANLESS_SOURCE = "common-sense"
_UNATTENDED_ALETHIC_SOURCES = ("sample", "llm-inferred", "common-sense", "induced")


def _unattended_source(doc: dict[str, Any]) -> dict[str, Any] | None:
    source = doc.get("source")
    if isinstance(source, Mapping) and source.get("mode") == UNATTENDED_MODE:
        return dict(source)
    return None


def _listed(value: Any) -> list[Any]:
    """A collection the rule may walk: a list, else nothing (review R-F14)."""
    return value if isinstance(value, list) else []


def _is_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _declared_documents(source: dict[str, Any], issues: list[ValidationIssue], *, rule_id: str) -> set[str]:
    def issue(path: str, message: str) -> None:
        issues.append(ValidationIssue(path=path, message=message, rule_id=rule_id))

    if source.get("reviewer") != "none":
        issue("$.source.reviewer", "an unattended model must declare reviewer: none")
    documents = source.get("documents")
    declared: set[str] = set()
    if not isinstance(documents, list) or not documents:
        issue("$.source.documents", "an unattended model must declare at least one source document")
        return declared
    for index, entry in enumerate(documents):
        if (
            isinstance(entry, Mapping)
            and set(entry) == {"sha256", "label"}
            and isinstance(entry.get("sha256"), str)
            and _SHA256_HEX.fullmatch(entry["sha256"])
            and isinstance(entry.get("label"), str)
            and entry["label"].strip()
        ):
            declared.add(entry["sha256"])
        else:
            issue(f"$.source.documents[{index}]",
                  "a source document is {sha256: 64 lowercase hex, label: non-empty string}, nothing else")
    return declared


def _span_issue(span: Any, path: str, declared: set[str], *, rule_id: str) -> ValidationIssue | None:
    if not isinstance(span, Mapping) or set(span) != _SPAN_KEYS:
        reason = "a span is {document_sha256, start, end, excerpt_sha256}, nothing else"
    elif not all(isinstance(span[key], str) and _SHA256_HEX.fullmatch(span[key])
                 for key in ("document_sha256", "excerpt_sha256")):
        reason = "span digests are 64 lowercase hex"
    elif not (_is_int(span["start"]) and _is_int(span["end"])):
        reason = "span offsets are integers"
    elif not 0 <= span["start"] < span["end"]:
        reason = "a span needs 0 <= start < end"
    elif span["document_sha256"] not in declared:
        reason = "the span names a document the source does not declare"
    else:
        return None
    return ValidationIssue(path=path, message=reason, rule_id=rule_id)


def _require_spans(owner: Any, path: str, label: str, declared: set[str], issues: list[ValidationIssue], *,
                   rule_id: str, span_rule_id: str) -> None:
    provenance = owner.get("provenance") if isinstance(owner, Mapping) else None
    spans = provenance.get("spans") if isinstance(provenance, Mapping) else None
    if not isinstance(spans, list) or not spans:
        issues.append(ValidationIssue(path=path, message=f"{label} cites no source span (provenance.spans)",
                                      rule_id=rule_id))
        return
    for index, span in enumerate(spans):
        found = _span_issue(span, f"{path}.provenance.spans[{index}]", declared, rule_id=span_rule_id)
        if found is not None:
            issues.append(found)


def _sample_span_issues(fact_type: dict[str, Any], path: str, declared: set[str], issues: list[ValidationIssue], *,
                        rule_id: str, span_rule_id: str) -> None:
    rows = fact_type.get("sample_population")
    count = len(rows) if isinstance(rows, list) else 0
    provenance = fact_type.get("provenance")
    entries = provenance.get("sample_spans") if isinstance(provenance, Mapping) else None
    target = f"{path}.provenance.sample_spans"
    if not count and entries is None:
        return
    if not isinstance(entries, list):
        issues.append(ValidationIssue(path=target, message="sample rows cite no source spans (provenance.sample_spans)",
                                      rule_id=rule_id))
        return
    covered: set[int] = set()
    for index, entry in enumerate(entries):
        row = entry.get("row") if isinstance(entry, Mapping) else None
        if not isinstance(entry, Mapping) or set(entry) != {"row", "span"} or not _is_int(row):
            issues.append(ValidationIssue(path=f"{target}[{index}]", message="a sample span is {row: integer, span}",
                                          rule_id=rule_id))
            continue
        if row in covered or not 0 <= row < count:
            issues.append(ValidationIssue(
                path=f"{target}[{index}].row", message=f"sample span row {row} is repeated or names no sample row",
                rule_id=rule_id))
        covered.add(row)
        found = _span_issue(entry.get("span"), f"{target}[{index}].span", declared, rule_id=span_rule_id)
        if found is not None:
            issues.append(found)
    missing = sorted(set(range(count)) - covered)
    if missing:
        issues.append(ValidationIssue(
            path=target, message=f"sample rows {missing} cite no source span", rule_id=rule_id))


def _rule_unattended(doc: dict[str, Any]) -> list[ValidationIssue]:
    """MG5: the unattended source mode, U1..U8, one walk; nothing without the mode."""
    source = _unattended_source(doc)
    raw = doc.get("source")
    mode = raw.get("mode") if isinstance(raw, Mapping) else None
    if source is None:
        # Close review R3-1: a near-miss spelling would silently switch the
        # family off; say so (a warning: the mode is not declared).
        near_miss = [
            ValidationIssue(path="$.source.mode", rule_id="semantic:unattended-u1", severity="warning",
                            message=f"source.mode {mode!r} is not 'unattended'; the unattended rules do not apply")
        ] if isinstance(mode, str) and mode.strip().casefold() == UNATTENDED_MODE else []
        # The schema admits `spans` on the otherwise closed induced provenance
        # only for this mode; outside it the key stays refused, as before MG5
        # (close review R4-F1: no MG-R1 exception).
        return near_miss + [
            ValidationIssue(path=f"{path}.provenance.spans", rule_id="semantic:unattended-u7",
                            message="provenance.spans on an induced constraint requires source.mode: unattended")
            for path, constraint in _iter_constraints(doc)
            if constraint.get("source") == "induced" and isinstance(constraint.get("provenance"), Mapping)
            and "spans" in constraint["provenance"]
        ]
    issues: list[ValidationIssue] = []
    declared = _declared_documents(source, issues, rule_id="semantic:unattended-u1")
    for path, element in _iter_provenance_bearing(doc):
        if element.get("status") == "confirmed":
            issues.append(ValidationIssue(
                path=path, message=f"{_provenance_bearing_label(element)} is confirmed, but no reviewer exists",
                rule_id="semantic:unattended-u2"))
    constraints = list(_iter_constraints(doc))
    for path, constraint in constraints:
        if constraint.get("source") in ("explicit", "user-supplied"):
            issues.append(ValidationIssue(
                path=path, message=f"source '{constraint.get('source')}' claims a human said it; nobody did",
                rule_id="semantic:unattended-u3"))
    for collection, label in (("object_types", "object type"), ("fact_types", "fact type")):
        for element in _listed(doc.get(collection)):
            if isinstance(element, Mapping):
                _require_spans(element, f"$.{collection}[id={element.get('id', '?')}]", label, declared, issues,
                               rule_id="semantic:unattended-u4", span_rule_id="semantic:unattended-u7")
    for path, constraint in constraints:
        provenance = constraint.get("provenance")
        spanless = constraint.get("source") == _UNATTENDED_SPANLESS_SOURCE and not (
            isinstance(provenance, Mapping) and "spans" in provenance)
        if not spanless:
            # A common-sense constraint needs no span, but a span it does carry
            # is checked like any other (review R-F6).
            _require_spans(constraint, path, "constraint", declared, issues,
                           rule_id="semantic:unattended-u5", span_rule_id="semantic:unattended-u7")
    for fact_type in _listed(doc.get("fact_types")):
        if isinstance(fact_type, Mapping):
            _sample_span_issues(dict(fact_type), f"$.fact_types[id={fact_type.get('id', '?')}]", declared, issues,
                                rule_id="semantic:unattended-u6", span_rule_id="semantic:unattended-u7")
    # Every provenance-bearing element, obligations and operations included:
    # D-03 is an error in this mode (close review R3-2).
    for path, element in _iter_provenance_bearing(doc):
        if element.get("modality") == "alethic" and element.get("source") in _UNATTENDED_ALETHIC_SOURCES:
            issues.append(ValidationIssue(
                path=path,
                message=f"an unreviewed {element.get('source')} {_provenance_bearing_label(element)} cannot be alethic in unattended mode",
                rule_id="semantic:unattended-u8"))
    order = {f"semantic:unattended-u{n}": n for n in range(1, 9)}
    return sorted(issues, key=lambda issue: order[issue.rule_id])


def unattended_span_issues(doc: dict[str, Any], documents: Mapping[str, bytes]) -> list[ValidationIssue]:
    """MG5 `gnd validate --document`: re-hash every valid span over a supplied document.

    ``documents`` maps a display path to raw bytes. Offsets count code points
    of the NFC text of the strict UTF-8 decoding (``canonical_document_text``);
    ``documents[].sha256`` is over the raw bytes. Messages name paths, digests
    and offsets, never document text (MG-R5)."""
    from gnd.anchors import AnchorError, canonical_document_text

    source = _unattended_source(doc) or {}
    declared = {entry.get("sha256") for entry in source.get("documents") or [] if isinstance(entry, Mapping)}
    supplied: dict[str, tuple[str, str]] = {}
    issues: list[ValidationIssue] = []
    for display, raw in documents.items():
        digest = hashlib.sha256(raw).hexdigest()
        if digest not in declared:
            issues.append(ValidationIssue(path=display, rule_id="unattended:document-undeclared",
                                          message=f"document sha256 {digest} is not declared in source.documents"))
            continue
        try:
            supplied[digest] = (display, canonical_document_text(raw))
        except AnchorError as error:
            issues.append(ValidationIssue(path=display, rule_id="unattended:document-unreadable",
                                          message=f"document is not strict UTF-8 text: {error}".replace(
                                              "anchor:sidecar-invalid: ", "")))
    for path, span in _iter_unattended_spans(doc):
        if not isinstance(span, Mapping) or span.get("document_sha256") not in supplied:
            continue
        if _span_issue(span, path, set(supplied), rule_id="unattended:span-invalid") is not None:
            continue
        _display, text = supplied[span["document_sha256"]]
        if span["end"] > len(text):
            issues.append(ValidationIssue(path=path, rule_id="unattended:span-out-of-range",
                                          message=f"span end {span['end']} is past the document's {len(text)} code points"))
        elif hashlib.sha256(text[span["start"]:span["end"]].encode("utf-8")).hexdigest() != span["excerpt_sha256"]:
            issues.append(ValidationIssue(path=path, rule_id="unattended:excerpt-mismatch",
                                          message=f"the excerpt at [{span['start']}, {span['end']}) has a different sha256"))
    return issues


def _iter_unattended_spans(doc: dict[str, Any]):
    def spans_of(owner: Any, path: str):
        provenance = owner.get("provenance") if isinstance(owner, Mapping) else None
        for index, span in enumerate(provenance.get("spans") or [] if isinstance(provenance, Mapping) else []):
            yield f"{path}.provenance.spans[{index}]", span

    for collection in ("object_types", "fact_types"):
        for element in doc.get(collection) or []:
            if isinstance(element, Mapping):
                yield from spans_of(element, f"$.{collection}[id={element.get('id', '?')}]")
    for path, constraint in _iter_constraints(doc):
        yield from spans_of(constraint, path)
    for fact_type in doc.get("fact_types") or []:
        provenance = fact_type.get("provenance") if isinstance(fact_type, Mapping) else None
        entries = provenance.get("sample_spans") if isinstance(provenance, Mapping) else None
        for index, entry in enumerate(entries if isinstance(entries, list) else []):
            if isinstance(entry, Mapping):
                yield f"$.fact_types[id={fact_type.get('id', '?')}].provenance.sample_spans[{index}].span", entry.get("span")
