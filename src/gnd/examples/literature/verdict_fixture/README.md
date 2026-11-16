# Verdicts on a derived claim

Run the verdict example on the [semantic revision release](../revision_fixture/README.md).

```sh
python -m gnd.examples.literature.verdict run revision-run --out verdict-run
python -m gnd.examples.literature.verdict replay revision-run verdict-run
python -m gnd.examples.literature.verdict evaluate revision-run --case reject-whale-a
python -m gnd.examples.literature.verdict evaluate revision-run --case both-approved --edition revised
```

The fixture includes saved synthetic opinions on two separate supports for
VampNet's ancestry from DMD. Each opinion binds the released claim, sense
decisions, interpretation policy, rule and definition. It also binds the
specific source occurrence, review and witness. The verifier checks the
independently pinned opinions before reading the release and replays each
selected certificate with its own source evidence.

Two approved supports back the claim. Rejecting whale-a leaves the other
support. When both are rejected the claim has no effective support. The
revised predicate invalidates the original opinions. A separately recorded
review and replayed witness restore whale-a's support for the same source
occurrence. The other support retains its original review.

The single-case command exits 0 for a supported result, 2 when there are
no effective supports, and 3 when shared bindings require revalidation or
the inputs are invalid. Run and replay report all five fixture cases and
exit 0 on a completed evaluation. Replay recomputes the report and checks
its exact bytes against the retained copy.
