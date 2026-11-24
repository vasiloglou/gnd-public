"""Deterministic large models for the Rmap time-bound tests (OB2 T4)."""

from __future__ import annotations

_MOD = {"source": "explicit", "status": "confirmed", "modality": "alethic", "provenance": {"user_quote": "generated"}}


def _uc(roles):
    return {"type": "uniqueness", "roles": roles, **_MOD}


def large_rmap_model(entities: int = 1400, fact_types: int = 4500) -> dict:
    """``entities`` popular-reference entities and ``fact_types`` fact types: one in four
    functional to a value type, m:n between entities, unary, or ternary with an n-1 key."""
    objects = [{"id": "code", "name": "Code", "kind": "value", "primitive": "String"}]
    for e in range(entities):
        objects.append({"id": f"e{e:05d}", "name": f"E{e:05d}", "kind": "entity",
                        "reference": {"mode": "popular", "value_type": f"e{e:05d}_id"}})
        objects.append({"id": f"e{e:05d}_id", "name": f"E{e:05d}Id", "kind": "value", "primitive": "Integer"})
    facts = []
    for f in range(fact_types):
        a, b, c = f"e{f % entities:05d}", f"e{(f * 7 + 1) % entities:05d}", f"e{(f * 13 + 2) % entities:05d}"
        fid = f"f{f:05d}"
        shape = f % 4
        if shape == 0:
            facts.append({"id": fid, "reading": f"{{E{a[1:]}}} has {{Code}}",
                          "roles": [{"object_type": a, "role_name": "subject"}, {"object_type": "code", "role_name": "code"}],
                          "constraints": [_uc(["subject"])]})
        elif shape == 1:
            facts.append({"id": fid, "reading": f"{{E{a[1:]}}} relates to {{E{b[1:]}}}",
                          "roles": [{"object_type": a, "role_name": "left"}, {"object_type": b, "role_name": "right"}],
                          "constraints": [_uc(["left", "right"])]})
        elif shape == 2:
            facts.append({"id": fid, "reading": f"{{E{a[1:]}}} is flagged",
                          "roles": [{"object_type": a, "role_name": "subject"}]})
        else:
            facts.append({"id": fid, "reading": f"{{E{a[1:]}}} meets {{E{b[1:]}}} at {{E{c[1:]}}}",
                          "roles": [{"object_type": a, "role_name": "first"}, {"object_type": b, "role_name": "second"},
                                    {"object_type": c, "role_name": "place"}],
                          "constraints": [_uc(["first", "second"])]})
    return {"version": 1, "source": {"kind": "text-conversation", "confidence": "standard", "mode": "guided"},
            "object_types": objects, "fact_types": facts}
