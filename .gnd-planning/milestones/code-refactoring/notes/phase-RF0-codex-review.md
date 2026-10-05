# Phase RF0 — single adversarial review (Codex)

**Edited retained evidence.** The reviewer's output below is verbatim except
for one sanitization: absolute paths to the local checkout were replaced with
`<repo>/`, and the final `exit=0` line of the capture was dropped. One
reviewer is one reviewer; this is not a panel.

- Reviewer: `codex exec --ephemeral --ignore-user-config --model gpt-6-sol --config model_reasoning_effort="xhigh" --sandbox read-only`, prompt on stdin, exit 0.
- Reviewed: `git diff 8664d82..HEAD` at `7c6db3c` over the tool, map, tests, RF0 notes and spec.
- Limit stated by the reviewer: pytest could not run in its read-only sandbox (no writable temporary directory). It checked the tests by reading them, and reproduced findings with in-memory inputs.

## Dispositions

Each finding was reproduced by a regression test observed red before its fix
([evidence](../evidence/phase-RF0/review-regressions-red.txt): 9 failed,
4 passed). The four tests that passed pre-fix close coverage gaps rather than
defects.

| Finding | Disposition |
|---|---|
| RF0-01 missing cases (delattr, patch.object, typing.TYPE_CHECKING, --no-renames) | Fixed: `test_r01_*` added. The `typing.TYPE_CHECKING`, lambda and rename cases already passed (coverage gaps); the delattr, patch.object and `mock.patch` cases were red |
| RF0-02 wrongly typed map value raises TypeError | Fixed: layer and lane values are type-checked → exit 3 (`test_r02_*`) |
| RF0-03 missing `--out` parent traceback | Fixed: the parent is checked before measuring, and write `OSError` → exit 3 (`test_r03_*`) |
| RF0-04 uncapped source read; read errors escape | Fixed: 4 MiB per-file read cap; `OSError` → exit 3 naming the file (`test_r04_*`) |
| RF0-05 `foo.TYPE_CHECKING` treated as type-only | Fixed: only `TYPE_CHECKING` and `typing.TYPE_CHECKING` match (`test_r05_r06_*`) |
| RF0-06 dynamic import under TYPE_CHECKING counted as runtime | Fixed: classified `type_only` (`test_r05_r06_*`) |
| RF0-07 private submodule import not recorded | Fixed (`test_r07_*`) |
| RF0-08 alias bindings leak across function scopes | Fixed in the module visitor with a scope stack (`test_r08_*`). Test-file bindings stay file-wide; that inventory resolves patch targets, and module-level imports dominate there |
| RF0-09 keyword-form patches dropped; non-gnd patch omitted | Keyword forms fixed (`test_r01_patch_object_mock_and_delattr`). Omitting patches whose target is bound to a non-`gnd` import (for example `os.sep`) is deliberate: the inventory's scope is `gnd` targets, and unbound targets are still recorded as `resolved: false`. Not changed |
| RF0-10 `--- ` line inside a hunk read as a file header | Fixed: header lines are parsed only between `diff --git` and the first `@@` (`test_r10_*`) |
| RF0-11 A2 "confirmed" by counting a top-level dynamic import | Corrected in place in `rf0-baseline.md`: refuted as worded, 184 |
| RF0-12 "five meanings" overstated | Corrected in place: five sites, three output meanings |
| RF0-13 line count 104,062 vs 104,094 | Corrected in place: 104,094 at `19b131b`. The old value was the pre-merge count |

## Reviewer output (verbatim, paths sanitized)

## Findings

- **RF0-01 — high · blocking — [tests/test_gnd_arch.py:379](<repo>/tests/test_gnd_arch.py:379).** The patch fixture exercises only `monkeypatch.setattr`. Reproduction: `rg -n 'monkeypatch\.delattr|patch\.object|typing\.TYPE_CHECKING|--no-renames' tests/test_gnd_arch.py` finds no cases. Those section 6.1 branches could be broken without failing their claimed tests. **Recommendation:** add cases with exact expected output for each missing form, plus a rename-sensitive compare fixture.

- **RF0-02 — high · blocking — [tools/gnd_arch.py:146](<repo>/tools/gnd_arch.py:146).** A valid JSON map with `"modules":{"gnd":{"layer":[]}}` raises `TypeError` and exits 1 with a traceback. I reproduced this by piping a copy of the real map with that one value changed into `measure --layers /dev/stdin`. **Recommendation:** type-check `layer` before set membership and convert malformed map values to exit 3.

- **RF0-03 — high · blocking — [tools/gnd_arch.py:775](<repo>/tools/gnd_arch.py:775).** `python3 tools/gnd_arch.py measure --out /tmp/rf0-nonexistent-parent-1/out.json` exits 1 with a `FileNotFoundError` traceback after measurement. **Recommendation:** handle output-path `OSError` under the documented exit contract.

- **RF0-04 — medium · hardening — [tools/gnd_arch.py:200](<repo>/tools/gnd_arch.py:200).** Source reads have no cap, and read errors escape `_parse`. An in-memory `Path.read_bytes` mock returning 1.6 MiB was fully parsed; `_parse(Path("."), "src/gnd/nonexistent.py")` raised `FileNotFoundError`. **Recommendation:** bound reads before parsing and report source I/O failures as exit 3 with the path.

- **RF0-05 — high · blocking — [tools/gnd_arch.py:223](<repo>/tools/gnd_arch.py:223).** Input `if foo.TYPE_CHECKING: import gnd.b` produces a `type_only` edge, although section 6.1 names only `TYPE_CHECKING` and `typing.TYPE_CHECKING`. **Recommendation:** match the specified expressions precisely and test both.

- **RF0-06 — high · blocking — [tools/gnd_arch.py:335](<repo>/tools/gnd_arch.py:335).** Input `if TYPE_CHECKING: importlib.import_module("gnd.a")` produces a runtime `dynamic` edge. With `gnd.a → gnd.b`, it falsely closes a runtime SCC. **Recommendation:** retain the type-only guard for literal dynamic imports.

- **RF0-07 — medium · blocking — [tools/gnd_arch.py:287](<repo>/tools/gnd_arch.py:287).** With module `gnd.pkg._hidden` present, `from gnd.pkg import _hidden` adds an edge but no private-import record: the submodule branch continues before checking the private name. **Recommendation:** record the private import on that branch and add a fixture.

- **RF0-08 — medium · hardening — [tools/gnd_arch.py:239](<repo>/tools/gnd_arch.py:239).** Alias bindings leak across scopes. For `import gnd.a as m; def f(): import gnd.b as m; m._inside; m._outside` with the last access outside `f`, the tool attributes *both* private accesses to `gnd.b`; the outer access is to `gnd.a`. **Recommendation:** keep bindings per lexical scope.

- **RF0-09 — high · blocking — [tools/gnd_arch.py:483](<repo>/tools/gnd_arch.py:483).** `monkeypatch.setattr(target="gnd.cli._x", value=1)` produces no patch row, including no `resolved: false` row. The committed fixture’s `monkeypatch.setattr(os, "sep", "/")` is likewise silently omitted. **Recommendation:** accept keyword arguments and record every recognized patch call, marking unresolved targets explicitly.

- **RF0-10 — high · blocking — [tools/gnd_arch.py:725](<repo>/tools/gnd_arch.py:725).** The diff parser mistakes a removed valid Python line `-- important`—represented as `--- important`—for a file header. Feeding that diff followed by `-other` attributes the removal to path `portant` instead of `src/gnd/a.py`. **Recommendation:** parse file headers only in diff-header state, then parse additions and removals inside hunks.

- **RF0-11 — medium · completeness — [rf0-baseline.md:29](<repo>/.gnd-planning/milestones/code-refactoring/notes/rf0-baseline.md:29).** A2 is marked “confirmed” by adding the one dynamic pair to 184 function-only lazy pairs. The dynamic `__import__` at `semantic_spec.py:1613` is a **top-level** assignment, so it cannot confirm “185 imports that occur only inside functions.” **Recommendation:** mark A2 refuted under that wording and report the categories separately.

- **RF0-12 — medium · completeness — [rf0-baseline.md:39](<repo>/.gnd-planning/milestones/code-refactoring/notes/rf0-baseline.md:39).** A12 turns five differently hashed *sites* into “five meanings.” `transition.model_digest` explicitly wraps `population._model_digest`, and `synth.provenance.model_digest` delegates to it. **Recommendation:** distinguish site count, implementation variants, and semantic meanings before setting RF2’s scope.

- **RF0-13 — low · completeness — [rf0-baseline.md:18](<repo>/.gnd-planning/milestones/code-refactoring/notes/rf0-baseline.md:18).** The note says 104,062 lines, while the committed metric JSON and a fresh read-only measurement both say **104,094**. **Recommendation:** correct the note or document a different counting method and source.

## Checked and found true

- Two read-only `measure` calls produced identical canonical JSON bytes (355,625 bytes), matching the committed metric JSON. This supports claim 3 for the current tree and interpreter.
- The layer map has exactly one entry for each of the 148 discovered modules. The note’s 15 AST-identical groups match the current measured groups.
- For A3, removing the single dynamic edge at `semantic_spec.py:1613` reduces the core SCC from 14 modules to 13. A13’s first version assignment is captured as `V2_SESSION_CONTRACT_VERSION`. For A16, `agent_cli` has ten measured importers and no outgoing `gnd` edge. These checks do not validate every baseline statement.
- A normal in-memory compare sample matched duplicate lines as a multiset and ignored blank lines; the command includes `--no-renames`. RF0-10 shows the parser can still misattribute.
- Code inspection confirms the ordinary order of usage parsing, existing `--out`, map, then sources. RF0-02 and RF0-03 refute the claimed total exit behavior.
- `git diff --quiet 19b131b..HEAD -- src/gnd .gnd-planning/milestones/public-launch` returned 0.

No files were modified and no network commands were run. The pytest suite **could not run**: pytest failed before tests began because this read-only sandbox has no writable temporary directory. Read-only collection found 33 tests; the reproductions above used in-memory inputs or paths that could not create output.
