"""Explicit raw export and bounded, non-replayable witness presentation."""

from copy import deepcopy

from gnd.witness.io import certificate_shape
from gnd.witness.types import DEFAULT_LIMITS, checked_limits


def witness_view(certificate, *, raw=False, expand=False, limits=DEFAULT_LIMITS):
    try:
        checked_limits(limits)
        certificate_shape(certificate, limits=limits)
    except (ValueError, TypeError, KeyError, RecursionError):
        return {
            "kind": "derivation-witness-view",
            "replayable": False,
            "exit_code": 3,
            "reason": "input-invalid",
            "work": {},
        }
    if raw and not expand:
        return {
            "kind": "derivation-witness-view",
            "replayable": True,
            "exit_code": 0,
            "certificate": deepcopy(certificate),
            "work": {},
        }
    visits, expanded = 0, []
    if expand:
        stack = [
            (r["root"], 1, expanded)
            for r in reversed(certificate["results"])
            if r["root"] is not None
        ]
        while stack:
            i, depth, destination = stack.pop()
            visits += 1
            if visits > limits.expanded_visits or depth > limits.proof_depth:
                return {
                    "kind": "derivation-witness-view",
                    "replayable": False,
                    "exit_code": 4,
                    "reason": "work-limit",
                    "work": {"node_visits": visits},
                }
            source = certificate["nodes"][i]
            node = dict(source) if raw else {"id": source["id"], "kind": source["kind"]}
            node["premises"] = []
            destination.append(node)
            stack.extend(
                (edge, depth + 1, node["premises"]) for edge in reversed(source.get("premises", []))
            )
    # Metadata is selected, never a walk that could accidentally retain values.
    return {
        "kind": "derivation-witness-view",
        "replayable": False,
        "exit_code": 0,
        "reason": "view-redacted" if not raw else None,
        "results": [
            {
                "request_index": r["request_index"],
                "status": r["status"],
                "reason": r["reason"],
                "root": r["root"],
            }
            for r in certificate["results"]
        ],
        "nodes": [
            {"id": n["id"], "kind": n["kind"], "premises": n.get("premises", [])}
            for n in certificate["nodes"]
        ],
        "work": {"node_visits": visits} if expand else {},
        **({"expanded": expanded} if expand else {}),
    }


def result_view(result):
    """Closed metadata selection also covers failures without a certificate."""
    return {
        "kind": "derivation-witness-view",
        "replayable": False,
        "exit_code": result["exit_code"],
        "reason": result.get("reason"),
        "results": [
            {k: r[k] for k in ("request_index", "status", "reason", "root")}
            for r in result["results"]
        ],
        "work": result.get("work", {}),
    }


# Why-not presentation: a closed selection by name. Population values (samples,
# constants, unavailable bindings) are replaced, never copied.
_WHY_NOT_STEP = ("kind", "index", "fact_type", "count")
_WHY_NOT_BLOCKER = (
    "kind", "index", "fact_type", "count", "derivation", "ground",
    "asserted_not_read", "sample_count",
)


def _why_not_role(spec):
    if "constant" in spec:
        return {"constant": "redacted"}
    return {"variable": spec["variable"], "bound": spec["bound"]}


def _why_not_clause(clause):
    blocker = {}
    for key, value in clause["blocker"].items():
        if key in _WHY_NOT_BLOCKER:
            blocker[key] = value
        elif key == "reads":
            blocker[key] = [str(name) for name in value]
        elif key == "roles":
            blocker[key] = {str(role): _why_not_role(spec) for role, spec in value.items()}
    blocker["samples"] = "redacted"
    descent = clause["descent"]
    return {
        "clause_index": clause["clause_index"],
        "steps": [
            {key: step[key] for key in _WHY_NOT_STEP if key in step} for step in clause["steps"]
        ],
        "blocker": blocker,
        "steps_after_blocker": clause["steps_after_blocker"],
        "descent": None if descent is None else _why_not_explanation(descent),
        "descent_stopped": clause["descent_stopped"],
    }


def _why_not_explanation(payload):
    unavailable = payload["unavailable"]
    return {
        "status": payload["status"],
        "reason": payload["reason"],
        "fact_type": payload["fact_type"],
        "mode": payload["mode"],
        "order": payload["order"],
        "unavailable": None if unavailable is None else {
            "reason": unavailable["reason"],
            "source_relation": unavailable["source_relation"],
            "binding": "redacted",
        },
        "clauses": [_why_not_clause(clause) for clause in payload["clauses"]],
        "work": {str(key): int(value) for key, value in payload["work"].items()},
    }


def why_not_view(payload):
    """The default CLI view of a why-not payload: structure and counts, no values."""
    return {
        "schema_version": payload["schema_version"],
        "exit_code": payload["exit_code"],
        **_why_not_explanation(payload),
    }
