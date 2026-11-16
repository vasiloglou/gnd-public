"""Publication-year advisories over LI5's candidate lineage vocabulary."""

from datetime import date

from gnd.anchors import strict_json
from gnd.artifacts import sha256_hex

CAP = 1 << 20
PUBLICATION = "publication"


def _record(value, fields):
    if not isinstance(value, dict) or set(value) != fields:
        raise ValueError("invalid publication advisory record")
    return value


def _text(value):
    return isinstance(value, str) and 0 < len(value) <= 256


def _date_index(data):
    _record(data, {"schema", "works", "dates"})
    if (data["schema"] != "literature-publication-dates/1"
            or not isinstance(data["works"], list) or not isinstance(data["dates"], list)
            or not all(_text(work) for work in data["works"])):
        raise ValueError("invalid publication dates input")
    works = {work: {} for work in data["works"]}
    if len(works) != len(data["works"]):
        raise ValueError("duplicate advisory work id")
    for entry in data["dates"]:
        _record(entry, {"work", "role", "precision", "value"})
        work, role, precision, value = (entry[k] for k in ("work", "role", "precision", "value"))
        if not _text(work) or work not in works or not _text(role):
            raise ValueError("invalid work or role for advisory date")
        if precision == "year" and type(value) is int and 1 <= value <= 9999:
            year = value
        elif precision == "day" and isinstance(value, str):
            day = date.fromisoformat(value)
            if value != day.isoformat():
                raise ValueError("day precision requires a calendar date")
            year = day.year
        else:
            raise ValueError("invalid declared precision or date value")
        works[work].setdefault(role, set()).add((precision, value, year))
    return works


def _publication(works, work):
    if work is None:
        return None, "missing-work-link"
    if work not in works:
        return None, "unknown-work"
    dates = works[work]
    if not dates:
        return None, "missing-date"
    candidates = dates.get(PUBLICATION, ())
    if not candidates:
        return None, "publication-date-missing"
    if len(candidates) != 1:
        return None, "conflicting-date"
    return next(iter(candidates)), None


def advise(edge_bytes: bytes, date_bytes: bytes, policy_bytes: bytes) -> dict:
    """Name the work pair and report their stated publication order."""
    edges, dates, policy = (
        strict_json(raw, max_bytes=CAP, too_large="advisory JSON exceeds its byte ceiling")
        for raw in (edge_bytes, date_bytes, policy_bytes)
    )
    _record(edges, {"schema", "edges"})
    _record(policy, {"schema", "chainable", "non_chaining", "transfer", "absence_words"})
    if (edges["schema"] != "literature-candidate-edges/1" or not isinstance(edges["edges"], list)
            or policy["schema"] != "literature-lineage-policy/1"
            or not isinstance(policy["chainable"], list) or not isinstance(policy["non_chaining"], list)
            or not all(_text(rel) for rel in policy["chainable"] + policy["non_chaining"])):
        raise ValueError("invalid candidate edges or lineage policy")
    chainable = set(policy["chainable"])
    excluded = set(policy["non_chaining"])
    works = _date_index(dates)
    report = []
    seen = set()
    counts = dict.fromkeys(("pass", "advisory", "unresolved"), 0)
    for edge in edges["edges"]:
        _record(edge, {"id", "relation", "descendant_work", "ancestor_work"})
        links = (edge["descendant_work"], edge["ancestor_work"])
        if (not _text(edge["id"]) or not _text(edge["relation"]) or edge["id"] in seen
                or any(link is not None and not _text(link) for link in links)):
            raise ValueError("invalid or duplicate candidate edge")
        seen.add(edge["id"])
        if edge["relation"] in excluded:
            continue
        if edge["relation"] not in chainable:
            raise ValueError("candidate edge uses an unknown lineage relation")
        descendant, descendant_reason = _publication(works, edge["descendant_work"])
        ancestor, ancestor_reason = _publication(works, edge["ancestor_work"])
        reason = descendant_reason or ancestor_reason
        if reason is None and descendant[0] != ancestor[0]:
            reason = "mixed-precision"
        if reason is not None:
            outcome = "unresolved"
        else:
            outcome = "pass" if descendant[2] >= ancestor[2] else "advisory"
            if outcome == "advisory":
                reason = "parent-published-later"
        report.append({
            **edge, "role": PUBLICATION, "outcome": outcome, "reason": reason,
            "descendant_date": descendant[1] if descendant else None,
            "ancestor_date": ancestor[1] if ancestor else None,
            "descendant_precision": descendant[0] if descendant else None,
            "ancestor_precision": ancestor[0] if ancestor else None,
        })
        counts[outcome] += 1
    return {
        "schema": "literature-date-advice/1", "edges": report, "counts": counts,
        "bindings": {
            "candidate_edges_sha256": sha256_hex(edge_bytes),
            "publication_dates_sha256": sha256_hex(date_bytes),
            "lineage_policy_sha256": sha256_hex(policy_bytes),
        },
    }
