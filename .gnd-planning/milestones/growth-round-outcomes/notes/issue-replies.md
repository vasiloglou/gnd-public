# Draft replies to #227 and #228 (GO5-C4)

Drafted 2026-11-23 for the owner to post. Nothing here is posted by an agent.
Each reply says what is on `main` and what is not released. Before posting,
replace "the GO2–GO5 pull request" with its link and confirm it has merged.

## #228 (`gnd evolve` parses each model text many times)

> Fixed on `main` by growth-round-outcomes GO1 (merged): one
> `gnd evolve preview` or `gnd evolve apply` now parses each model text once
> per reader. On the round fixture, `apply` parses 2 times where it parsed
> 22, and `preview` 2 where it parsed 6. Every preview, record, message and
> exit is unchanged. On one laptop, `apply` on a model of 2,404 object
> types took 12.8 s where it took 33.7 s; a round still costs time in
> proportion to the model. `gnd validate` and the other commands parse as
> before. Not in a release yet: it is listed under "Unreleased" in
> `docs/release-notes.md`.

## #227 (what happened to each part of a growth round)

> On `main` after the GO2–GO5 pull request, not in a release yet:
>
> 1. **Per-operation outcomes.** `gnd evolve preview --operation-outcomes`
>    names each operation `admitted`, `refused-by-policy`,
>    `refused-by-validation`, `refused-by-d12`, `dropped-with` a refused
>    one, or `unassessed` with the gates that did not run. When a gate
>    refuses the proposal, `--outcome-report FILE` writes the same rows; the
>    refusal and its exit are unchanged.
> 2. **The admitted part of a round.** `apply` stays whole.
>    `gnd.discover.narrow.narrow_proposal(proposal, outcomes)` returns a new
>    proposal of the operations no gate refused (their dependents dropped
>    with them), which you preview and apply like any other. There is no
>    `gnd evolve narrow` command yet; say if you need one.
> 3. **Reusing an element the model has.** "The reply shape" in
>    `unattended-growth.md` now says a reply names an existing element, its
>    own or included, by id only, and routes rows for an existing fact type
>    to `open_questions`, since the additive policy refuses a changed sample
>    row.
> 4. **A summary per round.** `gnd evolve summary ROUND_FILE --proposal P
>    --preview V --record D` prints one JSON document: what the round
>    reused, what your host dropped and why (your text, reported as yours),
>    the operations proposed, each verdict's count, the shape matches, and
>    the elements the applied record added. The fields are in the evolution
>    contract, "Round summary".
>
> Not done: a summary across rounds (compare the per-round documents), and
> any judgment of the host's reasons.
