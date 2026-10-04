# Generate a project and keep it aligned

Once the model is accepted, `gnd-codegen` turns it into a runnable plain-Python
project. The project has two halves with different owners:

| Half | Who writes it | What happens on regeneration |
|---|---|---|
| **Derived**: `tools.py` (one constructor per supplied fact type), projection schema, verbalization, applicability, a generated `SKILL.md` | `gnd codegen`, from the model | rewritten from the model; a hand edit is refused, not overwritten |
| **Extension**: your application code, `architecture.contract.yaml`, smoke tests, `pyproject.toml`, notes | you or your agent | never touched |

The extension calls the checker on its own output before publishing it. That is how
the application checks itself at run time.

## Ask your agent

```text
Use gnd-codegen for the accepted model.orm.yaml. Generate into a fresh project.
Implement the recommender as an extension that calls gnd.api.check before it
publishes any output. Add an architecture contract with known-user and unknown-user
smoke cases. Do not change the business rules to accommodate an implementation.
```

The skill runs `gnd validate`, then `gnd codegen model.orm.yaml --out my-project`, then
writes the extension files and implements the slice in them. Afterwards, select
conformance separately:

```text
Use gnd-conformance to inspect this project against the selected model. Report
derived-file, model-binding and architecture findings. Do not regenerate or repair
automatically.
```

## What GND checks

```sh
gnd codegen model.orm.yaml --out my-project          # 0 written, 11 refused
gnd conformance model.orm.yaml my-project --format json   # 0 aligned, 13 drift
```

`gnd conformance` makes four assertions:

1. **Integrity:** every derived file still matches its recorded digest.
2. **Currency:** the project was generated from this exact model.
3. **Structure:** the constructor surface matches the model's supplied fact types.
4. **Architecture:** bounded static observations of the extension agree with the
   declared contract.

Exit **13** means drift: a hand-edited derived file, a stale model, or a broken
architecture declaration. Regenerating over a hand-edited derived file exits **11**
and destroys nothing. A green conformance result is structural only: it says nothing
about whether your extension code behaves correctly. That is what your tests and the
population check are for.

## See it run

The BookRec tutorial runs this whole handoff with a supplied extension:

- [Generate the model-facing part of a project](../bookrec/03-project.md) runs
  `gnd codegen` and `gnd conformance`, and explains who owns which file.
- [Run the application and publish checked output](../bookrec/04-application.md)
  shows the extension refusing to publish output that fails the check.
- [Diagnose and repair](../bookrec/05-repair.md) introduces deliberate drift (exit 13)
  and restores it.

The [generated projects guide](../guides/generated-projects.md) documents the layout,
the architecture contract and every exit.
