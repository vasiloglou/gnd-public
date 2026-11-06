# type-induction-skills close gate. The default lane (pyproject addopts) is a
# superset of every TS1-TS5 pytest selection; it runs as part A (on beast-3 over
# a snapshot of the closing commit, output in default-lane.txt). Part B runs here.
set -o pipefail
cd "$(git rev-parse --show-toplevel)"
if [ "$1" = A ]; then uv run pytest -q -p no:cacheprovider 2>&1 | tail -15; exit; fi
echo '$ uv run pytest -q -m distribution tests/test_public_distribution.py tests/test_release_acceptance.py tests/test_public_built_inventory.py'
uv run pytest -q -m distribution tests/test_public_distribution.py tests/test_release_acceptance.py tests/test_public_built_inventory.py 2>&1 | grep -E "^FAILED|passed|failed|error" | sed "s|$PWD|<repo>|g"
echo '$ uv run python tools/run_tutorials.py'; uv run python tools/run_tutorials.py 2>&1 | tail -1
echo '$ uv run --group docs zensical build --strict'; uv run --group docs zensical build --strict 2>&1 | tail -2
echo '$ uv run python tools/check_docs.py site'; uv run python tools/check_docs.py site 2>&1 | tail -1
echo '$ uv run gnd install --symlink --project --force (twice: idempotence)'; uv run gnd install --symlink --project --force >/dev/null 2>&1; uv run gnd install --symlink --project --force 2>&1 | grep -c "already current"; git status --short .claude .codex | wc -l | sed 's/^ */link changes: /'
echo '$ uv run gnd doctor --project'; uv run gnd doctor --project >/dev/null 2>&1; echo "doctor exit $?"
echo '$ uv run ruff check src/gnd/discover tools/record_judge_sessions.py tools/run_tutorials.py tests/test_discover_type_evidence.py tests/test_discover_type_judgements.py tests/test_judge_fact_types_skill.py tests/test_model_multivalued_skill.py tests/test_type_judgements_example.py'
uv run ruff check src/gnd/discover tools/record_judge_sessions.py tools/run_tutorials.py tests/test_discover_type_evidence.py tests/test_discover_type_judgements.py tests/test_judge_fact_types_skill.py tests/test_model_multivalued_skill.py tests/test_type_judgements_example.py 2>&1 | tail -1
