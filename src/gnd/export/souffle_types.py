"""Separate bounded Souffle derivation claims; no constraint verdict."""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class SouffleLimits:
    document_bytes: int = 10485760
    bundle_bytes: int = 41943040
    container_depth: int = 64
    fact_types: int = 256
    roles: int = 64
    clauses: int = 1024
    atom_sites: int = 4096
    input_rows: int = 100000
    encoded_cells: int = 400000
    scalar_bytes: int = 4096
    numeric_digits: int = 128
    emission_visits: int = 1000000
    native_output_bytes: int = 10485760
    native_rows: int = 100000
    native_seconds: int = 30


DEFAULT_LIMITS = SouffleLimits()


def checked_limits(limits):
    if not isinstance(limits, SouffleLimits) or any(
        type(v) is not int or not 1 <= v <= getattr(DEFAULT_LIMITS, k)
        for k, v in vars(limits).items()
    ):
        raise ValueError("invalid ceilings")
    return limits


@dataclass
class ExportResult:
    exit_code: int = 0
    reason: str | None = None
    status: str = "exported"
    counts: dict = field(
        default_factory=lambda: dict.fromkeys(
            ("fact_types", "clauses", "input_rows", "encoded_cells", "emission_visits"), 0
        )
    )
    files: dict = field(default_factory=dict)

    def model_dump(self, *, mode="json"):
        return {
            "version": 1,
            "kind": "souffle-export-result",
            "exit_code": self.exit_code,
            "status": self.status,
            "reason": self.reason,
            "assurance": "none",
            "counts": self.counts,
        }


def refused(code=3, reason="input-invalid"):
    return ExportResult(
        code, reason, {2: "unsupported", 3: "input-refused", 4: "resource-refused"}[code]
    )
