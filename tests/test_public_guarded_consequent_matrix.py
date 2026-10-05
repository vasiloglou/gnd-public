"""Guarded consequent coverage with explicit synthetic-person fixture labels."""
from __future__ import annotations

import base64
import copy
import gzip
import hashlib
import json
import subprocess
import sys
import tempfile
from collections.abc import Iterable, Mapping, Sequence
from pathlib import Path
from typing import Any, NamedTuple

from jsonschema import Draft202012Validator
from ruamel.yaml import YAML

from gnd.report import load_report_schema

_FIXTURE_OWNER = tempfile.TemporaryDirectory(prefix="public-guarded-matrix-")
REPO_ROOT = Path(_FIXTURE_OWNER.name)
_packed = (Path(__file__).resolve().parent / "fixtures/public-guarded-branch-matrix.json.gz").read_bytes()
assert len(_packed) <= 65536
_expanded = gzip.decompress(_packed)
assert len(_expanded) <= 131072
_members = json.loads(_expanded)
_EXPECTED = {'book/model.orm.yaml', 'historical/violates-minor-adult.population.json', 'historical/violates-rated.population.json', 'expense/population.policy-conforming.json', 'historical/genre-only.population.json', 'expense/model.orm.yaml'}
assert len(_members) == 6 and {r["path"] for r in _members} == _EXPECTED
for _row in _members:
    _data = base64.b64decode(_row["base64"], validate=True)
    assert len(_data) <= 32768 and hashlib.sha256(_data).hexdigest() == _row["sha256"]
    assert _row["mode"] == 0o644
    _destination = REPO_ROOT / _row["path"]
    _destination.parent.mkdir(parents=True, exist_ok=True)
    _destination.write_bytes(_data)
    _destination.chmod(_row["mode"])
BOOKREC = REPO_ROOT / "book"
EXPENSE = REPO_ROOT / "expense"
P001_PRE_PROMOTION_MODEL = BOOKREC / "model.orm.yaml"
PHASE_FOUR_END_COMMIT = "frozen-fixture"
RATED_GUARD = "recommendation_excludes_rated_books"
MINOR_ADULT_GUARD = "recommendation_excludes_adult_books_for_minors"
GENRE_GUARD = "recommendation_matches_preferred_genre"
REPORT_VALIDATOR = Draft202012Validator(load_report_schema())
JsonObject = dict[str, Any]
Branch = tuple[str, str]
Binding = dict[str, Any]


def _git_blob(commit: str, relative: str) -> bytes:
    # Frozen bytes rematerialized locally; no target Git or fresh history claim.
    assert commit == PHASE_FOUR_END_COMMIT
    prefix = "examples/bookrec/populations/"
    assert relative.startswith(prefix)
    name = relative[len(prefix):]
    assert name in {"violates-rated.population.json", "violates-minor-adult.population.json", "genre-only.population.json"}
    return (REPO_ROOT / "historical" / name).read_bytes()

def _identity(value: Any) -> tuple[str, Any]:
    """ORM scalar identity, domain-tagged, written from the semantics directly.

    Python makes ``True == 1`` and hashes them alike; ORM does not. Booleans are
    a separate scalar domain from numbers, while Integer and Float share the
    numeric domain because Float and Number roles accept either JSON spelling.

    This is deliberately NOT ``gnd.checker._identity_key``, even though it must
    agree with it. Importing the checker would make this module a second reading
    of the checker rather than an independent one, and the whole point of
    recomputing a join here is that two independent sources agree. Same
    semantics, different code -- the C1 rule the synth oracle follows for the
    same reason.

    Found by the single-seat diff review: without this, an antecedent binding
    one variable across a Boolean role and an Integer role reported one binding
    where the runtime reports zero.
    """
    if isinstance(value, bool):
        return ("boolean", value)
    if isinstance(value, (int, float)):
        return ("number", value)
    return ("other", value)


def _unify(row: Mapping[str, Any], bind: Mapping[str, Any], seed: Binding) -> Binding | None:
    """Extend ``seed`` so ``row`` satisfies ``bind``, or ``None`` if it cannot.

    A ``bind`` value spelled ``$name`` is a variable: it takes the row's value
    for that role, and must agree -- by ORM identity, not Python equality --
    with any value the variable already carries. Every other value is a literal
    the row must match under the same identity.
    """
    out = dict(seed)
    for role, term in bind.items():
        if role not in row:
            return None
        observed = row[role]
        if isinstance(term, str) and term.startswith("$"):
            if term in out and _identity(out[term]) != _identity(observed):
                return None
            out[term] = observed
        elif _identity(observed) != _identity(term):
            return None
    return out


def antecedent_bindings(
    antecedent: Iterable[Mapping[str, Any]], facts: Mapping[str, Any]
) -> list[Binding]:
    """Every variable binding for which the whole antecedent conjunction holds.

    This is the join the checker computes, computed again from the same bytes by
    different code. The length is the binding count the report does not publish.
    """
    bindings: list[Binding] = [{}]
    for atom in antecedent:
        rows = facts.get(str(atom["fact_type"])) or []
        nxt: list[Binding] = []
        for seed in bindings:
            for row in rows:
                if not isinstance(row, Mapping):
                    continue
                extended = _unify(row, atom.get("bind") or {}, seed)
                if extended is not None:
                    nxt.append(extended)
        bindings = nxt
        if not bindings:
            break
    return bindings


def guarded_binding_counts(model: Mapping[str, Any], population: Mapping[str, Any]) -> dict[str, int]:
    """``constraint id -> independently recomputed binding count``.

    Model-level guarded constraints only; both Phase 4 cases put their guards
    there. Keyed by ``id`` rather than by position, because a report's
    ``constraint_ref`` is positional and the expense conversion moves indices.
    """
    facts = population.get("facts") or {}
    counts: dict[str, int] = {}
    for constraint in model.get("constraints") or []:
        if str(constraint.get("type")) != "guarded":
            continue
        cid = constraint.get("id")
        if cid is None:
            raise ValueError(f"guarded constraint without an id: {constraint!r}")
        counts[str(cid)] = len(antecedent_bindings(constraint.get("antecedent") or [], facts))
    return counts


def ref_to_id(model: Mapping[str, Any]) -> dict[str, str]:
    """The D-P4.15 resolution: ``constraints[N] -> id`` in document order.

    Every id must appear exactly once; a duplicate or a renamed constraint reds
    here rather than silently matching the wrong verdict downstream.
    """
    mapping: dict[str, str] = {}
    seen: set[str] = set()
    for index, constraint in enumerate(model.get("constraints") or []):
        cid = constraint.get("id")
        if cid is None:
            continue
        if str(cid) in seen:
            raise ValueError(f"duplicate constraint id: {cid}")
        seen.add(str(cid))
        mapping[f"constraints[{index}]"] = str(cid)
    return mapping


class CoverageCase(NamedTuple):
    """One committed population credited to one guarded branch."""

    model_path: Path
    population_path: Path
    constraint_id: str
    expected_verdict: str


class LoadedCoverageCase(NamedTuple):
    """In-memory form used by the negative controls."""

    model: JsonObject
    population: JsonObject
    constraint_id: str


def _read_json(path: Path) -> JsonObject:
    """Read one committed JSON object."""
    value = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(value, dict), path
    return value


def _read_model(path: Path) -> JsonObject:
    """Read one ORM YAML document without changing its declared fragments."""
    value = YAML(typ="safe").load(path.read_text(encoding="utf-8"))
    assert isinstance(value, dict), path
    return value


def _run_check(model_path: Path, population_path: Path) -> tuple[int, JsonObject]:
    """Run GND through the required subprocess interface and parse its report."""
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "gnd",
            "check",
            str(model_path),
            str(population_path),
            "--format",
            "json",
        ],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
        timeout=15,
    )
    assert completed.stdout, completed.stderr
    report = json.loads(completed.stdout)
    assert isinstance(report, dict)
    REPORT_VALIDATOR.validate(report)
    return completed.returncode, report


def _constraint(model: Mapping[str, Any], constraint_id: str) -> Mapping[str, Any]:
    """Resolve exactly one model-level constraint by stable ID."""
    matches = [
        constraint
        for constraint in model.get("constraints") or []
        if constraint.get("id") == constraint_id
    ]
    assert len(matches) == 1, constraint_id
    return matches[0]


def _covered_branches(cases: Sequence[LoadedCoverageCase]) -> tuple[set[Branch], set[str]]:
    """Credit only guarded branches whose independent antecedent join is nonempty."""
    branches: set[Branch] = set()
    absence_shapes: set[str] = set()
    for case in cases:
        constraint = _constraint(case.model, case.constraint_id)
        counts = guarded_binding_counts(case.model, case.population)
        if counts[case.constraint_id] == 0:
            continue
        consequent = constraint["consequent"]
        assert isinstance(consequent, Mapping) and len(consequent) == 1
        kind = str(next(iter(consequent)))
        branches.add((kind, str(constraint["modality"])))
        if kind == "absence":
            bind = consequent["absence"]["bind"]
            if len(bind) == 1:
                absence_shapes.add("unary")
            if len(bind) == 2 and all(
                isinstance(term, str) and term.startswith("$") for term in bind.values()
            ):
                absence_shapes.add("all-variable-arity-2")
    return branches, absence_shapes


def test_shipped_cases_cover_every_guarded_consequent_kind_and_both_modalities(
    tmp_path: Path,
) -> None:
    """Exclude branch credit from a missing case or a zero-binding antecedent."""
    # This v3.0 branch matrix deliberately uses the pre-promotion p001 model so
    # the genre consequent remains deontic. Its populations must therefore be
    # read from that phase's Git tree, not from Phase 4's evolved @2 corpus.
    historical_populations: dict[str, Path] = {}
    for name in ("violates-rated", "violates-minor-adult", "genre-only"):
        relative = f"examples/bookrec/populations/{name}.population.json"
        path = tmp_path / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(_git_blob(PHASE_FOUR_END_COMMIT, relative))
        historical_populations[name] = path

    committed = [
        CoverageCase(
            EXPENSE / "model.orm.yaml",
            EXPENSE / "population.policy-conforming.json",
            "policy_limit_meals",
            "pass",
        ),
        CoverageCase(
            P001_PRE_PROMOTION_MODEL,
            historical_populations["violates-rated"],
            RATED_GUARD,
            "fail",
        ),
        CoverageCase(
            P001_PRE_PROMOTION_MODEL,
            historical_populations["violates-minor-adult"],
            MINOR_ADULT_GUARD,
            "fail",
        ),
        CoverageCase(
            P001_PRE_PROMOTION_MODEL,
            historical_populations["genre-only"],
            GENRE_GUARD,
            "warning",
        ),
    ]
    loaded: list[LoadedCoverageCase] = []
    for case in committed:
        model = _read_model(case.model_path)
        population = _read_json(case.population_path)
        code, report = _run_check(case.model_path, case.population_path)
        ids = ref_to_id(model)
        resolved = {
            ids[str(verdict["constraint_ref"])]: verdict
            for verdict in report["verdicts"]
            if str(verdict["constraint_ref"]) in ids
        }
        assert case.constraint_id in resolved
        assert resolved[case.constraint_id]["verdict"] == case.expected_verdict
        assert code == report["exit_code"]
        loaded.append(LoadedCoverageCase(model, population, case.constraint_id))

    expected_branches = {
        ("comparison", "alethic"),
        ("absence", "alethic"),
        ("atom", "deontic"),
    }
    expected_absence_shapes = {"unary", "all-variable-arity-2"}
    assert _covered_branches(loaded) == (expected_branches, expected_absence_shapes)

    for index in range(len(loaded)):
        without_one_case = [*loaded[:index], *loaded[index + 1 :]]
        assert _covered_branches(without_one_case) != (
            expected_branches,
            expected_absence_shapes,
        )

    for index, case in enumerate(loaded):
        zero_witness = copy.deepcopy(case.population)
        antecedent = _constraint(case.model, case.constraint_id)["antecedent"]
        zero_witness["facts"][antecedent[0]["fact_type"]] = []
        dirty = list(loaded)
        dirty[index] = LoadedCoverageCase(case.model, zero_witness, case.constraint_id)
        assert guarded_binding_counts(case.model, zero_witness)[case.constraint_id] == 0
        assert _covered_branches(dirty) != (expected_branches, expected_absence_shapes)


