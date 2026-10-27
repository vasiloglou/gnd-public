# Reader 3: protocol, authority, compatibility and privacy

**Reviewed digests.** I checked both files with `shasum -a 256` and both match:
- `evidence/plan-review-r1/ilp-learners-plan.md` = `6cb10d97…8e463`
- `evidence/plan-review-r1/phase-IL1-spec.md` = `59629173…b027`

Both are byte-identical to their `notes/` twins (`diff` is empty). I also read `README.md` (28 lines).

**Verdict: request-changes** within this lens. One finding is a blocking compatibility defect in the IL1 spec. Two are authority over-reads that should be fixed before the owner gate. The rest are hardening or completeness.

**Scope:**
- How the plan and spec follow start-milestone and process-phase.
- How owner authority is read and labelled.
- What is carried over from the induced-knowledge (IK) milestone.
- IL-R7 compatibility.
- Licences.
- Privacy of evidence and of the data a live run sends out.

I did not assess ASP, rule-set or AMIE semantics beyond what IL-R7 touches.

## Findings

- **R3-F1** (blocking, high): **The IL1 registry as specified changes the `--target` choices that the RF1 CLI goldens pin. That breaks IL1-C1 and IL-R7.**
  - **The spec.** Spec §6 lines 73–75 say `LEARNERS` is "sorted by target" and `EXPORT_TARGETS` is "targets with render is not None". Lines 85–87 say both CLI `choices=` come from these tuples and that "`--help` goldens are unchanged because the sets are unchanged".
  - **The source.** Today the choices are an ordered tuple `("popper", "neutral")`, in `src/gnd/commands/export.py:108` and `src/gnd/commands/checking.py:452`. The neutral export has no rendering (`src/gnd/export/ilp_service.py:161`, `rendering = render(neutral) if target == "popper" else {}`), so `neutral`'s natural `render` is `None`.
  - **The consequence.** As written, `EXPORT_TARGETS` loses `neutral`, so `gnd export ilp --target neutral` would exit 64. Even if it kept `neutral`, sorting gives `{neutral,popper}`. The goldens pin the current order `{popper,neutral}`.
  - **Reproduce:** `grep -rln "{popper,neutral}" tests/fixtures/rf1-pins/goldens`. It hits `cli-help/gnd_export_ilp.json`, `cli-exit/gnd_export_ilp.json` and the `gnd_import_ilp-rules.py31{1,3,4}.json` help and exit goldens.
  - **Repair:**
    - Make the order *equal* (not just the set) by declaring `LEARNERS` in insertion order `popper, neutral`, not sorted.
    - Define `EXPORT_TARGETS` as every target that can be exported, including `neutral` (for example, `render` returns `{}` for `neutral`). Do not define it by `render is not None`.
    - Add a T3 row asserting both tuples equal `("popper", "neutral")`.
    - Delete the "because the sets are unchanged" reasoning.

- **R3-F2** (hardening, high): **The install authority is read beyond the question the owner answered, and the prior decline is not recorded as superseded.**
  - **What the owner answered.** "Yes, one recorded run each" answered a question naming SWI-Prolog, clingo and Popper, installed "in a scratch environment" (plan lines 91–97).
  - **How the plan applies it.** It counts the answer for every adapter (D2, line 385). That includes a JVM and AMIE (IL4-C4, line 275), ILASP/FastLAS binaries (IL2-C4) and a scratch Python rule-set learner (IL3-C4).
  - **Installs that are not scratch.** IL1-D3's example (spec line 126) is "SWI-Prolog and clingo from a package manager". That is a host-wide install, which contradicts both IL-R2's "scratch environment outside the repository" (plan line 77) and the owner's own "scratch" wording.
  - **The superseded decline.** The carried row the plan relies on is IK `012-milestone-close.md:151`: "the owner's call (installing Popper was declined)". The decline was IK5-D13 (a), ruled on 2026-10-26 (`notes/phase-IK5-spec.md:403,514-537`). Plan §1 and the harvest table (lines 106–108) never say that the 2026-10-27 answer supersedes it.
  - **Repair.** In §1, cite IK5-D13 (a) and 012:151 as superseded by the 2026-10-27 answer, for one run per adapter. Then make D2 and IL1-D3 require:
    - installs confined to a scratch prefix, with no system package manager, no `sudo` and no global PATH or shell-profile edits; any host-wide install needs its own explicit owner yes naming it;
    - prebuilt binaries and jars treated as downloads, approved per gate with the upstream URL, filename, size and SHA-256;
    - the plan gate confirming that "each" covers the JVM, AMIE and ILASP installs, which were not named in the question.

- **R3-F3** (blocking, high): **The IL5 live run is not covered by the owner's answer.** It needs a separate selection of agent, credentials, cost and data egress.
  - **The plan.** IL5 (plan lines 53–56, 182–193, 285–286) runs an agent through `gnd.agents` with a "named agent and model", and D2 counts it as one of the authorized runs.
  - **The source.** `gnd.agents` launches the `claude` or `codex` CLIs and forwards `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, `CLAUDE_CODE_OAUTH_TOKEN` and the home and user variables (`src/gnd/agents.py:53-56,178-205`).
  - **The rules.** AGENTS.md requires "explicitly selected terminal-agent tools and credentials" and never sourcing a repository `.env`; CONTRIBUTING.md:39-41 says the same. An answer about installing Prolog and ASP tools selects no agent, model, credential source or spend, and does not approve sending data to a provider.
  - **Repair.** Add plan decision D8, owner-ruled at the IL5 gate:
    - the agent adapter and model id;
    - the credential source, imported by name from the documented trusted environment and never printed;
    - a cost or call ceiling;
    - that the prompt input is only the committed synthetic IK6 export;
    - the provider's terms on generated output.

    Until D8 is ruled, mark IL5-C3 as blocked.

- **R3-F4** (completeness, medium): **The author's interpretations are labelled as owner answers in the README and the decision table.**
  - **README.** Lines 13–17 list as "Owner answers": "Popper included", "never in CI" and "neural learners out". The owner selected the four families offered and said "Yes, one recorded run each". "Never in CI" and the inclusion of Popper are the plan's reading (plan line 94: "This plan reads that as …"). Neural learners were simply not offered.
  - **Decision table.** D1 (line 384) and D2 (line 385) carry an `(o)` status over whole rows that mix the owner's words with proposals. This conflicts with the plan's own tag rule (lines 7–8) and with start-milestone.md:106-108.
  - **Repair.** Quote the owner's words verbatim in the README and in D1/D2. Label "Popper included", "never in CI" and "neural out" as proposed, and ask for confirmation at the plan gate.

- **R3-F5** (hardening, medium): **D5 offers an option the protocol forbids, is now stale, and no review stop rule is declared.**
  - **The option.** D5 (line 388) offers "none before IL1". The four-reviewer plan bar is binding: process-phase/SKILL.md:34,139,220; process-milestone/SKILL.md:66; start-milestone/SKILL.md:134.
  - **Stale text.** §8 line 348 still says "instrument unselected", but the owner has since selected four local reviewer agents.
  - **No stop rule.** review-convergence.md:56-59 requires the round budget and stagnation criterion to be declared "before round two, in the artifact's own bytes". The plan declares neither.
  - **No approval record.** The plan does not say how its approval will be recorded. The IK precedent is a separate gate record binding digests (`induced-knowledge/001-plan-gate.md`), because the plan itself is never edited.
  - **Repair, in r2:**
    - record D5 as owner-selected on 2026-10-27, four local readers, over the two r1 digests above, with r2 bytes carrying no review opinion;
    - strike "none";
    - declare the round budget and stop rule;
    - state that approval will live in a `001-plan-gate.md` that binds the plan and spec SHA-256s.

- **R3-F6** (hardening, medium): **IL1 spec §4 binds only the six standing rules. It does not bind the plan's own §0 rules by name.**
  - **The contract.** spec-note-contract.md:38-44 asks for "each of the plan's section 0 rules … by name … or argued inapplicable". standing-rules.md:8-10 adds: "Silence on a rule is a review finding."
  - **The gap.** Spec §3 and §4 (lines 34–49) cover IL-R1, IL-R2, IL-R5 and IL-R7. They are silent on:
    - IL-R3 (one re-check);
    - IL-R4 (the learner's numbers are claims);
    - IL-R6 (real Popper output is untrusted input);
    - IK-R1 to IK-R12, notably IK-R10 and IK-R11 (privacy of evidence and of `provenance.induction` from real output) and IK-R12 (the 600 s / 16 MiB bounds).
  - **Repair.** Add one row per IL-R and IK-R rule to §4, each bound to the specific code path or argued inapplicable.

- **R3-F7** (hardening, medium): **The privacy control the plan cites does not reach this milestone, and no phase owns extending it.**
  - **The claim.** Plan §6 line 323 says the IK close's downstream-name and username checks "extend to this directory".
  - **The downstream-name check.** It is hard-rooted at `.gnd-planning/milestones/induced-knowledge` (`tests/test_ik_close.py:291-294`).
  - **The username check.** There is no username test. The IK username fix was a manual sanitization (CD1, 012:121).
  - **The gap in IL1.** No test row T1–T7 and no phase criterion owns the extension.
  - **Why it matters for live runs:**
    - Live runs produce stderr, tracebacks, virtual-environment paths and install commands, all of which carry absolute home paths.
    - `run_bounded_process` redacts only the values of the environment it is given (`src/gnd/process.py:277-285,351-352`).
    - Spec line 109 says "Relative paths only" with no check behind it.
  - **Repair.** Add an IL1 test T8 that scans `.gnd-planning/milestones/ilp-learners/**` for home-path and username patterns and for the downstream digests, with a negative control. Require evidence scripts to pass `HOME`, `USER` and `TMPDIR` into the bounded-process environment so redaction applies. Require install commands to be recorded with a `<scratch>` placeholder.

- **R3-F8** (hardening, medium): **The inputs to the IL2–IL5 live runs are not pinned to synthetic committed fixtures.**
  - **The gap.** Only IL1 names its input (the IK6 refunds export). IL4 exports "a population" (plan line 166). IL2-C4, IL3-C4 and IL4-C4 name none.
  - **Why it matters:**
    - The ILP export writes raw population values into the learner's input (`induced-knowledge/007-phase-IK5.md:205-206`).
    - Learned rules carry constants from that input.
    - IL6 commits those outputs (plan line 291).
    - IL5 sends the input to an external provider.
    - IK-R10 requires fixtures to be synthetic or anonymized.
  - **Repair.** Add an IL-R rule: every live run reads only the IK6 refunds example or a committed synthetic fixture under `tests/fixtures/ilp_learners/`, named in the phase spec, with its export digest recorded.

- **R3-F9** (hardening, medium): **IL-R5's licence rule is too narrow and runs too late.**
  - **Too narrow.** IL-R5 (line 80) stops a phase only if a licence "forbids the recorded evidence use". The risk row "A non-OSI licence | IL-R5; nothing bundled" (line 326) implies a broader control than the rule provides.
  - **Too late.** IL-R5 checks at the phase gate, but the licence is needed before any download.
  - **Not covered at all:**
    - academic-only, non-commercial or binary-only distributions;
    - registration or click-through terms; accepting terms needs the owner's explicit consent;
    - repositories with no licence;
    - LLM provider terms on output.
  - **Unverified.** I could not check the ILASP, FastLAS, AMIE or CORELS licences offline. They must be checked upstream.
  - **A smaller gap.** Plan line 322 promises a check of the wheel metadata, but spec T7 (line 141) checks only `pyproject.toml`.
  - **Repair:**
    - record the licence from a cited upstream URL with its date before any download;
    - stop for an owner ruling on anything that is not a permissive OSI licence, or that has a click-through or registration step;
    - never commit a learner binary or source;
    - extend T7 to the built wheel's `Requires-Dist`.

- **R3-F10** (hardening, medium): **The live-run "fix in the adapter" clause contradicts IL1's byte-identity predicate.**
  - **The conflict.** Spec lines 113–116 and plan IL1-C4 (lines 237–239) put a rendering fix in IL1's scope if Popper rejects the rendering. But IL1-C1, IL-R7 and spec §9 (line 151, "changes to any wire format" out of scope) require the Popper rendering and the IK5 export goldens to stay byte-identical. A rendering fix necessarily changes them.
  - **What IL-R7 requires.** IL-R7 allows a change only if "a phase spec names the change and its version bump".
  - **Repair.** State that a rendering fix found by the live run returns IL1 to its owner gate as a spec amendment. The amendment would name the golden changes, the regenerated files and whether `gnd-ilp-export/1` needs a version bump. The fix should not be absorbed silently into IL1 scope.

- **R3-F11** (completeness, low): **The "learner's claim" in the live-run record is mislabelled.**
  - **The issue.** The spec says the run record's `coverage` is "computed by evaluating the program in SWI over `bk.pl` (the learner's claim…)" (spec lines 104–107). It is computed by GND's own evidence script, not reported by Popper.
  - **Why it matters.** Labelled as the learner's claim, the re-check compares the script against GND, not Popper against GND. That weakens the IL-R4 reading of the evidence.
  - **Repair.** Have the record label the run record's coverage as script-derived. Keep Popper's own printed counts verbatim as the learner-reported figures.
