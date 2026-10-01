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
