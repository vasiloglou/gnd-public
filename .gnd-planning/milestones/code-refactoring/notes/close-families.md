# code-refactoring — predicate 3 and the RF0 helper-family list

Read-only, 2026-11-25. Paths are relative to
`.gnd-planning/milestones/code-refactoring/` unless they start with `src/`;
`hf` = `notes/helper-families.md`, `NNN:L` = record line.

**Predicate 3** (`notes/code-refactoring-plan.md:75–77`): "every family that
the RF0 family list marks identical has exactly one definition. Every family
marked diverged keeps its variants, each pinned byte for byte, as RF-D11 rules."

**How the list defines identical** (hf:6–9; RF0 D7,
`notes/phase-RF0-spec.md:257`): an AST-identical group is an
*identical-candidate*. It "becomes *identical*, and so mergeable in RF2, only
when RF1's byte pins agree on every pinned input." `helper-families.md` was
never revised after RF0. No group in it is relabelled from "identical-candidate"
to "identical" or "diverged". The pin-agreement determination is recorded
only where RF2 says "promotion only after RF1 pin agreement"
(`notes/phase-RF2-spec.md:33`) and where RF6a says "merge only after
pre-existing helper pins exit0" (`notes/phase-RF6a-spec.md:38`).

**Current-source column.** This column was produced by running
`tools/gnd_arch.py measure` (Python 3.14.4) into scratch over two trees. The
first is `a390599`, the last production subject of the milestone (017
frontmatter). The second is the current `HEAD` `99cf3df2`. Both report the same
sites for every RF0 group, apart from line drift and one extra constructor site
at HEAD. `a390599` shows 12 AST-identical groups, matching RF9's "15 → 12"
(015:98). This column is a measurement, not a ruling.

## A. The 15 AST-identical groups

| Hash | RF0 classification (hf line) | Ruling applied | Single home or separate | Current source (a390599 / HEAD) |
|---|---|---|---|---|
| `f4d89086` sha256 hex (5 sites) | identical-candidate; "RF2 target" (hf:20) | **Merged in RF2.** Design A: the existing `sha256_hex` "remains the single body"; the other four become aliases (notes/phase-RF2-spec.md:125–127). D8 target 17→5 approved (:230, :367–371). Record: "Five RF2-owned identical groups went from 17 definitions to five" (007:278–279); RF2-C1 met (007:416). Shims at notes/shim-inventory.md:13–16. | One home: `gnd.artifacts.sha256_hex` | Group absent. `src/gnd/artifacts.py:232` |
| `2f5a20a1` report text (3 sites) | identical-candidate; "compact canonical JSON text. RF2 target" (hf:21) | **Merged in RF2** as `canonical_report_text` (notes/phase-RF2-spec.md:118–124). The spec notes "The family note's word 'compact' is incorrect" (indent=2). RF2-OQ1 sends that wording to close (007:530–532). Shims at notes/shim-inventory.md:10–12. | One home: `gnd.artifacts.canonical_report_text` | Group absent. `src/gnd/artifacts.py:1735`; three alias imports |
| `0f1cc1a7` safe-fs coordinate (2 sites) | identical-candidate; "RF4 (`safefs`) target" (hf:22) | **Kept separate by an RF4 ruling.** Harvest row: "filesystem identical candidates and all16variants move without merge" (notes/phase-RF4-spec.md:27). Design F: "Keep artifact and domain filesystem variants distinct" (:46). D2: "novariantmerge" (:65). Record: "They remain distinct" (009:200). Close item: reconcile this "visibility-only" decision with the plan wording (009:331). No record says whether RF1 pins agree for this pair. | Two definitions, not merged | Same hash: `artifacts._safe_fs_coordinate:231/238`, `conformance.structural._safe_coordinate:348` |
| `3d106ff9` directory identity (2 sites) | identical-candidate; "RF4 (`safefs`) target" (hf:23) | **Kept separate by an RF4 ruling.** Design F: "No merge of nested artifact directoryidentity and structural variant. T-PRE pays RF1 debt even though nestedbody stays" (notes/phase-RF4-spec.md:46). RF4 supplied the owed refusal pin (009:200; 006:204–207; RF1-07 in notes/phase-RF1-codex-review.md:29). No record says whether RF1 pins agree for this pair. | Two definitions, not merged | Same hash: `artifacts.directory_identity:309/316` (nested), `conformance.structural._directory_identity:338` |
| `5bebc70e` non-finite JSON hook (4 sites) | identical-candidate; "moving it is RF2 (move only)" (hf:24) | **Merged in RF2** as `reject_json_constant`, "four definitions" (notes/phase-RF2-spec.md:144). Nested hooks removed, readers pass the imported function (:150–155). | One home: `gnd.artifacts.reject_json_constant` | Group absent. `src/gnd/artifacts.py:1746` |
| `d9f0cf8e` duplicate-key hook A (3 sites) | identical-candidate; same treatment as above (hf:25) | **Merged in RF2** as `reject_json_duplicate_pairs`, "three definitions (including review.request's importable helper)" (notes/phase-RF2-spec.md:145–146). Alias at notes/shim-inventory.md:17. | One home: `gnd.artifacts.reject_json_duplicate_pairs` | Group absent. `src/gnd/artifacts.py:1750` |
| `dcbdd645` duplicate-key hook B (2 sites) | identical-candidate; "a second duplicate-key variant ... stays a separate variant unless RF1 pins show equal behavior" (hf:26) | **Merged within the group in RF2** as `reject_json_duplicate_pairs_result`, "two definitions; keep separate despite matching messages" (notes/phase-RF2-spec.md:147–148). Kept distinct from `d9f0cf8e`: "Both duplicate-hook variants remain distinct" (notes/shim-inventory.md:5). | One home for this group: `gnd.artifacts.reject_json_duplicate_pairs_result`. The duplicate-key family keeps two variants | Group absent. `src/gnd/artifacts.py:1759` |
| `22614c42` object types by id (3 sites) | identical-candidate; "model traversal. RF6 (`ModelIndex`) target" (hf:27) | **Algorithm merged in RF3/RF6a; wrapper definitions remain.** RF3 moved the popvalidate copy to `universe` (notes/shim-inventory.md:89). RF6a: "Identical model lookup families merge only after pre-existing helper pins exit0" (notes/phase-RF6a-spec.md:38). A3: "Shared object/role helper algorithms now serve three historical wrappers, retaining distinct original import metadata" (:94). A4: wrappers call "stateless compatibility methods on ModelIndex" (:102). Record: "stateless historical object/role/fact lookup aliases" (011:103). | Algorithm home: `gnd.model_index.ModelIndex.object_map` (`src/gnd/model_index.py:197`). Three one-line wrapper `def`s remain | New hash `cb7a0cdc`, still 3 sites: `universe._object_types_by_id:55/56`, `synth.oracle.constructive:102`, `synth.poolfile:178`, each `return ModelIndex.object_map(model)` |
| `c9b00e5d` role → object type (2 sites) | identical-candidate; "model traversal. RF6 target" (hf:28) | **Algorithm merged in RF6a; wrapper definitions remain.** Same A3/A4 rulings (notes/phase-RF6a-spec.md:94, :102; 011:103). | Algorithm home: `ModelIndex.role_map` (`src/gnd/model_index.py:203`). Two wrapper `def`s remain | New hash `e98b9c75`, 2 sites: `popvalidate._role_object_types:107`, `synth.oracle.constructive._role_object:106` |
| `ccbb68bd` `_rate` (2 sites) | identical-candidate; "Not in any planned family; recorded, no action proposed" (hf:29) | **Never addressed after RF1.** RF1 pinned it per group (notes/phase-RF1-spec.md:245–249). RF2 left it out of scope: "arithmetic and cross-meaning pairs not assigned to RF2" (notes/phase-RF2-spec.md:285–287). No RF4/RF6/RF8 spec or record names it. | Two definitions | Same hash: `fidelity.match._rate:83`, `measure.score._rate:294` |
| `c4e1c0f8` `_sorted_set` / `_canonical` (2 sites) | identical-candidate by AST, "names give different meanings. Not merged without an RF-D10 rename ruling" (hf:30) | **Never addressed; the precondition was never ruled.** RF1 gives the two their own non-encoder input sets (notes/phase-RF1-spec.md:235). RF2 left the cross-meaning pair out of scope (notes/phase-RF2-spec.md:285–287). No RF-D10 rename ruling for this pair appears in 003–017. | Two definitions | Same hash: `assurance.core._sorted_set:99`, `proof_bridge._canonical:302` |
| `73ae047d` pydantic `model_validate_json` override (3 sites) | identical-candidate; "RF8 scope (session)" (hf:31) | **Not ruled in RF8.** RF2 put it out of scope as "session duplicate bodies (RF8)" (notes/phase-RF2-spec.md:286). The RF8 spec has no row for it; store models were "physically moved verbatim" to `session_records` (notes/phase-RF8-spec.md:62). RF8 record: "No helper/schema/canonical encoder unification beyond this bounded session dependency change is claimed" (014:199). | Three definitions | New hash `fad2c39a`, still 3 sites: `session_eval:1307/1311`, `session_records:659`, `:955`. The body now calls `_rf7_input.loads` (RF7 C2 routing; 013:149) |
| `5153de62` session fork-evidence `entry` (2 sites) | identical-candidate; "RF8 scope" (hf:32) | **Not ruled in RF8.** `session_v7._entry` moved to `session_replay._entry` (notes/shim-inventory.md:861). No merge; 014:199 as above. | Two definitions | Same hash: `session_judgments.entry:133/135`, `session_replay._entry:57` |
| `cf363396` constructor | "trivial constructor; not a helper family" (hf:33) | Excluded as `not_a_family`, no pin (notes/phase-RF1-spec.md:249–250). | n/a | Still 2 sites at a390599; 3 at HEAD (`gnd.api:__init__` added after the milestone) |
| `cd3b7244` constructor | "trivial constructor; not a helper family" (hf:34) | Same as above. | n/a | Still 2 sites |

### Tally

- **Merged to one definition:** 5 groups, all in RF2 (`f4d89086`, `2f5a20a1`,
  `5bebc70e`, `d9f0cf8e`, `dcbdd645`). Homes are in `gnd.artifacts`.
- **Algorithm merged, wrapper definitions kept:** 2 groups (`22614c42`,
  `c9b00e5d`). Home is `ModelIndex`. They remain AST-identical groups of 3 and 2
  wrapper `def`s under new hashes.
- **Kept separate by an explicit ruling:** 2 groups (`0f1cc1a7`, `3d106ff9`),
  under RF4 spec D2 and design F.
- **Never addressed after RF1/RF2 scoping:** 4 groups (`ccbb68bd`, `c4e1c0f8`,
  `73ae047d`, `5153de62`). The two RF8-scoped groups were moved, not merged.
- **Not a family:** 2 groups (`cf363396`, `cd3b7244`).

### What this means for predicate 3 (observations, not rulings)

1. Predicate 3 binds only families "the RF0 family list marks identical". The
   list marks every group "identical-candidate" and was never updated. The
   records do not say whether the 8 groups that still have more than one
   definition (the 4 unaddressed, the 2 RF4-ruled, the 2 wrapper groups) are
   "identical" under D7. They therefore do not show whether those 8 groups fall
   under predicate 3.
2. RF2-C1 was scoped to "the RF2-owned groups"; "RF4/RF6/RF8 groups remain
   for their assigned phases" (notes/phase-RF2-spec.md:104–106). RF4 ruled no
   merge for its two. RF8 made no ruling on its two. RF6a merged the algorithm
   but kept the wrappers.
3. For `22614c42` and `c9b00e5d`, the close has to read "exactly one
   definition" as either one algorithm or one `def`. The records describe the
   wrappers as "historical wrappers" or "aliases" (011:103), but each wrapper is
   a separate `def`, not an import alias.

## B. RF0 identical-candidate groups inside diverged families

hf:40–44 say the identical-candidate groups inside the name-pattern families
are the groups in §A (`2f5a20a1` and `c4e1c0f8` in canonical_json;
`f4d89086` in sha256_hex; `0f1cc1a7` and `3d106ff9` in safe_filesystem). The
strict_json hooks `5bebc70e`, `d9f0cf8e` and `dcbdd645` are in hf:45. No
other identical-candidate group is listed.

## C. Diverged families (second half of predicate 3)

| Family (hf line) | RF0 class | What later records ruled | Variants kept? |
|---|---|---|---|
| canonical_json (hf:40) | 13 diverged (RF2 found 14: notes/phase-RF2-spec.md:394–397) | RF2-C2: "all fourteen source bodies equal the base SHA-256s" (007:417). RF7 amendment keeps "canonical encoder policies" out of scope (notes/RF7-plan-amendment.md:5; 013:364). | Yes |
| sha256_hex (hf:41) | 7 diverged | Not merged (RF2 design A only for `f4d89086`). | Yes |
| model_digest (hf:43) | diverged, "never merged (RF-R2)" | Renamed under RF-D10, algorithms distinct (007:316–319; 007:418). RF7 keeps "three digest meanings" (notes/phase-RF7-spec.md:20). | Yes |
| file_digest (hf:42) | diverged | **RF7 C6:** "File digest readers share regular-file nonblocking streaming primitive with raw/prefixed digest adapters" (notes/phase-RF7-spec.md:20, :37; 013:153). | Partly: one shared reader, adapters kept |
| strict_json (hf:45) | 6 diverged readers | **RF7 C2:** common `input_policy` loads/load/JSONDecoder across a 75-call inventory (013:149). | Merged into one intake policy, with domain adapters kept |
| yaml_guard (hf:47) | diverged | **RF7 C3:** guards added to two loaders; "Original other YAML loaders stay unchanged" (013:150). | Partly |
| iso_datetime (hf:48) | diverged | **RF7 C4:** "one strict ASCII ISO datetime parser across named GND sites", plus a copied grammar in standalone PyRel (013:151). | Merged (one parser plus a standalone copy) |
| safe_filesystem (hf:44) | 16 diverged | RF4: no merge (notes/phase-RF4-spec.md:46). RF7 C1 changed the safefs path policy (013:148). | Yes (policy changed) |
| validation_issues (hf:46) | diverged | RF2: one `issues_from_validation_error` where outputs are equal; "divergent converters remain" (007:311–312). | Yes |

**Disagreement:** RF-D11 (plan:494), predicate 3 (plan:75–77) and the risk row
"Diverged helpers get merged | RF-D11 keeps them separate" (plan:431) all say
diverged variants are kept. The RF7 spec rules "RF-D11 divergent helpers | C6:
merge input validators only (JSON/YAML/datetime/resolver)"
(notes/phase-RF7-spec.md:20). Yet the owner-directed amendment says it
supersedes only "RF-D7 ... and behavior-preservation requirement RF-R1"
(notes/RF7-plan-amendment.md:3). It does not name RF-D11.
