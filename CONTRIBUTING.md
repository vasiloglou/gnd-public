# Contributing

Work from this repository alone with Python >=3.11 and uv 0.10.10:

```sh
uv sync --locked --group dev
uv run gnd install --symlink --project --force
uv run gnd doctor --project
uv run pytest -q tests/test_release_examples.py tests/test_contributor_preparation.py tests/test_review_credential_launcher.py
```

Tracked installer links have no local receipt in a fresh clone. Adopt them once
with --force; never overwrite modified links or maintain them manually. Both
.codex and .claude roots contain the packaged links and real development-skill
twins. Regenerate packaged links through gnd install, keep real twins identical.
Ordinary development uses this checkout's editable package. Final acceptance
will additionally exercise the exact installed candidate in a fresh target-only
tree, with actual module/tool/link paths recorded.

Numbered work follows the full [process-phase](.codex/skills/process-phase/SKILL.md)
protocol: spec, owner gate, implementation, independent review, refactoring review,
record and explicit-path commit. The [sample spec](docs/development/examples/phase-spec.md)
and [sample record](docs/development/examples/phase-record.md) are non-authoritative
exercises. Source-owned runtime units await explicit handoff; changes here do not
silently transfer authority. Phase 3 final acceptance is pending.

Run focused affected tests with the default lane exclusions. Historical broad,
provider/native and certification lanes require separate selection. Never source
repository .env files; optional live review needs trusted credentials and explicit
selection. [Bootstrap history](docs/development/bootstrap.md) is historical;
the old original-definition accounting runner is not release acceptance under r3.
See [release preparation](docs/releasing.md) and [security reporting](SECURITY.md).

## Owner-controlled contributions

Contributions are by invitation. Only collaborators approved by `vasiloglou`
receive write access. Public availability permits reading and forking; it does
not grant permission to modify this repository.

For all changes, including owner and coding-agent changes, use a topic branch and
submit a pull request. Never push directly to main, force-push it, or delete it. Resolve
review conversations before merging. `.github/CODEOWNERS` names `vasiloglou` for
all files.

While `vasiloglou` is the only collaborator, branch protection requires PRs with
zero required approving reviews. GitHub prohibits authors from approving their
own PRs, so the owner's explicit merge decision is the acceptance step. Coding
agents may merge only with the owner's explicit authorization. Protection applies
to administrators too, with no PR bypass. Cloud CI is not currently a required
status check; run the focused checks applicable to a change and record results.

Before granting another account write access, enable one required approving
review and required code-owner review. Its PRs will then require `vasiloglou`'s
recorded approval. PRs authored by `vasiloglou` will need another authorized code
owner, or work must be authored through a separately controlled contributor/bot
identity so `vasiloglou` can approve. Never create a shared reviewer identity or
approve a PR through a token belonging to its author.

For a public repository, use the collaborators-only interaction limit to prevent
outside PRs, issues and comments. GitHub limits this setting to six months; renew
it before its reported expiration. It cannot be enabled while the repository is
private. Check the live settings before claiming restrictions are enforced.

## Refactoring dependencies and compatibility

The measured layer map is [tools/gnd_layers.json](tools/gnd_layers.json).
Errors and schemas have infrastructure homes; documents, values and universe
serve model data and lookup; extensions compute facts below checker and
applicability. Registry descriptors live in branches. Runtime graph checks count
lazy and literal dynamic imports as well as top-level imports. Add every new
module to the map, preserve the clean-layer ratchet, and do not grow allowances.

Old module names retain explicit aliases in the
[shim inventory](.gnd-planning/milestones/code-refactoring/notes/shim-inventory.md).
Patch the defining module for moved algorithms and the actual public lookup seam
for consumer wrappers. Move tests pin alias identity and source-scan coverage;
retirement follows the approved plan's RF-D5 gate. Current source changes make
old release evidence unavailable until its separately selected controls run.

Peripheral dependency homes are public filesystem seams in safefs, the bounded
runner in process, trusted adapters in agents, and the independent synth oracle
package. Assurance follows _wire, core, inheritance, claims, evidence dependency
order; transport carries receipts. Payload assembly lives in payloads, and
export/witness services own their thin API wrappers. Old imports remain aliases.

### Model query and constraint family homes

Use gnd.model_index.ModelIndex.for_model(model) for detached model queries. Each
request keys a bounded snapshot cache by current full model content, with unsafe
canonical shapes bypassing the cache. Keep the existing strict/truthy primitive
policy explicit. Raw serialization and deliberately retained domain traversal
sites are individually listed in the RF6 query policy; additions need a reason
and a current behavior control.

Constraint adaptation, evaluation, witness projection, presentation, scope and
shape selection use gnd.constraint_families.FAMILIES. Keep shared refusal and
vacuity precedence outside family-specific algorithms. The production branch
evidence registry remains a separate inventory. Preserve every historical import
shim until a separately approved retirement after the first release following RF6.
