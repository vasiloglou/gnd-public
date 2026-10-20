"""Closed in-process count feedback and validated host relation replacement.

These records are not persistent experiment feedback or external truth evidence.
"""
from __future__ import annotations

import json
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from gnd import input_policy
from gnd.artifacts import canonical_json_bytes
from gnd.errors import PopulationLoadError
from gnd.extensions import structured_extension_view
from gnd.model_index import ModelIndex
from gnd.population import Population, load_population_bytes

MAX_COUNT = 2**31 - 1
MAX_ROWS = 128
MAX_WIRE_BYTES = 16 * 1024
Count = Annotated[int, Field(strict=True, ge=0, le=2**31 - 1)]
Status = Literal['available', 'unavailable', 'not-evaluated', 'overflow']


class _Closed(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True, frozen=True, serialize_by_alias=True)


class VerdictCounts(_Closed):
    passed: Count | None = Field(alias='pass')
    fail: Count | None
    warning: Count | None
    unchecked: Count | None
    vacuous: Count | None


class FactCount(_Closed):
    fact_type: Annotated[str, Field(min_length=1, max_length=256)]
    asserted_count: Count | None
    asserted_status: Literal['available', 'not-evaluated', 'overflow']
    computed_count: Count | None
    computed_status: Status

    @model_validator(mode='after')
    def coherent_computation(self):
        if (self.asserted_status == 'available') != (self.asserted_count is not None):
            raise ValueError('asserted count must match availability')
        if (self.computed_status == 'available') != (self.computed_count is not None):
            raise ValueError('computed count must match availability')
        return self


class SessionFeedback(_Closed):
    kind: Literal['evaluation-session-feedback']
    schema_version: Literal[1]
    attempt: Annotated[int, Field(strict=True, ge=1, le=1_000_000)]
    operation: Literal['check']
    exit_code: Literal[0, 1, 2, 3, 4, 70]
    verdict_counts: VerdictCounts
    rows: Annotated[tuple[FactCount, ...], Field(max_length=128)]
    omitted_entries: Count
    truncated: bool

    @classmethod
    def model_validate_json(cls, json_data, **kwargs):
        if not isinstance(json_data, (str, bytes, bytearray)):
            raise TypeError('feedback JSON must be encoded text')
        encoded = json_data.encode('utf-8') if isinstance(json_data, str) else json_data
        if len(encoded) > MAX_WIRE_BYTES:
            raise ValueError('feedback byte limit exceeded')
        # The shared parser refuses duplicate keys, nonfinite values and deep
        # containers before Pydantic can collapse or coerce the encoded wire.
        parsed = input_policy.loads(json_data)
        return super().model_validate_json(canonical_json_bytes(parsed), **kwargs)

    @field_validator('schema_version', 'exit_code', mode='before')
    @classmethod
    def integer_literals(cls, value):
        if type(value) is not int:
            raise ValueError('integer wire field required')
        return value

    @model_validator(mode='after')
    def bounded_wire(self):
        if len(canonical_json_bytes(self.model_dump(mode='json', by_alias=True))) > MAX_WIRE_BYTES:
            raise ValueError('feedback byte limit exceeded')
        return self


def _count(value):
    return value if type(value) is int and 0 <= value <= MAX_COUNT else None


def build_feedback(model, population, payload, *, attempt):
    """Project bounded counts using the ordinary structured calculation only."""
    valid = isinstance(population, Population) and population.matches_validation_marker(model)
    view = None
    if valid and payload['exit_code'] in (0, 1, 2, 4) and not model.reference_populations:
        try:
            view = structured_extension_view(model, population)
        except Exception:  # noqa: BLE001 -- diagnostic counts cannot replace the checker result
            view = None
    facts = tuple(ModelIndex.for_model(model).iter_fact_types())
    rows = []
    omitted = 0
    truncated = False
    for fact in facts:
        name = fact['id']
        if len(rows) >= MAX_ROWS or not name or len(name) > 256:
            omitted += 1
            continue
        asserted = _count(len(population.facts.get(name, ()))) if valid else None
        computed = None
        status = 'not-evaluated'
        if view is not None:
            if name in view.unavailable:
                status = 'unavailable'
            elif name in view.possible:
                status = 'not-evaluated'
            elif name in view.facts:
                computed = _count(len(view.facts[name]))
                status = 'available' if computed is not None else 'overflow'
        truncated |= valid and asserted is None or status == 'overflow'
        rows.append(FactCount(fact_type=name, asserted_count=asserted,
                              asserted_status=('available' if asserted is not None else
                                               'overflow' if valid else 'not-evaluated'),
                              computed_count=computed, computed_status=status))
    report = payload.get('report', payload)
    counts = report.get('counts') or {}
    verdicts = {key: _count(counts.get(key, 0))
                for key in ('pass', 'fail', 'warning', 'unchecked', 'vacuous')}
    truncated |= any(value is None for value in verdicts.values())
    while True:
        document = {'kind': 'evaluation-session-feedback', 'schema_version': 1,
                    'attempt': attempt, 'operation': 'check', 'exit_code': payload['exit_code'],
                    'verdict_counts': VerdictCounts(**verdicts), 'rows': tuple(rows),
                    'omitted_entries': omitted, 'truncated': truncated or bool(omitted)}
        # Validate shape separately before trimming bytes; never hide a wrong
        # attempt/version under a diagnostic fallback.
        candidate = SessionFeedback.model_construct(**document)
        if len(canonical_json_bytes(candidate.model_dump(mode='json', by_alias=True))) <= MAX_WIRE_BYTES:
            return SessionFeedback(**document).model_dump(mode='json', by_alias=True)
        if not rows:
            raise ValueError('feedback header exceeds byte limit')
        rows.pop()
        omitted += 1


def compose_observation(model, population, replacements):
    """Compose an untrusted whole-relation replacement through the normal loader."""
    if not isinstance(population, Population) or not population.matches_validation_marker(model):
        raise ValueError('observation requires a current validated Population')
    if type(replacements) is not dict:
        raise TypeError('observations must map fact types to complete ordered row lists')
    index = ModelIndex.for_model(model)
    for name, rows in replacements.items():
        if type(name) is not str or index.fact_type(name) is None:
            raise ValueError('unknown observed fact type')
        if type(rows) is not list or any(type(row) is not dict for row in rows):
            raise TypeError('observation requires complete ordered row dictionaries')
    header = {key: getattr(population, key) for key in
              ('model', 'model_id', 'source', 'label', 'covers')
              if getattr(population, key) is not None}
    document = {'format_version': population.format_version, 'population': header,
                'instances': population.instances, 'facts': {**population.facts, **replacements}}
    try:
        data = json.dumps(document, allow_nan=False, ensure_ascii=False).encode('utf-8')
        return load_population_bytes(data, model=model, source='<host observation>.json')
    except (PopulationLoadError, TypeError, ValueError, RecursionError) as exc:
        raise ValueError('observation rejected by normal population validation') from exc
