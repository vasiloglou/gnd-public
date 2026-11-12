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

from gnd import input_policy as _rf7_input
from gnd import resolve_version
from gnd.artifacts import ArtifactError
from gnd.checker import check
from gnd.discover import joined, output, types
from gnd.discover import type_evidence as evidence
from gnd.discover import type_judgements as judgements
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
from gnd.evolve._includes import IncludeInputError, exclude_input_outputs, included_hosts
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
from gnd.model import MAX_MODEL_BYTES, _load_model_bytes_captured
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


def _proposal_bytes(
    result: dict[str, Any], actor: str, requested_at: str, population_path: Path
) -> tuple[bytes, bool]:
    """The written proposal, and whether it and its candidate model fit their caps."""
    ops = output.operations(result["final"], included_hosts=included_hosts(result["view"].model)) + result["type_operations"]
    document = output.candidate_document(result["document"], ops)
    model_fits = len(output.candidate_text(document).encode("utf-8")) <= MAX_MODEL_BYTES
    built = output.proposal(
        model_bytes=result["model_bytes"],
        document=document,
        ops=ops,
        actor=actor,
        requested_at=requested_at,
        population_name=population_path.name,
        **({"rationale": f"gnd discover: {len(ops)} candidate operations observed in "
                         f"{population_path.name}" + result.get("judged_from", "")}
           if result["type_operations"] else {}),
    )
    raw = output.canonical_bytes(built.model_dump(mode="json"))
    return raw, model_fits and len(raw) <= MAX_EVOLUTION_PROPOSAL_BYTES


def discover(
    model_path: Path,
    population_path: Path,
    *,
    families: tuple[str, ...],
    max_values: int,
    max_pairs: int,
    min_support: int = 20,
    show_values: bool = False,
    show_digests: bool = True,
    joined_settings: joined.Settings | None = None,
) -> dict[str, Any]:
    """Run discovery; return the report fields plus private build inputs."""
    joined.require_family(families, joined_settings)
    model_bytes = _read_capped(model_path, MAX_MODEL_BYTES, ModelLoadError, "model")
    population_bytes = _read_capped(
        population_path, MAX_POPULATION_BYTES, PopulationLoadError, "population"
    )
    model = _load_model_bytes_captured(model_bytes, source=model_path)
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
    if types.FAMILY in families:
        types.generic_declarations(view)  # an invalid declaration refuses first
    redacted = RedactionPolicy.from_model(model).effective_roles
    generated = generate(
        view, families=families, fact_types=eligible, max_values=max_values,
        max_pairs=max_pairs,
        redacted=redacted,
        derived_object_types=_derived_object_types(view),
    )
    joined_report = None
    declared_guards = set()
    if joined_settings is not None:
        joined_candidates, joined_report = joined.generate(
            view, joined_settings, eligible=eligible, redacted=redacted
        )
        declared = list(ModelIndex.for_model(model).iter_constraints_shared())
        declared_guards = {
            joined.guard_key(constraint)
            for _, constraint, _ in declared if constraint.get("type") == "guarded"
        }
        declared_ids = {constraint.get("id") for _, constraint, _ in declared}
        if any(
            c.core["id"] in declared_ids and joined.guard_key(c.core) not in declared_guards
            for c in joined_candidates
        ):
            joined_report["reason"] = "rule-id-collision"
        else:
            generated.candidates.extend(joined_candidates)
    catalogue = Catalogue(view, model)
    suppressed = dict.fromkeys(CATALOGUE + REDUNDANCY, 0)
    suppressed["redundant-frequency"] = generated.redundant_frequency
    rejected = {"vacuous": 0, "unchecked": 0, "fail": 0, "warning": 0}
    survivors: list[Candidate] = []
    for candidate in generated.candidates:
        if candidate.family == joined.FAMILY:
            rule = "declared" if joined.guard_key(candidate.core) in declared_guards else None
        else:
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
        checked = output.candidate_document(document, output.operations(envelopes, included_hosts=included_hosts(model)))
        try:
            checked_model = _load_model_bytes_captured(
                output.candidate_text(checked).encode("utf-8"), source=model_path, candidate=True
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
        verdicts = {v.constraint_ref: v for v in report.verdicts}
        for candidate, ref in zip(survivors, _refs(survivors, _base_counts(model)), strict=True):
            observed = verdicts.get(ref)
            verdict = None if observed is None else observed.verdict
            subjects = candidate.subjects
            if candidate.family == joined.FAMILY and (
                observed is None or observed.binding_count != subjects.count
                or len(observed.offending_facts) != subjects.violations
                or verdict != ("warning" if subjects.violations else "pass")
                or (near_miss(subjects.violations, subjects.count) and not joined.matches_counterexamples(
                    view, joined_settings, subjects.counterexamples, observed.offending_facts,
                ))
            ):
                raise DiscoveryDefect(f"{ref} disagrees with joined discovery support or verdict")
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
    type_proposals = None
    if types.FAMILY in families:
        envelope = {"inducer": {"name": output.INDUCER, "version": version}, "method": output.INDUCER,
                    "manifest_sha256": digest, "evidence": [{"ref": basename, "sha256": digest}]}
        spent = 3 * sum(len(output.candidate_text(constraint).encode("utf-8")) for _, constraint in final)
        budget = (min(MAX_MODEL_BYTES, MAX_EVOLUTION_PROPOSAL_BYTES) - BUDGET_MARGIN
                  - 2 * len(output.candidate_text(document).encode("utf-8")) - spent)
        type_arguments = {
            "view": view, "eligible": eligible, "min_support": min_support, "show_values": show_values,
            "show_digests": show_digests, "redacted": RedactionPolicy.from_model(model).effective_roles,
            "envelope": envelope, "budget": budget,
        }
        type_proposals = types.propose(**type_arguments)
    fields_extra = {} if type_proposals is None else {"fact_type_proposals": type_proposals.report}
    if joined_report is not None:
        fields_extra["joined_rules"] = joined_report
    return {
        "model_bytes": model_bytes,
        "document": document,
        "final": final,
        "type_operations": () if type_proposals is None else tuple(type_proposals.operations),
        "type_proposals": type_proposals,
        # So a judged run re-proposes with the same inputs (TS2).
        "type_arguments": None if type_proposals is None else type_arguments,
        "view": view,
        "fields": {
            "schema_version": output.REPORT_SCHEMA_VERSION,
            "tool": "gnd",
            "command": "discover",
            "gnd_version": version,
            "model": {"path": str(model_path), "sha256": hashlib.sha256(model_bytes).hexdigest()},
            "population": {"path": str(population_path), "sha256": digest},
            "bounds": {
                "families": [f for f in (*FAMILIES, types.FAMILY, joined.FAMILY) if f in families],
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
            **fields_extra,
        },
    }


def _trimmed_proposal(
    result: dict[str, Any], actor: str, requested_at: datetime, population_path: Path
) -> bytes | None:
    """The proposal bytes to write, or None when nothing is emitted."""
    if not (result["final"] or result["type_operations"]):
        return None
    proposal_bytes, fits = _proposal_bytes(result, actor, requested_at, population_path)
    types_ = result["type_proposals"]
    # The size estimate is a pre-filter; the written bytes decide
    # (close review): drop type groups from the tail, in steps, until
    # both caps hold. The other families keep their own estimate, so
    # without type groups the proposal is written as before.
    while not fits and types_ is not None and types_.group_sizes:
        types_.drop_last(max(1, len(types_.group_sizes) // 16))
        result["type_operations"] = tuple(types_.operations)
        if not (result["final"] or result["type_operations"]):
            return None
        proposal_bytes, fits = _proposal_bytes(result, actor, requested_at, population_path)
    return proposal_bytes


def _evidence(result: dict[str, Any], min_support: int, show_values: bool, show_digests: bool) -> dict[str, Any]:
    fields = result["fields"]
    return evidence.build_evidence(
        result["view"], result["type_proposals"],
        model_sha256=fields["model"]["sha256"], population_sha256=fields["population"]["sha256"],
        min_support=min_support, show_values=show_values, show_digests=show_digests,
        redacted_generics=result["type_proposals"].redacted_generics,
        redacted_roles=RedactionPolicy.from_model(result["view"].model).effective_roles,
    )


def _induced(view: PopulationView, proposals: types.TypeProposals) -> dict[int, list[str]]:
    """Per group position, the fact types whose induced_from names its attribute (D4)."""
    by_origin: dict[tuple[str, str], list[str]] = {}
    for fact_id, origin in evidence.origins(view).items():
        if origin is not None:
            by_origin.setdefault((origin["generic"], origin["attribute_sha256"]), []).append(fact_id)
    return {number: by_origin[record.generic, record.attribute_sha256]
            for number, record in enumerate(proposals.groups)
            if (record.generic, record.attribute_sha256) in by_origin}


_BOUND_KEYS = ("model_sha256", "population_sha256", "min_support", "show_values", "show_digests")


def _first_difference(given: bytes, recomputed: bytes) -> str:
    """Which bound setting differs, by key only: the evidence may hold values."""
    try:
        old = _rf7_input.loads(given)
    except (ValueError, RecursionError):
        return "the evidence is not this run's evidence"
    new = _rf7_input.loads(recomputed)
    if isinstance(old, dict):
        for key in _BOUND_KEYS:
            if old.get(key) != new[key]:
                return f"{key} differs from this run's; the evidence does not bind this model, population and settings"
    return "groups differ from this run's; the evidence does not bind this model, population and settings"


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
    min_support: int = 20,
    show_values: bool = False,
    show_digests: bool = True,
    type_evidence: str | None = None,
    type_evidence_in: str | None = None,
    duplicate_judgements: str | None = None,
    shape_judgements: str | None = None,
    joined_settings: joined.Settings | None = None,
) -> int:
    try:
        joined.require_family(families, joined_settings)
    except ValueError as error:
        _stderr(str(error))
        return EXIT_USAGE
    model_path, population_path = Path(model), Path(population)
    out_path, report_path = Path(out), Path(report)
    evidence_path = None if type_evidence is None else Path(type_evidence)
    evidence_in = None if type_evidence_in is None else Path(type_evidence_in)
    judgement_paths = {kind: Path(path) for kind, path in
                       (("duplicates", duplicate_judgements), ("shapes", shape_judgements)) if path is not None}
    judging = evidence_in is not None or bool(judgement_paths)
    if (evidence_path is not None or judging) and types.FAMILY not in families:
        _stderr("--type-evidence, --type-evidence-in and the judgements options need --families fact-type")
        return EXIT_USAGE
    if judging and (evidence_in is None or not judgement_paths):
        _stderr("--duplicate-judgements and --shape-judgements need --type-evidence-in, and it needs one of them")
        return EXIT_USAGE
    if judging and evidence_path is not None:
        _stderr("--type-evidence cannot be combined with --type-evidence-in")
        return EXIT_USAGE
    outputs = (out_path, report_path) + (() if evidence_path is None else (evidence_path,))
    inputs = (model_path, population_path) + (() if evidence_in is None else (evidence_in,)) + tuple(
        judgement_paths.values())
    resolved = [p.resolve() for p in (*outputs, *inputs)]
    if len(set(resolved)) != len(resolved):
        # --out, --report and the two inputs must be four different files (R9);
        # with --type-evidence, five (TS1); with judgements, every path (TS2).
        if judging:
            _stderr("--out, --report, MODEL, POPULATION, --type-evidence-in and the judgements files "
                    "must be different paths")
        elif evidence_path is None:
            _stderr("--out, --report, MODEL and POPULATION must be four different paths")
        else:
            _stderr("--out, --report, --type-evidence, MODEL and POPULATION must be five different paths")
        return EXIT_USAGE
    for path in inputs:
        if not path.is_file():
            _stderr(f"input {path} does not exist")
            return EXIT_NO_INPUT
    if out_path.is_symlink():
        _stderr(f"refusing to write through symbolic link {out_path}")
        return EXIT_IO
    if evidence_path is not None and evidence_path.is_symlink():
        _stderr(f"refusing to write through symbolic link {evidence_path}")
        return EXIT_IO
    if out_path.exists():
        # Owner ruling IK4-Q1 (2026-10-25): an existing proposal is never
        # overwritten or left beside a newer report; the run refuses first.
        _stderr(f"--out {out_path} already exists; nothing was written")
        return EXIT_COLLISION
    if evidence_path is not None and evidence_path.exists():
        _stderr(f"--type-evidence {evidence_path} already exists; nothing was written")
        return EXIT_COLLISION
    evidence_raw, documents, digests = b"", {}, {}
    if judging:
        # The judgements and their binding are checked before the model or
        # the population is read, so a wrong file refuses cheaply (TS2 §6.1).
        try:
            with evidence_in.open("rb") as handle:
                evidence_raw = handle.read(evidence.MAX_EVIDENCE_BYTES + 1)
            if len(evidence_raw) > evidence.MAX_EVIDENCE_BYTES:
                raise judgements.TypeJudgementError(
                    f"--type-evidence-in: the file exceeds {evidence.MAX_EVIDENCE_BYTES} bytes")
            evidence_sha256 = hashlib.sha256(evidence_raw).hexdigest()
            for kind, path in judgement_paths.items():
                documents[kind], digests[kind] = judgements.read(path, kind=kind)
                judgements.check_binding(documents[kind], kind=kind, evidence_sha256=evidence_sha256)
        except judgements.TypeJudgementError as error:
            _stderr(str(error))
            return EXIT_ILL_FORMED
        except OSError as error:
            _stderr(f"could not read input: {error}")
            return EXIT_IO
    try:
        result = discover(
            model_path, population_path,
            families=families, max_values=max_values, max_pairs=max_pairs,
            min_support=min_support, show_values=show_values, show_digests=show_digests,
            joined_settings=joined_settings,
        )
        loaded = result["view"].model
        if loaded.includes:
            exclude_input_outputs(model_path, loaded._included, outputs)
    except (IncludeInputError, ModelLoadError, ModelValidationError, PopulationLoadError, ReferenceInputError,
            types.GenericDeclarationError) as error:
        _stderr(str(error))
        return EXIT_ILL_FORMED
    except ArtifactError as error:
        # The reference binder is discover's only artifact read, and it passes
        # its own refusal through (IK4-Q2-R1). IKE-Q3 D1-A: evolve's exits, a
        # missing file 66 and any other refused path 74, judged by the cause
        # chain as evolve judges it.
        _stderr(f"reference population: {error}")
        cause: BaseException | None = error
        while cause is not None and not isinstance(cause, FileNotFoundError):
            cause = cause.__cause__
        return EXIT_NO_INPUT if cause is not None else EXIT_IO
    except DiscoveryDefect as error:
        _stderr(f"internal: {error}")
        return EXIT_INTERNAL
    except OSError as error:
        _stderr(f"could not read input: {error}")
        return EXIT_IO
    fields = result["fields"]
    try:
        proposal_bytes = _trimmed_proposal(result, actor, requested_at, population_path)
    except OSError as error:
        _stderr(f"could not write output: {error}")
        return EXIT_IO
    if judging:
        # TS2: the evidence must be what this run would write without
        # judgement, statuses final; then the verdicts are bound and the
        # family proposes again with them.
        try:
            recomputed = evidence.evidence_bytes(_evidence(result, min_support, show_values, show_digests))
            if recomputed != evidence_raw:
                raise judgements.TypeJudgementError(
                    f"--type-evidence-in: {_first_difference(evidence_raw, recomputed)}")
            verdicts = judgements.bind(_rf7_input.loads(recomputed), documents,
                                       induced=_induced(result["view"], result["type_proposals"]))
            if not show_values:
                hidden = [text for record in result["type_proposals"].groups
                          for text in (types.cell_text(record.attribute), *record.values,
                                       *(() if show_digests else (record.attribute_sha256,)))]
                judgements.scan_free_text(documents, hidden, result["model_bytes"].decode("utf-8"))
        except (evidence.TypeEvidenceError, judgements.TypeJudgementError) as error:
            _stderr(str(error))
            return EXIT_ILL_FORMED
        except evidence.TypeEvidenceOverflow as error:
            _stderr(f"internal: {error}")
            return EXIT_INTERNAL
        judged = types.propose(**result["type_arguments"], verdicts=verdicts, judgement={
            "evidence_sha256": hashlib.sha256(evidence_raw).hexdigest(),
            **{kind: (None if kind not in documents else
                      {"sha256": digests[kind], "skill": documents[kind]["judge"]["skill"]})
               for kind in ("duplicates", "shapes")},
        })
        result["type_proposals"] = judged
        result["type_operations"] = tuple(judged.operations)
        result["judged_from"] = "; fact-type verdicts from " + ", ".join(
            judgement_paths[kind].name for kind in ("duplicates", "shapes") if kind in documents)
        fields["fact_type_proposals"] = judged.report
        try:
            proposal_bytes = _trimmed_proposal(result, actor, requested_at, population_path)
        except OSError as error:
            _stderr(f"could not write output: {error}")
            return EXIT_IO
    fields["proposal"] = None if proposal_bytes is None else str(out_path)
    evidence_bytes = None
    if evidence_path is not None:
        # Built after the written-bytes trim, so every status is final, and
        # before any write, so a malformed induced_from writes nothing (TS1).
        try:
            evidence_bytes = evidence.evidence_bytes(_evidence(result, min_support, show_values, show_digests))
        except evidence.TypeEvidenceError as error:
            _stderr(str(error))
            return EXIT_ILL_FORMED
        except evidence.TypeEvidenceOverflow as error:
            _stderr(f"internal: {error}")
            return EXIT_INTERNAL
    try:
        if proposal_bytes is not None:
            output.write(out_path, proposal_bytes)
        output.write(report_path, output.canonical_bytes(fields))
        if evidence_bytes is not None:
            output.write(evidence_path, evidence_bytes)
    except OSError as error:
        _stderr(f"could not write output: {error}")
        return EXIT_IO
    if output_format == "json":
        sys.stdout.write(json.dumps(fields, indent=2, sort_keys=True, ensure_ascii=False) + "\n")
    else:
        sys.stdout.write(output.render_text(fields))
    return EXIT_OK
