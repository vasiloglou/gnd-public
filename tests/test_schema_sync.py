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


