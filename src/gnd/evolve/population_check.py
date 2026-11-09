"""The population check behind ``gnd evolve preview --check-population`` (UG2).

The additive policy refuses a new or strengthened constraint on a populated
fact type. With ``--check-population PATH`` the service reads one population
file, checks the candidate model over it once, and hands the policy one outcome
word per constraint operation; the policy alone decides which refusal clears
(``additive_policy_issues``). This module reads, loads, checks and maps. It
decides no cell.

Normative home: the evolution contract, "Additive policy", "Population check".
Disclosure (UG-R6): nothing here returns or raises a population value, a count
of facts, or the checker's message. Errors carry a fixed category message and,
for a population that fails validation, rule ids only.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Final

from gnd.address import positional_constraint_ref
from gnd.artifacts import ArtifactError, read_regular_file_bytes, sha256_hex
from gnd.checker import check
from gnd.documents import Model
from gnd.errors import PopulationLoadError
from gnd.exits import EXIT_IO, EXIT_NO_INPUT
from gnd.model_index import ModelIndex
from gnd.population import MAX_POPULATION_BYTES, Population, load_population_bytes

from .models import EvolutionOperationKind, EvolutionProposal
from .policy import ConstraintSubjects

__all__ = [
    "EvolutionPopulationError",
    "PopulationCheck",
    "constraint_placements",
    "population_outcomes",
    "read_population_for_check",
]

#: Band 3 is the evolution contract's "malformed input" band, written as the
#: literal the evolve lane already uses; 66 and 74 come from their one home.
_MALFORMED: Final = 3
_MODEL_ID_MISMATCH: Final = "population:model-id-mismatch"


class EvolutionPopulationError(Exception):
    """A ``--check-population`` input refused before the policy ran (UG2).

    Mapped to its exit by type, never by message: the message is a fixed
    category sentence plus, at most, sorted rule ids, so no population value
    reaches stderr (UG-R6).
    """

    def __init__(self, exit_code: int, message: str) -> None:
        super().__init__(message)
        self.exit_code = exit_code


@dataclass(frozen=True)
class PopulationCheck:
    """The digest of the bytes read and one outcome word per constraint operation."""

    sha256: str
    model_id: str
    outcomes: Mapping[int, str]


def _caused_by(error: BaseException, kind: type[BaseException]) -> bool:
    cause: BaseException | None = error
    while cause is not None:
        if isinstance(cause, kind):
            return True
        cause = cause.__cause__
    return False


def _over_cap(error: BaseException) -> bool:
    # The reader's own cap sentence (`gnd.artifacts.read_regular_bounded`).
    # A path that spells the same words is still refused, only in band 3
    # instead of 74; both bands refuse.
    cause: BaseException | None = error
    while cause is not None:
        if "-byte cap" in str(cause):
            return True
        cause = cause.__cause__
    return False


def read_population_for_check(anchor: Path, relative: str, *, candidate: Model) -> tuple[str, Population]:
    """Read the file once beneath ``anchor``, hash those bytes, load them against ``candidate``.

    The hashed bytes are the parsed bytes (UG-R5). The cap is applied at the
    read. ``model_id`` is required and must equal the candidate's (UG2-D7).
    Total over arbitrary bytes: every refusal is an ``EvolutionPopulationError``.
    """

    try:
        data = read_regular_file_bytes(anchor, relative, label="population", max_bytes=MAX_POPULATION_BYTES)
    except ArtifactError as error:
        if _caused_by(error, FileNotFoundError):
            raise EvolutionPopulationError(EXIT_NO_INPUT, "population file is missing") from None
        if _over_cap(error):
            raise EvolutionPopulationError(
                _MALFORMED, f"population exceeds the {MAX_POPULATION_BYTES}-byte cap"
            ) from None
        raise EvolutionPopulationError(
            EXIT_IO, "population file is not a readable regular file beneath the workspace"
        ) from None
    except OSError:
        raise EvolutionPopulationError(EXIT_IO, "population file could not be read") from None
    digest = sha256_hex(data)
    try:
        population = load_population_bytes(data, source="population.json", model=candidate)
    except PopulationLoadError as error:
        rules = sorted({str(issue.rule_id) for issue in getattr(error, "issues", ()) if getattr(issue, "rule_id", None)})
        if _MODEL_ID_MISMATCH in rules:
            raise EvolutionPopulationError(
                _MALFORMED, "population model_id does not match the candidate model"
            ) from None
        suffix = f" ({', '.join(rules)})" if rules else ""
        raise EvolutionPopulationError(
            _MALFORMED, f"population is not a valid population for the candidate model{suffix}"
        ) from None
    except (RecursionError, ValueError, TypeError, UnicodeDecodeError):
        raise EvolutionPopulationError(_MALFORMED, "population is not a valid population document") from None
    if population.model_id is None or candidate.model_id is None or population.model_id != candidate.model_id:
        raise EvolutionPopulationError(_MALFORMED, "population model_id does not match the candidate model")
    return digest, population


def _sample_row_fact_types(before: Model) -> frozenset[str]:
    found: set[str] = set()
    for row in ModelIndex.for_model(before).iter_fact_types_shared():
        rows = row.get("sample_population") if isinstance(row, dict) else None
        if isinstance(rows, list) and rows and row.get("id") is not None:
            found.add(str(row["id"]))
    return frozenset(found)


def population_outcomes(
    proposal: EvolutionProposal,
    *,
    before: Model,
    candidate: Model,
    population: Population,
    sha256: str,
    populated: frozenset[str],
    placements: Mapping[int, tuple[str | None, int]],
) -> PopulationCheck:
    """One ``check`` call; one outcome word per constraint ADD or MODIFY operation.

    ``placements`` maps an operation index to the (host fact type, position) of
    the constraint it placed in the candidate, from the replay. Outcomes, in
    precedence order: ``sample-rows`` (a subject has sample rows in the current
    model, which the checker does not see, UG2-D5), ``uncovered`` (a populated
    subject has no fact in the population, UG2-D4), the constraint's own verdict
    word, else ``not-located``. Other constraints' verdicts are ignored (UG2-D9).
    """

    report = check(candidate, population)
    verdicts = {row.constraint_ref: row.verdict for row in report.verdicts}
    subjects_of = ConstraintSubjects(ModelIndex.for_model(before))
    sampled = _sample_row_fact_types(before)
    facts = population.facts if isinstance(population.facts, dict) else {}
    with_facts = {str(key) for key, rows in facts.items() if isinstance(rows, list) and rows}
    outcomes: dict[int, str] = {}
    for position, operation in enumerate(proposal.operations):
        if operation.locator.locator_kind != "constraint" or operation.kind not in (
            EvolutionOperationKind.ADD,
            EvolutionOperationKind.MODIFY,
        ):
            continue
        subjects = subjects_of.of(operation)
        if subjects & sampled:
            outcomes[position] = "sample-rows"
            continue
        if any(subject not in with_facts for subject in subjects & populated):
            outcomes[position] = "uncovered"
            continue
        placement = placements.get(position)
        verdict = verdicts.get(positional_constraint_ref(*placement)) if placement is not None else None
        outcomes[position] = verdict if verdict is not None else "not-located"
    return PopulationCheck(sha256=sha256, model_id=str(candidate.model_id), outcomes=outcomes)


def constraint_placements(
    placed: Iterable[tuple[int, str | None, list[Any], Any]],
) -> dict[int, tuple[str | None, int]]:
    """Positions, by identity, of the constraint objects the replay placed.

    ``placed`` rows are (operation index, host id or None, host list, object);
    the object is found in its list with ``is``, so a later delete in the same
    proposal that shifts it is followed.
    """

    positions: dict[int, tuple[str | None, int]] = {}
    for position, host_id, collection, item in placed:
        for index, candidate in enumerate(collection):
            if candidate is item:
                positions[position] = (host_id, index)
                break
    return positions
