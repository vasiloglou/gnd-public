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

EXPECTED_PARSERS = 61  # OS1 and OS3 add one Ossie leaf each.
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


def _restore_frozen(parser, node):
    children = None
    for action in node['actions']:
        if action['class'] == '_HelpAction':
            continue
        if action['class'] == '_SubParsersAction':
            children = parser.add_subparsers(dest=action['dest'], required=action['required'])
            for name, child in node['subcommands'].items():
                _restore_frozen(children.add_parser(name, help=child['listed_help']), child)
            continue
        kwargs = {k: action[k] for k in ('default', 'help')}
        if action['class'] in {'_StoreAction', '_AppendAction'}:
            if action['class'] == '_AppendAction':
                kwargs['action'] = 'append'
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


def _model_review_successor():
    """Decode the frozen grammar independently, then add only MC2's literal leaf."""
    base = json.loads(golden_path('cli', 'tree').read_text())['subcommands']['verbalize']
    reference = cli._BandSafeParser(prog=base['prog'], description=base['description'])

    children = _restore_frozen(reference, base)
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


def _ossie_successor(command):
    """Add the declared Ossie leaf to the frozen parent tree."""
    base = json.loads(golden_path("cli", "tree").read_text())["subcommands"][command]
    reference = cli._BandSafeParser(prog=base["prog"], description=base["description"])
    subparsers = next(action for action in base["actions"] if action["class"] == "_SubParsersAction")
    children = reference.add_subparsers(dest=subparsers["dest"], required=True)
    choices = subparsers["choices"]
    for name in choices:
        children.add_parser(name, help=base["subcommands"][name]["listed_help"])
    old_help = json.loads(golden_path("cli-help", f"gnd {command}").read_text())["help"]
    assert reference.format_help() == old_help

    if command == "export":
        help_text = "export an Ossie ontology with a loss report"
        model_help = "path to the model file"
        out_help = "new ontology file path"
    else:
        help_text = "import a pinned Apache Ossie ontology and write a loss report"
        model_help = "path to the source Ossie JSON or YAML ontology"
        out_help = "new GND ORM model path"
    ossie = children.add_parser("ossie", help=help_text)
    ossie.add_argument("model", help=model_help)
    ossie.add_argument("--out", required=True, help=out_help)
    ossie.add_argument("--loss-report", help="new loss report path (default: OUT.loss.json)")
    if command == "export":
        ossie.add_argument("--format", choices=("yaml", "json"), default="yaml", help="ontology format (default: yaml)")
        ossie.add_argument("--strict", action="store_true", help="refuse any export with a refused disposition")
    leaf = _walk(ossie, ("gnd", command, "ossie"), {})
    leaf["listed_help"] = help_text
    choices.append("ossie")
    base["subcommands"]["ossie"] = leaf

    def probe(argv):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err), pytest.raises(SystemExit) as caught:
            reference.parse_args(argv)
        return {"exit": caught.value.code, "stdout": out.getvalue(), "stderr": err.getvalue()}

    return {
        "tree": base,
        "help": {f"gnd {command}": reference.format_help(), f"gnd {command} ossie": ossie.format_help()},
        "exit_probe": {
            path: {"help": probe([*argv, "--help"]), "unknown_flag": probe([*argv, "--rf1-unknown-flag"])}
            for path, argv in {f"gnd {command}": [], f"gnd {command} ossie": ["ossie"]}.items()
        },
    }


def _include_preview_successor():
    """Restore the frozen predecessor, then add MC3's one literal repeatable flag."""
    base = copy.deepcopy(json.loads(golden_path('cli', 'tree').read_text())['subcommands']['evolve']['subcommands']['preview'])
    old = CHECK_POPULATION_SUCCESSOR['preview']
    base['actions'].insert(old['action_index'], copy.deepcopy(old['action']))
    reference = cli._BandSafeParser(prog=base['prog'], description=base['description'])
    _restore_frozen(reference, base)
    before = _walk(reference, ('gnd', 'evolve', 'preview'), {})
    before['listed_help'] = base['listed_help']
    assert canonical(before) == canonical(base)
    assert reference.format_help() == _check_population_successor('gnd evolve preview', 'help')
    format_action = reference._actions.pop()
    assert format_action.dest == 'format'
    reference._optionals._group_actions.remove(format_action)
    reference.add_argument('--previous-include', action='append', default=None, metavar='ID=PATH',
                           help='authenticate old bytes for a repinned include from PATH beneath ROOT; repeatable')
    reference._actions.append(format_action)
    reference._optionals._group_actions.append(format_action)
    after = _walk(reference, ('gnd', 'evolve', 'preview'), {})
    after['listed_help'] = base['listed_help']
    def probe(argv):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err), pytest.raises(SystemExit) as caught:
            reference.parse_args(argv)
        return {'exit': caught.value.code, 'stdout': out.getvalue(), 'stderr': err.getvalue()}
    return {'tree': after, 'help': reference.format_help(),
            'exit_probe': {'help': probe(['--help']), 'unknown_flag': probe(['--rf1-unknown-flag'])}}


def _guarded_workflows_check_successor():
    """Restore RC4's frozen check parser, then add the two reviewed flags."""
    base = json.loads(golden_path("cli", "tree").read_text())["subcommands"]["check"]
    for action in base["actions"]:
        if action["help"] == argparse.SUPPRESS:
            action["help"] = argparse.SUPPRESS
    for successor in (COMPILED_SUCCESSOR, RULE_IDS_SUCCESSOR, BASELINE_SUCCESSOR, ALLOW_VACUOUS_SUCCESSOR):
        base["actions"].insert(successor["action_index"], copy.deepcopy(successor["action"]))
    parser = cli._BandSafeParser(prog=base["prog"], description=base["description"])
    _restore_frozen(parser, base)
    assert parser.format_help() == ALLOW_VACUOUS_SUCCESSOR["help"]
    # Restore the argument group order by declaring the actions in the frozen tree
    # before reconstructing the final reference parser.
    edition = dict(
        BASELINE_SUCCESSOR["action"], dest="baseline_model", option_strings=["--baseline-model"],
        help="compare rule editions on one population by declared rule ID and offending binding",
    )
    diagnostics = dict(
        ALLOW_VACUOUS_SUCCESSOR["action"], dest="guarded_diagnostics",
        option_strings=["--guarded-diagnostics"],
        help="report version 16: include antecedent binding diagnostics; implies --rule-ids",
    )
    base["actions"].insert(ALLOW_VACUOUS_SUCCESSOR["action_index"], edition)
    base["actions"].insert(ALLOW_VACUOUS_SUCCESSOR["action_index"] + 2, diagnostics)
    parser = cli._BandSafeParser(prog=base["prog"], description=base["description"])
    _restore_frozen(parser, base)
    return base, parser


def _guarded_workflows_check_probe():
    _, parser = _guarded_workflows_check_successor()
    result = {}
    for name, arguments in (("help", ["--help"]), ("unknown_flag", ["--rf1-unknown-flag"])):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err), pytest.raises(SystemExit) as caught:
            parser.parse_args(arguments)
        result[name] = {"exit": caught.value.code, "stdout": out.getvalue(), "stderr": err.getvalue()}
    return result


def test_cli_tree(tree):
    # Preserve RF1's historical bytes; approve only this additive successor.
    expected = json.loads(golden_path("cli", "tree").read_text())
    expected["subcommands"]["check"] = _guarded_workflows_check_successor()[0]
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
    expected['subcommands']['evolve']['subcommands']['preview'] = _include_preview_successor()['tree']
    expected['subcommands']['verbalize'] = _model_review_successor()['tree']
    for command in ("export", "import"):
        expected["subcommands"][command] = _ossie_successor(command)["tree"]
    _assert_successor("cli", "tree", tree[0], expected)


@pytest.mark.parametrize("path", PATHS)
def test_cli_help(tree, path):
    if path in {"gnd export", "gnd export ossie", "gnd import", "gnd import ossie"}:
        _assert_successor("cli-help", path, {"path": path, "help": tree[2][path]},
                          {"path": path, "help": _ossie_successor(path.split()[1])["help"][path]})
        return
    if path == 'gnd evolve preview':
        _assert_successor('cli-help', path, {'path': path, 'help': tree[2][path]},
                          {'path': path, 'help': _include_preview_successor()['help']})
        return
    if path in {'gnd verbalize', 'gnd verbalize model'}:
        _assert_successor('cli-help', path, {'path': path, 'help': tree[2][path]},
                          {'path': path, 'help': _model_review_successor()['help'][path]})
        return
    if path == "gnd check":
        _assert_successor("cli-help", path, {"path": path, "help": tree[2][path]},
                          {"path": path, "help": _guarded_workflows_check_successor()[1].format_help()})
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
    if path in {"gnd export", "gnd export ossie", "gnd import", "gnd import ossie"}:
        observed = {
            "help": {"exit": shown.returncode, "stdout": shown.stdout.decode(), "stderr": shown.stderr.decode()},
            "unknown_flag": {"exit": refused.returncode, "stdout": refused.stdout.decode(), "stderr": refused.stderr.decode()},
        }
        _assert_successor("cli-exit", path, observed, _ossie_successor(path.split()[1])["exit_probe"][path])
        return
    if path == 'gnd evolve preview':
        observed = {'help': {'exit': shown.returncode, 'stdout': shown.stdout.decode(), 'stderr': shown.stderr.decode()},
                    'unknown_flag': {'exit': refused.returncode, 'stdout': refused.stdout.decode(), 'stderr': refused.stderr.decode()}}
        _assert_successor('cli-exit', path, observed, _include_preview_successor()['exit_probe'])
        return
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
        expected = _guarded_workflows_check_probe() if path == "gnd check" else VALIDATE_DOCUMENTS_SUCCESSOR["exit_probe"]
        _assert_successor("cli-exit", path, observed, expected)
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


@pytest.mark.parametrize('damage', ['remove', 'metavar'])
def test_mc3_cli_successor_rejects_missing_or_changed_flag(tree, damage):
    observed = copy.deepcopy(tree[0]['subcommands']['evolve']['subcommands']['preview'])
    actions = observed['actions']
    flag = next(action for action in actions if action['dest'] == 'previous_include')
    if damage == 'remove':
        actions.remove(flag)
    else:
        flag['metavar'] = 'OTHER'
    with pytest.raises(AssertionError):
        _assert_successor('cli', 'preview', observed, _include_preview_successor()['tree'])
