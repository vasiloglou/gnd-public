"""Assertion #2 — the manifest's model digest equals the model's digest NOW.

**This assertion IS model-code drift.** GEN-02's headline is one sentence long:
the model moved and the code did not. Everything else conformance reports is
about the generated tree agreeing with its own record; this is the only check
that compares the tree's record against the *source of truth*.

**It is a standalone callable, and that is a design constraint rather than a
style preference.** ``gnd.cli`` already contains this loop once, inline, at
``cli.py:841-883`` (``_artifact_index_issue``) — recorded-versus-actual digests
computed in the middle of a command, returning ``(exit, message)`` tuples. A
third hand-written copy is what plan 03-04 refused for the manifest writer and
what this module refuses for the comparison. Phase 4's MODEL-02 must trigger a
downstream conformance re-check when a model changes, and it calls this function
from a THIRD entry point that is neither ``gnd conformance`` nor ``gnd codegen``.
Designing currency as something only the CLI can perform would strand that
dependency and make Phase 4 pay to extract it.

So: no argv, no parser, no printing, no ``sys.exit``, and no import of
``gnd.cli``. ``tests/test_conformance_drift.py`` asserts the last one in a fresh
interpreter, with a negative control proving the probe can report the opposite.

**Fail closed on an unreadable model.** ``model_digest`` raises rather than
returning a sentinel, because a sentinel would make an ABSENT model report as
drift — sending the user to regenerate against a file that is gone, when the
honest answer is that the check could not run at all. The CLI maps that to
exit 66 (a required artifact is missing), never to 13.

**The digest is over BYTES, not over the parsed model.** Two consequences worth
stating, because both are deliberate:

* A comment-only edit to ``model.orm.yaml`` reports drift even though the loaded
  model is identical. That is the honest answer for a digest-bound record: the
  manifest recorded the bytes it read, the bytes changed, and regeneration is
  one command. Hashing a canonicalized parse instead would introduce a second
  notion of model identity that ``build_manifest`` does not share, and two
  identities that disagree is strictly worse than one that is occasionally
  conservative.
* The model is never PARSED here, so a model that no longer loads still gets a
  currency answer. RESEARCH's G-09′ trap is the reverse of this and worth
  remembering: plan 06's structural assertion does load the model, and a
  mutation that makes the model invalid reds it through
  ``ModelValidationError`` rather than through the check.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

from gnd.codegen.manifest import CodegenManifest
from gnd.conformance import ConformanceError, Finding

__all__ = [
    "check_currency",
    "model_digest",
]


def model_digest(model_path: str | Path) -> str:
    """The model's content identity: sha256 over its bytes.

    The same computation ``build_manifest`` performs when it records
    ``model.sha256``, so the two sides of the comparison cannot drift apart by
    one of them changing how it hashes.
    """
    path = Path(model_path)
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError as error:
        raise ConformanceError(
            f"{path} could not be read, so currency could not be checked at "
            f"all: {error}. This is NOT drift — a check that could not run "
            f"must never report the project as conforming, and must not report "
            f"it as drifted either"
        ) from error


def check_currency(
    model_path: str | Path, manifest: CodegenManifest
) -> tuple[Finding, ...]:
    """Assertion #2: one finding if the model moved without regeneration.

    A pure function of a path and a record. Returns an empty tuple when the
    digests agree — the over-correction control asserts exactly that over a
    freshly generated project, because a check that always fires looks exactly
    like a working gate.

    The finding carries BOTH digests. G-09's mutation #2 asserts the pair is
    shown, and the reason is not cosmetic: "the model changed" is a claim a
    reader has to take on trust, while a recorded/actual pair is one they can
    reproduce with ``shasum -a 256``.
    """
    recorded = manifest.model.sha256
    actual = model_digest(model_path)
    if actual == recorded:
        return ()
    return (
        Finding(
            kind="model-digest-mismatch",
            target=Path(model_path).name,
            message=(
                f"the model moved and the code did not: {Path(model_path).name} "
                f"hashes to {actual[:12]}… now, and the manifest was written "
                f"against {recorded[:12]}…. Re-run `gnd codegen` to bring the "
                f"generated project back to the model"
            ),
            recorded_sha256=recorded,
            actual_sha256=actual,
        ),
    )
