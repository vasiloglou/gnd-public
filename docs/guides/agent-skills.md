# Work with GND in an agent session

GND ships agent instructions alongside its Python runtime. The runtime checks
artifacts; the skills guide a coding agent through the human work of clarifying
requirements, authoring a model, building an extension, or interpreting a
result. You can use the deterministic CLI and API without an agent session.

## Install the skills into your project

After installing the package, run these contextual setup commands in the
project where you want the agent to work:

```sh
gnd install --project
gnd doctor --project
```

The default install targets Claude Code and Codex discovery directories and
copies the packaged skills. `--claude` or `--codex` selects one runtime.
`--global` selects user-level placement. Use `--symlink` only for a development
installation whose package directory will remain available.

`doctor` reports installed-asset state, including collisions, modified files,
and stale or missing copies. It examines both scopes to reveal shadowing; a
current install says nothing about whether your model or application passes.
Do not overwrite an existing skill directory by hand to resolve a collision.
For contributors adopting the repository's tracked links, follow the distinct
[contributor setup](../development/index.md).

## Start from a clear user request

The BookRec and expense tutorials provide deterministic checkpoints and
agent-assisted prompts. An initial modeling request can be:

```text
Use gnd-model-from-text in Guided mode to model a book recommendation service.
A reader must not receive a book already read, and must meet its minimum age.
Genre preference is advisory. Ask me about ambiguous rules, then write the
model and a readable verbalization and validate the model.
```

Read the proposed rules and resolve the domain questions. Once you accept the
model, explicitly choose the next workflow:

```text
Use gnd-codegen with the accepted model.orm.yaml to create application/.
Then implement a small CLI in the extension-owned files that checks a
recommendation population using gnd.api and displays failed rules.
```

The code generator produces the derived half; the agent writes the requested
application extension. These are distinct actions. Continue with normal
application tests and the architecture smoke, and select conformance when you
need to check agreement with the model.

## Select a skill by its outcome

| Skill | What you ask it to produce |
|---|---|
| `gnd-model-from-text` | A new domain model and readable verbalization |
| `gnd-model-from-code` | A one-time recovered model with static source evidence |
| `gnd-model-evolve` | A reviewed change to an existing valid model |
| `gnd-codegen` | Derived Python project plus authored extension guidance |
| `gnd-conformance` | Evidence about model/project agreement |
| `gnd-dev-session` | A bounded experiment contract, run interpretation, and closure |
| `gnd-extract` | Facts extracted from a document and their bound sidecar |
| `gnd-render-doc` | A document rendered from facts with a checked manifest |
| `gnd-export` | Selected finite witnesses or bounded export artifacts |
| `gnd-review-panel` / `gnd-review-panel-light` | Advisory review that preserves failures and dissent |
| `gnd-adopt` | Explicit GSD requirement migration around code recovery |
| `gnd-new-project` | A one-time planning scaffold for a new GND project |
| `gnd-orm-core` | Authoritative representation and constraint references |
| `gnd-solve` | Guidance through the development stations |
| `gnd-update-review-panel` | Maintainer updates of the selected reviewer tools |

Each skill's entry point is under
[the packaged skill directory](https://github.com/vasiloglou/gnd-public/tree/main/src/gnd/skills).
Agents without native discovery can read the corresponding `SKILL.md` directly.

## Make each handoff explicit

A skill can recommend another skill and cite its evidence, but it does not
automatically invoke the sibling. A passing check is not permission to change
a model; a drift finding is not permission to regenerate code. State the next
action you want and the artifact it should use. Authorization you already gave
for that named scope remains relevant; the workflow should not invent another
gate merely because a tool returned.

The CLI `gnd solve` is a separate command harness: it can run a selected sequence
of CLI stations with its own gating and log. It does not author the model or
implement your application. See the [development walkthrough](../walkthrough.md).

A live agent or review session depends on your configured tool and credentials.
The installed tutorial checkpoints need neither. A saved transcript demonstrates
its historical run only; replaying saved data does not imply a new provider call.
