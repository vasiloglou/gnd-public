"""``gnd doccheck MODEL MANIFEST --artifacts DIR`` — the renderer-obligation
validator, scoped by the applicable set (R-05″, R-10′, P-2).

Skill prose explains, VALIDATORS discharge: every obligation the
``gnd-render-doc`` skill takes on is checked here by code over the document
manifest — the digest binding, the reference-mention obligation, the three
distractor kinds, and the renderer identity fields.

The rendering obligation is enforced ONLY over fact types in the applicable
set, consumed fail-closed from the ``<stem>.applicable.json`` artifact
``gnd extract`` published (R-10′/P-2). RESEARCH's P-2 measured the
impossibility this scoping answers: enforced hard over everything, ALL
``full_vocabulary`` documents are rejected (``salary``'s unit-based reference
yields nothing to render), and the round trip never runs; enforced leniently,
the unmentioned-entity flatterer returns invisibly. The warning sign R-10′
names — a rendering check that passes on ``full_vocabulary`` with NO
not-applicable rows — is a standing assertion below.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest
from support.digests import sha256_bytes as _sha256_bytes

from gnd import cli

REPO_ROOT = Path(__file__).resolve().parent.parent
FULL_VOCAB = REPO_ROOT / "tests" / "fixtures" / "models" / "full_vocabulary.orm.yaml"

#: The document text mentions, under lexical_normalize, every role filler of
#: every APPLICABLE fact type in the source population: employee 90210 (direct,
#: employee_id), the name, the project — and the composite assignment filler
#: via its component values (90210 + aurora-lattice, R-10′ path 2). The salary
#: surrogate is deliberately NOT mentioned: employee_earns_salary is
#: inapplicable BY THE ARTIFACT, not by leniency.
DOCUMENT = (
    "Employee 90210, known as Zelda Quixote, works on project aurora-lattice.\n"
    "The assignment pairing employee 90210 with aurora-lattice is active.\n"
    "The office ficus is thriving.\n"
    "Employee 90211 also appears in hallway chatter.\n"
    "Zelda Quixote leads project aurora-lattice.\n"
)

DISTRACTORS = [
    {"kind": "out-of-model", "text": "The office ficus is thriving."},
    {"kind": "near-miss-entity", "text": "Employee 90211 also appears in hallway chatter."},
    {
        "kind": "absent-fact",
        "text": "Zelda Quixote leads project aurora-lattice.",
        "fact_type": "employee_leads_project",
        "roles": {"employee": 90210, "project": "aurora-lattice"},
    },
]

POPULATION = {
    "population": {"model": "full_vocabulary.orm.yaml", "source": "agent-output"},
    "facts": {
        "employee_has_name": [{"employee": 90210, "name": "Zelda Quixote"}],
        "employee_works_on_project": [{"employee": 90210, "project": "aurora-lattice"}],
        "assignment_of_employee": [
            {"assignment": "assignment-tok71", "employee": 90210}
        ],
        "assignment_on_project": [
            {"assignment": "assignment-tok71", "project": "aurora-lattice"}
        ],
        "employee_earns_salary": [{"employee": 90210, "salary": "salary-opq1"}],
    },
}


@pytest.fixture()
def workspace(tmp_path: Path) -> Path:
    """A rendered-document workspace: the extract bundle in ``artifacts/``,
    plus population, document and a digest-consistent manifest beside it."""
    artifacts = tmp_path / "artifacts"
    assert cli.main(["extract", str(FULL_VOCAB), "--out", str(artifacts)]) == 0

    (tmp_path / "pop.json").write_text(json.dumps(POPULATION), encoding="utf-8")
    (tmp_path / "doc.md").write_text(DOCUMENT, encoding="utf-8")
    _write_manifest(tmp_path)
    return tmp_path


def _write_manifest(root: Path, **overrides: object) -> Path:
    doc_bytes = (root / "doc.md").read_bytes()
    pop_bytes = (root / "pop.json").read_bytes()
    applicable_bytes = (root / "artifacts" / "full_vocabulary.applicable.json").read_bytes()
    manifest: dict = {
        "schema_version": 1,
        "document": "doc.md",
        "document_sha256": _sha256_bytes(doc_bytes),
        "model": "full_vocabulary.orm.yaml",
        "model_sha256": _sha256_bytes(FULL_VOCAB.read_bytes()),
        "source_population": "pop.json",
        "source_population_sha256": _sha256_bytes(pop_bytes),
        "applicable_sha256": _sha256_bytes(applicable_bytes),
        "renderer_skill": "gnd-render-doc",
        "renderer_skill_version": "1",
        "executing_model": "claude-fable-5",
        "distractors": json.loads(json.dumps(DISTRACTORS)),
    }
    manifest.update(overrides)
    path = root / "manifest.json"
    path.write_text(json.dumps(manifest), encoding="utf-8")
    return path


def _run_doccheck(root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            "-m",
            "gnd",
            "doccheck",
            str(FULL_VOCAB),
            str(root / "manifest.json"),
            "--artifacts",
            str(root / "artifacts"),
        ],
        capture_output=True,
        text=True,
        check=False,
        cwd=REPO_ROOT,
    )


def test_doccheck_passes_full_vocabulary_with_inapplicable_rows_present(
    workspace: Path,
) -> None:
    """The passing case asserts BOTH halves of R-10′'s warning sign: exit 0
    AND that the consumed applicable.json contains at least one INAPPLICABLE
    fact type on this model. A doccheck pass that coincides with an
    all-applicable artifact on full_vocabulary means the resolver regressed
    (salary's unit-based reference suddenly 'resolved'), not that rendering
    got easier — P-2's measured impossibility would be silently repealed."""
    result = _run_doccheck(workspace)
    assert result.returncode == 0, (
        f"expected exit 0; stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )

    applicable = json.loads(
        (workspace / "artifacts" / "full_vocabulary.applicable.json").read_text(
            encoding="utf-8"
        )
    )
    inapplicable = [row for row in applicable["fact_types"] if not row["applicable"]]
    assert inapplicable, (
        "the R-10' standing assertion: a doccheck pass on full_vocabulary must "
        "coexist with >=1 inapplicable fact type in the consumed artifact"
    )


def test_doccheck_rejects_unmentioned_applicable_entity(workspace: Path) -> None:
    """The P-2 gate's mutation check: removing one applicable entity's
    reference value from the document text flips exit 0 → 3, with the entity
    named in the output — the unmentioned-entity flatterer cannot return."""
    stripped = DOCUMENT.replace("Zelda Quixote", "the employee")
    (workspace / "doc.md").write_text(stripped, encoding="utf-8")
    # Keep the manifest digest-consistent (and drop the distractor whose text
    # named her) so the ONLY violation is the unmentioned reference value.
    distractors = json.loads(json.dumps(DISTRACTORS))
    distractors[2]["text"] = "the employee leads project aurora-lattice."
    _write_manifest(workspace, distractors=distractors)

    result = _run_doccheck(workspace)
    assert result.returncode == 3, (
        f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )
    assert "zelda quixote" in result.stdout.lower(), (
        "the violation line must NAME the unmentioned entity"
    )


def test_doccheck_requires_all_three_distractor_kinds(workspace: Path) -> None:
    """R-05: at least one of EACH kind — out-of-model, near-miss-entity,
    absent-fact. A manifest missing any one kind exits 3."""
    for missing_kind in ("out-of-model", "near-miss-entity", "absent-fact"):
        remaining = [
            d for d in json.loads(json.dumps(DISTRACTORS)) if d["kind"] != missing_kind
        ]
        _write_manifest(workspace, distractors=remaining)
        result = _run_doccheck(workspace)
        assert result.returncode == 3, (
            f"missing {missing_kind} must exit 3; stdout:\n{result.stdout}"
        )
        assert missing_kind in result.stdout


def test_doccheck_rejects_absent_fact_that_exists(workspace: Path) -> None:
    """An absent-fact distractor duplicating a SOURCE fact under identity_key
    is not a distractor — it is a fact, and treating it as a planted lie would
    train the extractor's evaluator on a false negative. Exit 3."""
    distractors = json.loads(json.dumps(DISTRACTORS))
    distractors[2] = {
        "kind": "absent-fact",
        "text": "Employee 90210, known as Zelda Quixote, works on project aurora-lattice.",
        "fact_type": "employee_works_on_project",
        "roles": {"employee": 90210, "project": "aurora-lattice"},
    }
    _write_manifest(workspace, distractors=distractors)
    result = _run_doccheck(workspace)
    assert result.returncode == 3, f"stdout:\n{result.stdout}"
    assert "employee_works_on_project" in result.stdout


def test_doccheck_missing_applicable_artifact_exits_66(workspace: Path) -> None:
    """A missing applicable-set artifact is EX_NOINPUT (66) — the 01.2/D-22
    missing-required-artifact precedent — never 0 (an unscoped obligation
    silently held) and never 3 (nothing was checked, so nothing 'violated');
    fail closed with the artifact named."""
    (workspace / "artifacts" / "full_vocabulary.applicable.json").unlink()
    result = _run_doccheck(workspace)
    assert result.returncode == 66, (
        f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )
    assert "full_vocabulary.applicable.json" in result.stdout


def test_doccheck_binding_mismatch_exits_3(workspace: Path) -> None:
    """Obligation 1: an edited document (digest no longer matching
    document_sha256) exits 3 — the manifest binds by digest, not by name."""
    (workspace / "doc.md").write_text(DOCUMENT + "\npostscript.", encoding="utf-8")
    result = _run_doccheck(workspace)
    assert result.returncode == 3, f"stdout:\n{result.stdout}"
    assert "document_sha256" in result.stdout


def test_doccheck_empty_renderer_identity_exits_3(workspace: Path) -> None:
    """Obligation 4: the renderer identity fields must be non-empty — an
    anonymous rendering is not attributable provenance (WR-02)."""
    _write_manifest(workspace, executing_model="   ")
    result = _run_doccheck(workspace)
    assert result.returncode == 3, f"stdout:\n{result.stdout}"
    assert "executing_model" in result.stdout
