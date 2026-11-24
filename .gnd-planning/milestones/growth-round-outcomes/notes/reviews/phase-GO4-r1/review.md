All five SHA-256 values match the brief.

1. **F1 — Guard accepts reversed or deleted rules.** `tests/test_unattended_growth_guidance.py:337–343` checks fragments rather than the complete obligations. In-memory reproductions returned `[]` for each of these edits:
   - Replace `are an `open_questions` entry:` with `are not an `open_questions` entry:`.
   - Remove both id-only instructions.
   - Remove every `its own or included` qualification.
   - Replace `Rows for a new fact type only` with `Rows for any fact type`.

   Expected: a reported problem. Consequence: materially weakened or contradictory guidance passes T1. C2 is false.

2. **F2 — Markdown matchers mistake hidden text for rules and reject equivalent formatting.** `tests/test_unattended_growth_guidance.py:313–345` parses Markdown using exact lines and string splits. Executed reproductions:
   - Wrap each element/rows table line in `<!--\n…\n-->`: `_reply_rule_problems` returns `[]`, although both rules disappear from the rendered table.
   - Remove padding after the opening table pipes: it reports both rules missing.
   - Change the heading to `## The reply shape ##`: `_section` raises `ValueError`.
   - Use a `~~~json` fence: the example split raises `IndexError`.
   - Reflow the “never repeated” sentence onto one line: it reports the rule missing.

   These are legal Markdown inputs. Consequences include both missed removals and failures on equivalent formatting. This is an observable C5 failure.

3. **F3 — The page still gives conflicting instructions for reused facts.** `src/gnd/skills/gnd-model-from-text/references/unattended-growth.md:321` routes existing-type rows to `open_questions`, but lines 66–67 instruct the host to drop a matching added fact type and “write its facts against the existing one.”

   Reproduction: reuse the packaged model’s empty `order_arrives_via_channel` and write one sample row, `{"order":10,"channel":"web"}`, against it. The actual policy diff function returns `changed outside the admitted keys: sample_population`; the enclosing policy classifies this as `fact_types.modify`. Following that earlier instruction can therefore sink the round. Align the shape-match instruction with the new rows rule.

What I checked and found true:

- The current reply-shape prose explicitly covers owned and included elements, forbids repetition in the two named collections, and shows an existing constraint host.
- All six committed T2 cases behave as asserted; their coverage is insufficient.
- Both rounds of both packaged examples use fresh ids for element additions, including against the reviewed seed. Existing non-constraint element fields and include pins stay unchanged. Constraint additions use separate locators.
- C4 matches the contract and policy: adding, appending or replacing sample rows is refused. Identical-row control produces no diff refusal.

I could not run pytest or complete GND validation: this interpreter lacks pytest and the project dependencies, and the workspace is read-only. I executed the actual guard and policy helper functions through AST extraction in memory, and inspected examples using JSON/YAML parsers. No files were changed.

VERDICT: CHANGES_REQUESTED