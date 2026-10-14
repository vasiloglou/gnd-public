# PA5R — Junior-first PyRel learning path, public query seam, honest claims

Effective plan: r1 + A1 + A2 r3 (`010-plan-amendment-a2.md`). Prerequisite: PA5
`c9432b0`/`009` complete; A2 adopted in `50eba83`. This spec harvests A2 D0–D7,
its sequence/budget sections, PA5-C1..C6, §0 PA-R1..R8, the process-phase
standing rules, prior records 001–010 and the open PA6 state.

## Obligations

| Source | Obligation | Discharge |
|---|---|---|
| A2 D0 | Rewrite Snowflake execution claims: README.md:16-18, docs/index.md:241-242, :259, docs/tour.md:157-158, docs/agents/export-and-review.md:16, docs/agents/index.md:25-26 | Boundary wording; D7 Snowflake rule over these pages (T7) |
| A2 D1 | Public seam in the emitted program; both queries use only it + documented relationalai | `open_app`/`run_app`/`NativeApp` in pyrel_runtime.py (below); T1 name pin, T2 behavior identity |
| A2 D2 | Expense native chapter needs no rename/package surgery beyond chapter 2's own steps; no sixth shipped model | Fresh `expense-native` built with chapter 2's `gnd codegen` + install step; meal cap on a reader-local copy (amendment D2-a below) |
| A2 D3 | Shown command + checked output; normalization; one command per block; semantic lines shown | Runner `output=` grammar (below); T4, T5 |
| A2 D4 | Ten-step chapters, overview page, keep-list | Pages below; T6, T8 |
| A2 D5 | Both environments, hello checks, packaged runtime copy, outside runner | Overview "Set up" section; hello blocks in chapters |
| A2 D6 | Candidate producer as agent slot; faulty-agent step says it is injected; exp run as separate contract | BookRec `--proposal`; Expense `--chain`; wording checked by T7 |
| A2 D7 | Readability + claim gate with exact term list, 90 words, output, Snowflake, required sentences | `tests/test_pyrel_learning_path.py` (T7) |
| A2 sequence | PA5 → PA5R → PA6; PA6 re-gated, remaining repair slot | Record + README; PA6 constants untouched here (O-PA6 below) |
| PA5-C1 | Native blocks run sequentially in clean dirs, semantic outcomes asserted | Checked output carries disposition/rule/witness; native groups run (G2) |
| PA5-C2 | Offline paths still run; native skips labeled | Offline groups run (G1); existing skip controls |
| PA5-C3 | Policy home, query role, completion ≠ acceptance, deliberate bad candidates | Step 1 table, step 3, step 5 (`--proposal`, checker `--accept` on Ada/read) |
| PA5-C4 | Strict site build + links; desktop/mobile inspection; snippets from shipped code | `zensical build --strict`, `tools/check_docs.py`; browser review; snippet twins (existing test) |
| PA5-C5 | Six graphics bound to shipped facts/rules/results | SVG and checkpoint bytes unchanged; seam proven output-identical (T2); existing graphic tests |
| PA5-C6 | Rendered desktop/mobile, both themes, accessibility | Retained screenshots of both native pages and overview, 2 widths × 2 themes |
| PA-R1 | Native checks execute PyRel; no GND evaluator relabeled | `--proposal` pyrel path uses the exported PyRel checker, not `api.check` |
| PA-R2 | Complete checking; unknown ≠ empty | Seam keeps admission, coverage and derivation handling unchanged |
| PA-R4 | Acceptance never inferred from audit exit | Text summary derived from the verified result object only |
| PA-R5 | Exact staged bytes, inputs preserved, refusal after generation | `--proposal` captures and digest-binds proposal bytes; `_preserve_source` runs before checking |
| PA-R6 | Local, bounded, no remote | Seam has no connection parameter; version pin and limits retained |
| PA-R7 | One semantic home; layer map | Seam inside existing mapped module; checker stage factored, not duplicated |
| PA-R8 | Skips are not passes; no universal claims | Unchanged runner skip semantics; D7 claim rules |
| Standing 1 Totality | New consumers total over arbitrary JSON | `format_result` tolerates any result dict (T3 hostile cases); runner output parser refuses malformed markers |
| Standing 2 Bounds | Work proportional to input bounded | No new algorithmic work; normalization is linear in captured output |
| Standing 3 Order | Validation order per boundary | `--proposal`: output-exists → interpreter → captures → model load → preserve-source → checker → verify → publish (source-order pinned, T3) |
| Standing 4 One walk | One policy walk | Checker unchanged; seam does not re-implement admission |
| Standing 5 One home | Normative prose has one home | Setup lives only on the overview; chapters link to it |
| Standing 6 Measure | Contested representations measured | Output identity vs captured checkpoints (T2) |

## Interfaces

### D1 seam — `src/gnd/export/pyrel_runtime.py` (emitted program)

```python
class NativeApp:
    model            # the relationalai Model; use model.where/.select/.distinct directly
    source           # deep copy of the admitted input population (read-only use)
    derivations      # tuple[str, ...] of derived fact types, in profile order
    def has(self, fact_type: str) -> bool
    def ref(self, fact_type: str, role: str)          # fresh typed variable for that role
    def match(self, fact_type: str, **roles)          # atom over an asserted or computed fact type
    def relationship(self, name: str, **fields)       # fields: role name -> relationalai type
    def rows(self, query) -> list[list]               # bounded, sorted
    def check_work(self, estimate: int, what: str) -> None   # ProfileRefusal over the work limit
    def candidate(self) -> dict                       # copy of source with computed facts filled
    def propose(self, candidate: dict, calculation: dict) -> None
    def refuse(self, kind: str, reason: str) -> None

def open_app(population_path, output_path) -> NativeApp
def run_app(handler, argv) -> int    # argv = [population, output, *args]; exit 0/2/3/70
```

`open_app` performs, in order: byte cap, parse, `admit_model`, `admit_population`,
copy + derived-head coverage (refuses `coverage-not-declared`), `_profile_admit`,
version pin, `ApplicationOracle(..., config=local_config())`. `propose`/`refuse`
write the existing envelope with the existing binding digests. `run_app` maps
`ValueError`→3, `ProfileRefusal`→2, other→70, printing ≤300 chars to stderr —
identical to today's `main()` functions. No connection parameter. Existing
private names are untouched; RF1/RF2 pins stay green.

Each `native_query.py` becomes: imports, a `calculate(app, *args)` handler using
only the seam plus `relationalai.semantics` (`String`, `std.aggregates`), and
`main()` = `runpy.run_path(argv[1])['run_app'](calculate, argv[2:])`.

### D6 proposal checking — `src/gnd/export/applications.py`

`check_proposal(model_path, input_path, proposal_path, output_path, *, native_python, owned_relations)`
captures model, input and proposal bytes (`source_binding` gains `proposal_sha256`),
runs `_preserve_source(model, input, proposal, owned_relations)`, then the same
checker stage as `execute_application`, factored into one private helper used
by both. `calculation` stays `None`. BookRec CLI gains `--proposal FILE`
(pyrel and gnd backends; `--user` not required with it).

### Human summary — `format_result(result, *, kind)` in `applications.py`

Both CLIs gain `--format text` (default `json`, unchanged). Lines, derived only
from the result dict, total over any input:

```
Proposed for ada: cosmos, map              (BookRec, when a calculation exists)
Checking the agent's proposal: ada/night, ben/night   (BookRec --proposal)
Report: 3 submitted, 1 approved, 2260 EUR  (Expense, accepted report only)
Policy check: ACCEPTED | ACCEPTED with 1 warning | REJECTED | REFUSED (<reason>)
  warning   preferred_genre {"$u": "ada", "$b": "cosmos", "$g": "science"}
  violated  age_appropriate {"$u": "ada", "$b": "night"}
Published: <output as given> | Nothing was published.
```

### D3 runner grammar — `tools/run_tutorials.py`

`<!-- gnd-run expect=N [lane=x] [output=stdout|stderr] -->` + one `sh`/`python`
fence; with `output=`, the next fence must be ```` ```text ````, compared
after normalization: run directory → `<run>`, `gnd-native-(application|checker)-\w+`
→ `<tmp>`, `\d+\.\d+s` elapsed → `<time>`, trailing whitespace. A line `...`
in the expected text matches any run of lines. Marker count invariant, receipts
and skip semantics unchanged; receipts add `output_checked: bool`.

### D7 gate — `tests/test_pyrel_learning_path.py`

Full rules on `docs/pyrel-apps.md`, `docs/bookrec/07-native.md`,
`docs/expense/04-native.md`; Snowflake rule only on the six D0 locations' files.
Terms, 90-word paragraphs, output-on-every-marked-block, Snowflake paragraph
boundary, required runtime sentence and passing-check meaning, distinctions
present ("warning", "not accepted", "unknown"). Exit codes allowed only inside
the troubleshooting table rows.

## Decisions (delegated)

- **D2-a (amendment to A2 D2).** Measured: `gnd evolve` supports constraint
  `modify` via `ConstraintLocator`, but the meal-cap change would need a new
  proposal builder (`prepare_currency.py` only emits `add`), a linked project
  roster and preview/apply — three or more extra commands that bury step 7's
  point for a junior reader. Ruling: the reader edits a private copy in one
  visible, explained block that names the rule and the value (75 → 50), with a
  sentence sending shared-model changes to `gnd evolve` (chapter 3). Prior
  answer (evolve path) retained here; no shipped model added.
- **D3-a.** `output=` also applies to `python` fences (copy steps print a line),
  so D7's "every command shows output" is satisfiable.
- **O-PA6.** PA6's committed constants are not edited here; they go red after
  PA5R by design and are updated at PA6's new spec gate.
- **Overview location.** `docs/pyrel-apps.md`, nav under Tutorials first; it has
  no runnable blocks, so runner groups are unchanged.

## Tests and verification ledger

| Id | Test | Expected |
|---|---|---|
| T1 | PyRel lane: emitted program exposes exactly the seam names; private names still resolve | red before D1, then 0 |
| T2 | PyRel lane: rerun the captured checkpoint commands; calculation and policy equal the committed checkpoints | 0 before and after (identity) |
| T3 | `format_result` hostile dicts; `check_proposal` order + refusal cases (output exists, changed fact inventory, Ada/night rejected, no publish) | red first, then 0 |
| T4 | Runner: output match, mismatch fails, `...`, normalization, missing text fence refused | red first, then 0 |
| T5 | Both native groups' pages parse; every marked block in the two chapters has `output=` | red first, then 0 |
| T6 | Existing tutorial tests (`test_pyrel_tutorial_experience`, `test_documentation_tutorials -k 'bookrec or expense'`, `test_external_runtime_tutorials`, `test_bookrec_pyrel_application`, expense native tests, RF1 pins, pyrel export tests) | 0 |
| T7 | D7 gate | red before page rewrite, then 0 |
| T8 | `tools/run_tutorials.py --group bookrec/expense` offline and `--lane pyrel` | 0 each |
| G | `zensical build --strict`; `tools/check_docs.py`; ruff on touched files | 0 |
| V | Browser review, 3 pages × desktop/mobile × light/dark, figures readable | retained PNGs |

Deferred: PA6 install harness (expected red until re-gated), broad replay.

## Budget and review

Seam ≤ 140 lines; applications.py additions ≤ 90; runner ≤ 70; new tests ≤ 260;
each native chapter ≤ 260 lines; overview ≤ 140. No new dependency, no SVG
change. One Claude Code read-only phase review plus at most one repair; the
junior-reader pass is an extra reading by the same instrument listing every
claim with its evidence.

## Out of scope

Snowflake execution, LLM agents, model/corpus/answer changes, checker semantics,
graphic redesign, earlier chapters beyond the D2 install line, PA6 constants,
merge, release, certification.

Delegated approval (auto=true), 2026-10-13: preceding spec SHA-256 f20de63e363394a703b9296a5247d0213ccf45d2a06ee63daaf53119d21fa7bf. Authorization: owner chose auto=true for A2 and said "yes" to starting PA5R in chat; named milestone delegation persists. Implementability sweep located the oracle (pyrel_runtime.py:1477), the driver and candidate_transform hook (applications.py:145-245), the runner marker grammar (run_tutorials.py:17-31), chapter 2's install layout (02-application.md:35-52), chapter 3's in-place evolution (03-evolution.md:164-185) and the docs build (uv run --group docs zensical build --strict). D2-a and D3-a are delegated amendments within A2 scope; prior answers retained above. Instrument: spec prose; optional spec panel omitted. Red-first controls T1, T3, T4, T5, T7 before implementation. One Claude Code read-only review plus at most one repair. No merge, release or certification.

## Implementation findings

Recorded as found, 2026-10-13:

- F1 Identity measured. Before the seam, 12 checkpoint comparisons (4 BookRec, 8 Expense: calculation, policy, exit, acceptance, publication, guard refusal, candidate bytes) pass on the old queries; after the rewrite the same 12 pass unchanged. The chain-limit checkpoint is a report on invalid-chain.population.json, not an approve run (my first mapping was wrong; corrected before implementation).
- F2 Emitted-program bytes changed by design (A2 D1). tests/test_rf2_pre_move_pins.py follows an authenticated successor chain; PA5R adds evidence/PA5R/pyrel-successor.json (before = PA4 after, after = 9c4990a3…/98699 bytes) and tests/support/pyrel_application_successors.py extends only the rendered-bytes chain (RENDER_PHASES). Query-policy chains are unchanged and still green.
- F3 Pre-existing, not PA5R: tests/test_rf7_structure.py::test_complete_routing_and_dirty_controls and the pyrel_oracle test tests/test_pyrel_constraint_oracle.py::test_decided_verdicts_agree (ring_fail rel_reflexive) fail identically on a clean HEAD 50eba83 worktree. evidence/PA5R/preexisting-failures.txt. Open question for the milestone close; the seam avoids adding JSON parsing calls (copy.deepcopy).
- F4 Version-pin control moved with the pin: tests/test_bookrec_pyrel_application.py now patches importlib.metadata.version, which open_app reads at call time; the control still exits 70.
- F5 Witness key order in shown output is the checker report's sorted order ({"$b": "night", "$u": "ada"}); values are the A2 keep-list values.
- F6 Accepted read-only reports print no publication line (nothing is published by a report); all other non-published results print "Nothing was published.".
- F7 Exporter-level pages (README, index, tour, agents pages) need a boundary that fits plain gnd export, which also refuses remote connections: "not yet supported by gnd export" is added to D7's boundary phrases. Applications pages keep the A2 wording.
- F8 Overview nav label "PyRel + GND: rules to a checked app"; chapter nav labels renamed to match the new titles.
- F9 Meal-cap private copy changes only the comparison value; the run proves the checker accepts the edited model and rejects meal 101 at 60 EUR.
- F10 Budget overruns, measured: applications.py +152/-26 (budget 90), new tests 436 lines (260), BookRec chapter 269 and Expense chapter 314 lines (260). Causes: every executed step now carries a shown output fence; format_result is total over arbitrary input; four red-first test lanes. Seam 106 (140), runner +47 (70), overview 69 (140) are within budget. Delegated amendment (auto=true): accept these measured sizes; no further growth without a new ruling.

## Review triage (notes/phase-PA5R-claude-review.md), 2026-10-13

Reproduced before fixing; regression tests red first (evidence/PA5R/repair-red.txt).

| Finding | Class | Disposition |
|---|---|---|
| B1 gnd-backend --proposal skips input preservation | blocking | Reproduced by reading cli.py. Fixed: --proposal requires --backend pyrel (its only purpose is PyRel checking); test_gnd_backend_proposal_preserves_input |
| B2 Expense setup not chapter 2's | blocking | Fixed: copy to expense-native-demo, gnd codegen, chapter 2's install loop plus native_query.py; conformance measured exit 0 on that layout |
| B3 meal-cap edits a JSON path | blocking | Delegated ruling (auto=true), explicitly overriding A2 D2's sentence "Hand-editing JSON paths inside the chapter's code is not allowed" for this one exercise: evolve needs a new proposal builder, roster and preview/apply (D2-a). The page now names the path in prose, reads and prints the old value, and points shared-model changes to gnd evolve. Prior answer retained in D2-a |
| B4 format_result not total | blocking | Reproduced (three TypeErrors). Fixed with _list/_text; test_format_result_total_over_review_shapes |
| B5 blocks cannot be pasted in order | blocking | Fixed: every app command in a subshell; Python-block instructions in both chapters; stay-in-folder in the overview |
| H1 receipt status before output check | hardening | Reproduced. Fixed: status decided after both checks; test_receipt_status_reflects_output_mismatch |
| H2 candidate cap only on one path | hardening | Fixed: cap in _check_and_publish; test tightened and shown red |
| H3 multi-line reason; wrong BookRec row | hardening | Reproduced. Fixed: _text flattens; troubleshooting rows now match real outputs (ProfileRefusal coverage row) |
| H4 source not a copy; kind= dropped | hardening | source is a deep copy; kind= dropped as unnecessary (shape is inferred from the result), recorded drift |
| H5 hard-coded "was 75" | hardening | Fixed: printed from the model |
| H6 stray text after unchecked command | hardening | Implemented, then declined: agents/dev-session.md and agents/recorded-sessions.md use illustrative text after unchecked commands (measured red). PA5R pages are covered by the output= requirement test |
| H7 D7 gate weaker than A2 | hardening | Exit-code rows must sit in Troubleshooting with plain cause and fix; next-steps links tested on all three pages. Overview setup commands are not executed by design (A2 D5) |
| H8 D0 "yet"; "enterprise data" | hardening | "not yet supported" kept (honest: exporter returns 64). "enterprise data" removed from docs/agents/index.md |
| H9 F3 prose-only | hardening | Clean-HEAD transcript retained from the local CI run of 50eba83 |
| C1 next steps | completeness | Fixed on all three pages |
| C2 Expense plain-Python row | completeness | Fixed |
| C3 seam undocumented | completeness | Fixed: "The query toolkit" section in docs/pyrel-apps.md |
| C4 screenshot coverage | completeness | Remaining combinations captured after the final pages |
| C5 Expense candidate-byte identity | completeness | Deferred: no shipped Expense candidate files; calculation/policy identity holds for all 8 Expense checkpoints |
| Junior stuck list 1-12 | completeness | 1 uv venv --python 3.13; 2 stay-in-folder; 3,4 B5; 5 toolkit + step 3 prose; 6 $-variable gloss; 7 Ben/night explained; 8 echo $? and covers explained; 9 H3; 10 reworded; 11 B2; 12 path named in prose |

F11 Emitted bytes changed again by the H4 repair; the PA5R successor's "after" is refreshed to 56c4e7c2…/98735 bytes before commit.

## Repair review dispositions (notes/phase-PA5R-claude-repair-review.md)

The repair reading confirmed B1, B2, B4, B5 and H1–H5, H7, H8 resolved, accepted the H6 decline, and accepted B3 as a ruling that must be shown to the owner at milestone close (carried to the record's open questions). Its remaining findings, all handled without a third reading:

- N1/N2 and H9: the earlier "final" transcripts predated the last runner edit, and the H9 triage line overstated what was kept (prose only). Corrected: closing transcripts (*-closing*) were produced on the final tree; pre-existing failures now have a clean-HEAD transcript and a full offender comparison (evidence/PA5R/preexisting-failures*.txt, rf7-all-offenders.txt).
- N3: a missing owned relation no longer raises KeyError; regression shown red then green.
- N4: proposals use a dedicated `check` command; `check` and `--proposal` require each other.
- N5: toolkit table lists has/derivations/check_work; the main() wording corrected.
- N6: totals print as "2260 EUR total" in both modes. N7: status column widened to 11.
- Junior points 1–6: Python blocks run from a saved file (no paste/Ctrl-D); saved path explained; troubleshooting rows for FileExistsError and gnd not on PATH; Expense step 3 explains app.ref and aggregates; `check` replaces `recommend --proposal`.
- H4 drift: the interface sketch above lists format_result(result, *, kind); the shipped signature is format_result(result). Recorded, not changed.
