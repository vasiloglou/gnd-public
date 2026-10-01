"""The experiment lane: the structural INVARIANTS of an experiment on disk.

**This lane owns the invariants; a skill owns the language (G-10).** What can be
checked mechanically over ``SPEC.md`` and ``CONCLUSIONS.md`` — is the document
structured, does it parse, does every declared question id resolve, does every
evidence pointer name a file that exists inside the experiment — lives here as
code. What *makes* a good question, a good conclusion, or a well-chosen piece of
evidence is prose, and belongs in a skill. The split is deliberate: a validator
that tried to judge the language would either be unfalsifiable or wrong, and a
skill that tried to enforce the structure would be a convention rather than a
gate.

**Offline by construction.** Nothing here calls a provider or touches the
network. An experiment's recorded conclusion is only worth something if a
reviewer can recompute it from the committed tree, and a live call anywhere in
this lane's import closure would break exactly that.
``tests/test_measure_offline.py::test_no_network_library_is_reachable_from_the_generation_lane``
— scan 5, rooted at ``GENERATION_LANE_ROOTS`` — fails the suite on any
network-library import reachable from this package. It is a closure walk over
source, not a convention, and it is a NEW separately-named scan: scans 1-3 keep
their owner-decided scopes and scan 4's roots are the extraction and fidelity
lanes, so none of them would have seen an import added here (R-04', G-3).

Why a package rather than folding into ``cli.py``: G-15's rule is that no single
output carries two claim families, and a module boundary is the cheapest
structural enforcement of it. The experiment lane makes claims about ARTIFACTS —
is this experiment well-formed, is it closable — while the checker lane makes
verdicts about populations. Keeping them in one file would make the separation a
matter of discipline rather than of structure.

``SPEC.md`` and ``CONCLUSIONS.md`` are UNTRUSTED committed metadata, written by
an agent or a human and parsed by GND. This lane therefore adopts
``gnd.extract.manifest``'s posture verbatim: byte-capped reads applied before
the bytes are loaded, ``extra="forbid"`` closed records, closed ``Literal``
vocabularies, non-empty string constraints, the safe YAML loader only, and
failures that raise loudly carrying :class:`~gnd.model.ValidationIssue` records
so the CLI maps them to exit bands without re-deriving messages.
"""

from __future__ import annotations

__all__: list[str] = []
