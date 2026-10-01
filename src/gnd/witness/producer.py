"""Capture grounded firings from the production evaluator into a finite DAG."""

from __future__ import annotations

from gnd import checker
from gnd.artifacts import canonical_json_bytes
from gnd.model import ModelLoadError, ModelValidationError, iter_derivation_clauses
from gnd.population import PopulationLoadError
from gnd.references import bind_population, resolve_context
from gnd.witness.io import (
    classify_targets,
    roster,
    validate_targets,
    validate_witness_structure,
    witness_input_identity,
)
from gnd.witness.types import (
    DEFAULT_LIMITS,
    WitnessInputError,
    WitnessResult,
    WitnessWorkError,
    checked_limits,
    reduce_results,
    result_rows,
)


class GroundedTrace:
    def __init__(self, model, candidate, references, limits, closure):
        self.roles = roster(model)
        self.limits = limits
        self.joins = 0
        self.nodes = []
        self.proofs = {}
        self.bases = {}
        self.depths = []
        self.edges = self.cells = 0
        self.types = {ft["id"]: ft for ft in model.fact_types}
        self.clauses = {
            fid: iter_derivation_clauses(ft.get("derivation_rule"))
            for fid, ft in self.types.items()
        }
        populations = [(None, candidate)]
        if references is not None:
            populations += [
                (o.id, pop)
                for (o, _, _), pop in zip(
                    references._snapshots, references._populations, strict=True
                )
            ]
        self.opaque = set()
        for origin, pop in populations:
            for fid, rows in sorted(pop.facts.items()):
                if fid not in closure:
                    continue
                if self.types[fid].get("derivation") in {"derived", "semiderived"}:
                    continue
                for i, row in enumerate(rows):
                    if any(isinstance(v, dict) for v in row.values()):
                        self.opaque.add(fid)
                        continue
                    cells = self.typed_row(fid, [row[r] for r, _ in self.roles[fid]])
                    key = self.key(fid, cells)
                    self.bases.setdefault(key, (fid, origin, i, row))

    def resolve(self, key):
        proof = self.proofs.get(key)
        if proof is not None or key not in self.bases:
            return proof
        fid, origin, i, row = self.bases[key]
        cells = self.typed_row(fid, [row[r] for r, _ in self.roles[fid]])
        proof = self.add(
            {
                "kind": "base",
                "fact_type": fid,
                "tuple": cells,
                "origin": {
                    "kind": "reference" if origin else "candidate",
                    "reference_id": origin,
                    "fact_index": i,
                },
            }
        )
        self.proofs[key] = proof
        return proof

    def key(self, fid, cells):
        return fid, canonical_json_bytes(cells)

    def typed_row(self, fid, row):
        return [
            {"primitive": p, "value": v} for (_, p), v in zip(self.roles[fid], row, strict=True)
        ]

    def charge(self, amount):
        self.joins += amount
        if self.joins > self.limits.joins:
            raise WitnessWorkError("attempted joins exceed ceiling")

    def add(self, node):
        premises = node.get("premises", [])
        depth = 1 + max((self.depths[e] for e in premises), default=0)
        self.edges += len(premises)
        self.cells += len(node.get("bindings", {}))
        if (
            len(self.nodes) >= self.limits.nodes
            or self.edges > self.limits.edges
            or self.cells > self.limits.binding_cells
            or depth > self.limits.proof_depth
        ):
            raise WitnessWorkError("grounded graph ceiling")
        node["id"] = len(self.nodes)
        self.nodes.append(node)
        self.depths.append(depth)
        return node["id"]

    def row(self, fact_type, clause, binding, row):
        fid = fact_type["id"]
        cells = self.typed_row(fid, row)
        key = self.key(fid, cells)
        if key in self.proofs:
            return
        typed_bindings, premises = {}, []
        for atom in clause["body"]:
            afid = atom["fact_type"]
            acells = []
            for role, primitive in self.roles[afid]:
                term = atom["bind"][role]
                var = term[1:] if isinstance(term, str) and term.startswith("$") else None
                value = binding[var] if var is not None else term
                cell = {"primitive": primitive, "value": value}
                acells.append(cell)
                if var is not None:
                    typed_bindings[var] = cell
            proof = self.resolve(self.key(afid, acells))
            if proof is None:
                return  # The next production round can ground this firing.
            premises.append(proof)
        ci = self.clauses[fid].index(clause)
        for wi, _ in enumerate(clause.get("where", [])):
            premises.append(
                self.add(
                    {
                        "kind": "comparison",
                        "rule_fact_type": fid,
                        "clause_index": ci,
                        "where_index": wi,
                        "bindings": typed_bindings,
                        "premises": [],
                    }
                )
            )
        self.proofs[key] = self.add(
            {
                "kind": "rule",
                "fact_type": fid,
                "clause_index": ci,
                "tuple": cells,
                "bindings": typed_bindings,
                "premises": premises,
            }
        )

    def compact(self, roots):
        wanted, stack = set(), [r for r in roots if r is not None]
        while stack:
            i = stack.pop()
            if i not in wanted:
                wanted.add(i)
                stack.extend(self.nodes[i].get("premises", []))
        mapping = {old: new for new, old in enumerate(sorted(wanted))}
        nodes = []
        for old in sorted(wanted):
            node = dict(self.nodes[old], id=mapping[old])
            if "premises" in node:
                node["premises"] = [mapping[e] for e in node["premises"]]
            nodes.append(node)
        return nodes, [mapping[r] if r is not None else None for r in roots]


def produce_witness(model, candidate, targets, *, references=None, limits=DEFAULT_LIMITS):
    try:
        checked_limits(limits)
        validate_witness_structure(list(targets), limits=limits)
        if not 1 <= len(targets) <= limits.targets:
            raise ValueError("target count")
        validate_targets(targets, model)
        # Re-enter the structural readers even for programmatically supplied objects.
        from gnd.witness.io import intake, population_wire

        context = resolve_context(model, references) if model.reference_populations else None
        raw_refs = tuple((o.id, raw) for o, _, raw in context._snapshots) if context else ()
        # Population interchange is reconstructed explicitly; model_dump is its
        # internal representation and is used only for the documented identity.
        candidate_doc = population_wire(candidate)
        intake(
            model.model_dump(mode="json", exclude={"warnings"}),
            candidate_doc,
            raw_refs,
            limits=limits,
        )
        binding = witness_input_identity(model, candidate, references=context)
        populations = (candidate, *context._populations) if context else (candidate,)
        flags, scopes, closure = classify_targets(model, targets, populations)
        if not any(flags):
            return WitnessResult(2, result_rows(targets, "unsupported"))
        trace = GroundedTrace(model, candidate, context, limits, closure)
        combined = (
            bind_population(model, candidate, references=context).combined if context else candidate
        )
        relations = checker._base_relations(model, combined)
        token = checker._WITNESS_TRACE.set(trace)
        try:
            checker._evaluate_stratified_extensions(model, relations, heads=closure, exact=True)
        finally:
            checker._WITNESS_TRACE.reset(token)
        roots = [
            trace.resolve(trace.key(t["fact_type"], t["tuple"])) if flag else None
            for t, flag in zip(targets, flags, strict=True)
        ]
        nodes, roots = trace.compact(roots)
        statuses = [
            "unsupported"
            if not flag
            else "proved"
            if root is not None
            else "unknown"
            if trace.opaque & scope
            else "missing"
            for root, flag, scope in zip(roots, flags, scopes, strict=True)
        ]
        rows = [
            result_rows((t,), status, roots=(root,))[0]
            for t, status, root in zip(targets, statuses, roots, strict=True)
        ]
        for i, r in enumerate(rows):
            r["request_index"] = i
        certificate = {
            "version": 1,
            "kind": "derivation-witness",
            "binding": binding,
            "results": rows,
            "nodes": nodes,
        }
        try:
            # Canonical export adds exactly one final newline to compact JSON.
            if validate_witness_structure(certificate, limits=limits) >= limits.bytes:
                raise WitnessInputError("canonical wire newline exceeds ceiling")
        except WitnessInputError as error:
            raise WitnessWorkError("generated certificate exceeds wire ceiling") from error
        work = {"joins": trace.joins, "nodes": len(nodes)}
        return reduce_results(rows, certificate=certificate, work=work)
    except WitnessWorkError:
        return WitnessResult(4, result_rows(targets, "resource-refused"), reason="work-limit")
    except (
        ValueError,
        TypeError,
        KeyError,
        IndexError,
        OSError,
        AttributeError,
        RecursionError,
        ModelLoadError,
        ModelValidationError,
        PopulationLoadError,
    ):
        return WitnessResult(3, reason="input-invalid")
