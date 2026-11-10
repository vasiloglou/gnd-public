Retained Codex CLI first review; home/repository paths sanitized. Other wording retained verbatim.

**One required completeness repair** in `c6dad88d…9f3d22f7`; no blocking runtime defect found.

- **Completeness — retained pages still link to draft source.** [share-a-vocabulary.md:9](<REPO>/docs/how-to/share-a-vocabulary.md:9) and [shared-component-vocabulary.md:8](<REPO>/docs/tutorials/shared-component-vocabulary.md:8) send “Current example files” to `tree/codex/model-composition-docs-draft/...`. Following either retained entry point selects draft-branch source instead of eventual `main`, contrary to MC4’s source-link requirement and record019’s carryover. Reproduced by extracting both URLs with `.venv/bin/python -c`. Change those two targets to `tree/main/...`. I did not test remote availability or infer a 404.

Inspected the authority/gate binding, shipped proposals and populations, D-12 metadata, owned-only candidate, vocabulary retention, canonical citations, runner/test integration, R30 successor, navigation, release wording, and SVG source/alt text. All 37 candidate-manifest hashes and the gated spec prefix matched.

Actual focused probes:

- `.venv/bin/python -c` invoking `pytest.main` with packaged-skills tests, R30, prose-sync, and five expense-page checks; `-q -s --tb=short -p no:cacheprovider`, excluding temporary-file tests: **70 passed, 1 skipped, 7 deselected**.
- Python driver invoking `.venv/bin/python -m gnd check … --rule-ids`: all **10** documented population outcomes matched.
- Read-only `EvolutionService.preview` calls: edition-only analysis named only `receipt_required`; combined preview validated, was breaking, and accepted its exact report digest.
- `git diff --check c6dad88d… HEAD -- docs src tests tools dev zensical.toml`: **0**. The unrestricted comparison returned **2**, solely for trailing spaces in four retained historical logs.

The initial pytest attempt failed during temporary capture setup; direct `/private/tmp` creation also failed. A subsequent selection had **44 passed, 1 skipped, 1 setup error** before excluding the remaining temporary-file fixture. These errors are not passes.

I did not rerun publication/finalization, temporary mutation controls, strict build, rendered-site checks, native lanes, or broad/default/census suites. Their retained final outputs were inspected, not counted as fresh measurements. No files changed, agents/panels invoked, network research performed, or merge authority inferred.
