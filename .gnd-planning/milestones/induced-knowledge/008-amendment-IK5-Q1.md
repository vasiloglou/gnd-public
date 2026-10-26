---
milestone: induced-knowledge
station: amendment-IK5-Q1
skill: "n/a -- repository development via process-phase, not a gnd-solve station over a domain model"
scope: amendment-IK5-Q1
date: 2026-10-26
gate:
  command: "uv run pytest -q -p no:randomly tests/test_ilp_bridge.py tests/test_rf6_query_policy.py tests/test_rf8_structure.py tests/test_public_built_inventory.py <the docs test>"
  exit: 0
  output: "210 passed, 16 deselected in 63.05s (0:01:03)"
---

# Amendment IK5-Q1: the ILP export facts bound

**Claim.** `gnd export ilp`, and the export the import recomputes, refuse
`too-large` above 500,000 facts or above 64 MiB per written file, whichever
comes first. Each bound now refuses at its real value.

**Authority.** The owner accepted the recommendation to lower the facts bound
and keep the file cap ("I agree", 2026-10-26). The ruling text and its
arithmetic are in IK5 spec §17.

## What changed

- `src/gnd/export/ilp.py`: `MAX_FACTS` goes from 1,000,000 to 500,000.
- `src/gnd/ilp.schema.json`: `facts.maxItems` goes from 1,000,000 to 500,000.
- `docs/reference/ilp-bridge.md`: the refusal text, the bounds table and the
  work ceiling.
- `tests/test_ilp_bridge.py`: the R6 work line, which is now `ceiling 500006`.

## Tests

`test_q1_each_export_bound_refuses_at_its_real_value` runs with no monkeypatch:

| Case | Facts | Refused by |
|---|---|---|
| 5,001 copies of a 100-fact population | 500,100 | the facts bound (`exceeds 500000 facts`) |
| 4,800 copies, with 40-character example ids | 480,000 | the file cap (`would exceed 67108864 bytes`) |

During the change, the same 480,000 facts with short ids exported at exit 0, at
about 64 MB. That shows the 500,000 bound is reachable for narrow facts.

## Boundary

- No adversarial review ran over this one-constant change. It is covered by the
  boundary tests above.
- Formats, corpus answers and export digests are unchanged.
