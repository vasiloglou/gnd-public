# Testing gnd-model-from-text

How to run the skill end-to-end against the benchmark dialogue fixtures, capture outputs, and validate against the expected reference solutions. Case definitions live in [`cases.json`](cases.json).

> **Caveat:** the reference solutions in `expected/` are drafted targets-to-iterate-against, not authoritative ground truth.

---

## What "testing" means here

Testing this skill means: **invoke CSDP on a dialogue fixture, walk through the steps (or run One-shot for stress testing), and compare the output pair against the expected reference solution.**

Each test produces:
- `output.orm.yaml` — the designed ORM model
- `output.verbalization.txt` — Halpin-style CNL rendering
- `diff.md` — the eval-run report (T-E1..T-E4 verdicts)

The verbalization is the primary review surface for T-E5.

## Quick-start: smallest possible test

Use the [`movie_catalog` example](../examples/movie_catalog.dialogue.md) — small enough to read the full output.

1. Start a session with this skill available and say:

   > Run the gnd-model-from-text CSDP. I want to model a small movie-catalog domain. Use Guided mode. I'll provide examples and answer your questions.

2. Provide examples (copy from `examples/movie_catalog.dialogue.md` to replicate the canonical run, or invent your own). After Step 7f, the skill emits the two output files and validates them.

3. Compare against the canonical example:

   ```bash
   # paths below are relative to this document's own directory (<skill-dir>/evals/)
   diff /tmp/movie-test/model.orm.yaml ../examples/movie_catalog.orm.yaml
   ```

   Differences will exist (your dialogue will diverge from the canonical) — the goal isn't byte-equality, it's structural similarity.

## Full test cycle — fixtures × modes

For each fixture under `fixtures/` and each mode in `{guided, one-shot}`:

```
Run gnd-model-from-text against the dialogue at
<skill-dir>/evals/fixtures/<fixture>/dialogue.md
in <mode> mode. Emit outputs to <skill-dir>/evals/results/<YYYY-MM-DD>/<fixture>-<mode>/.
(<skill-dir> is this skill's own directory — resolve it before running.)
```

In **Guided** mode, you (the eval runner) play the user — answering Claude's questions following the fixture's intended path. In **One-shot** mode, the fixture transcript is fed as a single completed dialogue and Claude drafts in one pass.

## Validating outputs

Every emitted model must exit 0 through `gnd validate`. Where `gnd` is not installed, the
skill-bundled fallback covers layer 1 only — resolve `<skill-dir>` to this skill's own directory:

```bash
gnd validate output.orm.yaml                                         # two-layer
uv run <skill-dir>/scripts/validate_model.py output.orm.yaml         # zero-install fallback, layer-1 only
```

Then diff against expected per `cases.json` T-E1's equivalence rules:
- Object types match by name (modulo case)
- Fact types match by structural shape; reading wording may differ
- Explicit-source constraints must match in type, target, and provenance
- Inferred constraints judged by correctness rubric; modality assignments must follow the D-03 policy
- Halpin posture honored throughout

## Stakeholder reviewability test (T-E5)

For at least one fixture per eval cycle: run CSDP, hand the verbalization plus [`reviewability_checklist.md`](reviewability_checklist.md) to a domain-expert stakeholder unfamiliar with ORM, and have them fill it in. Pass = at least one stakeholder reports they can validate without help.

---
*Adapted from the rai-agent-skills ORM skills (branch an-orm-skill).*
