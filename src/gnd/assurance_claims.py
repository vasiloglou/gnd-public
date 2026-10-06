from __future__ import annotations

from gnd.assurance._wire import (
    closed as _closed,  # noqa: F401 -- compatibility surface
)
from gnd.assurance._wire import (
    strings as _strings,  # noqa: F401 -- compatibility surface
)
from gnd.assurance.claims import (
    INPUT_FIELDS as INPUT_FIELDS,  # noqa: PLC0414 -- compatibility surface
)
from gnd.assurance.claims import (
    OUTPUT_NODES as OUTPUT_NODES,  # noqa: PLC0414 -- compatibility surface
)
from gnd.assurance.claims import (
    RESULT_FIELDS as RESULT_FIELDS,  # noqa: PLC0414 -- compatibility surface
)
from gnd.assurance.claims import (
    validate_claim_graph as validate_claim_graph,  # noqa: PLC0414 -- compatibility surface
)
from gnd.assurance.claims import (
    validate_inputs as _validate_inputs,  # noqa: F401 -- compatibility surface
)

"""RF4 compatibility imports; retirement follows RF-D5."""










from gnd.assurance.claims import (
    PurePosixPath as PurePosixPath,  # noqa: PLC0414 -- historical imported binding
)
