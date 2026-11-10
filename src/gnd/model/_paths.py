"""Historical confined reference paths and retained roots; shared by includes."""
from __future__ import annotations

import os
import re
import stat
from contextlib import contextmanager
from pathlib import Path

from gnd.errors import ReferenceInputError


def _relative(path: object) -> str:
    if not isinstance(path, str) or not path or len(path) > 4096:
        raise ReferenceInputError("reference path is empty or exceeds 4096 characters")
    parts = path.split("/")
    if len(parts) > 32 or any(p in {"", ".", ".."} for p in parts):
        raise ReferenceInputError(
            "reference path must have at most 32 nonempty relative components"
        )
    if "\\" in path or "\x00" in path or re.match(r"^[A-Za-z]:", path):
        raise ReferenceInputError("reference path is not a confined POSIX relative path")
    return path


@contextmanager
def retained_root(root: str | Path):
    """Open every lexical ancestor without following a symlink."""
    if not hasattr(os, "O_NOFOLLOW") or not hasattr(os, "O_DIRECTORY"):
        raise ReferenceInputError("safe reference descriptor traversal is unavailable")
    absolute = Path(root)
    if not absolute.is_absolute():
        absolute = Path.cwd() / absolute
    descriptor = os.open(absolute.anchor, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        for part in absolute.parts[1:]:
            next_fd = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=descriptor)
            os.close(descriptor)
            descriptor = next_fd
        yield descriptor
    finally:
        os.close(descriptor)


def historical_path_at(descriptor: int, relative: str) -> None:
    """Check existing path parts without following links; authenticated history permits absence."""
    parts = _relative(relative).split('/')
    current = os.dup(descriptor)
    try:
        for index, part in enumerate(parts):
            try:
                observed = os.stat(part, dir_fd=current, follow_symlinks=False)
            except FileNotFoundError:
                return
            leaf = index == len(parts) - 1
            if not (stat.S_ISREG(observed.st_mode) if leaf else stat.S_ISDIR(observed.st_mode)):
                raise ReferenceInputError("unsafe historical include path")
            if not leaf:
                next_fd = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=current)
                os.close(current)
                current = next_fd
    finally:
        os.close(current)

_relative.__module__ = "gnd.model"
retained_root.__module__ = "gnd.model"
