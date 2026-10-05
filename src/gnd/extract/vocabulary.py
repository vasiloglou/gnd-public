"""The constraint-blind model verbalization — the rendering seed (R-08″).

``render_verbalization`` is constraint-blind BY CONSTRUCTION, not by review:
the builder reads ONLY ``object_types[]`` (id, name, kind, ``reference``,
``subtype_of``, ``inherits_reference``), ``fact_types[]`` (id, ``reading``,
``roles``), primitive shapes via ``popvalidate.resolve_primitive``, and —
solely for the external-mode identification phrase — the composite identity
:func:`gnd.extract.refscheme.reference_identity` derives from top-level
external ``uniqueness`` constraints' ``role_refs``. No other constraint access
exists anywhere in this module: no constraint sentences, no modality words, no
provenance prefixes. The panel's reason is Codex's finding that constraint
verbalizations bias the extractor toward REPAIRING violations — a document
seed that recites "each employee has exactly one salary" teaches the extractor
to emit the population the checker wants rather than the one the document
contains. ``tests/test_extract_vocabulary.py::test_vocabulary_is_constraint_blind``
pins this as byte-identity under constraint injection.

The header is a THIRD header form — mechanical derivation by ``gnd extract`` —
not the CSDP header (which claims a dialogue that never happened) and not the
Phase-4 introspection header ``verbalization-patterns.md:51`` reserves; that
reservation is the precedent for adding a derivation-flavoured form.

Sentence patterns follow ``verbalization-patterns.md`` (object-type modes at
:55-117, the external/composite phrase at :81-89). ``verbalize.py``'s ~55
``*_message`` functions are violation-voice and deliberately NOT imported —
only the neutralization boundary (``_neutralize``/``line_text``) is reused,
because model text (names, readings, units) includes user-supplied fields and
must not forge lines or escape quotes (T-02.1-06).
"""

from __future__ import annotations

from gnd.refscheme import reference_identity  # noqa: F401 -- compatibility export
from gnd.universe import resolve_primitive  # noqa: F401 -- compatibility export
from gnd.vocabulary import PLACEHOLDER as _PLACEHOLDER  # noqa: F401 -- compatibility export
from gnd.vocabulary import (
    __all__,  # noqa: F401 -- compatibility export
    reading_text,  # noqa: F401 -- compatibility export
    render_verbalization,  # noqa: F401 -- compatibility export
)
from gnd.vocabulary import display as _display  # noqa: F401 -- compatibility export
from gnd.vocabulary import (
    object_type_sentence as _object_type_sentence,  # noqa: F401 -- compatibility export
)


#: ``{Employee}`` and ``{Employee:manager}`` reading placeholders.


