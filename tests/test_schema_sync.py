"""Byte-identity guard between canonical and vendored schema copies (D-07).

The canonical schemas live in the gnd-orm-core references skill; the gnd
package vendors byte-identical copies for runtime use. If this test fails,
edit the CANONICAL copy (src/gnd/skills/gnd-orm-core/references/) and
regenerate the vendored copy (src/gnd/schema/) from it — never the other way
around.

Deliberate asymmetry — do NOT "fix" this by adding it to SCHEMA_PAIRS:
``src/gnd/report.schema.json`` is intentionally vendored-only, has no canonical
twin in the gnd-orm-core references, and lives OUTSIDE ``src/gnd/schema/``. It
describes the ``--format json`` payload, which is a runtime OUTPUT contract of
the ``gnd`` CLI — not an interchange *format* the gnd-orm-core skill documents
authoring rules for. Giving it a canonical twin would expand that skill's remit
to cover a contract no model or population author ever writes. Its own
round-trip guard lives in ``tests/test_report_json.py``, which validates real
payloads against it on every exit path.

The second exception: the two type schemas (TS3) are canonical at the runtime
``src/gnd/`` files and vendored into the gnd-orm-core references, the reverse
of SCHEMA_PAIRS; their own case is at the end of this file.
"""


import pytest
from support.repository import REPO_ROOT

CANONICAL_DIR = REPO_ROOT / "src" / "gnd" / "skills" / "gnd-orm-core" / "references"
VENDORED_DIR = REPO_ROOT / "src" / "gnd" / "schema"

SCHEMA_PAIRS = [
    "orm-meta.schema.json",
    "population.schema.json",
    # steps.schema.json is an INPUT interchange format -- a walk is a document a
    # caller authors and hands us, exactly like a model or a population -- so it
    # is paired, unlike the deliberately vendored-only report.schema.json above.
    "steps.schema.json",
]

@pytest.mark.parametrize("filename", SCHEMA_PAIRS)
def test_canonical_and_vendored_schemas_are_byte_identical(filename: str) -> None:
    canonical = CANONICAL_DIR / filename
    vendored = VENDORED_DIR / filename

    assert canonical.is_file(), f"canonical schema missing: {canonical}"
    assert vendored.is_file(), f"vendored schema missing: {vendored}"

    assert canonical.read_bytes() == vendored.read_bytes(), (
        f"{filename} has drifted between the canonical copy "
        f"({canonical}) and the vendored copy ({vendored}). "
        "The canonical schema lives in the gnd-orm-core skill: edit "
        "src/gnd/skills/gnd-orm-core/references/ and regenerate the vendored "
        "copy in src/gnd/schema/ from it (copy the canonical file over the "
        "vendored one)."
    )




#: CT3: the witness schema's canonical copy is the gnd-export reference, not
#: gnd-orm-core; witness version 2 changes both copies together.
EXPORT_CANONICAL_DIR = REPO_ROOT / "src" / "gnd" / "skills" / "gnd-export" / "references"


def test_witness_schema_twins_are_byte_identical() -> None:
    canonical = EXPORT_CANONICAL_DIR / "witness.schema.json"
    vendored = VENDORED_DIR / "witness.schema.json"
    assert canonical.read_bytes() == vendored.read_bytes(), (
        "witness.schema.json has drifted between src/gnd/skills/gnd-export/references/ "
        "and src/gnd/schema/; copy the reference over the vendored file."
    )


#: TS3 (spec D5): the two type schemas run the other way. gnd discover owns
#: src/gnd/type-evidence.schema.json and src/gnd/type-judgements.schema.json;
#: the gnd-orm-core copies are read-only, regenerated from the runtime files.
TYPE_SCHEMAS = ["type-evidence.schema.json", "type-judgements.schema.json"]


@pytest.mark.parametrize("filename", TYPE_SCHEMAS)
def test_type_schema_copies_are_byte_identical_to_the_runtime_files(filename: str) -> None:
    runtime = REPO_ROOT / "src" / "gnd" / filename
    copy = CANONICAL_DIR / filename
    assert copy.read_bytes() == runtime.read_bytes(), (
        f"{filename} has drifted: the runtime src/gnd/{filename} is canonical; "
        "copy it over src/gnd/skills/gnd-orm-core/references/."
    )
