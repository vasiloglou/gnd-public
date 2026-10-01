---
name: gnd-new-project
description: Opens a GND project in a repository by scaffolding the .gnd-planning directory — the one place all GND planning artifacts live — with its PROJECT.md one-pager and the first milestone directory, then makes the opening commit. Use when asked to "start a GND project", "gnd new project", "open a milestone", "scaffold .gnd-planning", or when any GND skill finds .gnd-planning absent and routes here. The directory is created exactly once and never re-scaffolded; an existing .gnd-planning is refused, and a new milestone is a new subdirectory, not a rewrite. Deliberately named .gnd-planning so it is never confused with a .planning directory that GSD or another framework may already own in the same repository. Not for authoring the model (gnd-model-from-text / gnd-model-from-code), not for recording a station's completion (each station's own skill does that, per the milestone-record contract), and never performed by the gnd CLI — gnd itself never reads or writes .gnd-planning and never touches git.
---

# GND New Project

## Summary

**What:** the one-time act of opening a GND project in a repository — create
`.gnd-planning/`, write its `PROJECT.md` one-pager, open the first milestone
directory, and commit the scaffold. Everything GND records about the project
afterwards — one record per material event, per the two-lane rule — lands
under `.gnd-planning/milestones/`, in the shape the record contract owns:
[`../gnd-orm-core/references/milestone-record-format.md`](../gnd-orm-core/references/milestone-record-format.md).

**Why the name:** a repository may already carry a `.planning/` directory
belonging to GSD or another framework. GND's planning artifacts live under
`.gnd-planning/`, never under `.planning/`, so the two frameworks can share a
repository without either misreading the other's records.

**When to use:**
- A repository is about to become a GND project and has no `.gnd-planning/`
- A GND skill reached its record-and-commit step and found `.gnd-planning/`
  absent
- A finished milestone needs a successor (`milestones/v2/` beside `v1/` —
  the one case where this skill acts on an existing `.gnd-planning/`)

**Opening a successor milestone: read the roadmap before writing the goals.**
`gnd coverage MODEL` prints, per model element, whether any experiment claims it
and whether a cited payload corroborates that claim. Run it before deciding what
the next milestone is for — a closing milestone's own claims are the most
optimistic reading of what was built, and the view separates the claims a
payload agrees with from the ones nobody has checked. It is read-only, exits 0
whatever it shows, holds no verdict about the work, and writes no file; a census
worth keeping is one a human redirects and commits. The vocabulary it prints is
defined once in
[`../gnd-orm-core/references/coverage-and-element-addressing.md`](../gnd-orm-core/references/coverage-and-element-addressing.md).

**When NOT to use:**
- `.gnd-planning/` already exists and the ask is anything other than opening
  a new milestone directory — the scaffold is created once and never
  re-created; refuse and say what exists
- Authoring the model — [`../gnd-model-from-text/SKILL.md`](../gnd-model-from-text/SKILL.md)
  (greenfield) or [`../gnd-model-from-code/SKILL.md`](../gnd-model-from-code/SKILL.md)
  (brownfield) own Station 1
- Recording a completed station — the station's own skill writes its record,
  in the contract's shape; this skill only provides the directory
- Walking the loop — [`../gnd-solve/SKILL.md`](../gnd-solve/SKILL.md)

## Workflow

### 1. Refuse an existing scaffold

If `.gnd-planning/` already exists, **stop**: report what is there
(`PROJECT.md`, the milestone directories and how many records each holds)
and do not touch it. The only act available over an existing scaffold is
opening the **next** milestone — a new empty directory under
`milestones/`, named with the user — and that is an append, never a rewrite.

### 2. Choose the milestone name

Ask the user, or default to `v1`. The name becomes
`.gnd-planning/milestones/<name>/` and every record in it will carry
`milestone: <name>` in its frontmatter.

### 3. Create the scaffold

```
.gnd-planning/
  PROJECT.md
  milestones/
    <name>/
```

`PROJECT.md` is a one-pager, written with the user:

- **The problem, in the user's words** — two or three sentences, quoted or
  paraphrased with their confirmation, not invented
- **The model's intended path** — a `Model:` line, normally
  `Model: model.orm.yaml` at the project root; the file need not exist yet.
  One line, machine-findable, so a later reader (or `gnd coverage`'s operator)
  learns where the requirements document lives without guessing
- **Where records go** — one line linking the record contract:
  records land in `milestones/<name>/`, one per material event, in the
  lanes and shape [`../gnd-orm-core/references/milestone-record-format.md`](../gnd-orm-core/references/milestone-record-format.md)
  defines

No status fields, no roadmap, no phase list — completion is proven by
records and their commits, never asserted by a document that can drift.

### 4. Offer the scaffold commit

Only on the user's explicit go-ahead, stage exactly the created files —
`.gnd-planning/PROJECT.md` and the milestone directory (add a `.gitkeep` if
the directory would otherwise be empty) — never `git add -A`. Offer, but do
not perform without that go-ahead, this commit:

```
chore(project): open .gnd-planning for <name>
```

with a short body naming the milestone opened and the problem one-pager's
location. Grammar and staging rules have one home:
[`../gnd-orm-core/references/milestone-record-format.md`](../gnd-orm-core/references/milestone-record-format.md).

### 5. Route to Station 1

The project is open; nothing is modeled yet. Hand off — explicitly, on the
user's go-ahead, never by auto-invoking — to
[`../gnd-model-from-text/SKILL.md`](../gnd-model-from-text/SKILL.md) for a
greenfield domain or
[`../gnd-model-from-code/SKILL.md`](../gnd-model-from-code/SKILL.md) for a
brownfield codebase, or to [`../gnd-solve/SKILL.md`](../gnd-solve/SKILL.md)
for the whole walk.

## What this skill will not do

- **It never re-scaffolds.** An existing `.gnd-planning/` is reported, not
  repaired, merged, or overwritten. A correction to `PROJECT.md` is the
  user's edit, not this skill's.
- **It never writes a record.** Station records belong to the station skills;
  an empty milestone directory is the honest state of a project where no
  station has completed.
- **It never touches `.planning/`.** Whatever else lives in the repository —
  GSD trees included — is out of scope by name.
- **It involves no `gnd` command.** The scaffold and the commit are the
  driving agent's acts; `gnd` itself never reads or writes `.gnd-planning/`
  and never touches git.

## Report

State, in your reply: whether the scaffold was created or refused (and, if
refused, what already existed); the milestone directory opened; the exact
paths staged and the commit subject used, or the paths proposed and that the
commit awaits the user's go-ahead; and the Station 1 handoff offered. Claim
nothing beyond the scaffold — an open project asserts nothing about any model,
gate, or station.
