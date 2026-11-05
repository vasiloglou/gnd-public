# TS2 adversarial review (one reviewer)

One reviewer is one reviewer. Retained below the rule, verbatim except one
edit: the session scratch path is replaced by `<scratch>`. The reviewer ran
in a subagent over the uncommitted TS2 working tree on top of `052bd7f5`,
after the D9 rename. The harness refused its `report.md`, so its returned
message is the report. Its probe scripts lived under `<scratch>/review-ts2`
(not retained); the phase record names the regression test for each finding.

---

# TS2 adversarial review (branch claude/ts2-spec, uncommitted tree on top of 052bd7f5)

Note: the harness blocked writing `report.md` ("subagents should return findings as text"), so this message is the complete report; no `report.md` was written.

Scratch root: `S=<scratch>/review-ts2`. Every probe below runs from the worktree root as `uv run python $S/probes/<file>`; `$S/probes/h.py` imports the TS2/TS1 test helpers (`build`, `discover`, `judged`, `judgements`, `verdict`). Known §12 items I1–I9 are not re-reported.

Gates I ran on the tree: `tests/test_discover_type_judgements.py` 62 passed; the TS1 gate list from the §8 ledger plus `test_schema_sync.py` 585 passed.

**No blocking defect was reproduced.** Nothing is written after a refusal, no TS2 path tracebacks, no-option runs are byte-identical to 7b171bb2, and judged proposals pass `gnd evolve preview --policy additive`, apply and `gnd validate`. Five reproduced findings follow.

## F1 — D4 is bypassed when the evidence truncated candidates (hardening; arguably blocking under TS-R2)
- `src/gnd/discover/type_judgements.py:120-126` checks D4 only over the candidates *listed in the evidence*. `build_evidence` drops candidates from the tail once the 10 MiB cap fills (`truncated > 0`, which D5 allows), so a later group lists no candidates, its already-induced fact type is invisible, and `distinct` is accepted.
- Repro: `uv run python $S/probes/p7b.py 15000` (TS1 fixture plus 15,000 one-row below-support attributes placed before `size`; default min-support).
- Observed: `evidence bytes 10481016 truncated 31227 truncated_groups 0` / `size group g15000 shape_match candidates listed: []` / `exit 0` / `size re-induced: ['item_has_attribute_induced_15000'] proposed total 1 over_budget 0` — `size` was already induced as `item_has_attribute_induced_0`, so this is a second induced fact type for the same attribute.
- Expected (D4/TS-R2): exit 3. The CLI already computes `origins(view)` for every fact type; checking origins over all fact types the entity plays (not only listed ones), or refusing verdicts on candidate-truncated groups, would close it. Related: for a fully candidate-truncated group the judge cannot name `of`, so only `distinct` is expressible.

## F2 — `judge.skill` is unscanned yet copied into the model under customer (hardening)
- `type_judgements.py:216-220` scans only `judge.agent` and `rationale`; `types.py` (`fact_provenance` block) writes `judge.skill` into `provenance.judgement.skill`. The schema pattern `^[a-z0-9][a-z0-9-]{0,63}$` admits attribute values such as the canary `colour-7f3a`.
- Repro: `uv run python $S/probes/p11.py` → `exit 0`, `canary in proposal: True`; the same text in `agent` → `exit 3 judge.agent names a population value`.
- Expected: §6.6 says `judgement` holds "no population value" and TS-R5 applies; scan `skill` too (or restrict it to known skill names).

## F3 — whole-token matching over-refuses relative to the spec's boundary rule (hardening, refuse-side)
- `type_judgements.py:35` (`_TOKEN`) / `:135-138`: punctuation becomes single-character tokens, so a hidden value that starts or ends with punctuation matches even when a letter/digit is adjacent. §6.5 says "the characters on either side are not letters, digits or `_`".
- Repro: `uv run python $S/probes/p6.py` (hidden value `?`, not in the model, mode unset): rationale `'Is this the same fact type?'` → `exit 3 … verdict 1: rationale names a population value`; without the `?` → exit 0. By the spec the `?` is preceded by the letter `e`, so it should be accepted.
- Randomised comparison against a literal implementation of §6.5 (`uv run python $S/probes/p3.py`, 60,000 cases): 4,600 over-refusals, 0 misses. On word-only patterns the Aho–Corasick matcher agrees exactly (0 mismatches), including failure-link matches.
- Expected: implement the character-boundary rule as written, or document the token rule.

## F4 — a judged `distinct` can create a fact type whose reading is byte-identical to an existing one (hardening)
- `types.py:266`: the reading uses the group `number`; only the id gets the clash suffix.
- Repro: `uv run python $S/probes/p9.py` (TS1 fixture without the `size` rows, `distinct` on g0, internal): the new `item_has_attribute_induced_0_1` gets reading `{Item} has induced item_has_attribute attribute 0 {AttributeValue}`, identical to existing `item_has_attribute_induced_0` with the same role players; preview, apply and validate all exit 0.
- §6.4 says "the same placeholder reading", so this follows the spec text, but `distinct` makes the equal-signature case reachable and the two fact types become indistinguishable when verbalised. Suggest deriving the reading number from the final id, or record it as accepted.

## F5 — declared branches no test can fail (completeness)
Mutations applied to a copy of `src/` under `$S/mut/<name>`, with the TS2 and TS1 test files run against it (`uv run python $S/probes/mutate.py <name>`):
- **M1** drop the `--type-evidence-in` size refusal (`service.py`, `if len(evidence_raw) > evidence.MAX_EVIDENCE_BYTES`) → 114 passed.
- **M2** drop `model_sha256` from `_BOUND_KEYS` → 114 passed.
- **M12** drop `origin["generic"] == group["generic"]` from D4 (`type_judgements.py:124`) → 114 passed.
- **M19** pass `""` instead of the model text to `scan_free_text` (the D10 exemption wiring, `service.py`) → 114 passed. M19 is a real behaviour change: `uv run python $S/probes/p10.py` (hidden value `label`, also a model word; rationale "it reads like a label") exits 0 on the real tree and 3 on the M19 copy. D10 is only unit-tested.
- Controls: C0 (drop "judged twice") → 1 failed; C1 (drop the evidence byte comparison) → 2 failed.
- Also untested: the judged path's 70 (`TypeEvidenceOverflow`) and 74 (`OSError`) exits, and the non-JSON-evidence branch of `_first_difference`.
- T26 as specified asks for a byte comparison against 7b171bb2; the implemented T26 only checks the absence of the new keys. Byte parity exists only as the evidence scripts.

## Checked and found sound
- **TS-R1 no-option parity:** `$S/probes/p4.py` compares the tree with `git archive 7b171bb2 src` (extracted to `$S/base`) over 5 fixtures × 3 modes × {default, `--min-support 1`, `--show-values`}, families `fact-type,uniqueness,mandatory`. Proposal, report, evidence and stdout are byte-equal in all 39 cases (modulo the output file name).
- Every refusal returns before `output.write`; no traceback on any TS2 path. No message echoes a rationale, `of`, a value or a digest; a duplicate-key error does not echo the key (p1). A judged run in text format works (p1).
- **Many-to-many:** at scale (600 pairs, 640 rows, 40 repeats) examples 256, counterexamples 32, support 600/640; preview, apply and validate pass in internal and unset (p5). With a redacted value role, `redact` is copied and apply passes in internal and customer (p2).
- **Matcher:** Aho–Corasick is correct (above) and linear: 2,000 adversarial patterns over a 1 MB model and 5,000 rationales take about 1.4 s (p12).
- Validation order matches §6.1. Group `g<n>` positions agree with the in-memory records. `drop_last` after judgement stays consistent with `proposed[]`.
- Recompute binding refuses on any setting change; I found no false refusal with unchanged inputs. One theoretical case: a trim exactly at the size boundary depends on `--actor`, `--requested-at` and the population file name, which the evidence does not record.
- Pre-existing at 7b171bb2, not TS2: a UTF-16 model gives a `UnicodeDecodeError` traceback from `load_model_bytes` (`model/__init__.py:290`, probe p8).

## Hygiene
No worktree file was edited; all mutations ran on copies under `$S/mut`. The first pytest run and `uv run` calls before I set `PYTHONDONTWRITEBYTECODE=1` may have refreshed gitignored `__pycache__` files; `git status` shows no change.

Files: `$S/probes/` holds `h.py`, `p1.py`–`p12.py`, `p7b.py`, `mutate.py`; the gate log is `$S/gate.log`.
