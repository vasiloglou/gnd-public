"""Original current payload alias census over actual installed package source."""
import atexit
import tempfile
from pathlib import Path

from support.rf5_sources import cli_sources

import gnd

_HOLDER = tempfile.TemporaryDirectory(prefix="gnd-public-payload-alias-")
REPO_ROOT = Path(_HOLDER.name).resolve()
(REPO_ROOT / "src").mkdir()
(REPO_ROOT / "src/gnd").symlink_to(Path(gnd.__file__).resolve().parent, target_is_directory=True)
atexit.register(_HOLDER.cleanup)

def test_the_payload_version_alias_sites_are_the_declared_compat_defaults() -> None:
    """P3-PIN-2 as re-scoped by the adversarial review (finding 2): the alias
    is no longer a gate that accepts exactly one version anywhere the CLI
    wires -- both consumers derive the expected version from the model -- but
    it deliberately REMAINS the default for direct API callers so every
    pre-derivation call site keeps its bytes. This pin enumerates the sites so
    a new alias consumer cannot arrive unnoticed."""

    import re

    sites: dict[str, int] = {}
    for relpath in (
        "src/gnd/coverage.py",
        "src/gnd/exp/session_eval.py",
        "src/gnd/exp/session.py",
        "src/gnd/exp/session_store.py",
    ):
        text = (REPO_ROOT / relpath).read_text(encoding="utf-8")
        sites[relpath] = len(re.findall(r"\bPAYLOAD_SCHEMA_VERSION\b", text))
    assert sites == {
        # import + read_json_document default + read_evidence_document
        # default + _index_transition default
        "src/gnd/coverage.py": 4,
        # import + validate_verifier_payload default
        "src/gnd/exp/session_eval.py": 2,
        # import + the expected_version() fallback for unmapped cases
        "src/gnd/exp/session.py": 2,
        # import + the replay fallback for an absent version map
        "src/gnd/exp/session_store.py": 2,
    }

    # And the CLI paths thread MODEL-derived versions, not the alias.
    cli_text = cli_sources()
    assert "case_payload_versions(contract, root)" in cli_text
    coverage_text = (REPO_ROOT / "src/gnd/coverage.py").read_text(encoding="utf-8")
    assert "payload_schema_version(model)" in coverage_text
