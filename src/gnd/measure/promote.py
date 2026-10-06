"""D-14 promotion: a defect-revealing population becomes a permanent corpus case.

D-14's rule is that generated populations are NOT checked in wholesale — they are
produced on demand from a seed — and that the ones which reveal a defect are
promoted into ``tests/fixtures/adversarial/`` permanently, carrying the seed and
the defect they caught. The corpus's whole value is that every case earned its
place, so the APPEND stays a reviewed human act: this module copies the inputs
and EMITS rows that are correct by construction; it never edits the manifest and
never touches ``tests/test_adversarial_corpus.py``.

**The ``why`` prose is the load-bearing field.** The runner interpolates it into
the failure message, so it is the text that stops a future engineer "fixing" a
red test by loosening the rule. It states what the case reported BEFORE the fix,
plus the seed, the generator version, and the case kind that produced it — D-14
requires the seed to travel with the case, and a case that cannot be regenerated
is a case nobody can reason about.

**Two corpora, two rules, both intact (the D-14 tension).**
``tests/fixtures/adversarial/`` stays hand-curated and grows only by review; the
phase's committed ``02-corpus/`` is a different artifact with a different
purpose — the pinned INPUT of a published number, committed under the owner's
rule that whatever corpus a published number was computed from is committed next
to the report. One is a regression suite, the other is a receipt.

**T-02-23 / T-02-24.** Destinations are built through ``synth.paths.slug`` and
``safe_output_path`` rooted at the corpus directory, so a model-derived filename
cannot escape it. Rows are emitted through the YAML writer with quoting rather
than string concatenation, then PARSED BACK and validated against the locked
record shape before being offered — a ``why`` string carrying YAML control
characters cannot forge manifest structure.
"""

from __future__ import annotations

import hashlib  # noqa: F401 -- historical compatibility binding
import io
import os
import shutil
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ruamel.yaml import YAML

from gnd.checker import CheckReport, ConstraintVerdict, band
from gnd.model import Model
from gnd.synth.paths import safe_output_path, slug
from gnd.synth.provenance import Sidecar

__all__ = [
    "MANIFEST_RECORD_KEYS",
    "PromotionError",
    "expected_exit_for",
    "manifest_rows",
    "promote_case",
    "render_manifest_rows",
]

#: The LOCKED record shape (``tests/fixtures/adversarial/manifest.yaml:1-30``).
#: ``id`` / ``expected_exit`` / ``why`` are required; the rest are optional by
#: the manifest's own header note. Emitted rows are validated against this before
#: they are offered for append.
MANIFEST_RECORD_KEYS = (
    "id",
    "command",
    "model",
    "population",
    "expected_exit",
    "why",
    "expect_rule_ids",
    "expect_reason_codes",
)

_REQUIRED_KEYS = ("id", "expected_exit", "why")


class PromotionError(Exception):
    """A promotion could not be produced correctly by construction."""


def expected_exit_for(model: Model, sidecar: Sidecar) -> int:
    """The exit code a CORRECT checker must produce over the promoted case.

    Derived by running the sidecar's EXPECTED verdicts through
    :func:`gnd.checker.band` — the single owner of the exit-band rule — rather
    than by guessing from the defect kind. A promoted case whose expected exit
    was hand-typed would pin the wrong thing the moment the band precedence
    changed, and the band rule already exists precisely so no second copy is
    written.
    """
    from gnd.measure.truth import ConstraintRefError, resolve_constraint_ref

    verdicts: list[ConstraintVerdict] = []
    for ref, state in sorted(sidecar.expectations.items()):
        try:
            constraint = resolve_constraint_ref(model, ref)
        except (ConstraintRefError, KeyError, IndexError, ValueError) as error:
            raise PromotionError(
                f"the sidecar labels {ref!r}, which does not resolve against the model "
                f"being promoted — the corpus case would pin a ref nobody can read: {error}"
            ) from error
        verdicts.append(
            ConstraintVerdict(
                scope_id=f"composition:oracle-verdict:n-a:{state.expected_verdict}",
                constraint_ref=ref,
                constraint_type=str(constraint.get("type") or ""),
                modality=str(constraint.get("modality") or ""),
                # R-01/P-4: the REAL resolved constraint's provenance, matching
                # measure/report.py's constraint.get("source"/"status") join —
                # never a field default, so the promoted corpus stays faithful.
                source=str(constraint.get("source") or ""),
                status=str(constraint.get("status") or ""),
                verdict=state.expected_verdict,
                message="",
            )
        )
    return band(CheckReport(verdicts=verdicts))


def _case_id(defect: dict[str, Any]) -> str:
    return slug(
        f"promoted-{defect['kind']}-{defect['constraint_ref']}-{defect['seed']}"
    ).removesuffix(".")


def _digest(path: Path) -> str:
    from gnd.safefs import file_sha256

    return '' + file_sha256(path)


@dataclass(frozen=True)
class _PromotionPlan:
    copied: dict[str, str]
    sources: tuple[tuple[Path, str], ...]


def _plan_case(
    defect: dict[str, Any],
    model_path: str | Path,
    corpus_dir: Path,
    *,
    populations_root: str | Path | None,
) -> _PromotionPlan:
    """Validate one promotion and describe its copies without writing them."""
    source_population = Path(populations_root or ".") / defect["population"]
    if not source_population.is_file():
        raise PromotionError(
            f"the defect names population {source_population} but no such file exists; "
            f"a promoted case whose input is gone cannot be a regression test"
        )
    model_source = Path(model_path)
    if not model_source.is_file():
        raise PromotionError(f"model {model_source} does not exist")

    model_suffix = model_source.suffix or ".yaml"
    model_rel = (
        f"models/{slug(model_source.stem)}.{_digest(model_source)[:16]}{model_suffix}"
    )
    population_suffix = source_population.suffix or ".json"
    population_rel = (
        f"populations/{_case_id(defect)}.{_digest(source_population)[:16]}"
        f"{population_suffix}"
    )
    sources: list[tuple[Path, str]] = [
        (model_source, model_rel),
        (source_population, population_rel),
    ]

    sidecar_ref = defect.get("sidecar") or ""
    if sidecar_ref:
        sidecar_source = Path(populations_root or ".") / sidecar_ref
        if not sidecar_source.is_file():
            raise PromotionError(
                f"the defect names sidecar {sidecar_source} but no such file exists"
            )
        sidecar_rel = f"populations/{Path(population_rel).stem}.meta.json"
        sources.append((sidecar_source, sidecar_rel))

    for _source, relative in sources:
        safe_output_path(corpus_dir, relative)
    return _PromotionPlan(
        copied={"model": model_rel, "population": population_rel},
        sources=tuple(sources),
    )


def _commit_plans(plans: list[_PromotionPlan], corpus_dir: Path) -> None:
    """Stage and commit a preflighted promotion batch with rollback on error."""
    copies: dict[str, Path] = {}
    for plan in plans:
        for source, relative in plan.sources:
            prior = copies.get(relative)
            if prior is not None and prior.read_bytes() != source.read_bytes():
                raise PromotionError(
                    f"two promoted inputs collide at {relative!r} with different bytes"
                )
            copies[relative] = source

    # Refuse every conflict before staging or changing the permanent corpus.
    for relative, source in copies.items():
        destination = safe_output_path(corpus_dir, relative)
        if destination.exists() and (
            not destination.is_file() or destination.read_bytes() != source.read_bytes()
        ):
            raise PromotionError(
                f"refusing to replace existing promoted input {destination}: bytes differ"
            )

    corpus_dir.parent.mkdir(parents=True, exist_ok=True)
    stage_root = Path(
        tempfile.mkdtemp(
            prefix=f".{corpus_dir.name}.promotion-", dir=corpus_dir.parent
        )
    )
    created: list[Path] = []
    try:
        for relative, source in copies.items():
            staged = safe_output_path(stage_root, relative)
            staged.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, staged)
            with staged.open("rb") as handle:
                os.fsync(handle.fileno())

        corpus_dir.mkdir(parents=True, exist_ok=True)
        for relative, source in copies.items():
            staged = safe_output_path(stage_root, relative)
            destination = safe_output_path(corpus_dir, relative)
            destination.parent.mkdir(parents=True, exist_ok=True)
            if destination.exists():
                if destination.read_bytes() != source.read_bytes():
                    raise PromotionError(
                        f"refusing concurrent replacement of {destination}: bytes differ"
                    )
                continue
            os.replace(staged, destination)
            created.append(destination)
    except Exception:
        for destination in reversed(created):
            destination.unlink(missing_ok=True)
        raise
    finally:
        shutil.rmtree(stage_root, ignore_errors=True)


def promote_case(
    defect: dict[str, Any],
    model_path: str | Path,
    sidecar: Sidecar,
    corpus_dir: str | Path,
    *,
    populations_root: str | Path | None = None,
) -> dict[str, str]:
    """Copy a defect-revealing population and its model into the corpus.

    Returns ``{"model": <relative>, "population": <relative>}`` — paths RELATIVE
    to the manifest's directory, which is what the runner resolves against. Every
    destination goes through ``safe_output_path``, so a model-derived name cannot
    write outside ``corpus_dir`` (T-02-23).

    ``populations_root`` is the corpus the defect was measured over. A defect's
    ``population`` is a corpus-root-relative identifier, not a file handle
    (F-05), so it is joined to that root to be READ; without the root it would
    resolve against the process CWD, which is the CR-01 defect at the promotion
    layer.
    """
    del sidecar  # manifest_rows validates its semantics through expected_exit_for
    corpus_path = Path(corpus_dir)
    plan = _plan_case(
        defect,
        model_path,
        corpus_path,
        populations_root=populations_root,
    )
    _commit_plans([plan], corpus_path)
    return plan.copied


def manifest_rows(
    defects: list[dict[str, Any]],
    model: Model,
    model_path: str | Path,
    sidecars: dict[str, Sidecar],
    corpus_dir: str | Path,
    *,
    generator_version: str,
    populations_root: str | Path | None = None,
) -> list[dict[str, Any]]:
    """Rows in the LOCKED record shape, one per defect, inputs copied.

    ``sidecars`` maps a defect's ``population`` path to the sidecar that labels
    it. Each row's ``expected_exit`` is derived through :func:`expected_exit_for`
    and each ``why`` states what the case reported BEFORE the fix, with the seed,
    the generator version and the case kind that produced it (D-14).

    ``populations_root`` is the corpus root the defects' corpus-relative paths
    are joined to for reading (F-05).
    """
    rows: list[dict[str, Any]] = []
    plans: list[_PromotionPlan] = []
    seen_case_ids: dict[str, str] = {}
    for defect in sorted(
        defects, key=lambda d: (d["constraint_ref"], d["population"], d["kind"])
    ):
        sidecar = sidecars.get(defect["population"])
        if sidecar is None:
            raise PromotionError(
                f"no sidecar for {defect['population']}; the case's ground truth would be "
                f"prose rather than a machine-readable label"
            )
        case_id = _case_id(defect)
        prior_population = seen_case_ids.get(case_id)
        if prior_population is not None:
            raise PromotionError(
                f"case-id collision: {case_id!r} names both {prior_population!r} "
                f"and {defect['population']!r}"
            )
        seen_case_ids[case_id] = defect["population"]
        plan = _plan_case(
            defect,
            model_path,
            Path(corpus_dir),
            populations_root=populations_root,
        )
        case_kind = sidecar.case_kind or sidecar.class_
        row = {
            "id": case_id,
            "command": "check",
            "model": plan.copied["model"],
            "population": plan.copied["population"],
            "expected_exit": expected_exit_for(model, sidecar),
            "why": (
                f"Promoted by `gnd measure --promote` (D-14). Before the fix this "
                f"population reported {defect['observed_verdict']!r} for "
                f"{defect['constraint_ref']} where the independent oracle establishes "
                f"{defect['expected_verdict']!r} — a {defect['kind']} on a "
                f"{defect['modality']} constraint, which under D-01 is a reproducible "
                f"defect to fix, not a rate to write down. Regenerate with seed "
                f"{defect['seed']} under {generator_version} from the "
                f"{case_kind} class. If this case ever goes green by the verdict "
                f"CHANGING rather than by the checker being fixed, that is the defect "
                f"returning: do not loosen the expectation."
            ),
        }
        reason_codes = defect.get("expect_reason_codes")
        if reason_codes:
            row["expect_reason_codes"] = list(reason_codes)
        _validate_row(row)
        rows.append(row)
        plans.append(plan)
    # Validate hostile-string-safe YAML for every row before touching the
    # permanent corpus. The caller renders again for output, byte-identically.
    render_manifest_rows(rows)
    _commit_plans(plans, Path(corpus_dir))
    return rows


def _validate_row(row: dict[str, Any]) -> None:
    unknown = set(row) - set(MANIFEST_RECORD_KEYS)
    if unknown:
        raise PromotionError(
            f"emitted row carries keys outside the LOCKED record shape: {sorted(unknown)}"
        )
    missing = [key for key in _REQUIRED_KEYS if key not in row]
    if missing:
        raise PromotionError(f"emitted row is missing required keys: {missing}")
    if not isinstance(row["expected_exit"], int):
        raise PromotionError("expected_exit must be an int")


def render_manifest_rows(rows: list[dict[str, Any]]) -> str:
    """The rows as YAML, written by the YAML writer and PARSED BACK.

    String concatenation is how a ``why`` carrying ``\\n`` or ``:`` forges
    manifest structure (T-02-24). Emitting through ``ruamel.yaml`` quotes what
    needs quoting; parsing the result back and re-validating each row against the
    locked shape proves the emission round-trips to the same records.
    """
    yaml = YAML()
    yaml.default_flow_style = False
    yaml.width = 88
    buffer = io.StringIO()
    yaml.dump({"cases": rows}, buffer)
    text = buffer.getvalue()

    reread = YAML(typ="safe").load(io.StringIO(text))
    if not isinstance(reread, dict) or list(reread) != ["cases"]:
        raise PromotionError("the emitted YAML did not round-trip to a `cases` mapping")
    if len(reread["cases"]) != len(rows):
        raise PromotionError(
            f"the emitted YAML round-tripped to {len(reread['cases'])} case(s), not "
            f"{len(rows)} — a `why` string forged manifest structure (T-02-24)"
        )
    for original, parsed in zip(rows, reread["cases"], strict=True):
        _validate_row(dict(parsed))
        if parsed["id"] != original["id"] or parsed["why"] != original["why"]:
            raise PromotionError("a promoted row did not survive its own serialization")
    return text
