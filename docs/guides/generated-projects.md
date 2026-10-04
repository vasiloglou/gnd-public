# Generate a project and keep it aligned

Code generation gives your application a Python surface that follows the
model. It emits fact tools, extraction artifacts, an agent skill, and the
initial extension structure. You then implement the product behavior:
recommendations, approval actions, storage adapters, user interfaces, or a CLI.
The [BookRec application](../bookrec/01-model.md) demonstrates that division.

## Generate from a validated model

These contextual commands assume a supported non-temporal `model.orm.yaml`
and a new destination directory:

```sh
gnd validate model.orm.yaml --format json
gnd codegen model.orm.yaml --out application
gnd conformance model.orm.yaml application --format json
```

Inspect the generated manifest and project before writing extension code.
The generator checks emitted Python syntax before publication and records the
derived files' digests. Generated tools correspond to model fact types; model
readings inform their docstrings. The project includes no provider SDK or
network client merely because it has an agent skill.

## Know which files you own

| Surface | Owner | How to change it |
|---|---|---|
| Derived tools, generated skill, extraction artifacts | Generator | Change the model where appropriate, then explicitly regenerate |
| Create-once `pyproject.toml`, references, architecture contract | Developer | Edit deliberately; regeneration preserves these files |
| Application entry points and business behavior you add | Developer | Ordinary code changes, tests, and smoke checks |

Repeating codegen for an unchanged model is idempotent. An edited derived file
or an unmanaged file occupying a derived path is refused, normally at exit
`11`. `--force` permits overwrite/adoption of such derived paths; it still does
not overwrite extension-owned files. Use it only after deciding that the
existing derived bytes should be replaced.

## Declare and exercise the runnable application

The create-once `architecture.contract.yaml` describes modules and symbols,
required artifacts, entry points, and smoke commands. Update it as you add the
application's runnable behavior. The generated pytest smoke module reads that
contract and runs its declared commands. A smoke row must actually start the
entry point and receive the declared exit; an unresolved module is not a
successful expected failure.

Static conformance and smoke execution have different jobs. Conformance reads
bytes and Python AST without importing your application. Smoke tests execute
your code with your own process permissions. Add focused application tests for
behavior that a return-code smoke does not establish.

## Interpret conformance

Conformance checks four areas:

1. **Integrity:** do derived bytes still match their manifest entries?
2. **Currency:** was the project generated from the current model?
3. **Structure:** do generated functions and artifacts agree with the model's
   declared vocabulary, independently of the stored manifest claims?
4. **Architecture:** do the declared modules, symbols, paths and entry points
   match static observations?

Exit `0` means these checks found no mismatch; exit `13` means drift. Missing
or malformed inputs have different refusal bands. Read the affected file,
assertion, examined/unexamined sets, and `limits` in the JSON report.

Conformance does not establish the correctness of arbitrary extension code.
Digest comparison alone also cannot detect a file co-edited with its manifest
entry; structural checks provide separate evidence, not a universal tamper
proof. After model evolution, a drift result calls for a decision about
regeneration and extension changes; GND does not regenerate automatically.

See the authoritative
[code generation contract](https://github.com/vasiloglou/gnd-public/blob/main/src/gnd/skills/gnd-codegen/references/codegen-contract.md),
[architecture contract](https://github.com/vasiloglou/gnd-public/blob/main/src/gnd/skills/gnd-codegen/references/architecture-contract.md),
and [conformance contract](https://github.com/vasiloglou/gnd-public/blob/main/src/gnd/skills/gnd-conformance/references/conformance-contract.md).
