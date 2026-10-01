"""Immutable limits and the separate finite-witness claim envelope."""

from dataclasses import dataclass


class WitnessInputError(ValueError):
    """Untrusted input did not enter the witness lane."""


class WitnessWorkError(ValueError):
    """The finite work ceiling was reached; no domain falsity is implied."""


@dataclass(frozen=True)
class WitnessLimits:
    bytes: int = 10 * 1024 * 1024
    container_depth: int = 64
    targets: int = 256
    nodes: int = 10000
    edges: int = 40000
    binding_cells: int = 100000
    joins: int = 100000
    proof_depth: int = 128
    scalar_bytes: int = 4096
    numeric_digits: int = 128
    expanded_visits: int = 20000


DEFAULT_LIMITS = WitnessLimits()


def checked_limits(limits: WitnessLimits) -> WitnessLimits:
    if not isinstance(limits, WitnessLimits) or any(
        type(value) is not int or value < 1 or value > getattr(DEFAULT_LIMITS, key)
        for key, value in vars(limits).items()
    ):
        raise WitnessInputError("limits cannot raise the fixed ceilings")
    return limits


@dataclass(frozen=True)
class WitnessResult:
    exit_code: int
    results: tuple[dict, ...] = ()
    certificate: dict | None = None
    reason: str | None = None
    work: dict | None = None

    def model_dump(self, *, mode: str = "json") -> dict:
        return {
            "exit_code": self.exit_code,
            "results": list(self.results),
            "certificate": self.certificate,
            "reason": self.reason,
            "work": self.work or {},
        }


STATUS = {
    "proved": (0, None),
    "missing": (2, "target-missing"),
    "unknown": (2, "value-unknown"),
    "unsupported": (2, "fragment-unsupported"),
    "invalid": (1, "proof-invalid"),
    "input-refused": (3, "input-invalid"),
    "resource-refused": (4, "work-limit"),
}


def result_rows(targets, status, *, roots=None):
    return tuple(
        {
            "request_index": i,
            "target": t,
            "status": status,
            "reason": STATUS[status][1],
            "root": roots[i] if roots is not None else None,
        }
        for i, t in enumerate(targets)
    )


def reduce_results(rows, *, certificate=None, work=None):
    codes = {STATUS[r["status"]][0] for r in rows}
    code = next((n for n in (3, 4, 1, 2, 0) if n in codes), 3)
    return WitnessResult(code, tuple(rows), certificate, None, work)
