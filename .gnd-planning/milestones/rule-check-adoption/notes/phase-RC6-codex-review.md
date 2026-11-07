# RC6 documentation review (Codex), retained verbatim

- Instrument: one reviewer in a different tool. One reviewer is one reviewer.
- Command: `codex exec --ephemeral --model gpt-6-sol --config model_reasoning_effort="xhigh" --sandbox read-only --color never --skip-git-repo-check -`, prompt on stdin (codex-cli 0.163.0), 106,437 tokens, exit 0.
- Reviewed bytes: `git diff 4232d233 8da3b3f7 -- docs src tools zensical.toml`, read against the code at 8da3b3f7.
- The reviewer ran in a read-only sandbox. The output below is unedited and contains no local path; the trailing "codex exit=0" line is the driver's.

## Reviewer output (verbatim)

```text
DISPOSITION: revise

ID: D1
SEVERITY: high
LOCATION: docs/how-to/adopt-rules-with-a-baseline.md:10
QUOTE: This how-to sets the gate up so that it fails only for what a change adds.
PROBLEM: A baseline check also exits 2 for a vacuous head rule unless allowed, or 4 for an unchecked must-hold rule in either run, even with no new violation (`checker/_reports.py:157-165`).
FIX: Say it fails for new must-hold violations while still refusing vacuous or undecidable checks as described below.

ID: D2
SEVERITY: medium
LOCATION: docs/how-to/adopt-rules-with-a-baseline.md:21
QUOTE: The component graph of the change under review.
PROBLEM: The SVG omits `admin` and `cache`, plus four head imports: `api → cache`, `admin → api`, `metrics → db`, and `legacy_ui → api`. It is a partial graph.
FIX: Draw the omitted nodes and imports, or call the figure a selected view of the graph.

ID: D3
SEVERITY: medium
LOCATION: docs/how-to/adopt-rules-with-a-baseline.md:21
QUOTE: its two edges are resolved.
PROBLEM: `reports → billing` remains in `head.population.yaml:21`. Both rows are *resolved as loop violations* because the reverse import was removed; both import edges were not removed.
FIX: Say both formerly offending rows are resolved, while `reports → billing` remains.

ID: D4
SEVERITY: low
LOCATION: docs/how-to/adopt-rules-with-a-baseline.md:109
QUOTE: The loop rule lists every edge inside every
PROBLEM: The text output just shown gives an aggregate message and lists no edge rows (`output.py:168-189`). The rows appear in JSON `offending_facts`, which the page shows later.
FIX: Identify JSON `offending_facts` as the place that lists the edges.

ID: D5
SEVERITY: high
LOCATION: docs/how-to/adopt-rules-with-a-baseline.md:249
QUOTE: A real violation, or a must-hold rule that could not be
PROBLEM: With `--baseline`, standing must-hold violations do not fail the run. The page’s own fixed example exits 0 with two `[fail, standing]` verdicts when `--allow-vacuous` is on. Advisory warnings also do not determine the exit band.
FIX: Say a **new must-hold** violation or an unchecked must-hold rule still prevents acceptance.

ID: D6
SEVERITY: medium
LOCATION: docs/how-to/adopt-rules-with-a-baseline.md:258
QUOTE: gnd check model.orm.yaml head.population.yaml --baseline main.population.yaml --allow-vacuous --format json
PROBLEM: This block has no `gnd-run` marker, so the tutorial runner does not execute it. Following the copied example literally also fails: its files are under `catalog/`, and it has `base.population.yaml`, not `main.population.yaml`.
FIX: Mark it explicitly as a path template, or make it an executable example command and add it to the runner.

ID: D7
SEVERITY: medium
LOCATION: docs/how-to/adopt-rules-with-a-baseline.md:265
QUOTE: | 2 | a must-hold rule had nothing to judge (without `--allow-vacuous`) |
PROBLEM: `CheckReport.has_vacuous` checks every verdict regardless of modality (`checker/_reports.py:115-117`); an advisory vacuous rule can also produce 2. With the displayed CI command’s `--allow-vacuous`, a 2 is converted to 0.
FIX: Say “a rule is vacuous, when `--allow-vacuous` is absent.”

ID: D8
SEVERITY: low
LOCATION: docs/how-to/adopt-rules-with-a-baseline.md:268
QUOTE: | 64 | the flags conflict |
PROBLEM: Other CLI usage errors also exit 64; `gnd check MODEL --bogus` does so. The table also omits the implemented internal-error exit 70.
FIX: Describe 64 as a usage error, including flag conflicts, and include 70.

ID: D9
SEVERITY: low
LOCATION: docs/reference/rule-check-report.md:56
QUOTE: Adding a loop elsewhere does not move an existing loop's rows,
PROBLEM: `acyclic_extent` emits rows in input-pair order (`semantic_spec.py:1455-1479`). Inserting a new loop earlier can shift existing rows’ array positions. Their key values remain stable.
FIX: Say adding a separate loop does not change the existing loop’s row values; matching ignores row order.

ID: D10
SEVERITY: low
LOCATION: docs/reference/rule-check-report.md:77
QUOTE: | `undecided` | verdicts unchecked in the head or the base, of either modality |
PROBLEM: `baseline.compare` counts distinct `constraint_ref` values (`baseline.py:93-104`). One rule unchecked in both runs contributes 1, not two unchecked verdicts.
FIX: Say “distinct rule references unchecked in either run, of either modality.”

ID: D11
SEVERITY: low
LOCATION: docs/reference/rule-check-report.md:86
QUOTE: Precedence 1 > 4 > 2 > 0, as for every check.
PROBLEM: This omits exit 3, which returns from model or population loading before verdict evaluation; the code documents the full order as 3 > 1 > 4 > 2 > 0 (`checker/_reports.py:141-145`).
FIX: Say this is the precedence **after successful loading**, or include 3 and explain its earlier return.

ID: D12
SEVERITY: medium
LOCATION: docs/reference/rule-check-report.md:107
QUOTE: Under `--allow-vacuous`, a last line says how
PROBLEM: `output.print_vacuous_acceptance` prints “vacuous accepted” whenever the flag and a vacuous verdict are present, even when the run exits 1. `gnd check` on the shipped head with `--allow-vacuous` demonstrates that output and exit 1 (`output.py:208-212`).
FIX: Make the text emitter say “accepted” only at exit 0, or document the current line without claiming acceptance.

ID: D13
SEVERITY: medium
LOCATION: docs/reference/cli.md:22
QUOTE: | `gnd check MODEL POPULATION --rule-ids --format json` | Report version 15: each verdict names its rule's declared id and remedy ([rule-check report](rule-check-report.md)) |
PROBLEM: Both fields are optional. A rule without an id gets a positional `address`, and one without a remedy gets `null` (`address.py:59-68`; `payloads.py:414-427`).
FIX: Say the report uses declared ids and remedies when present, with positional and `null` fallbacks.

ID: D14
SEVERITY: medium
LOCATION: docs/reference/cli.md:23
QUOTE: | `gnd check MODEL POPULATION --baseline BASE --format json` | Marks each violation new or standing against BASE; fails only for new ones ([how-to](../how-to/adopt-rules-with-a-baseline.md)) |
PROBLEM: No new violations can still yield exit 2 for head vacuity or 4 for an unchecked must-hold rule in either run (`checker/_reports.py:157-165`). Only *exit 1* is restricted to new must-hold violations.
FIX: Say “exit 1 is reserved for new must-hold violations; vacuity and undecidable checks retain their own exits.”

ID: D15
SEVERITY: low
LOCATION: docs/how-to/adopt-rules-with-a-baseline.md:55
QUOTE: The facts come from a scanner, not from a person or an agent, and the
PROBLEM: The shipped example contains static YAML and no scanner that produces it. `source: tool-output` and `producer` record a provenance claim; the loader does not verify that a scanner ran (`population-format.md:45-46`).
FIX: Present the scanner as the example’s scenario and describe the header as a provenance label.

CONFIRMED:
- The marked tutorial blocks’ expected exits and shown output agree with the example and the runner’s comparison logic.
- The example’s baseline counts are `new=2`, `standing=4`, `resolved=2`; the fixed population has `new=0`.
- Baseline keys combine the rule address with a canonical offending row; numeric `1` and `1.0` match.
- `novelty` and `row_novelty` are populated for failing or warning verdicts under a baseline, with row marks aligned to `offending_facts`.
- Version 15 reports `address`, `addressing`, and `remedy` with the documented positional and null fallbacks.
- The listed flag conflicts exit 64 before model loading.
- The two named refusals use the documented rule ids and occur before population loading.
- `--allow-vacuous` changes only a computed exit 2 to 0; new must-hold failures and unchecked must-hold rules retain precedence.
- Baseline runs, and vacuous runs accepted by `--allow-vacuous`, receive uncertified assurance.
- `gnd coverage` refuses version-15 check reports.
codex exit=0
```

## Triage (driving agent, 2026-11-06)

Each finding was checked against the code it cites; all fifteen are
accurate. All are documentation corrections, applied in the pages; the
tutorial runner, the style test, the strict build and the link check pass
after them.

| ID | Disposition |
|---|---|
| D1, D5, D14 | fixed: the pages say exit 1 is for new must-hold violations, while vacuous (2) and undecided (4) rules keep their exits |
| D2, D3 | fixed: the figure and its alt text call it a selected view, list what is left out, and say `reports → billing` remains while both loop rows are resolved |
| D4 | fixed: the edges are listed in the JSON report, shown next |
| D6 | fixed: the CI command is a placeholder template (`text`, not a runnable block) |
| D7, D8, D11 | fixed: exit 2 for a vacuous rule of either modality; 64 is any usage error; 70 added; precedence stated after loading |
| D9, D10 | fixed: row values (not positions) are stable; `undecided` counts distinct rules |
| D12 | documented: the closing line counts the vacuous rules the option covers and is printed even when the run fails for another reason. Whether to print it only when the option changed the exit code is a behaviour change to RC4's approved text (D3), left as an open question for the owner |
| D13 | fixed: ids and remedies when present, else position and `null` |
| D15 | fixed: the scanner is the scenario; `source` and `producer` are labels GND does not verify |

The corrected pages were not re-reviewed.
