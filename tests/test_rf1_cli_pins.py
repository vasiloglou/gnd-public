"""RF1 lane L-CLI: parser tree, help text, exit probes and exit map (spec 6.3)."""

from __future__ import annotations

import argparse

import pytest
from support.cli_runner import run_main
from support.rf1_pins import assert_golden, encode

from gnd import batch, cli, exits
from gnd.conformance import service as conformance_service
from gnd.evolve import models as evolve_models
from gnd.evolve import service as evolve_service
from gnd.exp import session_eval

EXPECTED_PARSERS = 52


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


def test_cli_tree(tree):
    assert_golden("cli", "tree", tree[0])


@pytest.mark.parametrize("path", PATHS)
def test_cli_help(tree, path):
    assert_golden("cli-help", path, {"path": path, "help": tree[2][path]})


@pytest.mark.parametrize("path", PATHS)
def test_cli_exit_probe(path, monkeypatch):
    _plain_env(monkeypatch)
    argv = path.split()[1:]
    shown = run_main([*argv, "--help"])
    refused = run_main([*argv, "--rf1-unknown-flag"])
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
        "gnd.exits": _constants(exits),
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
    """T-CLI-COV: the pinned path set is the discovered set and has 52 members."""
    _structure, parsers, helps = tree
    assert len(parsers) == EXPECTED_PARSERS
    assert sorted(parsers) == PATHS == sorted(helps)
