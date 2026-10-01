"""The evidence-path validator — G-13′'s two-function fix (plan 03-01).

An evidence pointer in ``CONCLUSIONS.md`` is an attacker-influenceable path in
untrusted committed metadata, and it is what makes a recorded conclusion
checkable. So it is accepted only when it is, in this order:

1. **non-empty** after stripping — checked lexically, before any filesystem call;
2. **lexically relative** under BOTH POSIX and Windows rules, with no ``..``
   component under either flavour;
3. **contained** in the experiment directory once resolved;
4. **symlink-free** in every component;
5. an **existing FILE** — ``is_file()``, never ``.exists()``.

Steps 2-4 are not one check written twice. RESEARCH §6.2 probed the shipped
``resolve_manifest_relative_path`` over ten inputs and **partly refuted G-13**:
it delivers containment (3) and symlink refusal (4), but it does NOT deliver the
lexical rejection (2) — a Windows-absolute pointer is an ordinary relative name
to POSIX ``Path``, so ``C:\\evil`` resolves to ``<experiment-dir>/C:\\evil`` and
is ACCEPTED. The lexical half lives in
:func:`~gnd.extract.manifest.manifest_path_issue`, which plan 03-01 made public
for exactly this reason: one implementation of the lexical rules, so a future
correction cannot land in one lane and miss the other.

Steps 1 and 5 are RESEARCH §6.3's two reproduced gate-cannot-fail vectors, both
produced by writing step 5 as ``.exists()``: ``evidence: ""`` resolves to the
experiment directory, which exists, and ``evidence: sub`` names a directory,
which also exists. Either one lets a conclusion with no citation at all pass as
cited — the gate would ship unable to fail. They are refused twice over here (1
lexically, 5 structurally), and that redundancy is deliberate defense in depth
rather than an accident: removing either guard alone leaves ``""`` refused.
"""

from __future__ import annotations

from pathlib import Path

from gnd.extract.manifest import (
    ManifestError,
    manifest_path_issue,
    resolve_manifest_relative_path,
)
from gnd.model import ValidationIssue

__all__ = [
    "EVIDENCE_RULE_ID",
    "EvidencePathError",
    "evidence_path_issue",
    "resolve_evidence_path",
    "resolve_experiment_directory",
]

#: The rule id every issue from this module carries, so the CLI maps refusals
#: into its output without re-deriving messages.
EVIDENCE_RULE_ID = "experiment:evidence-unresolvable"


class EvidencePathError(Exception):
    """An evidence pointer was empty, unsafe, uncontained, or named no file.

    Carries ``issues`` (:class:`~gnd.model.ValidationIssue` records) so the
    experiment CLI reports the refusal verbatim rather than re-deriving a
    message — the ``ManifestError`` contract, for the same reason.
    """

    def __init__(self, message: str, issues: list[ValidationIssue] | None = None):
        super().__init__(message)
        self.issues: list[ValidationIssue] = issues or [
            ValidationIssue(path="", message=message, rule_id=EVIDENCE_RULE_ID)
        ]


def evidence_path_issue(
    field: str, value: str, rule_id: str = EVIDENCE_RULE_ID
) -> ValidationIssue | None:
    """The LEXICAL half: an issue when ``value`` is empty or not safely relative.

    Pure — it takes no directory and touches no filesystem, so a refusal from
    here is provably reached before any path is resolved. Existence is not its
    business: a legal-looking pointer to a missing file returns ``None`` and is
    refused later, by :func:`resolve_evidence_path`.
    """
    if not value.strip():
        return ValidationIssue(
            path=field,
            message=(
                f"{field} is empty ({value!r}); an empty evidence pointer resolves "
                f"to the experiment directory ITSELF, which exists — so a "
                f"conclusion citing nothing would pass as cited (RESEARCH §6.3)"
            ),
            rule_id=rule_id,
        )
    # ``.`` is lexically contained and intentionally reaches the shape check
    # in ``resolve_evidence_path``. That check can then report the precise
    # error: a directory exists, but is not citable file evidence.
    if value.strip() == ".":
        return None
    return manifest_path_issue(field, value, rule_id)


def resolve_evidence_path(
    spec_path: str | Path,
    value: str,
    *,
    field: str = "evidence",
    rule_id: str = EVIDENCE_RULE_ID,
) -> Path:
    """The resolved evidence file, or raise :class:`EvidencePathError`.

    ``value`` resolves against ``spec_path``'s own directory — the experiment
    directory. Applies :func:`evidence_path_issue` first (nothing touches the
    filesystem until it returns ``None``), then the shipped containment and
    symlink loop, then ``is_file()``.

    Every refusal message names the offending FIELD and VALUE. A message that
    named only the resolved path would make a mutation check unable to tell a
    test that reds for the right reason from one that reds for any reason
    (RESEARCH Common Pitfall 1).
    """
    issue = evidence_path_issue(field, value, rule_id)
    if issue is not None:
        raise EvidencePathError(f"{field} {value!r}: {issue.message}", [issue])

    if value.strip() == ".":
        resolved = Path(spec_path).resolve().parent
    else:
        try:
            resolved = resolve_manifest_relative_path(
                spec_path, value, field=field, rule_id=rule_id
            )
        except ManifestError as error:
            message = (
                f"{field} {value!r} could not be resolved safely inside the "
                f"experiment directory: {error}"
            )
            raise EvidencePathError(
                message,
                [ValidationIssue(path=field, message=message, rule_id=rule_id)],
            ) from error

    # ONE acceptance gate, and it is is_file(). The directory/missing split below
    # only chooses the wording — putting an is_dir() branch ABOVE this line would
    # make `.exists()` here indistinguishable from `is_file()` in behaviour, and
    # the recorded mutation (replace is_file with exists) would stop reding.
    if not resolved.is_file():
        if resolved.is_dir():
            message = (
                f"{field} {value!r} names a directory ({resolved}); evidence must "
                f"be a FILE — a directory satisfies .exists() and would let a "
                f"conclusion with no citable artifact pass as cited (RESEARCH §6.3)"
            )
        else:
            message = (
                f"{field} {value!r} does not exist ({resolved}); the cited evidence "
                f"must be present in the experiment, or the citation is unverifiable"
            )
        raise EvidencePathError(
            message,
            [ValidationIssue(path=field, message=message, rule_id=rule_id)],
        )
    return resolved


def resolve_experiment_directory(
    spec_path: str | Path,
    value: str,
    *,
    field: str,
    rule_id: str = EVIDENCE_RULE_ID,
) -> Path:
    """Resolve a symlink-free directory named by experiment metadata.

    Codegen experiments bind their live conformance check to a generated
    project directory.  The lexical, containment, and symlink rules are the
    same as for evidence files; only the final shape differs.
    """
    issue = evidence_path_issue(field, value, rule_id)
    if issue is not None:
        raise EvidencePathError(f"{field} {value!r}: {issue.message}", [issue])

    try:
        resolved = resolve_manifest_relative_path(
            spec_path, value, field=field, rule_id=rule_id
        )
    except ManifestError as error:
        message = (
            f"{field} {value!r} could not be resolved safely inside the experiment "
            f"directory: {error}"
        )
        raise EvidencePathError(
            message,
            [ValidationIssue(path=field, message=message, rule_id=rule_id)],
        ) from error

    if not resolved.is_dir():
        shape = "a file" if resolved.is_file() else "missing"
        message = (
            f"{field} {value!r} is {shape} ({resolved}); the live conformance "
            f"subject must be an existing directory inside the experiment"
        )
        raise EvidencePathError(
            message,
            [ValidationIssue(path=field, message=message, rule_id=rule_id)],
        )
    return resolved
