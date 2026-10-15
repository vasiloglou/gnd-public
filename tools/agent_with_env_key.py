"""Run a terminal agent with exactly one credential imported from an env file.

The declared command adapter hands an agent only an allowlisted, credential-free
environment, and a standalone CLI with no login of its own cannot work there.
This wrapper reads the named key from a trusted env file as DATA (no shell is
sourced, nothing is printed), puts that one variable in the child's environment
and replaces itself with the agent process. Everything after ``--`` is the agent
command line.

    python tools/agent_with_env_key.py --env-file .env --name ANTHROPIC_API_KEY -- claude --print ...
"""
from __future__ import annotations

import argparse
import os
import shutil
from pathlib import Path

MAX_ENV_BYTES = 64 * 1024


def read_key(env_file: Path, name: str) -> str:
    with env_file.open('rb') as handle:
        raw = handle.read(MAX_ENV_BYTES + 1)
    if len(raw) > MAX_ENV_BYTES:
        raise SystemExit(f'{env_file}: larger than {MAX_ENV_BYTES} bytes; refusing')
    for line in raw.decode('utf-8', errors='replace').splitlines():
        stripped = line.strip()
        if stripped.startswith('export '):
            stripped = stripped[len('export '):].lstrip()
        key, separator, value = stripped.partition('=')
        if separator and key.strip() == name:
            value = value.strip()
            if len(value) >= 2 and value[0] == value[-1] and value[0] in '"\'':
                value = value[1:-1]
            if not value:
                raise SystemExit(f'{name} is empty in {env_file}')
            return value
    raise SystemExit(f'{name} is not set in {env_file}')


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--env-file', required=True, type=Path)
    parser.add_argument('--name', required=True, help='the one variable to import')
    parser.add_argument('command', nargs=argparse.REMAINDER, help='-- agent argv')
    args = parser.parse_args()
    command = args.command[1:] if args.command[:1] == ['--'] else args.command
    if not command:
        parser.error('no agent command given after --')
    executable = shutil.which(command[0])
    if executable is None:
        parser.error(f'{command[0]} is not on PATH')
    environment = dict(os.environ)
    if command[1:] != ['--version']:  # the adapter's version probe never needs the credential
        environment[args.name] = read_key(args.env_file, args.name)
    os.execve(executable, [executable, *command[1:]], environment)
    return 70  # unreachable


if __name__ == '__main__':
    raise SystemExit(main())
