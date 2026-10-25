"""``gnd discover`` service: one population in, induced candidates out (IK4).

Validation order (spec §4 rule 3): arguments (the parser), missing inputs, model
load, population load stamped against the model, candidate generation, one
``gnd check`` run over every surviving candidate, the admission filter,
candidate-against-candidate redundancy, outputs.
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
from dataclasses import replace
from datetime import datetime
from pathlib import Path
from typing import Any

from gnd import resolve_version
from gnd.checker import check
from gnd.discover import output
from gnd.discover.candidates import (
    CATALOGUE,
    FAMILIES,
    REDUNDANCY,
    Candidate,
    Catalogue,
    generate,
    redundancy,
)
from gnd.discover.support import PopulationView, Work
from gnd.errors import ModelLoadError, ModelValidationError, PopulationLoadError
from gnd.evolve.service import _operations_reference_set, _parse_model_text
from gnd.exits import EXIT_ILL_FORMED, EXIT_INTERNAL, EXIT_IO, EXIT_NO_INPUT, EXIT_OK
from gnd.model import load_model, load_model_bytes
from gnd.model_index import ModelIndex
from gnd.population import load_population, load_population_bytes

#: The IK2 induction-ref grammar the population's basename must satisfy.
_REF = re.compile(r"[A-Za-z0-9_][A-Za-z0-9._-]*")
MAX_EVIDENCE_REF = 256
NEAR_MISS_MAX = 32  # IK4-D3, with the 5% rule below


class DiscoveryDefect(Exception):
    """An internal invariant failed (exit 70)."""


def near_miss(violations: int, subjects: int) -> bool:
    """IK4-D3: ``1 <= v <= min(32, floor(0.05 d))``."""
    return 1 <= violations <= min(NEAR_MISS_MAX, (subjects * 5) // 100)


def _stderr(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)


def _eligible(view: PopulationView, document: dict[str, Any]) -> tuple[list[str], list[dict[str, str]]]:
    """Fact types discovery scans, and the skipped ones with a reason (IK4-D11)."""
    referenced = _operations_reference_set(document)
    eligible, skipped = [], []
    for fact_type in ModelIndex.for_model(view.model).iter_fact_types_shared():
        ft = str(fact_type.get("id"))
        if fact_type.get("derivation") in ("derived", "semiderived"):
            skipped.append({"fact_type": ft, "reason": "derived"})
        elif ft in referenced:
            skipped.append({"fact_type": ft, "reason": "referenced-by-operation"})
        else:
            eligible.append(ft)
    return eligible, skipped


def _subjects(view: PopulationView, candidate: Candidate) -> Candidate:
    if candidate.subjects is not None:
        return candidate
    if candidate.family == "uniqueness":
        roles = tuple(ModelIndex.constraint_roles(candidate.core))
        return replace(candidate, subjects=view.uniqueness(candidate.host, roles))
    role = next(r for r in view.roles[candidate.host] if r.name == candidate.core["role"])
    return replace(candidate, subjects=view.mandatory(role))


def _base_counts(model: Any) -> dict[str | None, int]:
    counts: dict[str | None, int] = {}
    for _, _, fact_type in ModelIndex.for_model(model).iter_constraints():
        host = str(fact_type.get("id")) if isinstance(fact_type, dict) else None
        counts[host] = counts.get(host, 0) + 1
    return counts


def _refs(candidates: list[Candidate], base: dict[str | None, int]) -> list[str]:
    seen = dict(base)
    refs = []
    for candidate in candidates:
        index = seen.get(candidate.host, 0)
        seen[candidate.host] = index + 1
        refs.append(
            f"fact_types[{candidate.host}].constraints[{index}]"
            if candidate.host is not None else f"constraints[{index}]"
        )
    return refs


def discover(
    model_path: Path,
    population_path: Path,
    *,
    families: tuple[str, ...],
    max_values: int,
    max_pairs: int,
) -> dict[str, Any]:
    """Run discovery; return the report fields plus private build inputs."""
    model_bytes = model_path.read_bytes()
    population_bytes = population_path.read_bytes()
    model = load_model(model_path)
    population = load_population(population_path, model=model)
    basename = population_path.name
    if len(basename) > MAX_EVIDENCE_REF or _REF.fullmatch(basename) is None:
        raise PopulationLoadError(
            f"population file name {basename!r} is not a valid induction evidence ref"
        )
    document = _parse_model_text(model_bytes.decode("utf-8"))
    work = Work()
    view = PopulationView(model, population, work)
    eligible, skipped_fact_types = _eligible(view, document)
    generated = generate(
        view, families=families, fact_types=eligible, max_values=max_values, max_pairs=max_pairs
    )
    catalogue = Catalogue(view, model)
    suppressed = dict.fromkeys(CATALOGUE + REDUNDANCY, 0)
    suppressed["redundant-frequency"] = generated.redundant_frequency
    rejected = {"vacuous": 0, "unchecked": 0, "fail": 0, "warning": 0}
    survivors: list[Candidate] = []
    for candidate in generated.candidates:
        rule = catalogue.rule(candidate)
        if rule is not None:
            suppressed[rule] += 1
            continue
        candidate = _subjects(view, candidate)
        if candidate.subjects.count == 0:
            rejected["vacuous"] += 1  # support 0: nothing to observe
            continue
        survivors.append(candidate)

    version = resolve_version()
    digest = hashlib.sha256(population_bytes).hexdigest()
    emitted: list[Candidate] = []
    near_misses: list[dict[str, Any]] = []
    if survivors:
        envelopes = [
            (c, output.induced(c, version=version, digest=digest, ref=basename)) for c in survivors
        ]
        checked = output.candidate_document(document, output.operations(envelopes))
        try:
            checked_model = load_model_bytes(
                output.candidate_text(checked).encode("utf-8"), source=model_path
            )
        except (ModelLoadError, ModelValidationError) as error:
            raise DiscoveryDefect(f"a generated candidate failed validation: {error}") from error
        checked_population = load_population_bytes(
            population_bytes, source=population_path, model=checked_model
        )
        report = check(checked_model, checked_population)
        verdicts = {v.constraint_ref: v.verdict for v in report.verdicts}
        for candidate, ref in zip(survivors, _refs(survivors, _base_counts(model)), strict=True):
            verdict = verdicts.get(ref)
            subjects = candidate.subjects
            if verdict == "pass":
                if subjects.violations:
                    raise DiscoveryDefect(f"{ref} passes but discovery counted violations")
                emitted.append(candidate)
                continue
            if verdict not in rejected:
                raise DiscoveryDefect(f"{ref} has no check verdict ({verdict!r})")
            rejected[verdict] += 1
            if verdict in ("fail", "warning") and near_miss(subjects.violations, subjects.count):
                near_misses.append({
                    "family": candidate.family,
                    "host": candidate.host,
                    "constraint": candidate.core,
                    "violations": subjects.violations,
                    "subjects": subjects.count,
                    "counterexamples": list(subjects.counterexamples),
                })
    emitted, redundant = redundancy(emitted)
    for rule, count in redundant.items():
        suppressed[rule] += count
    final = [(c, output.induced(c, version=version, digest=digest, ref=basename)) for c in emitted]
    refs = _refs(emitted, _base_counts(model))
    return {
        "model_bytes": model_bytes,
        "document": document,
        "final": final,
        "fields": {
            "schema_version": output.REPORT_SCHEMA_VERSION,
            "tool": "gnd",
            "command": "discover",
            "gnd_version": version,
            "model": {"path": str(model_path), "sha256": hashlib.sha256(model_bytes).hexdigest()},
            "population": {"path": str(population_path), "sha256": digest},
            "bounds": {
                "families": [f for f in FAMILIES if f in families],
                "max_values": max_values,
                "max_pairs": max_pairs,
                "max_key_arity": 4,
            },
            "skipped": {
                "fact_types": skipped_fact_types,
                "value_roles": generated.skipped_value_roles,
                "pairs": generated.skipped_pairs,
                "key_subsets": generated.skipped_key_subsets,
            },
            "rejected": rejected,
            "suppressed": suppressed,
            "emitted": [
                {"ref": ref, "family": c.family, "constraint": constraint,
                 "support": constraint["provenance"]["induction"]["support"]}
                for ref, (c, constraint) in zip(refs, final, strict=True)
            ],
            "near_misses": near_misses,
            "work": work.report(),
        },
    }


def _cmd_discover(
    model: str,
    population: str,
    *,
    out: str,
    report: str,
    actor: str,
    requested_at: datetime,
    families: tuple[str, ...],
    max_values: int,
    max_pairs: int,
    output_format: str,
) -> int:
    model_path, population_path = Path(model), Path(population)
    for path in (model_path, population_path):
        if not path.is_file():
            _stderr(f"input {path} does not exist")
            return EXIT_NO_INPUT
    try:
        result = discover(
            model_path, population_path,
            families=families, max_values=max_values, max_pairs=max_pairs,
        )
    except (ModelLoadError, ModelValidationError, PopulationLoadError) as error:
        _stderr(str(error))
        return EXIT_ILL_FORMED
    except DiscoveryDefect as error:
        _stderr(f"internal: {error}")
        return EXIT_INTERNAL
    except OSError as error:
        _stderr(f"could not read input: {error}")
        return EXIT_IO
    fields = result["fields"]
    out_path, report_path = Path(out), Path(report)
    try:
        if result["final"]:
            ops = output.operations(result["final"])
            built = output.proposal(
                model_bytes=result["model_bytes"],
                document=output.candidate_document(result["document"], ops),
                ops=ops,
                actor=actor,
                requested_at=requested_at,
                population_name=population_path.name,
            )
            output.write(out_path, output.canonical_bytes(built.model_dump(mode="json")))
            fields["proposal"] = str(out_path)
        else:
            fields["proposal"] = None
        output.write(report_path, output.canonical_bytes(fields))
    except OSError as error:
        _stderr(f"could not write output: {error}")
        return EXIT_IO
    if output_format == "json":
        sys.stdout.write(json.dumps(fields, indent=2, sort_keys=True, ensure_ascii=False) + "\n")
    else:
        sys.stdout.write(output.render_text(fields))
    return EXIT_OK
