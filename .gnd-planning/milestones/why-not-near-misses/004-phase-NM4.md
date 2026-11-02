---
milestone: why-not-near-misses
station: phase-NM4
skill: "n/a -- repository development via process-phase auto=false, not a gnd-solve station over a domain model"
scope: phase-NM4
date: 2026-11-02
gate:
  command: "uv run python tools/run_tutorials.py && uv run zensical build --strict && uv run python tools/check_docs.py site && uv run pytest -q tests/test_documentation_tutorials.py tests/test_plan_app_docs.py tests/test_disclosure_docs.py"
  exit: 0
  output: "256 tutorial blocks passed; no issues; 12774 local links/assets/anchors checked; 152 passed"
  note: >-
    The plan section 9 NM4 row (NM4-C3 commands plus the one-home test). The
    installed-docs check, the packaged-skill suites, the census suites and
    the T7/T9 scripted checks are in the body; evidence/NM4/final-gate.txt
    holds each command and exit.
slow_cadence:
  command: "uv run pytest -q"
  trigger: "explicit owner selection at milestone close (plan section 9)"
  reason: "every changed path is covered by the selected docs, skill and disclosure suites"
evidence:
  - path: .gnd-planning/milestones/why-not-near-misses/notes/phase-NM4-spec.md
    sha256: 457834fce393c2ed22e14503f7b095e2042e414d95f79e00b57b81551c4ee2fa
  - path: .gnd-planning/milestones/why-not-near-misses/notes/phase-NM4-docs-review.md
    sha256: 3bd6d8f07aab6b3f3e2fe273782c1e8d704b1f37c7ac15db14ef8ebde2c9c393
  - path: .gnd-planning/milestones/why-not-near-misses/evidence/NM4/final-gate.txt
    sha256: 723707092638c45ab0b77eecb4d3a8c21074b8d3be66c8956ca327e0e0f67844
  - path: .gnd-planning/milestones/why-not-near-misses/evidence/NM4/apply_edits.py
    sha256: 164b47bb820717f058b025ed480f04bcc9f00586824f5ddc4cc7151a053b0210
  - path: .gnd-planning/milestones/why-not-near-misses/evidence/NM4/check_against_dc2.py
    sha256: 9ff78a26efb2281dfb83e2081d56df651f71a7038073d8bbc1a777cc2dae8216
  - path: .gnd-planning/milestones/why-not-near-misses/evidence/NM4/check_inventory.py
    sha256: 40baa0c9540b049cca1fe9d252ca5dade37bfbe28da8b0442c8a5cf21dd3809f
  - path: docs/reference/disclosure.md
    sha256: 1772d70a25286a89acc4e9a97a62b5a3281afae8f970de50c991fced0aa0e34b
  - path: docs/how-to/disclosure-mode.md
    sha256: 5c6a596014863a257c42f4ac15ccf7a95b6c12d0662c7fb86fe2e2b74462a7af
  - path: tests/test_disclosure_docs.py
    sha256: 197707d303e4e49cd6bf14e6e0ac3ba091ddd2be0e8e6481663047ebaa7a4609
  - path: tools/run_tutorials.py
    sha256: 800a32be893c09d4bc2e325fe8e3eabbf6444f8fb4d5cf7e6aa18a12a253fafb
  - path: zensical.toml
    sha256: 70991a110b397ad82aae7cbd3ca1c5b73a60132a826fb874f4527c7213b2d2ff
  - path: src/gnd/disclosure.py
    sha256: babc9db422fff5fe39abf488035753da068b49b8b95d8e97073b067919c7b6fa
  - path: src/gnd/skills/gnd-export/SKILL.md
    sha256: 661c4e0f695f69d198779eb0d05e8809a59eff1d45a75f76c634ccecfdc5258c
  - path: src/gnd/skills/gnd-orm-core/references/representation-format.md
    sha256: 73f09f247d87738f717c6b623eea9cef6f366ceaf99066a12e81d2a33e49f491
---

# Phase NM4 -- documentation

Spec: [phase-NM4-spec.md](notes/phase-NM4-spec.md), r1, approved by the owner
on 2026-11-02 `(s4)` (SHA-256 `b973fbe0…8ddb1` at approval). The rulings were
D1 (a), D2 (a), D3 (a) and D4 (a), with no spec review panel. D5 was added
during implementation and ruled (a) `(s5)`. The approval instrument (D4) was
the DC2 drafts. T7 checks the shipped bytes against them, listing each stated
difference.

Checkpoints (NM4-C2), each shown to the owner as a private page with real or
illustrative output and answered with the quoted reaction:

| Checkpoint | Shown | Reaction |
|---|---|---|
| DC1, illustrative drafts after plan approval | 2026-11-01 | "Looks good" |
| DC1b, the how-to from real runs of `23e4a99` | 2026-11-01 | "Looks good" |
| DC2, every page from real runs of `420114e` | 2026-11-01 | "Looks good" |

## What shipped

- **New pages:**
  - `docs/reference/disclosure.md` (214 lines). It is the one home of the
    mode: the three states, setting and resolving it, refusals, the outputs
    that are the same in every mode, child processes, the threat model and
    the membership signal, declaring sensitive roles, and the table of every
    command and function, pasted from `disclosure_table()` between two
    markers.
  - `docs/how-to/disclosure-mode.md` (227 lines, 13 `gnd-run` blocks).
- **Registration:** the `disclosure` group in `tools/run_tutorials.py`;
  `disclosure` and `why-not` in the docs test parametrization (D3); two nav
  entries in `zensical.toml`.
- **Edits to 11 existing pages:** `why-not.md`, `cli.md`, `python-api.md` (a
  new executed section, "Under a disclosure mode"), `capabilities.md`,
  `formats.md`, `discover.md`, `ilp-bridge.md`, `guides/exports.md`,
  `agents/export-and-review.md`, `release-notes.md` (a disclosure-mode entry
  with the customer-mode contract changes) and `bookrec/02-facts.md` (one
  link, H5).
- **Packaged skills (two of the five planned, D5):**
  - `gnd-export/SKILL.md`: the near-miss counters, and the `customer`
    refusal of `--raw`;
  - `gnd-orm-core/references/representation-format.md`: how the modes use
    `redact`.
- **Source:** one docstring line in `src/gnd/disclosure.py` (H4).
- **Test:** `tests/test_disclosure_docs.py` (100 lines, 6 tests). It checks:
  - the table equals the code, and a dropped row is caught;
  - `NFKC` has one home;
  - the mode tables have one home;
  - a restated rule is caught;
  - every every-mode command is named on the page (F3).
- **Scripted checks** in `evidence/NM4/`:
  - `apply_edits.py`: the exact edits;
  - `check_against_dc2.py`: T7;
  - `check_inventory.py`: T9, with a negative control (one row removed
    fails).

Size: 441 new page lines, 112 lines added and 26 removed across 17 tracked
files, a 100-line test, and 350 lines of scripted checks. The spec estimated
about 460, 80, 15, 90 and 60. The scripted checks grew because T7 carries
the stated differences.

## Gate output

See [final-gate.txt](evidence/NM4/final-gate.txt).

| Command | Result |
|---|---|
| `tools/run_tutorials.py` | 256 blocks passed, exit 0 |
| `zensical build --strict`; `tools/check_docs.py site` | no issues; 12774 links checked; exit 0 |
| `test_documentation_tutorials.py test_plan_app_docs.py test_disclosure_docs.py` | 152 passed, exit 0 |
| packaged-skill, anonymity, disclosure and layering suites (8 files) | 166 passed, exit 0 |
| `tools/check_installed_docs.py --out <scratch>` | both wheel origins passed, exit 0 |
| T7 `check_against_dc2.py` | 2 new pages equal their drafts; 21 edits; 66 DC2 sentences and rows shipped; exit 0 |
| T9 `check_inventory.py` | 35 inventory files, each with a disposition; exit 0 |
| `test_ik6_skill_census.py test_il6_skill_census.py` | 5 failed, 13 passed **uncommitted**: both credit an uncommitted skill edit to their own scope. With the uncommitted credit switched off, both report no phase errors. **After the commit** (8bc5039), with `test_why_not_anonymity.py` and `test_disclosure_docs.py`: 27 passed, exit 0. |

## Implementation findings

From the spec's findings section:

| ID | Finding |
|---|---|
| F1 | The induced-knowledge census test diffs its base against the working tree with no end commit, and so forbids any edit to three skill files it marks unchanged. This became D5. |
| F2 | The judgment-contract sentence's style. Moot after D5. |
| F3 | One extra test: every every-mode command is named on the page. |
| F4 | `test_plan_app_docs` forbids exit codes and "production" in how-to prose. Three DC2 sentences were reworded and are listed as stated differences. |

## Adversarial review (NM4-C5)

One reviewer is one reviewer. A Claude subagent with read-only access, given
the docs and the code but not the author's conclusions, checked every changed
statement by running commands. Its report is
[phase-NM4-docs-review.md](notes/phase-NM4-docs-review.md). It found nothing
blocking, two should-fix accuracy gaps and two minor ones. All four are fixed
and listed as stated differences in T7:

- **R1:** the resolution rules apply only to the commands the mode governs;
  the every-mode commands ignore a malformed variable. Reproduced by the
  author. The code matches the plan's §2.2.
- **R2:** the unset row named all Python functions as raw; only witness,
  replay and why-not are.
- **R3:** the table said `raw=True` for functions that take no `raw`.
- **R4:** "three fields" where the filter prints two.

## Refactoring review

**None needed**, argued from what NM4 touched:

- **The generator.** `disclosure_table()` lives in the test that guards the
  page, its only caller. A tool script would add a second home for the same
  function.
- **The edit list.** `apply_edits.py` is evidence, not product code. It records
  exactly what changed and is re-checked by T7.
- **Seen and deferred:** the induced-knowledge census test's open-ended diff
  (F1) will block any later edit to the three files. Bounding it, as the IL
  census already does, is a maintenance task for the milestone close or
  later (NM4-Q1).

## Boundary -- what this phase does NOT establish

- **No behaviour change.** The pages describe `420114e`; the one source line
  is a docstring.
- **Unproved by the reviewer:** the `discover` and ILP-bridge redacted-role
  claims (they match the table's notes), and real child environments for
  `exp run`, `solve` and `review panel` (NM2 T30–T33 cover them).
- **Three skill files say nothing about the mode** (D5). The `customer`
  refusal is documented in `gnd-export/SKILL.md` and `disclosure.md`.
- **The census suites pass only once committed.** Measured by simulation
  and confirmed after the commit (27 passed).
- **Not run:** the broad default suite.
- **One reviewer:** the docs review was one reviewer.

## Open questions

| ID | Question | Owner |
|---|---|---|
| NM4-Q1 | Bound the induced-knowledge census test (`test_ik6_skill_census.py`) at that milestone's end, as the IL census counts only its own commits, so later skill edits are not forbidden (F1) | milestone close or a later maintenance pass |

Carried: NM2-Q1 is resolved by D1 (a) (`doccheck` stays every-mode); NM2-Q2
(`fidelity` in three modes, close); NM2-Q3 (RF1 golden recapture, later);
NM3-Q1 (the installed-docs command wording, close).

## Refuted premises

- **H1–H5** (spec, "Corrections to the plan").
- **The spec's T5 coverage claim** was too narrow: `test_plan_app_docs`'s
  prose rule (F4) was not read at spec time.
- **The DC2 drafts were accurate** only up to the reviewer's R1–R4.
