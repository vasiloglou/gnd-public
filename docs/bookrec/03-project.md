# 3. Generate the model-facing part of a project

You now have a model and concrete examples of acceptance and rejection. The
next step is a project that can use that model. `gnd codegen` creates the
model-facing scaffold and records which files it owns. You supply the
application algorithm and declare its structure.

Continue after [chapter 2](02-facts.md), in the same tutorial directory.

## Generate into a new destination

<!-- gnd-run expect=0 -->
```sh
gnd codegen bookrec-demo/model.orm.yaml --out bookrec-project
```

Open `bookrec-project`. The generated `model/` package, model artifacts and
`SKILL.md` describe the model's executable context. The `.gnd-codegen.json`
manifest records the model binding and generated file digests. `pyproject.toml`
and the reference notes are extension points: your application may grow there.

The generator does not infer a recommender algorithm from the rules. “Never
recommend an already-read book” describes a constraint on output; it does not
choose a useful ranking algorithm. This separation leaves normal Python
engineering in your hands while preserving a checkable model boundary.

## Add the authored checkpoint

The packaged `extension/bookrec/` directory contains a small library and CLI
written for this tutorial. Copy it into the generated project, together with
the model, input and architecture declaration.

<!-- gnd-run expect=0 -->
```python
from pathlib import Path
import shutil

source, project = Path("bookrec-demo"), Path("bookrec-project")
shutil.copytree(source / "extension/bookrec", project / "bookrec")
for name in ["model.orm.yaml", "seed.population.json", "architecture.contract.yaml"]:
    shutil.copy2(source / name, project / name)
assert (project / "bookrec/library.py").is_file()
assert (project / ".gnd-codegen.json").is_file()
print("Generated scaffold plus authored BookRec extension are ready.")
```

The architecture contract declares `bookrec.cli.main`, the module entry point,
commands, flags, fact types consumed and produced, and smoke scenarios. This is
a declaration for bounded structural inspection; it is not a proof of every
behavior in the library.

<!-- gnd-run expect=0 -->
```sh
gnd conformance bookrec-project/model.orm.yaml bookrec-project --format json
```

Expected: exit 0. Conformance checks the relationship between this model,
generated files, and declared architecture. It does not establish that every
future recommendation will be legal. The application must check each result.

## Understand what you own

| Surface | Typical contents | How to change it |
|---|---|---|
| Derived | Generated tools, artifacts, model-specific instructions | Regenerate deliberately from the selected model |
| Extension | Python dependencies, domain notes, architecture declaration | Edit as ordinary project code |
| Authored application | `bookrec/library.py`, `bookrec/cli.py` | Develop and test under the declared contract |
| Candidate data | Input and proposed recommendation facts | Check against the selected model before use |

The CLI checkpoint reads input, calls the library, checks the proposed output
with `gnd.api.check`, and publishes the accepted candidate. The next chapter
walks through that sequence. Its command is a normal module invocation; no
special application server is required.

<!-- gnd-run expect=0 -->
```sh
(cd bookrec-project && python -m bookrec.cli --help)
```

## Explicit agent handoffs

If you build the project with an agent, select `gnd-codegen` after accepting the
model and give it this bounded request:

> Use gnd-codegen for the accepted BookRec model. Generate into a fresh project.
> Implement the recommender as an extension using gnd.api.check before output
> publication. Add an architecture contract with known-user and unknown-user
> smoke cases. Do not change the business rules to accommodate an implementation.

Once the extension is ready, separately select `gnd-conformance`:

> Use gnd-conformance to inspect this project against the selected model.
> Report derived-file, model-binding and declared architecture findings. Do not
> regenerate or repair automatically.

The supplied checkpoint lets you complete both stages without a live agent.
Generated smoke tests are also present in the project; running those requires
`pytest` in your environment. The credential-free tutorial below verifies the
same accepted and refused behaviors directly with the application commands.

**Exercise:** Find `publish` in `bookrec/cli.py`. Identify the one branch that
moves candidate bytes to the final output path. What happens when checking
returns exit 2 or exit 4?

Next: [run the checked application](04-application.md).
