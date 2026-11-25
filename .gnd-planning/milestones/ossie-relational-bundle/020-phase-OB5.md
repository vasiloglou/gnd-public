---
milestone: ossie-relational-bundle
station: "phase-OB5"
skill: "n/a -- repository development, not a gnd-solve station over a domain model"
scope: phase-OB5
date: 2026-11-25
gates:
  - command: "ruling: owner answered ok to the OB5 spec r1; recorded as approval of H1-H6 and H8-H10, H7 open (017-OB5-spec-gate.md)"
    exit: "n/a -- ruling"
  - command: "ruling: owner answered yes to all at the checkpoint: pages to review, fix the two links broken on main, run the oracle lane (018-OB5-checkpoint-gate.md)"
    exit: "n/a -- ruling"
  - command: "ruling: owner approved the quoting fix and the change to approved corpus answer V2 (019-OB5-quoting-gate.md)"
    exit: "n/a -- ruling"
  - command: "uv run --group docs zensical build --strict"
    exit: 0
    output: "No issues found; Build finished"
  - command: "uv run python tools/check_docs.py site"
    exit: 0
    output: "19530 local links/assets/anchors checked"
  - command: "uv run pytest -q tests/test_ossie_docs.py tests/test_ossie_relational.py tests/test_physical_binding.py tests/test_ossie_export.py tests/test_rmap.py tests/test_ossie_import.py tests/test_ossie_formulas.py tests/test_rf1_cli_pins.py tests/test_documentation_tutorials.py tests/test_release_docs.py tests/test_skill_prose_sync.py --tb=line"
    exit: 0
    output: "1084 passed in 293.13s (0:04:53)"
    note: "T3-T6, plus the export, Rmap and binding suites selected again because H7 led to a code change"
  - command: "the project.md structure and inventory guard block (16 files)"
    exit: 1
    output: "1 failed, 865 passed, 2 deselected in 144.61s (0:02:24)"
    note: "the one failure, tests/test_development_scaffold.py::test_reference_closure_and_declared_bootstrap, is the known red; it fails on main"
  - command: "uv run ruff check"
    exit: 0
    output: "All checks passed!"
  - command: "python3 scripts/components_index.py changed --base origin/main --strict"
    exit: 0
    output: "changed against origin/main (6758d22): 40 file(s) differ; 0 to fix, 0 warning(s), 0 to reread"
  - command: "uv run python -m tests.support.physical_binding_corpus"
    exit: 0
    output: "V1: ok ... V7: ok; refusals: ok (50 rows, 19 rule ids)"
  - command: "GND_OSSIE_ORACLE_ROOT=<scratch> uv run pytest -q -m ossie_oracle tests/test_ossie_external_oracle.py -k 'not consumer'"
    exit: 0
    output: "90 passed, 1 deselected in 45.26s"
    note: "opt-in lane, run on the owner's request (018). First run, before the fix: 1 failed, 86 passed (notes/OB5-oracle-lane-run.md). The consumer test needs the RelationalAI environments and was not run."
evidence:
  - path: .gnd-planning/milestones/ossie-relational-bundle/notes/phase-OB5-spec.md
    sha256: 7f6eea49e4d8d4906c63e2abff34cdf55a5065c3180cae3ebfc034567de35215
  - path: .gnd-planning/milestones/ossie-relational-bundle/notes/OB5-oracle-lane-run.md
    sha256: 81bc060db5c92be1c8358814873e1f92c89557091e8d7dcf96cdccf29bab1209
  - path: .gnd-planning/milestones/ossie-relational-bundle/notes/reviews/phase-OB5-r1/review.md
    sha256: 659df7052c2c31cb57859494a09afb161e28894f8c28493c327d788ab2e50431
    note: "sanitized; run.json binds the original"
  - path: .gnd-planning/milestones/ossie-relational-bundle/notes/reviews/phase-OB5-r1/FINDINGS.md
    sha256: 1b79d1d08fc1d126bfe755663232571d58e06ad29aaaa0b200999613e8d8cd96
  - path: "tests/fixtures/physical_binding (29 files, concatenated in the order of 014-OB4-corpus-gate.md)"
    sha256: 07d17670e29bdac37c68d0f579055b5e009991b9cdbe2b623369aaa7c9b2965c
    note: "supersedes d8377d48...54ed: V2/expected.mapping.yaml changed on the owner's ruling (019), eight lines over six expressions; no other file changed"
  - path: src/gnd/export/ossie_relational.py
    sha256: bf41736815e75f0ad5be7a5190e83ae80e39892b43dd7c13f736b3a5e5d79f8a
  - path: src/gnd/skills/gnd-orm-core/references/representation-format.md
    sha256: 81f0fd2f8260bcc2557b04391ff0c519ff2b1c14d19469fc1b1c953c7a21554e
  - path: src/gnd/skills/gnd-export/SKILL.md
    sha256: 16cf80a5c045f8d67de6ccd7484bbf80683cbeacef5bd83774e7710340bb2478
  - path: src/gnd/examples/refunds/physical-binding.json
    sha256: 74b253fa1abdb66334283c0dbf2d1070c7db204e0a08f3641a964eac7f66cc6b
  - path: docs/explanation/ossie.md
    sha256: bf08d2062b0b4dcbfbb43a9be2f8dbec49ebeaec9af8fd17ded9d2f65637befb
  - path: docs/how-to/share-an-ossie-ontology.md
    sha256: 9c8e6de7f9407f9e40c58f1df878e3f19d64ce9499d1388e80ab06e2d2c93dfb
  - path: docs/how-to/describe-delivered-tables-for-ossie.md
    sha256: 817976d939649c8e7828d392719d52d7f2c628c9e722a274f2eb40a98f94697a
  - path: docs/release-notes.md
    sha256: ef9bd68b830b1a834781458b3096e2acf9a707f9a7788c80885e1c5aca13b26c
  - path: tests/test_ossie_docs.py
    sha256: c68f3124bafd9c8a01e0dfbe20d05b162da7fdf690cd88c439190b3a18405129
  - path: tests/test_ossie_external_oracle.py
    sha256: 963142afc100ef5c7d066e16a5ceb4f99b2ae7c49751514fbf0f8fca3e0a4912
  - path: tools/ossie_oracle.py
    sha256: 05c16866cd2666385428c475112a1bea3a9f8107ca5188468cada43bdea42f5d
---

# Phase OB5: docs and skill, and the first oracle-lane run

## What the phase did

1. **Docs and skill**, as the approved [spec](notes/phase-OB5-spec.md) says:
   the explanation (four new sections), the refunds how-to (five files, the
   tables, what is listed), a new how-to for the physical binding with a
   packaged example, the export skill's Ossie section, the release note
   `Unreleased: Ossie relational files`, and mentions in the README, the
   index page and the CLI reference.
2. **Two links broken on main** were fixed on the owner's word (018), so the
   strict build passes.
3. **The oracle lane ran for the first time** over the relational files
   (018, H7). It found a defect in merged OB3 and OB4 code, which was
   repaired here on the owner's ruling (019).

## The oracle lane and the quoting fix

The pinned upstream validator accepted the ontology, semantic model and
mapping of every census model. That settles what OB3 could not confirm:
quoted upper-case identifiers and `CASE WHEN` are accepted.

It rejected binding case V2. GND wrote every identifier quoted and
upper-cased. Ossie upper-cases a name only when it is a regular identifier
and keeps any other name as written, so `"UNI.STUDENT"` did not name the
dataset `uni.student`. The built-in path had the same defect for an object
type whose id is `select` or `not`.

**The repair.** `is_regular_identifier` in
`gnd.export.ossie_relational` states the class, measured with the pinned
validator over every Unicode character: a name is regular unless it is
empty, starts with an ASCII digit, holds white space or ASCII punctuation
other than `$` and `_`, or is the word `not` or `select` in any case.
`_quoted` upper-cases a regular name and writes any other as given. The
rule's one home is the normative section, "Semantic model and mapping".

**Held by tests.** In the default lane: a table of quoted forms, a binding
with a space, a dot and a hyphen in its names, and agreement between the
exporter and the corpus checker's independent statement of the rule over
every character. In the oracle lane: the exporter's class equals the
validator's over every character, and the validator accepts the
irregular-name binding and a table named `select`.

**Approved answers changed:** `physical_binding/V2/expected.mapping.yaml`
only. Two OB3 tests that pinned the old form (`"SELECT"`, and `"A""B"` for
a name with a quote) were updated to the new one.

## Spec obligations

| Obligation | Discharged by |
|---|---|
| O1, O5, O9 (the pages, skill and note; OB1's flags) | the files listed in the evidence |
| O2, O7 (exits by constant; the default change) | the release note; `test_the_release_note_states_the_exits_by_their_constants` |
| O3, O6 (build and link check) | the two gates above, both exit 0 |
| O4 (one home) | `test_every_rule_id_on_a_page_is_in_the_normative_section`, `test_every_reason_on_a_page_is_one_the_code_gives`, `test_the_normative_section_names_every_rule_and_reason_in_the_code`; the reviewer's reading (F5-F7) |
| O8, O10, O11 (the logical marker, surrogate keys, the accepted limits) | the explanation and the binding how-to |
| O12 (no claim about the upstream validator) | the pages say only that GND checks against the pinned schemas; that is still true and was left |
| O13 (OB1-Q1) | to the close sweep (H8) |
| O14, O15 | the `Unreleased:` heading; no downstream name (reviewer confirmed) |

**Normative audit (spec §5.7).** One gap: exit 64 was missing from the
section's exit list. Added. The test above found none in rule ids, reasons
or flags.

**T6 was discharged by reuse.** The tutorial runner already compares a
block's shown output with the real output, so the pages use its
`output=stdout` blocks and no new matcher was written.

## Implementation findings

| ID | Finding | What was done |
|---|---|---|
| IF1 | The reasons `derived-computed` and `identification-unmatchable` are stated in "Relational mapping (Rmap)", not in "Ossie interchange". | The tests read both normative sections as the one home. |
| IF2 | The strict build failed on main already, on two links in `docs/agents` from another milestone. | Fixed on the owner's word (018). |
| IF3 | The refunds model does not say a refund has one amount, so the amount gets its own table. | The how-to says so, as a teaching point. |
| IF4 | The exporter's Python (3.14) and the validator's (3.11) carry different Unicode tables. | See F1 and OB5-Q1. |

## Review

One Codex round, read-only, over the diff from `6758d224`
([brief](notes/reviews/phase-OB5-r1/BRIEF.md),
[review](notes/reviews/phase-OB5-r1/review.md),
[findings](notes/reviews/phase-OB5-r1/FINDINGS.md)). **One reviewer is one
reviewer.** Seven findings, all reproduced, all repaired at `7a6ccfe9`:

- **F2:** the corpus checker's normalizer disagreed with the exporter on 24
  control characters.
- **F3, F4:** the docs tests let a misspelled reason and a wrong exit number
  pass.
- **F5, F6, F7:** three false sentences on the pages.
- **F1:** a letter whose uppercase differs between Unicode versions. Stated
  as a limit, not removed (OB5-Q1).

The repairs are not re-reviewed.

## Refactoring review

**None needed.** The phase touched one product function, `_quoted`, and
added one beside it. Both callers already went through `_quoted`, so the
rule has one place in the product. The corpus checker restates it on
purpose: it is the independent side of the comparison, and a test now holds
the two together. The docs tests reuse `markdown_section` and the tutorial
runner. Nothing was seen and deferred.

## Open questions

| ID | Question | Owner |
|---|---|---|
| OB5-Q1 | F1: an identifier with a non-ASCII letter is upper-cased by the Unicode tables of the Python that runs the export. A reader on older tables may not match it. Accept as a stated limit, or write such names another way? | owner, at the PR or the close |
| OB5-Q2 | The review repairs (F1-F7) and the quoting fix are not re-reviewed. | owner; the close-bar panel reads the merged code |
| OB5-Q3 | The oracle lane's consumer test was not run: it needs the RelationalAI environments of the OS0 receipt. | owner, opt-in |
| OB1-Q1 | Carried: `guard_yaml`'s captured default. | the close sweep (H8) |
| OB4-Q3 | Carried: ask the reporter whether their schema uses surrogate keys, and whether their table names are schema-qualified (D10). | owner confirms the text first |

OB3-Q3 (run the oracle lane) and OB4-Q2 (a second OB4 review) are ruled:
the lane ran, and H10 declined the second round.

## Boundary

- **Not proved:** that a rule is never stated twice in different words on a
  page. Tests hold rule ids, reasons, flags and exit numbers; prose meaning
  was read by one reviewer, who found three false sentences.
- **Not proved:** upstream acceptance of a name with a non-ASCII letter
  whose case mapping changed between Unicode versions (F1).
- **Not run:** the oracle lane's consumer test; the evidence and census
  lanes outside this phase's impact.
- **Not done:** the reporter questions and the three issues (D10); the
  milestone close.
- The oracle scratch root is not kept in the repository. It is rebuilt from
  the OS0 receipt.
