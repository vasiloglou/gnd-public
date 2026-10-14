Retained one independent Claude Code initial review. No operator paths appeared; prose unchanged. Raw SHA-256 95965d12072cff81110187cb7ab76e56ac0ae9872d58997882a67220da856a7b. Read-only commands and changing-tree reading limits are disclosed below.

# PA5 independent diff review: initial pass

I couldn't refute PA5's central claims, but there are several gaps in what is user-visible and in how claims are bound to sources. One of these blocks acceptance: the new chapters, their alt text and the SVG labels drop the space between words and numbers ("costs800", "Submitted3"). The earlier chapters don't do this, and it shows on the rendered mobile page.

**Reading bounds.** I only read and searched. I ran no Python, tests, native tools or providers. I didn't open `.env`, credentials or `.agents/skills/`, and I edited nothing. Plan mode had no write tool, so there is no plan file; this message is the whole review. I used `jq`, `shasum`, `perl` and `cmp` read-only.

The producer was changing files while I read. New checkpoints and manifest changes appeared at 18:13:46, chapters changed at 18:12:38, and screenshots at 18:14:29. My findings refer to the bytes I hashed at about 18:14:

| File | sha256 (prefix) |
|---|---|
| `07-native.md` | `2d0b53bd` |
| `04-native.md` | `ff983947` |
| `run_tutorials.py` | `f112384b` |
| BookRec `sources.json` | `b4532c6a` |
| Expense `sources.json` | `890ff0dc` |

I first saw the BookRec scroll regions with no keyboard markup; that was fixed during my read (it now has `role="region" tabindex="0"`).

## Checked claims

**Confirmed:**
- **Native runs:** 52 BookRec and 33 Expense blocks passed, all with status `passed`. The four native blocks' `code_sha256` values in the receipts match the current chapter blocks, which I re-hashed with perl. So the code hasn't changed since the 18:09 run.
- **Offline runs:** 50 passed plus 2 skipped, and 31 passed plus 2 skipped. Skipped rows have no `elapsed_seconds`, and the transcript prints "Native lanes not executed: pyrel".
- **Receipts on failure:** they are written only after a completed run. A failing block raises before the write, and its row says `failed`.
- **SVG copies:** all six packaged SVGs are byte-identical to the docs copies, and the two `*-native-query.txt` files are byte-identical to the shipped `native_query.py` files. SVGs total about 14 KiB.
- **Checkpoints:** the 4 BookRec and 7 Expense checkpoints are byte-identical to the PA3 and PA4 final receipts. The 3 new BookRec refusal inputs match the PA2 native corpus population hashes, and the corpus model hashes match the current models.
- **Rule thresholds:** meals 75, training 1500, travel 2000, equipment 3000, team-lead 100 and finance 3000 all match the models. The IDs `age_appropriate`, `unread_only`, `preferred_genre`, `all_eligible`, `required_expense_has_currency` and `supported_currency` all exist.
- **Arithmetic:** 60 + 800 + 1400 = 2260. The checkpoint witnesses `{$a:800,$e:102}`, `[[101],[102]]` and `{$a:90,$e:101}` match.
- **Unchanged areas:** the tracked diff touches only docs, tests, the runner, the CSS and `zensical.toml`. No policy, compiler, runtime, model or corpus bytes changed.
- **Red controls:** 9 failed before implementation in `experience-red.txt`, and commit bcf9126 is ordered before the implementation.
- **Exit codes:** the CLIs return 2 and 3, and `native_query` returns 70, matching the troubleshooting text.
- **Expense CLI copy:** the copied `cli/` layout matches `from cli.reporting import` and the `__file__`-relative `native_query.py`.
- **Snippets:** `pymdownx.snippets` has `check_paths = true`.
- **Budgets:** runner +28 lines (limit 80), test file 105 lines, chapters 153 and 159 lines (limit 220), SVGs under 100 KiB.

**Not verifiable from what's retained:**
- That the runs used *separate* interpreters. Neither receipt nor transcript records interpreter paths, versions or the command line.
- What the "34 direct" check ran. `experience-green.txt` has no command.
- The strict site build and link evidence. `site-build.txt` doesn't record which bytes were built.

## Findings

**High**
1. **Numbers glued to words** in prose, alt text and SVG labels. Examples:
   - `docs/expense/04-native.md:3`: "Expense102 costs800 EUR … permits2000 EUR … only100"
   - `docs/bookrec/07-native.md:6,19,142`: "chapter6", "PyRel1.30.1", "Exit2", "SDK0"
   - the SVGs: "Submitted3", "Total2260 EUR", "Only103 → EUR;101/102", "Repair:102", "PASS:800 ≤2000"

   Chapters 01–06 have none of these. It's visible in `render/expense-mobile-default-top-final.png`, and screen readers will read "costs800" as one token.

**Medium**

2. **Some figure claims aren't bound to their sources.** `verify_graphic` (`tests/test_pyrel_tutorial_experience.py:16-37`) only checks that a label substring appears somewhere in the SVG. It doesn't check the label against a value in a source file.
   - The currency graphic is bound to `model.orm.json`, not `currency.orm.json`. So "supported_currency permits EUR only" isn't guarded, even though the checkpoint's `source_binding.model_sha256` (`ae75…`) could be compared against it.
   - The BookRec evolution graphic doesn't bind `strict.orm.yaml` or `complete.orm.yaml`.
   - These figure claims have no checkpoint and no executed block behind them: "USD also hits the EUR-only application guard" (`currency.svg`), "Ben → night is preserved" (`evolution.svg`), and the advisory/strict "cosmos, map" table rows (`07-native.md:92-93`).
   - Short labels like "75" or "3000" can match unrelated text.
3. **Rejection witnesses aren't asserted in the executed blocks.** C1 asks for named rejection witnesses, but only the rule's status is checked for:
   - Expense team-lead rejection (`04-native.md:80-81`): `{$a:800,$e:102}` isn't asserted.
   - BookRec `unread_only` mutation (`07-native.md:125`): `{$u:ada,$b:read}` isn't asserted.
4. **Receipts can go stale and aren't tied to a run** (`tools/run_tutorials.py:155-158`).
   - A failed run leaves any earlier passing receipt at the same path untouched.
   - The write isn't atomic, and nothing records interpreter paths, the PyRel interpreter, git HEAD/dirty state or the group.
   - The page basename alone is ambiguous: `scenario.md` appears in four groups.
   - A bad `--receipt` parent directory only fails after the whole native run, not at argparse time as the spec's totality rule wants.
5. **Weak interpreter control.** `test_native_block_receives_explicit_base_python` (`tests/test_pyrel_tutorial_experience.py:58-65`) only checks that the variable is non-empty. It doesn't check that it equals the base `--python`, or that the PyRel block ran under `GND_TUTORIAL_PYREL_PYTHON`. The runner silently falls back to the base interpreter (`run_tutorials.py:41,90`).
6. **Mobile evidence gap.** The `expense-1-mobile-*-right.png` frames are scrolled only about 24 px, so the cap numbers (75/1500/2000/3000) never appear in any retained mobile frame. Also, `expense-1-mobile-default.png` from 18:11 shows page text showing through over the diagram. The producer should re-check this.

**Low**

7. **Minimum width differs from the spec.** The CSS sets `min-width: 560px` (`docs/assets/styles.css:53`), but the spec says 480px. Either change one or record the decision.
8. **Duplicate region names.** All three regions per page have the same `aria-label` ("Scrollable bookrec diagram"). Use names specific to each figure.
9. **Eligibility SVG gaps.**
   - The plan asks for a reader/book/genre example, but no genre labels appear in the SVG.
   - The "Solid arrows" legend has nothing to contrast with.
   - Ben/read (already rated) isn't shown.
10. **Missing red-first record.** The two snippet-equality tests were added after bcf9126 and have no red record. The mobile control does have one.
11. **Refusal inputs aren't pinned.** The three `*-refusal.input.json` files are packaged but not hash-pinned in the manifest. Their PA2 traceability currently depends on hashes I found in PA2 `native-final.json`.

## Branch coverage

The runner branches reviewed are: selected, skipped, preflight, failed exit, timeout (raises with no row, so no false success), receipt present or absent, and the default offline lane. The default `run_pages` behaviour is unchanged except for the added environment variable and hashing.

I found no false native acceptance and no invented successful check. Every success shown in a figure traces to an executed block or a byte-identical checkpoint. The exceptions are the unbound claims in finding 2.

## Refactoring suggestions
- **Smaller manifests:** remove the full `path: []` copies of the model and seed from `sources.json`. They make the manifests about 104 KiB, which is more than all the SVGs combined, and the sha256 already pins those files.
- **Value-level checks:** have each manifest row tie a numeric SVG label to a JSON path in the model or checkpoint.
- **Source-binding check:** compare each checkpoint's `source_binding` hashes with the shipped model and population it claims to bind.
- **Safer receipt writes:** unlink the receipt path at startup, check the path early, then write atomically to a temp file and rename. Add `group` and interpreter identities to each row.

Not reviewed, as scoped: the wheel and full 137-case run, the four close reviewers, and any broad replay or publishing. The repair pass has not been used.
