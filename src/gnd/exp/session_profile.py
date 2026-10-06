"""Immutable session capabilities, separate from every wire schema."""
from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

from gnd.payloads import DERIVATION_PAYLOAD_SCHEMA_VERSIONS

JUDGMENT_SESSION_CONTRACT_VERSION = 8


@dataclass(frozen=True, slots=True)
class SessionProfile:
    contract_version: int
    legacy: bool = False
    tests: bool = False
    walk: bool = False
    declared_adapter: bool = False
    patch: bool = False
    judgments: bool = False
    launch_version: int | None = None
    feedback_version: int | None = None
    attempt_version: int | None = None
    result_version: int | None = None

    def select_feedback(self, *, walk: bool, redaction: bool, transition: bool,
                        payload_versions: Iterable[int]) -> int:
        """Preserve the legacy controller's wire precedence."""
        versions = tuple(payload_versions)
        return (7 if walk else 6 if redaction else 5 if transition else 4
                if 7 in versions else 3
                if any(v in DERIVATION_PAYLOAD_SCHEMA_VERSIONS for v in versions) else 2)

    def select_result(self, *, walk: bool, redaction: bool, transition: bool) -> int:
        return 5 if walk else 4 if redaction else 3 if transition else 2


_PROFILES = (
    SessionProfile(1, legacy=True),
    SessionProfile(2),
    SessionProfile(3, tests=True),
    SessionProfile(4, tests=True),
    SessionProfile(5, tests=True, walk=True),
    SessionProfile(6, tests=True, walk=True, declared_adapter=True),
    SessionProfile(7, tests=True, walk=True, declared_adapter=True, patch=True,
                   launch_version=3, feedback_version=8, attempt_version=9, result_version=6),
    SessionProfile(JUDGMENT_SESSION_CONTRACT_VERSION, tests=True, walk=True,
                   declared_adapter=True, patch=True, judgments=True,
                   launch_version=4, feedback_version=9, attempt_version=10, result_version=7),
)


def profile_for_version(version: object) -> SessionProfile | None:
    """Keep the wire dispatcher's equality semantics and handle arbitrary JSON."""
    for profile in _PROFILES:
        if version == profile.contract_version:
            return profile
    return None
