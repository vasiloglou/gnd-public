"""LR2: a span may lie anywhere in the document its anchor sidecar names.

One source has two sections; the quoted value is in the second. The rule is
held from both sides through the real ``gnd check --anchors --document``, and
the refusal is pinned to the span branch, not the digest check.
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import unicodedata
from pathlib import Path

from gnd.anchors import vocabulary_digest
from gnd.model import load_model

ROOT = Path(__file__).resolve().parents[1]
RULE = "A span may lie anywhere in the document whose SHA-256 is `document_sha256`."
LINK = "../reference/anchors.md#where-a-span-may-lie"
SECTION_A = "Section A. The study introduces record R-1 and its scope.\n"
SECTION_B = "Section B. Record R-1 bears the label Beta Harbor in the methods.\n"
VALUE = "Beta Harbor"
MODEL = (
    "version: 2\nmodel_id: urn:gnd-fixture:lr2-quote-scope@1\n"
    "source: {kind: text-conversation, confidence: standard, mode: one-shot}\n"
    "object_types:\n  - {id: record, name: Record, kind: value, primitive: String}\n"
    "  - {id: label, name: Label, kind: value, primitive: String}\n"
    "fact_types:\n  - id: record_has_label\n    reading: \"{Record} has label {Label}\"\n"
    "    roles: [{object_type: record, role_name: record}, {object_type: label, role_name: label}]\n"
    "    constraints:\n      - {type: anchored, role: label, source: explicit, status: confirmed,"
    " modality: alethic, provenance: {user_quote: x}}\n"
    "constraints: []\nrejected_proposals: []\n"
)


def _sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _case(tmp_path: Path, *, document: str, named: str) -> subprocess.CompletedProcess:
    """Write the model, population, the document checked and a sidecar naming ``named``."""
    (tmp_path / "model.orm.yaml").write_text(MODEL, encoding="utf-8")
    population = json.dumps({
        "population": {"model": "model.orm.yaml", "model_id": "urn:gnd-fixture:lr2-quote-scope@1",
                       "label": "conforming", "source": "fixture", "covers": ["record_has_label"]},
        "instances": {},
        "facts": {"record_has_label": [{"record": "R-1", "label": VALUE}]},
    }).encode("utf-8")
    (tmp_path / "population.json").write_bytes(population)
    (tmp_path / "document.txt").write_bytes(document.encode("utf-8"))
    whole = unicodedata.normalize("NFC", SECTION_A + SECTION_B)
    start = whole.index(VALUE)
    end = start + len(VALUE)
    sidecar = {
        "schema_version": 2,
        "population_sha256": _sha(population),
        "vocabulary_digest": vocabulary_digest(load_model(tmp_path / "model.orm.yaml")),
        "document_sha256": _sha(named.encode("utf-8")),
        "anchors": [{
            "fact_key": {"fact_type": "record_has_label", "roles": {"record": "R-1", "label": VALUE}},
            "role": "label",
            "span": {"start": start, "end": end},
            "occurrence": 0,
            "excerpt_sha256": _sha(whole[start:end].encode("utf-8")),
            "block_id": "section-a",
        }],
    }
    (tmp_path / "population.json.anchors.json").write_text(json.dumps(sidecar), encoding="utf-8")
    env = {key: value for key, value in os.environ.items() if key != "GND_DISCLOSURE"}
    return subprocess.run(
        [sys.executable, "-m", "gnd", "check", "model.orm.yaml", "population.json", "--anchors",
         "population.json.anchors.json", "--document", "document.txt", "--format", "json"],
        cwd=tmp_path, env=env, capture_output=True, text=True, check=False)


def test_t1_a_quote_from_another_section_binds_against_the_whole_source(tmp_path: Path) -> None:
    done = _case(tmp_path, document=SECTION_A + SECTION_B, named=SECTION_A + SECTION_B)
    assert done.returncode == 0, done.stdout + done.stderr
    report = json.loads(done.stdout)
    (anchored,) = [v for v in report["verdicts"] if v["constraint_type"] == "anchored"]
    assert anchored["verdict"] == "pass"


def test_t2_the_span_rule_refuses_when_the_document_is_the_shown_section(tmp_path: Path) -> None:
    done = _case(tmp_path, document=SECTION_A, named=SECTION_A)
    assert done.returncode == 3
    assert "anchor:binding-mismatch: source span or excerpt differs" in done.stdout + done.stderr
    assert "digest differs" not in done.stdout + done.stderr


def test_t3_a_sidecar_naming_another_document_is_the_digest_refusal(tmp_path: Path) -> None:
    done = _case(tmp_path, document=SECTION_A, named=SECTION_A + SECTION_B)
    assert done.returncode == 3
    assert "anchor:binding-mismatch: digest differs" in done.stdout + done.stderr


def test_t4_the_rule_has_one_home_and_the_literature_pages_cite_it() -> None:
    pages = [*sorted((ROOT / "docs").rglob("*.md")), *sorted((ROOT / "src" / "gnd" / "skills").rglob("*.md"))]
    homes = [page.relative_to(ROOT).as_posix() for page in pages if RULE in page.read_text(encoding="utf-8")]
    assert homes == ["docs/reference/anchors.md"]
    for page in ("docs/literature/index.md", "docs/literature/commands.md"):
        assert LINK in (ROOT / page).read_text(encoding="utf-8"), page


def test_t5_the_example_readme_says_what_it_verifies() -> None:
    text = " ".join((ROOT / "src/gnd/examples/literature/README.md").read_text(encoding="utf-8").split())
    for claim in ("the attempted sections of that pass joined with newlines",
                  "for the reported conflict, `conflict.txt`",
                  "binds its document by digest in an extraction sidecar",
                  "writes no anchor sidecar"):
        assert claim in text, claim
    assert "https://vasiloglou.github.io/gnd-public/reference/anchors/#where-a-span-may-lie" in text
