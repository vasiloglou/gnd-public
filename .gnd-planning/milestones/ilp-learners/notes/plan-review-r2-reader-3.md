# Round 2 — Reader 3: protocol, authority, compatibility and privacy

**Digests matched?** Yes, both:
- plan r2 is `e0668e30…3bb9`;
- IL1 spec r2 is `4a06f583…5af8`.

Both are byte-identical to their `notes/` twins (`cmp` printed nothing). I read the whole of `README.md` (45 lines, SHA-256 `d84545fa…6359`).

**Verdict: approve-with-fixes.**

**Scope:** whether my round-1 blocking findings R3-F1 and R3-F3 are resolved, whether the R3-F2 and R3-F4 authority repairs are honest, a privacy scan of the milestone directory, and defects that r2's own `(p1)` text introduced. I raise nothing about text r2 did not change.

**Privacy scan:** clean. I grepped the whole milestone directory (including `evidence/` and `manifest.json`) for home roots, `~/`, the local username, scratch and tmp roots, and the two downstream names. There were 0 hits.

## Round-1 blockers

| Finding | Status | Evidence |
|---|---|---|
| R3-F1: the registry would change the pinned `--target` choices and their order | **resolved** | **Order:** the registry is in declaration order (`popper`, `neutral`, later targets appended): plan:195–196, spec:133. This matches `commands/export.py:108`, `commands/checking.py:452` and the order of both schema enums (`ilp.schema.json:254–258`, `ilp-import.schema.json:30–34`). **`neutral` stays exportable:** `exports=True`, `render=None` means "no files beyond neutral.json" (spec:128–142). The `render is not None` definition is gone. **Literal choices kept:** the command modules keep literal `choices=`, so there is no RF5 edge (spec:157–168). **Tests:** T2 asserts both tuples equal `("popper", "neutral")` (spec:313). T1b keeps the RF1 help and exit goldens byte-identical (spec:312). The "because the sets are unchanged" reasoning is deleted. |
| R3-F3: the IL5 live run needs its own agent, credential, cost and egress ruling | **resolved** | **What the owner's answer does not cover:** §1 says it excludes the IL5 run, citing credentials and data going to a provider (plan:159–161). **D8 names every item:** adapter, model id, credential source imported by name and never printed, a call or cost ceiling, prompt limited to the synthetic IK6 export, and provider terms (plan:629). The owner's words "D8 at the IL5 gate" are quoted. **IL5-C3 is blocked until D8** (plan:91–92, 347–349, 462–463). The risk row is plan:531. **Prompt input** is pinned by IL-R8 (plan:129). |
| R3-F2 (hardening, authority repair): install reach and the superseded decline | **resolved, honest** | **Supersession:** IK5-D13 (a) and the 012 "installing Popper was declined" row are cited as superseded (plan:156–158). **Reach:** the plan reads the reach of "D2 yes (scratch prefix, downloads approved per gate)" as covering the JVM, AMIE, ILASP/FastLAS and rule-set installs (plan:152–155). That is not an over-read: the disposition's D2 question named exactly those (disposition D2 row), and the owner answered "D2 yes". **Scratch-prefix limits:** no package manager, no `sudo`, no profile edits, and downloads with URL, name, size and SHA-256. These are in IL-R2 (plan:123) and IL1-D3 (spec:300). The host-wide "from a package manager" example is gone. |
| R3-F4 (completeness, authority repair): owner words versus proposals | **resolved, honest** | **README:** quotes the selection, "Yes, one recorded run each" and the round-1 ruling verbatim (README:20–28). The quoted ruling matches the owner's words; only the trailing "Write r2." is omitted, harmlessly. Neural learners are moved to "Still proposed" (README:34–37). **Decision rows:** D1, D2 and D5 now quote or label precisely, and D1 marks "Leaving neural learners out is proposed" (plan:622–626). **Tag rules:** the `(o)` and `(p1)` rules are stated (plan:17–23). **Nit:** README:24 sits under "quoted:" but is an unquoted option label; this is harmless. |

## Self-inflicted findings (r2-introduced only)

- **R3-2-F1** (hardening, medium): **r2 binds the CLI choices and both schema enums to the wrong registry tuples once IL4 and IL5 land.**
  - **The claim.** Spec:135 defines `IMPORT_TARGETS` as "every target". Spec:162–165 and T2 (spec:313) pin both `target` enums to `IMPORT_TARGETS`, including the *export* wire `ilp.schema.json`. Plan:128 and plan:383 pin "both CLI `choices=` … equal the registry".
  - **Why it breaks:**
    - IL4's `amie` imports through the new `gnd import mined-rules`, not `ilp-rules` (plan:294–295). Under the current definition it would land in `ilp-rules --target` choices.
    - The export schema's enum would admit targets with `exports=False`.
    - The `exports` and `contract` fields that cause this are themselves r2 (plan:203, 206).
  - **Reproduce:** read spec:133–135 and plan:203–206 against plan:290–297.
  - **Repair:**
    - define `IMPORT_TARGETS` as the entries that `ilp-rules` accepts (`contract == "labelled-clauses"`);
    - pin `ilp.schema.json` to `EXPORT_TARGETS` and `ilp-import.schema.json` to `IMPORT_TARGETS`;
    - state `llm`'s `exports` value in plan §2.

- **R3-2-F2** (hardening, low): **The new D8 block has no outcome for a decline.**
  - **The claim.** IL5-C3 is blocked until D8 (plan:462–463). But IL6-C1 and completion predicate 6 replay "every adapter's committed run of record" (plan:93–96, 467–469). If D8 is ruled "no run", the milestone cannot close, and nothing says what IL6 shows.
  - **Repair:** state that a declined D8 leaves IL5 with fixture-only evidence, and that its IL6 row shows the outcome "not run (D8)".

- **R3-2-F3** (completeness, low): **IL-R1's wheel check is weakened in the spec.**
  - **The claim.** Plan IL-R1 and its risk row require a check of "the built wheel's `Requires-Dist`" (plan:122, 524). Spec IL-R1 and T7 instead read `importlib.metadata.requires("gnd")` from the installed (editable) distribution (spec:76, 323). That restates `pyproject.toml`; it does not test a built wheel.
  - **Repair:** either build the wheel into a temporary directory and read its `METADATA`, or relabel the plan's control as installed metadata.

- **R3-2-F4** (hardening, low): **IL-R10's "so redaction applies" is not true for every value.**
  - **The claim.** IL-R10 says scripts pass `HOME`, `USER` and `TMPDIR` "so redaction applies" (plan:131, spec:229). But `_sensitive_values` drops env values shorter than 4 bytes (`src/gnd/process.py:277–285`). A short username is never redacted.
  - **A second gap.** Redaction covers only the child's stdout and stderr (`process.py:351–352`), not the script's own `outcome.json` argv.
  - **Repair:**
    - say that T8 is the backstop;
    - have the script substitute `<scratch>` and `<home>` itself in every file it writes;
    - give T8 a fixed rule for usernames shorter than 4 characters, so it neither misses one nor produces false positives.

- **R3-2-F5** (hardening, low): **IL4's `--labels` change is not listed as a compatibility surface.**
  - **The claim.** The r2 IL4 command shape makes `--labels` and `--population` mutually exclusive, with the target deciding which is required (plan:290–293). Today `--labels` is `required=True` (`src/gnd/commands/export.py:106`). The change moves the existing `gnd export ilp` help golden, and possibly the exit golden for a missing `--labels` on `popper` and `neutral`.
  - **Where it is missing.** Plan §5 lists only the new `--target` value and `mined-rules` (plan:509–514).
  - **Repair:** name this in §5 and IL-R7. Require IL4 to keep the missing-`--labels` exit for `popper` and `neutral` unchanged, or to list the golden it moves.
