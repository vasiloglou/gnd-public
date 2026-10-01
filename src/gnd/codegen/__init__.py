"""The generation lane: a project emitted FROM a model, one way only.

``gnd codegen MODEL --out DIR`` turns ``model.orm.yaml`` into a plain-Python
project. The direction is one-way and permanent: **the model remains the single
source of truth**, and round-trip engineering — reading user edits back into the
model — is out of scope by name in ``REQUIREMENTS.md`` (line 70), which records
it as MDE's best-documented failure mode. The compatible triple GND ships
instead is *one-way generation + conformance checking + explicit model
evolution*. Nothing in this package may grow a path from emitted code back into
the model.

**What is emitted has the GND shape (G-01), not a provider-calling program.**
Phase 2.1's output is the reference specification: ``gnd extract``'s artifact
bundle plus ``gnd verify`` (the deterministic half) alongside a ``SKILL.md`` the
terminal agent runs (the language half). So "LLM + tools, plain Python"
decomposes as tools = code derived from the model's fact types, LLM = a
generated skill document, verifier = a call into the shipped ``gnd verify``. The
consequence worth stating: a generated project is **CI-runnable with zero
network and no API key**.

**G-02's no-provider-client rule binds THIS package, and the default template
ships none.** D-20/R-04‴ are about ``src/gnd/`` — a user's generated project is
their code, and adding a provider client there is their extension, landing in an
extension file by G-05. But the emitted default template contains no client and
no network import, because a rule read too narrowly ("codegen may emit an SDK
call") would smuggle a provider dependency into GND's own test lane through the
back door.

The guard with the name is **scan 5**,
``tests/test_measure_offline.py::test_no_network_library_is_reachable_from_the_generation_lane``,
whose ``GENERATION_LANE_ROOTS`` this package joined in the commit that created
it. Scan 5 is a closure walk over source, not a convention, and it is
separately named rather than a re-scoping of scans 1-4 (re-scoping an
owner-decided guard without a decision is forbidden, G-3). Scan 5 covers
``src/gnd/``; the EMITTED tree has its own scan in
``tests/test_codegen_emit.py``, because a guard rooted here inherits nothing
about the files this package writes.

Derived means CODE-EMITTED (G-05). Anything an LLM authored is extension by
definition — an LLM-authored file is not byte-reproducible and therefore cannot
be digest-gated, so calling it derived would either false-fail the conformance
check on every regeneration or quietly drop the digest over exactly the files
nobody is watching.
"""

from __future__ import annotations

__all__: list[str] = []
