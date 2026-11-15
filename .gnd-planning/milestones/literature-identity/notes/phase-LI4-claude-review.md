# LI4 Claude Code diff review

One read-only Claude Code reviewer, Sonnet high effort, prompt on stdin. Implementation snapshot relative to e76c3c59. Prompt SHA-256: `6176128e3d5e00733e5eb34275b5b7fea57a2e5a328c6eda62d7ec406ab8b028`. Output retained verbatim with host paths sanitized if present.

---

I read the spec, the producer, `judgments.py`, `api.judgments`, the publication and process primitives and every fixture. I executed nothing, and that includes the hash-pinned quote offsets, the model validation and `gnd check`. A1–A5 are not refuted on the shipped fixture, but several claims are weaker than the spec states and some are untested. Nothing here is a blocker for the happy path.

## Findings, highest risk first

**F1 (medium-high): the producer ignores the policy's trust mode, so a self-asserted policy admits rows.**
- `evaluate_judgments` accepts `trust_mode: "self-asserted"` with no pins when each receipt's `trust` equals that mode (`src/gnd/judgments.py:594-597`, pin rule at `:149`). Its report then says `verification_contract: "self-asserted"` (`:657-659`).
- `_judgments` (`assertion_admission.py:150-157`) checks `command`, `outcome`, `error` and a dict-typed `judgment_policy`, and nothing else. It never reads `verification_contract`, `assurance` or `trust_mode`, and `admission.json` doesn't record them.
- Repro, not run: set `trust_mode` to `self-asserted` and `trusted_receipts` to `[]` in `policy.json`, set each receipt's `trust` to `self-asserted`, flip `opinion-02` to `approve`, then run the producer. The subject digests don't cover `trust` or `verdict`, so no re-pinning is needed. I expect exit 0, row 2 admitted and the projection stamped `tool-output`/`literature-assertion-admission/1`.
- A5's "forged input refuses" therefore holds only in consumer-pinned mode, and nothing enforces or records that mode. Fix: require `verification_contract == "consumer-pinned-bytes-v1"`, or at least write it into the record.

**F2 (medium): no test covers a forged receipt.**
- The refusal parametrization (`tests/test_li4_assertions.py`, `test_inputs_refuse_without_a_complete_publication`) has no case that edits a receipt's `verdict`, `trust`, `sources` or subject digest while leaving the pin alone.
- `test_receipt_serialization_then_verdict_change` always calls `repin`. By reading, the correct behavior is `refuse("trust")`, which gives outcome 3 and producer exit 3 (`judgments.py:594-597`, `api.py:1184-1187`). That behavior is unpinned.
- Add a case that flips `opinion-08` from abstain to approve without repinning.

**F3 (medium): the condition sentinel is an exact lowercase string match.**
- `_support` tests `row["condition"] == "unspecified"` (`assertion_admission.py:83`). `_rows` only requires a non-blank string (`:49`).
- `"Unspecified"`, `"unspecified "`, `"none"` and `"n/a"` all count as a concrete condition. Rebinding the receipt as T2 does would pass such a row into the positive projection, which defeats A1.
- Related: an `unqualified` row carrying a real condition, such as `"high noise"`, passes silently. A `conditional` row only needs a concrete `condition`; `regime` and `experiment` may still be `unspecified`. That matches the spec text, but the spec also says a conditional statement "holds condition, regime and experiment".
- Fix: compare after `strip().casefold()`, and refuse an `unqualified` row whose `condition` isn't the sentinel.

**F4 (medium): the assertion identity key collides for several legitimate shapes.**
- `_identities` and `project` (`:54-62`, `:107-109`) require a bijection between statements and `(work, passage)`. `version`, `experiment` and `predicate` aren't in the key.
- Two experiments, or two versions of a work, reported in one passage make the whole input exit 3, not just the colliding row. A "versioned work" is only a free-text role; v1 and v2 of one `(work, passage)` cannot coexist.
- This follows the spec's "identified by work and passage", but it undercuts "distinct experiments remain distinct rows" and "model a versioned work". The model also has no constraint tying statements to the `assertion_names_*` rows. Those links, and the closed sets for polarity, attribution and kinds, are enforced only in Python (`TAGS`, `_identities`), so mechanical admission can never block a statement row.

**F5 (medium): the producer doesn't check that the report matches its inputs.**
- The spec says "a matching closed report supplies target opinions". The producer compares neither `judgment_policy.policy_sha256` nor `receipts_sha256` with the snapshot digests. The report is also not closed: extra keys are accepted, `opinion_admission` is never cross-checked, and nothing checks that the report's targets cover the policy's targets.
- The child runs privately over copied bytes, so a mismatch is unlikely in practice. But `admission.json` binds a report digest without establishing that the report describes the bound policy and receipts.
- If you add the `receipts_sha256` check, special-case an empty `receipts` list. The child then hashes a regenerated canonical empty document (`judgments.py:482-484`), which won't equal the snapshot.

**F6 (low-medium): the fixture's mention span doesn't match its text.**
- Statement 7's actor is `notes@390-396`. Receipt 07's quote starts at 390, the start of line 8 of `passages.txt`, and I counted the offsets by hand. So 390–396 is `"The no"`, not "Quartz" (about 421–427) or "note".
- The document id `notes` also matches neither `passages.txt` nor `working-notes`. No code or test validates mention ids.
- Either the id is opaque and the README's "document and span identifier" claim is unverified, or the fixture is wrong.
- Separately, eligibility ignores `actor_kind` and `object_kind`. The unresolved-mention row is projected as a positive own finding. The corpus gate approved that, so I'm flagging it for awareness only.

**F7 (low-medium): weak or non-discriminating tests.**
- **Over-limit:** `policy["targets"] *= 103` yields 1030 duplicate targets. Both the 1024 cap and the duplicate rule would refuse it (`judgments.py:115-118` and `:131-134`). The test can't tell which fired, so use distinct indexes beyond 1024.
- **No refusal reasons asserted:** every refusal test checks only exit 3 and that the directory is absent. Producer-specific refusals (`_rows`, `_identities`, `TAGS`, `_targets`) have no mutation test, and malformed input is covered only for `policy.json`. A producer that couldn't start the child (see F8) would pass every refusal test, and only the positive tests would notice.
- **Child error reason discarded:** the child's `error.reason` is dropped for any exit other than 0 or 1 (`:150-151`). Stale subject, stale evidence and limit all surface as `judgments:refused`.
- **Not a linearity test:** `test_maximum_contextual_projection_is_bounded` runs one size, 1024 rows, with a 10-second bound. Even quadratic code would pass. The spec says "linear projection test"; compare two sizes.
- **Pre-judgment refusal not pinned:** "existing destination refuses before judgment execution" can't be told apart from a refusal at publish time (`:163` vs `publish_directory_once`).
- **Rubric unread:** `rubric.json` is read by no code and no test. I confirmed by grep that only the gate and spec mention it, and `case-outcomes.json`'s `disposition` is unused. I checked by reading that the dispositions agree with the receipt verdicts (00 to 01, 03 to 07 supported/approve; 02 stretched/reject; 08 insufficient-evidence/abstain), but nothing pins it. D7 and A3's "distinct outcomes" are asserted only against the raw labels of rows 3–6.
- **One reason for four cases:** negation, comparison, speculation and citation all fail with the single reason `not-positive-own-finding` (`:118-119`), so the audit record can't distinguish the four.
- **Model not validated directly:** T1 says "model exit 0", but the test runs `gnd check` on the admitted output only.

**F8 (low, needs execution): the child runs with an empty environment.**
- `env={}` (`:147`) means no `PYTHONPATH`. If `gnd` is importable only through `PYTHONPATH`, the child exits 1 with empty stdout. `strict_json` then raises `ValueError`, giving exit 3 from `main` but a raw `ValueError` from `admit()`. This fails closed, but the reason is misleading.
- `asyncio.run` inside `admit` also raises `RuntimeError` when called under a running loop. `main` doesn't catch it.
- `--unredacted` is hard-coded, so `GND_DISCLOSURE=customer` makes every run exit 3. The producer needs only `admitted` and `verdict`, which the redacted report keeps, so redaction would work.

**F9 (low): other points.**
- With more than one judge, `admitted` follows `minimum_approvals`. An `[approve, reject]` pair with `minimum_approvals=1` clears `_support`, so "rejected cannot approve" is policy-dependent.
- A statement that isn't a policy target gets reason `missing`, the same as a target with no receipt.
- T8's "first moves admission record only" is imprecise: `judgment-report.json` also moves, because it embeds `receipts_sha256`. The test doesn't assert that.
- There is no determinism test (two identical runs, compare all four files), which the "portable relative route" claim relies on.
- macOS: `read_regular_path` refuses absolute paths through `/tmp` or `/var` symlinks.
- The `dev/components` changes and the committed fixtures are outside the supplied diff. I only saw that `graph.md` lists exactly the five imports the module uses.

## Claims verified by reading
- **Exit mapping:** `api.judgments` returns 0 if all targets are admitted and 1 otherwise. Errors give 3, or 4 for limit and io. The producer accepts only 0 or 1, with matching `outcome` and no error, so D2 holds (`api.py:1181-1187`).
- **Refusal order:** exists-check, then four bounded reads, then the child, then `project`, then publish. The marker is last, the tree is inventory-checked, and a failure removes the directory (`artifacts.py:1653-1720`). No partial result survives a refusal.
- **Eligibility:** rows 0, 1 and 7 are the only `asserts` + `own-finding` rows that are also supported. Rows 3–6 are supported but non-positive. Row 2 is rejected, 8 abstained, and 9 has no receipt and so is `missing`. This matches `case-outcomes.json`.
- **Quote offsets:** the byte offsets for receipts 00–08 are consistent with `passages.txt` (ASCII, one line each).
- **Selection:** the projection keeps raw order and statement rows verbatim, and filters identity rows by the kept assertion ids. The record's field set matches the spec exactly.
- **Parsing and reads:** `strict_json` refuses duplicate keys, constants, depth over 32 and integers over 18 digits. Read caps equal the API caps (10 MiB, policy 1 MiB).
- **Skills and packaging:** both skill pointers are identical text and don't touch the guarded sentences in `test_skill_prose_sync.py`. `uv_build` ships everything under `src/gnd`.

## What needs execution
1. The exact T1–T10 suite, including the gate's claim that the judgment command exits 1 with admitted 0, 1, 3, 4, 5, 6, 7.
2. The F1 self-asserted run, the unpinned forgery run and the F3 sentinel variants.
3. The hash-pinned quotes and the F6 offsets against `passages.txt`.
4. `gnd validate` on the model, and `gnd check` on both the raw and admitted populations.
5. Byte-determinism across two identical runs.
6. The F8 environment behavior without `PYTHONPATH`.
7. The corpus-gate hashes for `policy.json`, `receipts.json` and the test file.
8. Ruff, the guard list and the components check.
