# Close review, reader 1: CLI evidence and judgement core (TS1, TS2)

Subject: `git diff b733b2a..3665e28f`, HEAD 3665e28f, branch claude/ts4-spec. I edited no repository file. All scratch work is under `close/r1/` in the scratchpad: copied fixtures, `run.sh`, `judge.sh`, `prev.sh`, `mut.py`, `drift.sh`, and an exported b733b2a source tree in `r1/base/src` used for the baseline runs.

**Verdict: approve-with-fixes.** I found no blocker or major problem. Stale, incomplete and contradicted verdicts are refused with exit 3 and nothing is written. Every judged proposal I rendered passed `gnd evolve preview --policy additive`, then applied and validated. Default outputs match the baseline byte for byte. I have four minor or nit findings: two value-leak gaps, one documentation claim that a test disproves, and one schema-pattern nit.

## What I checked (no finding)

- **Tests.** `uv run pytest -q tests/test_discover_type_evidence.py tests/test_discover_type_judgements.py tests/test_schema_sync.py`: 131 passed. `tests/test_rf1_layering.py`, `tests/test_rf6_query_policy.py` and `tests/test_rf6_index.py`: 71 passed.
- **Layering and ModelIndex.** `tools/gnd_layers.json` adds `gnd.discover.type_evidence` and `gnd.discover.type_judgements`, both as discover/lanes. The new modules do not iterate the raw model. `type_evidence.origins` uses `ModelIndex.for_model(...).iter_fact_types_shared()`.
- **Schema twins.** The two schemas in `src/gnd/` and their copies under `gnd-orm-core/references/` are byte-identical (checked with `cmp`).
- **Default drift (TS-R1, predicate 5).** I ran b733b2a source and HEAD source on the same inputs: fixtures round-two, multi-valued, the duplicates example and a derived ex4 that proposes. Families were the default set, `fact-type`, and `fact-type,uniqueness,mandatory`; `--min-support` was the default or 3; disclosure was unset or customer. Proposal, report and stderr were byte-identical. The report and stdout differ only in the output path the run itself was given.
- **`--type-evidence` neutrality (predicate 1).** The proposal and report are identical with and without `--type-evidence`, under unset, customer and internal modes.
- **Evidence values.** No population cell text appears in the evidence. Under unset mode the 4 attribute digests appear in the evidence and the report. Under customer, 0 appear in either, and `show_digests` is false.
- **Binding (TS-R3).** Each of these exits 3 with nothing written:
  - evidence reserialised to different bytes ("evidence_sha256 is not the digest");
  - a model changed by a later `evolve apply` (model_sha256);
  - a population with one extra row (population_sha256);
  - `--min-support 3` (min_support);
  - `--show-values`, and `GND_DISCLOSURE=internal` (show_values);
  - `GND_DISCLOSURE=customer` (show_digests).

  Every message names the key, never a value.
- **Coverage and contradiction (TS-R2).** Each of these exits 3 with nothing written:
  - a missing verdict, or a repeated one;
  - a `g02` group id (schema);
  - `of` naming the generic fact type itself, which is not a candidate;
  - `distinct` on g0, which was already induced (D4);
  - `many-to-many` on the multi-valued g0, already induced;
  - `functional` (schema enum);
  - `duplicate` in a shapes file;
  - `of` on a `skip`;
  - a `kind` mismatch.
- **Usage errors (exit 64).** Each of these is refused: judgement options without the fact-type family; judgements without `--type-evidence-in`; `--type-evidence-in` without any judgements file; `--type-evidence` together with `--type-evidence-in`; a reused path; the same file given for both kinds.
- **Free-text scan, default mode.** It catches the attribute name (`dim-k4p1`), its upper-case form, a value (`d0.`), and the attribute name in `judge.agent`. It correctly lets `dim-k4p1s` through, since a letter is adjacent. A non-breaking hyphen escapes it, which the docs disclose ("exact text only").
- **Free-text scan, customer mode.** It catches an attribute digest in lower or upper case. A 20-character prefix of a digest passes, which falls under the same disclosed exact-match limit.
- **Rendering and admission (TS-R4, predicate 2).** I ran preview, apply and validate, each exiting 0, on:
  - the duplicates example, including a duplicate whose signature does not match (`of` is `item_has_colour`);
  - the multi-valued example, including a many-to-many group with an exact repeat, which became a counterexample (support 36/37);
  - all four remaining multi-valued groups judged many-to-many;
  - a clash case that produced `item_has_attribute_induced_2_1` with reading "attribute 2_1".

  Every constraint is `induced`/`proposed`/`deontic` and carries `provenance.judgement`. Under customer, the provenance has no `induced_from`, and neither the proposal nor the report holds an attribute digest beyond those already in the base model.

## Findings

### F1 (minor): the judgements file name enters the proposal without the value scan

- **Where:** `src/gnd/discover/service.py:579` (`judged_from`), used in `_proposal_bytes` at about line 189.
- **Problem:** The proposal rationale gets "fact-type verdicts from `<judgements file basename>`". Rationales, `judge.agent` and `judge.skill` are all scanned for values; this name is not. So a value hidden under the current mode can reach the written proposal, and from there the evolution records, through the file name.
- **Reproduction:** Disclosure unset, no `--show-values`.
  ```
  ./run.sh $S/w1 $S/ex/duplicates
  cp ex/duplicates/duplicates.judgements.json w1/dim-k4p1.json
  ./judge.sh $S/w1 --duplicate-judgements dim-k4p1.json
  ```
  The run exits 0, and `grep -o 'verdicts from [^"]*' w1/p.json` prints `verdicts from dim-k4p1.json`. A rationale containing `dim-k4p1` is refused.
- **Context:** The population file name already appears in the same rationale; that predates this change.
- **Fix:** Name the kinds and their digests, which are already in `provenance.judgement`, instead of the basenames. Alternatively, run the basenames through `scan_free_text`.

### F2 (minor): the scan covers less than the docs say

- **Where:** `src/gnd/discover/service.py:561-563`; `docs/reference/discover.md:289-291`.
- **Problem:** The docs say each free text "is checked for the text of any attribute or value the population holds". The forbidden list holds only each group's attribute cell and value cells. Entity cells such as `I-00`, cells of non-generic fact types, and cells of redacted-attribute generics are not checked. TS-R5 itself only promises "raw attribute value", so the code meets the plan rule; the docs overstate it.
- **Reproduction:**
  ```
  python3 mut.py w1 ex/duplicates/duplicates.judgements.json duplicates \
    "d['verdicts'][3]['rationale']+=' item I-00'; d['judge']['agent']='agent I-07'"
  ```
  The run exits 0.
- **Impact:** Low. Rationale and agent text are not copied into any CLI output (I checked p.json and r.json), and the skills never read the population.
- **Fix:** Narrow the docs to "any attribute name or attribute value of the generic fact types' groups". Alternatively, extend `hidden` to the entity cells.

### F3 (minor): a judged `distinct` can repeat an existing reading, contrary to the docs

- **Where:** `src/gnd/discover/types.py:265-269`; `docs/reference/discover.md:267-269` ("so it never repeats an existing reading").
- **Problem:** The suffix is added only when the id clashes. If a reviewed fact type already carries the generated-style reading under a different id, a judged-distinct group gets a new id and the same reading.
- **Reproduction:** `ex3` is the duplicates example with `item_has_attribute_induced_0` renamed to the reading "{Item} has induced item_has_attribute attribute 2 {AttributeValue}".
  ```
  ./run.sh $S/w5 $S/ex3
  ```
  Then judge with the shipped verdicts, rationales replaced by "x", followed by `./prev.sh w5 apply`. Preview, apply and validate all exit 0. The applied model then has `item_has_attribute_induced_0` and `item_has_attribute_induced_2` with identical readings.
- **Note:** This is contrived; the reviewer would have had to write the generated text by hand.
- **Fix:** Also check the candidate reading against the model's readings, and suffix until it is free. Or weaken the doc's "never".

### F4 (nit): a trailing newline gets past the `judge.skill` pattern and into model provenance

- **Where:** `src/gnd/type-judgements.schema.json:18`.
- **Problem:** jsonschema uses `re.search`, and in Python regex `$` also matches just before a final `\n`.
- **Reproduction:**
  ```
  python3 mut.py w1 ex/duplicates/duplicates.judgements.json duplicates "d['judge']['skill']+='\n'"
  ```
  The run exits 0, and the proposal holds `"skill": "gnd-judge-fact-types\n"`.
- **Note:** The group pattern has the same flaw but is caught later by `_GROUP.fullmatch`, and a digest with a newline is caught by the binding check.
- **Fix:** Use `\z`-equivalent anchoring, i.e. `^...(?!\n)$`, or fullmatch the skill name in `type_judgements.read`.

### H1 (hypothesis, accepted by the docs): customer mode loses the D4 guard in later rounds

Under customer, no `induced_from` is written (D3). The next round therefore cannot refuse `distinct` on an attribute that was already induced, so the same attribute can be proposed again. The docs disclose this at `docs/reference/discover.md:282-283`, so I record it as a known limit rather than a defect. It might deserve a line in the skills telling the judge to fall back on pair overlap.
