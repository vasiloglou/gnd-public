# Run the shared-vocabulary example

Two projects use one component scanner, with different rules. Checkout blocks
import loops. Platform warns when a component has no owner. This page runs the
checks behind [Share the scanner, keep your own rules](../tutorials/shared-component-vocabulary.md).
It expands the shipped twelve-component `rule_check` catalog.

!!! info "Review copy"

    Sharing, checking and repairing the catalogs run today. The vocabulary-update
    walkthrough is still in progress and is marked at the end.

!!! info "Files on GitHub"

    These review-copy files are on the draft branch:

    - [Checkout's project rules](https://github.com/vasiloglou/gnd-public/blob/codex/model-composition-docs-draft/src/gnd/examples/model_composition/checkout/project.orm.yaml)
    - [Platform's project rules](https://github.com/vasiloglou/gnd-public/blob/codex/model-composition-docs-draft/src/gnd/examples/model_composition/platform/project.orm.yaml)
    - [The component vocabulary](https://github.com/vasiloglou/gnd-public/blob/codex/model-composition-docs-draft/src/gnd/examples/model_composition/checkout/vocabulary/components-v1.orm.yaml)
    - [All example files](https://github.com/vasiloglou/gnd-public/tree/codex/model-composition-docs-draft/src/gnd/examples/model_composition)

Use a GND checkout of the draft branch for this unreleased example; the
[installation guide](../installation.md) explains development setup.

## Copy the example

<!-- gnd-run expect=0 -->
```sh
python -c "import gnd, pathlib, shutil; shutil.copytree(pathlib.Path(gnd.__file__).parent / 'examples/model_composition', 'catalog', dirs_exist_ok=True)"
```

| File in each project folder | Ownership | Purpose |
|---|---|---|
| `vocabulary/components-v1.orm.yaml` | Tool | The shared types and four fact types emitted by the scanner |
| `project.orm.yaml` | Project | A vocabulary pin and the project's own rule |
| `before.population.yaml` | Example scanner output | The twelve-component catalog before repair |
| `after.population.yaml` | Example scanner output | The catalog after repair |

The two local vocabulary files are identical. Each lives beneath the project
model that includes it. The project models add policy without copying the
tool's object or fact declarations. See the single
[model includes contract](https://github.com/vasiloglou/gnd-public/blob/main/src/gnd/skills/gnd-orm-core/references/representation-format.md#model-includes-version-5)
for the file-format rules.

Confirm both projects received the same vocabulary bytes:

<!-- gnd-run expect=0 -->
```sh
cmp catalog/checkout/vocabulary/components-v1.orm.yaml catalog/platform/vocabulary/components-v1.orm.yaml
```

## See what each project owns

Checkout owns the no-import-loops rule, including its rationale and remedy:

<!-- gnd-run expect=0 output=stdout -->
```sh
cat catalog/checkout/project.orm.yaml
```

```text
version: 5
model_id: urn:gnd-example:shared-components:checkout@1
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
    remedy: 'Break the loop: move the shared code into a lower component both can
      import.'
    provenance: {user_quote: 'No component may import itself, directly or through
        others.'}
```

Platform owns a different, advisory rule:

<!-- gnd-run expect=0 output=stdout -->
```sh
cat catalog/platform/project.orm.yaml
```

```text
version: 5
model_id: urn:gnd-example:shared-components:platform@1
includes:
- id: components
  path: vocabulary/components-v1.orm.yaml
  sha256: 512e10fb72a3e5c029000872ed85238006e7f851c1d24c0bca8fed05380479b3
fact_type_constraints:
- fact_type: component_has_owner
  constraints:
  - id: every_component_has_an_owner
    type: mandatory
    role: component
    source: user-supplied
    status: confirmed
    modality: deontic
    remedy: Add the owning team to the component's catalog entry.
    provenance: {user_quote: Every component should have an owning team.}
```

An advisory finding produces a warning. It does not block the run. This is the
same ownership policy as in the original component catalog.

## Validate both compositions

The tool's vocabulary is valid on its own:

<!-- gnd-run expect=0 output=stdout -->
```sh
gnd validate catalog/checkout/vocabulary/components-v1.orm.yaml
```

```text
OK: catalog/checkout/vocabulary/components-v1.orm.yaml is a valid GND ORM model
```

Each model loads the vocabulary it pins and adds its own rule:

<!-- gnd-run expect=0 output=stdout -->
```sh
gnd validate catalog/checkout/project.orm.yaml
```

```text
OK: catalog/checkout/project.orm.yaml is a valid GND ORM model
```

<!-- gnd-run expect=0 output=stdout -->
```sh
gnd validate catalog/platform/project.orm.yaml
```

```text
OK: catalog/platform/project.orm.yaml is a valid GND ORM model
```

## Check the catalogs

Checkout's facts contain two import loops: `api` ↔ `auth` and `search` ↔ `util`.
Platform's facts omit an owner for `metrics`. The scanner-output labels identify
the illustrative producer; GND checks the facts without running or attesting
to that scanner.

<!-- gnd-run expect=1 output=stdout -->
```sh
gnd check catalog/checkout/project.orm.yaml catalog/checkout/before.population.yaml --rule-ids
```

```text
BLOCKING (alethic)
  [fail] constraint:no_import_loops (fact_types[component_imports_component].constraints[0]): The relation 'component_imports_component' is acyclic — violated: 2 strongly connected groups (sizes 2, 2) hold 4 edges.
    remedy: Break the loop: move the shared code into a lower component both can import.
ADVISORY (deontic)
  (none)
pass=0 fail=1 warning=0 unchecked=0 vacuous=0
COVERAGE
  component_imports_component: declared, facts=14
  component_is_in_area: declared, facts=12
  component_has_owner: declared, facts=11
  component_ships_in_release: declared, facts=0
```

<!-- gnd-run expect=0 output=stdout -->
```sh
gnd check catalog/platform/project.orm.yaml catalog/platform/before.population.yaml --rule-ids
```

```text
BLOCKING (alethic)
  (none)
ADVISORY (deontic)
  [warning] constraint:every_component_has_an_owner (fact_types[component_has_owner].constraints[0]): Each component must play the 'component' role in 'component_has_owner' — violated: 'metrics' plays no such fact.
    remedy: Add the owning team to the component's catalog entry.
pass=0 fail=0 warning=1 unchecked=0 vacuous=0
COVERAGE
  component_imports_component: declared, facts=14
  component_is_in_area: declared, facts=12
  component_has_owner: declared, facts=11
  component_ships_in_release: declared, facts=0
```

## Check the repairs

Checkout removes `auth` → `api` and `util` → `search`. Platform adds the
`platform` team as the owner of `metrics`. The vocabulary and project rules
stay the same:

<!-- gnd-run expect=0 output=stdout -->
```sh
gnd check catalog/checkout/project.orm.yaml catalog/checkout/after.population.yaml --rule-ids
```

```text
BLOCKING (alethic)
  (none)
ADVISORY (deontic)
  (none)
pass=1 fail=0 warning=0 unchecked=0 vacuous=0
COVERAGE
  component_imports_component: declared, facts=12
  component_is_in_area: declared, facts=12
  component_has_owner: declared, facts=11
  component_ships_in_release: declared, facts=0
```

<!-- gnd-run expect=0 output=stdout -->
```sh
gnd check catalog/platform/project.orm.yaml catalog/platform/after.population.yaml --rule-ids
```

```text
BLOCKING (alethic)
  (none)
ADVISORY (deontic)
  (none)
pass=1 fail=0 warning=0 unchecked=0 vacuous=0
COVERAGE
  component_imports_component: declared, facts=14
  component_is_in_area: declared, facts=12
  component_has_owner: declared, facts=12
  component_ships_in_release: declared, facts=0
```

Both projects now pass their own rule. Every finding and remedy above comes
from an actual check of the shipped files.

## Next: review a vocabulary update

The completed walkthrough will add vocabulary v2, which changes a fact used by
a project rule. It will show a re-pin preview naming what breaks, followed by
one combined change that updates the vocabulary pin and repairs the rule.
That part is not implemented in this review copy.
