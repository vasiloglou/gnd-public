"""RF1 lane L-CLI: parser tree, help text, exit probes and exit map (spec 6.3)."""

from __future__ import annotations

import argparse
import contextlib
import copy
import io
import json
import os
from pathlib import Path

import pytest
from support.cli_runner import run_main
from support.rf1_pins import CAPTURE_ENV, assert_golden, canonical, encode, golden_path, minor_tag

from gnd import batch, cli, exits
from gnd.conformance import service as conformance_service
from gnd.evolve import models as evolve_models
from gnd.evolve import service as evolve_service
from gnd.exp import session_eval

EXPECTED_PARSERS = 59  # MC2 adds `gnd verbalize model`; historical paths retained.
COMPILED_SUCCESSOR = json.loads(
    (Path(__file__).parent / 'fixtures/compiled-snapshot-cli/expected.json').read_text()
)
# rule-check-adoption RC1 adds `check --rule-ids`; its help and exit probe supersede
# the compiled successor's for `gnd check` and differ from them by that one option.
RULE_IDS_SUCCESSOR = json.loads(
    (Path(__file__).parent / 'fixtures/rule-ids-cli/expected.json').read_text()
)
# RC3 adds `check --baseline`; its help and exit probe supersede RC1's for `gnd check`
# and differ from them by that one option.
BASELINE_SUCCESSOR = json.loads(
    (Path(__file__).parent / 'fixtures/baseline-cli/expected.json').read_text()
)
# RC4 adds `check --allow-vacuous`; its help and exit probe supersede RC3's for
# `gnd check` and differ from them by that one option.
ALLOW_VACUOUS_SUCCESSOR = json.loads(
    (Path(__file__).parent / 'fixtures/allow-vacuous-cli/expected.json').read_text()
)


# report-output-fidelity ROF3 adds `validate --identity`; its help and exit probe
# supersede RF1's for `gnd validate` and differ from them by that one option.
IDENTITY_SUCCESSOR = json.loads(
    (Path(__file__).parent / 'fixtures/model-identity-cli/expected.json').read_text()
)


# unattended-model-growth UG3 adds `validate --require-documents`; its help and exit
# probe supersede ROF3's for `gnd validate` and differ from them by that one option.
# The bytes are the same on every supported minor (measured on 3.11, 3.13, 3.14).
VALIDATE_DOCUMENTS_SUCCESSOR = json.loads(
    (Path(__file__).parent / 'fixtures/validate-documents-cli/expected.json').read_text()
)


# unattended-model-growth UG2 adds `evolve preview/apply --check-population`; the
# action is inserted into RF1's tree, and the help and exit probe of both commands
# are superseded per Python minor (their RF1 goldens are per minor too).
CHECK_POPULATION_SUCCESSOR = json.loads(
    (Path(__file__).parent / 'fixtures/check-population-cli/expected.json').read_text()
)
CHECK_POPULATION_PATHS = {"gnd evolve preview": "preview", "gnd evolve apply": "apply"}


def _check_population_successor(path: str, field: str):
    entry = CHECK_POPULATION_SUCCESSOR[CHECK_POPULATION_PATHS[path]][field]
    if minor_tag() not in entry:
        pytest.skip(f"no UG2 successor for {path} under {minor_tag()}")
    return entry[minor_tag()]


class _Captured(Exception):
    pass


def _plain_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("COLUMNS", "80")
    monkeypatch.setenv("NO_COLOR", "1")
    monkeypatch.setenv("PYTHON_COLORS", "0")
    monkeypatch.delenv("FORCE_COLOR", raising=False)


def _root(monkeypatch: pytest.MonkeyPatch) -> argparse.ArgumentParser:
    captured: list[argparse.ArgumentParser] = []

    def capture(parser, _args=None, _namespace=None):
        captured.append(parser)
        raise _Captured

    with monkeypatch.context() as patch:
        patch.setattr(cli._BandSafeParser, "parse_args", capture)
        with pytest.raises(_Captured):
            cli.main([])
    return captured[0]


def _name(value) -> object:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, type) or callable(value):
        return f"{getattr(value, '__module__', '?')}.{getattr(value, '__qualname__', type(value).__name__)}"
    return repr(value)


def _walk(parser: argparse.ArgumentParser, path: tuple[str, ...], out: dict) -> dict:
    out[" ".join(path)] = parser
    node = {
        "prog": parser.prog,
        "description": parser.description,
        "epilog": parser.epilog,
        "formatter_class": _name(parser.formatter_class),
        "parser_class": _name(type(parser)),
        "actions": [],
        "subcommands": {},
    }
    for action in parser._actions:
        entry = {
            "class": type(action).__name__,
            "option_strings": list(action.option_strings),
            "dest": action.dest,
            "nargs": action.nargs,
            "const": _name(action.const),
            "default": _name(action.default),
            "type": _name(action.type),
            "choices": None if action.choices is None else [str(choice) for choice in action.choices],
            "required": action.required,
            "help": action.help,
            "metavar": _name(action.metavar),
        }
        node["actions"].append(entry)
        if isinstance(action, argparse._SubParsersAction):
            helps = {choice.dest: choice.help for choice in action._choices_actions}
            for name, sub in action.choices.items():
                child = _walk(sub, (*path, name), out)
                child["listed_help"] = helps.get(name)
                node["subcommands"][name] = child
    return node


@pytest.fixture(scope="module")
def tree():
    with pytest.MonkeyPatch.context() as monkeypatch:
        _plain_env(monkeypatch)
        parsers: dict[str, argparse.ArgumentParser] = {}
        structure = _walk(_root(monkeypatch), ("gnd",), parsers)
        helps = {path: parser.format_help() for path, parser in parsers.items()}
    return structure, parsers, helps


def _paths() -> list[str]:
    with pytest.MonkeyPatch.context() as monkeypatch:
        parsers: dict[str, argparse.ArgumentParser] = {}
        _walk(_root(monkeypatch), ("gnd",), parsers)
    return sorted(parsers)


PATHS = _paths()


def _assert_successor(lane, key, observed, expected):
    if os.environ.get(CAPTURE_ENV):
        assert_golden(lane, key, observed)
    else:
        assert canonical(observed) == canonical(expected)


def _model_review_successor():
    """Decode the frozen grammar independently, then add only MC2's literal leaf."""
    base = json.loads(golden_path('cli', 'tree').read_text())['subcommands']['verbalize']
    reference = cli._BandSafeParser(prog=base['prog'], description=base['description'])

    def restore(parser, node):
        children = None
        for action in node['actions']:
            if action['class'] == '_HelpAction':
                continue
            if action['class'] == '_SubParsersAction':
                children = parser.add_subparsers(dest=action['dest'], required=action['required'])
                for name, child in node['subcommands'].items():
                    restore(children.add_parser(name, help=child['listed_help']), child)
                continue
            kwargs = {k: action[k] for k in ('default', 'help')}
            if action['class'] == '_StoreAction':
                assert action['const'] is None
                kwargs.update({k: action[k] for k in ('type', 'choices', 'metavar', 'nargs')})
            else:
                assert action['class'] == '_StoreTrueAction'
                kwargs['action'] = 'store_true'
            names = action['option_strings'] or [action['dest']]
            if action['option_strings']:
                kwargs.update(dest=action['dest'], required=action['required'])
            parser.add_argument(*names, **kwargs)
        return children

    children = restore(reference, base)
    before = _walk(reference, ('gnd', 'verbalize'), {})
    before['listed_help'] = base['listed_help']
    assert canonical(before) == canonical(base)  # Every old field binds before widening.
    model = children.add_parser('model', help='Render the complete model for review.')
    model.add_argument('model')
    after = _walk(reference, ('gnd', 'verbalize'), {})
    after['listed_help'] = base['listed_help']

    def probe(argv):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err), pytest.raises(SystemExit) as caught:
            reference.parse_args(argv)
        return {'exit': caught.value.code, 'stdout': out.getvalue(), 'stderr': err.getvalue()}

    paths = {'gnd verbalize': [], 'gnd verbalize model': ['model']}
    return {'tree': after, 'help': {'gnd verbalize': reference.format_help(),
                                  'gnd verbalize model': model.format_help()},
            'exit_probe': {path: {'help': probe([*argv, '--help']),
                                  'unknown_flag': probe([*argv, '--rf1-unknown-flag'])}
                           for path, argv in paths.items()}}


def test_cli_tree(tree):
    # Preserve RF1's historical bytes; approve only this additive successor.
    expected = json.loads(golden_path("cli", "tree").read_text())
    expected["subcommands"]["check"]["actions"].insert(
        COMPILED_SUCCESSOR["action_index"], copy.deepcopy(COMPILED_SUCCESSOR["action"])
    )
    expected["subcommands"]["check"]["actions"].insert(
        RULE_IDS_SUCCESSOR["action_index"], copy.deepcopy(RULE_IDS_SUCCESSOR["action"])
    )
    expected["subcommands"]["check"]["actions"].insert(
        BASELINE_SUCCESSOR["action_index"], copy.deepcopy(BASELINE_SUCCESSOR["action"])
    )
    expected["subcommands"]["check"]["actions"].insert(
        ALLOW_VACUOUS_SUCCESSOR["action_index"], copy.deepcopy(ALLOW_VACUOUS_SUCCESSOR["action"])
    )
    expected["subcommands"]["validate"]["actions"].insert(
        IDENTITY_SUCCESSOR["action_index"], copy.deepcopy(IDENTITY_SUCCESSOR["action"])
    )
    expected["subcommands"]["validate"]["actions"].insert(
        VALIDATE_DOCUMENTS_SUCCESSOR["action_index"], copy.deepcopy(VALIDATE_DOCUMENTS_SUCCESSOR["action"])
    )
    for command in ("preview", "apply"):
        successor = CHECK_POPULATION_SUCCESSOR[command]
        expected["subcommands"]["evolve"]["subcommands"][command]["actions"].insert(
            successor["action_index"], copy.deepcopy(successor["action"])
        )
    expected['subcommands']['verbalize'] = _model_review_successor()['tree']
    _assert_successor("cli", "tree", tree[0], expected)


@pytest.mark.parametrize("path", PATHS)
def test_cli_help(tree, path):
    if path in {'gnd verbalize', 'gnd verbalize model'}:
        _assert_successor('cli-help', path, {'path': path, 'help': tree[2][path]},
                          {'path': path, 'help': _model_review_successor()['help'][path]})
        return
    if path == "gnd check":
        _assert_successor("cli-help", path, {"path": path, "help": tree[2][path]},
                          {"path": path, "help": ALLOW_VACUOUS_SUCCESSOR["help"]})
        return
    if path == "gnd validate":
        _assert_successor("cli-help", path, {"path": path, "help": tree[2][path]},
                          {"path": path, "help": VALIDATE_DOCUMENTS_SUCCESSOR["help"]})
        return
    if path in CHECK_POPULATION_PATHS:
        _assert_successor("cli-help", path, {"path": path, "help": tree[2][path]},
                          {"path": path, "help": _check_population_successor(path, "help")})
        return
    assert_golden("cli-help", path, {"path": path, "help": tree[2][path]})


@pytest.mark.parametrize("path", PATHS)
def test_cli_exit_probe(path, monkeypatch):
    _plain_env(monkeypatch)
    argv = path.split()[1:]
    shown = run_main([*argv, "--help"])
    refused = run_main([*argv, "--rf1-unknown-flag"])
    if path in {'gnd verbalize', 'gnd verbalize model'}:
        observed = {'help': {'exit': shown.returncode, 'stdout': shown.stdout.decode(), 'stderr': shown.stderr.decode()},
                    'unknown_flag': {'exit': refused.returncode, 'stdout': refused.stdout.decode(), 'stderr': refused.stderr.decode()}}
        _assert_successor('cli-exit', path, observed, _model_review_successor()['exit_probe'][path])
        return
    if path in ("gnd check", "gnd validate"):
        observed = {
            "help": {"exit": shown.returncode, "stdout": shown.stdout.decode(), "stderr": shown.stderr.decode()},
            "unknown_flag": {
                "exit": refused.returncode,
                "stdout": refused.stdout.decode(),
                "stderr": refused.stderr.decode(),
            },
        }
        successor = ALLOW_VACUOUS_SUCCESSOR if path == "gnd check" else VALIDATE_DOCUMENTS_SUCCESSOR
        _assert_successor("cli-exit", path, observed, successor["exit_probe"])
        return
    if path in CHECK_POPULATION_PATHS:
        observed = {
            "help": {"exit": shown.returncode, "stdout": shown.stdout.decode(), "stderr": shown.stderr.decode()},
            "unknown_flag": {
                "exit": refused.returncode,
                "stdout": refused.stdout.decode(),
                "stderr": refused.stderr.decode(),
            },
        }
        _assert_successor("cli-exit", path, observed, _check_population_successor(path, "exit_probe"))
        return
    assert_golden(
        "cli-exit",
        path,
        {
            "help": {"exit": shown.returncode, "stdout": shown.stdout.decode(), "stderr": shown.stderr.decode()},
            "unknown_flag": {
                "exit": refused.returncode,
                "stdout": refused.stdout.decode(),
                "stderr": refused.stderr.decode(),
            },
        },
    )


def _constants(module, prefix="EXIT_"):
    return {name: value for name, value in sorted(vars(module).items()) if name.startswith(prefix)}


def test_cli_exit_map():
    observed = {
        "gnd.exits": {name: getattr(exits, name) for name in (
            "EXIT_EXPERIMENT_OPEN", "EXIT_INTERNAL", "EXIT_IO", "EXIT_NO_INPUT",
            "EXIT_USAGE", "EXIT_WALK_HALTED")},  # RF2 approved historical name projection.
        "gnd.exits.SOLVE_CONTROL_PLANE_EXITS": encode(exits.SOLVE_CONTROL_PLANE_EXITS),
        "gnd.cli": _constants(cli),
        "gnd.conformance.service": _constants(conformance_service, "_EXIT_"),
        "gnd.batch.BATCH_EXIT_PRECEDENCE": encode(batch.BATCH_EXIT_PRECEDENCE),
        "gnd.evolve.models._CONFORMANCE_EXIT_PRECEDENCE": encode(evolve_models._CONFORMANCE_EXIT_PRECEDENCE),
        "gnd.evolve.service._EXIT_PRECEDENCE": encode(evolve_service._EXIT_PRECEDENCE),
        "gnd.exp.session_eval.OUTCOME_BY_EXIT": encode(session_eval.OUTCOME_BY_EXIT),
    }
    assert_golden("cli", "exit-map", observed)


def test_cli_coverage(tree):
    """T-CLI-COV: the pinned path set is the complete discovered set."""
    _structure, parsers, helps = tree
    assert len(parsers) == EXPECTED_PARSERS
    assert sorted(parsers) == PATHS == sorted(helps)
