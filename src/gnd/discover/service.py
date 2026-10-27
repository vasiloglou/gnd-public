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
from gnd.discover.support import PopulationView, Work, work_ceiling
from gnd.errors import ModelLoadError, ModelValidationError, PopulationLoadError
from gnd.evolve.service import (
    MAX_EVOLUTION_PROPOSAL_BYTES,
    _operations_reference_set,
    _parse_model_text,
)
from gnd.exits import (
    EXIT_COLLISION,
    EXIT_ILL_FORMED,
    EXIT_INTERNAL,
    EXIT_IO,
    EXIT_NO_INPUT,
    EXIT_OK,
    EXIT_USAGE,
)
from gnd.model import MAX_MODEL_BYTES, load_model_bytes
from gnd.model_index import ModelIndex
from gnd.population import MAX_POPULATION_BYTES, load_population_bytes
from gnd.redaction import RedactionPolicy
from gnd.references import ReferenceInputError

#: The IK2 induction-ref grammar the population's basename must satisfy.
_REF = re.compile(r"[A-Za-z0-9_][A-Za-z0-9._-]*")
MAX_EVIDENCE_REF = 256
NEAR_MISS_MAX = 32  # IK4-D3, with the 5% rule below
BUDGET_MARGIN = 256 * 1024  # proposal envelope, audit and JSON escaping headroom


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


def _read_capped(path: Path, cap: int, error: type[Exception], label: str) -> bytes:
    """Read one input once, never more than ``cap + 1`` bytes (review R10)."""
    with path.open("rb") as handle:
        data = handle.read(cap + 1)
    if len(data) > cap:
        raise error(f"{label} file '{path}' exceeds the {cap}-byte input cap")
    return data


def _bind_references(model: Any, population: Any, root: Path) -> tuple[Any, Any]:
    """Bind declared reference populations as loading the model by path does (R3).

    A model loaded from bytes is unbound; its reference files resolve against
    the model's own directory. Returns the combined population and the context
    the check run needs."""
    if not model.reference_populations:
        return population, None
    from gnd.model import bind_declared_references
    from gnd.references import bind_population

    context = bind_declared_references(model, root=root, attach=True)
    return bind_population(model, population, references=context).combined, context


def _derived_object_types(view: PopulationView) -> frozenset[str]:
    played = set()
    for fact_type in ModelIndex.for_model(view.model).iter_fact_types_shared():
        if fact_type.get("derivation") in ("derived", "semiderived"):
            played.update(role.object_type for role in view.roles.get(str(fact_type.get("id")), []))
    return frozenset(played)


def _within_budget(
    survivors: list[tuple[Candidate, dict[str, Any]]], base: int
) -> tuple[list[tuple[Candidate, dict[str, Any]]], int]:
    """Keep candidates, in emission order, while the proposal stays under its caps.

    The proposal carries the candidate model as text and every constraint again
    in its operation, so a constraint costs about three times its JSON size and
    the model about twice its own (review R6)."""
    budget = min(MAX_MODEL_BYTES, MAX_EVOLUTION_PROPOSAL_BYTES) - BUDGET_MARGIN - 2 * base
    kept, used = [], 0
    for candidate, constraint in survivors:
        cost = 3 * len(output.candidate_text(constraint).encode("utf-8"))
        if used + cost > budget:
            continue
        used += cost
        kept.append((candidate, constraint))
    return kept, len(survivors) - len(kept)


def discover(
    model_path: Path,
    population_path: Path,
    *,
    families: tuple[str, ...],
    max_values: int,
    max_pairs: int,
) -> dict[str, Any]:
    """Run discovery; return the report fields plus private build inputs."""
    model_bytes = _read_capped(model_path, MAX_MODEL_BYTES, ModelLoadError, "model")
    population_bytes = _read_capped(
        population_path, MAX_POPULATION_BYTES, PopulationLoadError, "population"
    )
    model = load_model_bytes(model_bytes, source=model_path)
    population = load_population_bytes(population_bytes, source=population_path, model=model)
    basename = population_path.name
    if len(basename) > MAX_EVIDENCE_REF or _REF.fullmatch(basename) is None:
        raise PopulationLoadError(
            f"population file name {basename!r} is not a valid induction evidence ref"
        )
    population, _ = _bind_references(model, population, model_path.parent)
    document = _parse_model_text(model_bytes.decode("utf-8"))
    work = Work()
    view = PopulationView(model, population, work)
    eligible, skipped_fact_types = _eligible(view, document)
    generated = generate(
        view, families=families, fact_types=eligible, max_values=max_values,
        max_pairs=max_pairs,
        redacted=RedactionPolicy.from_model(model).effective_roles,
        derived_object_types=_derived_object_types(view),
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
    envelopes = [
        (c, output.induced(c, version=version, digest=digest, ref=basename)) for c in survivors
    ]
    envelopes, over_budget = _within_budget(
        envelopes, len(output.candidate_text(document).encode("utf-8"))
    )
    survivors = [c for c, _ in envelopes]
    emitted: list[Candidate] = []
    near_misses: list[dict[str, Any]] = []
    if survivors:
        checked = output.candidate_document(document, output.operations(envelopes))
        try:
            checked_model = load_model_bytes(
                output.candidate_text(checked).encode("utf-8"), source=model_path
            )
        except (ModelLoadError, ModelValidationError) as error:
            # Never echo the candidate: it may carry population values (R2).
            rules = sorted({i.rule_id for i in getattr(error, "issues", ())})
            raise DiscoveryDefect(f"a generated candidate failed validation {rules}") from error
        checked_population, references = _bind_references(
            checked_model,
            load_population_bytes(population_bytes, source=population_path, model=checked_model),
            model_path.parent,
        )
        try:
            report = check(checked_model, checked_population, references=references)
        except Exception as error:
            raise DiscoveryDefect(f"the check run failed ({type(error).__name__})") from error
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
                raise DiscoveryDefect(f"{ref} has no check verdict")
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
    ceiling = work_ceiling(view, eligible, generated.pairs_compared)
    if sum(work.counts.values()) > ceiling:
        raise DiscoveryDefect("discovery work exceeded its stated ceiling")
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
                "redacted_value_roles": generated.skipped_redacted_value_roles,
                "unrepresentable_value_roles": generated.skipped_unrepresentable_value_roles,
                "derived_mandatory_roles": generated.skipped_derived_mandatory_roles,
                "pairs": generated.skipped_pairs,
                "key_subsets": generated.skipped_key_subsets,
                "over_budget": over_budget,
            },
            "rejected": rejected,
            "suppressed": suppressed,
            "emitted": [
                {"ref": ref, "family": c.family, "constraint": constraint,
                 "support": constraint["provenance"]["induction"]["support"]}
                for ref, (c, constraint) in zip(refs, final, strict=True)
            ],
            "near_misses": near_misses,
            "work": work.report(ceiling),
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
    out_path, report_path = Path(out), Path(report)
    resolved = [p.resolve() for p in (out_path, report_path, model_path, population_path)]
    if len(set(resolved)) != len(resolved):
        # --out, --report and the two inputs must be four different files (R9).
        _stderr("--out, --report, MODEL and POPULATION must be four different paths")
        return EXIT_USAGE
    for path in (model_path, population_path):
        if not path.is_file():
            _stderr(f"input {path} does not exist")
            return EXIT_NO_INPUT
    if out_path.is_symlink():
        _stderr(f"refusing to write through symbolic link {out_path}")
        return EXIT_IO
    if out_path.exists():
        # Owner ruling IK4-Q1 (2026-10-25): an existing proposal is never
        # overwritten or left beside a newer report; the run refuses first.
        _stderr(f"--out {out_path} already exists; nothing was written")
        return EXIT_COLLISION
    try:
        result = discover(
            model_path, population_path,
            families=families, max_values=max_values, max_pairs=max_pairs,
        )
    except (ModelLoadError, ModelValidationError, PopulationLoadError, ReferenceInputError) as error:
        _stderr(str(error))
        return EXIT_ILL_FORMED
    except DiscoveryDefect as error:
        _stderr(f"internal: {error}")
        return EXIT_INTERNAL
    except OSError as error:
        _stderr(f"could not read input: {error}")
        return EXIT_IO
    fields = result["fields"]
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
