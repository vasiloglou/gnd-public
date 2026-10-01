"""The conformance lane: does the generated code still agree with the model?

**This package emits the THIRD claim family, and it never blends (G-15, D-01).**
GND now publishes exactly three kinds of payload and no output carries two:

======================  ==========================================  ================================
family                  what it says                                who emits it
======================  ==========================================  ================================
verdicts                one population satisfied / violated a       ``gnd check``, ``gnd verify``
                        constraint; a band; ``acceptance_ready``    (``report.schema.json``)
rates                   a numerator over a denominator, per row     ``gnd fidelity``, ``gnd measure``
                        (``fidelity`` / ``measurement`` schemas)
**conformance**         **which FILES exist, what they hash to,     **``gnd conformance``**
                        and where the code and the model have       (``conformance.schema.json``)
                        drifted apart**
======================  ==========================================  ================================

So nothing in this package produces a verdict, a band-4 lattice value, an
``acceptance_ready`` claim or a rate, and ``conformance.schema.json`` has no
place to put one. ``report.py``'s builders are ``CheckReport``-typed and were
deliberately NOT generalized to carry this: feeding conformance through the
verdict payload would mean widening ``CheckReport`` with codegen fields, which
is D-01's blending error arriving inside a data structure (RESEARCH §5). The
new schema is likewise never added to ``tests/test_schema_sync.py::SCHEMA_PAIRS``
— it has no canonical twin in ``gnd-orm-core``, and that file's docstring
forbids the "fix".

**What conformance checks, and — louder — what it does not (G-08).**

Four assertions ship:

#. **Integrity** — every DERIVED file's bytes still hash to what the manifest
   recorded (:mod:`gnd.conformance.integrity`).
#. **Currency** — the manifest's model digest equals the model's digest right
   now. This one IS model-code drift: the model moved and the code did not
   (:mod:`gnd.conformance.currency`).
#. **Structural** — the emitted surface still names the MODEL's fact types,
   computed from the model and the filesystem and from neither the manifest nor
   a previous generation (:mod:`gnd.conformance.structural`, plan 03-06).
#. **Architecture** — the authored architecture contract's declared modules,
   symbols, artifacts and entry points agree with static filesystem and AST
   observations, without importing or executing project code
   (:mod:`gnd.conformance.architecture`).

Assertions #1 and #2 are EXACT and CORROBORATING and cheap — and both are
SELF-REFERENTIAL: each compares the generator's output against a digest the
generator wrote, so both are green on a project that is 100% derived and 0%
useful. #3 is the anti-tautology gate, and it is the reason a green conformance
result means anything at all.

A green result from #1 and #2 is a narrower claim than it looks. It says the
derived surface is unedited and current. Extension bytes are never
integrity-digest-gated, because human- and LLM-authored text is not
byte-reproducible (G-05). Assertion #4 may still statically inspect an explicitly
declared extension contract or source; that observation is not a digest claim.

That limit does not live in prose. Every file the manifest records is reported
in exactly one of two lists — ``examined`` or ``unexamined`` — and
``unexamined`` is schema-REQUIRED with ``minItems: 0``, so it is
present-and-empty rather than absent when nothing was skipped. An absent list is
a defect: a reader cannot tell "nothing was skipped" from "the skipping was not
reported". :data:`gnd.codegen.manifest.INTEGRITY_LIMITS` — published as data by
plan 03-04 for exactly this — travels into the payload's ``limits`` block rather
than being paraphrased here.

**The tree under inspection is user-controlled and possibly hostile
(T-03-24/25/28).** Conformance NEVER imports the generated project; importing a
module to inspect it would execute arbitrary user code on every CI run. It reads
bytes and hashes them, re-applies the manifest's lexical path rule before any
file is opened rather than trusting that the reader already did, opens with
``lstat`` so a planted symlink is never followed, and reports an oversized
occupant from its stat rather than hashing it.

**Offline, and covered by scan 5.** ``src/gnd/conformance/`` joined
``GENERATION_LANE_ROOTS`` in
``tests/test_measure_offline.py::test_no_network_library_is_reachable_from_the_generation_lane``
in the commit that created this package — the posture ``src/gnd/codegen/`` took
at plan 03-03. Scan 5 is a closure walk over source, not a convention, and it
is separately named rather than a re-scoping of scans 1-4 (G-3). A conformance
result is only worth something if a reviewer can reproduce it from the
repository, which a network call anywhere in this closure would end.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

__all__ = [
    "UNEXAMINED_REASON",
    "ConformanceError",
    "ConformanceResult",
    "ExaminedFile",
    "Finding",
    "FindingKind",
    "UnexaminedFile",
]

#: The finding vocabulary, as module-level DATA and a CLOSED ``Literal`` — the
#: ``Ownership`` / ``FileStateName`` discipline, one lane over.
#:
#: Exactly the kinds the shipped assertions emit, and no more. Plan 03-06 added
#: the structural kinds in the same commit as the check that produces them;
#: declaring them ahead of the emission would have been worse than useless,
#: because an unreachable member is indistinguishable from an unimplemented
#: check and reads as coverage that does not exist.
#: ``tests/test_conformance_drift.py`` asserts every member appears as a literal
#: in an assertion module, so the extension point cannot be taken without the
#: emission arriving with it.
FindingKind = Literal[
    # assertion #1 — the recorded bytes and the actual bytes disagree, or the
    # occupant is not a regular file that can be hashed at all.
    "derived-file-modified",
    # assertion #1 — the manifest records the file and the filesystem does not.
    "derived-file-missing",
    # assertion #2 — the manifest's model digest and the model's own disagree.
    # THIS is model-code drift: the model moved and the code did not.
    "model-digest-mismatch",
    # assertion #3 — the model declares a fact type and nothing in the tree
    # defines its tool. THE anti-tautology catch: a generator emitting
    # well-formed nothing produces one of these per fact type and satisfies
    # assertions #1 and #2 completely.
    "fact-type-unimplemented",
    # assertion #3 — the tool exists and its parameters are not the fact type's
    # role names in declared order.
    "tool-signature-mismatch",
    # assertion #3 — a module-level def in the derived tool module that no model
    # fact type names. Paired with `fact-type-unimplemented` on a consistent
    # rename, and the pair is what proves the assertion read the model and the
    # filesystem independently.
    "orphan-tool-symbol",
    # assertion #3 — the fact type IS covered, but only by a file GND did not
    # emit. Reported rather than forbidden (G-08).
    "fact-type-satisfied-by-non-derived",
    # assertion #3 — a constructor exists for a fact type whose structured
    # derivation rule means the MODEL computes its facts (v5.0 Phase 3,
    # D-P3.5). A stale un-regenerated project reds at model-digest-mismatch
    # first; this kind catches the constructor somebody wrote back, in any
    # file of any ownership.
    "derived-fact-type-constructed",
    # assertion #3 — the model cannot be mapped to a distinct Python surface at
    # all (two ids sanitizing to one symbol), so no expectation exists to check.
    "identifier-hazard",
    # assertion #3 — a source file that could not be parsed, stat'ed or read.
    # A finding rather than a crash: one broken file must not deny the answer
    # for every other fact type.
    "unparseable-source",
    # assertion #4 -- the authored architecture declaration and statically
    # observed project tree disagree, or the declaration cannot be evaluated.
    "contract-unreadable",
    "contract-missing",
    "declared-module-missing",
    "declared-symbol-missing",
    "symbol-shape-mismatch",
    "declared-artifact-missing",
    "artifact-path-mismatch",
    "artifact-reference-unfound",
    "entry-point-module-missing",
    "entry-point-flag-unfound",
    "contract-fact-type-unknown",
]

#: Why an extension file is never digest-gated, as one published string rather
#: than a message assembled at each site. It travels into the payload verbatim,
#: so a reader confirms the scope from the JSON rather than from this docstring.
UNEXAMINED_REASON = (
    "extension files are user- or LLM-authored and therefore not "
    "byte-reproducible (G-05); integrity has no record to compare them "
    "against and does not digest-gate them, while a separate conformance "
    "assertion may statically inspect an explicitly declared extension"
)


class ConformanceError(Exception):
    """Conformance could not be performed at all — an unreadable model, or a
    manifest naming a path the lexical rule refuses.

    Loud and fail-closed, and deliberately NOT a finding: a finding is a
    statement about the project, and this is a statement that no such statement
    could be made. Reporting "no drift" over a check that never ran is the one
    outcome G-08 exists to prevent.
    """


@dataclass(frozen=True)
class Finding:
    """One thing conformance found, with the evidence attached.

    ``recorded_sha256`` / ``actual_sha256`` are the PAIR, and carrying both is
    load-bearing rather than decorative: a finding saying only "the model
    changed" cannot be distinguished by a reader from one that guessed, and
    G-09's mutation #2 asserts the pair is shown.

    ``actual_sha256`` is ``None`` exactly when the bytes could not be hashed —
    the file is absent, is not a regular file, or is over the byte cap — and
    ``message`` then says which. It is never a sentinel digest.
    """

    kind: FindingKind
    target: str
    message: str
    recorded_sha256: str | None = None
    actual_sha256: str | None = None


@dataclass(frozen=True)
class ExaminedFile:
    """A file conformance actually digest-gated, and what it found."""

    relpath: str
    recorded_sha256: str
    actual_sha256: str | None


@dataclass(frozen=True)
class UnexaminedFile:
    """A file conformance deliberately did not check, and why (G-08)."""

    relpath: str
    ownership: str
    reason: str


@dataclass(frozen=True)
class ConformanceResult:
    """Findings, plus the PARTITION that gives them their honest scope.

    ``examined`` and ``unexamined`` together cover every file the manifest
    records, exactly once each. That is asserted structurally by
    ``tests/test_conformance_drift.py`` rather than merely intended, because a
    file that fell out of both lists would take its own unexaminedness with it —
    and a green report over a silently-dropped file is the exact failure G-08
    names.
    """

    findings: tuple[Finding, ...] = ()
    examined: tuple[ExaminedFile, ...] = field(default=())
    unexamined: tuple[UnexaminedFile, ...] = field(default=())
