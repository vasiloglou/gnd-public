# GSD environment cleanup — the printed checklist

After a project migrates, GSD residue remains on the operator's machine. This
checklist is **printed and walked through by hand — never automated**: every
item touches the operator's global settings or home directory, and this skill
edits neither.

**No item ships a count.** A number measured on one machine is wrong on every
other, and a checklist that says "16 grants" to an operator who counts 14 has
taught them to distrust the rows that are right. Each item ships the command
that measures it **here, on this machine, now**; the number the command prints
is the number. Record what was found and what was removed in the migration's
milestone record — that is where measured numbers belong.

| # | Item | Measure with | Clean looks like | Manual remedy |
|---|---|---|---|---|
| 1 | GSD graphify hook | `grep -n gsd-graphify-update.sh ~/.claude/settings.json` | no match | remove the hook entry; delete `~/.claude/hooks/gsd-graphify-update.sh` if present |
| 2 | GSD worktree path guard | `grep -n gsd-worktree-path-guard.js ~/.claude/settings.json` | no match | remove the hook entry; delete the hook file if present |
| 3 | GSD permission grants | `grep -o '"[^"]*gsd[^"]*"' ~/.claude/settings.json` | no matches | delete each listed grant from the permissions block |
| 4 | GSD state directory | `ls -d ~/.gsd` | "No such file or directory" | archive or delete `~/.gsd/` |
| 5 | GSD worktree directory | `ls -d ~/gsd-workspaces` | "No such file or directory" | archive or delete `~/gsd-workspaces/` |
| 6 | In-repo GSD enforcement | `grep -n 'GSD Workflow Enforcement' .claude/CLAUDE.md` | no match | replace the section with the GND entry-points template below |
| 7 | Orphaned GSD skills | `ls ~/.claude/skills 2>/dev/null \| grep -i gsd` | no matches | delete each listed skill directory |

Work top to bottom; re-run each item's command after its remedy and confirm
the clean state before moving on. An item already clean is recorded as clean,
not skipped silently.

## The GND entry-points template

Item 6's replacement text — the one block this checklist ships whole, because
it is the one thing the operator pastes rather than deletes:

```markdown
## GND Workflow

This project is developed with GND. The model is the requirements document:
`model.orm.yaml` at the repository root, with planning artifacts under
`.gnd-planning/`.

Entry points:
- `gnd coverage model.orm.yaml` — the element roadmap: what is claimed,
  what is evidenced, what is open
- the `gnd-solve` skill — the full station loop for a work slice
- the `gnd-dev-session` skill — a verifier-gated agent session
- the `gnd-model-evolve` skill — any change to the model itself

The `.planning/` tree, if present, is the read-only historical record of the
project's pre-GND development. Do not write to it.
```

## What this checklist is not

It is not a proof the environment is clean — items outside its seven rows are
outside its claim. It never edits `~/.claude/settings.json` or deletes a
directory itself, and it does not run on any machine but the one in front of
the operator. GSD's own uninstaller, where one exists, is the authority on
GSD's files; this checklist only finds what a GSD uninstall left behind.
