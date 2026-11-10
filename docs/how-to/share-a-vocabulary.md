# Share a vocabulary, keep your project's rules

A component scanner knows what a component is and which components import
others. Several projects use that same vocabulary. Each project has its own
architecture rules, and a scanner update should not overwrite them.

Keep the two responsibilities in two files. The tool ships the vocabulary;
the project pins that file and adds its rules. Both `gnd validate` and
`gnd check` read the resulting model. You will see an import loop fail a
project-owned rule, with the project's own advice on how to fix it, and then
see the corrected facts pass.

!!! info "Early review copy"

    This checkpoint runs on the merged MC1 implementation. The example below
    is prepared for the model-composition milestone. The vocabulary-update
    and re-pin walkthrough at the end is still a placeholder.

<div class="app-figure" markdown="1" role="region" tabindex="0" aria-label="Shared vocabulary and project-owned rule">

![The tool owns components-v1.orm.yaml, which declares Component imports Component. The project owns project.orm.yaml, which pins the vocabulary by sha256 and adds no_import_loops with its own rationale and remedy. GND verifies the pin and checks the composed model against scanner facts. Those facts contain api importing auth and auth importing api, so the project's rule fails for one loop of two components and two edges. The remedy asks the project to move shared code into a lower component both can import.](../assets/applications/shared-vocabulary-draft.svg)
</div>

*Source: `vocabulary/components-v1.orm.yaml`, `project.orm.yaml` and
`cycle.population.yaml` in the example, adapted from the shipped
`rule_check` component catalog.*

## Copy the example

Copy the example into a working folder:

<!-- gnd-run expect=0 -->
```sh
python -c "import gnd, pathlib, shutil; shutil.copytree(pathlib.Path(gnd.__file__).parent / 'examples/model_composition', 'catalog', dirs_exist_ok=True)"
```

| File | Who owns it | What it contains |
|---|---|---|
| `catalog/vocabulary/components-v1.orm.yaml` | The tool | Component, Area, Owner and Release types; the four fact types the scanner emits |
| `catalog/project.orm.yaml` | This project | The vocabulary pin and the project's no-import-loops rule |
| `catalog/cycle.population.yaml` | Scanner example | Three import edges, including the loop between api and auth |
| `catalog/fixed.population.yaml` | Scanner example after repair | Two import edges, with auth no longer importing api |

These small populations are illustrative scanner output. Their `producer`
labels describe the example; GND does not run or attest to the scanner.

## Keep the rule in the project

The vocabulary declares `component_imports_component`, with `importer` and
`imported` roles. The project attaches its acyclic rule to that included
fact type. It does not copy the vocabulary's object or fact definitions.

This is the complete project file:

<!-- gnd-run expect=0 output=stdout -->
```sh
cat catalog/project.orm.yaml
```

```text
version: 5
model_id: urn:gnd-example:shared-components@1
includes:
  - id: components
    path: vocabulary/components-v1.orm.yaml
    sha256: 512e10fb72a3e5c029000872ed85238006e7f851c1d24c0bca8fed05380479b3
fact_type_constraints:
  - fact_type: component_imports_component
    constraints:
      - id: no_import_loops
        type: ring
        variant: acyclic
        source: user-supplied
        status: confirmed
        modality: alethic
        rationale: A loop means no component in it can be built or tested alone.
        remedy: "Break the loop: move the shared code into a lower component both can import."
        provenance:
          user_quote: "No component may import itself, directly or through others."
```

The pin names the exact vocabulary bytes used by this project. The project
also owns the rule's id, rationale and remedy. For the model-file contract,
see [Model includes (version 5)](https://github.com/vasiloglou/gnd-public/blob/main/src/gnd/skills/gnd-orm-core/references/representation-format.md#model-includes-version-5).

Validate the vocabulary on its own:

<!-- gnd-run expect=0 output=stdout -->
```sh
gnd validate catalog/vocabulary/components-v1.orm.yaml
```

```text
OK: catalog/vocabulary/components-v1.orm.yaml is a valid GND ORM model
```

Then validate the project. GND verifies the included file and checks the
composition, including the project's attached rule:

<!-- gnd-run expect=0 output=stdout -->
```sh
gnd validate catalog/project.orm.yaml
```

```text
OK: catalog/project.orm.yaml is a valid GND ORM model
```

## See the project's rule fail

The scanner's first population says `web` imports `api`, `api` imports
`auth`, and `auth` imports `api`. The last two edges form a loop.

<!-- gnd-run expect=1 output=stdout -->
```sh
gnd check catalog/project.orm.yaml catalog/cycle.population.yaml --rule-ids
```

```text
BLOCKING (alethic)
  [fail] constraint:no_import_loops (fact_types[component_imports_component].constraints[0]): The relation 'component_imports_component' is acyclic — violated: 1 strongly connected group (size 2) holds 2 edges.
    remedy: Break the loop: move the shared code into a lower component both can import.
ADVISORY (deontic)
  (none)
pass=0 fail=1 warning=0 unchecked=0 vacuous=0
COVERAGE
  component_imports_component: declared, facts=3
  component_is_in_area: undeclared, facts=0
  component_has_owner: undeclared, facts=0
  component_ships_in_release: undeclared, facts=0
```

The finding names `no_import_loops`, the id in the project file, and prints
that file's remedy. The vocabulary supplied the relation; the project
supplied the rule being enforced.

Only the imports relation is supplied in this small population. The other
three relations are shown as undeclared; this example places no project
rule on them.

## Check the repair

In the corrected scanner output, `auth` no longer imports `api`. The
remaining path is `web → api → auth`. Keep both model files as they are
and check those new facts:

<!-- gnd-run expect=0 output=stdout -->
```sh
gnd check catalog/project.orm.yaml catalog/fixed.population.yaml --rule-ids
```

```text
BLOCKING (alethic)
  (none)
ADVISORY (deontic)
  (none)
pass=1 fail=0 warning=0 unchecked=0 vacuous=0
COVERAGE
  component_imports_component: declared, facts=2
  component_is_in_area: undeclared, facts=0
  component_has_owner: undeclared, facts=0
  component_ships_in_release: undeclared, facts=0
```

The same project rule now passes. Fixing the code changes the scanner's
facts; it does not require changing the shared vocabulary or weakening the
rule.

## Next: review a vocabulary update

**Placeholder for MC3.** The completed walkthrough will ship a second,
versioned vocabulary that removes a fact type used by a project rule. It
will show a re-pin preview naming the broken rule, followed by one combined
re-pin and rule edit that publishes and checks successfully. Those commands
are not implemented in this checkpoint.
