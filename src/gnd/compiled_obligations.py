"""Opt-in standing operation implications and shared typed subset matching."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from gnd.values import identity_key

MAX_COMPILED_WORK = 100_000


class CompiledWorkLimit(ValueError):
    """The complete snapshot obligation set exceeded its counted work budget."""


@dataclass
class WorkBudget:
    limit: int
    visits: int = 0

    def visit(self, count: int) -> None:
        self.visits += count
        if self.visits > self.limit:
            raise CompiledWorkLimit('compiled obligation role-cell work limit')


@dataclass
class _PreparedSubsetRows:
    """One call's effective relation view and counted required projections."""

    facts: Any
    budget: WorkBudget | None = None
    required: dict[tuple[str, tuple[str, ...]], set[tuple[Any, ...]]] = field(
        default_factory=dict
    )

    def key(self, row: Any, roles: tuple[str, ...]) -> tuple[Any, ...]:
        if self.budget is not None:
            self.budget.visit(len(roles))
        return tuple(identity_key(row.get(role)) for role in roles)

    def offending_rows(self, entry: dict[str, Any]) -> list[Any]:
        subset = entry['subset']
        left = self.facts.get(str(subset['of']), ())
        if not left:
            return []
        pairs = entry['role_pairs']
        right_roles = tuple(pair[1] for pair in pairs)
        projection = str(subset['in']), right_roles
        if projection not in self.required:
            self.required[projection] = {
                self.key(row, right_roles)
                for row in self.facts.get(projection[0], ())
            }
        required = self.required[projection]
        left_roles = tuple(pair[0] for pair in pairs)
        return [row for row in left if self.key(row, left_roles) not in required]


def offending_rows(entry: dict[str, Any], facts: Any,
                   budget: WorkBudget | None = None) -> list[Any]:
    """Match every role pair against one required row, using typed identity."""
    return _PreparedSubsetRows(facts, budget).offending_rows(entry)


def compiled_entries(model):
    """Compile current declarations without mutating the loaded side table."""
    from gnd.model._operations import _effect_index, compile_operation

    effects = _effect_index(model.operations)
    return [(op, entry) for op in model.operations
            for entry in compile_operation(op, effects) if entry.get('subset')]


def compose(model, population, report):
    """Compose compiled verdicts without reusing narrower snapshot assurance."""
    from gnd.checker._reports import ConstraintVerdict
    from gnd.extensions import PARTIAL_OPAQUE, constraint_view_dispatch, evaluate_derivations
    from gnd.model_index import ModelIndex

    entries = compiled_entries(model)
    if not entries:
        return report
    token = PARTIAL_OPAQUE.set(True)
    try:
        extensions, _derivations = evaluate_derivations(model, population)
        view = constraint_view_dispatch(model, population, extensions)
    finally:
        PARTIAL_OPAQUE.reset(token)
    unavailable = {row.fact_type for row in report.derivations if row.verdict == 'unchecked'}
    unavailable.update(getattr(extensions, 'unavailable', {}))
    budget = WorkBudget(MAX_COMPILED_WORK)
    metadata_exhausted = False
    subjects = {str(entry['subset'][side]) for _op, entry in entries for side in ('of', 'in')}
    # Passing derivation consistency does not mean that its extension is definite:
    # a correct empty claim can still have possible-only rows.
    try:
        for head, possible in getattr(extensions, 'possible', {}).items():
            if head not in subjects:
                continue
            relation = extensions.get(head)
            if relation is None:
                unavailable.add(head)
                continue

            def row_key(row):
                budget.visit(len(row))
                return tuple(identity_key(value) for value in row)

            known = {row_key(row) for row in relation.rows}
            if any(row_key(row) not in known for row in possible):
                unavailable.add(head)
    except CompiledWorkLimit:
        metadata_exhausted = True
    # Opaque rule declarations without a calculated extension cannot imply absence.
    for fact in ModelIndex.for_model(model).iter_fact_types_shared():
        if fact.get('derivation') in ('derived', 'semiderived') and not isinstance(
            fact.get('derivation_rule'), dict
        ):
            unavailable.add(str(fact['id']))
    rows = []
    prepared = _PreparedSubsetRows(view.facts, budget)
    for operation, entry in entries:
        of, into = str(entry['subset']['of']), str(entry['subset']['in'])
        subjects = {of, into}
        reason = None
        offending = []
        if not subjects <= set(view.covers):
            verdict, event, reason = 'unchecked', 'uncovered', 'compiled-obligation-uncovered'
        elif subjects & unavailable or any(
            isinstance(value, dict) for subject in subjects
            for fact in view.facts.get(subject, ()) for value in fact.values()
        ):
            verdict, event, reason = ('unchecked', 'unavailable',
                                      'compiled-obligation-unavailable')
        elif metadata_exhausted:
            verdict, event, reason = ('unchecked', 'work-limit',
                                      'compiled-obligation-work-limit')
        else:
            try:
                offending = prepared.offending_rows(entry)
                if not view.facts.get(of):
                    verdict, event = 'vacuous', 'vacuous'
                elif offending:
                    verdict = 'fail' if entry['modality'] == 'alethic' else 'warning'
                    event = 'violated:' + entry['modality']
                else:
                    verdict, event = 'pass', 'clean'
            except CompiledWorkLimit:
                verdict, event, reason = ('unchecked', 'work-limit',
                                          'compiled-obligation-work-limit')
        source = operation['preconditions'][entry['source_index']]
        identity = f"{operation['id']}.{entry['obligation']}"
        message = (f"{identity}: every {of} fact requires a matching {into} fact; "
                   f"{len(offending)} unmatched." if reason is None else f'{identity}: {reason}.')
        rows.append(ConstraintVerdict(
            scope_id='snapshot:compiled-subset:n-a:' + event,
            constraint_ref=entry['locator'], constraint_type='compiled-subset',
            modality=entry['modality'], source=source['source'], status=source['status'],
            verdict=verdict, message=message, offending_facts=offending,
            reason_code=reason,
        ))
    return report.model_copy(update={
        'verdicts': [*report.verdicts, *rows], 'snapshot_projection': None,
        'phase1_trace': None, 'assurance_input_scope_ids': (),
    })
