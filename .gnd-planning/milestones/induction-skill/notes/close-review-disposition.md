# Close review -- disposition

2026-11-26. Instrument: four local reviewer agents (plan D13 (o): "use four
local reviewer agents for the plan and close review, as in the
induced-knowledge milestone"). The selection names the instrument only.

## Subject and limits

The four readers started with fresh context, each with the common
[brief](close-review-brief.md.snapshot) and a different lens. Each verified the
four digests, made its own clean clone of candidate `9b69ca5f`, and wrote only
in its own scratch folder. They ran concurrently as local model agents, not as
humans or a provider panel. No paid tool, credential or network beyond `uv sync`
was used; reader 3 read issues #318 and #319 with `gh` (read-only). Every
reader returned **APPROVE_WITH_FIXES**.

| Reader | Lens | Report |
|---|---|---|
| 1 | completion predicates and their evidence | [reader 1](close-review-reader-1.md) |
| 2 | the code bytes that carried no review opinion | [reader 2](close-review-reader-2.md) |
| 3 | the sweep, plan amendments, protocol, authority and privacy | [reader 3](close-review-reader-3.md) |
| 4 | the business page against its recordings | [reader 4](close-review-reader-4.md) |

The repairs below were made after the review. **They carry no review opinion**;
no second round was run.

## Dispositions

| Id | Class | Disposition | Where |
|---|---|---|---|
| R1-F1 | completeness | fixed: the census half of the IS1 red control never existed | plan §11 A4; sweep |
| R1-F2 | completeness | fixed: a README beside the recordings lists all nine runs and why three did not meet a check | `c59dc769` |
| R1-F3 | completeness | fixed: the email scan covers `refunds/skill-sessions`, as IS2-C1 asked | `c59dc769` |
| R1-F4 | hardening | carried | [#318 comment](https://github.com/vasiloglou/gnd-public/issues/318#issuecomment-7192877526) |
| R1-F5 | hardening | carried (already IS2-Q1; the reproduction is cited) | #318 comment |
| R1-F6 | hardening | fixed: extra-free groups run on the bare wheel | `1c4bc454`; plan §11 A2 |
| R1-F7 | completeness | fixed: the page says a replay shows the first line of each result | `c59dc769` |
| R2-F1 | completeness | fixed: component index regenerated | `1c4bc454` |
| R2-F2 | hardening | fixed, as R1-F6 | `1c4bc454` |
| R2-F3 | completeness | fixed: `results.json` records the extras and each pass | `1c4bc454` |
| R2-F4 | hardening | carried: the U+2028 class in the sibling recorders | #318 comment |
| R3-F1 | blocking until measured | fixed: IS2-Q2 is closed on the close record's measurement | close record |
| R3-F2 | completeness | fixed: the neutral export is recorded, not shown | sweep |
| R3-F3 | completeness | fixed: record 002's deferred refactor (IS1-Q3) has its target | sweep |
| R3-F4 | completeness | fixed: the missing IS1 round-2 cases are on #318 | #318 comment |
| R3-F5 | completeness | fixed: IS1-Q4 retired with its own reason | sweep |
| R3-F6 | hardening | carried to the owner: `1cbbc18d` is on GitHub through both pushed branches | sweep (IS2-Q4) |
| R3-F7 | hardening | fixed: the owner's answer is quoted whole with its question | [owner-statements.txt](../evidence/close/owner-statements.txt) |
| R3-F8 | completeness | fixed: every carried row names its next owner; stated limitations retired | sweep |
| R3-F9 | completeness | fixed: the paid call before any gate record is a refuted control | sweep |
| R3-F10 | completeness | fixed: the unmeasured departures are folded into the Haiku row | sweep |
| R3-F11 | hardening | fixed: the USD 10 ceiling is the author's, under the owner's D11 approval | sweep; close record |
| R3-F12 | hardening | fixed: A1 names the run of record and the shipped rendering | plan §11 A1 |
| R3-F13 | completeness | fixed: "dispositions each of them" | plan §11 |
| R4-F1 | hardening | fixed by Fable: the refused commands printed an exit status, ran a loop or an inline Python script, or used `command -v` | `c59dc769` |
| R4-F2 | hardening | fixed on the page; the keep rule's `&&` case carried | `c59dc769`; #318 comment |
| R4-F3 | completeness | fixed: the page says three of nine did not follow the skill fully | `c59dc769` |
| R4-F4 | hardening | fixed: the second IS-R7 exception is recorded | plan §11 A3 |
| R4-F5 | hardening | fixed, as R1-F7 | `c59dc769` |
| R4-F6 | hardening | carried: the prose rule skips tables and alt text | #318 comment |
| R4-F7 | completeness | fixed: the page says the example's README states the rule | `c59dc769` |

## Found by the close's own gates, after the review

- **The wheel cap, twice more.** The full default lane at `4e1ae32c` failed
  eleven cases in `tests/test_pyrel_applications_install.py`:
  `tools/accept_pyrel_applications_install.py` still capped the wheel at
  12 MiB, as did `tests/test_release_preparation.py`. Both are copies of the
  budget the owner raised at C2; fixed in `bfc2495e`.
- **`gnd diff` needs the `synth` extra without saying so.** The bare-wheel pass
  of the repaired installed check stopped at
  `docs/how-to/share-an-ossie-ontology.md`: `gnd diff` synthesizes populations
  by default, and on an install without the extra it ends with an internal
  error naming the extra. The defect is on main (the old check stopped earlier,
  at the guarded-rules chapter, so it never reached this page) and outside this
  milestone. Carried to the owner as a proposed issue.
