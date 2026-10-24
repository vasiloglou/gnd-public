"""IK2 induced-provenance semantic rules (induced-knowledge milestone).

A separate home inside the ``gnd.model`` package so ``_validation`` stays under
its RF6 size ceiling. The rules are registered, in order, at the end of
``gnd.model._validation._SEMANTIC_RULES`` and re-exported by ``gnd.model``.
``_iter_provenance_bearing`` is imported per call: ``_validation`` imports this
module, so a module-level import back would be circular.
"""

from __future__ import annotations

import re
from typing import Any

from gnd.errors import ValidationIssue


def _iter_provenance_bearing(doc: dict[str, Any]):
    from gnd.model._validation import _iter_provenance_bearing as walk

    return walk(doc)


_WHITESPACE = re.compile(r"\s")


def _induction_strings(induction: dict[str, Any], base: str):
    """Yield ``(path, string)`` for every pattern-governed string of a block.

    These are the tokens, ids, refs and digests whose schema ``pattern`` the
    final-newline gap affects. ``confidence.formula`` is free text and is not
    one of them (IK2-F3)."""
    inducer = induction.get("inducer")
    if isinstance(inducer, dict):
        for key in ("name", "version"):
            yield f"{base}.inducer.{key}", inducer.get(key)
    for key in ("method", "manifest_sha256"):
        yield f"{base}.{key}", induction.get(key)
    for key in ("examples", "counterexamples"):
        items = induction.get(key)
        if isinstance(items, list):
            for index, item in enumerate(items):
                yield f"{base}.{key}[{index}]", item
    evidence = induction.get("evidence")
    if isinstance(evidence, list):
        for index, item in enumerate(evidence):
            if isinstance(item, dict):
                for key in ("ref", "sha256"):
                    yield f"{base}.evidence[{index}].{key}", item.get(key)


def _rule_induced_provenance(doc: dict[str, Any]) -> list[ValidationIssue]:
    """IK2: an ``induced`` claim's induction block is internally consistent.

    The schema fixes shape and bounds; these are the cross-field facts it
    cannot state. Support counts the examples it lists, so ``examples`` cannot
    outnumber the numerator nor ``counterexamples`` the remainder, and no id is
    both. Whitespace in a token, id, ref or digest is refused because
    ``jsonschema`` matches with Python ``re.search``, whose ``$`` also matches
    before a final newline, so those patterns alone would let ``"a\\n"``
    through (IK2 S1).

    The block is a recorded claim: nothing here recomputes it from a
    population, which a model file does not carry."""
    issues: list[ValidationIssue] = []
    for path, element in _iter_provenance_bearing(doc):
        if element.get("source") != "induced":
            continue
        provenance = element.get("provenance")
        induction = provenance.get("induction") if isinstance(provenance, dict) else None
        if not isinstance(induction, dict):
            continue  # absent or malformed block is layer 1's rejection
        base = f"{path}.provenance.induction"

        def issue(at: str, message: str) -> None:
            issues.append(
                ValidationIssue(path=at, message=message, rule_id="semantic:induced-provenance")
            )

        for at, text in _induction_strings(induction, base):
            if isinstance(text, str) and _WHITESPACE.search(text):
                issue(at, "induction strings may not contain whitespace, including a final newline")
        support = induction.get("support")
        examples = induction.get("examples")
        counterexamples = induction.get("counterexamples")
        if not (
            isinstance(support, dict)
            and isinstance(examples, list)
            and isinstance(counterexamples, list)
        ):
            continue
        numerator = support.get("numerator")
        denominator = support.get("denominator")
        if not (type(numerator) is int and type(denominator) is int):
            # JSON Schema counts 10.0 as an integer; support counts are exact
            # integers, and a float would also skip every check below (R1).
            issue(f"{base}.support", "support numerator and denominator must be exact integers")
            continue
        if numerator > denominator:
            issue(f"{base}.support", f"support numerator {numerator} exceeds denominator {denominator}")
        if len(examples) > numerator:
            issue(
                f"{base}.examples",
                f"{len(examples)} examples listed but support counts only {numerator}",
            )
        if len(counterexamples) > max(denominator - numerator, 0):
            issue(
                f"{base}.counterexamples",
                f"{len(counterexamples)} counterexamples listed but support leaves only "
                f"{max(denominator - numerator, 0)}",
            )
        shared = sorted(
            {item for item in examples if isinstance(item, str)}
            & {item for item in counterexamples if isinstance(item, str)}
        )
        if shared:
            issue(
                f"{base}.counterexamples",
                f"ids listed as both example and counterexample: {shared}",
            )
    return issues


def _rule_induced_confirmed_reviewed(doc: dict[str, Any]) -> list[ValidationIssue]:
    """IK2: a confirmed ``induced`` claim names a non-blank review record.

    The meta-schema requires ``reviewed_in`` with ``minLength: 1``; this
    refuses the whitespace-only value that passes it, as
    ``semantic:imported-confirmed-reviewed`` does for imports."""
    issues: list[ValidationIssue] = []
    for path, element in _iter_provenance_bearing(doc):
        if element.get("source") != "induced" or element.get("status") != "confirmed":
            continue
        provenance = element.get("provenance")
        reviewed_in = provenance.get("reviewed_in") if isinstance(provenance, dict) else None
        if isinstance(reviewed_in, str) and not reviewed_in.strip():
            issues.append(
                ValidationIssue(
                    path=f"{path}.provenance.reviewed_in",
                    message=(
                        "induced claim is 'confirmed' with a blank 'reviewed_in' record — "
                        "confirmation must name the review that made it"
                    ),
                    rule_id="semantic:induced-confirmed-reviewed",
                )
            )
    return issues
