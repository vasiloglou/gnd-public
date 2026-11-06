# Close reader 3: completion predicates, records and evidence

Scope: type-induction-skills at `3665e28f`, read-only. I read the plan, the gate 001, records 002-006, all five specs, the README and the predecessor's 007/008/009.

## Verdict: approve-with-fixes

The phase evidence is real and mostly stated honestly. Every digest that should match does match, and the owner-gated spec digests check out against git. The records do state their limits: superseded recording bytes, the TS4 `no_population_access: false`, prose-only criteria. The defects are in three places. First, how predicate 5's with-family parity and predicate 6 are recorded. Second, a delegated narrowing of an owner-approved predicate that is filed as a "refuted premise". Third, stale status and open-item bookkeeping. None of this blocks the close, but the close record must fix it.

## Digest verification

I checked every `evidence:` entry in records 002-006 (91 entries) with `shasum -a 256`.

- **Match: 79.** This covers all evidence files, all spec and review notes, all TS4 and TS5 entries, and all TS2 source entries.
- **Mismatch: 12.** Each one is a later legitimate edit:
  - 002 (TS1): `type_evidence.py`, `types.py`, `service.py` and `commands/discover.py`. All four were changed in TS2 `8b69a278`, and TS2's 003 records the current digests.
  - 002: `discover.md`. Re-recorded in 003, then 006.
  - 002: `tests/test_discover_type_evidence.py` (record `80f2ea03`, disk `6a7c68b2`). Changed in TS2 `8b69a278`, the usage-message assertion (TS2 spec §12 I6, named in 003:115-116). **No record lists its current digest** (F9).
  - 003: `discover.md`. Re-recorded in 006.
  - 004 (TS3): the skill, the recorder, `test_judge_fact_types_skill.py` and `gnd-orm-core/SKILL.md`. All changed in TS4, which re-records them in 005. 004:155-160 states that the skill and recorder were superseded.

Gate digests, checked against git:

- Plan r1 is `c2a2c091…` at `dfb14884` and at `c5a15fd`.
- TS1 r1 is `c04210d7…` and TS1 r2 is `6d68a509…` (at `496435d2`).
- TS2 is `eb24b8f3…` (at `85d67fb4`). TS3 is `08fb0052…` (at `b7978b78`).
- All of these match.
- The TS4 (`2add491b…`) and TS5 (`fdc7cb9e…`) pre-mark digests **cannot be checked from git**: each spec's draft and delegated mark landed in one commit (`16d478ad`, `79cf0a5c`).

Recording manifests:

- In TS3 `recording-2` and TS4 `recording`, every kept file matches its manifest.
- TS4's manifest source `tools/record_judge_sessions.py` (`e3e7ac93…`) is stale against disk (`f3f5ab36…`, after the R1 fix). The test exempts it explicitly (`tests/test_model_multivalued_skill.py:185-186`).

## Findings

**F1 (major): predicate 5's with-family parity has no recorded table against the pre-milestone baseline.**
- Location: plan:88-91, plan:102 (TS-R1); 002:124-128 and 002:161-163; 003:149-150.
- Evidence: the recorded tables are `TS1/parity-b733b2a.json` vs `parity-after.json`, and TS2's IK4 pair. Both are the IK4 corpus, and `CT4/capture_parity.py:1` says it runs "without the fact-type family". The only recorded with-family table is `TS2/fixture-parity-*.json` (36 runs), and its baseline is `7b171bb2`, which already contains TS1.
- TS1's own with-family baseline evidence is two things:
  - T16, which compares with and without the option inside the new tree. The TS1 reviewer says T16 "cannot catch a regression shared by both paths" (phase-TS1-claude-review.md:73).
  - The reviewer's 29-case run against HEAD, which lives in scratch (`$R`) and is not kept under `evidence/`.
- The predicate's "with or without `--families fact-type` … by a recorded table" is therefore met only for the without-family half.
- The chain is otherwise sound: `parity-b733b2a.json` equals CT4's `parity-after.json` (`a093457d…`), TS2's `parity-7b171bb2.json` equals TS1's `parity-after.json` (`4061906d…`), only E6's `stderr_sha256` differs, and I confirmed that no `src/gnd` module changed after `b4ef8cbf` (only package data under `examples/`).
- Fix: at the close, capture the TS2 fixture-parity script (and the IK4 corpus run with the family) against `b733b2a` and record that table. Otherwise, record predicate 5 as "met without the family; with the family, met against `7b171bb2` and by an unrecorded reviewer run at TS1".

**F2 (major): predicate 6 is recorded "met", but its own spec says "not as written".**
- Location: 006:111, 006:147-149, 006:165-166; phase-TS5-spec.md:78-83, 109, 130.
- Evidence: the spec's sweep says "Predicate 6 as one evidence | Not as written (P5); D2". The record says "met with refuted premise P5". Nothing refuted P5: one walk is feasible, but it needs a third paid run that nobody authorized (006:148-149).
- This is a scope reduction of an owner-approved completion predicate, made under the delegated `(d5)` D2. It is not a false premise. The owner's DC-TS5 "Looks good, continue" accepts the page; it is not an amendment of the predicate.
- Fix: in the close, record predicate 6 as "not met as written; amended by delegated ruling `(d5)` D2". Surface it for owner acceptance, or ask whether to authorize the third recording.

**F3 (major): the §10 rows and TS-D0 are not swept. Some are ruled, some are moot, and some were implemented without a ruling.**
- Location: 001:31-36; README:38-39; plan:24-33, 465-476.
- Ruled by the owner:
  - TS-D4, TS-D5, TS-D9 and TS-D10 via TS2 `(a2)` D1, D7 and D8.
  - TS-D6 via TS3 `(a3)` D1.
  - TS-Q1 via TS1 D1, TS-Q2 via TS2 D8, and TS-Q3 via TS2 D3.
- Met in fact: TS-D1.
- TS-D0 can be discharged now. The owner's words are quoted in `composition-and-type-induction/008-owner-rulings.md:51-52` ("semantically with a skill"; "with a skill a variant of rai-orm"). Commit `e32cc362` precedes the plan draft, and phase-TS1-spec.md:55 already cites them "for plan TS-D0". Yet plan:31-32 says the words "are not in the repository", and README:38 still lists TS-D0 as open.
- TS-D7 is moot: the owner ruled CT4-Q1 in 008:55. But the "record the dependency" half was never done. Under internal or unset mode, `provenance.induced_from` writes the guessable attribute digest into the model; 007:196 notes that this digest is guessable.
- TS-D2, TS-D3, TS-D8 and TS-D11 were implemented as proposed, and no gate rules them.
- Fix: in the close, add a §10 disposition table with one row each, marking every ruling as owner, delegated `(d*)` or "implemented under proposal, unruled". Cite 008 for TS-D0 and record the TS-D7 dependency.

**F4 (minor): the README status is stale and contradicts itself.**
- Location: README:9-14 and README:38-39.
- Evidence: the bold status still ends at "TS1 implemented and recorded", and "Still open: … TS-D2 to TS-D11" ignores the rulings listed in F3. The body (59-70) is current.
- Fix: refresh both at the close.

**F5 (minor): two different approvals share the label `(a1)`.**
- Location: README:10-11; 002:59-60; phase-TS1-spec.md:5, 263.
- Evidence: `(a1)` labels both the plan approval (001) and the TS1 spec r2 approval, which were two answers ("Yes, approve r1" and "Approve as proposed"). Both are the owner's quoted words, so neither is wrongly attributed, but the reference is ambiguous.
- Fix: relabel the TS1 spec approval, for example `(a1b)`, or note the reuse.

**F6 (minor): premise labels P1 and P2 collide across records.**
- Location: 002:217, 002:222; phase-TS1-spec.md:23; 003:254-256, 003:262-268; 004:181; 005:172; 006:159.
- Evidence: the TS1 spec and record use phase-local P1 (digest keying) and P2 (`DiscoveryDefect` cap). TS2 onward use milestone-wide P1 (judgement provenance) and P2 (no `functional`). In TS3's "P1, P2 and P3" and TS5's "P1–P6", it is unclear whether TS1's P2 is included.
- Fix: rename TS1's premises (for example TS1-P1 and TS1-P2) in the close's plan-repair list.

**F7 (minor): a TS4 record sentence is false for its own recording.**
- Location: 005:143-146.
- Evidence: the record says "both recordings' manifests bind the recorder's bytes and the tests check those sources are current". The TS4 test skips the recorder (`test_model_multivalued_skill.py:185-186`), and the TS4 manifest's recorder digest is stale. The TS4-C5 row (005:118) says "current" only for the skill. That is accurate, but it does not say the recorder was superseded.
- Fix: one sentence in the close: the TS4 recording ran on recorder `e3e7ac93…`, which R1 superseded, and the recorder is exempted in T14.

**F8 (minor): the TS1 implementation go-ahead is not recorded.**
- Location: 002 (entire record).
- Evidence: the TS1 spec says implementation begins "only on the owner's explicit go-ahead" (phase-TS1-spec.md:9-10). Record 002 never states that go-ahead, unlike 003:80 and 004:56-57. Separately, the TS2 spec was drafted on a "relayed" go-ahead (README:46). Drafting needs no approval, so that one is harmless.
- Fix: cite the go-ahead in the close, or state that it was not recorded.

**F9 (nit): no record carries the current digest of `tests/test_discover_type_evidence.py`.**
- Evidence: see the digest section above.
- Fix: list it in the close's evidence.

**F10 (nit): the TS4-C5 recording passed 9 of 10 recorded checks.**
- Location: 005:90, 005:159-161.
- Evidence: "met" rests on a corrected check run offline over the kept streams. The record says so honestly. The close should repeat it rather than shorten it to "met".

## Predicate status

| # | Recorded | Evidence supports |
|---|---|---|
| 1 | TS1 met | yes (T1-T20; 52 tests; cap and time measured) |
| 2 | TS2 met | yes, with P1 and P2 recorded; 31/31 mutations; T21-T22 apply |
| 3 | TS3 met; TS3-C4 for superseded bytes | yes after `recording-2` (10/10, current sources); C3 is prose plus one run in unset mode; customer mode has no run |
| 4 | TS4 met | yes, with R1 (F10); the redacted, truncated and `null` branches are prose only |
| 5 | parity | partial (F1) |
| 6 | TS5 met with P5 | overstated (F2) |
| 7 | close pending | gates, reviews (one subagent per phase) and PRs #88-#90 recorded; the close sweep, the PR and the slow lanes are outstanding |

**CT-close-Q1 and CT-close-Q2: discharged in substance, not yet formally.**
- Q1: `test_t9_distinct_lifts_the_once_per_generic_limit`, the TS3 skill with its recordings, and `discover.md:151-160`, which now separates default from judged behaviour.
- Q2: `test_t14_many_to_many`, `test_t17`, the TS4 skill with its recording, and `discover.md:136-137`. The default still counts `multi_valued`, as 008:52 ruled.
- 009:33-35 hands both to this milestone. The close record must state the discharge in writing.

## Open items with owner and target, as the records give them

| Item | Source | Owner / target |
|---|---|---|
| Plan repairs P1 (TS2), P2 (TS2), P3 (TS3), P4 (TS4), P5 (TS5), P6 (TS5), §2.2 key `g<n>`, TS1's P2 and TS-R7 "growth zero", TS1 I8 packaging test name | 002:217; 003:254; 004:181; 005:172; 006:159 | "at the close"; **not yet applied** (plan unchanged since `181d3abd`) |
| TS3-Q1, a shared recorder turn loop | 004:172 | TS4, or maintenance; then "maintenance, with TS4-Q1" |
| TS3-Q2, `judge.skill` tokens scanned | 004:174 | "the CLI owner (maintenance)": **no named person or milestone** |
| TS3-Q3, re-record | 004:179 | resolved (005:171) |
| TS4-Q1, a single stream-walk generator | 005:168 | maintenance: **no named owner** |
| CT4 DateTime kind (minted String value type) | 002:209; 003:247 | maintenance (TS2 D9 declined it): **no named owner** |
| Malformed-YAML traceback, exit 1 | 002:214 | maintenance: **no named owner** |
| UTF-16 model `UnicodeDecodeError` | 003:251 | maintenance: **no named owner** |
| `test_rf7_structure.py` red at base (2 failures) | 004:139; 004:183 | maintenance: **no named owner** |
| `bounded_json` "proposal" wording | 003:220 | maintenance, outside the discover lane: **no named owner** |
| Deferred `types._kind` cross-module | 002:179 | executed in TS2 (D9); closed |
| Slow cadence: `evidence or census`, `test_public_distribution.py`, `test_release_acceptance.py` (literals edited, not run), full default lane, every tutorial group | 002:17; 003:19; 004:17; 005:17; 006:15 | the milestone close |
| TS-D0, TS-D2, TS-D3, TS-D7 (dependency), TS-D8, TS-D11 | 001:31; README:38 | **unruled; no target** beyond the close (F3) |
| Customer-mode runs of either skill; S3's `null`, redacted and truncated branches; R1's other-generic case | 004:162; 005:152 | **unowned** (stated limits) |
| Binding blind to `--actor`, `--requested-at` and population name at the trim boundary | 003:233 | stated limit; **unowned** |
| Predicate 6 single walk (third paid run) | 006:147 | **owner decision needed** (F2) |
| Carried from CT: CT-close-Q3, Q4, Q5, CT2-Q1, CT2-Q2, O18 | plan:381 | CT owners; Q3 and Q4 were ruled in 008; O18 belongs to the reporter |
| Owner acceptance of the milestone | plan:96 | the owner |
