# Milestone Records and Station Commits

**The normative contract** for how a consuming project records completed GND stations and commits them — the `.gnd-planning/` directory, the per-station record file, and the commit grammar. Every workflow skill links here at its gate; none restates this text (D-07).

**Scope — who this binds.** This contract binds the **driving agent** working in a consuming project (a repository where GND skills run, like an expense tracker built with GND). It never binds the `gnd` CLI: `gnd` itself never reads, writes, or is aware of `.gnd-planning/`, and it never touches git. The record and the commit are the driving agent's acts, performed after a skill's own gate has spoken — they add no authority to any gate result and change no claim.

Cross-references:
- Which station a skill owns and where its gate lives → [`../../gnd-solve/SKILL.md`](../../gnd-solve/SKILL.md)
- The directory this contract writes into is scaffolded once, by [`../../gnd-new-project/SKILL.md`](../../gnd-new-project/SKILL.md)

## When a record is due — the two lanes

Not every station run earns a record. The driving agent works in one of two lanes, chosen by risk, and names the lane in one line at the gate when it matters:

**Fast lane — the default for routine, reversible work.** Direct edits, focused tests, a smoke run where one applies. No station record, no station commit, no experiment, no panel. The evidence is the working tree and the validators' own exit codes. Ask the user for a decision only when a choice materially changes scope or is hard to reverse.

**Evidence lane — entered when risk justifies it.** A full experiment for genuine convergence or agent-behavior uncertainty; conformance when a model or generated surface may have drifted; a review panel for destructive, ambiguous, security-sensitive, or high-blast-radius decisions; and a durable milestone record for each such **material event** — a published model, a closed experiment, an accepted evolution, a panel run, a refusal that taught something.

Two rules keep the lanes honest:

- **Prefer milestone-level records over per-station ones.** A run of routine stations that ends in one material event takes one record citing the run, not a record per station. A round-trip case suite takes **one batched record** naming every case and its band verbatim — never one record and commit per case.
- **A commit needs the user's explicit go-ahead.** The record and the commit are the driving agent's acts, performed only on the user's authorization — never implied by a green exit, and never performed by `gnd`.

The lane choice gates the *record*, not the discipline: whichever lane a station ran in, its own gate command and exit band are what they are, and neither lane adds authority to a claim or waives a skill's Limits.

## The `.gnd-planning/` directory

`.gnd-planning/` sits at the consuming-project root and holds all GND planning artifacts. It is created exactly once, by [`../../gnd-new-project/SKILL.md`](../../gnd-new-project/SKILL.md) — no other skill creates it, and a skill that finds it absent offers `gnd-new-project` rather than scaffolding ad hoc. The name is deliberate: a repository may also carry a `.planning/` directory belonging to GSD or another framework, and the two must never be confused — GND artifacts go under `.gnd-planning/`, nowhere else.

Layout:

```
.gnd-planning/
  PROJECT.md                          # one-pager: the problem, in the user's words
  milestones/
    <milestone-name>/                 # e.g. v1, v2-multi-currency
      001-model.md                    # one record per material event (evidence lane)
      002-synth.md
      003-codegen.md
      ...
```

The directory is **append-only**. A record is never edited after its commit — a correction is a **new** record, with the next number, citing the record it corrects by path and sha256. Deleting or rewriting a record destroys evidence the same way editing a retained attempt would.

## Record file naming

`NNN-<scope>.md`, where `NNN` is monotonic within the milestone (001, 002, …) and `<scope>` is the same scope token the commit uses (table below). The number orders records within a milestone; the scope names the station. Two runs of the same station produce two records with two numbers — never a second write to the first.

## Record file shape

An optional `covers:` list may follow `evidence:` in the frontmatter, naming
the model elements this record's work bears on, in the address grammar of
[`coverage-and-element-addressing.md`](coverage-and-element-addressing.md).
**Nothing validates this field, and nothing reads it today** -- `gnd coverage`
reads experiment `SPEC.md` files and explicitly named payloads, never milestone
records. `covers:` here is a human-readable claim awaiting a reader that may
never be built; if one ever is, malformed entries surface as unmatched rows in
the coverage view, never as errors here. A `covers:` line is a claim, not a
measurement (A5) -- writing it does not make it true, and omitting it does not
make work uncovered.

```markdown
---
milestone: v1
station: 3                # which unit of work produced this record: a gnd-solve
                          # station number, "roundtrip", or a free-form string for
                          # work outside the station loop (a milestone phase, a
                          # repair pass) -- e.g. "phase-6a". Free-form names the
                          # work; it is never a substitute for the scope token
skill: gnd-codegen
scope: codegen            # == the commit scope token and the filename token
date: 2026-08-19
gate:
  command: "uv run gnd codegen model.orm.yaml --out project/"
  exit: 0
evidence:
  - path: project/.gnd-codegen.json
    sha256: <64 hex, recomputable with shasum -a 256>
  - path: model.orm.yaml
    sha256: <64 hex>
---

# Claim

One sentence, in the gate's own vocabulary. Never an adjective standing in
for an exit band -- write "exited 0", not "passed"; "band 13", not "failed".

## Gate output (verbatim)

    <the exact stdout/stderr lines and the exit code, unedited>

## Boundary -- what this result did NOT establish

- Mandatory, at least one clause. Copy the owning skill's own Limits
  language rather than inventing softer wording.

## Open questions

- Frontier items this run surfaced. The section is required; an empty
  list is allowed and means "this run surfaced none".

## Refuted premises

- Only when a run killed a belief the work was resting on. Cite the
  evidence that killed it by path + sha256. Omit the section otherwise.

## Refactoring review

- Required for phase-scoped records (station: "phase-N"); optional
  elsewhere. Exactly two honest answers: refactors EXECUTED, each named
  and behavior-preserving, or "none needed" argued from what the work
  actually touched. A deferred refactor is an open question with a named
  target, never silent debt.
```

Rules the shape carries:

- **The claim never merges families (D-24).** A record about a session outcome cites the conformance result by digest if it needs to; it never presents the two as one verdict.
- **The boundary section is not optional.** A green exit is a narrow claim; the record states what it is narrow about. Every skill's Limits section is the source text.
- **Digests are computed from bytes on disk** after the last write, with `shasum -a 256`, never copied from memory or an earlier run.
- **A citation names committed bytes -- and an exception declares itself.** A record cites an artifact by path AND digest, and the digest of an uncommitted working-tree file is NOT a citation, because the reader must be able to check the claim out of history. The one admitted exception is run evidence deliberately kept out of the tree (a recovery report, a retained attempt): its digest may be recorded, but the record must say plainly that the bytes live outside history and the claim is correspondingly weaker -- checkable only by whoever holds the bytes. An undeclared exception is an overclaim.

## Why there is no index and no status field

Completion **is** the record's existence plus its commit. An index file would be a second source of truth that drifts; ordering and inventory are recomputable from `ls` and `git log --oneline -- .gnd-planning/`; every digest is recomputable from the named path. A `status:` field would claim something the evidence already proves or contradicts. This is the same posture the rest of GND takes: no payload carries an adjective where a reader can recompute the fact.

## The commit

One commit per **recorded** gate — evidence lane, on the user's explicit go-ahead — made **after** the record file is written so the record rides in the same commit as the artifacts it binds. Fast-lane work commits through the consuming repository's ordinary development flow, un-narrated by this contract.

### Grammar

```
<type>(<scope>): <imperative subject, <= 65 chars, no trailing period>

<body, wrapped ~72-80 columns:
 - what the gate established, with exit codes verbatim
 - what it did NOT establish (the boundary clause, compressed)
 - the record file path on its own closing line>
```

Body conventions: use `--` rather than em-dashes; **never put backticks in a commit message** (shells perform command substitution on them — a real commit in GND's own history was garbled this way); reference files by bare path.

### Type selection

- **`feat`** — the station produced or changed working artifacts (model, corpus, generated project, closed experiment, published evolution, rendered document).
- **`docs`** — the station produced *evidence about* existing artifacts (a conformance band, a panel review, an extraction verdict, a retained non-accepted session worth recording).
- **`fix`** — a mid-station repair (the model corrected after synth exited non-zero, a contract corrected after exit 3).
- **`chore`** — scaffolding (`gnd-new-project`).

A record of a refuted premise is `docs`, with the refutation in the body.

### Scope tokens, by station

The table names what a record binds to *when the evidence lane applies*; the lane rule above decides whether one is due at all.

| Station | Skill | Scope token | Type | Record triggers on |
|---|---|---|---|---|
| 0 | `gnd-new-project` | `project` | `chore` | scaffold commit only — no record file |
| 1 | `gnd-model-from-text` / `gnd-model-from-code` | `model` | `feat` | `gnd validate` exit 0 (or the bundled fallback validator exit 0, recorded as layer-1-only) / `gnd recovery verify` exit 0 |
| 2 | synth + measure (the grounding half of `gnd-dev-session`) | `synth` | `feat` | `gnd synth` exit 0 (and `gnd measure` exit 0 when measure ran) |
| 3 | `gnd-codegen` | `codegen` | `feat` | `gnd codegen` exit 0, including a regeneration |
| 3b | extension implementation (the consuming project's own tooling; the extension half of `gnd-codegen`) | `slice` | `feat` | a shipped slice worth milestone evidence |
| 4 | `gnd-dev-session` | `<lowercase experiment id>` (for `EXP-001-contact-roster`: record `004-exp-001-contact-roster.md`, commit `feat(exp-001-contact-roster): ...`) | `feat` at close 0; `docs` for a retained terminal run exit 15 disposition or a close exit 14 refusal that taught something | `gnd exp close` exit 0; `gnd exp run` exit 15 for a terminal disposition worth recording; `gnd exp close` exit 14 only as a refusal that taught something, never as a terminal session outcome |
| 5 | `gnd-conformance` | `conformance` | `docs` | band 0 or 13, recorded verbatim either way |
| 6 | `gnd-model-evolve` | `evolve-<proposal>` (e.g. `evolve-p001`) | `feat` | the D-13 `record.json` present — the completion marker |
| 6 (exit-18 hand edit) | `gnd-model-evolve` | `model` | `fix` | `gnd validate` exit 0 plus every linked-project conformance payload recorded |
| 7 | `gnd-review-panel` | `panel` | `docs` | `gnd review finalize` exit 0 |
| adopt | `gnd-adopt` | `adopt` | `feat` | `verify_migration.py` exit 0 over the reviewed mapping; `gate:` holds that command, and the record's body quotes `gnd validate` exit 0 on the published model verbatim -- two commands, one record, no merged verdict (D-24) |
| roundtrip | `gnd-extract` | `extract-<case>`, or `extract-<suite>` for one batched case-suite record | `docs` | after `gnd verify` reports any band 0–4 |
| roundtrip | `gnd-render-doc` | `render-<case>`, or `render-<suite>` for one batched case-suite record | `feat` | `gnd doccheck` exit 0 |

### What is staged

Stage **by explicit path**: the station's declared artifacts plus the record file. Never `git add -A`, never `git add .` — a station commit that sweeps in unrelated worktree changes binds the record to bytes it never claimed. Each skill's Record-and-commit section names its declared artifacts; the record file is always the last path staged.

### When

After the gate, and only after. A skill whose gate refused (codegen exit 11, panel exit 16) has produced no completion to record as `feat` — record the refusal honestly as `docs` if it taught something, or fix and re-run. For the two boundary skills, see the next section.

## Sequencing for boundary skills

`gnd-extract` and `gnd-render-doc` each run a bounded transaction with a declared write set — "No other path is read, written, moved or deleted" is a security rule in those skills and **this contract does not loosen it**. The record write and the commit happen strictly **after** the transaction has closed and the skill's own report is complete. They are a separate act, over paths the operator chose — never a path the untrusted document names. During the transaction, the write set remains exactly the skill's two declared files; the record is not part of the extraction or the render.

## What a record never claims

- Never an adjective for an exit band — the band is quoted, the reader derives the meaning.
- Never a merged verdict across claim families (D-24) — cite by digest, don't blend.
- Never authority the gate did not grant — a recorded green conformance still says nothing about extension code; the record repeats that boundary, it cannot waive it.
- Never a substitute for retained evidence — `runs/`, `panel-run/`, and the evolution `--records` tree stay where they are; the record cites them, it does not copy them.

## The milestone-close record

Closing a milestone is itself a material event with a record, and that record
owes two sections no phase record can discharge for it:

- **The open-questions sweep** -- REQUIRED. Every record in the milestone
  directory is re-read and every open question it raised is dispositioned:
  closed (citing the record that closed it), carried (naming the next owner),
  or retired (with the reason). A question that appears in no sweep row was
  missed, and the sweep exists so that is detectable.
- **Refactoring review** -- each phase record carries its own `Refactoring
  review` section with one of exactly two honest answers: refactors EXECUTED
  (each named and behavior-preserving) or "none needed" argued from what the
  phase touched. The close record confirms every deferred refactor has an
  open-questions row with a named target -- deferred structure work is never
  silent debt.

## Worked example commits

Ordinary station (station 3, green gate):

```
feat(codegen): generate the expense agent project from model.orm.yaml

uv run gnd codegen model.orm.yaml --out project/ exited 0. Derived files
written with digests recorded in project/.gnd-codegen.json; the extension
half (references/expense-agent-notes.md, pyproject.toml) authored, which
regeneration never overwrites. The green result establishes that the
derived surface matches the model at its recorded digest -- it says
nothing about extension code and nothing about what any tool function
computes.

Record: .gnd-planning/milestones/v1/003-codegen.md
```

Boundary skill, non-zero band recorded honestly:

```
docs(extract-invoice-batch-7): read the document back at verify band 1

uv run gnd verify model.orm.yaml extracted.population.json --artifacts
bundle/ exited 1 -- an alethic violation the document's own world
carries, reported as it stands, not repaired; a band about the
document's world is never a signal to edit facts. During the extraction
the write set was exactly extracted.population.json and its sidecar;
this record and commit happened after the bounded transaction closed
and stage only those two files plus the record.

Record: .gnd-planning/milestones/v1/006-extract-invoice-batch-7.md
```
