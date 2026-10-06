"""The conformance payload: files, digests, drift — and the scope, as a fact.

Four module contracts, re-aimed from ``fidelity/report.py:1-35`` at this lane.

**Raw evidence, always.** Every finding names its subject and carries the digest
pair it was derived from, and every file the manifest records appears in
``examined`` or ``unexamined`` with its digests or its reason. A reader can
re-derive the whole result with ``shasum -a 256`` and the committed manifest;
nothing here has to be taken on trust.

**No timestamp, byte-reproducible.** Sorted keys, pre-sorted lists, no
``generated_at``. Two ``gnd conformance`` runs over one unchanged project are
byte-identical, which is what makes a recorded conformance result something a
reviewer can reproduce from the repository rather than something they can only
believe.

**No blending of claim families (G-15, D-01).** This is GND's third payload
family. ``gnd check``/``gnd verify`` emit verdicts, ``gnd fidelity``/``gnd
measure`` emit rates, and this emits files-digests-drift — and no output carries
two. Concretely: nothing here is a verdict, a band, an ``acceptance_ready``
claim or a rate, ``conformance.schema.json`` closes every object so none can be
added by accident, and ``report.py`` was deliberately NOT extended to carry
this. Its builders are ``CheckReport``-typed and its stated invariant is that
every field serializes FROM a ``CheckReport``; feeding conformance through it
would mean widening ``CheckReport`` with codegen fields, which is D-01's
blending error arriving inside a data structure (RESEARCH §5). ``report.py``'s
``PAYLOAD_SCHEMA_VERSION`` is untouched by this plan and its ``command`` enum
gains no member.

**And the honest scope is a SCHEMA fact, not prose (G-08, R-13′).**
``unexamined`` is schema-required with ``minItems: 0`` — present-and-empty
rather than absent — and ``limits`` is a required block whose three permanent
members cannot be removed. The reason this is machinery rather than a comment
is that the payload is what a CI job branches on: a green conformance result
will be read as "the generated project is fine", and the only defence against
that misreading is a payload that says, in the same breath and in a field the
consumer must parse, exactly which files it never looked at.
"""

from __future__ import annotations

import json  # noqa: F401 -- historical compatibility binding
from collections.abc import Mapping, Sequence
from importlib.resources import files
from pathlib import Path
from typing import Any

from gnd import input_policy as _rf7_input
from gnd import verbalize
from gnd.artifacts import canonical_report_text as canonical
from gnd.codegen.manifest import INTEGRITY_LIMITS, CodegenManifest
from gnd.conformance import UNEXAMINED_REASON, ConformanceResult, Finding
from gnd.conformance.architecture import ArchitectureResult
from gnd.conformance.structural import StructuralResult

__all__ = [
    "CONFORMANCE_SCHEMA_VERSION",
    "LIMITS",
    "build_conformance_payload",
    "canonical",
    "load_conformance_schema",
    "render_conformance",
]

#: Conformance payload key-set version. Bump ONLY on a breaking change to the
#: key set or to a value's MEANING — never for an additive field, a new
#: ``assertions`` member, or a new ``findings`` kind, all three of which this
#: payload was shaped to absorb (``report.py``'s ``PAYLOAD_SCHEMA_VERSION``,
#: ``fidelity/report.py``'s ``FIDELITY_SCHEMA_VERSION`` and ``measure/report``'s
#: ``MEASUREMENT_SCHEMA_VERSION`` carry the identical rule).
#:
#: /1: the initial contract (plan 03-05) — assertions #1 (integrity) and #2
#: (currency), the G-08 examined/unexamined partition, and the R-13′ ``limits``
#: block.
#:
#: /1, widened by plan 03-06 with assertion #3 and NO BUMP. What arrived: the
#: ``structural`` member of ``assertions`` (now ``contains``-required), six new
#: ``findings`` kinds, the required ``satisfied`` array carrying which FILE
#: satisfied each model fact type and who owns it, the required
#: ``model.fact_types`` count that array reconciles against, the
#: ``structural-surface-only`` limit, and the REMOVAL of the non-required
#: ``structural-conformance-deferred`` limit whose gap the assertion closes.
#:
#: The disposition, stated once so it is not re-decided: **no bump.** The bump
#: rule above exists for a breaking change to a PUBLISHED key set, and this key
#: set was introduced two plans ago inside the same unreleased phase and has
#: never shipped in a release, so there is no consumer pinned to the narrower
#: shape. ``tests/test_conformance_payload.py`` was written at 03-05 to survive
#: exactly this widening and stayed green through it without relaxation, which
#: is the evidence for the disposition rather than an assurance about it — had it
#: red, the change would have been breaking after all and the number would have
#: moved instead of the test.
CONFORMANCE_SCHEMA_VERSION = 1

#: What a GREEN result does not say, as module-level DATA (R-13′).
#:
#: The first three descriptions are :data:`gnd.codegen.manifest.INTEGRITY_LIMITS`
#: VERBATIM rather than paraphrased. Plan 03-04 published that tuple as
#: importable data for exactly this hand-off, and a paraphrase is where a limit
#: quietly softens: "a manifest cannot record its own digest" becomes "some
#: edits may not be detected" becomes nothing at all, in three commits by three
#: people who each thought they were only tightening the prose.
#:
#: The five ids ``manifest-co-edit``, ``extension-unexamined``,
#: ``green-is-not-correctness``, ``structural-surface-only`` and
#: ``architecture-static-only`` are
#: schema-REQUIRED members and cannot be dropped: none of them can ever be
#: closed by more checking.
#:
#: ``structural-conformance-deferred`` USED to sit here and is gone. Plan 03-05
#: emitted it as the one non-required member precisely because it named a gap a
#: named plan would close, and plan 03-06 closed it — a published limit that no
#: longer holds is a false statement about the check's own scope, which is worse
#: than an unpublished one. The rule that made the removal safe is one clause
#: long: **a limit that never closes is contains-required; a limit a named plan
#: will close is emitted but not required.**
LIMITS: tuple[dict[str, str], ...] = (
    {"id": "manifest-co-edit", "description": INTEGRITY_LIMITS[0]},
    {"id": "extension-unexamined", "description": UNEXAMINED_REASON},
    {"id": "green-is-not-correctness", "description": INTEGRITY_LIMITS[2]},
    {
        "id": "structural-surface-only",
        # No apostrophe anywhere in this string, deliberately. `render_conformance`
        # neutralizes every value through `verbalize.path_segment`, which escapes
        # apostrophes — correct as a uniform default for untrusted strings, and
        # pure noise over GND's own constants, where it prints `the model\'s`.
        # Plan 05 hit this on `structural-conformance-deferred` and fixed it the
        # same way, because a renderer with a trusted/untrusted branch is one
        # refactor away from applying the wrong branch to a hostile string.
        "description": (
            "assertion #3 binds the NAMES and SIGNATURES of the emitted tools to "
            "the fact types and role names that the model declares; it does not "
            "read a function body. A tool whose name and parameters agree with "
            "the model may still compute the wrong thing, and the only check "
            "that catches that is the runtime verifier over the population the "
            "generated agent actually produces"
        ),
    },
    {
        "id": "architecture-static-only",
        "description": (
            "assertion #4 checks declared paths, module-level positional shape, "
            "fact-type membership, recognized path expressions and whole-AST "
            "flag or subcommand string presence without executing project code; "
            "string presence does not prove argparse wiring, declared exits are "
            "unverified without smoke rows, unrecognized expressions and "
            "cross-module indirection are not guessed, computed-only artifact "
            "names can report reference-unfound, dotted entry modules use only "
            "project-root flat module paths, weakening remains visible only in "
            "declared counts and review, pure-existence artifacts arm no path "
            "check, and the two service observations are point-in-time reads "
            "rather than an atomic filesystem snapshot"
        ),
    },
)

ARCHITECTURE_CONTRACT_ABSENT_LIMIT = {
    "id": "architecture-contract-absent",
    "description": (
        "the codegen manifest does not list an architecture contract and no "
        "contract leaf exists, so assertion #4 has no declarations to inspect"
    ),
}


def load_conformance_schema() -> dict[str, Any]:
    """The Draft 2020-12 schema describing this payload, resolved through
    ``importlib.resources`` so the contract ships with the INSTALLED package
    (the ``report`` / ``measurement`` / ``fidelity`` schema precedent — a
    source-tree read passes while the resource is missing from the wheel).

    Vendored-only at the package root: it describes a runtime OUTPUT contract of
    the ``gnd`` CLI, not an interchange format the gnd-orm-core skill documents
    authoring rules for, so it has no canonical twin and stays out of
    ``SCHEMA_PAIRS`` (``tests/test_schema_sync.py:9-18``).
    """
    schema_text = (
        files("gnd").joinpath("conformance.schema.json").read_text(encoding="utf-8")
    )
    return _rf7_input.loads(schema_text)




def _finding_entry(finding: Finding) -> dict[str, Any]:
    return {
        "kind": finding.kind,
        "target": finding.target,
        "message": finding.message,
        "recorded_sha256": finding.recorded_sha256,
        "actual_sha256": finding.actual_sha256,
    }


def build_conformance_payload(
    model_path: str | Path,
    manifest: CodegenManifest | None,
    integrity: ConformanceResult | None,
    currency: Sequence[Finding] | None,
    *,
    structural: StructuralResult | None = None,
    architecture: ArchitectureResult | None = None,
    actual_model_sha256: str | None,
    gnd_version: str,
    error: str | None = None,
) -> dict[str, Any]:
    """Assemble the conformance payload.

    ``manifest``, ``integrity``, ``currency`` and ``structural`` are each
    ``None`` when the corresponding assertion could not be performed — an absent
    or unparseable codegen manifest, an unreadable model, a model that will not
    LOAD. That case is reported as ``ran: false`` with an ``error``, and NEVER as
    an assertion with zero findings: a check that could not run must not be
    indistinguishable from a check that passed (R-13′). This is the same rule the
    fidelity census applies to a case that failed to load, one lane over.

    ``structural`` is KEYWORD-ONLY with a ``None`` default while the other three
    are positional. Two reasons, and neither is style. Plan 05's payload guard
    calls this builder positionally with four arguments to prove the
    could-not-run path is representable; a fifth positional would have broken
    that call and the widening would have been paid for by editing the test that
    exists to catch widenings. And the default is safe in the one direction that
    matters — a caller who forgets it gets ``ran: false``, which fails closed and
    is loudly visible in the payload, rather than an assertion that silently
    reports zero findings. (The four-``None``-able-argument shape is a smell plan
    05 recorded rather than defended; it is now five, and the honest note is that
    a ``ConformanceRun`` record would be a class whose only behaviour is to be
    unpacked, so the smell is still the better of the two.)

    Emits no timestamp and pre-sorted lists so two runs reproduce byte-for-byte.
    """
    integrity_findings = list(integrity.findings) if integrity is not None else []
    currency_findings = list(currency) if currency is not None else []
    structural_findings = list(structural.findings) if structural is not None else []
    architecture_findings = list(architecture.findings) if architecture is not None else []

    examined = sorted(
        (
            {
                "relpath": entry.relpath,
                "recorded_sha256": entry.recorded_sha256,
                "actual_sha256": entry.actual_sha256,
            }
            for entry in (integrity.examined if integrity is not None else ())
        ),
        key=lambda entry: entry["relpath"],
    )
    unexamined = sorted(
        (
            {
                "relpath": entry.relpath,
                "ownership": entry.ownership,
                "reason": entry.reason,
            }
            for entry in (integrity.unexamined if integrity is not None else ())
        ),
        key=lambda entry: entry["relpath"],
    )

    satisfied = sorted(
        (
            {
                "fact_type_id": entry.fact_type_id,
                "symbol": entry.symbol,
                "relpath": entry.relpath,
                "ownership": entry.ownership,
            }
            for entry in (structural.satisfied if structural is not None else ())
        ),
        key=lambda entry: entry["fact_type_id"],
    )

    findings = sorted(
        (
            _finding_entry(finding)
            for finding in [
                *integrity_findings,
                *currency_findings,
                *structural_findings,
                *architecture_findings,
            ]
        ),
        key=lambda entry: (entry["kind"], entry["target"]),
    )

    return {
        "schema_version": CONFORMANCE_SCHEMA_VERSION,
        "tool": "gnd",
        "command": "conformance",
        "gnd_version": gnd_version,
        "model": {
            # The file NAME, never the path: the payload names the model
            # without naming the machine it ran on, and the digests below are
            # the authoritative identity (`stable_model_identifier`'s rule,
            # reached without a third copy of that function — the model here is
            # a caller-named argv path, not a corpus member).
            "id": Path(model_path).name,
            "recorded_sha256": manifest.model.sha256 if manifest is not None else None,
            "actual_sha256": actual_model_sha256,
            # Assertion #3's denominator: the fact types it formed an
            # EXPECTATION for. Equal to the declared count except where an
            # `identifier-hazard` finding names a fact type that could not be
            # mapped to a Python surface at all — and that exception is why the
            # count is taken from the expectation rather than from
            # `len(model.fact_types)`: the partition
            # `len(satisfied) + #unimplemented == fact_types` must be exact, and
            # a fact type nothing could expect belongs to neither side of it.
            #
            # Null when the model would not LOAD. A digest is available over
            # bytes that will not parse; a fact-type count is not, and emitting 0
            # there would make an unreadable model look like an empty one.
            "fact_types": len(structural.expected) if structural is not None else None,
        },
        "project": {
            "manifest_version": manifest.manifest_version if manifest is not None else None,
            # The partition's audit trail: len(examined) + len(unexamined) must
            # equal this, checkable by a reader counting the printed arrays.
            "recorded_files": len(manifest.files) if manifest is not None else 0,
        },
        "assertions": [
            {
                "id": "integrity",
                "ran": integrity is not None,
                "findings": len(integrity_findings),
            },
            {
                "id": "currency",
                "ran": currency is not None,
                "findings": len(currency_findings),
            },
            {
                "id": "structural",
                "ran": structural is not None,
                "findings": len(structural_findings),
            },
            {
                "id": "architecture",
                "ran": architecture is not None,
                "findings": len(architecture_findings),
            },
        ],
        "architecture": {
            "contract": (
                {
                    "relpath": architecture.contract.relpath,
                    "sha256": architecture.contract.sha256,
                }
                if architecture is not None and architecture.contract is not None
                else None
            ),
            "declared": (
                {
                    "modules": architecture.declared.modules,
                    "symbols": architecture.declared.symbols,
                    "artifacts": architecture.declared.artifacts,
                    "artifact_requirements": architecture.declared.artifact_requirements,
                    "entry_points": architecture.declared.entry_points,
                    "smoke_rows": architecture.declared.smoke_rows,
                }
                if architecture is not None and architecture.declared is not None
                else None
            ),
            "scanned": list(architecture.scanned) if architecture is not None else [],
        },
        "examined": examined,
        "unexamined": unexamined,
        "satisfied": satisfied,
        "findings": findings,
        "limits": {
            "unchecked": [
                *(dict(limit) for limit in LIMITS),
                *(
                    [dict(ARCHITECTURE_CONTRACT_ABSENT_LIMIT)]
                    if architecture is not None and architecture.contract_absent
                    else []
                ),
            ]
        },
        "error": error,
    }


def render_conformance(payload: Mapping[str, Any]) -> str:
    """The text rendering: findings FIRST, then the scope that bounds them.

    The scope closes the report rather than opening it for the same reason
    ``render_fidelity`` puts the census first and the un-publishability line
    last — a reader who stops after the headline should have read the headline,
    and a reader who reads to the end should be unable to miss what the headline
    did not cover.
    """
    model = payload["model"]
    lines = [
        (
            f"conformance for {verbalize.path_segment(model['id'])} "
            f"({payload['project']['recorded_files']} recorded file(s))"
        )
    ]

    if payload["error"]:
        lines.append(f"ERROR: {verbalize.path_segment(payload['error'])}")

    for assertion in payload["assertions"]:
        state = (
            f"{assertion['findings']} finding(s)"
            if assertion["ran"]
            else "DID NOT RUN — this is not a pass"
        )
        lines.append(f"  {assertion['id']}: {state}")

    architecture = payload["architecture"]
    binding = architecture["contract"]
    declared = architecture["declared"]
    lines.append("")
    if binding is None:
        lines.append("architecture declaration: no readable contract binding")
    else:
        lines.append(
            "architecture declaration: "
            f"{verbalize.path_segment(binding['relpath'])} "
            f"sha256 {verbalize.path_segment(binding['sha256'])}"
        )
    if declared is None:
        lines.append("  declared: unavailable")
    else:
        lines.append(
            "  declared: "
            f"{declared['modules']} module(s), {declared['symbols']} symbol(s), "
            f"{declared['artifacts']} artifact(s), "
            f"{declared['artifact_requirements']} artifact requirement(s), "
            f"{declared['entry_points']} entry point(s), "
            f"{declared['smoke_rows']} smoke row(s)"
        )
    lines.append(
        f"  scanned: {len(architecture['scanned'])} file(s) whose bytes assertion #4 obtained"
    )
    for relpath in architecture["scanned"]:
        lines.append(f"    {verbalize.path_segment(relpath)}")

    lines.append("")
    if payload["findings"]:
        for finding in payload["findings"]:
            lines.append(
                f"DRIFT [{verbalize.path_segment(finding['kind'])}] "
                f"{verbalize.path_segment(finding['target'])}: "
                f"{verbalize.path_segment(finding['message'])}"
            )
    elif not payload["error"]:
        lines.append(
            f"no drift: {len(payload['examined'])} derived file(s) match the "
            f"manifest, the model has not moved since generation, and "
            f"{len(payload['satisfied'])} model fact type(s) are named by the "
            f"emitted surface"
        )

    # Assertion #3's half of the partition, printed only where it is not the
    # uniform answer: a reader scanning a clean report wants the ONE line that
    # says every fact type is covered by derived code, and the exceptions named
    # individually when they are not.
    off_surface = [
        entry for entry in payload["satisfied"] if entry["ownership"] != "derived"
    ]
    if off_surface:
        lines.append("")
        lines.append(
            f"satisfied OUTSIDE the derived surface: {len(off_surface)} fact "
            f"type(s) covered by code GND did not emit"
        )
        for entry in off_surface:
            lines.append(
                f"  {verbalize.path_segment(entry['fact_type_id'])} -> "
                f"{verbalize.path_segment(entry['relpath'])} "
                f"[{verbalize.path_segment(entry['ownership'])}]"
            )

    lines.append("")
    lines.append(
        f"unexamined by integrity: {len(payload['unexamined'])} file(s) not digest-gated"
    )
    for entry in payload["unexamined"]:
        lines.append(
            f"  {verbalize.path_segment(entry['relpath'])} "
            f"[{verbalize.path_segment(entry['ownership'])}] — "
            f"{verbalize.path_segment(entry['reason'])}"
        )

    lines.append("")
    lines.append("limits of a green result:")
    for limit in payload["limits"]["unchecked"]:
        lines.append(
            f"  {verbalize.path_segment(limit['id'])}: "
            f"{verbalize.path_segment(limit['description'])}"
        )
    return "\n".join(lines)
