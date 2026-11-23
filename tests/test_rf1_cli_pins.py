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

EXPECTED_PARSERS = 64  # OS1 and OS3 add one Ossie leaf each; include-root-routes IR2 adds `gnd flatten`; AC1 adds two COUNT membership leaves.
COUNT_CLI_PATHS = {"gnd", "gnd witness-count", "gnd replay-count"}
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


def _restore_frozen(parser, node, *, types=None):
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
            if kwargs['type'] is not None:
                known = {'builtins.int': int, 'gnd.cli._positive_int': cli._positive_int}
                kwargs['type'] = (types or {}).get(kwargs['type']) or known[kwargs['type']]
        else:
            assert action['class'] == '_StoreTrueAction'
            kwargs['action'] = 'store_true'
        names = action['option_strings'] or [action['dest']]
        if action['option_strings']:
            kwargs.update(dest=action['dest'], required=action['required'])
        parser.add_argument(*names, **kwargs)
    return children


def _witness_projection_successor(command):
    """Add the two rooted projection options to the frozen witness parser."""
    base = json.loads(golden_path("cli", "tree").read_text())["subcommands"][command]
    parser = cli._BandSafeParser(prog=base["prog"], description=base["description"])
    _restore_frozen(parser, base)
    inherited = _walk(parser, ("gnd", command), {})
    inherited["listed_help"] = base["listed_help"]
    assert canonical(inherited) == canonical(base)
    composition = next(action for action in parser._actions if action.dest == "composition")
    composition.help = {
        "witness": "composition record for a composed population",
        "replay": "composition record bound by the witness",
    }[command]
    # The rooted flags are declared before the existing replay presentation flags.
    position = parser._actions.index(composition) + 1
    flags = [
        parser.add_argument("--flat-model", help="bound flat model from an include-root extraction"),
        parser.add_argument("--flattening-record", help="origin record paired with --flat-model"),
    ]
    for offset, flag in enumerate(flags):
        parser._actions.remove(flag)
        parser._actions.insert(position + offset, flag)
        group = parser._optionals._group_actions
        group.remove(flag)
        group.insert(group.index(composition) + 1 + offset, flag)
    after = _walk(parser, ("gnd", command), {})
    after["listed_help"] = base["listed_help"]
    return after, parser


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


FLATTEN_HELP = "write an include root's flat model and its record"
FLATTEN_ROOT_PATHS = ("gnd", "gnd doctor", "gnd install", "gnd uninstall")


def _with_flatten_choice(text):
    """The frozen root text with `flatten` listed after `extract`, once per choice list."""
    before = "extract,export"
    assert before in text, "the frozen choice list moved"
    return text.replace(before, "extract,flatten,export")


def _flatten_successor():
    """include-root-routes IR2: the declared `gnd flatten` leaf after `extract`.

    The leaf is declared here, independently of `gnd.commands.flatten`; the
    root help, tree and the root usage that four exit probes print are the
    frozen goldens with that one choice inserted.
    """
    reference = cli._BandSafeParser(prog="gnd")
    children = reference.add_subparsers(dest="command", required=True)
    flatten = children.add_parser("flatten", help=FLATTEN_HELP, description=(
        "Resolve a version-5 model's includes, as gnd check does, and write "
        "<stem>.flat.orm.json and <stem>.flattening.json (gnd-flattening/1) "
        "into --out, both files or neither. Temporal models are accepted. "
        "Reference paths in the flat model stay relative to the root model's "
        "directory. Exits 0 when both files are written, 3 when the model is "
        "invalid, declares no includes or an include is refused, 11 when "
        "either output file already exists (nothing is written), 64 on usage "
        "errors, 66 when the model is missing, 74 when the output path is "
        "refused or unwritable."))
    flatten.add_argument("model", help="path to the include root")
    flatten.add_argument("--out", required=True, help="output directory")
    flatten.add_argument("--format", choices=("text", "json"), default="text")
    leaf = _walk(flatten, ("gnd", "flatten"), {})
    leaf["listed_help"] = FLATTEN_HELP

    tree = json.loads(golden_path("cli", "tree").read_text())
    action = next(a for a in tree["actions"] if a["class"] == "_SubParsersAction")
    action["choices"].insert(action["choices"].index("extract") + 1, "flatten")
    tree["subcommands"]["flatten"] = leaf

    extract_line = "    extract             emit the per-model extraction artifact bundle (VER-01,\n                        DATA-02)\n"
    root_help = json.loads(golden_path("cli-help", "gnd").read_text())["help"]
    assert extract_line in root_help, "the frozen extract listing moved"
    root_help = _with_flatten_choice(root_help).replace(
        extract_line, extract_line + f"    flatten             {FLATTEN_HELP}\n")

    def probe(argv):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err), pytest.raises(SystemExit) as caught:
            reference.parse_args(argv)
        return {"exit": caught.value.code, "stdout": out.getvalue(), "stderr": err.getvalue()}

    exit_probe = {"gnd flatten": {"help": probe(["flatten", "--help"]),
                                  "unknown_flag": probe(["flatten", "--rf1-unknown-flag"])}}
    for path in FLATTEN_ROOT_PATHS:
        frozen = json.loads(golden_path("cli-exit", path).read_text())
        frozen = {k: v for k, v in frozen.items() if k in ("help", "unknown_flag")}
        exit_probe[path] = json.loads(_with_flatten_choice(json.dumps(frozen)))
    exit_probe["gnd"]["help"]["stdout"] = root_help
    return {"tree": tree, "help": {"gnd": root_help, "gnd flatten": flatten.format_help()},
            "exit_probe": exit_probe}


def _include_preview_successor():
    """MC3's successor, then GO2's two outcome options (growth-round-outcomes, #227)."""
    return _include_preview_reference(outcomes=True)


def _include_preview_reference(*, outcomes):
    """Restore the frozen predecessor, then add MC3's one literal repeatable flag;
    with ``outcomes``, also GO2's --operation-outcomes and --outcome-report,
    declared right after --shape-report as the production parser declares them."""
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
    if outcomes:
        added = [
            reference.add_argument(
                '--operation-outcomes', action='store_true',
                help='name an outcome for every operation of the proposal (admitted, refused and why, or unassessed)'),
            reference.add_argument(
                '--outcome-report', default=None, metavar='FILE',
                help='when the preview is refused, write every operation\'s outcome to FILE beneath ROOT; '
                     'requires --operation-outcomes'),
        ]
        for container in (reference._actions, reference._optionals._group_actions):
            for action in added:
                container.remove(action)
            anchor = next(i for i, action in enumerate(container) if '--shape-report' in action.option_strings)
            container[anchor + 1:anchor + 1] = added
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
    """Restore RC4, add the guarded workflow flags and GC3 diagnostics help."""
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
    diagnostics["help"] = "include guarded binding and disjunction diagnostics; implies --rule-ids"
    base["actions"].insert(ALLOW_VACUOUS_SUCCESSOR["action_index"], edition)
    base["actions"].insert(ALLOW_VACUOUS_SUCCESSOR["action_index"] + 2, diagnostics)
    parser = cli._BandSafeParser(prog=base["prog"], description=base["description"])
    _restore_frozen(parser, base)
    return base, parser


def _guarded_cases_synth_successor():
    base = json.loads(golden_path("cli", "tree").read_text())["subcommands"]["synth"]
    base["actions"].insert(-1, {
        "class": "_StoreTrueAction", "dest": "guarded_cases", "option_strings": ["--guarded-cases"],
        "default": False, "const": True, "choices": None, "metavar": None, "nargs": 0,
        "required": False, "type": None,
        "help": "generate active failing and passing cases for guarded rules in a fresh corpus",
    })
    parser = cli._BandSafeParser(prog=base["prog"], description=base["description"])
    _restore_frozen(parser, base)
    return base, parser


def _guarded_join_discover_successor():
    base = json.loads(golden_path("cli", "tree").read_text())["subcommands"]["discover"]
    actions = base["actions"]
    next(action for action in actions if action["dest"] == "families")["help"] = (
        "comma-separated subset of the seven default families; add fact-type or guarded-join to opt in"
    )
    for flag, metavar, help_, type_ in (
        ("joined-relation", "FACT:SOURCE:TARGET",
         "guarded-join family: binary relation and endpoint roles", None),
        ("joined-classifier", "FACT:ENTITY:CLASS",
         "guarded-join family: binary classifier and its roles", None),
        ("joined-marker", "FACT:ENTITY:VALUE=JSON",
         "guarded-join family: restrict same-class candidates by a target marker", None),
        ("max-directed-pairs", "N",
         "guarded-join family: most ordered class pairs considered (default 256)",
         "gnd.commands.discover._at_least.<locals>.parse"),
    ):
        actions.insert(-1, {
            "class": "_StoreAction", "dest": flag.replace("-", "_"), "option_strings": ["--" + flag],
            "default": None, "const": None, "choices": None, "metavar": metavar, "nargs": None,
            "required": False, "type": type_, "help": help_,
        })
    parser = cli._BandSafeParser(prog=base["prog"], description=base["description"])
    # The probe parses only help and an unknown option. Conversion semantics
    # are exercised by the direct discover command fixtures.
    _restore_frozen(parser, base, types={
        action["type"]: str for action in actions if action["type"] is not None
    })
    return base, parser


def _guarded_successor_probe(parser):
    result = {}
    for name, arguments in (("help", ["--help"]), ("unknown_flag", ["--rf1-unknown-flag"])):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err), pytest.raises(SystemExit) as caught:
            parser.parse_args(arguments)
        result[name] = {"exit": caught.value.code, "stdout": out.getvalue(), "stderr": err.getvalue()}
    return result


def _count_cli_successor(base):
    """Reconstruct the frozen root and add the two COUNT command grammars."""
    root = cli._BandSafeParser(prog=base["prog"], description=base["description"])
    root.add_argument("--version", action="version", help=base["actions"][1]["help"])
    root.add_argument("--disclosure", action=cli._StoreOnce, choices=base["actions"][2]["choices"],
                      help=base["actions"][2]["help"])
    children = root.add_subparsers(dest="command", required=True)
    additions = {
        "witness-count": "produce a bounded COUNT membership certificate",
        "replay-count": "independently replay a COUNT membership certificate",
    }
    for name in base["actions"][-1]["choices"]:
        children.add_parser(name, help=base["subcommands"][name]["listed_help"])
        if name != "why-not":
            continue
        for count_name, help_text in additions.items():
            child = children.add_parser(count_name, help=help_text)
            child.add_argument("model")
            child.add_argument("population")
            child.add_argument("--request", required=True, help="expected COUNT group request")
            child.add_argument("--raw", action="store_true", help="explicitly reveal bound values")
            if count_name == "witness-count":
                child.add_argument("--out", help="create a new certificate file; requires --raw")
            else:
                child.add_argument("certificate")
    parsers = {}
    observed = _walk(root, ("gnd",), parsers)
    base["actions"][-1] = observed["actions"][-1]
    base["subcommands"].update({name: observed["subcommands"][name] for name in additions})
    return parsers


def test_cli_tree(tree):
    # Preserve RF1's historical bytes; approve only this additive successor.
    expected = json.loads(golden_path("cli", "tree").read_text())
    expected["subcommands"]["check"] = _guarded_workflows_check_successor()[0]
    expected["subcommands"]["synth"] = _guarded_cases_synth_successor()[0]
    expected["subcommands"]["discover"] = _guarded_join_discover_successor()[0]
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
    for command in ("witness", "replay"):
        expected["subcommands"][command] = _witness_projection_successor(command)[0]
    flattened = _flatten_successor()["tree"]
    expected["actions"] = flattened["actions"]
    expected["subcommands"]["flatten"] = flattened["subcommands"]["flatten"]
    _count_cli_successor(expected)   # AC1's two leaves go on top of the root that already lists flatten
    _assert_successor("cli", "tree", tree[0], expected)


@pytest.mark.parametrize("path", PATHS)
def test_cli_help(tree, path):
    if path in COUNT_CLI_PATHS:
        parser = _count_cli_successor(_flatten_successor()["tree"])[path]
        _assert_successor("cli-help", path, {"path": path, "help": tree[2][path]},
                          {"path": path, "help": parser.format_help()})
        return
    if path in {"gnd witness", "gnd replay"}:
        parser = _witness_projection_successor(path.split()[1])[1]
        _assert_successor("cli-help", path, {"path": path, "help": tree[2][path]},
                          {"path": path, "help": parser.format_help()})
        return
    if path in {"gnd", "gnd flatten"}:
        _assert_successor("cli-help", path, {"path": path, "help": tree[2][path]},
                          {"path": path, "help": _flatten_successor()["help"][path]})
        return
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
    if path == "gnd discover":
        _assert_successor("cli-help", path, {"path": path, "help": tree[2][path]},
                          {"path": path, "help": _guarded_join_discover_successor()[1].format_help()})
        return
    if path == "gnd synth":
        _assert_successor("cli-help", path, {"path": path, "help": tree[2][path]},
                          {"path": path, "help": _guarded_cases_synth_successor()[1].format_help()})
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
    if path in COUNT_CLI_PATHS:
        observed = {
            "help": {"exit": shown.returncode, "stdout": shown.stdout.decode(), "stderr": shown.stderr.decode()},
            "unknown_flag": {"exit": refused.returncode, "stdout": refused.stdout.decode(), "stderr": refused.stderr.decode()},
        }
        parser = _count_cli_successor(_flatten_successor()["tree"])[path]
        _assert_successor("cli-exit", path, observed, _guarded_successor_probe(parser))
        return
    if path in {"gnd witness", "gnd replay"}:
        observed = {
            "help": {"exit": shown.returncode, "stdout": shown.stdout.decode(), "stderr": shown.stderr.decode()},
            "unknown_flag": {"exit": refused.returncode, "stdout": refused.stdout.decode(), "stderr": refused.stderr.decode()},
        }
        parser = _witness_projection_successor(path.split()[1])[1]
        _assert_successor("cli-exit", path, observed, _guarded_successor_probe(parser))
        return
    if path in {"gnd flatten", *FLATTEN_ROOT_PATHS}:
        observed = {
            "help": {"exit": shown.returncode, "stdout": shown.stdout.decode(), "stderr": shown.stderr.decode()},
            "unknown_flag": {"exit": refused.returncode, "stdout": refused.stdout.decode(), "stderr": refused.stderr.decode()},
        }
        expected = _flatten_successor()["exit_probe"][path]
        if path != "gnd flatten":   # AC1: the root usage these probes print also lists the two COUNT leaves
            expected["unknown_flag"]["stderr"] = expected["unknown_flag"]["stderr"].replace(
                "witness,replay,witness-view,why-not,import",
                "witness,replay,witness-view,why-not,witness-count,replay-count,import",
            )
        _assert_successor("cli-exit", path, observed, expected)
        return
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
    if path in ("gnd check", "gnd validate", "gnd synth", "gnd discover"):
        observed = {
            "help": {"exit": shown.returncode, "stdout": shown.stdout.decode(), "stderr": shown.stderr.decode()},
            "unknown_flag": {
                "exit": refused.returncode,
                "stdout": refused.stdout.decode(),
                "stderr": refused.stderr.decode(),
            },
        }
        successors = {"gnd check": _guarded_workflows_check_successor,
                      "gnd synth": _guarded_cases_synth_successor,
                      "gnd discover": _guarded_join_discover_successor}
        expected = (VALIDATE_DOCUMENTS_SUCCESSOR["exit_probe"] if path == "gnd validate"
                    else _guarded_successor_probe(successors[path]()[1]))
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
