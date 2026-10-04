"""Public generation scan roots retain the original package coverage guard."""
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PHASE_PACKAGES = ("exp", "codegen", "conformance")


def test_every_package_this_phase_created_is_covered_by_the_generation_lane_scan():
    """Three packages landed across three plans; a root nobody appended is silent.

    `test_measure_offline.py`'s scan 5 walks the transitive import closure of
    `GENERATION_LANE_ROOTS`. Scans 1-4 are scoped to the measure, provider and
    extraction/fidelity lanes, so a network import inside `src/gnd/exp/`,
    `src/gnd/codegen/` or `src/gnd/conformance/` is caught by NONE of them
    unless that package's root is in the tuple.

    Each package added its own root in the commit that created it, and each
    plan's mutation confirmed it — but the three claims lived in three modules.
    Asserted together here, as the closing plan's meta-check, so a fourth
    package added by a later phase without a root is a visible omission rather
    than an invisible one.
    """
    from test_measure_offline import GENERATION_LANE_ROOTS

    roots = {Path(root).name for root in GENERATION_LANE_ROOTS}
    missing = set(PHASE_PACKAGES) - roots
    assert not missing, (
        f"{sorted(missing)} are not in GENERATION_LANE_ROOTS, so a network "
        f"import in them would be caught by no offline scan at all"
    )
    for package in PHASE_PACKAGES:
        assert (REPO_ROOT / "src" / "gnd" / package).is_dir(), (
            f"src/gnd/{package}/ does not exist, so the assertion above passed "
            f"over a root naming nothing"
        )

