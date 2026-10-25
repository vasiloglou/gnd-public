---
milestone: induced-knowledge
station: amendment-IK1-Q1
skill: "n/a -- repository development via process-phase, not a gnd-solve station over a domain model"
scope: amendment-IK1-Q1
date: 2026-10-24
gate:
  command: "uv run pytest -q -p no:randomly <90 files, evidence/IK2/gate-files.txt>"
  exit: 0
  output: "4009 passed, 61 deselected, 1 warning in 396.49s (0:06:36); the warning is the pre-existing exp-session one recorded in IK2"
---

# Amendment IK1-Q1: description nesting cap

**Claim.** An object-type `description` may nest containers at most 64 levels
deep, with the description object itself as level 1. Level 65 or deeper exits 3
with `jsonschema:maxDepth`. Nothing outside descriptions changes.

**Authority.** The owner accepted the recommendation of a limit of 64 ("ok go
on", 2026-10-24); see IK1 spec §14 for the ruling text and its arithmetic.

## What changed

- **`src/gnd/model/_validation.py`, `_layer1_structural`:** the iterative walk
  counts container levels inside a description and refuses past 64 before any
  recursive schema validation. To keep the file under its RF6 5,000-line
  ceiling, IK2's `_induced_constraint_paths` helper moved to `gnd.model._induction`.
- **`representation-format.md`:** the description field states the cap, the
  JSON-model limit and the evolve window.
- **RF6b successor:** the `_layer1_structural` row now points at the new body.

## Tests

`tests/test_object_type_description.py`, `q1` cases:

| Case | Without the cap | With the cap |
|---|---|---|
| level 64, dict and list | exit 0 | exit 0 |
| level 65, dict and list | exit 0 (red) | exit 3, `jsonschema:maxDepth` |
| level 200 | exit 0 (red) | exit 3, `jsonschema:maxDepth` |
| 70 levels under `provenance` (not a description) | exit 0 | exit 0 |

## Boundary

- **Evolve window.** A description at roughly levels 60–64 validates but cannot
  pass through an evolve proposal, whose whole-document cap is 64. The
  recommendation's "matches evolve" was imprecise (spec §14).
- **JSON models** stop at whole-document depth 64, about 60 levels of
  description.
- **Past roughly 240 levels**, the YAML loader's own recursion still refuses
  first: exit 3, unnamed.
- **Review.** No adversarial review ran over this small change. It is covered by
  the boundary tests above.

**Owner ruling, 2026-10-25 (o).** Offered the choice of closing the 60–64-level
evolve window with a cap of about 59, the owner chose "go with your rec":
leave the cap at 64 and keep the window as a recorded residual (IK4 spec §18).
