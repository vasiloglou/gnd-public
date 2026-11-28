**Verdict: changes requested.** Discovery can do every bad thing the brief asks about. It leaks sample values, misreports when its pair budget runs out, misses or invents signals on legal models, and crashes on a malformed model. All 18 SHA-256 values match the brief. The new tests pass (7 passed), but none of them covers these inputs. Nothing in the repository was changed; the only file I wrote is the plan-mode notes file outside it.

## 1. Findings

**F1 — `src/gnd/commands/discover.py:289-299`: a malformed model gives a raw traceback.**
- **What's wrong:** `_cmd_candidates` catches only `FileNotFoundError`, `OSError` and `ModelValidationError`. YAML that won't parse, or input refused by the YAML guard, escapes as an uncaught exception.
- **Consequence:** `gnd consolidate candidates pyproject.toml` prints a `ruamel.yaml.parser.ParserError` traceback and exits 1, and `README.md` raises an uncaught `ModelLoadError`. On the same file, `gnd verbalize model` prints `ERROR: expected '<document start>'…`. This breaks the spec's rule that "invalid models follow the normal CLI conventions."
- **Reproduce:** `python -I -c "import sys; from gnd.cli import main; sys.exit(main(['consolidate','candidates','pyproject.toml']))"`

**F2 — `src/gnd/evolve/candidates.py:151, 157`: the output reveals sample values.**
- **What's wrong:** each sample row's evidence carries `row_sha256`, a plain, unsalted SHA-256 of the canonical row. The command is registered as `value-free` (`src/gnd/disclosure.py:109`, `docs/reference/disclosure.md`), and nothing else in `src/gnd` emits a row digest.
- **Consequence:** on the test corpus, trying every `{"order": o, "customer": c}` with o and c from 0 to 999 matched both emitted digests within seconds. It recovered the full sample rows (10, 1) and (11, 1). Short, low-entropy sample rows can therefore be read back from a surface that promises to emit no population values.

**F3 — `src/gnd/evolve/candidates.py:167-173`: the pair budget is charged once per shared trigram, not once per comparison.**
- **What's wrong:** `charge("pairs")` runs before the `compared` de-duplication check. A pair that shares k trigrams is charged k times.
- **Consequence:** I used a model with only two value types, `CustomerShippingAddressLine` and `CustomerShippingAddressLane`. It reports `work.pairs = 22` for one distinct comparison. With `max_pairs=1` it returns `complete: false, reason: "pairs-limit"`, yet the only near-name group is already in the output. So the reported work and stop reason are wrong, and the 25,000 default runs out far sooner than the number of comparisons implies.

**F4 — `src/gnd/evolve/candidates.py:127`: explicit unit information is never read.**
- **What's wrong:** the spec says to group "using explicit unit information where present". The schema provides `reference: {mode: unit-based, unit, measure_type}`, but the unit signal only runs for `kind == "value"` and only looks at lexical name tokens.
- **Consequence:** value types `LatencyMs` and `LatencySeconds` form a `unit` group. The same two declared as unit-based entities with `unit: ms` and `unit: s` form no group.

**F5 — `src/gnd/evolve/candidates.py:63`: readings are not Unicode-normalized.**
- **What's wrong:** `_reading_shape` only casefolds and collapses whitespace, even though `_tokens` NFC-normalizes names.
- **Consequence:** I used two facts on Customer whose readings, `"{Customer} is listed in the café"`, differ only between the NFC and NFD forms of "é". They are grouped under `role-players` and `near-name` but not under `reading-shape`.

**F6 — `src/gnd/evolve/candidates.py:20-28`: the tokenizer and unit list are fitted to the fixtures.**
- **What's wrong:** a camel-case boundary is placed only between a lowercase letter and an uppercase one, and `_UNITS` includes the single letters `s`, `m` and `g`.
- **Consequences:**
  - `TTLSeconds` and `TTLMinutes` each come out as a single token (`ttlseconds`), so no `unit` group forms. The same applies to `Latency2Ms` (`latency2ms`).
  - Clothing sizes `ShirtSizeS` and `ShirtSizeM` are grouped as `unit`. That is the "arbitrary shared suffix" the spec forbids.

**F7 — `src/gnd/evolve/candidates.py:119-120` (from reading only): the singleton count ignores samples in included facts.**
- **What's wrong:** included elements hit `continue` before the sample loop, so their rows never add to `observed`.
- **Consequence:** an entity owned by the root model, with a second instance only in an included fact's samples, would still be reported as a `singleton`. This conflicts with "include-owned definitions may supply context."
- **Not run:** this needs include files on disk.

## 2. What I checked and found true
- Placeholders in a reading are substituted by position. This is safe because `_rule_reading_placeholders` (`_validation.py:485`) requires placeholders to match roles in order and in number, so `next(slots)` cannot run out.
- `role_player_signature` is the existing helper that ignores role order. The `reading-shape` signal keeps role position.
- `located()`: the 64-character hex check is a full-grammar check for a flat token (fine). `type(...) is int` rejects `bool`, and empty or reversed spans (`start >= end`) are dropped.
- Group IDs and evidence digests are the same after reversing declarations, as the test shows.
- The item budget is charged before the work it covers (in `emit`, the sample rows and the n-grams).
- Included object types don't appear as group members.
- The `compared` set stays bounded by `max_pairs`.

**Matchers I tried, and the inputs:**

| Matcher | Inputs |
|---|---|
| `_tokens` | `TTLSeconds`, `Latency2Ms`, `HTTPTimeoutMs`, `ShirtSizeS`, `ÉtéMs` |
| `_UNITS` | `ShirtSizeS` / `ShirtSizeM` |
| the 3-character n-gram slice | two long near-identical names |
| `_reading_shape` | NFC vs NFD readings |
| the `count` marker | read only; `CountOfOrders` gives the frame `count of {}` (fine) |

## 3. What I couldn't check
- **F7 and include handling in general:** they need an include tree on disk, and I stayed read-only.
- **Composite-reference entities:** I didn't test whether `identity_key` distinguishes or merges dict-valued sample cells, because I couldn't confirm the population format for them.
- **Large models:** the reporter's two large models aren't in the repository, so I couldn't measure the default budgets on them.
- **Repository guards:** I didn't run the layer, dynamic-query or component guards.

VERDICT: CHANGES_REQUESTED
