# Reproduce the compact-growth close measurements

Run from the repository root, using Python 3.14 and the locked uv environment. The final example and replay were introduced at 54c8a28c and finalized at 1dc3c77a. The underlying package code is the implementation accepted at 21b7286f.

```bash
scratch=$(mktemp -d)
uv build --wheel --out-dir "$scratch/wheels"
uv venv "$scratch/env"
shasum -a 256 "$scratch"/wheels/*.whl
uv pip install --python "$scratch/env/bin/python" "$scratch"/wheels/*.whl
"$scratch/env/bin/python" .gnd-planning/milestones/compact-growth-context/evidence/verify_install.py
uv run pytest -q tests/test_growth_view.py tests/test_rf1_cli_pins.py tests/test_disclosure_mode.py::test_t38_parity_holds_with_an_ambient_variable --tb=short
```

The retained wheel check builds in the source tree, then imports the installed package with the isolated interpreter. It enumerates the valid *.orm.yaml fixtures under tests/fixtures, compares each path with its loaded Model, executes the packaged example on a fresh copy, and verifies all eight documented CLI commands. The replay emitted:

```text
Path and loaded-model pairs with identical bytes: 229
Installed CLI/API bytes: 497. SHA-256: b3be4910c0e937e8db09eba4d7f1f5727b1439e957930e3ac3b57da23fbf6b23
Packaged commands passed: 8. Direct, retry, defer and reversal verified.
142 passed in 3.00s
```

The measured wheel SHA-256 was 0c86af1e4334f0a04102f5819612578646645b2462b9fcfdc8e758003c78cde6. This is the final packaged artifact. The earlier GC2 record retains its historical wheel identity and its pre-close example. The CLI and Python reference pages are docs/reference/cli.md and docs/reference/python-api.md. The phase records and review run files bind each reviewed file and reviewer output to its digest. The CLI test module explicitly includes the grammar tree, help and exit probes.

## Close panel dispositions

The repeated concerns about replayability and reversed binding are fixed across 54c8a28c and 1dc3c77a. The example checks both named assignments against the agent-attributed source spans and records which direction the text supports. The test resolves the direct hit against the loaded fact and checks that the root bytes remain identical across the ambiguous deferral.

The declared coordinate convention is in the ORM representation guide: the document digest covers raw bytes, while offsets count code points after NFC normalization of strict UTF-8. The example follows that convention. The two representations are deliberately different. The evidence-only edit is exercised in test_cli_utf8_include_identity_and_stale_snapshot, which preserves the view after changing raw root bytes and refuses a mismatched included file.

The growth guide defines guarded signatures as participating atom locations, fact IDs and role names. It directs the host to the full model for variable bindings, operators and complete rule meaning. Using these search signatures to decide rule equivalence would exceed their contract.

The projection test compares all represented family names with the live registry. An isolated negative control inserted an unrepresented family into that dictionary and ran test_full_inventory_and_size. It failed at the registry equality assertion as expected. The registry and repository files remained unchanged after the process exited.
