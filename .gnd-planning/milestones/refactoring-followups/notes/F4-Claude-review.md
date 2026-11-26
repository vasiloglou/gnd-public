I'm requesting changes. In short: both readers now refuse YAML deeper than 64 collections before building anything, error classes and exit codes are unchanged, and the review writer refuses NaN and both infinities. Historical error precedence is only partly kept: in some inputs a different message now wins. Every SHA-256 in the brief matched, so I read the bytes the brief names.

## 1. Findings

**F1 (low): the depth refusal can now take the place of the historical alias, event-budget or syntax message** — `src/gnd/model/_parsing.py:174`, `src/gnd/population.py:452`

- **What's wrong:** the depth check raises at the first collection past 64, in the middle of the same pass that checks aliases, the event budget and syntax. So if a too-deep collection comes before an alias, an event-budget overrun or a syntax error, the depth message wins. The old reader reported the alias, event or syntax error for those same bytes. The spec says to "Preserve each existing … alias/event diagnostic."
- **What someone would see:** I compared the current code with a run where I replaced the depth check by a no-op in that process only:

| Input | Current result | Without the depth check |
|---|---|---|
| `- [[…65…0…]]\n- &a 1\n- *a\n` (model) | `ModelLoadError: YAML depth cap exceeded` | `ModelLoadError: model YAML alias/event guard refused input` |
| same input (population) | `PopulationLoadError: YAML depth cap exceeded` | `PopulationLoadError: YAML document 's.yaml' uses an anchor/alias ('*a') …` |
| `- [[…65…]]\n- [unclosed\n` | `ModelLoadError` / `PopulationLoadError`: depth | raw `ruamel ParserError` from both readers |
| 65-deep prefix, then more than `MAX_YAML_EVENTS` events | depth | event-budget refusal |

- **What doesn't change:** the CLI exit code. `gnd validate` and `gnd check` exit 3 both ways (I ran it). When the alias comes first, the alias message still wins.
- **Fix:** record the first depth crossing during the pass and raise it after the loop. That keeps a single pass and still refuses before anything is built.
- **To reproduce:** `/tmp/f4probe.py` and `/tmp/f4probe2.py`.

**F2 (low): the population depth message doesn't name the file** — `src/gnd/population.py:452`, `src/gnd/input_policy.py:135`

- **What's wrong:** the wording `"YAML depth cap exceeded"` is fixed inside `checked_yaml_depth`. The neighbouring population messages name the file (`YAML document '{source}' …`), but this one can't. The spec says "the reader owns its error wording"; the helper only lets the reader choose the error class.
- **What someone would see:** `gnd check MODEL deep.pop.yaml` prints `ERROR: YAML depth cap exceeded` with no file name. The alias refusal for the same input names the file.

**F3 (low, test support): one golden is special-cased by its literal key** — `tests/support/rf7_pins.py:20-29`

- **What's wrong:** this is the "branch on one literal name" the standing check describes. Every other RF7 golden change is a row in `tests/fixtures/rf7-restrictions/successors.json`, with a reason, the changes, and before/after paths and hashes. This branch bypasses that table, and the table (19 rows) doesn't mention the F4 change.
- **Also:** the NaN and infinity expectations are computed by calling `json.dumps(value, allow_nan=False)` again. That is the same stdlib call the code under test makes, so it can't fail; it doesn't pin any bytes.
- The finite answers stay bound to the original golden through its hash. That part is sound.
- **Fix:** add a successor row, with per-minor `after` files if the message differs between Python versions.

**F4 (outside the stated scope; shown only at function level): the writer can still emit text that isn't valid UTF-8 JSON**

- **What's wrong:** `_canonical_payload({'run_directory': '/tmp/a\udcffb'})` returns `'{"run_directory":"/tmp/a\udcffb"}'`. That string raises `UnicodeEncodeError: surrogates not allowed` when encoded as UTF-8, so the output isn't strict JSON.
- **Where it can matter:** `review/service.py:173` puts `str(output_directory)` into the payload. On Linux, a directory name that isn't valid UTF-8 would carry such a character.
- I didn't run the CLI on Linux. On macOS such a directory can't be created.

## 2. What I checked and found true

- **Depth policy:** both readers apply `input_policy.MAX_DEPTH` (64) in their existing single event pass. 64 levels pass the guard and reach the schema validator. 65 and 1000 levels are refused quickly with the readers' own error classes. Checked with flow sequences, block mappings, flow mappings and a CRLF file with a block scalar.
- **No double counting:** in multi-document streams the depth resets per document. The 40/40 case still gets the historical `ComposerError`.
- **Kept as before:** the error classes, the exit codes (3), the alias message when the alias comes first, the model's block-scalar handling and its JSON fallback.
- **JSON-looking input:** a model whose text starts with `{` is still refused by the JSON reader's existing depth check (`model JSON input refused`). That is the historical behaviour.
- **Writer:** `allow_nan=False` refuses `nan`, `inf` and `-inf` nested in containers. The finite output (Unicode, separators, key order) matches the RF1 golden. The three payloads in `review/service.py` contain no floats.
- **Tests:** `tests/test_refactoring_input_boundaries.py`, `tests/test_rf1_helper_pins.py` and the related input-policy, RF7 and review tests ran: 486 passed, 55 deselected.
- **Standing check, matchers tried:**
  - `checked_yaml_depth`: an event-type counter, not a pattern over text. Tried with block, flow, multi-document and CRLF input; no defect.
  - The literal-key branch in `rf7_pins`: reported as F3.
  - The pre-existing JSON character-level depth scan used by the model's `{` fallback (not part of this diff): `{version: '[[[…70']}` is legal YAML only one level deep, but it is refused as `model JSON input refused`. The scan counts brackets inside a single-quoted YAML string. It predates F4; I note it for #302.

## 3. What I couldn't check

- The end-to-end failure in F4 needs a Linux filesystem that allows file names that aren't valid UTF-8; I only showed it at function level.
- The new tests only use timing and the error message to show the refusal happens before construction. Nothing spies on node construction.
- I didn't run the full default test suite, only the affected tests listed above.

I didn't touch the repository. I did write scratch files outside it (`/tmp/f4probe*.py`, `/tmp/f4cli/`) and, because this session is in plan mode, a short summary at `~/.claude/plans/review-brief-a-giggly-newt.md`.

VERDICT: CHANGES_REQUESTED
