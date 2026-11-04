# Phase MG6 docs review (MG6-C5)

Reviewer: one independent docs reviewer, against shipped behavior at HEAD 7961119 plus the
uncommitted MG6 working tree. Repository treated read-only.

## Verdict

**approve-with-fixes.** Every executable block on the how-to runs and prints what the page
shows (runner group `growth` passes, and a by-hand re-run matches). Two sentences misdescribe
shipped behavior in a way a reader would act on (R-F1, R-F2); both are one- or two-sentence
fixes. The rest is completeness and wording.

## Findings

### R-F1 (blocking): `apply` does not "rewrite the model file as canonical one-line JSON"

`docs/how-to/grow-a-model.md`, section "Apply the round": "`apply` rewrites the model file as
canonical one-line JSON, so comments and YAML layout in the file are gone."

Shipped behavior: `apply` publishes the proposal's `candidate_model.text` verbatim; the
preview/apply check is semantic ("declared operations do not equal the canonical candidate
model", `src/gnd/evolve/service.py:1357`, `:1717`), not a byte form. The one-line JSON here
comes from the build script, which calls `gnd.discover.output.candidate_text` (a
`json.dumps(..., separators=(",", ":"))`, `src/gnd/discover/output.py:99`).

Reproduced: copied the example, replaced round-1's `candidate_model.text` with the original
commented YAML plus the new fact type in block YAML (sha256 recomputed;
`scratchpad/review-mg6/yaml_candidate.py`). `preview --policy additive` exit 0, `apply
--policy additive` exit 0, and the published `model.orm.yaml` still begins
`# A shop's model, grown one round at a time (MG6 how-to).` with its YAML layout intact.

So the page's advice ("Keep your hand-written YAML elsewhere") rests on a false premise, and
the MG6-C3/O22 obligation is discharged with an inaccurate statement.

Fix: "`apply` writes the proposal's `candidate_model` text as the new model file. The
proposals here were built with GND's own helper, which writes canonical one-line JSON, so after
this round the file's comments and YAML layout are gone." Optionally: "a proposer that writes
YAML text keeps YAML."

### R-F2 (blocking): the how-to never mentions `--populated`, so its motivating case is unprotected

The page opens with a program that "extracts facts into them" and says a new rule "on facts you
already hold" is refused: "GND checks that for you, round by round." But a fact type is
populated only through `sample_population` rows, a declared reference population, a
`population` artifact in the proposal, or `--populated ID` (evolution contract, "Additive
policy", **Populated**). Facts a program extracts into separate population files are none of the
first three. The example works only because `order_placed_by_customer` has sample rows.

Reproduced: a round-3 proposal (built with the MG6 build script's `proposal()` helper,
`scratchpad/review-mg6/unpop.py`) adding the same mandatory constraint to
`order_arrives_via_channel`, which has no sample rows:

- `preview ... --policy additive` exit **0**, no `policy-issue` (admitted);
- `preview ... --policy additive --populated order_arrives_via_channel` exit **3**,
  `constraint.populated.add`.

A reader following the page in its own scenario gets a silent admission. The reference page and
CLI row show `--populated`; the how-to and the three pointer paragraphs
(`docs/guides/evolution-and-recovery.md`, `docs/agents/evolve.md`, release note bullet wording
aside) do not.

Fix: one paragraph after the round-2 refusal: "GND counts a fact type as populated when the
model holds sample rows for it (as here). Facts your program keeps in population files are
invisible to the model: name each such fact type with `--populated FT`, on both `preview` and
`apply`." Add `--populated FT` to the `evolve.md` bullet and the guide paragraph
("a fact type that already holds facts" -> "... facts, by sample rows or `--populated`").

### R-F3 (hardening): "rule" means three different things on one page

`grow-a-model.md` calls the mandatory constraint "a mandatory rule" / "A new rule there", calls
the matrix cell "the rule of the policy it broke", says "The guide never states a rule"
(constraint), then "Read the rules back" shows `verbalize_rules`, which renders **derivation
rules only** (`docs/reference/rule-verbalization.md`: "renders derived fact types' rules").
A reader who just watched GND refuse "a mandatory rule" will expect read-back to cover
constraints; it never prints one (`api.verbalize_rules` on the grown model returns one entry,
`customer_is_active`). The guide paragraph has the same "adds a rule" wording.

Fix: say "constraint" for constraints (the policy's own word), "cell" for the matrix cell, and
open the read-back section with "Derivation rules your program wrote ... (constraints are in the
full verbalization, `model.verbalization.txt`)".

### R-F4 (completeness): the consolidated release note drops or narrows facts from the five entries

Compared with `git show HEAD:docs/release-notes.md`:

1. Unattended: the old entry refused a model that "marks anything `confirmed` or
   `user-supplied`"; the new bullet says only "nothing `confirmed`". U3 (no `explicit` /
   `user-supplied` source) is gone.
2. Additive: dropped "A preview made with the option carries `policy`, `populated_args`,
   `populated` and `policy_issues`; the keys are omitted otherwise" (a visible preview-schema
   change for consumers) and the fact that `apply` *refuses* (exit 3) when its options differ;
   "repeats the options" reads as a recommendation. Verified: apply without `--policy` after an
   additive preview exits 3, "--policy differs from the reviewed preview".
3. Shape report: dropped "`apply` needs no new option; it rebuilds the report", and the key name
   `shape_matches` is nowhere in the note.
4. Rule verbalization fix: dropped "Its output now equals the output for the loaded model".
5. "Without the new options, previews, applies, extract bundles and validation results are
   byte-identical": `source.mode: unattended` is a model value, not an option, and the
   verbalization fix *is* a flag-free output change (raise -> text). Suggest "Without the new
   options or `source.mode: unattended`, ... byte-identical to before, except that ..." and list
   both exceptions (induced `provenance.spans`; the verbalization fix).

Fix: restore items 1-3 as short clauses; reword item 5.

### R-F5 (completeness): unattended span requirement overstated

`grow-a-model.md`: "requires every element, constraint and sample row to cite its source text";
`docs/agents/model-from-text.md`: "cites a span of its source text for every claim". U5 exempts
`common-sense` constraints (they cite `library_entry`), and U4 covers object and fact types,
not roles. The release note gets this right ("non-common-sense constraint"). Fix: "every object
type, fact type, sample row and every constraint except a common-sense one (which names its
library entry)". The how-to also points to "the `gnd-model-from-text` skill's Unattended mode"
without a link; link `representation-format.md` ("Unattended source"), the one home.

### R-F6 (completeness): disposition table misses grep hits

`grep -rlE 'evolve (preview|apply)|gnd extract|one-shot|verbalize_rules' docs src/gnd/skills
README.md` (38 files, list in `scratchpad/review-mg6/grep.txt`) finds two files not in the
table:

- `src/gnd/skills/gnd-orm-core/references/representation-format.md` (the MG5 normative home;
  "no change: updated in MG5" is the likely disposition, but it must be stated).
- `src/gnd/skills/gnd-orm-core/references/verbalization-patterns.md:31`:
  `mode=<guided|one-shot>` in the verbalization header template, which omits `mvp-fast` and
  `unattended`. Pre-existing for mvp-fast, but now stale for the milestone's mode; dispose it
  (fix or "no change, because ...").

The new `docs/how-to/grow-a-model.md` also hits and is not listed (trivial). The table lists
files the case-sensitive grep does not hit (`USAGE.md`, `examples/`, `dialogue-patterns.md`);
harmless over-coverage, but the T1 claim "covers every file the grep finds" is false as written.

### R-F7 (completeness/readability): wording a reader without the plan will trip on

- "the fact types played by the same object types" (how-to, guide, evolve.md:
  "fact types over the same object types" is fine): object types play roles; fact types are
  not played. Use "fact types whose roles are played by the same object types". "what each role
  means" overpromises: the guide gives the player's description, reference mode and primitive.
- Packaged example leaks plan jargon and repo-only paths: `model.orm.yaml` comment
  "(MG6 how-to)" survives into every reader's copy (and into the published model in R-F1's
  YAML case); `src/gnd/examples/growth/README.md` tells an installed-package reader to run
  `.gnd-planning/.../evidence/MG6/build_growth_example.py`, which is not in the wheel. Drop
  "MG6" and say "regenerated from the repository's build script".
- Release note "GND now owns five checks": rule read-back is not a check; "five capabilities".
- `tests/test_growth_example.py` runs a script under `.gnd-planning/.../evidence/`; product
  tests depending on milestone evidence paths is fragile if planning is archived. Consider
  `tools/` (spec D4 did not decide the script's home).

## Claims checked and confirmed

- Copy command exit 0; round-2 preview exit 3 with the exact stderr line shown; preview still
  written; `policy_issues` line `0 constraint.populated.add fact_types[order_placed_by_customer].constraints[mandatory:new:0]`.
- "The model is unchanged": sha256 `cb4848ed...` before and after the refused preview; no
  records directory created.
- Round-1 preview exit 0 with one `shape_matches` group, `order_returned_via_channel ~
  order_arrives_via_channel | {Order} arrives via {Channel}`; "never changes the exit" (exit 0,
  `breaking: false`).
- `apply` without `--policy` after an additive preview: exit 3 ("--policy differs"); with it:
  exit 0, RECORDED, conformance-exit 0; first 40 chars as shown.
- `gnd extract --guidelines` exit 0; `model.guidelines.md` listed with digest in
  `model.artifacts.json`; grep prints the two lines shown; no constraint appears; header text
  matches the page's "writes what the document says" sentence and extraction contract §4a.
- `api.verbalize_rules` prints the one shown line; payload `exit_code` 0, `status: rendered`.
- `evolve-policy.md` and `documents.md`/`agents/documents.md` additions agree with the evolution
  contract and §4a. CLI help confirms `--guidelines`, `--policy`, `--populated` on the stated
  commands; `apply` has no `--shape-report` (consistent with the pages).
- nav entry and `growth` runner group present; anonymity scan of changed pages and example: 0
  matches.

## What I ran

- `uv run python tools/run_tutorials.py --group growth` -> "10 tutorial blocks passed".
- `uv run pytest -q tests/test_growth_example.py` -> 2 passed.
- By hand in temp dirs (`mktemp -d`), with the worktree's `.venv/bin` on PATH: every how-to
  command in order, plus sha256 of the model before/after, the preview's policy keys, apply
  without `--policy`, the full guideline file and artifacts index, the full
  `verbalize_rules` payload.
- R-F1 reproduction: `scratchpad/review-mg6/yaml_candidate.py` (YAML candidate text) ->
  preview 0, apply 0, comments kept.
- R-F2 reproduction: `scratchpad/review-mg6/unpop.py` (mandatory on unpopulated fact type) ->
  exit 0 without `--populated`, exit 3 with it.
- Disposition grep (output in `scratchpad/review-mg6/grep.txt`); `git diff HEAD`;
  `git show HEAD:docs/release-notes.md`; reads of the evolution contract (Additive policy, Shape
  report), extraction contract §4a, representation-format "Unattended source", the
  model-from-text skill's Unattended mode, rule-verbalization reference, `service.py` and
  `discover/output.py`.
- `.venv/bin/zensical build --strict` -> no issues; `tools/check_docs.py site` -> 13393 links
  checked. Note: this wrote the gitignored `site/` build directory in the worktree (ignored by
  `.gitignore:13`, no tracked change; `git status` unchanged).
