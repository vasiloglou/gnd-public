"""Bounded native proposals followed by independent, exact-byte acceptance."""
from __future__ import annotations

import asyncio
import hashlib
import json
import os
import re
import tempfile
from collections import Counter
from pathlib import Path

from gnd.errors import ModelLoadError, ModelValidationError
from gnd.json_input import bounded_json
from gnd.model import load_model_bytes
from gnd.process import ProcessLimits, run_bounded_process
from gnd.safefs import artifact_publish_leaf_atomic, artifact_read_regular_bounded

from .emit import render_pyrel
from .pyrel_runtime import _constraint_entries, _parse_document, admit_model, admit_population

INPUT_CAP = 1_048_576
ARTIFACT_CAP = 4_194_304
LIMITS = ProcessLimits(timeout_seconds=60, terminate_grace_seconds=2,
                       stdin_limit_bytes=0, stdout_limit_bytes=INPUT_CAP,
                       stderr_limit_bytes=INPUT_CAP, total_output_limit_bytes=2 * INPUT_CAP)


def verify_policy_report(report, model_doc, model_sha, population_sha, process_exit):
    """Refuse missing, forged, partial or unsuccessful acceptance evidence."""
    if not isinstance(report, dict):
        raise ValueError('policy report must be an object')  # noqa: TRY004 -- one refusal protocol
    if (type(report.get('schema_version')) is not int or report['schema_version'] != 1
            or report.get('profile') != 'applications-v1'
            or report.get('backend') != 'duckdb-local'
            or report.get('accepted') is not True
            or type(report.get('exit_code')) is not int or report['exit_code'] != 0
            or type(process_exit) is not int or process_exit != 0
            or report.get('binding') != {'model_sha256': model_sha, 'population_sha256': population_sha}):
        raise ValueError('unsuccessful or misbound policy report')
    index = admit_model(model_doc)
    expected = {ref: (c.get('id', ref), c['type'], c.get('modality', 'alethic'))
                for ref, c, _ in _constraint_entries(index)}
    verdicts = report.get('verdicts')
    heads = report.get('derivations')
    if not isinstance(verdicts, list) or not isinstance(heads, list):
        raise ValueError('missing policy inventories')  # noqa: TRY004
    seen = set()
    warnings = False
    for row in verdicts:
        if not isinstance(row, dict):
            raise ValueError('malformed verdict')  # noqa: TRY004
        ref = row.get('constraint_ref')
        if not isinstance(ref, str) or ref in seen or ref not in expected:
            raise ValueError('unexpected or duplicate obligation')
        seen.add(ref)
        identity = (row.get('id'), row.get('constraint_type'), row.get('modality'))
        if (identity != expected[ref] or not isinstance(row.get('status'), str)
                or row['status'] not in {'satisfied', 'warning'}):
            raise ValueError('unsuccessful or misidentified obligation')
        if not isinstance(row.get('witnesses'), list) or 'reason' not in row or row['reason'] is not None:
            raise ValueError('malformed obligation evidence')
        if row['status'] == 'warning':
            if row['modality'] != 'deontic' or not row['witnesses']:
                raise ValueError('warning requires a deontic witness')
            warnings = True
        elif row['witnesses']:
            raise ValueError('satisfied obligation has violation witnesses')
    if seen != set(expected):
        raise ValueError('incomplete obligation inventory')
    expected_heads = {'derivation:' + name: name for name, fact in index.fact_types.items()
                      if fact.get('derivation') not in (None, 'asserted') or 'derivation_rule' in fact}
    seen = set()
    for row in heads:
        if not isinstance(row, dict):
            raise ValueError('malformed derivation')  # noqa: TRY004
        ref = row.get('derivation_ref')
        if (not isinstance(ref, str) or ref in seen or ref not in expected_heads
                or row.get('fact_type') != expected_heads[ref] or row.get('status') != 'satisfied'
                or not isinstance(row.get('computed'), list)
                or row.get('missing') != [] or row.get('extra') != []
                or 'reason' not in row or row['reason'] is not None):
            raise ValueError('unsuccessful or misidentified derivation')
        seen.add(ref)
        admit_population({'facts': {row['fact_type']: row['computed']}}, index)
    if seen != set(expected_heads):
        raise ValueError('incomplete derivation inventory')
    if report.get('status') != ('accepted_with_warnings' if warnings else 'accepted'):
        raise ValueError('inconsistent acceptance composition')


def _capture(path, cap):
    path = Path(path).absolute()
    return artifact_read_regular_bounded(path.parent, path.name, max_bytes=cap)[0]


def _child(argv, home):
    env = {key: value for key, value in os.environ.items()
           if key in {'PATH', 'LANG', 'LC_ALL', 'LC_CTYPE', 'TMPDIR', 'TEMP', 'TMP', 'SystemRoot'}}
    env['RAI_BUILD_DIR'] = str(home / 'build')
    result = asyncio.run(run_bounded_process(tuple(map(str, argv)), cwd=home, env=env, limits=LIMITS))
    if (result.status not in {'succeeded', 'failed'} or result.timed_out
            or result.stdout_truncated or result.stderr_truncated or not result.process_group_cleaned):
        raise RuntimeError('native process lifecycle refused: ' + result.status)
    return result


def _preserve_source(model_doc, source, candidate, owned_relations):
    index = admit_model(model_doc)
    facts = index.fact_types
    heads = {name for name, fact in facts.items()
             if fact.get('derivation') not in (None, 'asserted') or 'derivation_rule' in fact}
    if (not isinstance(owned_relations, (tuple, list))
            or any(not isinstance(name, str) for name in owned_relations)
            or len(set(owned_relations)) != len(owned_relations)
            or not set(owned_relations) <= set(facts) - heads):
        raise ValueError('owned relations must name distinct asserted facts')
    admit_population(source, index)
    if not isinstance(candidate, dict) or not isinstance(candidate.get('facts'), dict):
        raise ValueError('candidate facts must be an object')  # noqa: TRY004 -- application refusal
    if set(candidate['facts']) != set(source.get('facts', {})) | heads:
        raise ValueError('candidate changed source fact inventory')
    def counted(rows):
        if not isinstance(rows, list):
            raise ValueError('candidate fact rows must be a list')  # noqa: TRY004
        return Counter(json.dumps(row, sort_keys=True, allow_nan=False) for row in rows)
    for name, rows in source.get('facts', {}).items():
        if name not in set(owned_relations) | heads and counted(candidate['facts'][name]) != counted(rows):
            raise ValueError('candidate changed asserted source facts: ' + name)
    for document in (source, candidate):
        if not isinstance(document.get('population'), dict):
            raise ValueError('population metadata must be an object')  # noqa: TRY004
        if not isinstance(document['population'].get('covers'), list):
            raise ValueError('coverage must be a list')  # noqa: TRY004
    if (json.dumps({key: value for key, value in source.items() if key not in {'facts', 'population'}}, sort_keys=True)
            != json.dumps({key: value for key, value in candidate.items() if key not in {'facts', 'population'}}, sort_keys=True)
            or json.dumps({key: value for key, value in source['population'].items() if key != 'covers'}, sort_keys=True)
            != json.dumps({key: value for key, value in candidate['population'].items() if key != 'covers'}, sort_keys=True)):
        raise ValueError('candidate changed source instances or metadata')
    expected_covers = Counter(source['population']['covers'])
    expected_covers.update(heads - set(expected_covers))
    if Counter(candidate['population']['covers']) != expected_covers:
        raise ValueError('candidate changed asserted source coverage')


def _check_and_publish(result, *, interpreter, model_doc, model_sha, sources, runtime_bytes, candidate_bytes, output):
    """Check exact candidate bytes in a fresh stage; publish only verified acceptance."""
    model_bytes = sources[0][1]
    if len(candidate_bytes) > INPUT_CAP:
        raise ValueError('candidate exceeds native byte cap')
    # Create the checker stage only after any query group has exited.
    # Query-created paths/runtime/build artifacts cannot enter this run.
    with tempfile.TemporaryDirectory(prefix='gnd-native-checker-') as checked_directory:
        checked_home = Path(checked_directory)
        candidate = checked_home / 'candidate.json'
        policy_path = checked_home / 'policy.json'
        checked_runtime = checked_home / 'runtime.py'
        for name, data in [('candidate.json', candidate_bytes), ('runtime.py', runtime_bytes),
                           ('model.orm.yaml', model_bytes)]:
            artifact_publish_leaf_atomic(checked_home, name, data)
        checked = _child([interpreter, '-I', checked_runtime, candidate, '--accept', '--out', policy_path], checked_home)
        if checked.return_code == 3:
            result.update(exit_code=3, reason=checked.stderr.decode('utf-8', errors='replace')[-300:])
            return result
        report = bounded_json(_capture(policy_path, ARTIFACT_CAP), max_bytes=ARTIFACT_CAP)
    result['policy'] = report
    if checked.return_code != 0:
        result['exit_code'] = checked.return_code if checked.return_code in {1, 2, 3} else 70
        return result
    verify_policy_report(report, model_doc, model_sha,
                         hashlib.sha256(candidate_bytes).hexdigest(), checked.return_code)
    if any(_capture(path, INPUT_CAP) != data for path, data in sources):
        raise RuntimeError('source bytes changed during native execution')
    artifact_publish_leaf_atomic(output.parent, output.name, candidate_bytes)
    result.update(exit_code=0, accepted=True, published=True)
    return result


def execute_application(model_path, input_path, output_path, *, native_python, query_script,
                        query_args=(), candidate_transform=None, owned_relations=(), allowed_guard_kinds=()):
    """Only captured candidate bytes with complete native acceptance are published."""
    result = {'exit_code': 70, 'accepted': False, 'published': False,
              'policy': None, 'calculation': None}
    try:
        if (not isinstance(allowed_guard_kinds, (tuple, list)) or len(allowed_guard_kinds) > 16
                or any(not isinstance(kind, str) or re.fullmatch('[a-z][a-z0-9-]{0,63}', kind) is None
                       for kind in allowed_guard_kinds)
                or len(set(allowed_guard_kinds)) != len(allowed_guard_kinds)):
            raise ValueError('guard kinds must be distinct bounded declarations')
        output = Path(output_path).absolute()
        if output.exists() or output.is_symlink():
            result.update(exit_code=2, reason='output already exists')
            return result
        interpreter = Path(native_python)
        if not interpreter.is_absolute() or not interpreter.is_file():
            raise RuntimeError('explicit native interpreter is unavailable')
        model_bytes = _capture(model_path, INPUT_CAP)
        input_bytes = _capture(input_path, INPUT_CAP)
        load_model_bytes(model_bytes, source=model_path)
        model_doc = _parse_document(model_bytes.decode('utf-8'))
        model_sha = hashlib.sha256(model_bytes).hexdigest()
        input_sha = hashlib.sha256(input_bytes).hexdigest()
        result['source_binding'] = {'model_sha256': model_sha, 'input_sha256': input_sha}
        # Capture the owned query too: neither child can change later source reads.
        query_bytes = _capture(query_script, INPUT_CAP)
        with tempfile.TemporaryDirectory(prefix='gnd-native-application-') as directory:
            home = Path(directory)
            model = home / 'model.orm.yaml'
            seed = home / 'seed.json'
            runtime = home / 'runtime.py'
            query = home / 'query.py'
            proposal = home / 'proposal.json'
            model.write_bytes(model_bytes)
            seed.write_bytes(input_bytes)
            runtime_bytes = render_pyrel(model).encode('utf-8')
            runtime.write_bytes(runtime_bytes)
            query.write_bytes(query_bytes)
            child = _child([interpreter, '-I', query, runtime, seed, proposal, *query_args], home)
            if child.return_code != 0:
                result.update(exit_code=child.return_code if child.return_code in {2, 3} else 70,
                              reason=child.stderr.decode('utf-8', errors='replace')[-300:])
                return result
            envelope = bounded_json(_capture(proposal, ARTIFACT_CAP), max_bytes=ARTIFACT_CAP)
            if (not isinstance(envelope, dict) or type(envelope.get('schema_version')) is not int
                    or envelope['schema_version'] != 1
                    or envelope.get('binding') != {'model_sha256': model_sha, 'input_sha256': input_sha}):
                raise ValueError('malformed or misbound native proposal')
            if 'guard_refusal' in envelope:
                guard = envelope['guard_refusal']
                if (set(envelope) != {'schema_version', 'binding', 'guard_refusal'}
                        or not isinstance(guard, dict) or set(guard) != {'exit_code', 'kind', 'reason'}
                        or type(guard['exit_code']) is not int or guard['exit_code'] != 1
                        or not isinstance(guard['kind'], str) or guard['kind'] not in allowed_guard_kinds
                        or not isinstance(guard['reason'], str) or not 1 <= len(guard['reason']) <= 300):
                    raise ValueError('malformed or undeclared application guard refusal')
                result.update(exit_code=1, application_refusal=guard)
                return result
            if not isinstance(envelope.get('candidate'), dict) or not isinstance(envelope.get('calculation'), dict):
                raise ValueError('malformed native candidate/calculation')  # noqa: TRY004 -- refusal protocol
            document = envelope['candidate']
            if candidate_transform is not None:
                document = candidate_transform(document)
            _preserve_source(model_doc, _parse_document(input_bytes.decode('utf-8')), document, owned_relations)
            candidate_bytes = (json.dumps(document, sort_keys=True, indent=2, allow_nan=False) + '\n').encode()
            result['calculation'] = envelope['calculation']
            return _check_and_publish(result, interpreter=interpreter, model_doc=model_doc, model_sha=model_sha,
                                      sources=((model_path, model_bytes), (input_path, input_bytes)),
                                      runtime_bytes=runtime_bytes, candidate_bytes=candidate_bytes, output=output)
    except (ValueError, UnicodeError, ModelLoadError, ModelValidationError) as error:
        result.update(exit_code=3, reason=str(error)[:300])
    except Exception as error:  # noqa: BLE001 -- application refusal must withhold publication
        result.update(exit_code=70, reason=f'{type(error).__name__}: {error}'[:300])
    return result


def check_proposal(model_path, input_path, proposal_path, output_path, *, native_python, owned_relations=()):
    """Check a supplied candidate, such as an agent's proposal, with the exported PyRel checker.

    No native query runs, so ``calculation`` stays ``None``. The proposal may change only
    ``owned_relations``; its bytes are captured and bound like the input's.
    """
    result = {'exit_code': 70, 'accepted': False, 'published': False,
              'policy': None, 'calculation': None}
    try:
        output = Path(output_path).absolute()
        if output.exists() or output.is_symlink():
            result.update(exit_code=2, reason='output already exists')
            return result
        interpreter = Path(native_python)
        if not interpreter.is_absolute() or not interpreter.is_file():
            raise RuntimeError('explicit native interpreter is unavailable')
        model_bytes = _capture(model_path, INPUT_CAP)
        input_bytes = _capture(input_path, INPUT_CAP)
        proposal_bytes = _capture(proposal_path, INPUT_CAP)
        load_model_bytes(model_bytes, source=model_path)
        model_doc = _parse_document(model_bytes.decode('utf-8'))
        model_sha = hashlib.sha256(model_bytes).hexdigest()
        result['source_binding'] = {'model_sha256': model_sha,
                                    'input_sha256': hashlib.sha256(input_bytes).hexdigest(),
                                    'proposal_sha256': hashlib.sha256(proposal_bytes).hexdigest()}
        document = bounded_json(proposal_bytes, max_bytes=INPUT_CAP)
        _preserve_source(model_doc, _parse_document(input_bytes.decode('utf-8')), document, owned_relations)
        result['proposal'] = {name: document['facts'].get(name, []) for name in owned_relations}
        candidate_bytes = (json.dumps(document, sort_keys=True, indent=2, allow_nan=False) + '\n').encode()
        with tempfile.TemporaryDirectory(prefix='gnd-native-application-') as directory:
            model = Path(directory) / 'model.orm.yaml'
            model.write_bytes(model_bytes)
            runtime_bytes = render_pyrel(model).encode('utf-8')
        return _check_and_publish(result, interpreter=interpreter, model_doc=model_doc, model_sha=model_sha,
                                  sources=((model_path, model_bytes), (input_path, input_bytes),
                                           (proposal_path, proposal_bytes)),
                                  runtime_bytes=runtime_bytes, candidate_bytes=candidate_bytes, output=output)
    except (ValueError, UnicodeError, ModelLoadError, ModelValidationError) as error:
        result.update(exit_code=3, reason=str(error)[:300])
    except Exception as error:  # noqa: BLE001 -- application refusal must withhold publication
        result.update(exit_code=70, reason=f'{type(error).__name__}: {error}'[:300])
    return result


_WITNESS_LINES = 5


def _list(value):
    return value if isinstance(value, list) else []


def _text(value):
    return ' '.join(str(value).split())


def _row_label(row):
    if isinstance(row, dict) and set(row) == {'user', 'book'}:
        return f"{row['user']}/{row['book']}"
    return json.dumps(row, sort_keys=True, default=str)


def format_result(result):
    """Short human summary of an application result; total over any input."""
    result = result if isinstance(result, dict) else {}
    lines = []
    proposal = result.get('proposal')
    if isinstance(proposal, dict):
        proposal = [row for rows in proposal.values() for row in _list(rows)]
    if isinstance(proposal, list):
        lines.append("Checking the agent's proposal: " + ', '.join(_row_label(row) for row in proposal))
    calculation = result.get('calculation') if isinstance(result.get('calculation'), dict) else {}
    selected = [row for row in _list(calculation.get('selected_pairs')) if isinstance(row, dict)]
    if selected:
        users = {str(row.get('user')) for row in selected}
        if len(users) == 1:
            lines.append(f'Proposed for {users.pop()}: ' + ', '.join(str(row.get('book')) for row in selected))
        else:
            lines.append('Proposed: ' + ', '.join(_row_label(row) for row in selected))
    approval = result.get('approval')
    if isinstance(approval, dict):
        lines.append(f"Proposed approval: expense {approval.get('expense')} by {approval.get('chain')}")
    report = result.get('report') if isinstance(result.get('report'), dict) else None
    if report is not None and result.get('accepted') is True:
        totals = report.get('totals_by_currency')
        total = (', '.join(f'{amount} {currency}' for currency, amount in totals.items()) + ' total'
                 if isinstance(totals, dict) else f"{report.get('total_eur')} EUR total")
        lines.append(f"Report: {report.get('submitted')} submitted, {report.get('approved')} approved, {total}")
    policy = result.get('policy') if isinstance(result.get('policy'), dict) else None
    verdicts = [row for row in _list((policy or {}).get('verdicts')) if isinstance(row, dict)]
    status = (policy or {}).get('status')
    refusal = result.get('application_refusal')
    if result.get('accepted') is True:
        warnings = sum(1 for row in verdicts if row.get('status') == 'warning')
        lines.append('Policy check: ACCEPTED' + (f" with {warnings} warning{'s' if warnings != 1 else ''}"
                                                 if warnings else ''))
    elif isinstance(refusal, dict):
        lines.append(f"Policy check: REFUSED by the application ({_text(refusal.get('reason'))})")
    elif status == 'rejected':
        lines.append('Policy check: REJECTED')
    elif status == 'incomplete':
        lines.append('Policy check: NOT ACCEPTED (some rules could not be decided)')
    elif policy is not None:
        lines.append('Policy check: NOT ACCEPTED')
    else:
        reason = result.get('reason')
        lines.append('Policy check: NOT RUN' + (f' ({_text(reason)})' if isinstance(reason, str) and reason.strip() else ''))
    for row in verdicts:
        status = row.get('status')
        if not isinstance(status, str) or status == 'satisfied':
            continue
        witnesses = _list(row.get('witnesses'))
        label = f"  {_text(status):<11} {_text(row.get('id'))}"
        for witness in witnesses[:_WITNESS_LINES]:
            lines.append(label + ' ' + json.dumps(witness, default=str))
        if len(witnesses) > _WITNESS_LINES:
            lines.append(f'  ... {len(witnesses) - _WITNESS_LINES} more')
        if not witnesses:
            lines.append(label)
    if result.get('published') is True:
        lines.append(f"Published: {result.get('output')}")
    elif report is None or result.get('accepted') is not True:
        lines.append('Nothing was published.')
    return lines
