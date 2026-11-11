# OS1 exporter review: candidate 050a2f62, base 47e2ce98

**Decision: changes requested. Do not write the OS1 completion record yet.** The core mapping and the publication primitive held up. I found one likely bug on valid input (F1) and one semantic gap (F2). Two items need an owner ruling (F3, F5), and a likely YAML hazard needs a quick test (F4). The pinned external lane has not run, so OS1-C2 is open, as the candidate record says.

I read files only and ran nothing. I did not confirm that my working tree is at 050a2f62, and I did not diff the fixture repairs. Every finding below comes from reading the code, not from an executed repro.

## Findings

**F1 (High, likely): a valid model without object-type `name` exits 70.**
- `name` is optional in the model schema (`src/gnd/schema/orm-meta.schema.json:261`). GND's own validator defaults it to the id (`src/gnd/model/_validation.py:502`).
- `ModelIndex` returns the raw rows with no default (`src/gnd/model_index.py:117-120`).
- The exporter indexes `obj["name"]` at `src/gnd/export/ossie.py:72`, `:76` and `:262`. That raises `KeyError`, which `src/gnd/commands/export.py:87` maps to exit 70.
- To confirm, export a six-line model whose object types omit `name`. The expected behaviour is a `gnd_<id>` or id-derived concept name, not exit 70.
- All 38 eligible census models name every object type, so the census cannot catch this.

**F2 (Medium): composite `identify_by` does not check that the link is functional.**
- `_add_references` (`ossie.py:161-186`) only checks arity 2, that the first-role type is the owner, and that the role ref names the second role.
- It never checks that `_role_order` produced `ManyToOne` or `OneToOne`. A fact with no internal uniqueness, or only a spanning one, still lands in `identify_by`. The constraint is then marked native at `ossie.py:215`.
- GND's own rule is just as loose (`_validation.py:634-644`), so a valid model can reach this.
- To confirm: take the `reference_scheme_elicitation` Task model, drop the two single-role uniqueness constraints (examples lines 129 and 136), and re-export. I expect `identify_by` to list relationships with no multiplicity.

**F3 (Medium, needs a ruling): a `proposed` or `deontic` uniqueness becomes a native multiplicity.**
- `_role_order` (`ossie.py:97-121`) and the composite pass ignore `status` and `modality`.
- OS0 ruled that modality pointers go to the sidecar. Nothing in OS0 or OS1 covers `status: proposed`, which is allowed on active constraints; `status: rejected` is excluded (`_validation.py:866`).
- A reader of the ontology alone sees `OneToOne` for a constraint nobody confirmed.
- Either gate native multiplicity on `confirmed`, or record the ruling and pin it with a test. The test fixture `MODALITY` (`tests/test_ossie_export.py:32-37`) only uses alethic and confirmed.

**F4 (Medium, not reproduced): YAML 1.1 reader hazard.**
- The writer is ruamel with default 1.2 semantics (`ossie.py:390-395`). The pinned parser environments use PyYAML 6.0.3 (`.gnd-planning/milestones/ossie-interchange/evidence/OS0/pins.json:20`).
- GND role names match `^[a-z][a-z0-9_]*$`, so `on`, `off`, `no`, `yes`, `y` and `n` are legal. As I recall (unverified), ruamel emits them unquoted, and PyYAML would read them as booleans, failing the schema's `name: string`.
- The ordinary census test uses JSON only (`tests/test_ossie_export.py:69`). The oracle lane does use YAML, but no census role has these names.
- To confirm, export a synthetic model with a role named `on` or `no`, then load the YAML with a 1.1 loader.

**F5 (Low–Medium): strict mode trips on empty population containers.** `_metadata` marks a refusal as soon as the path is `reference_populations` or `sample_population` (`ossie.py:342-346`, `:357-359`). An empty `reference_populations: []` or `sample_population: []` also sets `refused`, so strict exits 3 with nothing lost. GND's own docs treat `[]` as the absent case (`representation-format.md:898`). Decide whether to count only non-empty containers.

**F6 (Low): the CLI help for `--strict` over-promises.** It says "refuse any export with lost elements" (`src/gnd/commands/export.py:164`). Strict only refuses population rows, not extension rows. The CLI golden copies the same string (`tests/test_rf1_cli_pins.py:241`), so the golden would not notice a mismatch.

## Test gaps against the acceptance cases

- **Subtype cycles:** the `ossie:cyclic-subtypes` branch (`ossie.py:220-223`) is real, because validation does not reject cycles (`_validation.py:1163-1164`). No test reaches it; a grep of the Ossie tests for "cyclic" finds nothing.
- **Depth and non-JSON metadata:** the spec says depth and non-JSON metadata exit 3, and the `json_document` → `OssieInputError` mapping (`ossie.py:65-68`) is new to this command. The refusal-order test covers only missing, malformed, oversized, include, alias and missing-parent (`tests/test_ossie_export.py:225-255`). There are no depth, FIFO, directory or non-JSON cases.
- **Census count:** nothing asserts 41 paths, 38 exports and 3 refusals (`tests/test_ossie_export.py:24`).
- **Oracle include check:** the oracle test accepts any refusal under `/expense/teams/` (`tests/test_ossie_external_oracle.py:39`), which also covers the non-include `shared/` files. The reason-string assertion limits the damage.
- **Source order:** the order claim at `phase-OS1-spec.md:98-99` is not tested, because `Counter` ignores order (`tests/test_ossie_export.py:81`). The sidecar's canonical JSON sorts keys (`src/gnd/artifacts.py:203-210`), so key order survives only in the loss-report rows.
- **Local validation:** it is schema-only (`ossie.py:383`). Dangling `extends`, `identify_by` or role concepts pass locally. The oracle's negative control covers only an unknown role concept (`tests/test_ossie_external_oracle.py:49-72`).
- **Publication I/O faults:** only link-step faults are injected (`tests/test_ossie_export.py:268-284`), not staging-write faults. The spec obligation says "induced I/O failure on each file".
- **Same-directory aliasing:** only `--loss-report == --out` is tested. `--loss-report == OUT.gnd.json` is covered by the same identity check but has no test.

## Claims checked and held

- **Pointers:**
  - `_pointers` (`ossie.py:89-90`) escapes `~` before `/`, as RFC 6901 requires.
  - `_metadata` walks each pointer once and sets one disposition per row, and the test compares the multiset of pointers.
- **Census:**
  - The 41 paths equal the 42 `.orm.*` files under the two inventory roots (`evidence/OS0/revised/reproduce/inventory.py:27`) minus `evals/expected/synthetic_good_user`, which is outside those roots by design.
  - `includes` refusals are data-driven in the ordinary test.
- **Refusal omission:**
  - Refused subtrees are skipped before any sidecar write (`ossie.py:357-371`).
  - Their pointer keys are fixed schema names or role names, so they carry no data (`orm-meta.schema.json:76-113`, `:652-657`).
  - The loss-report rows for those subtrees also carry no values.
- **Readings:**
  - The placeholder regex matches the validator's (`ossie.py:33` against `_validation.py:94`).
  - The validator enforces placeholder count equal to role count (`_validation.py:480-493`), so `next(forward)` cannot raise `StopIteration`.
  - The qualified-inverse set check and the bare-binary reversal are conservative.
- **Role order:**
  - The `by_omitted` guard keeps the `next(iter(...))` pick deterministic.
  - The ManyToOne owner is the determinant role, consistent with the synthetic test (`tests/test_ossie_export.py:141-161`).
  - I did not re-derive Ossie's ManyToOne convention. It rests on OS0 E4/E6 and the parser controls.
- **Determinism:** I found no output-affecting set iteration, and the schema validator is cached with `lru_cache`.
- **Pins:** `PINNED.json`, `evidence/OS0/pins.json` and `tools/ossie_oracle.py:15-17` agree on the commit and the schema SHA.
- **Publication (`src/gnd/safefs.py:533-578`):**
  - `os.link` never replaces an existing file, and linking to a dangling symlink returns EEXIST.
  - Rollback unlinks only the inode it created, and `ExitStack` discards each temp file before closing its directory.
  - `src/gnd/commands/export.py:91-102` publishes loss report, sidecar, then document, and maps exists, I/O and artifact errors to 11 and 74.
  - Alias and missing-parent cases leave no stray files.
- **Duplicate ids:** these are refused at validation (`_validation.py:367`), so the index maps cannot drift from the document order.

## Not reproduced

- Anything dynamic: no test, repro or oracle was run. F1, F2 and F4 are static readings that need a short synthetic model each.
- I did not read the Ossie `ontology.md` semantics, and I did not diff the four fixture role renames or check whether skill prose still matches them.
- A grep of the skill examples, with a path I wrote against the main checkout instead of this worktree, was denied. I did not retry it. Everything else used worktree paths.

## Required before an OS1 completion record

1. Fix F1 and add a no-`name` test.
2. Fix F2 (require a functional relationship) or record an owner ruling, and add a test either way.
3. Get a ruling on F3 and pin it with a test.
4. Add the F4 YAML round-trip test, and cover the cycle, depth and non-JSON, and FIFO and directory exit cases.
5. Run the selected pinned lane and record its output separately from the local results.

I can draft the synthetic cases for F1, F2 and F4 if you want them. Writing them needs edit access, so I haven't started.
