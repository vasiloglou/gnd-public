"""Run the three source-scoped literature competency examples offline."""
from __future__ import annotations

import argparse
import asyncio
import sys
from decimal import Decimal
from pathlib import Path
from typing import Any

from gnd.anchors import recognised_ranges, recognition_index, strict_json
from gnd.artifacts import (
    ArtifactError,
    canonical_json_bytes,
    read_regular_bounded,
    sha256_hex,
)
from gnd.process import BoundedProcessResult, ProcessLimits, run_bounded_process

FIXTURE = Path(__file__).parent / "depth_fixture"
INPUT_LIMIT = 128 * 1024
PROCESS_LIMIT = 1 << 20
PROCESS_LIMITS = ProcessLimits(
    timeout_seconds=30,
    terminate_grace_seconds=1,
    stdin_limit_bytes=0,
    stdout_limit_bytes=PROCESS_LIMIT,
    stderr_limit_bytes=INPUT_LIMIT,
    total_output_limit_bytes=PROCESS_LIMIT,
)
CASES = ("dynamics", "molecular", "algorithms")
CASES_SHA = "366dee9620694a6037496f51247248e8f937feae04939778b0cfce0d99327d70"
SUPPORT_SHA = "8d697a5a169d6dfa27a0dacb498df9e86bd78f1ffbd5365ea82f38264333ed59"
CONTEXT = {
    "dataset_version": "experiment_dataset",
    "split": "experiment_split",
    "metric": "experiment_metric",
    "units": "experiment_units",
    "conditions": "experiment_conditions",
}
RELATIONS = ("subject_specializes", "subject_has_component", "subject_influenced_by")
EXPERIMENT_FIELDS = {
    **CONTEXT,
    "score": "experiment_score",
    "baseline": "experiment_baseline",
    "configuration": "experiment_configuration",
    "uncertainty": "experiment_uncertainty",
}


class ExampleError(ValueError):
    """The worked example cannot establish the requested output."""


def _read(root: Path, name: str) -> bytes:
    return read_regular_bounded(root, name, max_bytes=INPUT_LIMIT)[0]


def _decode(data: bytes) -> dict:
    try:
        value = strict_json(data, max_bytes=PROCESS_LIMIT, too_large="example JSON exceeds its cap")
    except (ValueError, RecursionError) as error:
        raise ExampleError("invalid example JSON") from error
    if not isinstance(value, dict):
        raise ExampleError("expected an example JSON object")
    return value


def _write(out: Path, name: str, data: Any) -> bytes:
    raw = canonical_json_bytes(data)
    (out / name).write_bytes(raw)
    return raw


def _command(out: Path, *args: str) -> BoundedProcessResult:
    result = asyncio.run(run_bounded_process(
        (sys.executable, "-m", "gnd", *args), cwd=out, env={}, limits=PROCESS_LIMITS,
    ))
    if (result.status not in {"succeeded", "failed"} or result.stdout_truncated
            or result.stderr_truncated or not result.process_group_cleaned):
        raise ExampleError(f"{args[0]} failed to finish its bounded run")
    return result


def _success(out: Path, *args: str) -> bytes:
    result = _command(out, *args)
    if result.return_code != 0:
        raise ExampleError(f"{args[0]} exited {result.return_code}")
    return result.stdout


def _load_reviewed(fixture: Path, name: str, expected_sha: str) -> dict:
    raw = _read(fixture, name)
    document = _decode(raw)
    if sha256_hex(raw) != expected_sha:
        raise ExampleError(f"reviewed {name} binding differs")
    return document


def _fact_rows(facts: dict) -> None:
    if not all(
        isinstance(rows, list) and all(
            isinstance(row, dict) and all(isinstance(value, str) for value in row.values())
            for row in rows
        ) for rows in facts.values()
    ):
        raise ExampleError("invalid example fact rows")


def _question_rows(case: dict, support: dict, document: bytes, facts: dict) -> list[dict]:
    if sha256_hex(document) != support["document_sha256"]:
        raise ExampleError("reviewed source document binding differs")
    text = document.decode("utf-8")
    _fact_rows(facts)
    by_fact = {
        fact: [row for row in rows if row.get("subject") == case["subject"]]
        for fact, rows in facts.items()
    }
    answers = []
    for question, evidence in zip(case["questions"], support["rows"], strict=True):
        if question["id"] != evidence["id"]:
            raise ExampleError("reviewed question roster differs")
        primary = evidence["primary"]
        claimed_locator = {key: value for key, value in primary.items() if key != "evidence_form"}
        if claimed_locator != question["primary"]:
            raise ExampleError(f"reviewed primary locator differs for {question['id']}")
        start, end = evidence["span"]
        excerpt = text[start:end]
        if not (0 <= start < end <= len(text)) or sha256_hex(excerpt.encode()) != evidence["span_sha256"]:
            raise ExampleError("reviewed source span differs")
        selected = {fact: by_fact.get(fact, []) for fact in question["requires"]}
        reviewed = evidence["facts"]
        for fact, rows in selected.items():
            if rows and rows != reviewed.get(fact):
                raise ExampleError(f"unreviewed facts for {question['id']}")
        supported = all(selected.values()) and evidence["decision"] == "supported"
        answers.append({
            "id": question["id"],
            "status": "supported" if supported else "unknown",
            "claim_kind": question["claim_kind"],
            "facts": selected if supported else {},
            "missing": [fact for fact, rows in selected.items() if not rows],
            "evidence": {
                **primary,
                "review": evidence["decision"],
                "document_sha256": support["document_sha256"],
                "span": evidence["span"],
                "span_sha256": evidence["span_sha256"],
                "excerpt": excerpt,
            },
        })
    return answers


def _check_case(out: Path, model: str, document: bytes, facts: dict) -> dict:
    (out / "document.txt").write_bytes(document)
    _success(out, "extract", model, "--out", "bundle")
    stem = model.removesuffix(".json")
    index_raw = _read(out, f"bundle/{stem}.artifacts.json")
    index = _decode(index_raw)
    population = "population.json"
    raw = _write(out, population, {"population": index["header_template"], "facts": facts})
    sidecar = _write(out, "population.extraction.json", {
        "schema_version": 1,
        "model": model,
        "model_sha256": index["model"]["sha256"],
        "population": population,
        "population_sha256": sha256_hex(raw),
        "document": "document.txt",
        "document_sha256": sha256_hex(document),
        "projection_sha256": index["artifacts"][f"{stem}.projection.schema.json"]["sha256"],
        "skill": "gnd-extract",
        "skill_version": "1",
        "executing_model": "saved-public-fixture",
    })
    verified = _success(out, "verify", model, population, "--artifacts", "bundle", "--format", "json")
    checked = _success(out, "check", model, population, "--format", "json")
    return {
        "model_sha256": index["model"]["sha256"],
        "population_sha256": sha256_hex(raw),
        "extraction_sha256": sha256_hex(sidecar),
        "bundle_index_sha256": sha256_hex(index_raw),
        "verification": _decode(verified)["outcome"],
        "check": _decode(checked)["outcome"],
    }


def compare_scores(left: dict[str, str], right: dict[str, str]) -> tuple[str, list[str]]:
    """Compare scores by the declared evidence context."""
    mismatches = [name for name in CONTEXT if name in left and name in right and left[name] != right[name]]
    if mismatches:
        return "incompatible", mismatches
    missing = [name for name in (*CONTEXT, "score") if name not in left or name not in right]
    return ("unknown", missing) if missing else ("comparable", [])


def _comparison_inputs(raw: bytes) -> tuple[dict, list[dict], dict[str, dict[str, str]]]:
    fixture = _decode(raw)
    if (fixture.get("origin") != "synthetic" or not isinstance(fixture.get("facts"), dict)
            or not isinstance(fixture.get("pairs"), list)):
        raise ExampleError("invalid synthetic comparison corpus")
    facts, pairs = fixture["facts"], fixture["pairs"]
    _fact_rows(facts)
    by_experiment: dict[str, dict[str, str]] = {}
    for field, fact in EXPERIMENT_FIELDS.items():
        for row in facts.get(fact, []):
            if set(row) != {"experiment", field}:
                raise ExampleError(f"invalid synthetic experiment field {field}")
            record = by_experiment.setdefault(row["experiment"], {})
            if field in record:
                raise ExampleError(f"ambiguous synthetic experiment field {field}")
            record[field] = row[field]
    ids = set()
    for pair in pairs:
        if (not isinstance(pair, dict) or set(pair) != {"id", "left", "right"}
                or any(not isinstance(value, str) for value in pair.values())
                or pair["id"] in ids or pair["left"] not in by_experiment or pair["right"] not in by_experiment):
            raise ExampleError("invalid synthetic comparison pair")
        ids.add(pair["id"])
    return facts, pairs, by_experiment


def _checked_comparisons(out: Path, facts: dict, pairs: list[dict],
                         experiments: dict[str, dict[str, str]]) -> tuple[list[dict], str]:
    population = _write(out, "comparison.population.json", {
        "population": {"model": "vocabulary.orm.json", "source": "fixture"},
        "facts": facts,
    })
    _success(out, "check", "vocabulary.orm.json", "comparison.population.json", "--format", "json")
    rows = []
    for pair in pairs:
        status, fields = compare_scores(experiments[pair["left"]], experiments[pair["right"]])
        rows.append({**pair, "origin": "synthetic", "status": status, "fields": fields})
    return rows, sha256_hex(population)


def _dimension_probe() -> dict:
    reported, equivalent, energy = "2 fs", "0.002 ps", "2 eV"
    text = f"{reported}\n{equivalent}\n{energy}"
    index = recognition_index(text, {"integer", "decimal"})
    magnitude = int(reported.split()[0])
    integer_ranges = recognised_ranges(index, "integer", magnitude)
    equivalent_start = len(reported) + 1
    energy_start = equivalent_start + len(equivalent) + 1
    equivalent_magnitude = Decimal(equivalent.split()[0])
    equivalent_range = (equivalent_start, equivalent_start + len(str(equivalent_magnitude)))
    recognized_equivalent = equivalent_range in recognised_ranges(index, "decimal", equivalent_magnitude)
    normalized_equivalent = equivalent_range in integer_ranges
    energy_matches = (energy_start, energy_start + len(str(magnitude))) in integer_ranges
    return {
        "axis": "dimensions",
        "observed": {
            "time": {"reported": reported, "equivalent": equivalent},
            "energy": energy,
            "reported_matches_checked_magnitude": (0, len(str(magnitude))) in integer_ranges,
            "equivalent_recognized_as_decimal": recognized_equivalent,
            "equivalent_matches_checked_magnitude": normalized_equivalent,
            "energy_matches_checked_magnitude": energy_matches,
        },
        "opens_ld2": not normalized_equivalent or energy_matches,
        "requirement": "Accept an equivalent time step and refuse the same magnitude in energy units.",
    }


def _percentage_probe() -> dict:
    before, after = Decimal(40), Decimal(45)
    absolute = after - before
    relative = (absolute / before * 100).normalize()
    values = (before, after, relative)
    text = f"From {before}% to {after}%: {absolute} percentage points, or a relative change of {relative}%."
    index = recognition_index(text, {"percent"})
    recognized = [value for value in values if recognised_ranges(index, "percent", value)]
    points_as_percent = bool(recognised_ranges(index, "percent", absolute))
    return {
        "axis": "percent-versus-points",
        "observed": {
            "recognized_percentages": [float(value) if value % 1 else int(value) for value in recognized],
            "absolute_change_points": str(absolute),
            "relative_change_percent": str(relative),
            "points_recognized_as_percent": points_as_percent,
        },
        "opens_ld2": recognized != list(values) or points_as_percent,
        "requirement": "Keep the absolute change in percentage points separate from the relative percent change.",
    }


def _decimal_probe(out: Path) -> dict:
    args = ("decimal.orm.json", "decimal.population.json")
    _success(out, "check", *args, "--format", "json")
    population = _decode(_read(out, args[1]))
    target = _decode(_read(out, "decimal.targets.json"))["targets"][0]
    checked_value = population["facts"]["reported_decimal"][0]["value"]
    cell = target["tuple"][0]
    if cell["value"] != checked_value:
        raise ExampleError("decimal witness target differs from the checked value")
    witness = _command(out, "witness", *args, "--targets", "decimal.targets.json", "--raw", "--out", "decimal.witness.json")
    result = _decode(witness.stdout)
    results = result.get("results")
    observed = {"primitive": cell["primitive"], "checked_value": str(checked_value)}
    if witness.return_code == 2 and results and results[0]["reason"] == "fragment-unsupported":
        native_exact = False
        observed.update(exit=2, reason="fragment-unsupported")
    elif witness.return_code == 0:
        _success(out, "replay", *args, "decimal.witness.json", "--raw")
        native_exact = True
        observed.update(exit=0, replay="accepted")
    else:
        raise ExampleError("unexpected decimal witness probe outcome")
    return {
        "axis": "exact-decimal-witness",
        "observed": observed,
        "opens_ld2": not native_exact,
        "requirement": "Reproduce the checked decimal time step in a witness.",
    }


def _subject_occurrence(facts: dict, subject: str) -> tuple[str, dict]:
    labels = facts.get("subject_label", [])
    for index, row in enumerate(labels):
        if row["subject"] == subject:
            return row["subject"], {"fact_type": "subject_label", "fact_index": index, "role": "subject"}
    raise ExampleError(f"case subject {subject} has no checked label occurrence")


def build(out: Path, *, fixture: Path = FIXTURE) -> dict:
    """Materialize a fresh packaged run and return its competency report."""
    cases = _load_reviewed(fixture, "cases.json", CASES_SHA)
    evidence = _load_reviewed(fixture, "support.json", SUPPORT_SHA)
    inputs = {
        case: (_read(fixture, f"{case}.txt"), _decode(_read(fixture, f"{case}.facts.json")))
        for case in CASES
    }
    answers = {
        case: _question_rows(cases[case], evidence[case], *inputs[case]) for case in CASES
    }
    comparison_facts, pairs, experiments = _comparison_inputs(_read(fixture, "comparison.json"))
    out.mkdir()
    vocabulary = _read(fixture, "vocabulary.orm.json")
    (out / "vocabulary.orm.json").write_bytes(vocabulary)
    case_outputs = {}
    for case, (document, facts) in inputs.items():
        folder = out / case
        folder.mkdir()
        (folder / "vocabulary.orm.json").write_bytes(vocabulary)
        (folder / "root.orm.json").write_bytes(_read(fixture, f"{case}.orm.json"))
        binding = _check_case(folder, "root.orm.json", document, facts)
        subject, occurrence = _subject_occurrence(facts, cases[case]["subject"])
        case_outputs[case] = {
            "subject": subject,
            "subject_occurrence": occurrence,
            "labels": facts.get("subject_label", []),
            "relationships": {relation: facts[relation] for relation in RELATIONS if relation in facts},
            "questions": answers[case],
            "binding": binding,
        }
    comparisons, comparison_sha = _checked_comparisons(out, comparison_facts, pairs, experiments)
    for suffix in ("orm", "population", "targets"):
        name = f"decimal.{suffix}.json"
        (out / name).write_bytes(_read(fixture, name))
    report = {
        "format": "literature-depth/1",
        "cases": case_outputs,
        "comparisons": comparisons,
        "synthetic_experiments": experiments,
        "synthetic_relationships": {
            relation: comparison_facts[relation] for relation in RELATIONS if relation in comparison_facts
        },
        "quantities": [_dimension_probe(), _percentage_probe(), _decimal_probe(out)],
        "bindings": {"case_sha256": CASES_SHA, "support_sha256": SUPPORT_SHA,
                     "comparison_population_sha256": comparison_sha},
    }
    _write(out, "report.json", report)
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        build(args.out)
    except (ArtifactError, OSError, ExampleError, UnicodeError) as error:
        print(f"literature-depth: {error}", file=sys.stderr)
        return 3
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
