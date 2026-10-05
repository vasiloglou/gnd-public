"""README and packaged fallback expose the same six original limits."""
from __future__ import annotations

import re

import pytest
from test_public_packaged_invocation_guards import CAPABILITY_LIMITS, README


@pytest.mark.parametrize('limitation', sorted(CAPABILITY_LIMITS))
def test_the_user_facing_limitation_list_matches_the_script(limitation: str) -> None:
    """``README.md`` restates the fallback's limits for readers who never open the
    script. Two copies of one list is the drift shape this project guards
    mechanically everywhere else (``tests/test_schema_sync.py`` for the schemas),
    so the same regexes run against both. A README that understates the limits is
    worse than the script doing it: it is the copy a user actually reads.
    """
    readme = README.read_bytes()
    assert re.search(CAPABILITY_LIMITS[limitation], readme, re.IGNORECASE), f"README.md's zero-install fallback section does not name the limitation {limitation!r}, which the script's own capability statement does. The two lists must agree item for item — six limitations, no fewer (D-14). Repair: add it to README.md rather than removing it from the script."
