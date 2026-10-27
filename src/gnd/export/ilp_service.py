"""``gnd export ilp`` and ``gnd import ilp-rules``: the ILP bridge service (IK5).

Contract page: ``docs/reference/ilp-bridge.md``. Spec:
``.gnd-planning/milestones/induced-knowledge/notes/phase-IK5-spec.md``.

**Export** validation order (spec §4 rule 3): arguments, the manifest read and
schema, the mode check, model load, binding, each population (path, digest,
load), representability, render, write.

**Import** validation order: arguments, the clauses read, the run-record read,
the clause-digest binding, the manifest read and mode check, model load,
binding, the export recomputed and its digest compared, the learner binding,
the coverage shape, the fragment checks per clause, candidate-model validation,
re-evaluation, the set comparison, then the proposal write. Every refusal is
exit 3 with a named reason (IK5-D8) and writes nothing; admission is
all-or-nothing (IK5-D9). GND computes coverage and support itself; the
learner's sets are only compared (IK-R2).
"""

from __future__ import annotations

import hashlib
import json
import sys
from dataclasses import dataclass, field
from datetime import UTC, datetime
from importlib.resources import files
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from gnd import input_policy as _rf7_input
from gnd.errors import ModelLoadError, ModelValidationError
from gnd.exits import (
    EXIT_COLLISION,
    EXIT_ILL_FORMED,
    EXIT_INTERNAL,
    EXIT_IO,
    EXIT_NO_INPUT,
    EXIT_OK,
)
from gnd.export import ilp as _ilp
from gnd.export import ilp_learners as _learners
from gnd.export.ilp import IlpError
from gnd.export.ilp_rewrite import rewrite
from gnd.measure import labels as _labels

__all__ = ["_cmd_export_ilp", "_cmd_import_ilp_rules"]

#: IK5-D14: bounds fixed before results.
CLAUSES_CAP = 1024 * 1024
RUN_CAP = 32 * 1024 * 1024
MAX_DEPTH = 4
INDUCTION_EXAMPLES = 256
INDUCTION_COUNTEREXAMPLES = 32


def _stderr(message: str) -> None:
    print(message, file=sys.stderr)


def _schema(name: str) -> Draft202012Validator:
    text = files("gnd").joinpath(name).read_text(encoding="utf-8")
    return Draft202012Validator(_rf7_input.loads(text))


def _validate(document: Any, name: str, version: str, label: str) -> None:
    errors = sorted(_schema(name).iter_errors(document), key=lambda e: list(e.absolute_path))
    if errors:
        first = errors[0]
        where = "/".join(str(part) for part in first.absolute_path) or "(root)"
        raise IlpError(EXIT_ILL_FORMED, f"{label} fails {version} at {where}: {first.message}")


def _read_capped(path: Path, cap: int, label: str) -> bytes:
    if path.is_symlink():
        raise IlpError(EXIT_IO, f"refusing {label} {path}: it is a symbolic link")
    try:
        with path.open("rb") as handle:
            data = handle.read(cap + 1)
    except FileNotFoundError:
        raise IlpError(EXIT_NO_INPUT, f"{label} {path} does not exist") from None
    except OSError as error:
        raise IlpError(EXIT_ILL_FORMED, f"could not read {label} {path}: {error}") from None
    if len(data) > cap:
        raise IlpError(EXIT_ILL_FORMED, f"{label} {path} exceeds the {cap}-byte cap")
    return data


def _json(data: bytes, label: str) -> Any:
    try:
        return _rf7_input.loads(data)
    except (ValueError, TypeError, RecursionError) as error:
        raise IlpError(EXIT_ILL_FORMED, f"{label} is not valid JSON: {error}") from None


def _depth(literal: Any, depth: int = 0) -> int:
    """The nesting depth of ``not``/``or``/``aggregate`` inside one literal."""
    if not isinstance(literal, dict):
        return depth
    if "not" in literal:
        return _depth(literal["not"], depth + 1)
    if "or" in literal:
        return max((_depth(item, depth + 1) for branch in literal["or"] for item in branch),
                   default=depth + 1)
    if "aggregate" in literal:
        return max((_depth(item, depth + 1) for item in literal["aggregate"]["args"]),
                   default=depth + 1)
    return depth


@dataclass(frozen=True)
class _Prepared:
    manifest: Any
    model_bytes: bytes
    model: Any
    document: dict[str, Any]
    bound: Any
    neutral: dict[str, Any]
    tree: dict[str, bytes]
    columns: dict[str, Any]
    work: Any
    #: Each object type's ancestor closure, for the join check 9b (IL1, D12 (o)).
    closures: dict[str, frozenset[str]]
    #: One entry per candidate model loaded by check 10 and the final checks,
    #: so the import's work counts them (IK5-Q6).
    reloads: list[int] = field(default_factory=list)

    @property
    def digest(self) -> str:
        return _ilp.export_digest(self.tree)


def _prepare(model_path: Path, labels_path: Path, target: str) -> _Prepared:
    """Manifest, model, binding and the export tree, in the export's order."""
    from gnd.evolve.service import _parse_model_text
    from gnd.model import MAX_MODEL_BYTES, load_model_bytes
    from gnd.redaction import RedactionPolicy

    manifest = _labels.read_label_manifest(labels_path)
    if manifest.mode != "class":
        raise IlpError(EXIT_ILL_FORMED, f"expected-state: label manifest {labels_path} is in "
                       "expected-state mode; the export learns from class labels (IK5-D2)")
    model_bytes = _read_capped(model_path, MAX_MODEL_BYTES, "model")
    model = load_model_bytes(model_bytes, source=model_path)
    if model.reference_populations:
        raise IlpError(EXIT_ILL_FORMED, "references: models with declared reference "
                       "populations are not exported (IK5 boundary)")
    bound = _labels.bind_manifest(manifest, model, hashlib.sha256(model_bytes).hexdigest())
    cache: dict[tuple[str, str], Any] = {}
    populations = []
    for entry in manifest.document["populations"]:
        key = (entry["path"], entry["sha256"])
        if key not in cache:
            cache[key] = _labels.read_population(manifest, entry, model)
        populations.append(cache[key])
    neutral, columns, work = _ilp.build_neutral(
        model=model, model_sha256=hashlib.sha256(model_bytes).hexdigest(), manifest=manifest,
        populations=populations, redacted=RedactionPolicy.from_model(model).effective_roles,
    )
    render = _learners.learner(target).render
    rendering = render(neutral) if render is not None else {}
    return _Prepared(manifest, model_bytes, model, _parse_model_text(model_bytes.decode("utf-8")),
                     bound, neutral, _ilp.export_tree(neutral, target, rendering), columns, work,
                     _ilp.type_closures(model))


def _refuse_out(out: Path) -> int | None:
    if out.is_symlink():
        _stderr(f"refusing to write through symbolic link {out}")
        return EXIT_IO
    if out.exists():
        _stderr(f"--out {out} already exists; nothing was written")
        return EXIT_COLLISION
    return None


def _cmd_export_ilp(model: str, labels: str, *, target: str, out: str) -> int:
    """``gnd export ilp``: write the neutral form and the named adapter's rendering."""
    model_path, out_path = Path(model), Path(out)
    if not model_path.is_file():
        _stderr(f"model {model_path} does not exist")
        return EXIT_NO_INPUT
    refused = _refuse_out(out_path)
    if refused is not None:
        return refused
    try:
        prepared = _prepare(model_path, Path(labels), target)
        _ilp.write_tree(out_path, prepared.tree)
    except (IlpError, _labels.LabelError) as error:
        _stderr(str(error))
        return error.code
    except (ModelLoadError, ModelValidationError) as error:
        _stderr(f"invalid model: {error}")
        return EXIT_ILL_FORMED
    except OSError as error:
        _stderr(f"could not write the export: {error}")
        return EXIT_IO
    work = prepared.work.report()
    if work["total"] > work["ceiling"]:
        _stderr(f"internal: export work {work['total']} exceeds its ceiling {work['ceiling']}")
        return EXIT_INTERNAL
    print(f"EXPORTED {len(prepared.neutral['examples'])} examples and "
          f"{len(prepared.neutral['facts'])} facts to {out_path} ({target})")
    print(f"export_sha256 {prepared.digest}")
    print(f"work {work['total']} (ceiling {work['ceiling']})")
    return EXIT_OK


def _read_clauses(path: Path, target: str) -> tuple[bytes, dict[str, Any]]:
    data = _read_capped(path, CLAUSES_CAP, "clauses")
    parse = _learners.learner(target).parse
    if parse is not None:
        try:
            text = data.decode("utf-8")
        except UnicodeDecodeError:
            raise IlpError(EXIT_ILL_FORMED, "unparsable: the program is not UTF-8") from None
        document = parse(text)
    else:
        document = _json(data, f"clauses {path}")
    _validate(document, "ilp-clauses.schema.json", "gnd-ilp-clauses/1", f"clauses {path}")
    for index, clause in enumerate(document["clauses"]):
        if max((_depth(literal) for literal in clause["body"]), default=0) > MAX_DEPTH:
            raise IlpError(EXIT_ILL_FORMED, f"clause {index}: nesting deeper than {MAX_DEPTH}")
    return data, document


def _placeholder(learner: dict[str, str], method: str, prepared: _Prepared) -> dict[str, Any]:
    """An induction block that validates, for shape checks before support exists."""
    return {"inducer": dict(learner), "method": method,
            "manifest_sha256": prepared.manifest.sha256, "examples": [],
            "support": {"numerator": 0, "denominator": 1}, "counterexamples": [],
            "evidence": [{"ref": "ilp/export.json", "sha256": prepared.digest}]}


def _envelope(core: dict[str, Any], induction: dict[str, Any], rationale: str) -> dict[str, Any]:
    return {**core, "source": "induced", "status": "proposed", "modality": "deontic",
            "rationale": rationale, "provenance": {"induction": induction}}


def _load_candidate(prepared: _Prepared, constraints: list[dict[str, Any]], model_path: Path) -> Any:
    from gnd.discover import output
    from gnd.model import load_model_bytes

    prepared.reloads.append(len(constraints))
    ops = output.add_operations([(None, c) for c in constraints], prefix="ilp")
    document = output.candidate_document(prepared.document, ops)
    return load_model_bytes(output.candidate_text(document).encode("utf-8"), source=model_path)


def _validated(prepared: _Prepared, constraint: dict[str, Any], index: int, model_path: Path) -> None:
    """Check 10: the model plus this one constraint validates."""
    from pydantic import ValidationError

    try:
        _load_candidate(prepared, [constraint], model_path)
    except (ModelLoadError, ModelValidationError) as error:
        codes = sorted({issue.rule_id for issue in getattr(error, "issues", ())})
        raise IlpError(EXIT_ILL_FORMED, f"clause {index}: invalid-guarded: {codes}") from None
    except ValidationError as error:
        raise IlpError(EXIT_ILL_FORMED, f"clause {index}: invalid-guarded: "
                       f"{error.error_count()} operation errors") from None


def coverage(verdicts: list[dict[str, str]], ids: list[str]) -> dict[str, list[str]]:
    """Covered, vacuous and unchecked ids for one clause, in manifest order.

    ``warning`` is covered; ``pass``, ``vacuous`` and ``unchecked`` are not
    (IK5-D7), the last two listed separately. A deontic constraint cannot
    ``fail``, so a ``fail`` or a missing verdict is an internal defect (C-F1)."""
    out: dict[str, list[str]] = {"covered": [], "vacuous": [], "unchecked": []}
    for identifier, verdict in zip(ids, verdicts, strict=True):
        if verdict["verdict"] == "warning":
            out["covered"].append(identifier)
        elif verdict["verdict"] in ("vacuous", "unchecked"):
            out[verdict["verdict"]].append(identifier)
        elif verdict["verdict"] != "pass":
            raise RuntimeError(f"{verdict['ref']} drew {verdict['verdict']!r} on a deontic rule")
    return out


def _cmd_import_ilp_rules(
    model: str,
    clauses: str,
    labels: str,
    run: str,
    *,
    target: str,
    out: str,
    actor: str,
    requested_at: datetime | None,
    output_format: str,
) -> int:
    """``gnd import ilp-rules``: admit learned clauses as induced guarded constraints."""
    from gnd.discover import output
    from gnd.evolve.service import MAX_EVOLUTION_PROPOSAL_BYTES

    model_path, clauses_path, run_path, out_path = Path(model), Path(clauses), Path(run), Path(out)
    for label, path in (("model", model_path), ("clauses", clauses_path), ("run record", run_path)):
        if not path.is_file():
            _stderr(f"{label} {path} does not exist")
            return EXIT_NO_INPUT
    refused = _refuse_out(out_path)
    if refused is not None:
        return refused
    try:
        clause_bytes, clause_doc = _read_clauses(clauses_path, target)
        run_bytes = _read_capped(run_path, RUN_CAP, "run record")
        record = _json(run_bytes, f"run record {run_path}")
        _validate(record, "ilp-run.schema.json", "gnd-ilp-run/1", f"run record {run_path}")
        clauses_sha = hashlib.sha256(clause_bytes).hexdigest()
        if record["clauses_sha256"] != clauses_sha:
            raise IlpError(EXIT_ILL_FORMED, f"clauses-mismatch: the run record binds clauses "
                           f"{record['clauses_sha256']}, not {clauses_sha}")
        prepared = _prepare(model_path, Path(labels), target)
        if record["export_sha256"] != prepared.digest:
            raise IlpError(EXIT_ILL_FORMED, f"export-mismatch: the run record binds export "
                           f"{record['export_sha256']}, not {prepared.digest}")
        learner = record["learner"]
        entry = _learners.learner(target)
        if entry.learner is not None and learner["name"] != entry.learner:
            raise IlpError(EXIT_ILL_FORMED, f"learner-mismatch: a {target} import needs a "
                           f"{entry.learner} run record, not {learner['name']!r}")
        count = len(clause_doc["clauses"])
        indexes = [row["clause"] for row in record["coverage"]]
        if sorted(indexes) != list(range(count)):
            raise IlpError(EXIT_ILL_FORMED, f"coverage-shape: the run record must list each of "
                           f"the {count} clauses exactly once, not {indexes}")
        reported = {row["clause"]: row["covered"] for row in record["coverage"]}
        method = entry.method
        run_sha = hashlib.sha256(run_bytes).hexdigest()
        prefix = f"learned by {learner['name']} {learner['version']} from manifest " \
                 f"{prepared.manifest.sha256[:8]}, clause"
        cores = []
        for index, clause in enumerate(clause_doc["clauses"]):
            core = rewrite(clause, index, prepared.neutral, prepared.columns,
                           closures=prepared.closures)
            _validated(prepared, _envelope(core, _placeholder(learner, method, prepared),
                                           f"{prefix} {index}"), index, model_path)
            cores.append(core)
        candidate = _load_candidate(prepared, [
            _envelope(core, _placeholder(learner, method, prepared), f"{prefix} {index}")
            for index, core in enumerate(cores)], model_path)
        populations, checks = _labels.score_populations(prepared.bound, candidate)
    except (IlpError, _labels.LabelError) as error:
        _stderr(str(error))
        return error.code
    except (ModelLoadError, ModelValidationError) as error:
        _stderr(f"invalid model: {error}")
        return EXIT_ILL_FORMED
    except OSError as error:
        _stderr(f"could not read input: {error}")
        return EXIT_IO

    base = len(prepared.document.get("constraints") or [])
    ids = [entry["id"] for entry in prepared.manifest.document["populations"]]
    classes = {entry["id"]: entry["class"] for entry in prepared.manifest.document["populations"]}
    known = set(ids)
    rows, constraints = [], []
    verdict_reads = 0
    try:
        indexes_by_report: dict[int, dict[str, list[str]]] = {}
        for population in populations:
            if id(population.report) not in indexes_by_report:
                table: dict[str, list[str]] = {}
                for verdict in population.report.verdicts:
                    table.setdefault(verdict.constraint_ref, []).append(verdict.verdict)
                indexes_by_report[id(population.report)] = table
        for index, core in enumerate(cores):
            ref = f"constraints[{base + index}]"
            verdicts = []
            for population in populations:
                found = indexes_by_report[id(population.report)].get(ref, [])
                verdict_reads += 1
                if len(found) != 1:
                    raise RuntimeError(f"{ref} has no single verdict in {population.id!r}")
                verdicts.append({"ref": ref, "verdict": found[0]})
            seen = coverage(verdicts, ids)
            claimed = reported[index]
            unknown = [i for i in claimed if i not in known]
            if unknown:
                raise IlpError(EXIT_ILL_FORMED, f"clause {index}: unknown-example: the run record "
                               f"reports {unknown[:32]}, which the manifest does not list")
            if set(claimed) != set(seen["covered"]):
                missing = [i for i in seen["covered"] if i not in set(claimed)][:32]
                extra = [i for i in claimed if i not in set(seen["covered"])][:32]
                raise IlpError(EXIT_ILL_FORMED, f"clause {index}: coverage-mismatch: GND covers "
                               f"{missing} that the learner did not report, and the learner "
                               f"reports {extra} that GND does not cover; vacuous "
                               f"{seen['vacuous'][:32]}, unchecked {seen['unchecked'][:32]}")
            rows.append((index, ref, seen, len(claimed)))
        for index, ref, seen, _claimed in rows:
            if not seen["covered"]:
                raise IlpError(EXIT_ILL_FORMED, f"clause {index}: covers-nothing: the rule covers "
                               "no example, so it has no support")
        evidence = [{"ref": "ilp/export.json", "sha256": prepared.digest},
                    {"ref": "ilp/clauses", "sha256": clauses_sha},
                    {"ref": "ilp/run", "sha256": run_sha}]
        report_rows = []
        for (index, ref, seen, claimed), core in zip(rows, cores, strict=True):
            negatives = [i for i in seen["covered"] if classes[i] == _ilp.COVERS_CLASS]
            positives = [i for i in seen["covered"] if classes[i] != _ilp.COVERS_CLASS]
            support = {"numerator": len(negatives), "denominator": len(seen["covered"])}
            induction = {
                "inducer": dict(learner), "method": method,
                "manifest_sha256": prepared.manifest.sha256,
                "examples": negatives[:INDUCTION_EXAMPLES],
                "support": support,
                "counterexamples": positives[:INDUCTION_COUNTEREXAMPLES],
                "evidence": evidence,
            }
            constraints.append(_envelope(core, induction, f"{prefix} {index}"))
            report_rows.append({"index": index, "ref": ref, "covered": len(seen["covered"]),
                                "reported": claimed, "vacuous": seen["vacuous"],
                                "unchecked": seen["unchecked"], "support": support})
        ops = output.add_operations([(None, c) for c in constraints], prefix="ilp")
        document = output.candidate_document(prepared.document, ops)
        _load_candidate(prepared, constraints, model_path)
        built = output.proposal(
            model_bytes=prepared.model_bytes, document=document, ops=ops, actor=actor,
            requested_at=requested_at or datetime.now(UTC), origin="gnd import ilp-rules",
            prefix="ilp",
            rationale=f"gnd import ilp-rules: {len(ops)} learned clauses from "
                      f"{learner['name']} {learner['version']}",
        )
        data = output.canonical_bytes(built.model_dump(mode="json"))
        if len(data) > MAX_EVOLUTION_PROPOSAL_BYTES:
            raise IlpError(EXIT_ILL_FORMED, f"too-large: the proposal would exceed "
                           f"{MAX_EVOLUTION_PROPOSAL_BYTES} bytes")
    except IlpError as error:
        _stderr(str(error))
        return error.code
    except (ModelLoadError, ModelValidationError) as error:
        _stderr(f"internal: the learned constraints failed validation together: {error}")
        return EXIT_INTERNAL
    except RuntimeError as error:
        _stderr(f"internal: {error}")
        return EXIT_INTERNAL
    reloads = len(prepared.reloads)
    work = {"export": prepared.work.report()["total"], "checks": checks, "verdicts": verdict_reads,
            "reloads": reloads, "total": checks + verdict_reads + reloads,
            "ceiling": len(populations) * (1 + len(cores)) + len(cores) + 2}
    if work["total"] > work["ceiling"]:
        _stderr(f"internal: import work {work['total']} exceeds its ceiling {work['ceiling']}")
        return EXIT_INTERNAL
    try:
        with out_path.open("xb") as handle:
            handle.write(data)
    except FileExistsError:
        _stderr(f"--out {out_path} already exists; nothing was written")
        return EXIT_COLLISION
    except OSError as error:
        _stderr(f"could not write the proposal: {error}")
        return EXIT_IO

    def entry(path: Path, digest: str) -> dict[str, str]:
        return {"path": str(path), "sha256": digest}

    report = {
        "schema_version": "gnd-ilp-import/1", "tool": "gnd", "command": "import ilp-rules",
        "target": target, "learner": dict(learner), "export_sha256": prepared.digest,
        "inputs": {"model": entry(model_path, hashlib.sha256(prepared.model_bytes).hexdigest()),
                   "manifest": entry(Path(labels), prepared.manifest.sha256),
                   "clauses": entry(clauses_path, clauses_sha), "run": entry(run_path, run_sha)},
        "clauses": report_rows, "proposal": str(out_path), "work": work,
    }
    if output_format == "json":
        sys.stdout.write(json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False) + "\n")
    else:
        lines = [f"IMPORTED {len(report_rows)} learned clauses -> {out_path}"]
        lines += [f"  clause {row['index']} {row['ref']}: covers {row['covered']} "
                  f"(support {row['support']['numerator']}/{row['support']['denominator']}), "
                  f"vacuous {len(row['vacuous'])}, unchecked {len(row['unchecked'])}"
                  for row in report_rows]
        sys.stdout.write("\n".join(lines) + "\n")
    return EXIT_OK

