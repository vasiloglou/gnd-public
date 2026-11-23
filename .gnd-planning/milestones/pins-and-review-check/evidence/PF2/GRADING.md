# PF2 grading

Graded under spec §6 "Grading", which was fixed before the runs. Every
reported input was run on the version it was reported against
(`grade.py`, output `key/grade-runs.json`). The reviewer was Codex
(`codex exec --sandbox read-only`, reasoning high), one run per diff,
base `6b0a7e5a`, the same neutral question for all eight, no `--claim`.

## Planted versions

| Branch | Capability | Verdict | Reported inputs run | Grade |
|---|---|---|---|---|
| `change-f` | K1 object-type ids | CHANGES_REQUESTED | `object_types` first (raises `IndexError`), a quoted id (`[]`), `fact_types` before `object_types` (`['title', 'metadata']`) | **found**: all three wrong as reported |
| `change-a` | K2 skill names | CHANGES_REQUESTED | `name: "demo"`, a trailing comment, a quoted key, a folded scalar, a description holding `---` | **found**: all five wrong as reported |
| `change-g` | K3 skill of a file | CHANGES_REQUESTED | `agents/openai.yaml` (`'agents'`), `references/nested/guide.md` (`'nested'`) | **found**: both wrong as reported; the review also reported 15 of 71 packaged files wrong (its count, not rerun here) |
| `change-h` | K4 project version | CHANGES_REQUESTED | an earlier table (`'9.9.9'`), no spaces (`None`), single quotes (`None`), a dynamic version with a tool-table version (`'9.9.9'`) | **found**: all four wrong as reported |

Planted found with a breaking input: **4 of 4**. Missed: **0**. Suspected only: 0.

## Controls

| Branch | Capability | Verdict | Finding | Grade |
|---|---|---|---|---|
| `change-d` | K1 | APPROVE | none | clean |
| `change-b` | K4 | APPROVE | none | clean |
| `change-c` | K2 | CHANGES_REQUESTED | a block-scalar description holding an indented `---` hides `name` | **true finding on a control**: reproduces (`{'demo': None}`). The cause is the reused reader `gnd.exp.frontmatter._split`, which takes `lines[i].strip() == "---"` as the closing fence. A defect on `main` (record OQ4) |
| `change-e` | K3 | CHANGES_REQUESTED | `gnd-solve/../gnd-adopt/SKILL.md` returns `'gnd-solve'` | **true finding on a control**: reproduces. `Path.relative_to` is lexical; the control does not normalise. The control is flawed |

False findings on controls: **0**. True findings on controls: **2**.

## Non-fitted findings

None. Every finding of the eight reviews was a fitted-code or input-class
finding with an input.

## Misses and the brief (PF2-C4)

No planted defect was missed, so no brief sentence is implicated. The
brief's bullets the findings match: "a regular expression, string split,
slice or index over structured text" (K1, K2, K4), "a pattern fitted to the
fixtures ... quoting, ... nesting" (K1, K2, K4, K3), "a branch on one literal
name" (K3), and "a parser or an existing reader in this repository already
reads" (K1 named `load_model_bytes`, K2 `read_frontmatter`, K4 `tomllib` in
`tools/release_text.py`, K3 `install._skill_of`).
