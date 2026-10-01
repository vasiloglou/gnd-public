"""Filename slugging and traversal-safe output paths for model-derived names.

A generated population's filename is derived from UNTRUSTED model content — a
fact-type id, a model id, a class label — any of which may carry ``..``, an
absolute prefix, or a path separator (T-02-09). The traversal guard is NOT
re-derived here: :func:`safe_output_path` delegates to
:func:`gnd.install.safe_destination`, the exact guard ``gnd install`` bought
once (string-level rejection, resolved-parent containment, and a symlinked
parent-chain refusal). Importing it rather than re-writing it is deliberate — a
second copy of a security guard is how the two drift apart.

:func:`slug` is the reduction that keeps a model-derived token from EVER reaching
the guard as an escape in the first place: it collapses everything outside
``[a-z0-9._-]`` to ``-`` and strips leading dots, so a hostile id becomes an
inert filename component. The guard remains the backstop for the assembled
relative path; slug is the front-line normaliser for a single segment.
"""

from __future__ import annotations

import re
from pathlib import Path

from gnd.install import safe_destination

__all__ = ["safe_output_path", "slug"]

#: Everything that is NOT a safe filename character collapses to a single dash.
_UNSAFE = re.compile(r"[^a-z0-9._-]+")
#: Leading dots (``.`` / ``..``) are stripped so a slugged segment can never be a
#: relative-parent reference or a hidden file.
_LEADING_DOTS = re.compile(r"^\.+")


def slug(text: str) -> str:
    """Reduce a model-derived identifier to a safe single filename segment.

    Lower-cased, non-``[a-z0-9._-]`` runs collapsed to ``-``, leading dots
    stripped, and a non-empty fallback so a token that reduces to nothing still
    yields a usable component. This is a NORMALISER, not the security boundary —
    :func:`safe_output_path` is the boundary, and it runs on the assembled path.
    """
    lowered = str(text).strip().lower()
    collapsed = _UNSAFE.sub("-", lowered)
    stripped = _LEADING_DOTS.sub("", collapsed).strip("-")
    return stripped or "x"


def safe_output_path(root: str | Path, relpath: str) -> Path:
    """The destination ``root / relpath`` under the output root, or raise.

    Delegates to :func:`gnd.install.safe_destination`
    (:class:`gnd.install.InstallPathError` on refusal) so the generator reuses
    the checked traversal guard rather than re-deriving it. ``relpath`` is a
    POSIX-style relative path built from already-:func:`slug`-ged segments; the
    guard is the backstop that refuses an escape even if a caller forgets to
    slug.
    """
    return safe_destination(Path(root), relpath)
