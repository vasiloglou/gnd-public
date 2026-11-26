# F7 review: compatibility migration table, generator and guide

All six SHA-256 values match the brief, so I read the bytes it names. Running the generator in memory, with nothing written, produces output identical to `migration.tsv`. I ran it from this checkout's `src` using the venv of the sibling F6 review checkout.

Short answer: every literal, RF4 and RF8 row has a disposition, but many migration targets can't be used as given, and the identity and patch limits aren't clear yet.

## 1. Findings

**F1: 341 migration targets are themselves re-bindings, not where the name is defined** (`audit.py:66-68`, and the RF6b and RF9 rows copied from the inventory)
- **What is wrong:** I parsed each target's module and found 341 targets that the module only imports from elsewhere:

  | Phase | Rows |
  |---|---|
  | RF6b | 208 |
  | RF4 | 104 |
  | RF9-repair | 12 |
  | RF8 imports | 8 |
  | RF3 | 5 |
  | RF2 | 3 |
  | MC1 | 1 |

- **Rows pointing at the standard library (111 of them):**
  - `migration.tsv:282` sends `gnd.model.json` to `gnd.model._validation.json`, which is really the standard `json` module.
  - `:280` sends `gnd.model.annotations` to `gnd.model._validation.annotations`, really `__future__.annotations`.
  - `gnd.agent_cli.asyncio` goes to `gnd.process.asyncio`, and `gnd.synth.mutate.Path` goes to `gnd.synth.oracle.mutations.Path`.
- **Rows pointing at another gnd alias (230 of them):**
  - `gnd.checker._core._identity_key` is only an import of `gnd.values.identity_key`.
  - `gnd.output.CheckReport` is an import of `gnd.checker.CheckReport`.
  - `gnd.exp.session_store.AttemptRecord` is an import of `gnd.exp.session_records.AttemptRecord`.
- **Cause in the generator:** at line 67, the RF4 fallback throws away the origin it already found whenever that origin is outside the new module. It then writes `f"{new}.{name}"` instead.
- **What a reader would see:** the guide says "For an ordinary import, use the migration target". Following it, people would import `json` from a private gnd module, or switch from one alias to another alias that may itself be retired later.

**F2: 118 historical names have several different targets, and the guide's rule for following them breaks**
- **Duplicates:** `gnd.checker._identity_key` appears as RF3 → `gnd.values.identity_key` and as RF6b → `gnd.checker._core._identity_key`. `gnd.checker._PHASE3_LEGACY_CONSTRAINT_VIEW` has three different targets. The guide doesn't say which one to use.
- **The "later row" rule:** the guide says to "follow its target through any later row". But RF4 and RF8-import rows are appended after MC1 rows, so the file is not in time order.
- **Nine chains go backwards:** the next step for each is an earlier row. For example, row 1364 maps `session_v7.AttemptRecord` → `session_store.AttemptRecord`, and the next step for that name is at row 776. Another is row 1372 → row 477.
- **What a reader would see:** someone following the stated rule stops at an alias.

**F3: 36 rows map a name to itself**
- **Examples:** `gnd.model.load_model`, `gnd.model.Literal`, `gnd.model.os`, `gnd.model.MAX_BYTES` and `gnd.model.retained_root` each have the same historical name and target.
- **Why it matters:** the identity check is trivially "same object" for these. They also carry the release text "later removal needs approval", which suggests the public `gnd.model.load_model` could be removed.
- **What is missing:** the rows give no migration (for example "import `os` directly", or "this is the stable public name").

**F4: The two "bound" identity cells come from note text, not a live check, and the generator has no dirty control** (`audit.py:162-163`)
- **What is wrong:** line 158 computes the live identity result, and lines 162-163 then overwrite it with whatever the inventory note says.
- **How I tested it:** in memory, I deleted `gnd.exp.conclusions._validation_issues` and changed `gnd.exp.spec._validation_issues` to bind `"WRONG_ID"`. The generator still printed `bound SPEC_RULE_ID` and `bound CONCLUSIONS_RULE_ID`, both with "retain".
- **Spec gap:** the spec requires the generator to "Exercise live identity, current patch lookup, and a dirty control". `audit.py` only does the identity check. Patch lookup is a static scan only, and there is no dirty control.
- **Consequence:** the table can't detect a broken wrapper or a missing binding.

**F5: The patch scan misses common `unittest.mock` forms, including one that really occurs** (`audit.py:105-119`)
- **Real miss:** `tests/test_public_phase4_transition_support.py:393` runs `patch.multiple(transition, _refuse=..., ...)`. That patches `gnd.transition._refuse`, but the `patch_old` cell for that row (`migration.tsv:56`) is empty.
- **Crafted inputs the scan also missed:**
  - `mock.patch.object(v, attribute="_HIDDEN", new=1)`
  - `monkeypatch.setattr(target="gnd.exp.session_v7._HIDDEN", ...)`
  - `mock.patch.multiple("gnd.exp.session_v7", _HIDDEN=1)`
- **Why it matters:** the guide claims "common module/attribute patches" are covered, and tells readers to use the patch columns as sites to inspect. A migrator would miss a patch that the module really looks up at call time.

**F6: Rows are classified by literal cell text, not by inventory section** (`audit.py:52`, `:59`, `:166`)
- **Phase label:** a legal MC1 row whose identity-control cell is `` `tests/test_z.py::test_alias` `` gets the phase `tests/test_z.py::test_alias` instead of `MC1`.
- **Retirement detection:** a row noting "retired in FU9 … no longer importable" misses the FU5 branch. It would be rendered "retain / first release carrying this notice" with "unavailable" identity, and nothing guards against that.
- **Silently dropped rows:** a row written `|gnd.x.y | …` with no space after the pipe is dropped, and there is no check that the literal row count is 847.
- **Current state:** every existing row is classified correctly today. The generator should read the section headers instead, and refuse "unavailable" rows that have no retirement record.

**F7: The guide's docs links will not work on the published site** (`docs/refactoring-import-migration.md`, `docs/release-notes.md:3`) — found by reading only
- **Links:** the guide links to `../.gnd-planning/...`, but `zensical.toml` sets `docs_dir = "docs"`. No other docs page links into `.gnd-planning`, and link validation is set to `not_found = "warn"`. So the links to the migration table and the FU5 record would be broken on the built site.
- **Nav:** the new page is not in `nav`.
- **Release notes:** the new `## Unreleased` heading sits above the intro paragraph ("Version 0.5.0 … is the latest release"), so that paragraph now appears under Unreleased. The page's own convention is a named `Unreleased:` section after the intro.

## 2. Checked and true
- **Row coverage:** the table has 1,373 rows: 847 literal, 479 RF4 and 47 RF8 imports, matching the spec. Every row has a disposition and a release value.
- **FU5 retirements:** the three FU5 helpers are marked absent / "retired (FU5, #114)" with no replacement. That is consistent with the owner's #114 ruling.
- **Validation wrappers:** the two wrappers are distinct functions that bind `SPEC_RULE_ID` and `CONCLUSIONS_RULE_ID`, so the current text is accurate.
- **Live identity:** all other rows resolve to the same object live.
- **Guide examples:** both examples are real:
  - `tests/test_conformance_payload.py:834` patches `model_file_sha256` on the service module.
  - `tests/test_v71_phase4_successors.py:197` patches `session_runtime`.
- **Matchers that held up:**
  - `bindings` resolves relative imports and aliases correctly.
  - `qualified` correctly follows `import gnd.x.y` and `as` aliases.
  - Positional string `patch(...)` and `patch.object(mod, "x")` / `setattr(mod, "x", v)` are detected.
  - The `new.split()[0]` step correctly strips "(bound …)" and "(same object)".
- **Scope of the scan:** no first-party `.py` outside `src/` and `tests/` imports gnd, so scanning only those two folders loses nothing.
- **Dynamic lookups:** a local alias (`v = gnd.exp.session_v7`) and `getattr(v, "_HIDDEN")` are both missed, as expected. The guide already discloses dynamic lookup and local shadowing.

## 3. Could not check
- **Docs site build:** I didn't run `zensical build`, because it writes a `site/` folder. F7 comes from reading the config.
- **The repo's own `uv run` and the full test suite:** I didn't run either. `uv run` would create a `.venv` in this checkout, which breaks the read-only rule. I used the F6 checkout's venv with this checkout's `src` instead.
- **Third-party usage:** not measurable, as the spec says.

VERDICT: CHANGES_REQUESTED
