"""Shared verifier environment allowlist."""
from __future__ import annotations

import os


def verifier_environment() -> dict[str, str]:
    """Return the live environment allowlist shared by verifier processes."""

    return {
        name: os.environ[name]
        for name in ("PATH", "HOME", "TMPDIR", "LANG", "LC_ALL", "SSL_CERT_FILE")
        if name in os.environ
    }




# Preserve the historical public qualification of moved objects.
verifier_environment.__module__ = "gnd.exp.session"
