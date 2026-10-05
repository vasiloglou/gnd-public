# Helper families — RF0 classification

Source: [`metrics-RF0.json`](../evidence/metrics-RF0.json) at base `19b131b`,
Python 3.14. The classification follows RF0 decision D7:

- **identical-candidate** — two or more sites in different modules whose
  `ast.dump` is equal once the docstring and the function name are removed
  (argument names are kept). A candidate becomes *identical*, and so
  mergeable in RF2, only when RF1's byte pins agree on every pinned input.
- **diverged** — anything else. Under RF-D11, diverged variants stay
  separate in this milestone, each pinned byte for byte.

Hashes are the first eight hex digits of the tool's sha256, which is
comparable only under Python 3.14.

## AST-identical groups (15)

| Hash | Sites | Classification and reason |
|---|---|---|
| `f4d89086` | `artifacts.sha256_hex:210`, `assurance_evidence._sha:55`, `diff._digest:29`, `install._sha256:257`, `recovery.verify._sha256:51` | identical-candidate: one-line sha256 hex helper. RF2 target (`artifacts.sha256_hex`) |
| `2f5a20a1` | `conformance.report.canonical:181`, `coverage.canonical_payload:226`, `fidelity.report.canonical:153` | identical-candidate: compact canonical JSON text. RF2 target |
| `0f1cc1a7` | `artifacts._safe_fs_coordinate:216`, `conformance.structural._safe_coordinate:348` | identical-candidate: safe-filesystem coordinate. RF4 (`safefs`) target |
| `3d106ff9` | `artifacts.directory_identity:294`, `conformance.structural._directory_identity:338` | identical-candidate: directory identity. RF4 (`safefs`) target |
| `5bebc70e` | `declared_adapter.reject_constant:95`, `exp.adapter_policy.reject_constant:211`, `exp.session_eval.reject_constant:1379`, `exp.session_store.reject_constant:169` | identical-candidate: strict-JSON non-finite hook. Belongs to the strict-JSON family; moving it is RF2 (move only), and tightening is deferred (RF-D7) |
| `d9f0cf8e` | `declared_adapter.reject_duplicates:98`, `exp.session_store.reject_duplicates:172`, `review.request._reject_duplicate_object_pairs:626` | identical-candidate: duplicate-key hook. Same treatment as `5bebc70e` |
| `dcbdd645` | `exp.adapter_policy.reject_duplicates:214`, `exp.session_eval.reject_duplicate_pairs:1382` | identical-candidate, but a second duplicate-key variant that differs from `d9f0cf8e`. It stays a separate variant unless RF1 pins show equal behavior |
| `22614c42` | `popvalidate._object_types_by_id:88`, `synth.assemble._object_types_by_id:179`, `synth.poolfile._object_types_by_id:176` | identical-candidate: model traversal. RF6 (`ModelIndex`) target |
| `c9b00e5d` | `popvalidate._role_object_types:94`, `synth.assemble._role_object:183` | identical-candidate: model traversal. RF6 target |
| `ccbb68bd` | `fidelity.match._rate:83`, `measure.score._rate:294` | identical-candidate: small arithmetic helper. Not in any planned family; recorded, no action proposed |
| `c4e1c0f8` | `assurance._sorted_set:102`, `proof_bridge._canonical:301` | identical-candidate by AST, but the two names give different meanings. Not merged without an RF-D10 rename ruling |
| `73ae047d` | `exp.session_eval.model_validate_json:1301`, `exp.session_store.model_validate_json:714`, `:1010` | identical-candidate: pydantic override boilerplate. RF8 scope (session) |
| `5153de62` | `exp.session_judgments.entry:133`, `exp.session_v7._entry:69` | identical-candidate: session fork evidence. RF8 scope |
| `cf363396` | `exp.junit.__init__:177`, `exp.tests_runner.__init__:256` | trivial constructor; not a helper family |
| `cd3b7244` | `exp.session_patch.__init__:17`, `json_input.__init__:13` | trivial constructor; not a helper family |

## Name-pattern families

| Family | Sites | Distinct ASTs | Classification |
|---|---|---|---|
| canonical_json | 18 | 16 | One identical-candidate group (`2f5a20a1`, 3 sites) and one cross-meaning pair (`c4e1c0f8`). The other 13 are **diverged**: `artifacts.canonical_json_bytes` and `canonical_json_text` (the canonical home), `assurance_inheritance`, `model_verbalization`, `evolve.models`, `review.request`, `synth.poolfile`, `codegen.emit`, `extract.anchors`, `measure.report`, `transition`, and the two `cli` helpers. They differ in annotations, docstrings, `try` wrappers, model-dump preprocessing and newline handling. The audit's "11 identical" refers to this set (baseline finding F2) |
| sha256_hex | 12 | 8 | Group `f4d89086` (5 sites) is an identical-candidate. **Diverged:** `codegen.manifest.digest_text`, `export.souffle.digest`, `extract.anchors._digest`, `judgments.digest`, `measure.promote._digest`, `population._content_digest`, `synth.poolfile._sha256` (different inputs or prefixes) |
| file_digest | 5 | 5 | **diverged** (`evolve.service` ×2, `exp.tests_runner`, `synth.provenance`, `transition`). The audit reports different symlink handling |
| model_digest | 5 | 5 | **diverged**: five sites, three output meanings (baseline A12). RF2 renames them under RF-D10; they are never merged (RF-R2) |
| safe_filesystem | 16 | 16 | **diverged**, plus the two identical-candidates above (`0f1cc1a7`, `3d106ff9`), which are found by body rather than by name. RF4 moves them without merging; tightening is deferred |
| strict_json | 6 | 6 | **diverged** readers. The hooks inside them form the identical-candidate groups `5bebc70e`, `d9f0cf8e` and `dcbdd645` |
| validation_issues | 6 | 6 | **diverged**: the rule ids are embedded, as the audit reports. RF2's `issues_from_validation_error` applies only where RF1 pins show the same output |
| yaml_guard | 5 | 5 | **diverged**; tightening is deferred (RF-D7) |
| iso_datetime | 2 | 2 | **diverged** (`popvalidate._is_datetime` vs `synth.values._parse_datetime`); the result affects verdicts, and tightening is deferred |

Each regular expression in `helper_patterns` (`tools/gnd_layers.json`) is
listed once, as the family names above.
