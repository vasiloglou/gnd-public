"""NM2: the disclosure mode (why-not-near-misses notes/phase-NM2-spec.md)."""

from __future__ import annotations

import argparse
from pathlib import Path

import pytest
from support.cli_runner import run_main

from gnd import cli

ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / "src/gnd/examples/disclosure"
MODEL = str(EXAMPLE / "model.orm.yaml")
POP = str(EXAMPLE / "population.json")
VARIABLE = "gnd: error: GND_DISCLOSURE must be 'internal' or 'customer'"
LOOSENING = "gnd: error: --disclosure internal is refused when GND_DISCLOSURE=customer"


def refusal(option):
    return f"gnd: error: {option} is refused in customer disclosure mode"


def gnd(monkeypatch, *argv, env=None):
    if env is None:
        monkeypatch.delenv("GND_DISCLOSURE", raising=False)
    else:
        monkeypatch.setenv("GND_DISCLOSURE", env)
    return run_main(list(argv))


# -- the CLI parser tree --------------------------------------------------------

class _Captured(Exception):
    pass


def root_parser(monkeypatch) -> argparse.ArgumentParser:
    captured = []

    def capture(self, args=None, namespace=None):
        captured.append(self)
        raise _Captured

    with monkeypatch.context() as patch:
        patch.setattr(cli._BandSafeParser, "parse_args", capture)
        with pytest.raises(_Captured):
            cli.main([])
    return captured[0]


def leaves(parser, path=("gnd",)):
    subs = [a for a in parser._actions if isinstance(a, argparse._SubParsersAction)]
    if not subs:
        yield " ".join(path), parser
        return
    for name, child in subs[0].choices.items():
        yield from leaves(child, (*path, name))


def minimal_argv(path, parser, extra=()):
    """A parseable argv for ``path``: every required argument gets a dummy value."""
    argv = list(path.split()[1:])
    for action in parser._actions:
        if isinstance(action, (argparse._HelpAction, argparse._SubParsersAction)):
            continue
        value = action.choices[0] if action.choices else "x"
        if not action.option_strings:
            argv.append(str(value))
        elif action.required:
            argv += [action.option_strings[0], str(value)]
    return [*argv, *extra]


def value_options(parser):
    return [a.option_strings[0] for a in parser._actions if a.dest in ("raw", "unredacted") and a.option_strings]


# -- T1-T3: the resolver ----------------------------------------------------------

@pytest.mark.parametrize("ctx", [None, "internal", "customer"])
@pytest.mark.parametrize("env", [None, "internal", "customer"])
def test_t1_resolve_matrix(ctx, env):
    from gnd import disclosure
    environ = {} if env is None else {"GND_DISCLOSURE": env}
    with disclosure.invocation(ctx):
        got = disclosure.resolve(environ)
    expected = "customer" if "customer" in (ctx, env) else (ctx or env)
    assert got == expected


@pytest.mark.parametrize("mode", [None, "internal", "customer"])
@pytest.mark.parametrize("requested", [False, True])
def test_t2_values_allowed_matrix(mode, requested, monkeypatch):
    from gnd import disclosure
    monkeypatch.delenv("GND_DISCLOSURE", raising=False)
    with disclosure.invocation(mode):
        if mode == "customer" and requested:
            with pytest.raises(disclosure.DisclosureRefused, match="raw=True is refused"):
                disclosure.values_allowed(requested, "raw=True")
            return
        got = disclosure.values_allowed(requested, "raw=True")
    assert got is {None: requested, "internal": True, "customer": False}[mode]


HOSTILE = ["", "Customer", "customer ", "CUSTOMER", "ïnternal", "x" * 65536]


@pytest.mark.parametrize("value", HOSTILE, ids=["empty", "title", "space", "upper", "accent", "long"])
def test_t3_hostile_values_are_refused(value, monkeypatch):
    from gnd import disclosure
    with pytest.raises(disclosure.DisclosureRefused) as error:
        disclosure.resolve({"GND_DISCLOSURE": value})
    assert value not in str(error.value) or value == ""
    result = gnd(monkeypatch, "check", MODEL, POP, env=value)
    assert (result.returncode, result.stdout) == (3, b"")
    assert result.stderr.decode().strip() == VARIABLE


# -- T4-T12: CLI resolution order, bands and refusals ---------------------------------

def test_t4_malformed_variable_is_ignored_off_disclosure_leaves(monkeypatch):
    plain = gnd(monkeypatch, "coverage", MODEL)
    bad = gnd(monkeypatch, "coverage", MODEL, env="Customer")
    assert (bad.returncode, bad.stdout) == (plain.returncode, plain.stdout)


@pytest.mark.parametrize("argv", [
    ["--disclosure", "bogus", "check", MODEL, POP],
    ["--disclosure", "customer", "--disclosure", "customer", "check", MODEL, POP],
    ["check", MODEL, POP, "--disclosure", "customer"],
], ids=["bad-value", "repeated", "after-subcommand"])
def test_t5_t6_option_usage_errors_exit_64(argv, monkeypatch):
    result = gnd(monkeypatch, *argv)
    assert (result.returncode, result.stdout) == (64, b"")


def test_t7_option_cannot_loosen_customer(monkeypatch):
    result = gnd(monkeypatch, "--disclosure", "internal", "check", MODEL, POP, env="customer")
    assert (result.returncode, result.stdout) == (3, b"")
    assert result.stderr.decode().strip() == LOOSENING


@pytest.mark.parametrize("env,option", [("customer", "customer"), ("internal", "customer"), (None, "customer")])
def test_t8_customer_from_either_source(env, option, monkeypatch):
    result = gnd(monkeypatch, "--disclosure", option, "check", MODEL, POP, "--format", "json", env=env)
    assert result.returncode == 1
    assert b"example.com" not in result.stdout
    refused = gnd(monkeypatch, "--disclosure", option, "check", MODEL, POP, "--unredacted", env=env)
    assert (refused.returncode, refused.stdout) == (3, b"")


def test_t9_malformed_variable_is_refused_before_the_option(monkeypatch):
    result = gnd(monkeypatch, "--disclosure", "internal", "check", MODEL, POP, env="Customer")
    assert (result.returncode, result.stderr.decode().strip()) == (3, VARIABLE)


def test_t10_loosening_is_refused_before_raw_requests(monkeypatch):
    result = gnd(monkeypatch, "--disclosure", "internal", "check", MODEL, POP, "--unredacted", env="customer")
    assert (result.returncode, result.stderr.decode().strip()) == (3, LOOSENING)


def test_t11_every_raw_request_is_refused_under_customer(monkeypatch):
    calls = []
    monkeypatch.setattr(cli, "_run_handler", lambda args: calls.append(args) or 0)
    found = []
    for path, parser in leaves(root_parser(monkeypatch)):
        for option in value_options(parser):
            found.append((path, option))
            result = gnd(monkeypatch, *minimal_argv(path, parser, [option]), env="customer")
            assert (result.returncode, result.stdout) == (3, b""), (path, option, result.stderr)
            assert result.stderr.decode().strip() == refusal(option), path
    assert calls == []
    # 7 leaves with --unredacted and 8 with --raw (spec, implementability sweep).
    assert sorted(o for _, o in found).count("--unredacted") == 7
    assert sorted(o for _, o in found).count("--raw") == 8


def test_t12_the_cli_mode_does_not_leak_after_main(monkeypatch):
    from gnd import disclosure
    gnd(monkeypatch, "--disclosure", "internal", "check", MODEL, POP)
    assert disclosure.resolve({}) is None
    gnd(monkeypatch, "--disclosure", "customer", "check", MODEL, POP)
    assert disclosure.resolve({}) is None
