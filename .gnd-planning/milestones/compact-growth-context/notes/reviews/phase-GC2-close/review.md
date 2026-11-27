## Review of e831b9dc → working tree at 54c8a28cd6bc

All four files match the SHA-256 values in the brief. I changed nothing. My runs used an existing installed environment at `/private/tmp/gnd295-close-replay/env` with bytecode writing turned off, and `git status` was the same before and after.

**Short answer:** C1 holds for the shipped fixture. The retained replay reproduces the 497-byte view, the 229 parity pairs and the 8 commands. It cannot reproduce the wheel digest recorded in `003-phase-GC2.md`, and it would fail on the wheel that digest names.

### Findings

**F1. The committed replay does not reproduce the measurements as recorded** (`003-phase-GC2.md:24-49`; `evidence/verify_install.py:46` and `:42-57`)

- The record lists `Wheel SHA-256: 1f388ac0…`, the README at `f28c4618…` and the test at `7e42b22b…`. Those are the bytes of e831b9dc, not of this change. The diff does not update the record.
- The output that matches the record line for line, wheel digest included, came from a different, uncommitted script: `/private/tmp/gnd295-final-accept/verify.py`. Its result is in `/private/tmp/gnd295-final-accept/result.txt`.
- The committed `verify_install.py` prints different lines and never prints or computes a wheel digest. It also does not hold the build-and-install steps; the gate entry is only the prose "uv build --offline --wheel followed by clean wheel install".
- Run against the wheel the record names, the committed script would raise `KeyError` at line 46. That wheel's packaged README has no `reversed_binding_supported` key: `unzip -p /private/tmp/gnd295-final-accept/wheels/*.whl gnd/examples/seeded_growth/README.md | grep -c reversed_binding_supported` prints 0.
- The script's output does exist, in `/private/tmp/gnd295-close-replay/result.txt`, from wheel `d3525ac1…`, which packages the current README. That digest is not recorded anywhere in the milestone.
- A wheel built from HEAD cannot match `1f388ac0…`, because the README is packaged and has changed.
- **Consequence:** the record certifies a wheel digest and README/test hashes for older bytes than the shipped ones. No command in the repository reproduces that digest.

**F2. `supports_binding` breaks on legal readings** (`src/gnd/examples/seeded_growth/README.md:80-83`)

This is the standing check on code fitted to its examples. The function substitutes values with `str.format_map`, keyed by the object type's exact `name`. The model's own placeholder rule (`src/gnd/model/_validation.py:485-532`) is positional: a label can be the object-type id or its name, matched after casefolding and keeping only letters and digits, with an optional `:qualifier`.

I changed the seed reading in memory, confirmed `semantic_validate` reports no errors, and ran the README function on each variant:

| Reading | Result |
|---|---|
| `{WorkKey} has version {VersionId}` (shipped) | forward True, reversed False ✔ |
| `{work} has version {version}` | `KeyError: 'work'` |
| `{workkey} has version {versionid}` | `KeyError: 'workkey'` |
| `{WorkKey:work} has version {VersionId:version}` | `ValueError: Invalid format specifier 'work'` |
| `{Work Key} has version {VersionId}` | `KeyError: 'Work Key'` |

Expected for each: forward True, reversed False.

A fact type whose two roles are played by the same object type also fails. For `{Person} manages {Person}` the two placeholders collapse to one key: the forward binding renders "P-2 manages P-2" and the reversed binding renders "P-1 manages P-1". Neither direction can match the source, so the function cannot tell them apart. I ran this on a hand-built view with no model, since the format logic is the whole question.

- **Consequence:** a host that copies this packaged guide to its own valid model gets an exception instead of a decision. The comment at lines 77-78 narrows the claim to "this passage", so this does not falsify C1.
- `verbalize_population._sentence` already does this positional substitution. It quotes values and adds a period, so it is not a drop-in replacement, but its substitution logic is the one that matches the grammar.

**F3 (style). The verifier's guide parsing has no breaking input in the current README** (`verify_install.py:44`, `:50-55`)

The splits on `` ```python\n `` and `` ```bash\n ``, plus the `startswith("gnd ")` check, would miss fences with other spacing, CRLF line endings or backslash continuations. The test at `tests/test_growth_view.py:55` uses the same split. The README is the project's own file, so I found no input that breaks it today.

### What I checked and found true

- **C1 holds.** The forward reading formats to exactly the document span. "W-1 has version V-1" occurs once in the NFC-normalised `round-2.document.txt`. The reversed binding formats to "V-1 has version W-1", which does not match.
- The check depends on the model's role direction. If the seed's reading were inverted, `assert supports_binding(bindings)` would fail.
- I ran the README's Python block read-only against the source example with the installed environment. It printed `reversed_binding_supported: False`, bindings `{'work': 'W-1', 'version': 'V-1'}` and `inspected_ids: ['work_has_version']`.
- The test sees a regression either way. If `supports_binding` always returned True, the README's `assert not …` and the test's `is False` would both fail; if it always returned False, the forward assert would fail. Nothing in C1 requires a general search of the source.
- The new test lines also check that the root file is unchanged by the run, and that the direct-lookup row's reading and roles equal the loaded model's.
- `verify_fixture_parity()` from the committed script, run on the installed wheel, printed "Path and loaded-model pairs with identical bytes: 229".
- The growth view of `root.orm.yaml` is 497 bytes with SHA-256 `b3be4910…`, matching the replay's result file.

### What I could not check

- I did not build or install a fresh wheel and did not run `verify_installed_example()`, which copies files and runs the apply commands. That kept the review read-only; the 8-command count rests on the retained `gnd295-close-replay/result.txt`.
- I did not run pytest, because it writes temporary files.

VERDICT: CHANGES_REQUESTED
