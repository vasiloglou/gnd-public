"""The sidecar: a population's out-of-band provenance, bound to what it labels.

D-15 froze the population format — a generator seed is something an agent output
would never carry, and the format's whole value is that one shape serves agent
output, synthetic data and eval fixtures. So everything a measured rate needs to
be reproducible and trusted — seed, generator identity, model identity, and the
per-constraint ground truth — lives HERE, in a ``<stem>.meta.json`` sidecar keyed
to the population path, and NOTHING in this module touches
``population.schema.json`` or its synced copies.

**Cryptographically bound to what it labels (C6).** The sidecar carries three
REQUIRED digests — ``population_sha256`` (the file it describes),
``model_digest`` (the model that file was checked against), and ``pool_sha256``
(the artifact its values were drawn from) — plus RELATIVE paths only (an absolute
``/tmp`` or CI path leaks into a committed artifact and breaks cross-machine
reproduction). :func:`read_sidecar` REJECTS any unknown field and any sidecar
whose ``population`` field does not name the neighbouring file, so a swapped,
stale, or schema-drifted sidecar fails loud rather than silently corrupting every
downstream rate. Plan 04 recomputes and compares all three digests at scoring
time; this module ships the fields it checks.

**Typed expectations (C3).** ``expectations`` is a map ``constraint_ref ->``
:class:`ExpectedState`, NOT a bare ground-truth string. An
expected-unchecked-by-design case — an alethic ``textual`` constraint, a
derivation-only ``subtype-partition`` — is representable as
``{satisfied, unchecked, reason}`` and is therefore NOT mislabelled a measurement
artifact by plan 04's scorer. This is the type plans 04/05/06 consume, so it is
defined HERE, at the sidecar owner, rather than downstream.
"""

from __future__ import annotations

import hashlib  # noqa: F401 -- historical compatibility binding
import json
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, ValidationError

from gnd import input_policy as _rf7_input
from gnd.population import _model_digest
from gnd.synth import GENERATOR_VERSION

__all__ = [
    "CASE_KIND_TO_LABEL",
    "SIDECAR_SCHEMA_VERSION",
    "SUPPORTED_SIDECAR_SCHEMA_VERSIONS",
    "CaseKind",
    "ExpectedState",
    "Sidecar",
    "SidecarError",
    "model_digest",
    "read_sidecar",
    "write_sidecar",
]

#: The sidecar contract version. BUMP when the field set changes so a reader can
#: refuse a sidecar written by an incompatible generator rather than
#: mis-parsing it. Opaque and monotonic; readers compare, never parse.
#: /2: plan 05 added the violating-class keys (violates, violates_target,
#: isolating, isolation_verified, baseline_seed) — additive and optional, so a
#: /1 sidecar still reads clean.
#: /3: plan 06 added the boundary/frontier keys (case_kind, predicted_verdict,
#: boundary_side, epsilon, not_derivable) — additive and optional again.
#: /4: the generator operator and complete not-derivable manifest moved into
#: the sidecar so measurement never derives coverage from unbound index labels.
#: /5: structured derivations excluded from mutation scoring are named in the
#: sidecar instead of being inferred from the model or an unbound index.
SIDECAR_SCHEMA_VERSION = "gnd-sidecar/5"
SUPPORTED_SIDECAR_SCHEMA_VERSIONS = frozenset(
    {
        "gnd-sidecar/1",
        "gnd-sidecar/2",
        "gnd-sidecar/3",
        "gnd-sidecar/4",
        SIDECAR_SCHEMA_VERSION,
    }
)
SidecarSchemaVersion = Literal[
    "gnd-sidecar/1",
    "gnd-sidecar/2",
    "gnd-sidecar/3",
    "gnd-sidecar/4",
    "gnd-sidecar/5",
]

GroundTruth = Literal["satisfied", "violated", "no-subjects"]
ExpectedVerdict = Literal["pass", "fail", "warning", "unchecked", "vacuous"]

#: The FIVE case kinds a measurement distinguishes, mapped onto the THREE
#: population-header ``label`` values D-10 froze (D-15 forbids a fourth):
#:
#: | ``case_kind`` (sidecar) | ``label`` (population header) | why |
#: |---|---|---|
#: | ``conforming`` | ``conforming`` | — |
#: | ``boundary``   | ``boundary``   | — |
#: | ``violating``  | ``violating``  | — |
#: | ``no-subjects``| **``boundary``** | it is the frontier of *evaluability*: nothing in it violates anything, so ``violating`` would be false, and ``conforming`` would tell a consumer "this should pass" when the predicted verdict is ``vacuous`` |
#: | ``unchecked``  | **``boundary``** | the frontier of mechanical *decidability*, same reasoning — the predicted verdict is ``unchecked``, so a ``conforming`` label would misdirect |
#:
#: The DISCRIMINATING field is ``case_kind`` in the sidecar; ``label`` stays the
#: coarse three-way hint in the population file, exactly as Phase 1 D-10 defined
#: it, and no schema copy moves.
CASE_KIND_TO_LABEL: dict[str, str] = {
    "conforming": "conforming",
    "boundary": "boundary",
    "violating": "violating",
    "no-subjects": "boundary",
    "unchecked": "boundary",
}

CaseKind = Literal["conforming", "boundary", "violating", "no-subjects", "unchecked"]


class SidecarError(Exception):
    """A sidecar failed to parse, carried an unknown field, or did not name the
    population beside it (C6). Loud by design — a silent mismatch corrupts a
    rate."""


class ExpectedState(BaseModel):
    """The expected outcome for ONE constraint on a labelled population (C3).

    Three orthogonal facts, because a bare ground-truth string cannot express an
    expected-unchecked-by-design case and would make plan 04 score it a
    measurement artifact:

    - ``ground_truth`` — what the assembler's CONSTRUCTIVE witness established:
      ``satisfied`` / ``violated`` / ``no-subjects``. NEVER the checker's verdict
      (C1); it is the independent oracle a false-fail is measured against.
    - ``expected_verdict`` — the verdict a CORRECT checker should emit for that
      ground truth: ``pass`` / ``fail`` / ``warning`` / ``unchecked`` /
      ``vacuous``. An alethic ``textual`` constraint is ``{satisfied, unchecked,
      ...}``; a derivation-only ``subtype-partition`` likewise.
    - ``reason`` — why the expected verdict diverges from a naive read of the
      ground truth (``"textual-not-mechanical"``,
      ``"subtype-derivation-only"``), or ``None`` when it does not.
    """

    model_config = ConfigDict(extra="forbid")

    ground_truth: GroundTruth
    expected_verdict: ExpectedVerdict
    reason: str | None = None


class Sidecar(BaseModel):
    """A population's provenance record, bound to the file by three digests (C6).

    ``class_`` serialises as ``class`` (a Python keyword). ``extra="forbid"``
    makes any unknown field a load-time rejection — a swapped-format or
    schema-drifted sidecar cannot be read as valid.
    """

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    # Keep compatible historical readers explicit.  An arbitrary string here
    # lets a newer writer silently change semantics underneath an older scorer.
    schema_version: SidecarSchemaVersion = SIDECAR_SCHEMA_VERSION
    #: Path of the population this sidecar describes, RELATIVE to the output root
    #: (never absolute — a machine path in a committed artifact breaks
    #: reproduction). read_sidecar rejects a sidecar whose value does not name the
    #: neighbouring file.
    population: str
    #: sha256 of the population file's bytes — REQUIRED. Plan 04 recomputes and
    #: compares; an edited population is caught here.
    population_sha256: str
    class_: Literal["conforming", "boundary", "violating"] = Field(alias="class")
    #: The RNG seed used — supplied via --seed or drawn from OS entropy, ALWAYS
    #: recorded, so the development lane's probabilistic default is still
    #: regenerable (D-07′).
    seed: int
    generator_version: str = GENERATOR_VERSION
    gnd_version: str
    #: The population's declared model reference (opaque; never dereferenced).
    model: str
    model_id: str | None = None
    #: Digest of the model content this population was checked against — REQUIRED
    #: (C6). A wrong-model sidecar is caught by plan 04 recomputing this.
    model_digest: str
    #: The pool artifact block. pool_path is RELATIVE; pool_sha256 is REQUIRED and
    #: non-empty for Faker runs too (an omitted --pool materialises a hashed file).
    pool_source: str
    pool_path: str
    pool_sha256: str
    #: LLM-proposer provenance (D-07′) — present only for an LLM-composed pool.
    proposer_model: str | None = None
    prompt_version: str | None = None
    pool_size: int
    #: constraint_ref -> ExpectedState (C3). The typed map plans 04/05/06 read.
    expectations: dict[str, ExpectedState] = Field(default_factory=dict)
    #: Violating-class provenance (plan 05, D-05'). ``violates`` is the FULL
    #: predicted set of constraint refs the mutation breaks (the label per-
    #: constraint attribution credits); ``violates_target`` the one the operator
    #: aimed at; ``isolating`` whether the set has exactly one member;
    #: ``isolation_verified`` that the real checker CONFIRMED the set on this
    #: very case (never assumed from the operator's name); ``baseline_seed`` the
    #: conforming baseline the mutation started from — a violating case that
    #: cannot be traced to its baseline cannot be regenerated. All None for
    #: conforming populations.
    violates: list[str] | None = None
    violates_target: str | None = None
    isolating: bool | None = None
    isolation_verified: bool | None = None
    baseline_seed: int | None = None
    #: Boundary / frontier provenance (plan 06, D-06). ``case_kind`` is the
    #: FIVE-valued discriminator (:data:`CASE_KIND_TO_LABEL` maps it onto the
    #: three frozen ``label`` values); ``target`` names the constraint whose
    #: bound the case sits at; ``predicted_verdict`` is that constraint's
    #: derived expectation, computed at the same time as the data — a boundary
    #: case without a prediction is not a measurement input, it is just data;
    #: ``boundary_side`` is ``inside`` / ``outside`` / ``frontier``; ``epsilon``
    #: is the ACTUAL derived neighbour step (``math.nextafter``'s delta, ``P1D``,
    #: ``PT0.000001S``, ``1``, ``membership``, ``1 fact``…), never the name of a
    #: constant; ``not_derivable`` carries the sides of the SAME constraint that
    #: had no reachable case, each with the mechanism that makes it unreachable.
    case_kind: CaseKind | None = None
    operator: str | None = None
    target: str | None = None
    predicted_verdict: ExpectedVerdict | None = None
    boundary_side: str | None = None
    epsilon: str | None = None
    not_derivable: list[dict[str, Any]] | None = None
    #: Structured derivation obligations intentionally excluded from mutation
    #: scoring because the bounded generator has no independent mutation oracle.
    unmutated_derivations: list[dict[str, str]] = Field(default_factory=list)


def validated_model_sha256(model: Any) -> str:
    """The digest plan 04 recomputes and compares (C6). Delegates to
    :func:`gnd.population._model_digest`, the SAME digest the population loader
    stamps its validation marker with, so the two can never disagree about what a
    model's content is."""
    return _model_digest(model)


def _sha256_file(path: str | Path) -> str:
    from gnd.safefs import file_sha256

    return '' + file_sha256(path)


def write_sidecar(sidecar: Sidecar, population_path: str | Path) -> Path:
    """Write ``<stem>.meta.json`` beside ``population_path``.

    ``population_sha256`` is computed over the just-written population file, so
    the sidecar is bound to the exact bytes on disk (C6). The ``population`` field
    is normalised to the population file's basename — the sidecar lives beside its
    population, so a bare name is both relative and unambiguous. Returns the
    sidecar path.
    """
    population_path = Path(population_path)
    bound = sidecar.model_copy(
        update={
            "population": population_path.name,
            "population_sha256": _sha256_file(population_path),
        }
    )
    sidecar_path = population_path.with_suffix(".meta.json")
    payload = bound.model_dump(by_alias=True)
    sidecar_path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return sidecar_path


def read_sidecar(path: str | Path, *, verify_population_hash: bool = True) -> Sidecar:
    """Read and validate a sidecar, REJECTING drift and mismatch (C6).

    Four loud refusals:

    1. an unknown field — ``extra="forbid"`` makes a swapped-format or
       schema-drifted sidecar a :class:`SidecarError`;
    2. a ``population`` field that does not name the neighbouring file — a sidecar
       swapped next to a different population;
    3. a ``population`` value that is absolute or escapes its directory — a leaked
       machine path;
    4. a ``population_sha256`` that no longer matches the neighbouring file's bytes
       — the population was edited after emission (skippable via
       ``verify_population_hash=False`` for a metadata-only read).

    The FULLER recompute-and-compare of ``model_digest`` / ``pool_sha256`` needs
    the model and pool objects and is plan 04's scoring-time loader (C6); this
    reader ships the local population binding those digests ride alongside.
    """
    path = Path(path)
    try:
        with path.open("rb") as handle:
            raw = handle.read(_rf7_input.MAX_BYTES + 1)
        if len(raw) > _rf7_input.MAX_BYTES:
            raise ValueError("JSON input exceeds byte cap")
        document = _rf7_input.loads(raw.decode("utf-8"))
    except (OSError, ValueError) as error:
        raise SidecarError(f"sidecar {path} could not be read: {error}") from error
    try:
        sidecar = Sidecar.model_validate(document)
    except ValidationError as error:
        raise SidecarError(f"sidecar {path} is invalid:\n{error}") from error

    # WR-03: the RELATIVE-path rule is the module docstring's promise and it
    # applies to BOTH path fields. It used to be enforced on `population` only,
    # so a sidecar carrying `"pool_path": "/Users/someone/pools/x.pool.json"`
    # validated clean and the pool digest was then verified against a file
    # outside the corpus, on one machine only. `pool_path` legitimately carries
    # nested segments (the pool lives in a subdirectory), so the length clause
    # that applies to `population` does not apply here — the other two do.
    pool_path = Path(sidecar.pool_path)
    if pool_path.is_absolute() or ".." in pool_path.parts:
        raise SidecarError(
            f"sidecar {path} names an absolute or escaping pool_path "
            f"{sidecar.pool_path!r}; pool_path is RELATIVE to the corpus root "
            f"(C6 — a machine path in a committed artifact breaks cross-machine "
            f"reproduction and lets the pool digest be verified against a file "
            f"outside the corpus)."
        )

    declared = sidecar.population
    declared_path = Path(declared)
    if declared_path.is_absolute() or ".." in declared_path.parts or len(declared_path.parts) != 1:
        raise SidecarError(
            f"sidecar {path} names an absolute, nested, or escaping population "
            f"path {declared!r}; the sidecar lives beside its population, so the "
            f"field must be a bare relative filename (C6 — a machine path breaks "
            f"cross-machine reproduction)."
        )
    # The sidecar for population <stem>.<ext> is named <stem>.meta.json. A sidecar
    # swapped next to a different population declares a name whose derived sidecar
    # name no longer matches this file — caught here (C6).
    if declared_path.with_suffix(".meta.json").name != path.name:
        raise SidecarError(
            f"sidecar {path} names population {declared!r}, whose sidecar would be "
            f"{declared_path.with_suffix('.meta.json').name!r}, not this file — a "
            f"swapped or stale sidecar (C6)."
        )
    neighbour = path.parent / declared
    if not neighbour.exists():
        raise SidecarError(
            f"sidecar {path} names population {declared!r} but no such file sits beside it (C6)."
        )
    if verify_population_hash:
        actual = _sha256_file(neighbour)
        if actual != sidecar.population_sha256:
            raise SidecarError(
                f"sidecar {path} records population_sha256 "
                f"{sidecar.population_sha256!r} but {declared!r} now hashes to "
                f"{actual!r} — the population was edited after emission (C6)."
            )
    return sidecar


model_digest = validated_model_sha256  # RF2 compatibility alias.
