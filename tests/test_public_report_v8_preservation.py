from __future__ import annotations

from gnd.report import load_report_schema

ANSWERS = {'unchanged_report_versions': [3, 4, 5, 6, 7]}

def _version_constants(value: object) -> set[int]:
    found: set[int] = set()
    if isinstance(value, dict):
        if value.get('const') in range(3, 9):
            found.add(value['const'])
        for child in value.values():
            found.update(_version_constants(child))
    elif isinstance(value, list):
        for child in value:
            found.update(_version_constants(child))
    return found

def test_report_schema_adds_only_version_8() -> None:
    versions = _version_constants(load_report_schema())
    assert set(ANSWERS['unchanged_report_versions']).issubset(versions)
    assert 8 in versions
