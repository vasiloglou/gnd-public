from __future__ import annotations

import asyncio
import os
from pathlib import Path

import pytest

from gnd.agent_cli import ProcessLimits, run_bounded_process
from gnd.review import adapters as review_adapters
from gnd.review.adapters import (
    ReviewerPolicy,
    resolve_reviewer_policies,
    reviewer_policies,
    sanitized_reviewer_environment,
)

REPO_ROOT = Path(__file__).resolve().parents[1]

@pytest.mark.network
@pytest.mark.parametrize("policy", reviewer_policies(), ids=lambda item: item.reviewer_id.value)
def test_installed_cli_help_accepts_fixed_invocation_surface(policy: ReviewerPolicy) -> None:
    """Opt-in, zero-prompt smoke: one real help probe and one surface check."""

    environment = sanitized_reviewer_environment(dict(os.environ))
    resolved = next(
        item
        for item in resolve_reviewer_policies(environment)
        if item.policy.reviewer_id == policy.reviewer_id
    )
    if resolved.executable is None:
        pytest.skip(f"{policy.executable_name} is not installed")
    result = asyncio.run(
        run_bounded_process(
            (resolved.executable, *policy.capability_argv),
            cwd=REPO_ROOT,
            env=environment,
            limits=ProcessLimits(
                timeout_seconds=15.0,
                terminate_grace_seconds=0.5,
                stdin_limit_bytes=0,
                stdout_limit_bytes=1024 * 1024,
                stderr_limit_bytes=1024 * 1024,
                total_output_limit_bytes=2 * 1024 * 1024,
            ),
        )
    )

    assert review_adapters._capability_is_proven(policy, result)
