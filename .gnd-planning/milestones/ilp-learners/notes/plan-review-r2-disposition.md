# Plan review — round 2 (confirmation) disposition

2026-10-27. This is the single confirmation round that the
[round-1 disposition](plan-review-r1-disposition.md) declared.

**How it ran:**
- **Instrument:** the same four local reviewer agents, with the same lenses
  (D5 (o)).
- **Restriction:** each reader judged only whether its own round-1 blocking
  findings are resolved, and reported only defects that r2's own changes
  introduced.
- **The owner's request** for this round, 2026-10-27 (o): "Run the declared
  confirmation round over plan r2 and IL1 spec r2 with the same four lenses,
  restricted to whether the round-1 blocking findings are resolved".

## Subjects and limits

- **Plan r2** SHA-256:
  `e0668e30d4ee8c6e9e921e0cbad66d80338f94e5bcc9d69740ce318700ce3bb9`.
- **IL1 spec r2** SHA-256:
  `4a06f58346ea3e147f57a485ee2f8c5189190938130c44c47b5022ed0cff5af8`.
- **Inspection HEAD:** `63f7f1f`; the planning files are uncommitted.
- **Retained snapshots:** the [plan](../evidence/plan-review-r2/ilp-learners-plan.md)
  and the [IL1 spec](../evidence/plan-review-r2/phase-IL1-spec.md). The
  [manifest](../evidence/plan-review-r2/manifest.json) records snapshot and
  reader-note digests.

**How the readers worked:**
- Every reader verified both digests and diffed r1 against r2.
- All four ran concurrently, one model family, run locally.
- No installs, credentials, network or paid tools were used.
- Probes wrote only under the session scratchpad.
- No repository file was changed.

**Edits to the retained notes:** the reader notes keep the returned text.
Scratch paths were already written as `<scratchpad>`.

## Opinions

| Reader | Lens | Verdict | Round-1 blockers | New: blocking / hardening / completeness |
|---|---|---|---|---|
| [1](plan-review-r2-reader-1.md) | semantics and admission safety | approve-with-fixes | 4 of 4 resolved | 0 / 3 / 1 |
| [2](plan-review-r2-reader-2.md) | implementability, homes and layers | approve-with-fixes | 6 of 6 resolved | 0 / 4 / 1 |
| [3](plan-review-r2-reader-3.md) | protocol, authority, compatibility, privacy | approve-with-fixes | 2 of 2 resolved; R3-F2 and R3-F4 repairs judged honest | 0 / 3 / 2 |
| [4](plan-review-r2-reader-4.md) | measurability and reproducibility | approve-with-fixes | R4-F1 resolved; R4-F7 partially | 0 / 3 / 1 |

**The round-1 blockers.** **13 of 14 are resolved, and R4-F7 is partially
resolved.** Its remainder is the same three defects as R4-2-F1, R4-2-F2 and
R4-2-F4 below; it is not a separate gap.

**The new findings.** There are **18, none blocking.** Some are duplicates
across readers, so there are 12 distinct defects. Reader 3's privacy scan of
the milestone directory found 0 hits.

## Coordinator reproduction

| Finding | Check | Result |
|---|---|---|
| R2-2-F2 | `ilp_rewrite.rewrite(clause, index, neutral, columns)` (`ilp_rewrite.py:62–64`) takes no model or index; `test_ilp_bridge.py:552–554` calls it with four positional arguments | reproduced |
| R1-2-F1 | check 5's `role_type` map keys every `_` under one name (`ilp_rewrite.py:127–133`), while `_vars` and `_anonymous` treat `_` as fresh (`:55–61`) | reproduced by reading |
| R1-2-F2 | check 5 tests only that each type's primitive is `integer` (`ilp_rewrite.py:143–145`), not object-type compatibility | reproduced |
| R4-2-F1, R2-2-F3 | the import report embeds input and output paths (`ilp_service.py:456–462`); the proposal's `requested_at` defaults to `datetime.now(UTC)` (`:418`) | reproduced |
| R3-2-F4 | `_sensitive_values` skips env values shorter than 4 bytes (`process.py:277–285`) | reproduced |
| R1-2-F4, R2-2-F4, R4-2-F3 | three readers independently simulated `\\[0-7]{1,7}\\` before `\\.`; an 8-digit escape never reaches `_unquote` | accepted on three agreeing probes |
| R3-2-F1, R2-2-F1 | spec r2 defines `IMPORT_TARGETS` as every target and pins both enums to it; plan r2 routes `amie` through `gnd import mined-rules` | reproduced by reading |

No finding was refuted.

## Findings grouped by repair

| Theme | Findings | Proposed repair (r3) |
|---|---|---|
| A. Target tuples | R3-2-F1, R2-2-F1 | **`IMPORT_TARGETS`** becomes the entries with `contract == "labelled-clauses"` (what `ilp-rules` accepts). **The enums:** `ilp.schema.json` is pinned to `EXPORT_TARGETS` and `ilp-import.schema.json` to `IMPORT_TARGETS`. **Plan §2** states `llm`'s `exports` value (`False`). **IL4** names its own report `command` value. |
| B. Join check specification | R1-2-F1, R1-2-F2, R1-2-F3, R2-2-F2 | **A shared function.** 9b becomes `check_join_types(atoms, compares, columns, *, closures)` in `ilp_rewrite`, called by `rewrite` and by IL4's Horn-rule mapping. **The closure map** (`object type → {t} ∪ supertype_closure(t)`) is computed once in `_prepare` from ModelIndex and carried on the prepared state, not on the `gnd-ilp/1` wire. `rewrite` gains a keyword-only `closures=None`; `None` skips 9b, so existing four-argument callers keep working. **`_` is excluded:** each occurrence is fresh, and a T5b case covers `_` at two incompatible types and stays exit 0. **A comparison** predicate's declared type counts as a join site of its variable operand (D13). |
| C. Replay determinism | R4-2-F1, R2-2-F3 | **Fixed arguments:** the script and T9 both pass `--requested-at 2026-01-01T00:00:00Z`, `--actor ilp-live` and `--format json`, and run from a fixed working directory with identical relative paths. **What T9 asserts:** the exit, the report with its path fields normalized, and the proposal's SHA-256. For an exit-3 outcome it asserts the redacted stderr refusal line instead, and no `import-report.json` is expected. |
| D. Outcome list | R4-2-F2 | **Two fields:** `termination` ∈ {`rendering-rejected`, `completed`, `learner-timeout`, `wall-clock-kill`, `output-limit`} and `import` ∈ {`none`, `refused:<name>`, `admitted`}. **Reconciled labels:** `unparsable` is `refused:unparsable`, and a block over the cap is the importer's own refusal. |
| E. Program extraction | R4-2-F4 | **The banner** string is recorded from the pinned version at the gate. **The program** is the first maximal run of `^wrong\(.*\.$` lines after the last banner. **One extractor function** is used by the script and by T9, and T9 asserts it reproduces `program.pl` (or empty) from the committed raw stdout. |
| F. 8-digit octal | R1-2-F4, R2-2-F4, R4-2-F3 | **The tokenizer** reads `\\[0-7]+\\` before `\\.`. **`_unquote`** refuses more than 7 digits with the octal message. **T4b** gains the two-quote context case. |
| G. IL4 command surfaces | R3-2-F5, R2-2-F5 | **Existing goldens:** plan §5 and IL4 name the changed existing goldens (the `export ilp` help usage line; the `unknown_flag` exit stderr). **The new rule:** the target-decides-required rule is a post-parse check with exit 64, and the missing-`--labels` exit for `popper` and `neutral` stays unchanged. **`mined-rules`** lives in `gnd.commands.checking`, which is already bound to `ilp_service`, so the "bound in `gnd_entrypoints.json`" text is corrected to "no new binding". |
| H. D8 decline | R3-2-F2 | **If D8 is declined:** IL5 keeps fixture-only evidence, its IL6 row shows `not run (D8)`, and completion predicates 5 and 6 accept that outcome. |
| I. Privacy and dependency checks | R3-2-F3, R3-2-F4 | **T7** builds the wheel into a temporary directory and reads `Requires-Dist` from its `METADATA`, so the plan's control stands as written. **The evidence script** substitutes `<scratch>` and `<home>` itself in every file it writes, and T8 is named the backstop. **T8** matches the username as a whole path component, whatever its length. |

## Decision the repairs need

| ID | Question | Readings and cost | Proposed |
|---|---|---|---|
| D13 | Does the D12 join check also cover a comparison's declared type (R1-2-F2)? | **Yes:** closes the same type confusion for models with two integer value types. It is a further narrowing of the shipped import, listed in the IL1 record like D12's. **No:** correct the spec sentence and record the gap as an accepted residual | yes |

## Convergence (computed under the declared stop rule)

| Round | Seats | Per-seat counts | Self-inflicted / total | Blocking / total | Severity ceiling | Verdicts |
|---|---|---|---|---|---|---|
| 1 | 4 | 12 / 12 / 11 / 12 | 0 / 47 | 14 / 47 | high | 4 request-changes |
| 2 | 4 | 4 / 5 / 5 / 4 | 18 / 18 | 0 / 18 | high (hardening) | 4 approve-with-fixes |

**The stop rule is met.** The self-inflicted ratio is 1.0 (above one half),
blocking fell to 0, and every verdict is approve-with-fixes. Under the declared
budget, **no further review round runs.**

**After review, two readings:**
- **Reading (a):** the owner directs r3, applying themes A–I (and D13 as
  ruled), with no further review round, as the induced-knowledge milestone did
  after its round 2 (its P-1..P-9). r3 bytes would then carry no review
  opinion, and plan approval would be over r3.
- **Reading (b):** the owner approves r2 as reviewed, and themes A–I move into
  the IL1 spec at its gate, where IL1 is the instrument (themes A–F and I are
  IL1 spec text; G and H are plan text for IL4 and IL5).

## Owner direction (appended after the round)

**2026-10-27 (o):** "Apply themes A–I as r3 with no further review round, D13
yes. Then I will decide on plan approval over r3." This chooses reading (a)
and rules D13 yes.

**r3 applies themes A–I and D13**, tagged `(p2)` in the plan and the IL1 spec.
Theme H (the D8 decline) and theme G (the IL4 command surfaces) are plan text.
r3 bytes carry no review opinion.

## Boundary

- **No approval exists.** Plan r2 and spec r2 are not approved. Approval will
  be recorded in `001-plan-gate.md`, binding the approved bytes' SHA-256.
- **One model family.** The readers are one model family, run locally; each is
  one reading.
- **Licences are unverified.** They stay open under IL-R5 until each gate.
