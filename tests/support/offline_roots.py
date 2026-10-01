"""Current generation lane roots, shared without historical test imports."""
from support.repository import REPO_ROOT

GENERATION_LANE_ROOTS = tuple(REPO_ROOT / "src" / "gnd" / name for name in ("exp", "codegen", "conformance", "evolve"))
