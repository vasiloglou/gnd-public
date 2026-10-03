from __future__ import annotations

import json
import math
import os
import shutil
import signal
import subprocess
import tempfile
from pathlib import Path
from typing import Any

from gnd.model import load_model
from gnd.popvalidate import resolve_primitive

REPO_ROOT = Path(__file__).resolve().parents[2]
CORPUS = REPO_ROOT / 'tests' / 'fixtures' / 'derivation-evaluation'
PYREL_VERSION = '1.30.1'
PYREL_OUTPUT_LIMIT = 4 * 1024 * 1024

def _bounded_command(argv: list[str], *, timeout: int, env: dict[str, str] | None=None) -> subprocess.CompletedProcess[str]:
    """Run one foreign seat command and kill its whole process group on timeout."""
    process = subprocess.Popen(argv, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=env, start_new_session=True)
    try:
        stdout, stderr = process.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        os.killpg(process.pid, signal.SIGKILL)
        process.communicate()
        raise
    return subprocess.CompletedProcess(argv, process.returncode, stdout, stderr)

def _pyrel_json_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    """Reject duplicate keys before JSON decoding can discard their evidence."""
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f'PyRel output repeats JSON key {key!r}')
        result[key] = value
    return result

def _pyrel_validate_token(token: Any, primitive: str | None) -> None:
    assert isinstance(token, str), 'PyRel identity token must be a JSON string'
    value = json.loads(token, object_pairs_hook=_pyrel_json_object)
    if not isinstance(value, list) or len(value) != 2:
        raise ValueError('PyRel identity token must contain a tag and payload')
    tag, payload = value
    valid = False
    if tag == 'string':
        valid = isinstance(payload, str)
    elif tag == 'boolean':
        valid = isinstance(payload, bool)
    elif tag == 'number':
        valid = isinstance(payload, list) and len(payload) == 2 and all(type(part) is int for part in payload) and (payload[1] > 0) and (math.gcd(*payload) == 1)
    if not valid:
        raise ValueError('PyRel identity token has an invalid tag or payload')
    expected_tag = 'boolean' if primitive == 'Boolean' else 'number' if primitive in {'Integer', 'Float', 'Number'} else 'string' if primitive in {'String', 'Date', 'DateTime', 'Binary'} else None
    if expected_tag is not None and tag != expected_tag:
        raise ValueError(f'PyRel identity token tag {tag!r} is not valid for {primitive}')
    if token != json.dumps(value, ensure_ascii=False, separators=(',', ':')):
        raise ValueError('PyRel identity token is not canonical JSON')

def _pyrel_extensions(model: Path, population: Path, *, executable: str | None=None) -> dict[str, tuple[tuple[str, ...], ...]]:
    """Run the isolated foreign seat on raw inputs, then validate its output."""
    executable = executable or shutil.which('uv')
    if executable is None:
        raise RuntimeError('uv executable absent; PyRel derivation seat unavailable')
    script = REPO_ROOT / 'tests' / 'oracles' / 'pyrel_derivation_oracle.py'
    with tempfile.TemporaryDirectory(prefix='gnd-pyrel-derivation-') as directory:
        scratch = Path(directory)
        output = scratch / 'result.json'
        process = _bounded_command([executable, 'run', '--locked', '--script', str(script), str(model), str(population), '--out', str(output)], timeout=120, env={**os.environ, 'RAI_BUILD_DIR': str(scratch / 'build')})
        if process.returncode != 0:
            raise RuntimeError(f'PyRel derivation process exited {process.returncode}: {process.stderr}')
        with output.open('rb') as stream:
            raw = stream.read(PYREL_OUTPUT_LIMIT + 1)
        if len(raw) > PYREL_OUTPUT_LIMIT:
            raise ValueError('PyRel derivation output exceeds the 4 MiB read limit')
        document = json.loads(raw.decode('utf-8'), object_pairs_hook=_pyrel_json_object)
    if not isinstance(document, dict) or set(document) != {'schema_version', 'backend', 'version', 'extensions'}:
        raise ValueError('PyRel derivation output has an invalid envelope')
    if type(document['schema_version']) is not int or document['schema_version'] != 1:
        raise ValueError('PyRel derivation output requires schema_version 1')
    if document['backend'] != 'pyrel' or document['version'] != PYREL_VERSION:
        raise ValueError('PyRel derivation output has the wrong backend or package version')
    loaded_model = load_model(model)
    heads = {str(fact['id']): tuple(resolve_primitive(str(role['object_type']), loaded_model) for role in fact['roles']) for fact in loaded_model.fact_types if isinstance(fact.get('derivation_rule'), dict)}
    extensions = document['extensions']
    if not isinstance(extensions, dict) or set(extensions) != set(heads):
        raise ValueError('PyRel derivation output has missing or unexpected heads')
    result: dict[str, tuple[tuple[str, ...], ...]] = {}
    for head, primitives in heads.items():
        rows = extensions[head]
        assert isinstance(rows, list), f'PyRel head {head} rows must be an array'
        checked = []
        for row in rows:
            if not isinstance(row, list) or len(row) != len(primitives):
                raise ValueError(f'PyRel head {head} row has wrong shape or arity')
            for token, primitive in zip(row, primitives, strict=True):
                _pyrel_validate_token(token, primitive)
            checked.append(tuple(row))
        if len(checked) != len(set(checked)):
            raise ValueError(f'PyRel head {head} contains duplicate rows')
        if checked != sorted(checked):
            raise ValueError(f'PyRel head {head} rows are not in canonical order')
        result[head] = tuple(checked)
    return result
