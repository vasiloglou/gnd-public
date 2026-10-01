# The architecture contract

This is the single normative format reference for the create-once
`architecture.contract.yaml` emitted by [`../SKILL.md`](../SKILL.md). The file
declares a generated project's intended structure and runnable surface. Loading
it establishes only that the declaration is closed, bounded, and internally
consistent; it does not inspect declared files or execute declared behavior.

## Location and ownership

The contract is the literal project-root path `architecture.contract.yaml`.
`gnd codegen` creates a loader-valid skeleton once, records it as an extension,
and never rewrites it—not on an ordinary rerun and not with `--force`. Paths in
the contract are project-root-relative POSIX paths. The loader reads the
contract itself through a bounded, regular-file, no-follow open and never opens
a path declared inside it.

## Closed format

YAML is the authored syntax; JSON is accepted because it is a YAML subset. All
five root keys are required, even when their lists are empty. Unknown fields are
refused at every level, strings are strict strings, and integer fields do not
accept booleans.

| Coordinate | Type | Meaning |
|---|---|---|
| `contract_version` | integer, exactly `1` | format version |
| `modules` | list of module rows | source modules whose public symbols are declared |
| `modules[].path` | string path | project-root-relative module path |
| `modules[].symbols` | list of symbol rows | public symbols expected in the module |
| `modules[].symbols[].name` | string | symbol name |
| `modules[].symbols[].parameters` | list of strings | parameter names in declared order |
| `artifacts` | list of artifact rows | project artifacts the declaration inventories |
| `artifacts[].path` | string path | project-root-relative artifact path |
| `artifacts[].required_by` | list of string paths | module paths that require the artifact |
| `entry_points` | list of entry-point rows | dotted Python modules that expose runnable behavior |
| `entry_points[].module` | string | unique dotted module name and smoke-row identity |
| `entry_points[].subcommands` | list of strings | declared subcommand vocabulary |
| `entry_points[].flags` | list of strings | declared flag vocabulary |
| `entry_points[].consumes` | list of strings | declared input/fact vocabulary |
| `entry_points[].produces` | list of strings | declared output/fact vocabulary |
| `entry_points[].exits` | list of exit rows | declared exit-code meanings |
| `entry_points[].exits[].code` | integer, `0`–`255` | declared process exit code |
| `entry_points[].exits[].meaning` | string | human-readable meaning of the exit |
| `smoke` | list of smoke rows | runnable examples executed by the smoke runner |
| `smoke[].id` | string | unique smoke-row id |
| `smoke[].entry_point` | string | one declared `entry_points[].module` |
| `smoke[].argv` | list of strings | argument vector, excluding the interpreter/module launch |
| `smoke[].expect_exit` | integer, `0`–`255` | an exit code declared by the named entry point |

An empty `artifacts[].required_by` list is a pure-existence declaration. In
particular, the codegen skeleton inventories its four generated artifacts with
`required_by: []`; that does not arm a path-mismatch check. There is no
`model_sha256` field. Model currency remains a separate conformance claim.

## Paths, exits, and substitutions

Every module path, artifact path, and `required_by` path must use a normalized,
non-empty relative POSIX spelling. Absolute POSIX paths, Windows drive or UNC
roots, NUL, backslashes, `..`, `.` or empty components, and doubled separators
are refused lexically before any declared path is opened.

Entry-point module names and smoke ids are unique. Each smoke row must name one
unambiguous entry point, and its `expect_exit` must occur in that entry point's
`exits[].code` list.

The only smoke-argv substitution is the literal `{tmp}`. It may be a whole
token or part of one, such as `{tmp}/out.json`. Other names, conversions,
format specifications, escaped braces, and unmatched braces are refused. The
loader validates this declaration but does not perform the substitution or run
the command.

## Validation order and diagnostics

The filesystem wrapper first performs the bounded no-follow read. The byte
parser then applies, in order: UTF-8 decode; YAML event and alias preflight;
exactly-one-document safe parse; closed shape validation; one lexical path
walk; entry-point uniqueness; smoke-id uniqueness; smoke entry-point
resolution; declared-exit membership; argv substitution validation. Shape
failure prevents semantic walks over an untrusted value. Once shape validation
succeeds, semantic issues are accumulated in the order below.

| Order | Rule id | Refusal |
|---:|---|---|
| 1 | `architecture:path-invalid` | a declared project path violates the lexical policy |
| 2 | `architecture:entry-point-duplicate` | entry-point module identity is duplicated |
| 3 | `architecture:smoke-id-characters` | a smoke id contains `[`, `]`, or whitespace |
| 4 | `architecture:smoke-id-duplicate` | smoke id is duplicated |
| 5 | `architecture:smoke-entry-point-unknown` | a smoke row names no unique declared entry point |
| 6 | `architecture:smoke-exit-undeclared` | expected exit is absent from the named entry point |
| 7 | `architecture:smoke-substitution` | an argv token contains a substitution other than `{tmp}` |

A smoke id becomes the pytest node id `test_smoke[<id>]`, which is the exact
string a tests-mode session contract cites in `required_tests`. A bracket closes
the parametrize segment early and whitespace splits an id no selector can name
again, so both are refused at authoring time rather than diagnosed at gate time
-- where the only symptom is a required test that never appears.

Pre-semantic failures use the closed diagnostic ids
`architecture:decode`, `architecture:document-too-large`,
`architecture:yaml`, `architecture:yaml-alias`,
`architecture:yaml-document-count`, `architecture:shape`, and
`architecture:read`. They remain diagnostics on one loader error surface; they
do not create CLI exit bands.

## Running the smoke rows

`gnd codegen` emits `test_architecture_smoke_<package>.py` beside this contract:
three lines that hand every declared row to `gnd.archsmoke` under pytest. The
runner **re-reads this file at test time**, so editing a row changes what runs
with no regeneration step, and the emitted module is create-once -- your bytes,
never rewritten.

The basename carries the package because pytest's default import mode requires
unique test-module basenames across roots without `__init__.py`; two projects
emitting one shared basename abort collection outright.

A row passes only when the entry point **started** and exited its declared code.
An entry point that never resolved is reported as `did-not-start` and is never
compared to a declared band -- `python -m` on a missing module exits 1, which is
also a legitimate declared refusal, so the exit code alone cannot tell them
apart. A row is additionally bounded: its process group is killed at the
deadline, and each captured stream stops at 64 KiB.

Smoke **executes your project's code with your own identity**. It is an
acceptance convenience, never a security boundary, and GND does not sandbox it.
Static conformance never runs any of this: nothing under `gnd.conformance`
imports the runner, and a test pins that.

Declared exits that no row cites are reported as unarmed by
`gnd.archsmoke.uncited_exits`. A declared exit is documentation until a row
runs it.

## Resource and claim limits

The contract is capped at 1 MiB on both filesystem reads and byte parsing. YAML
aliases are refused, and event preflight is capped at 100,000 events before
object construction. Semantic validation is linear in the declared list and
argv sizes.

A loader-valid contract asserts no static conformance, executed behavior,
design quality, or correctness. Static checks and smoke execution are separate,
later consumers with separate evidence. Editing this extension file does not
alter the model or the digest-gated derived surface.
