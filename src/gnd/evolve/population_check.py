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

import os
import re
from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any, Final

from ruamel.yaml.error import YAMLError

from gnd.address import positional_constraint_ref
from gnd.artifacts import ArtifactError, read_regular_file_bytes, sha256_hex
from gnd.checker import check
from gnd.documents import Model
from gnd.errors import PopulationLoadError
from gnd.exits import EXIT_COLLISION, EXIT_IO, EXIT_NO_INPUT
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
    "workspace_relative",
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


def _over_cap(error: BaseException, relative: str) -> bool:
    """The reader's own cap refusal for exactly this file, matched as a whole sentence.

    ``gnd.artifacts`` reports a file over the cap as ``artifact REL is N bytes,
    over the CAP-byte cap`` (or ``grew over``). The sentence is matched in full
    and its path must be the one we asked for, so a file name that spells the
    same words cannot move a symlink refusal into band 3 (review R7).
    """

    pattern = re.compile(
        rf"artifact (?P<path>.+) (?:is \d+ bytes, over|grew over) the {MAX_POPULATION_BYTES}-byte cap"
    )
    cause: BaseException | None = error
    while cause is not None:
        match = pattern.fullmatch(str(cause))
        if match is not None and match.group("path") == relative:
            return True
        cause = cause.__cause__
    return False


def workspace_relative(anchor: Path, value: str) -> str:
    """The population path relative to the workspace, decided lexically (no filesystem access).

    The read itself refuses symlinks and escapes descriptor by descriptor; this
    only spells the path. A path outside the workspace is refused here, at read
    time, after every proposal refusal (review R8).
    """

    path = Path(os.path.normpath(value if os.path.isabs(value) else os.path.join(anchor, value)))
    try:
        relative = path.relative_to(Path(os.path.normpath(anchor)))
    except ValueError:
        raise EvolutionPopulationError(EXIT_IO, "population file is outside the workspace") from None
    if not relative.parts or relative.parts[0] == "..":
        raise EvolutionPopulationError(EXIT_IO, "population file is outside the workspace")
    return PurePosixPath(*relative.parts).as_posix()


def read_population_for_check(
    anchor: Path, value: str, *, candidate: Model, expected_sha256: str | None = None
) -> tuple[str, Population]:
    """Read the file once beneath ``anchor``, hash those bytes, load them against ``candidate``.

    The hashed bytes are the parsed bytes (UG-R5). The cap is applied at the
    read. ``model_id`` is required and must equal the candidate's (UG2-D7).
    With ``expected_sha256`` (apply), a digest that differs is refused as stale
    (11) before the bytes are parsed, whatever they now hold (review R5).
    Total over arbitrary bytes: every refusal is an ``EvolutionPopulationError``.
    """

    relative = workspace_relative(anchor, value)
    try:
        data = read_regular_file_bytes(anchor, relative, label="population", max_bytes=MAX_POPULATION_BYTES)
    except ArtifactError as error:
        if _caused_by(error, FileNotFoundError):
            raise EvolutionPopulationError(EXIT_NO_INPUT, "population file is missing") from None
        if _over_cap(error, relative):
            raise EvolutionPopulationError(
                _MALFORMED, f"population exceeds the {MAX_POPULATION_BYTES}-byte cap"
            ) from None
        raise EvolutionPopulationError(
            EXIT_IO, "population file is not a readable regular file beneath the workspace"
        ) from None
    except OSError:
        raise EvolutionPopulationError(EXIT_IO, "population file could not be read") from None
    digest = sha256_hex(data)
    if expected_sha256 is not None and digest != expected_sha256:
        raise EvolutionPopulationError(
            EXIT_COLLISION, "reviewed preview is stale: population changed before apply"
        )
    # The suffix selects YAML or JSON in the shared loader; the stem is fixed so
    # no operator path reaches a loader message (review R3).
    suffix = PurePosixPath(relative).suffix.lower()
    source = f"population{suffix if suffix in {'.json', '.yaml', '.yml'} else '.json'}"
    try:
        population = load_population_bytes(data, source=source, model=candidate)
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
    except (RecursionError, ValueError, TypeError, UnicodeDecodeError, ArithmeticError, YAMLError):
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
    final_host: Callable[[str | None], list[Any] | None],
) -> dict[int, tuple[str | None, int]]:
    """Positions, by identity, of the constraint objects the replay placed, in the final tree.

    ``placed`` rows are (operation index, host fact type id or None, host list,
    object). ``final_host`` returns the host's constraint list in the final
    replayed document (the service's own lookup). A later operation that
    replaced the whole fact type (a detached list) or the object itself leaves
    the operation unplaced: ``not-located``, never the verdict of whatever now
    sits at the old position (review R1). Each final host list is indexed once
    by identity, so the lookup is linear (review R4).
    """

    indexes: dict[str | None, dict[int, int] | None] = {}
    positions: dict[int, tuple[str | None, int]] = {}
    for position, host_id, _recorded, item in placed:
        if host_id not in indexes:
            found = final_host(host_id)
            indexes[host_id] = (
                {id(entry): index for index, entry in enumerate(found)} if isinstance(found, list) else None
            )
        index_of = indexes[host_id]
        index = None if index_of is None else index_of.get(id(item))
        if index is not None:
            positions[position] = (host_id, index)
    return positions
