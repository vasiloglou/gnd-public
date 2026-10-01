"""The skill-to-code handoff contracts and the matcher-side identity module
(R-04‴, R-05″, D-15).

The document manifest and the extraction sidecar are the ONLY interface between
the two skills (gnd-render-doc, gnd-extract) and the code validators (`gnd
verify`, `gnd doccheck`). Both are untrusted input naming paths and digests, so
both load STRICTLY: ``extra="forbid"`` (a swapped-format or schema-drifted file
fails loud, provenance.py's D-15 discipline), three-plus REQUIRED sha256 digests
(C6 binding — the digest is the identity, WR-02), and RELATIVE paths only
(test_measure_corpus_root's untrusted-index rule: an absolute or ``..``-escaping
entry is refused, never resolved).

``identity.py`` is the matcher-side scalar identity: the SAME specified domains
as ``synth/identity.scalar_identity`` — booleans / numbers / strings separate —
implemented independently (C1: the matcher must not call the checker it is
composed with, and must not import the synthesis oracle either; P-6/F-7 is the
precedent bug), applied AFTER R-10's lexical normalization and only to strings.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from gnd.extract.identity import identity_key, lexical_normalize
from gnd.extract.manifest import (
    DocumentManifest,
    ExtractionSidecar,
    ManifestError,
    read_document_manifest,
    read_extraction_sidecar,
)

DIGEST = hashlib.sha256(b"x").hexdigest()


def _manifest_doc(**overrides: object) -> dict:
    doc: dict = {
        "schema_version": 1,
        "document": "doc.md",
        "document_sha256": DIGEST,
        "model": "full_vocabulary.orm.yaml",
        "model_sha256": DIGEST,
        "source_population": "pop.json",
        "source_population_sha256": DIGEST,
        "applicable_sha256": DIGEST,
        "renderer_skill": "gnd-render-doc",
        "renderer_skill_version": "1",
        "executing_model": "claude-fable-5",
        "distractors": [
            {"kind": "out-of-model", "text": "The office ficus is thriving."},
            {"kind": "near-miss-entity", "text": "employee 90211 also exists."},
            {
                "kind": "absent-fact",
                "text": "Zelda leads aurora-lattice.",
                "fact_type": "employee_leads_project",
                "roles": {"employee": 90210, "project": "aurora-lattice"},
            },
        ],
    }
    doc.update(overrides)
    return doc


def _sidecar_doc(**overrides: object) -> dict:
    doc: dict = {
        "schema_version": 1,
        "population": "pop.json",
        "population_sha256": DIGEST,
        "model": "full_vocabulary.orm.yaml",
        "model_sha256": DIGEST,
        "projection_sha256": DIGEST,
        "document": "doc.md",
        "document_sha256": DIGEST,
        "skill": "gnd-extract",
        "skill_version": "1",
        "executing_model": "claude-fable-5",
    }
    doc.update(overrides)
    return doc


def _write(tmp_path: Path, name: str, doc: dict) -> Path:
    path = tmp_path / name
    path.write_text(json.dumps(doc), encoding="utf-8")
    return path


# --- strict loading: unknown fields, missing digests, path escapes ---


def test_unknown_field_is_rejected(tmp_path: Path) -> None:
    """extra="forbid" in practice: an unknown field in EITHER contract file is a
    load-time ManifestError NAMING the field — a schema-drifted or swapped file
    can never be read as valid (provenance.py's D-15 discipline)."""
    manifest = _write(tmp_path, "m.json", _manifest_doc(surprise="?"))
    with pytest.raises(ManifestError) as manifest_error:
        read_document_manifest(manifest)
    assert "surprise" in str(manifest_error.value)

    sidecar = _write(tmp_path, "s.json", _sidecar_doc(fidelity=1.0))
    with pytest.raises(ManifestError) as sidecar_error:
        read_extraction_sidecar(sidecar)
    assert "fidelity" in str(sidecar_error.value)


@pytest.mark.parametrize(
    "path_value",
    [
        "/abs/pop.json",
        "../escape/pop.json",
        "a/../../escape.json",
        "\\Windows\\System32",
        "C:drive-relative.json",
        "",
        "   ",
        "doc\x00.md",
    ],
    ids=[
        "absolute",
        "parent-escape",
        "nested-escape",
        "windows-root",
        "windows-drive-relative",
        "empty",
        "blank",
        "nul",
    ],
)
def test_absolute_and_escaping_paths_are_rejected(
    tmp_path: Path, path_value: str
) -> None:
    """Path fields are UNTRUSTED input (test_measure_corpus_root's rule): an
    absolute or parent-escaping entry is refused at load, never resolved."""
    sidecar = _write(tmp_path, "s.json", _sidecar_doc(population=path_value))
    with pytest.raises(ManifestError):
        read_extraction_sidecar(sidecar)

    manifest = _write(tmp_path, "m.json", _manifest_doc(document=path_value))
    with pytest.raises(ManifestError):
        read_document_manifest(manifest)


def test_missing_digest_is_rejected(tmp_path: Path) -> None:
    """Every *_sha256 field is REQUIRED with no default (C6: the digest IS the
    binding; an optional digest is an optional binding)."""
    for field in (
        "document_sha256",
        "model_sha256",
        "source_population_sha256",
        "applicable_sha256",
    ):
        doc = _manifest_doc()
        del doc[field]
        path = _write(tmp_path, "m.json", doc)
        with pytest.raises(ManifestError):
            read_document_manifest(path)

    for field in (
        "population_sha256",
        "model_sha256",
        "projection_sha256",
        "document_sha256",
    ):
        doc = _sidecar_doc()
        del doc[field]
        path = _write(tmp_path, "s.json", doc)
        with pytest.raises(ManifestError):
            read_extraction_sidecar(path)


def test_bad_distractor_kind_is_rejected(tmp_path: Path) -> None:
    """R-05: the three distractor kinds are a CLOSED vocabulary — a kind outside
    {out-of-model, near-miss-entity, absent-fact} is rejected at load."""
    doc = _manifest_doc()
    doc["distractors"][0]["kind"] = "helpful-extra"
    path = _write(tmp_path, "m.json", doc)
    with pytest.raises(ManifestError):
        read_document_manifest(path)


def test_absent_fact_distractor_requires_fact_type_and_roles(tmp_path: Path) -> None:
    """An absent-fact distractor without {fact_type, roles} cannot be checked
    for genuine absence (doccheck obligation 3), so it fails closed at load."""
    doc = _manifest_doc()
    doc["distractors"][2] = {"kind": "absent-fact", "text": "Zelda leads."}
    path = _write(tmp_path, "m.json", doc)
    with pytest.raises(ManifestError):
        read_document_manifest(path)

    for invalid in ("", None):
        doc = _manifest_doc()
        doc["distractors"][2]["fact_type"] = invalid
        path = _write(tmp_path, "m.json", doc)
        with pytest.raises(ManifestError):
            read_document_manifest(path)

    doc = _manifest_doc()
    doc["distractors"][2]["roles"] = {}
    path = _write(tmp_path, "m.json", doc)
    with pytest.raises(ManifestError):
        read_document_manifest(path)


def test_valid_contracts_load(tmp_path: Path) -> None:
    manifest = read_document_manifest(_write(tmp_path, "m.json", _manifest_doc()))
    assert isinstance(manifest, DocumentManifest)
    assert manifest.renderer_skill == "gnd-render-doc"
    assert [d.kind for d in manifest.distractors] == [
        "out-of-model",
        "near-miss-entity",
        "absent-fact",
    ]

    sidecar = read_extraction_sidecar(_write(tmp_path, "s.json", _sidecar_doc()))
    assert isinstance(sidecar, ExtractionSidecar)
    assert sidecar.skill == "gnd-extract"
    assert sidecar.population_sha256 == DIGEST


@pytest.mark.parametrize("version", [None, 0, 2, 999])
def test_protocol_version_is_required_and_fixed(tmp_path: Path, version: int | None) -> None:
    manifest_doc = _manifest_doc()
    sidecar_doc = _sidecar_doc()
    if version is None:
        manifest_doc.pop("schema_version")
        sidecar_doc.pop("schema_version")
    else:
        manifest_doc["schema_version"] = version
        sidecar_doc["schema_version"] = version

    with pytest.raises(ManifestError):
        read_document_manifest(_write(tmp_path, "m.json", manifest_doc))
    with pytest.raises(ManifestError):
        read_extraction_sidecar(_write(tmp_path, "s.json", sidecar_doc))


@pytest.mark.parametrize(
    ("manifest_overrides", "sidecar_overrides"),
    [
        ({"renderer_skill": "gnd-extract"}, {"skill": "gnd-render-doc"}),
        ({"renderer_skill_version": ""}, {"skill_version": ""}),
        ({"executing_model": "   "}, {"executing_model": "   "}),
    ],
)
def test_handoff_identities_are_exact_and_nonempty(
    tmp_path: Path,
    manifest_overrides: dict[str, object],
    sidecar_overrides: dict[str, object],
) -> None:
    with pytest.raises(ManifestError):
        read_document_manifest(
            _write(tmp_path, "m.json", _manifest_doc(**manifest_overrides))
        )
    with pytest.raises(ManifestError):
        read_extraction_sidecar(
            _write(tmp_path, "s.json", _sidecar_doc(**sidecar_overrides))
        )


def test_oversized_manifest_is_rejected(tmp_path: Path) -> None:
    """The read is byte-capped (report.py's MAX_POPULATION_ISSUES posture:
    bound every untrusted-input-proportional resource)."""
    from gnd.extract.manifest import MAX_MANIFEST_BYTES

    doc = _sidecar_doc(executing_model="x" * (MAX_MANIFEST_BYTES + 1))
    path = _write(tmp_path, "s.json", doc)
    with pytest.raises(ManifestError):
        read_extraction_sidecar(path)


# --- the matcher-side identity module ---


def test_lexical_normalize_is_lexical_only_and_strings_only() -> None:
    """R-10: casefold + collapse internal whitespace runs + strip — nothing
    semantic, no aliasing — and it applies to STRINGS ONLY: every other type is
    returned unchanged."""
    assert lexical_normalize("  Ann   B ") == lexical_normalize("ann b")
    assert lexical_normalize("Ann\tB\nC") == "ann b c"
    assert lexical_normalize(140891) == 140891
    assert lexical_normalize(True) is True
    assert lexical_normalize(None) is None


def test_identity_domains_are_separate() -> None:
    """Booleans, numbers and strings are SEPARATE identity domains.

    Mutation this test guards (F-7, closed 2026-08-12, the precedent bug one
    layer down): keying on plain equality drops the domain tag, and Python's
    ``1 == True`` then folds a boolean filler into a numeric one — the exact
    identity collapse F-7 fixed in the checker. Switching ``identity_key`` to
    return the bare normalized value reds this test.
    """
    assert identity_key(1) != identity_key(True)
    assert identity_key(1) != identity_key("1")
    assert identity_key(True) != identity_key("1")


def test_identity_key_normalizes_strings_first() -> None:
    assert identity_key("  Ann   B ") == identity_key("ann b")
    assert identity_key("Ann") == ("string", "ann")
    assert identity_key(140891) == ("number", 140891)
    assert identity_key(False) == ("boolean", False)


# --- source-level contracts ---


def test_identity_module_is_independent() -> None:
    """C1 independence in both directions: the matcher-side identity imports
    NOTHING from gnd.checker (the implementation it is composed with) and
    NOTHING from gnd.synth (the oracle it must stay independent of)."""
    import ast

    source = (
        Path(__file__).resolve().parent.parent
        / "src"
        / "gnd"
        / "extract"
        / "identity.py"
    ).read_text(encoding="utf-8")
    imported: set[str] = set()
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.Import):
            imported.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imported.add(node.module or "")
    forbidden = {
        name
        for name in imported
        if name == "gnd"
        or name.startswith(("gnd.checker", "gnd.synth"))
    }
    assert not forbidden, (
        f"identity.py must not import the checker or the synthesis oracle "
        f"(C1 both directions, F-7 precedent); found {sorted(forbidden)}"
    )


def test_contracts_declare_extra_forbid_and_required_digests() -> None:
    """Source-level acceptance: both models forbid unknown fields, and every
    *_sha256 field is a required str with no default."""
    for model_cls in (DocumentManifest, ExtractionSidecar):
        assert model_cls.model_config.get("extra") == "forbid"
        for name, field in model_cls.model_fields.items():
            if name.endswith("_sha256"):
                assert field.is_required(), (
                    f"{model_cls.__name__}.{name} must be REQUIRED — an optional "
                    f"digest is an optional binding (C6)"
                )
                assert field.annotation is str
