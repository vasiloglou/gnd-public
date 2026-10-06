"""The close gate — a two-set difference plus pointer resolvability (plan 03-02).

``gnd exp close`` answers one question: **has this experiment discharged what it
declared?** It is a VALIDATOR that returns an exit code, not a state machine
(G-11). There are no transitions, no locks and no status registry here, because
REQUIREMENTS.md draws the GND/GSD boundary around exactly that: GSD's phase-
workflow engine is not adopted, and an experiment lifecycle with states would be
that engine arriving under a new name. What ships is a directory convention and a
non-zero exit.

The verdict, mechanically (RESEARCH §6.4):

- ``declared`` = the question ids in ``SPEC.md``
- ``resolved``  = the resolution ids in ``CONCLUSIONS.md``
- FAIL iff ``declared - resolved != empty`` (a question the experiment forgot),
  or ``resolved - declared != empty`` (an ORPHAN — an answer to a question
  nobody asked), or a resolution's evidence pointer will not resolve to a file
  inside the experiment, or a ``follows:`` reference names an experiment that
  does not exist or has not concluded.
- Plus, for the kinds whose row in ``KIND_POLICY`` says so, the obligations
  that are about the experiment's DELIVERABLE rather than its conclusions:
  conformance for ``codegen`` (see :func:`_conformance_findings`), and a
  recorded launch whose latest run accepted for ``work`` (O-18, see
  :func:`_work_findings`).
- **PASS otherwise, REGARDLESS of the outcome VALUES.**

That last line is the whole design and the thing most likely to be built
backwards, so it is worth being explicit about what it costs and buys.

    Every instinct says a gate should require a good outcome. This one must not.
    A gate that demanded success would pay for lying: the cheapest way through it
    would be to write ``answered`` over a question nobody investigated. It would
    also reproduce, on GND's own process layer, precisely the error every prior
    phase of this project has been correcting — an artifact reporting a state
    nobody established. An experiment whose every question honestly resolves to
    ``unanswered`` with a reason and a citation is a GOOD experiment and closes
    at exit 0.

    A backwards implementation looks STRICTER and passes careless review, which
    is why the asymmetry has its own named test module
    (``tests/test_exp_asymmetry.py``) and its own recorded mutation.

The gate therefore reads ``outcome`` **never** — not once in this module. The one
rule that depends on the outcome value (a non-answer must carry a reason) is
discharged in :class:`~gnd.exp.conclusions.Resolution`'s own validator, at load,
before this module sees the document at all.

**The G-17 seam is FILLED (plan 03-06).** A codegen experiment is refused when
model-code conformance did not pass. Plan 02 left the branch out rather than
defaulting it to a passing value, and warned that a parameter like
``conformance_passed: bool = True`` would be a gate that cannot fail for the case
it exists for — a class this project's defect history names roughly fourteen
times.

What shipped is stronger than the parameter that was pre-declared: there is **no
conformance parameter at all**. :func:`evaluate_close` resolves and validates the
recorded payload itself, from the experiment directory it already has, so the
gate is not something a caller can be trusted to supply, forget, or fabricate.
The pre-declaration asked for a parameter without a default so every call site
would be forced to say what it knows; removing the parameter removes the class of
call site that could say the wrong thing. See :func:`_conformance_findings` for
the pass rule and for why an ABSENT result is a failure rather than a default.

**This is not a demand for a good outcome, and the distinction is worth being
explicit about**, because it sits one paragraph below the asymmetry above and
reads at a glance like its opposite. G-12 forbids the gate to require that an
experiment's questions resolved *well*; an all-``unanswered`` codegen experiment
with clean conformance still closes at exit 0, and nothing here reads
``outcome``. What the codegen branch requires is that the ARTIFACT the experiment
produced is not internally broken — that the generated project still agrees with
the model it claims to have been generated from. An experiment may honestly
conclude "this approach did not work"; it may not conclude anything at all on top
of a generated tree that has silently drifted from its own model, because every
claim it recorded was measured against a project that no longer exists in the
form the record describes.
"""

from __future__ import annotations

import json  # noqa: F401 -- historical compatibility binding
import os
import re
import stat
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

from gnd import input_policy as _rf7_input
from gnd.exp.conclusions import ExperimentConclusions
from gnd.exp.paths import (
    EvidencePathError,
    resolve_evidence_path,
    resolve_experiment_directory,
)
from gnd.exp.spec import (
    CLOSE_OBLIGATIONS,
    EXPERIMENT_DIR_PATTERN,
    KIND_POLICY,
    ExperimentSpec,
)

__all__ = [
    "CLOSE_OBLIGATIONS",
    "CONCLUSIONS_FILENAME",
    "CONFORMANCE_EVIDENCE",
    "MAX_SESSION_RUN_INDEX",
    "MIN_SESSION_RUN_INDEX",
    "SESSION_LAUNCHES_DIRNAME",
    "SESSION_RESULT_FILENAME",
    "SESSION_RUNS_DIRNAME",
    "SESSION_RUN_CLAIM_PATTERN",
    "SESSION_RUN_PATTERN",
    "CloseFinding",
    "CloseFindingKind",
    "CloseResult",
    "close_outcome",
    "evaluate_close",
]

#: The document whose presence is what "concluded" means on disk. Named once so
#: the gate and the ``follows:`` check cannot disagree about it.
CONCLUSIONS_FILENAME = "CONCLUSIONS.md"

#: Where a codegen experiment records its conformance result, by CONVENTION —
#: one relpath inside the experiment directory, named once here so the gate and
#: the author cannot disagree about where the evidence lives (the
#: :data:`CONCLUSIONS_FILENAME` discipline, one obligation over).
#:
#: The alternative — a ``conformance:`` pointer in ``CONCLUSIONS.md``'s
#: frontmatter — was declined for two reasons. It widens a record that is CLOSED
#: (``extra="forbid"``) precisely to stop fields that look like verdicts from
#: being accepted beside outcomes the gate ignores; and it buys nothing, because
#: an author who omits the pointer and an author who omits the file both land on
#: the same absent-evidence failure. A convention costs one constant and cannot
#: be mis-declared.
CONFORMANCE_EVIDENCE = "conformance.json"

#: Where a session's runs land, by the same CONVENTION as
#: :data:`CONFORMANCE_EVIDENCE`: one directory name inside the experiment,
#: named once here so the runner, the gate and the author cannot disagree. The
#: runner's own ``_next_session_run_root`` builds ``runs/run-NNNN`` and this is
#: the only other reader of that shape.
SESSION_RUNS_DIRNAME = "runs"

#: The terminal claim inside one run directory. Both session lanes write this
#: name — the data-driven store and the tests-mode runner — which is what lets
#: one gate read either without asking the contract which lane ran.
SESSION_RESULT_FILENAME = "result.json"

#: Where both lanes record the launch itself. ``recorded-launch`` is named for
#: this directory, so the branch reads it rather than settling for the terminal
#: result: a ``result.json`` alone is a claim ABOUT a launch, while a launch
#: record is the launch's own evidence, and an experiment that never spawned
#: anything can produce the first far more easily than the second.
SESSION_LAUNCHES_DIRNAME = "launches"

#: The run-directory shape the runner mints. A directory under ``runs/`` that
#: does not match is not a run this gate will count, in either direction: it
#: neither satisfies ``recorded-launch`` nor fails ``latest-sessions-accepted``,
#: because a name nothing writes is a name this gate cannot interpret.
#:
#: The two alternatives are exactly the images of ``f"run-{index:04d}"``: four
#: digits for the first 9999 runs, then five or more with no leading zero. The
#: shape is this narrow because the gate ORDERS runs by the integer in the
#: name, and a looser ``run-\\d{4,}`` admits ``run-00001`` beside ``run-0001``
#: — two directories claiming one position, with "latest" then decided by sort
#: stability rather than by anything real. Injectivity of name -> index is what
#: makes "the highest-indexed run" a well-defined phrase.
#:
#: **``[0-9]`` and not ``\\d``, ``\\A``/``\\Z`` and not ``^``/``$``.** Python's
#: ``\\d`` matches every Unicode decimal digit and ``int()`` parses them, so
#: ``run-٠٠٠١`` (Arabic-Indic) and ``run-１２３４`` (fullwidth) matched the old
#: spelling and resolved to indices 1 and 1234 — aliases for names the
#: allocator mints, and injectivity was therefore still false. ``$`` compounds
#: it by also matching before a trailing newline, so ``"run-0001\\n"`` was a
#: second alias for index 1. Directory names are bytes a filesystem accepts,
#: not text the pattern gets to assume, and this gate reads the name as an
#: ORDER KEY, so an alias is a second directory claiming one position.
SESSION_RUN_PATTERN = re.compile(r"\Arun-(?:[0-9]{4}|[1-9][0-9]{4,})\Z")

#: The allocator's range, matching ``_next_session_run_root``'s own bound. It
#: is asserted rather than assumed: ``run-0000`` and ``run-1000000`` have the
#: mintable SHAPE but no run the allocator produced ever carries either, so a
#: directory wearing one is not evidence of a launch.
MIN_SESSION_RUN_INDEX = 1
MAX_SESSION_RUN_INDEX = 999_999

#: Anything under ``runs/`` that CLAIMS to be a run by wearing the ``run-``
#: prefix over digits. The gate refuses such an entry that is not a real
#: directory at a mintable index, rather than skipping it.
#:
#: Skipping was the original behavior and it was not fail-closed: with a real
#: accepted ``run-0001`` present, making ``run-0002`` a symlink or a plain file
#: made the newest position vanish, and the older acceptance answered for it.
#: A name that is not of this shape at all — ``NOTES.md``, a scratch directory
#: — is genuinely unrelated to the numbered sequence and is still ignored.
#:
#: This one keeps Unicode-aware ``\\d`` ON PURPOSE, which is the opposite
#: choice from :data:`SESSION_RUN_PATTERN` one entry up, and the asymmetry is
#: the point. ``run-٠٠٠١`` is unmistakably claiming to be run 1, so it must be
#: REPORTED rather than passed over as an unrelated name — while the mint
#: pattern's ASCII-only spelling is what stops it from ever reaching the index
#: parse and aliasing a real ``run-0001``. Wide enough to catch the claim,
#: narrow enough to never count it.
SESSION_RUN_CLAIM_PATTERN = re.compile(r"\Arun-\d+\Z")

# Compatibility export for callers that used the old fixture helper. The close
# gate itself is driven only by KIND_POLICY and CLOSE_OBLIGATIONS below.
CONFORMANCE_GATED_KIND = next(
    kind
    for kind, policy in KIND_POLICY.items()
    if CLOSE_OBLIGATIONS.conformance in policy.close_obligations
)

#: The CLOSED, machine-readable finding vocabulary. Published because a CI job
#: may branch on it, and closed for the reason every vocabulary in this codebase
#: is closed: an eighth kind must be a decision, not an accident. Two of the
#: seven were exactly that decision — ``unmet-conformance`` at plan 03-06 and
#: the work pair at O-18 — each arriving with the branch that emits it.
#:
#: Notice what is NOT a kind here: there is no "unsatisfactory outcome" and there
#: never will be. All seven are about COMPLETENESS (a question unaccounted for in
#: one direction or the other), CITATION (a pointer that names no artifact),
#: REFERENCE (a named experiment that is not there), or — for a codegen or a
#: work experiment — the INTEGRITY OF THE ARTIFACT the experiment is about. None
#: is about whether the experiment's result was good.
#:
#: ``unmet-conformance`` is the one that has to earn its place beside the other
#: four, because it is the only one that reads a measurement rather than a
#: document. It earns it by being a claim about the SUBJECT's internal
#: consistency and not about its quality: the generated project no longer agrees
#: with the model it was generated from, so every conclusion recorded against
#: that project was measured against something the record no longer describes. An
#: experiment that honestly concludes "this approach failed" closes at 0; an
#: experiment whose tree has drifted from its own model cannot close at all,
#: whatever it concluded.
#:
#: ``unrecorded-launch`` and ``unaccepted-session`` are the WORK kind's two
#: (O-18), and they earn their place the same way ``unmet-conformance`` did: by
#: being about the experiment's DELIVERABLE rather than its conclusions. A work
#: experiment is the unit that replaced phase plans — its declared session IS
#: the work — so one that never launched has nothing to close over, and one
#: whose latest launch did not accept is claiming completion for work its own
#: declared gate refused. Neither branch reads ``outcome``: the conclusions may
#: honestly record anything, and a work experiment that is abandoned rather
#: than finished is recorded as a close REFUSAL that taught something, never
#: closed.
CloseFindingKind = Literal[
    "forgotten-question",
    "orphan-resolution",
    "unresolvable-evidence",
    "unresolved-reference",
    "unmet-conformance",
    "unrecorded-launch",
    "unaccepted-session",
]


@dataclass(frozen=True)
class CloseFinding:
    """One undischarged obligation.

    ``id`` is the offending question id or reference — reported verbatim, and
    reported at all, because "one question is unresolved" is a message an author
    cannot act on. Every gate message in this lane names the thing it is
    refusing (RESEARCH Common Pitfall 1: a message that names only a resolved
    path makes a mutation check unable to tell a test that reds for the right
    reason from one that reds for any reason).
    """

    kind: CloseFindingKind
    id: str
    message: str


@dataclass(frozen=True)
class CloseResult:
    """The gate's evaluation. ``findings`` empty means the experiment closes.

    ``declared`` and ``resolved`` are carried for REPORTING — an author reading a
    refusal wants to see both operands of the subtraction, not just its result.
    They are required rather than defaulted: a ``CloseResult`` that says "this
    experiment declared nothing" by default would be a small lie available to
    every future caller.
    """

    findings: list[CloseFinding]
    declared: tuple[str, ...]
    resolved: tuple[str, ...]
    #: Outcome values, in resolution order, for the CLI's report ONLY. Kept
    #: beside the verdict rather than inside it so that a reader can see them
    #: while the verdict provably did not: nothing in this module branches on
    #: them.
    outcomes: tuple[str, ...] = field(default=())


def _reference_finding(reference: str, message: str) -> CloseFinding:
    return CloseFinding(kind="unresolved-reference", id=reference, message=message)


def _follows_findings(spec: ExperimentSpec, spec_path: Path) -> list[CloseFinding]:
    """G-14, at its stated price: one field and one check.

    A ``follows:`` entry names a SIBLING experiment by directory name (plan
    03-01's decision: the id IS the directory name, which is why ``gnd exp
    validate`` refuses a spec whose id disagrees with its location). So the guard
    against T-03-08 — a content-supplied path joined raw — is that a legal
    reference must be a legal experiment id.

    That constraint is strictly stronger than the lexical path rules in
    :mod:`gnd.exp.paths`: :data:`~gnd.exp.spec.EXPERIMENT_DIR_PATTERN` admits no
    separator, no drive letter, no ``.`` and no ``..`` at ALL, so ``../../etc``,
    ``C:\\evil`` and ``/etc/passwd`` are refused before any path is constructed.
    It is therefore the ONE guard here rather than one guard plus an unreachable
    spare — a check that can never fire is a check that cannot fail, and plan
    03-01 already paid for that lesson (an ``is_dir()`` branch hoisted above an
    acceptance gate stops a mutation reding). **If this pattern is ever widened,
    the lexical path rules must be re-added below it.**

    "Concluded" is proxied by "carries a CONCLUSIONS.md", deliberately.
    Evaluating the referenced experiment RECURSIVELY is cross-experiment
    conclusion search, which is EXP-03 and is v2 — no index, no cache, no
    registry.
    """
    findings: list[CloseFinding] = []
    experiments_root = spec_path.parent.parent
    for reference in spec.follows:
        if not EXPERIMENT_DIR_PATTERN.match(reference):
            findings.append(
                _reference_finding(
                    reference,
                    f"follows: {reference!r} is not a legal experiment id; a "
                    f"reference resolves BY DIRECTORY NAME and must match "
                    f"{EXPERIMENT_DIR_PATTERN.pattern} — no path was built from it",
                )
            )
            continue
        referenced = experiments_root / reference
        if not referenced.is_dir():
            findings.append(
                _reference_finding(
                    reference,
                    f"follows: {reference!r} names no experiment beside this one "
                    f"({referenced}); a reference to an experiment that does not "
                    f"exist cites nothing",
                )
            )
            continue
        if not (referenced / CONCLUSIONS_FILENAME).is_file():
            findings.append(
                _reference_finding(
                    reference,
                    f"follows: {reference!r} exists but has no "
                    f"{CONCLUSIONS_FILENAME}; an experiment cannot build on one "
                    f"that has not concluded",
                )
            )
    return findings


def _conformance_finding(message: str) -> CloseFinding:
    return CloseFinding(kind="unmet-conformance", id=CONFORMANCE_EVIDENCE, message=message)


def _conformance_findings(spec: ExperimentSpec, spec_path: Path) -> list[CloseFinding]:
    """G-17 = SC4, as a branch selected by the kind policy table.

    **THE PASS RULE, stated once and derived here in the CONSUMER:**

        Conformance *passed* iff the schema-valid payload's ``findings`` array is
        EMPTY and every assertion in it reports ``ran:true``.

    The first clause is the rule this gate turns on. The second is not an
    addition to it — it is the precondition that makes it mean anything, and it
    is the reason ``ran`` exists in that payload at all: plan 05 put it there
    because "a check that could not run reports zero findings for the same reason
    a clean one does, so the count can never carry that distinction". Without the
    second clause, a payload recording an unreadable model would open this gate
    with an empty array, which is the R-13′ failure — a missing measurement
    looking green — arriving inside the one branch built to prevent it.

    **No pass-fail field was added to the conformance family to support this, and
    none may be.** G-15 assigns that family files, digests and drift and forbids
    it a verdict; a boolean summarizing the findings would be a verdict living in
    the wrong envelope (D-01's blending error inside the third payload family)
    AND a second source of truth for a fact already present in the data. The
    derivation belongs to the reader, and this function is the reader.

    **The recorded exit code is not consulted either**, and there is nowhere here
    that could be. An exit code is a property of a past process invocation, not of
    the artifact; a payload copied out of a different run would carry a stale one,
    and the payload is what the experiment commits.

    **An ABSENT result is a FAILURE, never a default pass.** A codegen experiment
    with no ``conformance.json`` is refused. This is R-13′'s rule again — a
    missing measurement must not look green — and it is exactly why plan 02 left
    this seam unfilled rather than defaulting it to a passing value.

    The artifact is resolved through :func:`~gnd.exp.paths.resolve_evidence_path`,
    the plan-01 validator, so it is non-empty, lexically safe under both path
    flavours, contained in the experiment directory, symlink-free and a real
    FILE — the same guarantees every cited evidence pointer gets, because this
    pointer decides more than any of them. It is then validated against
    ``conformance.schema.json`` BEFORE its findings array is read: an experiment
    author must not be able to open the gate with a hand-written file that merely
    looks like a payload, and an unvalidatable file is a FAILURE rather than an
    unknown.
    """
    if CLOSE_OBLIGATIONS.conformance not in KIND_POLICY[spec.kind].close_obligations:
        return []

    # Imported at call time: `gnd.exp` must stay importable without pulling the
    # generation lane in behind it, and the conformance package reaches
    # `gnd.codegen.emit` through assertion #3.
    import json  # noqa: F811 -- historical compatibility binding

    from jsonschema import Draft202012Validator, ValidationError

    from gnd.conformance.integrity import MAX_CONFORMANCE_BYTES
    from gnd.conformance.report import load_conformance_schema
    from gnd.conformance.service import run_conformance

    try:
        payload_path = resolve_evidence_path(spec_path, CONFORMANCE_EVIDENCE, field="conformance")
    except EvidencePathError as error:
        return [
            _conformance_finding(
                f"this experiment declares kind {spec.kind!r}, whose "
                f"conclusion is gated on model-code conformance, and no usable "
                f"{CONFORMANCE_EVIDENCE} is recorded beside it: {error}. Run `gnd "
                f"conformance MODEL DIR --format json > {CONFORMANCE_EVIDENCE}` in "
                f"the experiment directory. An absent measurement is not a passing "
                f"one"
            )
        ]

    size = payload_path.stat().st_size
    if size > MAX_CONFORMANCE_BYTES:
        return [
            _conformance_finding(
                f"{CONFORMANCE_EVIDENCE} is {size} bytes, over the "
                f"{MAX_CONFORMANCE_BYTES}-byte cap for untrusted committed "
                f"metadata; it was reported from its stat and never read"
            )
        ]

    try:
        payload = _rf7_input.loads(payload_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        return [
            _conformance_finding(
                f"{CONFORMANCE_EVIDENCE} could not be read as JSON, so the "
                f"conformance obligation could not be evaluated and is therefore "
                f"not discharged: {error}"
            )
        ]

    try:
        Draft202012Validator(load_conformance_schema()).validate(payload)
    except ValidationError as error:
        return [
            _conformance_finding(
                f"{CONFORMANCE_EVIDENCE} is not a valid conformance payload "
                f"(conformance.schema.json): {error.message} at "
                f"{'/'.join(str(part) for part in error.absolute_path) or '<root>'}. "
                f"A file that merely looks like a payload does not open this gate"
            )
        ]

    if spec.model is None or spec.project is None:
        return [
            _conformance_finding(
                "this codegen experiment does not declare both model: and "
                "project: experiment-relative references, so the recorded "
                "conformance payload cannot be rebound to a live subject"
            )
        ]

    try:
        model_path = resolve_evidence_path(spec_path, spec.model, field="model")
        project_root = resolve_experiment_directory(spec_path, spec.project, field="project")
        current_payload = run_conformance(model_path, project_root).payload
    except (
        EvidencePathError,
        OSError,
    ) as error:
        return [
            _conformance_finding(
                "live conformance could not be rerun over the model/project "
                f"declared by this experiment: {error}. A recorded result is "
                "not current evidence when its subject cannot be checked"
            )
        ]

    findings: list[CloseFinding] = []

    did_not_run = [
        str(assertion.get("id"))
        for assertion in payload.get("assertions", [])
        if not assertion.get("ran")
    ]
    if did_not_run:
        findings.append(
            _conformance_finding(
                f"the recorded conformance run reports assertion(s) "
                f"{', '.join(sorted(did_not_run))} as NOT HAVING RUN"
                + (f" ({payload.get('error')})" if payload.get("error") else "")
                + f". Zero findings from a check that did not run is not a clean "
                f"result, and {CONFORMANCE_EVIDENCE} is the artifact this "
                f"experiment committed"
            )
        )

    drift = payload.get("findings", [])
    if drift:
        named = ", ".join(f"{entry.get('kind')}:{entry.get('target')}" for entry in drift[:4])
        findings.append(
            _conformance_finding(
                f"the recorded conformance run reports {len(drift)} drift "
                f"finding(s) — {named}"
                + (" and more" if len(drift) > 4 else "")
                + ". A codegen experiment cannot close over a generated project "
                "that no longer agrees with its model, because every conclusion "
                "it records was measured against a tree the record no longer "
                "describes"
            )
        )

    if current_payload != payload:
        findings.append(
            _conformance_finding(
                f"{CONFORMANCE_EVIDENCE} does not match a canonical live "
                "conformance run over the experiment's declared model and "
                "project. The recorded result is stale or belongs to a "
                "different subject; regenerate it before closing"
            )
        )

    return findings


@dataclass(frozen=True)
class _SessionRun:
    """One minted run directory, ordered by the index in its own name."""

    index: int
    root: Path
    result: Path | None
    launched: bool


def _launch_finding(run_id: str, message: str) -> CloseFinding:
    return CloseFinding(kind="unrecorded-launch", id=run_id, message=message)


def _session_finding(run_id: str, message: str) -> CloseFinding:
    return CloseFinding(kind="unaccepted-session", id=run_id, message=message)


#: The launch records a run's ``launches/`` directory may contain. The runner
#: writes ``0001.json``, zero-padded like the run directories one level up, so
#: an arbitrary ``forged.json`` is not one of them.
SESSION_LAUNCH_PATTERN = re.compile(r"\A[0-9]{4,}\.json\Z")


def _launch_records(run_root: Path) -> list[Path]:
    """Every well-named regular launch record in this run, sorted.

    A launch record is the evidence that a run actually happened, so what
    counts as one is deliberately narrow: a real regular file, in a real
    directory, named the way the runner names them. The first version accepted
    any regular filename ending in ``.json``, which made
    ``launches/forged.json`` containing ``{}`` sufficient — the obligation was
    satisfiable by creating a file with the right extension.

    **Timing, stated accurately.** The data-driven store writes its launch
    record BEFORE the agent is invoked; the tests lane writes ``0001.json``
    after the child has run, because the document it writes carries the
    post-child manifests. So a launch record proves a run reached publication,
    not that a child was spawned at a particular moment — a narrower claim than
    an earlier version of this docstring made, and the accurate one.
    """
    launches = run_root / SESSION_LAUNCHES_DIRNAME
    try:
        info = launches.lstat()
    except FileNotFoundError:
        return []
    if stat.S_ISLNK(info.st_mode) or not stat.S_ISDIR(info.st_mode):
        return []
    found: list[Path] = []
    for entry in sorted(launches.iterdir()):
        if not SESSION_LAUNCH_PATTERN.match(entry.name):
            continue
        entry_info = entry.lstat()
        if stat.S_ISREG(entry_info.st_mode):
            found.append(entry)
    return found


def _has_launch_record(run_root: Path) -> bool:
    """Whether this run holds the launch's own evidence, not a claim about it."""
    return bool(_launch_records(run_root))


def _read_capped(path: Path, cap: int) -> bytes:
    """Read at most ``cap`` bytes through ONE descriptor opened ``O_NOFOLLOW``.

    Not ``lstat`` then ``stat`` then :meth:`Path.read_bytes`. That sequence
    checks one object and reads another: between the checks and the read the
    name can be repointed at a symlink to an accepted result elsewhere, or at a
    file that grows past the cap, and the cap then describes only a file that
    no longer exists. Opening once with ``O_NOFOLLOW``, verifying the
    DESCRIPTOR with ``fstat``, and bounding the read on that same descriptor
    makes the checked object and the read object the same object.

    ``O_NONBLOCK`` is part of the same idiom and is not decoration: opening a
    FIFO read-only BLOCKS until a writer appears, and the ``fstat`` that would
    have rejected it runs only after the open returns — so without it a named
    pipe standing where ``result.json`` belongs hangs `gnd exp close` forever
    rather than refusing it. ``gnd.exp.junit`` opens its own untrusted result
    path with exactly these flags for exactly this reason. The flag is ignored
    for regular files, which is every legitimate case.

    Raises ``OSError`` when the name is not a regular file, and ``ValueError``
    when the descriptor holds more than the cap.
    """
    flags = os.O_RDONLY | os.O_NONBLOCK | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_CLOEXEC", 0)
    fd = os.open(path, flags)
    try:
        info = os.fstat(fd)
        if not stat.S_ISREG(info.st_mode):
            raise OSError(f"{path} is not a regular file")
        # Read to cap + 1 so "exactly at the cap" and "over it" are told apart
        # by the read itself rather than by a size the read did not use — and
        # LOOP, because a single os.read may return fewer bytes than asked for.
        # Treating one short read as end-of-file would truncate a legitimate
        # large result and refuse it as unparseable, which is a false refusal
        # produced by the safety check rather than by the evidence.
        chunks: list[bytes] = []
        remaining = cap + 1
        while remaining > 0:
            chunk = os.read(fd, remaining)
            if not chunk:
                break
            chunks.append(chunk)
            remaining -= len(chunk)
        payload = b"".join(chunks)
        if len(payload) > cap:
            raise ValueError(f"{path} exceeds the {cap}-byte cap")
        return payload
    finally:
        os.close(fd)


def _session_runs(experiment_root: Path) -> tuple[list[_SessionRun], list[CloseFinding]]:
    """``(runs newest-last, findings)`` for everything under ``runs/``.

    Enumeration is narrow, total, and FAIL-CLOSED, and the third is the one
    that had to be repaired. Narrow: only a real directory at a mintable index
    is a run this gate can order, and a set it cannot order has no "latest" to
    check. Total: an unreadable ``runs/`` raises ``OSError`` to the caller
    rather than reading as an empty sequence, because "there are no runs" and
    "I could not look" are different claims and only one is the author's fault.

    Fail-closed: an entry that CLAIMS to be a run — the ``run-`` prefix over
    digits — but is a symlink, a plain file, or at an index the allocator
    cannot mint is reported, never skipped. Skipping it was unsound in exactly
    the case that matters: with a real accepted ``run-0001`` present, making
    ``run-0002`` a symlink deleted the newest position from the gate's view and
    let the older acceptance answer in its place. A name of another shape
    entirely is unrelated to the numbered sequence and is still ignored.
    """
    runs_root = experiment_root / SESSION_RUNS_DIRNAME
    try:
        info = runs_root.lstat()
    except FileNotFoundError:
        return [], []
    if stat.S_ISLNK(info.st_mode) or not stat.S_ISDIR(info.st_mode):
        raise OSError(f"session runs root {runs_root} must be a real directory")

    runs: list[_SessionRun] = []
    findings: list[CloseFinding] = []
    for entry in sorted(runs_root.iterdir()):
        if not SESSION_RUN_CLAIM_PATTERN.match(entry.name):
            continue

        entry_info = entry.lstat()
        if stat.S_ISLNK(entry_info.st_mode) or not stat.S_ISDIR(entry_info.st_mode):
            findings.append(
                _session_finding(
                    entry.name,
                    f"{SESSION_RUNS_DIRNAME}/{entry.name} is named as a run but "
                    f"is not a real directory; the gate will not read past it "
                    f"to an older run, because an object standing where the "
                    f"newest run should be hides exactly the run that decides "
                    f"this obligation",
                )
            )
            continue

        if not SESSION_RUN_PATTERN.match(entry.name):
            findings.append(
                _session_finding(
                    entry.name,
                    f"{SESSION_RUNS_DIRNAME}/{entry.name} is not a name `gnd "
                    f"exp run` mints — the allocator writes `run-NNNN` "
                    f"zero-padded to four digits — so it is not evidence of a "
                    f"launch and cannot be placed in the run order",
                )
            )
            continue

        index = int(entry.name.removeprefix("run-"))
        if not MIN_SESSION_RUN_INDEX <= index <= MAX_SESSION_RUN_INDEX:
            findings.append(
                _session_finding(
                    entry.name,
                    f"{SESSION_RUNS_DIRNAME}/{entry.name} carries index {index}, "
                    f"outside the allocator's range "
                    f"{MIN_SESSION_RUN_INDEX}–{MAX_SESSION_RUN_INDEX}; no run "
                    f"`gnd exp run` produced is numbered this way",
                )
            )
            continue

        candidate = entry / SESSION_RESULT_FILENAME
        try:
            result_info = candidate.lstat()
        except FileNotFoundError:
            result = None
        else:
            result = candidate if stat.S_ISREG(result_info.st_mode) else None
        runs.append(_SessionRun(index, entry, result, launched=_has_launch_record(entry)))
    return sorted(runs, key=lambda run: run.index), findings


def _accepted_disposition(payload: bytes) -> tuple[bool, str, str]:
    """``(accepted, run_id, description)`` for either lane's terminal claim.

    ONE gate reads BOTH lanes, and it reads each through that lane's own strict
    model rather than through a hand-rolled ``payload["disposition"] ==
    "accepted"``. A dict lookup would accept any document carrying that one key
    — including a two-line file an author wrote by hand — which is the same
    defect ``_conformance_findings`` refuses by validating against the
    conformance schema before reading its findings array. Here the strict
    readers are :class:`~gnd.exp.session_store.SessionResult` (the data-driven
    store) and :class:`~gnd.exp.tests_runner.TestsSessionResult` (the tests
    lane); both are ``extra="forbid"`` with closed disposition vocabularies.

    Either lane may have produced the run, and the gate does not consult the
    contract to decide which to expect: a work experiment may declare tests and
    non-tests cases, and asking the contract would make this branch disagree
    with the runner that actually wrote the file.

    The returned ``run_id`` is the document's OWN claim about which run it
    belongs to, and the caller checks it against the directory the document was
    found in. See :func:`_work_findings` for why that check is the difference
    between a gate and a formality.
    """
    from pydantic import ValidationError

    from gnd.exp.session_store import SessionOutcome, SessionResult
    from gnd.exp.tests_runner import TestsSessionResult

    # RecursionError joins the caught set because it is what CPython's JSON
    # parser raises on deeply nested input — 10,000 nested arrays fit in 20 KB,
    # well under the byte cap — and it is not a ValueError. Uncaught, a hostile
    # committed artifact escaped this branch entirely and left `gnd exp close`
    # with a traceback instead of a refusal, which is a missing measurement
    # looking like anything other than a failure (R-13′).
    _MALFORMED = (ValidationError, ValueError, RecursionError)

    try:
        result = SessionResult.model_validate_json(payload)
    except _MALFORMED:
        pass
    else:
        return (
            result.disposition is SessionOutcome.accepted,
            result.run_id,
            (f"disposition {result.disposition.value!r} ({result.terminal_reason})"),
        )

    try:
        tests_result = TestsSessionResult.model_validate_json(payload)
    except _MALFORMED as error:
        raise ValueError(str(error)) from error
    return (
        tests_result.disposition == "accepted",
        tests_result.run_id,
        f"disposition {tests_result.disposition!r}"
        + (f" ({tests_result.reason})" if tests_result.reason else ""),
    )


def _launch_digest_findings(run: _SessionRun, payload: bytes) -> list[CloseFinding]:
    """Bind the tests-lane result to a launch record that actually exists.

    The tests lane's ``result.json`` NAMES its launch record by digest --
    ``launch_sha256`` is the SHA-256 of ``launches/0001.json``'s bytes -- and
    until this check the gate read that field and never looked. "A launch
    record exists" and "the launch record this result describes exists" are
    different claims, and only the second is evidence about THIS result.

    The data-driven lane carries no equivalent digest in its terminal document,
    so it gets the weaker check (a well-named launch record is present) and
    this function says so rather than pretending the two lanes are bound
    equally.
    """
    from pydantic import ValidationError

    from gnd.exp.tests_runner import TestsSessionResult

    try:
        tests_result = TestsSessionResult.model_validate_json(payload)
    except (ValidationError, ValueError, RecursionError):
        return []  # a data-driven result; its own reader already accepted it
    if tests_result.launch_sha256 is None:
        return []

    import hashlib

    for record in _launch_records(run.root):
        try:
            digest = hashlib.sha256(record.read_bytes()).hexdigest()
        except OSError:
            continue
        if digest == tests_result.launch_sha256:
            return []
    return [
        _session_finding(
            run.root.name,
            f"{run.root.name}/{SESSION_RESULT_FILENAME} names launch record "
            f"{tests_result.launch_sha256[:12]}... but no file in "
            f"{SESSION_LAUNCHES_DIRNAME}/ hashes to it; the result describes a "
            f"launch this run does not hold",
        )
    ]


#: The session contract, beside ``SPEC.md``. Read here only to learn which
#: cases the experiment DECLARED; the contract's own reader owns everything
#: else about it.
SESSION_CONTRACT_FILENAME = "session.contract.json"

#: The contract's own cap, restated here as the READ bound for the same file.
#: Named from the contract module so the two cannot drift.
MAX_SESSION_CONTRACT_READ_BYTES = 1 * 1024 * 1024


def _declared_case_findings(
    run: _SessionRun,
    experiment_root: Path,
    payload: bytes,
    *,
    experiment_id: str | None = None,
) -> list[CloseFinding]:
    """An accepted result must account for every required tests case declared.

    The document's internal rules cannot catch this one, and that is why it
    needs the contract. Take a REAL two-case result whose second case failed,
    delete the failing case's feedback row, flip ``disposition`` to
    ``accepted`` and ``reason`` to null, and every surviving row is honest,
    every field is legal, and the only evidence of the deleted case is its
    absence. A document cannot notice what is missing from itself.

    The contract can: it is the committed declaration of which cases the run
    was required to satisfy. So an accepted result must carry a required row
    for every required tests-mode case the contract declares.

    **A contract that cannot be read is NOT a pass.** An accepted result whose
    declaration is unreadable cannot be checked for completeness, and R-13′
    makes an uncheckable measurement a refusal rather than an unknown.
    """
    from pydantic import ValidationError

    from gnd.exp.session import case_payload_versions
    from gnd.exp.session_contract import (
        SessionContractError,
        TransitionAcceptance,
        read_session_contract,
    )
    from gnd.exp.session_eval import case_decision
    from gnd.exp.session_store import SessionResult, SessionStore
    from gnd.exp.tests_runner import TestsSessionResult

    try:
        session_result = SessionResult.model_validate_json(payload)
    except (ValidationError, ValueError, RecursionError):
        session_result = None
    if session_result is not None:
        if session_result.schema_version not in {5, 6, 7}:
            return []
        contract_path = experiment_root / SESSION_CONTRACT_FILENAME
        try:
            raw = _read_capped(contract_path, MAX_SESSION_CONTRACT_READ_BYTES)
            document = _rf7_input.loads(raw)
            selected_id = experiment_id or document["experiment_id"]
            contract = read_session_contract(
                contract_path,
                experiment_root=experiment_root,
                experiment_id=selected_id,
            )
        except (
            OSError,
            ValueError,
            TypeError,
            KeyError,
            RecursionError,
            SessionContractError,
        ) as error:
            return [
                _session_finding(
                    run.root.name,
                    f"{run.root.name}/{SESSION_RESULT_FILENAME} reports walk-floor "
                    f"accounting, but {SESSION_CONTRACT_FILENAME} could not be read "
                    f"and rebound: {error}",
                )
            ]
        import hashlib

        expected = {
            case.case_id: (
                case.role.value,
                len(case.acceptance.walk.required_ops),
                len(case.acceptance.walk.forbidden_ops),
            )
            for case in contract.cases
            if isinstance(case.acceptance, TransitionAcceptance)
            and case.acceptance.walk is not None
        }
        observed = {
            row.case_id: (row.role, row.required_ops, row.forbidden_ops)
            for row in session_result.walk_floors
        }
        case_names = ", ".join(sorted(expected)) or "<none>"
        if session_result.contract_sha256 != hashlib.sha256(raw).hexdigest():
            return [
                _session_finding(
                    run.root.name,
                    f"walk-floor result for declared case(s) {case_names} is bound "
                    "to a different session contract digest",
                )
            ]
        if observed != expected:
            return [
                _session_finding(
                    run.root.name,
                    f"walk-floor result does not exactly account for declared "
                    f"case(s) {case_names} and their required/forbidden counts",
                )
            ]
        try:
            if session_result.best_attempt is None:
                raise ValueError("result does not name a best attempt")
            store = SessionStore(
                run.root,
                run_id=run.root.name,
                contract_id=contract.experiment_id,
            )
            if session_result.schema_version in {6, 7}:
                from gnd.exp.session_v7 import reconstruct

                if contract.schema_version not in {7, 8}:
                    raise ValueError("v7 result requires its v7 contract")
                reconstruct(store, contract, allow_terminal=True)
                record, _ = store._v7_best
                attempt_bytes = store._read_evidence_leaf(
                    f"attempts/{record.attempt_index:04d}/attempt.json", cap=10 * 1024 * 1024
                )
            else:
                record, attempt_bytes, _, _ = store._load_attempt_for_resume(
                    session_result.best_attempt,
                    contract=contract,
                    expected_payload_versions=case_payload_versions(contract, experiment_root),
                )
            if (
                hashlib.sha256(attempt_bytes).hexdigest()
                != session_result.best_attempt_manifest_sha256
                or record.candidate_inventory.tree_sha256 != session_result.best_candidate_sha256
            ):
                raise ValueError("best-attempt identity differs from immutable evidence")
        except (OSError, ValueError) as error:
            return [
                _session_finding(
                    run.root.name,
                    f"walk-floor result for declared case(s) {case_names} is not "
                    f"bound to its named immutable attempt: {error}",
                )
            ]
        evaluations = {row.case_id: row for row in record.evaluation.results}
        inconsistent = sorted(
            row.case_id
            for row in session_result.walk_floors
            if (evaluation := evaluations.get(row.case_id)) is None
            or row.discharged
            != case_decision(
                next(case for case in contract.cases if case.case_id == row.case_id),
                evaluation,
            ).accepted
        )
        if inconsistent:
            return [
                _session_finding(
                    run.root.name,
                    "walk-floor discharge differs from immutable attempt for case(s) "
                    + ", ".join(inconsistent),
                )
            ]
        undischarged = sorted(
            row.case_id
            for row in session_result.walk_floors
            if row.role == "required" and not row.discharged
        )
        if undischarged:
            return [
                _session_finding(
                    run.root.name,
                    "required walk floor is not discharged for case(s) " + ", ".join(undischarged),
                )
            ]
        return []

    try:
        tests_result = TestsSessionResult.model_validate_json(payload)
    except (ValidationError, ValueError, RecursionError):
        return []  # a data-driven result; case accounting is its reader's own

    contract_path = experiment_root / SESSION_CONTRACT_FILENAME
    try:
        raw = _read_capped(contract_path, MAX_SESSION_CONTRACT_READ_BYTES)
        document = _rf7_input.loads(raw)
        cases = document["cases"]
        declared = {
            str(case["case_id"])
            for case in cases
            if case.get("role") == "required"
            and isinstance(case.get("acceptance"), dict)
            and case["acceptance"].get("mode") == "tests"
        }
    except (OSError, ValueError, TypeError, KeyError, RecursionError) as error:
        return [
            _session_finding(
                run.root.name,
                f"{run.root.name}/{SESSION_RESULT_FILENAME} reports acceptance, "
                f"but {SESSION_CONTRACT_FILENAME} could not be read to check "
                f"that every declared case is accounted for: {error}. An "
                f"acceptance whose declaration is unreadable is not a checked "
                f"acceptance",
            )
        ]

    present = {row.case_id for row in tests_result.feedback if row.role == "required"}
    missing = declared - present
    if missing:
        return [
            _session_finding(
                run.root.name,
                f"{run.root.name}/{SESSION_RESULT_FILENAME} reports acceptance "
                f"but carries no required feedback row for declared case(s) "
                f"{', '.join(sorted(missing))}; a result that accounts for only "
                f"some of the cases it had to satisfy is not an acceptance of "
                f"all of them",
            )
        ]
    return []


def _work_findings(spec: ExperimentSpec, spec_path: Path) -> list[CloseFinding]:
    """O-18's two work obligations, each a branch with its own failing case.

    A ``work`` experiment is the unit this milestone put in a phase plan's
    place, so what it must discharge to close is not what an ``analysis``
    experiment must: its declared session IS the work it committed to do.

    - ``recorded-launch``: at least one minted run directory holds a launch
      record under ``launches/`` AND a terminal ``result.json``. An experiment
      that never launched has nothing to close over, and an author who closes
      one has recorded a completion for work that did not run. The launch
      record rather than the result alone is what the obligation is NAMED for,
      and the difference is not pedantic: a ``result.json`` is a claim about a
      launch, which an author can author, while the launch record is the
      launch's own evidence, which only a run that reached publication has.
    - ``latest-sessions-accepted``: the HIGHEST-INDEXED run — the last thing
      that happened — reports ``accepted``. Not "some run accepted": a rule
      satisfied by any run in the history would let a green attempt three runs
      back speak for a red one that came after it, which is a gate that reports
      a state nobody established.

    **Neither branch reads an outcome value, and the asymmetry of the module
    docstring is intact.** G-12 forbids requiring that the questions resolved
    *well*, and these do not: a work experiment whose every question resolves
    ``unanswered`` with a reason still closes at exit 0, provided its declared
    session ran and accepted. What these require is that the DELIVERABLE
    exists — the same claim the codegen branch makes about a generated tree.
    A work experiment abandoned rather than finished does not close; per the
    record contract it is recorded as a close REFUSAL that taught something,
    which is a `docs` record and an honest one.

    **A missing or unreadable terminal result is a FAILURE, never a default
    pass** (R-13′). The three ways a latest run can fail to establish
    acceptance — no ``result.json`` at all, one that no strict reader accepts,
    and one that reads cleanly and says something other than ``accepted`` — are
    three separate messages, because an author cannot act on a message that
    names only the third.
    """
    obligations = KIND_POLICY[spec.kind].close_obligations
    wants_launch = CLOSE_OBLIGATIONS.recorded_launch in obligations
    wants_accepted = CLOSE_OBLIGATIONS.latest_sessions_accepted in obligations
    if not wants_launch and not wants_accepted:
        return []

    experiment_root = spec_path.parent
    runs, findings = _session_runs(experiment_root)

    if wants_launch and not any(run.result is not None and run.launched for run in runs):
        findings.append(
            _launch_finding(
                SESSION_RUNS_DIRNAME,
                f"this experiment declares kind {spec.kind!r}, whose declared "
                f"session IS the work it committed to do, and no launch is "
                f"recorded: no {SESSION_RUNS_DIRNAME}/run-NNNN holds both a "
                f"{SESSION_LAUNCHES_DIRNAME}/ record and a "
                f"{SESSION_RESULT_FILENAME} beside {spec_path.name}. Run "
                f"`gnd exp run {spec.id}` before closing — an experiment that "
                f"never launched has nothing to close over",
            )
        )

    if not wants_accepted or not runs:
        return findings

    latest = runs[-1]
    if latest.result is None:
        findings.append(
            _session_finding(
                latest.root.name,
                f"the latest recorded launch {latest.root.name!r} left no "
                f"{SESSION_RESULT_FILENAME}, so it never reached a terminal "
                f"claim; a launch whose disposition was never written is not an "
                f"accepted one",
            )
        )
        return findings

    if not latest.launched:
        findings.append(
            _session_finding(
                latest.root.name,
                f"the latest run {latest.root.name!r} carries a "
                f"{SESSION_RESULT_FILENAME} but no "
                f"{SESSION_LAUNCHES_DIRNAME}/ record, so nothing was ever "
                f"spawned in it; a terminal claim without the launch it "
                f"describes is an assertion, not evidence",
            )
        )
        return findings

    from gnd.exp.session_store import MAX_SESSION_RESULT_BYTES

    try:
        payload = _read_capped(latest.result, MAX_SESSION_RESULT_BYTES)
    except ValueError:
        findings.append(
            _session_finding(
                latest.root.name,
                f"{latest.root.name}/{SESSION_RESULT_FILENAME} is over the "
                f"{MAX_SESSION_RESULT_BYTES}-byte cap for untrusted committed "
                f"metadata; the read stopped at the cap rather than continuing",
            )
        )
        return findings
    except OSError as error:
        findings.append(
            _session_finding(
                latest.root.name,
                f"{latest.root.name}/{SESSION_RESULT_FILENAME} could not be "
                f"read, so acceptance could not be established and is therefore "
                f"not discharged: {error}",
            )
        )
        return findings

    try:
        accepted, run_id, description = _accepted_disposition(payload)
    except ValueError as error:
        findings.append(
            _session_finding(
                latest.root.name,
                f"{latest.root.name}/{SESSION_RESULT_FILENAME} is not a valid "
                f"session result under either lane's reader: {error}. A file "
                f"that merely looks like a result does not open this gate",
            )
        )
        return findings

    if run_id != latest.root.name:
        findings.append(
            _session_finding(
                latest.root.name,
                f"{latest.root.name}/{SESSION_RESULT_FILENAME} reports "
                f"run_id {run_id!r}, so it is not this run's terminal claim — "
                f"it belongs to {run_id!r}. An accepted result copied out of an "
                f"earlier run does not make a later one accepted",
            )
        )
        return findings

    if not accepted:
        findings.append(
            _session_finding(
                latest.root.name,
                f"the latest recorded launch {latest.root.name!r} reports "
                f"{description}; a work experiment cannot close over a session "
                f"its own declared gate refused. Fix what the disposition names "
                f"and re-run, or record the refusal honestly instead of closing",
            )
        )
        return findings

    findings.extend(_launch_digest_findings(latest, payload))
    findings.extend(
        _declared_case_findings(
            latest,
            spec_path.parent,
            payload,
            experiment_id=spec.id,
        )
    )
    return findings


def evaluate_close(
    spec: ExperimentSpec,
    conclusions: ExperimentConclusions,
    spec_path: str | Path,
) -> CloseResult:
    """Evaluate every close obligation and return them ALL.

    Not first-failure-wins: an author who fixes a forgotten question and re-runs
    should not then discover an orphan. Reporting one difference at a time makes
    the two-set formulation invisible, and is how somebody concludes the orphan
    check does not exist.

    ``spec_path`` locates the experiment directory — evidence pointers resolve
    against it, ``follows:`` references resolve against its parent, and the
    codegen branch resolves ``conformance.json`` inside it.

    **There is still no conformance parameter, and adding one — defaulted or
    not — is forbidden** (G-17). :func:`_conformance_findings` reads the recorded
    payload from the experiment directory itself, so no caller can supply,
    forget, or fabricate the input this gate turns on. See the module docstring.
    """
    path = Path(spec_path)
    declared = tuple(question.id for question in spec.questions)
    resolved = tuple(resolution.id for resolution in conclusions.resolves)

    findings: list[CloseFinding] = []

    # The subtraction, both ways. `outcome` is not read here and is not read
    # anywhere in this module: the gate's verdict is a function of set membership
    # and pointer resolvability ONLY (G-12). The one rule that does depend on an
    # outcome value — a non-answer must carry a reason — was discharged by
    # Resolution's own validator at load, before this function was called.
    declared_set = set(declared)
    resolved_set = set(resolved)
    obligations = KIND_POLICY[spec.kind].close_obligations

    if CLOSE_OBLIGATIONS.complete_conclusions in obligations:
        for question in declared:  # declared order: the spec's order is the report's
            if question not in resolved_set:
                findings.append(
                    CloseFinding(
                        kind="forgotten-question",
                        id=question,
                        message=(
                            f"declared question {question!r} is not resolved in "
                            f"{CONCLUSIONS_FILENAME}; an experiment may close on an "
                            f"honest 'unanswered' with a reason, but it may not "
                            f"quietly forget a question it set out to answer"
                        ),
                    )
                )

        for resolution_id in resolved:
            if resolution_id not in declared_set:
                findings.append(
                    CloseFinding(
                        kind="orphan-resolution",
                        id=resolution_id,
                        message=(
                            f"{CONCLUSIONS_FILENAME} resolves {resolution_id!r}, which "
                            f"SPEC.md never declared; an answer to a question nobody "
                            f"asked is not a conclusion this experiment committed to"
                        ),
                    )
                )

    # Citation. D-22 made structural (G-13): a published claim cannot exist
    # without a raw artifact a reader can open.
    if CLOSE_OBLIGATIONS.resolving_evidence in obligations:
        for resolution in conclusions.resolves:
            try:
                resolve_evidence_path(path, resolution.evidence, field="evidence")
            except EvidencePathError as error:
                findings.append(
                    CloseFinding(
                        kind="unresolvable-evidence",
                        id=resolution.id,
                        message=(
                            f"resolution {resolution.id!r} cites evidence that does not "
                            f"resolve: {error}"
                        ),
                    )
                )

    findings.extend(_follows_findings(spec, path))

    # G-17 = SC4. A branch in code with its own mutation test, because a success
    # criterion discharged by a sentence in a SKILL.md is a gate that cannot fail.
    # THE PASS RULE: conformance passed iff the schema-valid payload's `findings`
    # array is empty AND every assertion in it reports ran:true. Nothing else is
    # consulted — no verdict field (none exists, and G-15 forbids one), and no
    # recorded exit code (a property of a past process, not of the artifact).
    findings.extend(_conformance_findings(spec, path))

    # O-18. The work kind's two obligations, selected by the same table and for
    # the same reason the conformance branch is: a work experiment's declared
    # session is its deliverable, so "did it run, and did the last run accept"
    # is a claim about the ARTIFACT, never about whether its questions resolved
    # well. Nothing here reads `outcome` either.
    findings.extend(_work_findings(spec, path))

    return CloseResult(
        findings=findings,
        declared=declared,
        resolved=resolved,
        outcomes=tuple(resolution.outcome for resolution in conclusions.resolves),
    )


def close_outcome(result: CloseResult) -> int:
    """Close findings -> exit code. ONE decision function, like ``_install_outcome``.

    Precedence is trivially short and that is a design statement, not an
    omission: **any finding -> 14, otherwise 0.** All five finding kinds are one
    claim — *this experiment's obligations are not discharged* — so splitting
    them across bands would ask a CI job to distinguish repairs that are largely
    the same repair (go back to the experiment and finish it). The kinds stay
    machine-readable in :class:`CloseFinding` for a reader who wants the detail,
    which is where a detail belongs when it does not change what the caller does.

    ``unmet-conformance`` is 14 here and NOT band 13. 13 is
    ``EXIT_MODEL_CODE_DRIFT``, a claim about a GENERATED PROJECT whose repair is
    ``gnd codegen``; this is a claim about an EXPERIMENT that may not close, whose
    repair is to re-measure and re-conclude. The drift is the reason, not the
    verdict — one number meaning two claims is D-01's blending error arriving in
    the exit-code contract (G-16), and the payload the branch read is where a
    reader goes for the drift itself.

    The bands ABOVE this function belong to ``_experiment_outcome`` in the CLI,
    which keeps the shipped precedence **74 > 66 > 3 > 14 > 0**: an unreadable
    target says nothing about its contents, a missing SPEC.md means the
    subtraction has no left operand, and an unparseable document means the
    obligations could not be EVALUATED — reporting 14 for any of those would
    assert "this experiment is still open" when the truth is "this experiment is
    unreadable".

    **Band 10 is deliberately not reused.** ``EXIT_DRIFT = 10`` already means
    *doctor's ASSET drift* — installed skill files stale, missing or modified,
    repaired by re-installing. A refused close is a different claim about a
    different artifact with an unrelated repair. One number meaning two drifts is
    D-01's blending error arriving in the exit-code contract (G-16), and it would
    be discovered by whoever writes the first CI job that branches on it.

    **The outcome VALUES are not an input to this function.** They are not even
    reachable from ``result.findings``, which is the point: a verdict computed
    from findings cannot be moved by writing a flattering outcome (T-03-07).
    """
    from gnd.exits import EXIT_EXPERIMENT_OPEN

    if result.findings:
        return EXIT_EXPERIMENT_OPEN
    return 0
