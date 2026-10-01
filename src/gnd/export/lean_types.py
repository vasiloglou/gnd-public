"""Bounded finite-model export claims, separate from checking and proof."""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class LeanLimits:
    document_bytes: int = 10485760
    bundle_bytes: int = 41943040
    container_depth: int = 64
    object_types: int = 128
    fact_types: int = 256
    roles: int = 16
    clauses: int = 1024
    constraints: int = 1024
    carrier_values: int = 4096
    input_rows: int = 100000
    scalar_bytes: int = 4096
    numeric_digits: int = 128
    emission_visits: int = 1000000
    native_output_bytes: int = 10485760
    native_seconds: int = 30


DEFAULT_LIMITS = LeanLimits()


def checked_limits(limits):
    if not isinstance(limits, LeanLimits) or any(
        type(v) is not int or not 1 <= v <= getattr(DEFAULT_LIMITS, k)
        for k, v in vars(limits).items()
    ):
        raise ValueError("invalid ceilings")
    return limits


@dataclass
class LeanResult:
    exit_code: int = 0
    reason: str | None = None
    status: str = "exported"
    counts: dict = field(
        default_factory=lambda: dict.fromkeys(
            (
                "object_types",
                "fact_types",
                "clauses",
                "constraints",
                "carrier_values",
                "input_rows",
                "emission_visits",
            ),
            0,
        )
    )
    files: dict = field(default_factory=dict)
    native: dict = field(default_factory=dict)

    def model_dump(self, *, mode="json"):
        return dict(
            version=1,
            kind="lean-compile-result" if self.native else "lean-export-result",
            exit_code=self.exit_code,
            status=self.status,
            reason=self.reason,
            assurance="none",
            proof_status="unproved",
            counts=self.counts,
            **self.native,
        )


def refused(code=3, reason="input-invalid"):
    return LeanResult(
        code, reason, {2: "unsupported", 3: "input-refused", 4: "resource-refused"}[code]
    )
