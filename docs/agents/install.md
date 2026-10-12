# Install the skills

The `get-nick-done` package contains two halves: the `gnd` Python runtime and a set
of agent skills. The skills are folders with a `SKILL.md` in the open
[Agent Skills](https://agentskills.io/) format. Claude Code reads them from
`.claude/skills/` and Codex reads them from `.codex/skills/`. `gnd install` copies them
there.

You can also [install through the Claude Code or Codex marketplace](../marketplace-plugins.md). Choose one skill installation method for each agent.

Run these commands in an empty directory, or in the project where your agent works:

<!-- gnd-run expect=0 -->
```sh
gnd install --project
```

<!-- gnd-run expect=0 -->
```sh
gnd doctor --project
```

`install` places every packaged skill for both agents. `doctor` reports what is placed
in both the project and user scopes, because user-level skills take precedence over
project-level ones. It also reports stale, missing, modified or colliding copies. A
current install says nothing about whether your model or application passes.

Every installed skill is a self-contained folder:

<!-- gnd-run expect=0 -->
```python
from pathlib import Path

for root in (Path(".claude/skills"), Path(".codex/skills")):
    skills = sorted(p.parent.name for p in root.glob("gnd-*/SKILL.md"))
    print(root, len(skills), "skills:", ", ".join(skills))
    assert skills and "gnd-model-from-text" in skills and "gnd-dev-session" in skills
```

## Choose where to install

| Flag | Effect |
|---|---|
| `--project` | `./.claude/skills` and `./.codex/skills`; commit them with the project |
| `--global` (default) | `~/.claude/skills` and `$CODEX_HOME/skills` |
| `--claude` / `--codex` | only one agent |
| `--sync` | refresh every root that already has an install manifest, for example after `uv tool upgrade get-nick-done` |
| `--symlink` | link instead of copy; development installs only |
| `--force` | replace unmanaged files that block a write; never touches files you edited |

`gnd uninstall` removes only what GND placed and leaves your edits alone. Do not resolve
a collision by overwriting a skill directory by hand. Contributors adopting the
repository's tracked links follow the separate [contributor setup](../development/index.md).

## Agents without native skill discovery

Any agent that can read files can use the skills: point it at the relevant `SKILL.md`,
for example *"Read .claude/skills/gnd-model-from-text/SKILL.md and follow it."* Each
skill names the artifacts it writes and the `gnd` command that checks them.

[What each skill produces →](index.md)
