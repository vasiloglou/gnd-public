"""RF3 shared dependency home; algorithms retain predecessor semantics."""
from __future__ import annotations

from gnd.errors import ValidationIssue


def manifest_path_issue(field: str, value: str, rule_id: str) -> ValidationIssue | None:
    """An issue when ``value`` is not a safe, non-empty relative path.

    Checked under BOTH path flavours: a Windows-absolute entry
    (``C:\\evil``) is not absolute to POSIX ``Path`` and vice versa, and this
    file is a committed artifact that crosses machines.

    PUBLIC since plan 03-01 (was ``_path_issue``, absent from ``__all__``).
    Phase 3 research probed :func:`resolve_manifest_relative_path` over ten
    inputs and found it gives containment and symlink refusal but NOT this
    lexical check — it resolves ``C:\\evil`` to ``<dir>/C:\\evil`` and accepts
    it. ``gnd.exp.paths`` needs both halves, and exporting this one keeps a
    single implementation of the lexical rules: a future correction here cannot
    land in one lane and miss the other.
    """
    from gnd.install import InstallPathError, _reject_unsafe_relpath

    try:
        _reject_unsafe_relpath(value, source=f"{field} in manifest")
    except InstallPathError as error:
        return ValidationIssue(
            path=field,
            message=str(error),
            rule_id=rule_id,
        )
    return None


manifest_path_issue.__module__ = 'gnd.extract.manifest'
