# Local reserved-score procedure

The model, path policy and first prepared source corpus are bound by
records 021 and 022. Keep the key, both annotation inputs and both
composed runs in a directory outside the worktree. These private inputs
and the aggregate result files are tied by SHA-256.

Copy the key locally from the owner-approved ref and require its digest
before invoking the scorer.

```sh
git show refs/heads/literature-heldout:heldout-answer-key.json > "$local_key"
test "$(shasum -a 256 "$local_key" | cut -d' ' -f1)" = \
  "$(cat src/gnd/examples/literature/answers/heldout.sha256)"
```

The following route assembles the annotated source passages and invokes
the fixed directed-path proof procedure. Each invocation chooses its own
new local output directory. The input and score variables are local paths.

```sh
example=src/gnd/examples/literature
uv run python -m gnd.examples.literature.lineage_run assemble "$example" \
  "$example/lineage/model.orm.yaml" "$local_annotations" "$local_run"
uv run python -m gnd.examples.literature.lineage_run score \
  "$example/lineage/model.orm.yaml" "$local_run" "$local_key" > "$local_score"
```

The first score exited 1. The annotated source correction in record 023
preceded the second invocation, which exited 0, with the same rules,
policy, scorer, and answer key. The retained aggregate objects preserve the
scorer output fields other than `paths`. They add the three verified
fields `phase`, `annotations_sha256` and `path_policy_sha256`. The
annotation digest was computed from the bytes passed into assembly.
The policy digest was computed from the committed table, with the model
regeneration and unchanged policy checked separately.

The phase-review repair later required the retained admission bundles
as part of scoring. Its replay against the already corrected private
run produced the same score bytes. That replay is a regression check
of the updated verifier, using the already measured cases.
