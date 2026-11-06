# TS5 gate: spec T1-T4 over the phase tree.
set -o pipefail
cd "$(git rev-parse --show-toplevel)"
echo '$ uv run python tools/run_tutorials.py --group type-judgements'; uv run python tools/run_tutorials.py --group type-judgements 2>&1 | tail -1
echo '$ uv run --group docs zensical build --strict'; uv run --group docs zensical build --strict 2>&1 | tail -2
echo '$ uv run python tools/check_docs.py site'; uv run python tools/check_docs.py site 2>&1 | tail -1
echo '$ uv run pytest -q <T3: 6 files>'; uv run pytest -q tests/test_type_judgements_example.py tests/test_packaged_skills.py tests/test_skill_prose_sync.py tests/test_development_scaffold.py tests/test_disclosure_docs.py tests/test_tutorial_output_blocks.py 2>&1 | tail -1
echo '$ T4: anonymity and absolute-path scan of the new files'
F="docs/how-to/judge-induced-fact-types.md docs/assets/applications/judge-flow.svg docs/assets/applications/judge-duplicates.svg docs/assets/applications/judge-multivalued.svg $(git ls-files src/gnd/examples/type_judgements)"
if grep -nE "gnd-apps|gnd-analytics|/Users/|/home/" $F; then echo "T4 FAILED"; else echo "no downstream names, no absolute paths"; fi
echo '$ uv run ruff check tests/test_type_judgements_example.py'; uv run ruff check tests/test_type_judgements_example.py 2>&1 | tail -1
