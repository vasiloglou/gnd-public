# PyRel tutorials as a pedagogical agent-in-the-loop story

Draft r1, 2026-10-14. Milestone: `pyrel-agent-loop`. Successor to the closed
`pyrel-applications` milestone (PR #21, merged as `a9a2f08`).

Owner request (review of the shipped PyRel pages, 2026-10-14, quoted in
[`README.md`](../README.md)): the pages are "not good"; the shell commands are
ugly; the file-copy Python "is not informative at all"; the material must be
"more educational, pedagogical", emphasize "how the rules are written", show
"rules and constraints written in pyrel as well", and show GND "used with an
LLM or a coding assistant": "what the LLM outputs, how this is checked by the
GND and what it feeds back", "how to use the skills", and "reasoning".

Owner rulings taken in the same session are listed in section 10. The owner
approved this plan by default ("approve the plan by default", 2026-10-14) and
directed that provider keys, if a hosted-model run is wanted, come from the
repository `.env` parsed as data. Planning authorship is not publication or
merge authority.

## Problem and completion predicates

Observed on `a9a2f08`:

- `docs/pyrel-apps.md`, `docs/bookrec/07-native.md`, `docs/expense/04-native.md`
  run every step through `(cd DIR && "$GND_TUTORIAL_GND_PYTHON" -m ... --backend pyrel --pyrel-python "$GND_TUTORIAL_PYREL_PYTHON" --format text)`.
  `tools/run_tutorials.py:150` puts the PyRel interpreter first on `PATH` in
  pyrel-lane blocks, which is why the pages avoid bare `python`.
- `docs/expense/04-native.md:68-86` and `docs/expense/02-application.md:33-52`
  assemble the project with a per-file `shutil.copy2` loop.
- Each chapter shows one rule as a YAML excerpt and one query excerpt. No page
  shows a rule in plain English from the verbalizer, and no page shows a rule
  as a PyRel query. `gnd export pyrel` emits one generic translator plus the
  model text (`src/gnd/export/emit.py`, `src/gnd/export/pyrel_runtime.py`);
  there is no per-rule emitted snippet to quote.
- The "faulty agent" is a shipped candidate the reader injects. No page shows
  a coding assistant's output, GND's check of it, or the feedback. The agents
  section has that loop only for the approvals plan task
  (`docs/agents/plans.md`, `dev-session.md`, `recorded-sessions.md`).
- Amendment A2 D6 of `pyrel-applications` ruled "No LLM call, model key or
  nondeterministic step is added" for those pages.

**Outcome:** the three PyRel pages and the agents section teach, with commands
a reader types, how a rule is written (English, ORM, PyRel), how a PyRel query
computes while GND checks, and how a coding assistant proposes, is checked,
receives feedback and repairs, using the packaged skills. Real Claude Code and
Codex sessions are recorded once as digest-bound evidence; the runnable pages
replay a deterministic stand-in.

The milestone closes only when:

1. **Readable commands.** Every executed command on the three pages is of the
   form `python <project>/app.py ...` or `gnd ...` with no interpreter
   variable, no `cd`, no `--pyrel-python` and no `--format`. The PyRel
   interpreter is named once, in Set up, through `GND_PYREL_PYTHON`.
2. **One copy per project.** No page block copies files one by one. Each
   project is one `copytree` (BookRec) or `gnd codegen` plus one `copytree`
   (Expense), and `gnd conformance` exits 0 on the result.
3. **Rules three ways.** Each chapter shows at least one rule as its
   `provenance.user_quote`, as the verbalizer's sentence, as the ORM
   constraint, and as a hand-written PyRel query that runs and prints the same
   witness GND prints. A `pyrel_oracle` test proves the hand-written queries
   agree with `gnd.api.check` over the shipped corpus.
4. **The agent loop, twice.** Each chapter runs `gnd exp run` with a shipped
   deterministic stand-in whose first attempt is refused with the pinned
   witness and whose second attempt is accepted, and then runs the accepted
   candidate through the PyRel app. Each chapter also shows a recorded real
   Claude Code session (Codex where recorded): task, assistant output excerpt,
   GND feedback, outcome; every quoted excerpt is printed by a runnable block
   from a SHA-256-checked committed file.
5. **Skills shown in place.** Each chapter names the skill a reader would ask
   for at steps 2, 3, 5 and 7, with the prompt, two to four steps the skill
   makes the assistant take (cited from its `SKILL.md`), the artifact, and the
   `gnd` command that checks it. The agents section cross-references the
   chapters instead of duplicating them.
6. **Gates green.** Both tutorial lanes, the strict site build, `check_docs`,
   the prose tests, the focused suites, the full suite classification, and
   `tools/accept_pyrel_applications_install.py` from a fresh install pass with
   updated pins; records retained; PR opened against `main`.

## 0. Binding design rules

| Rule | Requirement |
|---|---|
| PL-R1 Reader-shell equivalence | A page command runs unchanged in the reader's shell after Set up and in the tutorial runner. The runner supplies `GND_PYREL_PYTHON`; it never rewrites page text and never shadows `python`. |
| PL-R2 No live model in pages, tests or CI | LLM calls happen only in `tools/record_pyrel_sessions.py` under a recorded owner gate. Pages replay committed bytes or run shipped deterministic scripts. Supersedes A2 D6 for this milestone only. |
| PL-R3 Quotes are printed, not typed | Every transcript or feedback excerpt shown on a page is produced by a runnable block that checks the file's SHA-256 against `manifest.json` and prints the lines. The `text` fence after it is compared by the runner. |
| PL-R4 Equivalents are labelled | Hand-written PyRel rules are labelled as equivalents of what the checker generates. The checker's program is `gnd export pyrel`; the page never presents hand-written text as emitted text. |
| PL-R5 Pinned witnesses survive | Ada/night `{"$b": "night", "$u": "ada"}`, Ada/read, `{"$a": 800, "$e": 102}`, `[101]`/`[102]` remain the shown refusals. Rule meanings in shipped models do not change; rule changes on pages go through `gnd evolve` on a reader-local copy. |
| PL-R6 Honest evidence | Every recorded run is listed in `results.json`; illustrative sessions are named as such; redaction is one documented substitution; the unredacted digest is recorded. A first-try acceptance is reported as such. |
| PL-R7 Prose gates kept | A2 D7's readability and claim gate (`tests/test_pyrel_learning_path.py`) applies to every page this milestone touches or adds, including the SHA-256 letter-digit rule. |
| PL-R8 One-home and pins | New example scripts are RF7-allowlisted executables outside the layer map (`tools/gnd_layers.json:11`); doc twins are byte-pinned; block counts, wheel inventory and page lists are updated in the same phase that changes them. |

Every phase also discharges or argues inapplicable the process-phase standing
rules (totality, algorithmic bounds, validation order, one policy walk, one
normative home, measurement over argument).

## 1. Scope, sources and authority

In scope: `docs/pyrel-apps.md`, `docs/bookrec/07-native.md`,
`docs/expense/04-native.md`, `docs/agents/*.md`, `zensical.toml` titles,
`src/gnd/export/applications.py` (interpreter default), the two example CLIs,
new example files under `src/gnd/examples/{bookrec,expense}/`,
`tools/run_tutorials.py`, `tools/record_pyrel_sessions.py` (new), tests and
pins named in section 9.

Sources read: the owner's review; `pyrel-applications` plan r1, A1, A2
(`notes/plan-amendment-a2.md` D0–D7, owner rulings O1–O4), records 009–014;
`docs/development/documentation.md`; `src/gnd/examples/approvals/recordings/`
and `docs/agents/recorded-sessions.md` (recording pattern);
`src/gnd/exp/session_contract.py` (schema 6, constraint-satisfaction),
`src/gnd/exp/adapter_policy.py`, `src/gnd/agents.py`; `src/gnd/codegen/plan.py`
(collision rule); the tests listed in section 9.

Authority: the owner's 2026-10-14 rulings (section 10). Delegated approval for
phase gates within this milestone follows from "approve the plan by default";
the live-recording step (PL4) and the merge remain explicit owner actions.
`pyrel-applications` records are cited and never edited. No release,
certification or publication is authorized.

## 2. Contract proposal and product behavior

Public seam: `execute_application(..., *, native_python=None, ...)` and
`check_proposal(..., *, native_python=None, ...)`. `None` reads
`GND_PYREL_PYTHON`; absent or empty → result `exit_code 70`, `reason`
`no PyRel interpreter: pass native_python or set GND_PYREL_PYTHON`; a relative
or missing path keeps the existing reason `explicit native interpreter is unavailable`.
The child environment allowlist is unchanged.

Example CLIs: `--pyrel-python` optional with the same fallback and the usage
error `--backend pyrel needs the PyRel interpreter: pass --pyrel-python PATH or export GND_PYREL_PYTHON=PATH`
(exit 2). `--format` default is `text` when `--backend pyrel`, `json`
otherwise; `--format json` stays available. `--backend` stays explicit.

Launchers: `src/gnd/examples/bookrec/app.py` and
`src/gnd/examples/expense/project/app.py` put their package directory on
`sys.path` and call the CLI `main()`. Reader command:

```sh
python bookrec-native/app.py recommend --user ada \
  --model bookrec-native/model.orm.yaml --input bookrec-native/seed.population.json \
  --output ada.json --backend pyrel
```

Runner: in pyrel-lane blocks `GND_PYREL_PYTHON` is exported from
`GND_TUTORIAL_PYREL_PYTHON`; `PATH` keeps the GND interpreter first in every
block. `GND_TUTORIAL_*` names remain for the harness and receipts.

Rules in PyRel: `rules_in_pyrel.py` per domain, public `relationalai` API
only, prints one line per rule (`<id>  OK` / `<id>  violated  {witness}` /
`<id>  warning  {witness}`) with GND's variable names; exit 1 on an alethic
violation.

Agent loop: shipped `stand_in_agent.py` per domain; schema-6 contract with
`constraint-satisfaction` acceptance and `coverage` floors; `gnd exp run`
exits 0 after two attempts; attempt-1 feedback carries `offending_facts` equal
to the pinned witness.

Recordings: `src/gnd/examples/<domain>/recordings/` in the approvals layout
plus `agent.stdout` per attempt and `transcripts/` for skill invocations.

## 3. Dependencies and artifact homes

Sequence: `PL0 -> PL1 -> {PL2, PL3} -> PL4 -> PL5 -> PL6`. PL2 and PL3 are
independent after PL1. PL4 reuses PL3's contract. PL5 needs PL2, PL3 and PL4
(excerpts). PL6 last.

| Artifact | Home |
|---|---|
| Interpreter default | `src/gnd/export/applications.py` |
| CLIs, launchers, ready folder | `src/gnd/examples/bookrec/{app.py,extension/bookrec/cli.py}`, `src/gnd/examples/expense/{extension.py,project/}` |
| Rules in PyRel, stand-ins, proposals, recordings | `src/gnd/examples/{bookrec,expense}/` |
| Doc twins | `docs/assets/applications/*-rules-in-pyrel.txt`, existing `*-native-query.txt` |
| Runner and recorder | `tools/run_tutorials.py`, `tools/record_pyrel_sessions.py` |
| Pages | `docs/pyrel-apps.md`, `docs/bookrec/07-native.md`, `docs/expense/04-native.md`, `docs/agents/*.md` |
| Evidence | `.gnd-planning/milestones/pyrel-agent-loop/evidence/<phase>/` |

Prerequisites present on `a9a2f08`: pinned PyRel runtime project
(`tutorials/runtimes`, `release_governance/runtime-environment`), schema-6
session machinery, approvals recording pattern, local `claude` and `codex`
CLIs (`/opt/homebrew/bin`). Hosted models are optional and need
`OPENROUTER_API_KEY`, read from `.env` as data only.

## 4. Phases, deliverables, criteria and inherited residuals

| ID | Deliverables | Criteria |
|---|---|---|
| PL0 | This plan, obligations, README, plan-gate record, PL1 spec | PL0-C1 obligations table maps every owner sentence and carried A2 rule to a phase; PL0-C2 owner approval recorded |
| PL1 | Seam fallback; CLI fallback and format default; `app.py` launchers; `expense/project/`; runner env; page commands rewritten (commands only) | PL1-C1 new tests exit 0; PL1-C2 both lanes green for bookrec and expense; PL1-C3 no page block copies files one by one; PL1-C4 no `--pyrel-python`, `--format`, `cd`, or `$GND_TUTORIAL_*` in page commands |
| PL2 | `rules_in_pyrel.py` ×2, doc twins, agreement test | PL2-C1 `pyrel_oracle` agreement over the native-seam corpus; PL2-C2 pinned witnesses printed on the bad candidates |
| PL3 | `stand_in_agent.py` ×2; contract/policy blocks; replay reader; accepted candidate through the app | PL3-C1 `gnd exp run` exits 0 after 2 attempts in both domains; PL3-C2 attempt-1 `offending_facts` equal the pinned witnesses; PL3-C3 attempt-2 candidate passes `check_proposal`/`execute_application` |
| PL4 | `tools/record_pyrel_sessions.py`; owner authorization record; recordings ×2 domains; `tests/test_pyrel_recordings.py` | PL4-C1 every run listed in `results.json`; PL4-C2 digests, no path/key needles, replay bands match; PL4-C3 at least one attempt per domain with `offending_facts`, or the README states none occurred |
| PL5 | Three pages rewritten; `docs/agents` edits; nav titles; prose tests; junior-reader pass | PL5-C1 completion predicates 1–5 observed on the pages; PL5-C2 both lanes, strict build, `check_docs`, prose tests exit 0; PL5-C3 rendered review desktop and mobile, both themes |
| PL6 | Pins and counts; wheel inventory; fresh-install acceptance; close record; PR | PL6-C1 `accept_pyrel_applications_install.py` exit 0 with new constants; PL6-C2 full suite classified; PL6-C3 PR open against `main` |

Inherited from A2 (kept): D0 Snowflake boundary wording; D1 public query seam;
D2 rule changes through `gnd evolve` (now enforced on pages); D3 output shown
for every executed command; D4 chapter order (step 5 renamed "An agent in the
loop"); D5 two-environment setup; D7 readability gate. Superseded: D6 (see
PL-R2). Inherited residual from `014-milestone-close.md`: seven `main` test
failures unrelated to these pages; classify again at PL6, do not fix here.

## 5. Documentation, skill and compatibility surfaces

- `docs/development/documentation.md`: update the PyRel lane paragraph (runner
  exports `GND_PYREL_PYTHON`; bare `python` is the GND interpreter).
- `docs/reference/formats.md` or the applications reference, if any, gains the
  env var and the `--format` default.
- Skills are not edited; pages cite `SKILL.md` steps by heading.
- Compatibility: `--pyrel-python` keeps working and wins over the env var;
  `--format json` keeps the JSON shape; `execute_application(native_python=PATH)`
  unchanged for callers that pass it.

## 6. Risks and required controls

| Risk | Control |
|---|---|
| Claude Code under `acceptEdits` cannot run `gnd check` | Policy adds `--allowedTools "Bash(gnd *),Read,Write,Edit"`; disclosed in the recordings README; owner approves the scope at the PL4 gate |
| Real agents accepted first time | Task variant T2 asks for something the rules forbid; README and page report what happened; no synthetic failure presented as recorded |
| Agent invents facts, band 3 | Page explains band 3 as ill-formed, not a rule failure; replay asserts recorded band |
| Transcript contains workspace paths or keys | Workspace path chosen free of needles; one substitution; `tests/test_pyrel_recordings.py` needle scan |
| `--format text` default breaks JSON consumers | Two `pyrel_oracle` tests pass `--format json`; change noted in records |
| Runner no longer shadows `python` | `docs/runtimes/pyrel.md` and other pyrel-lane pages use `"${GND_TUTORIAL_PYREL_PYTHON:?...}"` explicitly and are unaffected; verified by running every group in both lanes at PL1 |
| Block-count pins drift | Counted at PL6 from receipts; PL5 records them provisionally |
| Review repair hazard | One initial review per phase, one repair round for reproduced blockers, convergence ledger before any second round |

## 7. Out of scope

Snowflake execution or credentials; changing any shipped rule's meaning;
checker semantics; new `gnd` subcommands; editing `pyrel-applications`
records; editing BookRec chapters 1–6 or Expense chapters 1–3 beyond links;
benchmarking or ranking models; release, certification, publication, merge.

## 8. Execution, approval and review protocol

Branch `codex/pyrel-agent-loop` from `origin/main`. Phases run with
`process-phase <ID> pyrel-agent-loop`. The owner's default approval is
recorded as delegated approval for phase specs within this milestone
(`001-plan-gate.md`); the PL4 live-recording step and the PR merge are
explicit owner actions. Each phase: spec, implementation, focused tests, one
independent diff review by the explicitly selected local reviewer, a repair
round only for reproduced blockers, record. Plan and close use the four-local-reader
bar unless the owner rules otherwise; this plan's gate records that the owner
approved by default without readers. Commits per phase; PR at PL6.

## 9. Per-phase verification and affected consumers

| Phase | Commands (exit 0 unless stated) | Affected consumers |
|---|---|---|
| PL1 | `uv run pytest -q tests/test_pyrel_interpreter_env.py tests/test_ready_projects.py tests/test_pyrel_tutorial_experience.py tests/test_documentation_tutorials.py tests/test_rf7_structure.py tests/test_expense_tutorial.py tests/test_bookrec_tutorial.py`; `uv run pytest -q -m pyrel_oracle tests/test_bookrec_pyrel_application.py tests/test_expense_pyrel_application.py tests/test_pyrel_proposal_check.py tests/test_pyrel_native_seam.py`; `uv run python tools/run_tutorials.py --group bookrec` and `expense`; both with `--lane pyrel` and `GND_TUTORIAL_PYREL_PYTHON`; `--group runtime-pyrel --lane pyrel` | `tests/test_bookrec_pyrel_application.py:26`, `tests/test_expense_pyrel_application.py:33` (`--format json`), `tests/test_pyrel_tutorial_experience.py:85-97`, `tests/test_rf7_structure.py:22-31`, `tests/test_pyrel_applications_install.py:35,44` |
| PL2 | `uv run pytest -q -m pyrel_oracle tests/test_rules_in_pyrel.py`; `tests/test_pyrel_tutorial_experience.py` twins | `docs/assets/applications/`, RF7 allowlist |
| PL3 | `uv run pytest -q tests/test_pyrel_stand_in_sessions.py`; page blocks in the offline lane | `tests/test_rf7_structure.py`, wheel inventory |
| PL4 | `uv run pytest -q tests/test_pyrel_recordings.py`; `-m pyrel_oracle` replay through `check_proposal`; `tools/record_pyrel_sessions.py --authorized-by <record>` (owner-gated, once) | `src/gnd/examples/*/recordings/`, wheel size |
| PL5 | prose tests; both lanes; `uv run --group docs zensical build --strict`; `uv run python tools/check_docs.py site`; `--group agent-recorded`, `agent-session`, `agent-model` | `tests/test_pyrel_learning_path.py`, `tests/test_tutorial_output_blocks.py`, `tests/test_development_scaffold.py`, `zensical.toml` |
| PL6 | `uv run python tools/accept_pyrel_applications_install.py --out <fresh>`; `uv run pytest -q` classified against `main` | `tools/accept_pyrel_applications_install.py:67,179`, `tests/test_pyrel_applications_install.py:61,90` |

## 10. Owner decisions and open questions

Owner-decided, 2026-10-14 (chat session, recorded in `001-plan-gate.md`):

| # | Decision | Ruling |
|---|---|---|
| PL-D1 Scope | Three PyRel pages plus `docs/agents` | owner |
| PL-D2 Commands | Env-var interpreter default plus ready project folders; no new `gnd` subcommand | owner |
| PL-D3 LLM loop | Record real Claude Code and Codex sessions as evidence and keep a scripted runnable replay | owner |
| PL-D4 Process | New milestone via `start-milestone`; branch from `main` | owner |
| PL-D5 Approval | Plan approved by default; phase gates delegated within this milestone | owner |
| PL-D6 Keys | If hosted models are recorded, read the one needed key from `.env` as data, never source or print it | owner |

Proposed, to be confirmed at the named phase:

| # | Question | Proposed | Phase |
|---|---|---|---|
| PL-Q1 | `--format` default text under `--backend pyrel` | yes | PL1 spec |
| PL-Q2 | Claude Code tool scope for recording | `Bash(gnd *),Read,Write,Edit` | PL4 gate |
| PL-Q3 | Runs per agent per task variant | 2 | PL4 gate |
| PL-Q4 | Record hosted models too | no, unless both terminal agents are accepted first time on T2 | PL4 gate |
| PL-Q5 | Codex invocation | `codex exec --json` with scratch `CODEX_HOME`; verify against installed version first | PL4 spec |
