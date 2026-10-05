"""Strict source-anchor interchange and bounded lexical matching."""

from __future__ import annotations

from gnd.anchors import DATE as _DATE  # noqa: F401 -- compatibility export
from gnd.anchors import DECIMAL as _DECIMAL  # noqa: F401 -- compatibility export
from gnd.anchors import HEX as _HEX  # noqa: F401 -- compatibility export
from gnd.anchors import INTEGER as _INTEGER  # noqa: F401 -- compatibility export
from gnd.anchors import (
    MAX_DOCUMENT_BYTES,  # noqa: F401 -- compatibility export
    MAX_SIDECAR_BYTES,  # noqa: F401 -- compatibility export
    AnchorError,  # noqa: F401 -- compatibility export
    AnchorSidecar,  # noqa: F401 -- compatibility export
    bind_anchors,  # noqa: F401 -- compatibility export
    canonical_document_text,  # noqa: F401 -- compatibility export
    lexical_ranges,  # noqa: F401 -- compatibility export
    parse_anchor_sidecar,  # noqa: F401 -- compatibility export
    read_anchor_sidecar,  # noqa: F401 -- compatibility export
    read_regular_path,  # noqa: F401 -- compatibility export
    recognised_ranges,  # noqa: F401 -- compatibility export
    recognition_index,  # noqa: F401 -- compatibility export
    recognition_target,  # noqa: F401 -- compatibility export
    validate_anchor_sidecar,  # noqa: F401 -- compatibility export
    vocabulary_digest,  # noqa: F401 -- compatibility export
    write_anchor_sidecar,  # noqa: F401 -- compatibility export
)
from gnd.anchors import NUMBER as _NUMBER  # noqa: F401 -- compatibility export
from gnd.anchors import NUMERIC_TOKEN as _NUMERIC_TOKEN  # noqa: F401 -- compatibility export
from gnd.anchors import canonical as _canonical  # noqa: F401 -- compatibility export
from gnd.anchors import digest as _digest  # noqa: F401 -- compatibility export
from gnd.anchors import exact_keys as _exact_keys  # noqa: F401 -- compatibility export
from gnd.anchors import pairs as _pairs  # noqa: F401 -- compatibility export
from gnd.anchors import parse as _parse  # noqa: F401 -- compatibility export
from gnd.anchors import (
    reject_constant as _reject_constant,  # noqa: F401 -- compatibility export
)
from gnd.anchors import scalar as _scalar  # noqa: F401 -- compatibility export
from gnd.anchors import word as _word  # noqa: F401 -- compatibility export
