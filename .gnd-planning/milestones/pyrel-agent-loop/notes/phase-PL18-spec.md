# Phase PL18 spec: GSD-style pages for the plan apps, built from real runs

## 1. Status

Delegated approval (auto=true), 2026-10-15. Owner rulings:
- the C2 mockup ("it looks great");
- "approve the plan by default";
- C6: "I would show the rules expressed in pyrel";
- "you should finish P16 and P17".

Checkpoint C8 is the Course tutorial page rendered from real files, shown before
the other pages are written.

## 2. Provenance

- **A1 targets:** PL18 row (:426); §README and home page (:40-50); tutorial
  shape (:52-84); §What moves where (:89-96); §Replays (:169-182); §Figures
  fix (:184-190); §Tests that change (:202-212); the PyRel and requirements
  appendices (:391-399, :460-478); feasibility (:314-329).
- **PL7–PL11 never ran.** Record 012 reordered the work, so their page
  obligations land here.
- **Harvest of 2026-10-15** (one Explore agent, read-only). It found that the
  following do not exist:
  - `gnd export pyrel --explain` (PL12 replaced it with `--rules`, and the
    apps' `rules` command prints the requirements);
  - `tools/render_replay.py`;
  - any recording of Claude Code running a GND skill;
  - `gnd[pyrel]`.

  The plugin marketplace does exist (`.claude-plugin/`, `/gnd:<skill>`).
- **The PL17 recordings:**
  - Course: one run was refused on a rule and then accepted
    (`llama-3.2-3b/course/run-2`).
  - Access and Trip: several such runs.
  - Clinic and Lease: none.

## 3. Obligations

| Source | Obligation | Discharge |
|---|---|---|
| A1 :426 | Course and Clinic as tutorials; Access, Trip, Lease as How-to pages; an Explanation page | §6.2-§6.4 |
| A1 :40-50 | Home page: "How it works" as the loop, Quickstart with the plugin and one prompt, shell only for PyRel | §6.1 |
| A1 :52-84 | Eight steps, each with You type / Claude Code does / You get / GND says | §6.2 |
| A1 :150-156 | The replay is the first run in recording order that is refused on a rule and then accepted, and the page names it; if none, say so and label any stand-in as scripted | §6.2 (Course, per-example rule), §6.3 (Clinic: none) |
| A1 :169-182 | Replays are rendered from committed, SHA-256-checked recordings: animated SVG, static final state for reduced motion, text transcript in a disclosure | §6.5 |
| A1 :391-399, :460-478 | Pages show each rule's requirement and say which lowering ran: the LQP program's `require`; locally, DuckDB violation queries | §6.2 step 3 |
| C6 owner remark | The rules in PyRel are visible, not collapsed | §6.2 step 3 (answers mockup question 3) |
| A1 :314-329 | "the plan is refused at step N"; no live clock (Clinic's "today" is a dated fact); each page says which checker checked | §6.2-§6.4 |
| A1 L6, L7 | Lease: anchoring is `gnd verify`, GND only. Clinic: the textual rule is reported as not checked | §6.4, §6.3 |
| A1 :184-190 | Figures fix: no Markdown image right after `<div markdown="1">`, with a failing test | §6.6 |
| PL-R2, PL-R3 (main plan) | No live model in pages, tests or CI; quotes come from committed files, never typed | §6.5, §8 |
| PL-R7 | Prose gates apply to every new page | §8 |

## 4. Standing rules, bound

1. **Honest evidence.** Every session, verdict and plan on a page comes from a
   committed file. Session text is included verbatim (`--8<--` from a docs
   twin, byte-equal to the recording). The page says which run it is.
2. **No live calls.** Runnable blocks use the GND checker and the stand-in bots
   only.
3. **Bounds.** Replays stay under 60 KiB each. The new pages run in their own
   runner group under 120 s.

## 5. What the reader sees

- **Home page** (`docs/index.md`):
  - What is GND;
  - How it works, eight lines with the slash commands;
  - Quickstart (`/plugin marketplace add vasiloglou/gnd-public`,
    `/plugin install gnd@gnd-marketplace`, then one prompt);
  - Documentation in Tutorials / How-to / Reference / Explanation;
  - Why it works.

  The existing hero stays, and its caption links to the Course tutorial.
- **Tutorials:**
  - `docs/tutorials/course-planner.md`;
  - `docs/tutorials/clinic-refills.md`.
- **How-to pages:**
  - `docs/how-to/access-requests.md`;
  - `docs/how-to/trip-budget.md`;
  - `docs/how-to/lease-schedule.md`.
- **Explanation:** `docs/explanation/rules-as-pyrel.md`, "How a rule becomes a
  PyRel check", built from `app.py rules` and the generated programs.
- **Recorded runs:** `docs/how-to/model-runs.md`, the PL17 results table and
  how to read a run.

## 6. Design

### 6.1 Home page and README
- **Home page.** The mockup's order. "How it works" names the loop:
  1. rules;
  2. `/gnd:gnd-model-from-text`;
  3. the bot;
  4. ask;
  5. plan;
  6. check;
  7. execute or repair;
  8. `/gnd:gnd-model-evolve`.
- **Quickstart prompt.** "Open the GND course planner example and plan Maya's
  spring semester." The plugin skills read the example's README.
- **README.** It gets the same "How it works" and a link to the tutorials. The
  fallback-limit sentences stay, as pinned.

### 6.2 Course tutorial (eight steps, mockup C2 shape)
1. **Write the rules.** `rules.md`, included verbatim.
2. **Model them.** Typed: `/gnd:gnd-model-from-text rules.md`.
   - Shown:
     - a replay of a recorded Claude Code session running the skill (§6.5,
       gate 019);
     - the model's sentences from GND's verbalizer;
     - `gnd validate` exit 0, as a runnable block.
   - The page says the tutorial continues with the shipped model, which may
     differ from yours.
3. **Read the rules as PyRel.** `python course/app.py rules` is a runnable
   block, shown in full. A table pairs each registrar sentence with its
   requirement. One paragraph says which lowering is shown and which runs
   locally.
4. **Ask the bot.** The question, typed.
5. **It proposes a plan.** From `llama-3.2-3b/course/run-2`, attempt 1. This is
   the first Course run, in recording order, refused on a rule and then
   accepted; the page names it.
6. **GND checks it.** The verdict as printed, plus one sentence on the witness:
   "the plan is refused at state 1".
7. **Repair and execute.** Attempt 2 and the published state.
   `app.py check plans/...` runs as a block for the stand-in's version.
8. **Change a rule.** `gnd evolve preview` and `gnd evolve apply` with a shipped
   proposal (term load 6 → 4). The same plan is then refused. Runnable.

Also: "What you did"; and a link to the full results table, which says that
Claude models were accepted at the first attempt.

### 6.3 Clinic tutorial
The same eight steps, plus three Clinic-specific points:
- "today" is a dated fact;
- dates with `date_add`;
- the textual rule is reported as not checked.

No Clinic run was refused on a rule and then accepted, and the page says so. The
repair shown is the stand-in's, labelled scripted. The real runs appear in a
table.

### 6.4 How-to pages
Each page follows the mockup's how-to shape: Before you start, Ask, Read the
refusal, The repaired plan.
- **Access:** replay `llama-3.1-8b/access/run-1`, and Haiku's decline.
- **Trip:** replay `llama-3.1-8b/trip/run-2`. It notes that a plan can pass
  the rules and still under-answer the question.
- **Lease:** Claude's type refusal (exit 3) and its repair; anchoring is
  checked by `gnd verify`, GND only.

### 6.5 Replays (`tools/render_replay.py`)
- **Inputs:**
  - (a) a plan-app `session.txt`;
  - (b) a Claude Code `stream-json` transcript.
- **Output.** An SVG in the hero's visual language: a terminal card whose lines
  appear in order through CSS animation, with the final state static under
  `prefers-reduced-motion`.
- **Accessibility.** Every replay is followed by a `<details>` holding the
  verbatim text transcript.
- **Built from committed files only.** `--check` re-renders and compares bytes.
- **Skill sessions (gate 019).** Claude Code (account default and haiku), 2 runs
  each, runs `/gnd:gnd-model-from-text rules.md` in a scratch folder holding
  only the Course `rules.md`, with the plugin's skills installed. The run is
  recorded as stream-json, with the same redaction and leak search as PL17.

### 6.6 Tests and pins
- **New runner group `plan-apps`** over the new pages. It runs `rules`,
  `check`, `validate` and `evolve`. No model is called.
- **New `tests/test_plan_app_docs.py`.** It checks:
  - every included session file is byte-equal to its recording;
  - each page names its replayed run, and that run satisfies the A1 rule;
  - no `python` fence appears on a Tutorials page;
  - every replay is followed by a transcript disclosure;
  - prose rules (no "exit N" in prose outside tables, paragraphs of at most
    90 words).
- **New `tests/test_replays.py`.** Re-render equality, `role="img"`/title/desc,
  and the reduced-motion rule.
- **Figures fix.** A failing test for a Markdown image right after
  `<div markdown="1">`, then the four sites are fixed.
- **Acceptance tool.** `tools/accept_pyrel_applications_install.py` copies
  `plan_apps` too, so snippets resolve in the installed docs build.

## 7. Decisions

| # | Question | Ruling |
|---|---|---|
| D1 | Mockup Q1, the four-part step | kept (approved shape) |
| D2 | Mockup Q2, replay animation | plays once when shown; the final frame is static under reduced motion; transcript always available |
| D3 | Mockup Q3, PyRel weight | visible (owner remark C6) |
| D4 | Mockup Q4, first tutorial | Course first; BookRec and Expense stay as they are |
| D5 | `--explain` | not added. `app.py rules` and `gnd export pyrel --rules lqp` show the requirements |
| D6 | Mockup step 3, codegen | not shown as generating this bot. The apps share a hand-written core; a How-to line points to `/gnd:gnd-codegen` for your own model |
| D7 | Moving BookRec ch7 and Expense ch4 to Reference, and per-skill How-to pages | deferred (PL18-Q1). Out of this phase's size, and pinned by acceptance counts |
| D8 | Skill-session recordings | gate 019, Course only, 4 runs |

## 8. Tests

| # | Case | Expected |
|---|---|---|
| 1 | runner group `plan-apps`, offline lane | exit 0 |
| 2 | `tests/test_plan_app_docs.py` | pass |
| 3 | `tests/test_replays.py`, with each replay's `--check` | pass |
| 4 | figures test fails before the fix, passes after | pass |
| 5 | strict docs build, `tools/check_docs.py site` | exit 0 |
| 6 | existing prose and learning-path tests, `test_development_scaffold` references | pass |
| 7 | rendered review of the Course page, desktop and mobile, both themes | screenshots |

## 9. Out of scope

- Rewriting BookRec and Expense.
- Per-skill How-to pages.
- Snowflake.
- Model fidelity (PL16-Q1).
- Live model calls in pages or CI.

## 10. Approval instrument

This prose and checkpoint C8 (the Course page, real files), as delegated
approval (auto=true).

## 11. Amendments during implementation and after review (delegated approval, auto=true, 2026-10-15)

| # | Amendment | Why |
|---|---|---|
| A1 | Step 8 lowers the credit cap (18 → 6) for every student instead of the term load (6 → 4) | a 2-3 course plan never meets a 4-course cap, so the term-load change could not refuse the plan step 7 accepted. The first wording ("part-time students") did not match the model and was corrected after review (B7) |
| A2 | D2 reads "plays once when the page loads" | an inline SVG animates on load; starting on scroll would need script |
| A3 | The one-prompt Quickstart ("Open the GND course planner example ...") is not offered | no packaged skill opens the examples, so the prompt is not backed by anything a reader could check. The Quickstart links the tutorial instead |
| A4 | Pages name the checker: the recorded runs were checked by the DuckDB program, the runnable blocks by GND's checker | review H10 |
| A5 | Every page names the run folder it replays; the clinic and lease pages say no run was refused on a rule and then accepted, and label the stand-in as scripted | review H2, A1 protocol |
| A6 | The skill-session replay's transcript is labelled condensed and links the full session | review H4 |
| A7 | Clinic: the page states the model's gap (no rule ties a refill to the day) shown by `claude-haiku/clinic/run-3`, and drops the false "today is a fact" claim | review B2; the state holds no such fact |
| A8 | The skill recorder resolves its workspace path, parses result events reliably, and keeps tool output only for a plain `gnd` command | review B3, H6, H7 |
