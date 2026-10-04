# From a domain rule to a working application

A useful first GND project ends with a small application behavior you can run:
check a recommendation, approve an expense, or inspect a shipping request.
You can use individual commands as needed. The optional `gnd solve` harness
organizes selected CLI steps once their inputs already exist.

## Follow the application path

1. **Describe one decision.** Write example facts and rules, then author a
   model with the [modeling guide](guides/modeling.md) or the text-to-model skill.
2. **Check contrasting cases.** Validate the model and inspect one accepted
   population and one purposeful failure. Add synthetic grounding when it
   answers a real testing question.
3. **Generate the project.** Produce the model-derived tools and artifacts,
   then implement the user-visible behavior in developer-owned extensions.
4. **Test the application.** Run focused tests and the architecture smoke.
   Inspect conformance when the generated surface or model may have drifted.
5. **Change deliberately.** Evolve an existing model when requirements change,
   regenerate explicitly where needed, and rerun the affected examples.

Use [BookRec](bookrec/01-model.md) for the full path. Its generated artifacts
and supplied application extension make each stage concrete. The
[expense chapters](expense/01-model.md) provide a second path focused on state
checks and adding a requirement to an existing application.

## Use the CLI station harness when it helps

`gnd solve` composes validation, synthesis, code generation, experiment run,
and conformance in its documented order. It does not elicit requirements,
author an experiment contract, or implement the extension for you. Inspect
the current help before selecting a walk:

<!-- gnd-run expect=0 -->
```sh
gnd solve --help
```

The following is a **contextual** validation-only walk. It assumes the model
exists and uses an explicit workspace. `--auto` authorizes the selected gate;
without it the harness requests authorization interactively.

```sh
gnd solve model.orm.yaml --workspace walk-output --until validate --auto
```

Select `--from`, `--until`, and `--skip` according to the station names shown
by help. An experiment directory must already be authored and be inside the
workspace when the `exp-run` station is selected. The harness records station
selection, authorization, captured output and evidence paths.

Exit `0` means all selected stations completed with accepted exits. Exit `17`
means the walk halted. The individual station's exit and halt reason are in
the log; a halted walk is not a replacement domain verdict. A self-consistent
log describes the harness record, not independent proof of every claimed
process execution.

For code recovery, finish the separate `gnd recovery verify` gate before
entering the harness. For agent-directed work, select each sibling skill
explicitly as described in [agent skills](guides/agent-skills.md). The workflow
map and stable station numbering live in the
[solve skill](https://github.com/vasiloglou/gnd-public/blob/main/src/gnd/skills/gnd-solve/SKILL.md);
the executable station policy lives in `gnd solve --help`.
