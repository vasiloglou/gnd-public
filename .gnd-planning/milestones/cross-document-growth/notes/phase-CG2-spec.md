# CG2 · Candidate discovery for one model

Ruled specification, 2026-11-28. Depends on the CG1 evidence representation in 9ffa5a89. The effective [plan](cross-document-growth-plan.md) §§0, 4–6, 8–10 and amendment §3 govern this phase. The source is [issue 339](https://github.com/vasiloglou/gnd-public/issues/339). The reporter measured the two large models. Those models are outside the acceptance corpus.

## Public result

Run `gnd consolidate candidates MODEL` to read a validated model and emit a JSON report to stdout. Default to 100,000 indexed items and 25,000 candidate comparisons. Accept nonnegative integer overrides, including zero. Usage and invalid models follow the normal CLI conventions. A budget stop returns an explicitly incomplete report with charged counts, the specific exhausted budget and any completed groups. Sorting by score descending then group ID makes output repeatable. This command only reads.

## Signals and identity

Count distinct typed instances observed for each entity across its roles in the inline samples. An entity with one observed instance yields a singleton demotion suggestion. Group facts by role-player multiset using the existing role_player_signature contract and independently by normalized reading, substituting a common slot only for a player whose declaration cites exactly one document. Keep other players identified. Use the existing placeholder grammar, including qualified roles. Compare object and fact labels within kind using normalized names and an indexed shared prefix or character n-gram. Require a similarity threshold for candidate pairs. Treat near names with incompatible players as suggestions and show both signatures. Group value types using explicit unit information where present and recognized lexical unit or count qualifiers with the same primitive. Counted nouns require a count expression; arbitrary shared suffixes cannot establish a unit or count.

Every result carries its signal, member kind, sorted root-owned IDs, score, member evidence and stable group ID. Derive the ID from signal, kind and IDs using canonical JSON SHA-256. Derive evidence identity separately from semantic values, role signatures and sorted origin spans. Charge emitted evidence and every indexed sample or declaration, and charge candidate comparisons before examining them. Avoid materializing a quadratic candidate list. Include-owned definitions may supply context but cannot be offered as mutation targets. Empty inputs with valid model structure produce zero groups.

## Verification and boundary

Run the command through the normal CLI entry point. For each signal construct a positive and negative control. Shuffle declarations and span lists, rename identifiers, add a new supporting document, exercise disjoint and shared role players, one item below and exactly at each measured budget. Assert read-only model bytes, group identity, evidence changes, the terminal reason and charged work. Run the public CLI surface, layer, dynamic-query and component guards for any new module. CG3 owns decisions, proposals, mutations, recovery and the threshold loop.
