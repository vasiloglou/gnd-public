"""Score the frozen synthetic diagnostic corpus using its predeclared sample."""

from __future__ import annotations

import argparse
import json
import random
from pathlib import Path

from .assurance_report import Refusal
from .name_diagnostics import SCORES, diagnose, read_diagnostic_input

SAMPLE = 100
MINIMUM_PER_KIND = 20
SEED = 193


def _quotas(sizes: dict[str, int]) -> dict[str, int]:
    if sum(sizes.values()) < SAMPLE:
        return sizes.copy()
    floors = {kind: min(MINIMUM_PER_KIND, count) for kind, count in sizes.items()}
    remaining = SAMPLE - sum(floors.values())
    capacities = {kind: count - floors[kind] for kind, count in sizes.items()}
    capacity = sum(capacities.values())
    counts = floors.copy()
    fractions = {}
    for kind, room in capacities.items():
        allocation, fraction = divmod(remaining * room, capacity)
        counts[kind] += allocation
        fractions[kind] = fraction
    for kind in sorted(counts, key=lambda item: (-fractions[item], item))[:SAMPLE - sum(counts.values())]:
        counts[kind] += 1
    return counts


def score(emissions: list[dict], labels: dict[tuple[str, str], str | None]) -> dict:
    """Sample uniformly within each kind and report exact false-discovery counts."""
    strata = {kind: [] for kind in sorted(SCORES)}
    for emission in emissions:
        strata[emission["kind"]].append(tuple(emission["occurrences"]))
    quotas = _quotas({kind: len(rows) for kind, rows in strata.items()})
    randomizer = random.Random(SEED)
    result = {}
    for kind, rows in strata.items():
        ordered = sorted(rows)
        draw = sorted(randomizer.sample(ordered, quotas[kind])) if quotas[kind] < len(ordered) else ordered
        wrong = [pair for pair in draw if labels.get(pair) != kind]
        denominator = len(draw)
        measured = denominator >= MINIMUM_PER_KIND
        result[kind] = {
            "emitted": len(rows),
            "sampled": draw,
            "wrong_pairs": wrong,
            "false_discoveries": len(wrong),
            "denominator": denominator,
            "false_discovery_fraction": [len(wrong), denominator] if measured else None,
            "status": ("pass" if 5 * len(wrong) <= denominator else "fail") if measured else "unmeasured",
        }
    return result


def _labels(data: object) -> tuple[str, dict[tuple[str, str], str | None]]:
    if (not isinstance(data, dict)
            or set(data) != {"schema", "labeller", "independent", "unlisted_pair_kind", "labels"}
            or data["schema"] != "literature-diagnostic-labels/1"
            or not isinstance(data["labeller"], str) or data["independent"] is not False
            or data["unlisted_pair_kind"] is not None or not isinstance(data["labels"], list)):
        raise Refusal("labels:schema")
    labels = {}
    for row in data["labels"]:
        if not isinstance(row, dict) or set(row) != {"pair", "kind", "story", "name_seed"}:
            raise Refusal("labels:schema")
        pair, kind = row["pair"], row["kind"]
        if (not isinstance(pair, list) or len(pair) != 2 or not all(isinstance(item, str) for item in pair)
                or pair[0] >= pair[1] or kind not in (*SCORES, None) or tuple(pair) in labels
                or not all(isinstance(row[field], str) and row[field] for field in ("story", "name_seed"))):
            raise Refusal("labels:schema")
        labels[tuple(pair)] = kind
    return data["labeller"], labels


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("occurrences", type=Path)
    parser.add_argument("labels", type=Path)
    args = parser.parse_args(argv)
    output = {"schema": "literature-diagnostics-measurement/1", "exit_code": 0}
    try:
        data, input_digest = read_diagnostic_input(args.occurrences)
        label_data, label_digest = read_diagnostic_input(args.labels)
        labeller, labels = _labels(label_data)
        emitted = diagnose(data)
        metrics = score(emitted, labels)
        output.update(input_sha256=input_digest, labels_sha256=label_digest, labeller=labeller, independent=False,
                      seed=SEED, sample_target=SAMPLE, budget=[1, 5], kinds=metrics,
                      exit_code=int(any(item["status"] == "fail" for item in metrics.values())))
    except (Refusal, ValueError, UnicodeError, RecursionError):
        output.update(exit_code=3, reason="input:invalid")
    print(json.dumps(output, indent=2, sort_keys=True))
    return output["exit_code"]


if __name__ == "__main__":
    raise SystemExit(main())
