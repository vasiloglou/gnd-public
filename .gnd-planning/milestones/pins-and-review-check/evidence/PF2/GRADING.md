# PF2 grading

Graded under spec §6 "Grading", which was fixed before the runs. Every
input a review reported was run on the version it was reported against, and
on that capability's other version too (`gen/grade.py`, output
`key/grade-runs.json`, 64 rows). The first grading pass ran a subset; the
PF2 phase review (round 1, F2) found the gap and the script was extended
(correction c1, 2026-11-23). No grade changed. The reviewer was Codex
(`codex exec --sandbox read-only`, reasoning high), one run per diff,
base `6b0a7e5a`, the same neutral question for all eight, no `--claim`.

## Planted versions

| Branch | Capability | Verdict | Reported inputs run | Grade |
|---|---|---|---|---|
| `change-f` | K1 object-type ids | CHANGES_REQUESTED | `object_types` first, an inline header comment and `object_types: []` (each raises `IndexError`), a quoted id and an indentless sequence (each `[]`), `fact_types` before `object_types` (`['title', 'metadata']`) | **found**: all six wrong as reported |
| `change-a` | K2 skill names | CHANGES_REQUESTED | `name: "demo"`, a trailing comment, a quoted key, a folded scalar, an indented mapping, a description holding `---`, no frontmatter (raises `IndexError`), a name after a body rule (`'evil'`) | **found**: all eight wrong as reported |
| `change-g` | K3 skill of a file | CHANGES_REQUESTED | `agents/openai.yaml`, `examples/...`, `evals/fixtures/.../README.md`, `references/nested/...`, `scripts/nested/...`, `references/references/...` | **found**: all six wrong as reported; the review also reported 15 of 71 packaged files wrong (its count, not rerun here) |
| `change-h` | K4 project version | CHANGES_REQUESTED | an earlier table, a dynamic version beside a tool-table version, a version line in a multiline description (each `'9.9.9'`), no spaces, single quotes, a quoted key (each `None`), a Unicode escape (`'1.2.\\u0033'`) | **found**: all seven wrong as reported |

Planted found with a breaking input: **4 of 4**. Missed: **0**. Suspected only: 0.

## Controls

| Branch | Capability | Verdict | Finding | Grade |
|---|---|---|---|---|
| `change-d` | K1 | APPROVE | none | clean |
| `change-b` | K4 | APPROVE | none | clean |
| `change-c` | K2 | CHANGES_REQUESTED | a block-scalar description holding an indented `---` hides `name` | **true finding on a control**: reproduces (`{'demo': None}`). The cause is the reused reader `gnd.exp.frontmatter._split`, which takes `lines[i].strip() == "---"` as the closing fence. A defect on `main` (record OQ4) |
| `change-e` | K3 | CHANGES_REQUESTED | `gnd-solve/../gnd-adopt/SKILL.md` returns `'gnd-solve'` | **true finding on a control**: reproduces, with the review's three further inputs: a leading `..` and a file outside the root (each `'..'`), and a relative path under an absolute root (raises `ValueError`). `Path.relative_to` is lexical; the control does not normalise. The control is flawed |

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
