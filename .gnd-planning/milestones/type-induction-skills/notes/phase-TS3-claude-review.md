# TS3 adversarial review (one reviewer)

One reviewer is one reviewer. The report is kept below. It is verbatim except
in two ways: the session scratch path is replaced by `<scratch>` and the
worktree path by `<worktree>`, and the reviewer's local paths in F8 are
reduced to `<worktree>`. The reviewer ran as a subagent over commit
`51ec0a3a` (diff `b4ef8cbf..51ec0a3a`). It edited nothing in the worktree
and made no paid model call. Its probe scripts lived under
`<scratch>/review-ts3` and are not kept; the phase record names the
regression test for each finding.

---

# TS3 adversarial review: commit 51ec0a3a (diff b4ef8cbf..51ec0a3a, branch claude/ts3-spec)

One reviewer is one reviewer. I found 7 issues. None stops the recorded run from being accepted. F1–F4 are hardening and affect what the skill tells an agent to do; F5 and F6 are recorder weaknesses; F7 is a test-coverage gap. I also found one committed path leak (hygiene, under F8). None of these repeats I1–I6.

`<scratch>` is the session scratchpad. The scratch clone `<scratch>/review-ts3/repo` is checked out at 51ec0a3a, with `.venv` symlinked to the worktree's venv.

## Findings

**F1 — `SKILL.md:62-66` (judge text) — hardening.** The skill tells the agent to put counts from the evidence in each `rationale` and its own model name in `judge.agent`. In the default mode (unset, no `--show-values`) the agent cannot see the values, but the CLI refuses any free text that matches a population value. Common short values therefore collide. The fixed `judge.skill` value can collide too, and the skill gives no way out of that.
- Repro, run from the worktree root: `PYTHONDONTWRITEBYTECODE=1 uv run python <scratch>/review-ts3/numeric_repro.py <scratch>/review-ts3 mass-k4p3 VALUE`. It copies the fixture, sets one value of group g2 to VALUE, rebuilds the evidence, rebinds the recorded judgements to the new digest and runs `gnd discover --duplicate-judgements`.
- Observed:

  | VALUE | Exit | Message |
  |---|---|---|
  | `24` | 3 | `verdict 0: rationale names a population value` (the recorded "24 rows, 24 shared pairs") |
  | `5` | 3 | `judge.agent names a population value` (the agent name is `claude-sonnet-5-5`) |
  | `types` | 3 | `judge.skill names a population value` (the skill name, which the skill requires verbatim) |
  | `d999` (control) | 0 | — |

- Expected: when values are hidden, the skill should not tell the agent to quote numbers. Rationales should cite group ids, fact-type ids and words from the model readings. The skill should also say what to do when a refusal names `judge.agent` or `judge.skill`. The `judge.skill` dead end comes from TS2's CLI scan (the skill name is matched token by token). That half should be raised with the CLI owner.

**F2 — `SKILL.md:93-100` (R3 versus R4) — hardening.** R3's condition, "every candidate with a non-null `overlap.pairs` has 0", is true by default when every overlap is `null`. Because the rules apply in order, R3 gives `distinct` before R4's "only null overlaps → ask" is ever reached. The same happens for a candidate whose role is redacted, where the overlap is always `null`.
- Repro: `python3 -I <scratch>/review-ts3/nulls_build.py <scratch>/review-ts3/nulls <worktree>/tests/fixtures/type-judgements/round-two`, then `uv run gnd discover … --type-evidence <scratch>/review-ts3/nulls/evidence.json`.
- Observed: every group's only candidate is `item_has_colour` with `pairs: None`. The prose's R3 gives `distinct`; R4 says ask.
- Expected: R3 should require at least one comparable candidate, or R4 should come first for the all-null case.

**F3 — `SKILL.md:39-44, 86-100` (candidate truncation not handled) — hardening.** Step 1 refuses only when `truncated_groups` is above 0. It ignores the separate `truncated` count of candidates left out under the 10 MiB cap. With candidates missing, R3 applies to nothing and gives `distinct` for a group that is really a 100% duplicate, and the CLI accepts it. With more truncation, the CLI accepts neither verdict.
- Repro: `uv run python <scratch>/review-ts3/trunc_repro.py <scratch>/review-ts3 3600`, then `uv run python <scratch>/review-ts3/trunc_r3.py <scratch>/review-ts3 3600`. `runner/capped_gnd.py` lowers `MAX_EVIDENCE_BYTES` to the given size in that process only.
- Observed at cap 3600: `truncated 6`, and g1 has `[]` candidates. g1 is really a duplicate of `item_has_colour`. Judging it `distinct` (the R3 result) exits 0 and proposes `item_has_attribute_induced_1`.
- Observed at cap 3100: `distinct` is refused ("already induced as item_has_attribute_induced_0"), and `duplicate` is refused too ("'of' is not a candidate … (candidates were truncated)").
- Expected: when `truncated` is above 0, the skill should refuse, or ask about the affected groups.

**F4 — `SKILL.md:86-88` (R1 ignores `origin.generic`) — hardening.** `same_attribute` compares only the attribute digest. The CLI's D4 check (`type_judgements.py:130-133`) also requires `origin.generic == group.generic`. So R1 forces `duplicate` and says "the CLI refuses `distinct` there" even when the CLI does not.
- Repro: `python3 -I <scratch>/review-ts3/generic2_build.py <scratch>/review-ts3/generic2 <fixture>` (adds a second generic, `item_has_tag`, with the attribute `dim-k4p1`), then run discover with the judgements in `<scratch>/review-ts3/generic2/j.json`.
- Observed: g4 (`item_has_tag`) has candidate `induced_0` with `origin=('item_has_attribute', True)` and `pairs: 0`. A `distinct` verdict on g4 exits 0.
- Expected: R1 should apply only when the origin's `generic` equals the group's.

**F5 — `tools/record_judge_sessions.py:133-136, 184` — hardening.** The `no_population_access` check can be bypassed, and part of it can never fire.
- `build_evidence` leaves a copy of `items.population.json` in a sibling `judge-evidence-*` temporary directory for the whole session. `Read`, `Glob` and `Grep` are allowed on any path.
- `tool_calls` scans the redacted streams. `redact` turns that temporary path, file name included, into `<tmp>`, and turns ROOT into `<repo>`. So the `str(FIXTURE) in call` branch can never match.
- Reads of `answer-key.json` are not checked at all.
- Repro: `uv run python <scratch>/review-ts3/popscan.py <scratch>/review-ts3`. It feeds synthetic tool calls through the real `redact`, `kept_stream` and `tool_calls`.
- Observed: `missed {"command": "cat <tmp>"}`, `missed {"file_path": "<tmp>"}`, `missed …/answer-key.json`, `missed cat ../*/items.*`. Only the read under the fixture path is flagged, and only because its name contains "population". `FIXTURE literal ever survives redaction: False`.
- Expected: run the check before redaction, delete the population copy before the first turn (the evidence alone is enough), and add an answer-key check.
- The committed run is not affected: its only calls are `ls`/`shasum` in the workspace and two Reads under `<workspace>`.

**F6 — `tools/record_judge_sessions.py:141, 174, 181, 105-110` — completeness.** `workspace.json` and `only_judgements_new` compare file names only, and `check()` copies the model from FIXTURE, not from the workspace. If the agent edits `model.orm.yaml` in the workspace, nothing detects it, although TS-R6 says the skill writes only its judgements file. This is a code reading, confirmed against the lines above.
- Expected: record SHA-256 before and after for every workspace file.

**F7 — `tests/test_judge_fact_types_skill.py` T8/T9 — completeness.** Mutations of the clone (`<scratch>/review-ts3/mutate.py`) that leave all 36 tests passing:
- an apply instruction in plain prose: "Then run `gnd evolve apply MODEL proposal.json` yourself.";
- R1's body flipped to `distinct`;
- the 90% line changed to 10%;
- `over_budget` removed from the eligible statuses.

T9 pins only the rule headings, and T8 scans only fenced code. Removing `over_budget` would make the CLI refuse ("group … has no verdict") on any over-budget evidence, and no test notices. These mutations are caught: the `truncated_groups` refusal removed, R1 seeded into orm-core, an absolute path seeded, the key flipped, a canary in turn-02, a `results.json` check set false, one changed byte in the vendored schema, a census row dropped (IL6), and fixture g3 at full overlap (T13).
- Expected: pin each rule's key clause (the verdict word, the 90%, the three eligible statuses), and add a plain-prose check that no sentence other than the "never" one names `evolve apply`.

**F8 — hygiene: `.gnd-planning/milestones/type-induction-skills/evidence/TS3/gate.txt:16,20,22` — anonymity.** This committed file contains absolute local paths with the user name and worktree name, `<worktree>/...`, from the install and doctor output.
- Repro: `git diff b4ef8cbf..51ec0a3a | grep -n '^+.*/Users/'`, which hits 3 lines, all in this file.
- TS1's and TS2's `gate.txt` have none. T17 does not cover it because it scans only `recording/`.
- Expected: redact these lines, for example to `<repo>`.

## Checked and found sound
- **Recording:** in `turn-*.jsonl` the agent ran `ls`/`shasum` in the workspace (a `python3` call was denied) and read `<workspace>/evidence.json` and `<workspace>/model.orm.yaml`. It read nothing outside the workspace, made no apply call, and wrote no file before turn 2. `evidence_sha256` (75c734f8…) equals the SHA-256 of the evidence the test rebuilds, and its `model_sha256` check matched `shasum` (adb36c4f…). The verdicts match the key. The rerun of `discover.txt`/`preview.txt` exits 0.
- **Manifest:** its `sources` digests match the current recorder, SKILL.md and the three fixture files byte for byte, so the recording is not stale.
- **Recorder logic:**
  - `passed()` precedence is correct (`(v==0 and v is not False) if _exit else v is True`), and `None` fails.
  - The break rule stops on a nonzero exit or a timeout (`code=None`), or once a file exists after turn ≥2.
  - Timeout output is decoded.
  - The leak check covers home, user name and keys.
  - `judgements_in` is fine for this run; it scans only the top level.
- **Decision rules against the CLI:**
  - R2's "rows − exact_repeats" equals the distinct pairs (`types.py:193`), and `overlap.pairs` counts distinct pairs.
  - The eligible statuses and the `of`-only-on-duplicate rule match `type_judgements.py`.
  - Customer mode works: `same_attribute` is still given, and where no origin exists R2 catches the re-seen attribute.
  - `over_budget` groups carry candidates.
  - The handoff command options exist.
- **Tests:**
  - All three in-scope test files pass in the clone (51 passed).
  - I ran all 51 test files that read `src/gnd/skills`, AGENTS.md or `.claude/skills`: 2203 passed and 2 failed. Both failures are in `test_rf7_structure.py` (lazy-import violations in `gnd.commands.*`), and they also fail at base b4ef8cbf, so they predate TS3. No pin site was missed.
  - The IL6 pin to 7818be1 is sound: dropping a census row fails 6 tests by name.
  - The schema sync case fails on a one-byte edit.
- **Anonymity:** no downstream application name appears anywhere in the diff.

## Hygiene
- I edited nothing in the worktree. `git status` in the worktree is clean.
- Everything I wrote is under `<scratch>/review-ts3/`: the `repo/` clone (restored to 51ec0a3a, plus a `.venv` symlink), the `numeric/`, `trunc/`, `nulls/`, `generic2/` and `popscan/` directories, the repro scripts, `runner/capped_gnd.py`, and `skill_tests.out`.
- `popscan.py` created and removed one empty `judge-evidence-*` directory in the system temporary directory.
- I ran no `claude` session and no paid model, called the recorder only with `--help`, and read no `.env`.
- The full-suite run used the clone's ROOT and pytest's own temporary directories.
