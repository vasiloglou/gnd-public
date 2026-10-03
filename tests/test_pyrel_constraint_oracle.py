"""PyRel constraint-oracle agreement lane (opt-in: ``pytest -m pyrel_oracle``).

Runs ``tests/oracles/pyrel_constraint_oracle.py`` — an independent ORM
constraint evaluator built on RelationalAI's PyRel with a local DuckDB
backend — over labeled (model, population) fixture pairs and compares its
verdicts against the production checker's.

The comparison contract is deliberately narrow, because the oracle is
policy-free and the production checker is not:

- production ``fail`` / ``warning`` (a witnessed violation, whatever the
  modality)  -> oracle ``violated``
- production ``pass``               -> oracle ``satisfied``
- production ``vacuous`` / ``unchecked`` -> no expectation: vacuity clauses,
  coverage-omission, and observability policy are GND semantics the oracle
  does not implement, so both agreement and disagreement there would be
  noise, not evidence.
- oracle ``unsupported``            -> no expectation (the reason is retained).
- oracle ``error``                  -> always red; a crashed constraint is
  never a skip.

The floor assertions are the instrument (harvest the memory rule: ask what a
green would report if the code did nothing). If the oracle reported
``unsupported`` everywhere, every per-verdict comparison would be skipped and
the lane would still be green — so the lane additionally demands a minimum
number of decided comparisons and, for every family the oracle claims, at
least one agreed violation and one agreed satisfaction across the corpus.

Availability: the lane needs ``uv`` (to run the PEP 723 script in its own
environment — the ``relationalai`` package pins ``pydantic<2.13.0`` and can
never share the project environment) and network access on the first run to
populate uv's cache. Absent ``uv`` the lane skips visibly, never silently.
"""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

import pytest

from gnd.checker import check
from gnd.model import load_model
from gnd.population import load_population

pytestmark = pytest.mark.pyrel_oracle

REPO = Path(__file__).resolve().parent.parent
ORACLE = REPO / "tests" / "oracles" / "pyrel_constraint_oracle.py"
RUNTIME = REPO / "src/gnd/export/pyrel_runtime.py"
CHECKER_FIXTURES = REPO / "tests" / "fixtures" / "checker"
ORACLE_FIXTURES = REPO / "tests" / "fixtures" / "pyrel-oracle"

CASES: list[tuple[str, Path, Path]] = [
    ("ring_pass", CHECKER_FIXTURES / "ring.orm.yaml",
     CHECKER_FIXTURES / "population.ring_pass.yaml"),
    ("ring_fail", CHECKER_FIXTURES / "ring.orm.yaml",
     CHECKER_FIXTURES / "population.ring_fail.yaml"),
    ("setfam_pass", CHECKER_FIXTURES / "setfam.orm.yaml",
     CHECKER_FIXTURES / "population.setfam_pass.yaml"),
    ("setfam_fail", CHECKER_FIXTURES / "setfam.orm.yaml",
     CHECKER_FIXTURES / "population.setfam_fail.yaml"),
    ("misc_pass", CHECKER_FIXTURES / "misc.orm.yaml",
     CHECKER_FIXTURES / "population.misc_pass.yaml"),
    ("misc_fail", CHECKER_FIXTURES / "misc.orm.yaml",
     CHECKER_FIXTURES / "population.misc_fail.yaml"),
    ("basics_pass", ORACLE_FIXTURES / "basics.orm.yaml",
     ORACLE_FIXTURES / "population.basics_pass.yaml"),
    ("basics_fail", ORACLE_FIXTURES / "basics.orm.yaml",
     ORACLE_FIXTURES / "population.basics_fail.yaml"),
]

#: production verdict -> the oracle status it predicts (absent key = skip).
EXPECTED = {"fail": "violated", "warning": "violated", "pass": "satisfied"}

#: Every family the oracle claims to evaluate must show BOTH outcomes agreed
#: at least once across the corpus, so silent unsupport can never green the lane.
CLAIMED_FAMILIES = {
    "uniqueness", "mandatory", "mandatory-disjunctive", "value", "frequency",
    "ring", "subset", "equality", "exclusion", "exclusive-or",
    "value-comparison", "cardinality", "subtype-partition",
}

#: Floor on decided comparisons corpus-wide (measured 76 at authoring time).
#: A floor alone is NOT sufficient: with 76 decided and a floor of 70, an oracle
#: that newly declines up to six constraints stays green. The floor is retained
#: because the seeded M2 control asserts against it; EXPECTED_DECIDED below is
#: what actually forbids selective skipping.
COMPARED_FLOOR = 70

#: The exact decided-comparison count. Pinned, not floored: any constraint the
#: oracle newly declines to evaluate reds this, which is the only way to catch an
#: oracle that skips SOME of its work rather than all of it.
EXPECTED_DECIDED = 76

#: The exact corpus-wide census of declined constraints, by reason. A new
#: `unsupported` anywhere changes this multiset and must be accounted for
#: deliberately rather than absorbed by a floor's headroom.
EXPECTED_UNSUPPORTED: dict[str, int] = {
    "time-relative-operand": 2,
    "subtype-membership-derivation-only": 2,
    "family-not-evaluated:textual": 2,
}

#: (case, constraint_ref) -> written rationale, for a row where the production
#: checker declined to decide but the oracle decided anyway. MUST stay empty
#: unless a reviewed rationale exists: such a row is a disagreement the
#: comparison contract is structurally unable to report, so it is refused at the
#: point where it would become invisible rather than counted as a skip.
REVIEWED_DECIDED_ON_NATIVE_UNDECIDED: dict[tuple[str, str], str] = {}


# --- comparison predicates: ONE home each ----------------------------------
# The real tests and the seeded-mutation control both call these, so a control
# that reds proves the predicate the real test uses can red.

def _decided(rows: list[dict]) -> list[dict]:
    """Rows where BOTH sides decided, and are therefore comparable."""
    return [row for row in rows
            if row["native"] in EXPECTED and row["oracle"] in {"violated", "satisfied"}]


def _mismatches(rows: list[dict]) -> list[tuple]:
    """Decided rows that disagree."""
    return [(row["case"], row["ref"], row["native"], row["oracle"])
            for row in _decided(rows) if row["oracle"] != EXPECTED[row["native"]]]


def _family_gaps(rows: list[dict]) -> tuple[set[str], set[str]]:
    """Claimed families lacking an agreed violation / an agreed satisfaction."""
    violated: set[str] = set()
    satisfied: set[str] = set()
    for row in _decided(rows):
        if row["oracle"] == EXPECTED[row["native"]]:
            (violated if row["oracle"] == "violated" else satisfied).add(row["family"])
    return CLAIMED_FAMILIES - violated, CLAIMED_FAMILIES - satisfied


def _require_uv() -> str:
    executable = shutil.which("uv")
    if executable is None:
        pytest.skip("uv executable absent — PyRel oracle lane needs `uv run --script`")
    return executable


def _run_oracle_over_corpus(executable: str, oracle_path: Path, out_dir: Path) -> dict[str, dict]:
    """One oracle subprocess per corpus case, for ANY oracle source file."""
    runs: dict[str, dict] = {}
    for name, model_path, population_path in CASES:
        out = out_dir / f"{name}.json"
        completed = subprocess.run(
            [executable, "run", "--script", str(oracle_path), str(model_path),
             str(population_path), "--out", str(out)],
            capture_output=True, text=True, timeout=600, cwd=REPO, check=False,
        )
        assert completed.returncode == 0, (
            f"oracle failed on {name}:\n{completed.stdout[-2000:]}\n{completed.stderr[-2000:]}"
        )
        runs[name] = json.loads(out.read_text(encoding="utf-8"))
    return runs


def _rows_from_runs(runs: dict[str, dict]) -> list[dict]:
    """Flat per-constraint comparison rows across the whole corpus."""
    rows: list[dict] = []
    for name, model_path, population_path in CASES:
        model = load_model(model_path)
        population = load_population(population_path, model=model)
        report = check(model, population)
        oracle = {v["constraint_ref"]: v for v in runs[name]["verdicts"]}
        for verdict in report.verdicts:
            rows.append({
                "case": name,
                "ref": verdict.constraint_ref,
                "family": verdict.constraint_type,
                "native": verdict.verdict,
                "oracle": oracle.get(verdict.constraint_ref, {}).get("status", "MISSING"),
                "reason": oracle.get(verdict.constraint_ref, {}).get("reason"),
            })
    return rows


@pytest.fixture(scope="module")
def oracle_runs(tmp_path_factory: pytest.TempPathFactory) -> dict[str, dict]:
    """The REAL oracle, run once per corpus case and cached for the module."""
    return _run_oracle_over_corpus(
        _require_uv(), ORACLE, tmp_path_factory.mktemp("pyrel-oracle")
    )


@pytest.fixture(scope="module")
def comparisons(oracle_runs: dict[str, dict]) -> list[dict]:
    """Flat per-constraint comparison rows across the whole corpus."""
    return _rows_from_runs(oracle_runs)


@pytest.mark.parametrize("name", [case[0] for case in CASES])
def test_every_constraint_is_addressed(name: str, oracle_runs: dict[str, dict],
                                       comparisons: list[dict]) -> None:
    """The oracle emits exactly one verdict per production constraint ref."""
    missing = [row["ref"] for row in comparisons if row["case"] == name
               and row["oracle"] == "MISSING"]
    assert missing == []
    native_refs = {row["ref"] for row in comparisons if row["case"] == name}
    oracle_refs = {v["constraint_ref"] for v in oracle_runs[name]["verdicts"]}
    assert oracle_refs == native_refs


def test_oracle_emits_no_duplicate_constraint_refs(oracle_runs: dict[str, dict]) -> None:
    """One verdict per reference, checked on the RAW list, not the indexed dict.

    ``_rows_from_runs`` indexes the oracle's verdicts by ``constraint_ref``, so a
    payload carrying two rows for one reference silently keeps the last. A wrong
    verdict followed by a right one would then compare green. Check the list.
    """
    for name, payload in oracle_runs.items():
        refs = [verdict["constraint_ref"] for verdict in payload["verdicts"]]
        duplicates = sorted({ref for ref in refs if refs.count(ref) > 1})
        assert duplicates == [], f"{name}: duplicate oracle verdicts for {duplicates}"


def test_no_oracle_errors(comparisons: list[dict]) -> None:
    errors = [(row["case"], row["ref"], row["reason"]) for row in comparisons
              if row["oracle"] == "error"]
    assert errors == []


def test_decided_verdicts_agree(comparisons: list[dict]) -> None:
    """Wherever both sides decided, they must decide alike."""
    assert _mismatches(comparisons) == []


def test_comparison_floor(comparisons: list[dict]) -> None:
    """A lane that skipped everything must be red, not green."""
    compared = _decided(comparisons)
    assert len(compared) >= COMPARED_FLOOR, (
        f"only {len(compared)} decided comparisons — the oracle is skipping too much"
    )


def test_every_claimed_family_shows_both_outcomes(comparisons: list[dict]) -> None:
    """Each claimed family needs >=1 agreed violation AND >=1 agreed pass."""
    missing_violated, missing_satisfied = _family_gaps(comparisons)
    assert missing_violated == set()
    assert missing_satisfied == set()


def test_native_undecided_rows_carry_no_decided_oracle_verdict(
    comparisons: list[dict],
) -> None:
    """The oracle may not decide where the production checker abstained.

    ``EXPECTED`` has no key for ``vacuous``/``unchecked``, so such a row is
    dropped from every comparison and every floor. A row where the oracle
    nonetheless returned ``violated``/``satisfied`` is therefore a disagreement
    the contract cannot report — the exact shape that let a false decided
    subtype-partition verdict sit in the committed corpus unseen. Refuse it here,
    where it becomes invisible, rather than trusting the skip.
    """
    decided_on_abstention = [
        (row["case"], row["ref"], row["family"], row["native"], row["oracle"])
        for row in comparisons
        if row["native"] not in EXPECTED
        and row["oracle"] in {"violated", "satisfied"}
        and (row["case"], row["ref"]) not in REVIEWED_DECIDED_ON_NATIVE_UNDECIDED
    ]
    assert decided_on_abstention == []

    live = {(row["case"], row["ref"]) for row in comparisons}
    stale = sorted(key for key in REVIEWED_DECIDED_ON_NATIVE_UNDECIDED if key not in live)
    assert stale == [], f"exemption(s) for rows that no longer exist: {stale}"


def test_the_comparison_census_is_complete(comparisons: list[dict]) -> None:
    """Every verdict row is accounted for: compared, or skipped for a named reason.

    A skip that nothing counts is how a false oracle verdict stayed invisible for
    a whole authoring pass. The census must exhaust the rows.
    """
    decided = len(_decided(comparisons))
    skipped_native = len([r for r in comparisons if r["native"] not in EXPECTED])
    skipped_oracle = len([r for r in comparisons
                          if r["native"] in EXPECTED
                          and r["oracle"] not in {"violated", "satisfied"}])
    assert decided + skipped_native + skipped_oracle == len(comparisons)
    assert decided >= COMPARED_FLOOR


def test_the_decided_count_and_decline_census_are_exact(comparisons: list[dict]) -> None:
    """Selective skipping must red, not hide in the floor's headroom.

    An oracle that quietly stops evaluating two of its thirteen families would
    drop from 76 decided comparisons to 74 -- still above COMPARED_FLOOR, still
    showing both outcomes for every family from its remaining sub-branches, and
    still green. Pinning the exact count and the exact decline census removes
    that headroom: any new decline has to be accounted for here on purpose.
    """
    assert len(_decided(comparisons)) == EXPECTED_DECIDED
    census: dict[str, int] = {}
    for row in comparisons:
        if row["oracle"] == "unsupported":
            census[row["reason"]] = census.get(row["reason"], 0) + 1
    assert census == EXPECTED_UNSUPPORTED


def test_require_mode_is_reserved(tmp_path: Path) -> None:
    """``--mode require`` declares its own incompleteness rather than pretending.

    The LQP/Native-App runtime that evaluates PyRel ``require`` constraints is
    not available locally; until a local LQP engine lands, require mode must
    report every constraint unsupported with the documented reason.
    """
    executable = _require_uv()
    out = tmp_path / "require.json"
    _, model_path, population_path = CASES[-1]
    completed = subprocess.run(
        [executable, "run", "--script", str(ORACLE), str(model_path),
         str(population_path), "--out", str(out), "--mode", "require"],
        capture_output=True, text=True, timeout=600, cwd=REPO, check=False,
    )
    assert completed.returncode == 0, completed.stderr[-2000:]
    payload = json.loads(out.read_text(encoding="utf-8"))
    assert payload["mode"] == "require"
    assert payload["verdicts"], "require mode must still address every constraint"
    for verdict in payload["verdicts"]:
        assert verdict["status"] == "unsupported"
        assert verdict["reason"] == "require-mode-needs-lqp-runtime"


# --- the negative control ---------------------------------------------------
# A harness that verifies this phase's own claim is believed only after a
# negative control: feed it a known-dirty artifact and watch it red.
#
# The fault is injected into the ORACLE SOURCE and travels the whole path the
# lane claims to verify — PyRel evaluation, JSON serialization, the subprocess
# boundary, row assembly, and the floors. Mutating the assembled comparison rows
# instead would only show that three list comprehensions read their own input.

#: The exact ``_decide`` body the oracle ships; two seeds rewrite it.
_DECIDE_BODY = (
    '        if witnesses:\n'
    '            return "violated", witnesses[:WITNESS_CAP]\n'
    '        return "satisfied", []'
)

#: The head of ``evaluate``; one seed short-circuits it.
_EVALUATE_HEAD = (
    '        """Return (status, witnesses-or-reason) for one constraint."""\n'
    '        family = constraint.get("type")'
)

#: label -> (exact source fragment, its replacement, the floor that must red)
SEEDED_MUTATIONS: dict[str, tuple[str, str, str]] = {
    "M1-inverted-decision": (
        _DECIDE_BODY,
        (
            '        if witnesses:\n'
            '            return "satisfied", []\n'
            '        return "violated", [["seeded"]]'
        ),
        "mismatches",
    ),
    "M2-everything-unsupported": (
        _EVALUATE_HEAD,
        (
            '        """Return (status, witnesses-or-reason) for one constraint."""\n'
            '        return "unsupported", "seeded"\n'
            '        family = constraint.get("type")'
        ),
        "floor",
    ),
    # NOT "never violates": cardinality returns its status directly and does not
    # route through _decide, so a mutated _decide leaves that family untouched.
    # The control asserts what it actually establishes -- that at least one
    # claimed family loses its agreed violation.
    "M3-decide-never-violates": (
        _DECIDE_BODY,
        '        return "satisfied", []',
        "family-gaps",
    ),
}


@pytest.mark.parametrize("label", sorted(SEEDED_MUTATIONS))
def test_seeded_oracle_mutation_makes_the_agreement_lane_red(
    label: str, tmp_path: Path,
) -> None:
    """A really-broken oracle must red the floor it breaks, through the real path."""
    executable = _require_uv()
    original, replacement, expected_red = SEEDED_MUTATIONS[label]

    source = RUNTIME.read_text(encoding="utf-8")
    assert source.count(original) == 1, (
        f"{label}: mutation anchor is not unique in the oracle source — "
        "the control cannot claim to have injected the fault it names"
    )
    mutated = tmp_path / "tests/oracles/pyrel_constraint_oracle.py"
    mutated.parent.mkdir(parents=True)
    mutated.write_bytes(ORACLE.read_bytes())
    compiler = tmp_path / "src/gnd/export/pyrel_runtime.py"
    compiler.parent.mkdir(parents=True)
    compiler.write_text(source.replace(original, replacement), encoding="utf-8")

    out_dir = tmp_path / "runs"
    out_dir.mkdir()
    rows = _rows_from_runs(_run_oracle_over_corpus(executable, mutated, out_dir))

    if expected_red == "mismatches":
        assert _mismatches(rows), f"{label}: an inverted oracle agreed with the checker"
    elif expected_red == "floor":
        assert len(_decided(rows)) < COMPARED_FLOOR, (
            f"{label}: an oracle that decides nothing still met the comparison floor"
        )
    else:
        missing_violated, _ = _family_gaps(rows)
        assert missing_violated, (
            f"{label}: an oracle whose _decide never reports a violation still "
            "showed an agreed violation for every claimed family"
        )
