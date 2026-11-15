# LI3 name diagnostics

Status: implementable once the delegated corpus and measurement gate is recorded (2026-11-15).

## Provenance

Literature-identity plan r3, 001 owner gate D4 and LI2 composition
resolution ([LI2 record](../010-phase-LI2.md)). Sections 0, 2, 4 LI3, 5, 6, 7, 8 and 9 are effective.
The phase uses example scope. The diagnostic and its answer labels
are author-controlled synthetic data assembled for this finite test.

## Obligations

| Source | Obligation | Evidence |
|---|---|---|
| Plan LI3 N1 | VAMPnet/VampNet and WhAM/WHAM are homonyms, normalizing flow/normalizing flows are synonyms, and $PINN/PINNs are a family signal | T1 checks all four with original spellings |
| N2 | Flow matching across fields produces no homonym at or above T | T2 uses a shared introducing work and disjoint contexts |
| N3 | Declare and bind the input, sample, labeller, strata, denominators and budget before measurement. Use 300 or more occurrences, count the full output below 100, and treat strata below 20 as unmeasured | T3 and premeasurement record |
| N4 | Refuse malformed input at exit 3 and test a bound on occurrences and candidates | T4 and T5 |
| Plan §0 | One policy walk, bounded reads, validation order, documented format and measurement | Standing rules below |
| Plan §2 and §4 | Example report with one kind, threshold and score, unresolved proposals only | T1, T6 |
| Plan §§5–7 | Document example route, use original context, no automatic application or discover family | README, T6 |
| Plan §9 | Diagnostics tests, N4 tests, N3 measurement, guards and lint | Gate table |
| 001 D4, pending decisions | Example only. Choose T, k and budget before output | Decision table |
| LI1, LI2 | Preserve original labels, respect unresolved placeholders, retain dormant coverage stage and existing resolution readers | T6 plus affected LI1/LI2 tests |
| Plan §6 | Meaning stays with reviewers, avoid silent coercion and avoid copying public works | T1, T4 and synthetic corpus |

## Standing rules

Read a capped buffer before decoding, use strict JSON with duplicate-key and
nesting checks, then validate the full input shape before classifying. T4
covers parse and shape failures. Bound computation with a predeclared pair
ceiling and short capped text, and exercise it at the layer that enumerates
pairs in T5. A single classifier encodes the precedence homonym, family,
synonym over all pairs. The example README owns the input and output
contract and cites the composition reference for resolution semantics.
Measure precision controls against a pinned independently authored synthetic
answer ledger. The example-only surface does not introduce runtime model
queries, a constraint family, or packaged skill pins.

## Goal

Generate candidates for review using the input's names and contexts, returning
exit 0 for a report and exit 3 for a malformed or over-budget input. A
candidate carries an unresolved resolution proposal for a reviewer. The
tool writes its report to stdout and leaves the sources intact.

## Design

| Capability | Search and result | Decision |
|---|---|---|
| Name signals | `name diagnostics normalization` and `near miss string distance`. The witness near-miss path normalizes values for one derivation blocker | New example classifier. The blocker-specific algorithm lacks introducing-work evidence, contexts and family matching |
| Bounded JSON | Literature assurance report has a bounded byte reader and JSON limits. Composition's code reads trusted model and sidecar references | Reuse the bounded standalone example reader as far as its shape allows. Keep the resolution wire defined in the composition reference |
| Measurement | Assurance report has stage floors. N3 samples candidate kinds from a prelabelled corpus | New offline measurement over the report, with expected labels separate |

Add `name_diagnostics.py` under the literature example. The CLI
`python -m gnd.examples.literature.name_diagnostics INPUT` writes exactly one
JSON object to stdout. Its proposed module surface is
`diagnose(data: Any) -> dict` and `main(argv: list[str] | None = None) -> int`.
Add the named case corpus, measurement input, separate answer ledger and
README, plus a focused test module and component index entry.

The closed input is a `literature-name-occurrences/1` document with
`occurrences`. Each row has `id`, `work`, `contexts` (nonempty distinct string
ids), `introducing_works` (possibly empty distinct strings), a composition
`key` (source, object_type, string value), `evidence` (one LI2 coordinate
without the key index) and `population_sha256`. IDs are unique. Multiple
mentions of a key may be represented, with deterministic deduplication of a
proposed key pair. At most 500 occurrences and 8,000 emitted candidates, values up to 96 characters,
lists capped at 8, lexical identifiers capped at 64, and the existing
4 MiB read cap. A pair needs two distinct source keys of one type.
Canonical output order uses the input ids. Synthetic fixture rows cite
synthetic source bytes and primary coordinates.

Apply NFC and casefold for text equality. Words reduce to letters and
digits with a single final plural s removed when the remaining token has at
least four characters. Original spelling is kept in the output. Compare
only distinct works for family recurrence. A homonym score of 1.0 requires
folded equality with disjoint contexts, or a case variant of a compact name
with acronym casing. Shared introducing works suppress homonym. Family
requires a shared token of at least four characters, k distinct works with
the token, and no introducing assertion for the token. A synonym requires
overlapping contexts and original folded values within one insertion,
deletion or substitution. Family and synonym scores are fixed at 0.9 and
0.85 respectively. Threshold T applies to every kind. All three are signals
for human inspection.

Output is `literature-name-diagnostics/1`, with `exit_code`, `input_sha256`,
`threshold`, `family_minimum_works`, `candidates` and `reason`. Every
candidate carries its two occurrence IDs, kind, score and one LI2
`unresolved` decision, with two copied coordinates, population digest
bindings and two unique generated placeholders. Originals remain intact.
Validation order is input bytes, schema and cap limits, per-row consistency,
candidate generation and closed report serialization.

## Decisions

| ID | Decision | Basis |
|---|---|---|
| D1 | T = 0.8 and k = 4 | Both published controls can be reproduced before inspecting the measurement output |
| D2 | At most 1/5 false discoveries in each measured category | Chosen before measurement for these bounded synthetic cases |
| D3 | Sample 100 across strata, at least 20 each if available. Allocate the rest by proportional largest remainder after the floors. Draw uniformly within each stratum with seed 193. Below 100 take a census, and strata below 20 remain unmeasured | Resolves the plan's uniform and stratified language as uniform within each stratum |
| D4 | Corpus-first, label design uses the scenario's authored meanings and semantic relationships. Keep observations and label data separate | Structured interchange, intentional near misses and fixed issuer/provenance |
| D5 | No spec panel. One Claude Code phase-diff review on stdin | Explicit milestone delegation |

## Tests and verification

| Test | Expected result |
|---|---|
| T1 four named pairs and precedence | report exits 0 with exact N1 kinds |
| T2 flow matching controls | absence of homonym at threshold, and disjoint-context control without shared work does emit |
| T3 preregistered measurement and controls | named input digest, each denominator, false positives and fraction. Oracle scores at budget, known wrong outputs exceed budget |
| T4 hostile bytes, types, unknown fields, coordinates and duplicates | exit 3 without traceback or partial candidates |
| T5 500 inputs and worst relevant pair generation under 10 seconds | measurable cap and candidate ceiling |
| T6 candidate serialization | unresolved only, exact source coordinates and digests, distinct placeholders, no file changes |
| Structure, lint, component | project hook selection plus index check against phase base |
| Broad lanes | explicit owner cadence |

## Scope

Records the synthetic measurement. A discover family, applying decisions,
authority over meaning, changes to existing LI2 decisions, and successor
work are outside this phase.

## Size

Approximately 220 lines for input and classifier, 120 lines for corpus
and measurement tooling and 130 lines for the focused tests.

## Approval instrument

Review the authored corpus stories, expected exits and N1/N2 outcomes
before implementing. Commit the synthetic mixture and answer ledger and
bind their digests in the corpus and premeasurement record. Record each
decision as a delegated ruling after the implementability sweep.

## Implementability sweep

Occurrence coordinates and digests are independently available from
sources. The classifier needs no approved decision to generate an unresolved
proposal. The first four named pairs can be constructed from the pinned
LI1 examples and synthetic occurrence contexts. Inputs for the measurement
assign meanings independently of the detector and can supply both
true and false candidates in every stratum. The pair bound is finite
and T5 can test its upper end. Report and CLI carry no shared writer.
