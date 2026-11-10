"""NM2: the disclosure mode (why-not-near-misses notes/phase-NM2-spec.md)."""

from __future__ import annotations

import argparse
import contextlib
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


TYPED = {"requested_at": "2026-11-01T00:00:00Z"}   # arguments whose type rejects "x"


def minimal_argv(path, parser, extra=()):
    """A parseable argv for ``path``: every required argument gets a dummy value."""
    argv = list(path.split()[1:])
    for action in parser._actions:
        if isinstance(action, (argparse._HelpAction, argparse._SubParsersAction)):
            continue
        value = action.choices[0] if action.choices else TYPED.get(action.dest, "x")
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
    monkeypatch.setattr(cli, "_run_handler", lambda handler, args: calls.append(args) or 0)
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


# -- T13-T15: the disclosure table --------------------------------------------------

def table_keys(monkeypatch):
    import inspect

    from gnd import api, redaction
    from gnd.export import service
    leaves_found = {path for path, _ in leaves(root_parser(monkeypatch))}
    api_names = {f"api:{n}" for n in dir(api)
                 if not n.startswith("_") and callable(getattr(api, n)) and not inspect.ismodule(getattr(api, n))}
    session = {f"api:EvaluationSession.{n}" for n, v in vars(api.EvaluationSession).items()
               if not n.startswith("_") and callable(v)}
    export = {f"export.service:{n}" for n in dir(service)
              if not n.startswith("_") and inspect.isfunction(getattr(service, n))
              and getattr(service, n).__module__ == "gnd.api"}
    kinds = {f"kind:{k}" for k in redaction.OutputKind.__args__}
    return leaves_found | api_names | session | export | kinds


def assert_table(surfaces, keys):
    assert set(surfaces) == keys, (sorted(keys - set(surfaces)), sorted(set(surfaces) - keys))


def test_t13_the_table_is_total_and_live(monkeypatch):
    from gnd.disclosure import SURFACES
    keys = table_keys(monkeypatch)
    assert sum(k.startswith("gnd ") for k in keys) == 50  # MC2 model-review leaf
    assert_table(SURFACES, keys)


@pytest.mark.parametrize("damage", ["missing", "stale"])
def test_t14_the_table_check_fails_on_damage(damage, monkeypatch):
    from gnd.disclosure import SURFACES, Surface
    surfaces = dict(SURFACES)
    if damage == "missing":
        surfaces.pop("gnd why-not")
    else:
        surfaces["gnd no-such-command"] = Surface("value-free")
    with pytest.raises(AssertionError):
        assert_table(surfaces, table_keys(monkeypatch))


#: Which test discharges each site and every-mode row (T15).
CASES = {
    "declared-cli": "test_t16_the_cli_walk_sets_every_value_dest",
    "declared-api": "test_t16_api_check_family_leaks_nothing_under_customer",
    "view-cli": "test_t22_t23_cli_views_follow_the_mode",
    "view-api": "test_t19_t20_witness_lane_api",
    "export": "test_t25_export_functions_resolve_raw",
    "every-mode": "test_t26_every_mode_and_value_free_leaves_see_no_mode",
    "option-cli": "test_ct4_discover_show_values_follows_the_mode",
    "session": "test_t30_t31_sessions_forward_customer_only",
}


def test_t15_every_row_has_a_discharging_case():
    # A registry check: every governed row maps to a named case and every case is used.
    # The discharge itself is shown by the named tests, not here.
    from gnd.disclosure import SURFACES
    names = set(globals())
    assert all(test in names for test in CASES.values())
    used = set()
    for key, surface in SURFACES.items():
        if surface.kind == "value-free" and not surface.spawns:
            continue
        if key.startswith("kind:"):
            group = "session" if key.startswith("kind:session") else "declared-api"
        elif key.startswith("gnd "):
            group = ("declared-cli" if surface.convention == "declared" else "option-cli"
                     if surface.convention == "option" else "view-cli" if surface.convention
                     else "session" if key == "gnd exp run" else "every-mode")
        elif key.startswith("export.service:") or key.split(":")[1] in (
                "export_lean", "export_souffle", "run_souffle", "souffle_witness"):
            group = "export"
        else:
            group = ("declared-api" if surface.convention == "declared" else "view-api" if surface.convention
                     else "every-mode")
        assert group in CASES, key
        used.add(group)
    assert used == set(CASES)


# -- T16-T18, T27: the check family ---------------------------------------------------

def captured_namespaces(monkeypatch, argv, env=None):
    seen = []
    monkeypatch.setattr(cli, "_run_handler",
                        lambda handler, args: seen.append({k: v for k, v in vars(args).items()
                                                          if k != "handler" and not k.startswith("_seen_")}) or 0)
    result = gnd(monkeypatch, *argv, env=env)
    return result, seen


def test_t16_the_cli_walk_sets_every_value_dest(monkeypatch):
    sites = 0
    for path, parser in leaves(root_parser(monkeypatch)):
        options = value_options(parser)
        if not options:
            continue
        sites += 1
        dests = [o.lstrip("-") for o in options]
        argv = minimal_argv(path, parser)
        _, unset = captured_namespaces(monkeypatch, argv)
        _, internal = captured_namespaces(monkeypatch, ["--disclosure", "internal", *argv])
        _, customer = captured_namespaces(monkeypatch, argv, env="customer")
        for dest in dests:
            assert (unset[0][dest], internal[0][dest], customer[0][dest]) == (False, True, False), path
    assert sites == 15


def _emails(payload):
    import json
    text = json.dumps(payload) if not isinstance(payload, (bytes, str)) else (
        payload.decode() if isinstance(payload, bytes) else payload)
    return "ann@example.com" in text


def test_t16_cli_check_leaks_nothing_under_customer(monkeypatch):
    argv = ["check", MODEL, POP, "--format", "json"]
    unset = gnd(monkeypatch, *argv)
    customer = gnd(monkeypatch, *argv, env="customer")
    internal = gnd(monkeypatch, "--disclosure", "internal", *argv)
    raw = gnd(monkeypatch, *argv, "--unredacted")
    assert (unset.returncode, customer.returncode, internal.returncode) == (1, 1, 1)
    assert not _emails(unset.stdout) and not _emails(customer.stdout)
    assert customer.stdout == unset.stdout                       # T18 parity of the redacted default
    assert internal.stdout == raw.stdout and _emails(internal.stdout)   # T17


def test_t16_api_check_family_leaks_nothing_under_customer(monkeypatch):
    from gnd import api, disclosure
    from gnd.model import load_model
    from gnd.population import load_population
    monkeypatch.delenv("GND_DISCLOSURE", raising=False)
    model = load_model(MODEL)
    population = load_population(POP, model=model)
    calls = {
        "check": lambda **kw: api.check(MODEL, POP, **kw),
        "verbalize": lambda **kw: api.verbalize(MODEL, POP, **kw),
        "check_with_receipt": lambda **kw: api.check_with_receipt(model, population, **kw)[0],
        "session.check": lambda **kw: api.EvaluationSession(model).check(population, **kw),
        "session.check_with_receipt": lambda **kw: api.EvaluationSession(model).check_with_receipt(population, **kw)[0],
    }
    for name, call in calls.items():
        unset = call()
        with disclosure.invocation("customer"):
            customer = call()
            with pytest.raises(disclosure.DisclosureRefused, match="unredacted=True is refused"):
                call(unredacted=True)
        with disclosure.invocation("internal"):
            internal = call()
        assert not _emails(unset) and not _emails(customer), name
        assert customer == unset, name
        assert internal == call(unredacted=True) and _emails(internal), name
    refused = {
        "validate": lambda: api.validate(MODEL, unredacted=True),
        "diff": lambda: api.diff(MODEL, MODEL, unredacted=True),
        "transition": lambda: api.transition(MODEL, POP, {}, unredacted=True),
        "judgments": lambda: api.judgments("m", "p", "q", "r", trusted_root=".", unredacted=True),
        "session.transition": lambda: api.EvaluationSession(model).transition(population, {}, unredacted=True),
    }
    with disclosure.invocation("customer"):
        for name, call in refused.items():
            with pytest.raises(disclosure.DisclosureRefused):
                call()


def test_t27_internal_callers_are_not_refused(monkeypatch):
    from gnd import api, disclosure
    seen = []
    monkeypatch.setattr(api, "_check_unresolved", lambda *a, **kw: seen.append(kw.get("unredacted")) or {})
    from gnd.model import load_model
    from gnd.population import load_population
    model = load_model(MODEL)
    session = api.EvaluationSession(model)
    monkeypatch.setattr(api, "build_feedback", lambda *a, **kw: {}, raising=False)
    with disclosure.invocation("internal"), contextlib.suppress(Exception):
        # Only the flag handed to the check matters; the stubbed payload may not build feedback.
        session.check_with_feedback(load_population(POP, model=model), attempt=1)
    assert seen[:1] == [False]


# -- T19-T25: the witness lane and exports ---------------------------------------------

WHY = ROOT / "tests/fixtures/why_not/claims"
DISPATCH = ROOT / "tests/fixtures/v71/phase3/dispatch"


def test_t19_t20_witness_lane_api(monkeypatch):
    from gnd import api, disclosure
    from gnd.witness import service
    from gnd.witness.view import result_view, why_not_view
    monkeypatch.delenv("GND_DISCLOSURE", raising=False)
    calls = {
        "why_not": (lambda: api.why_not(WHY / "model.orm.json", WHY / "gap.pop.json", "credited"),
                    lambda raw: {**why_not_view(raw), "view": "redacted"}),
        "witness": (lambda: api.witness(DISPATCH / "model.orm.yaml", DISPATCH / "candidate.pop.json",
                                        DISPATCH / "targets.json"), result_view),
        "replay": (lambda: api.replay(DISPATCH / "model.orm.yaml", DISPATCH / "candidate.pop.json",
                                      DISPATCH / "direct.witness.json"), result_view),
    }
    for name, (call, project) in calls.items():
        unset = call()
        with disclosure.invocation("internal"):
            internal = call()
        with disclosure.invocation("customer"):
            customer = call()
        assert unset == internal and "view" not in unset, name
        assert customer == project(unset) and customer != unset, name
        assert getattr(api, name) is getattr(service, name)        # T21


def cli_json(monkeypatch, *argv, env=None):
    import json
    result = gnd(monkeypatch, *argv, env=env)
    return result.returncode, json.loads(result.stdout) if result.stdout else None


VIEW_CALLS = {
    "why-not": ["why-not", str(WHY / "model.orm.json"), str(WHY / "gap.pop.json"), "--fact-type", "credited"],
    "witness": ["witness", str(DISPATCH / "model.orm.yaml"), str(DISPATCH / "candidate.pop.json"),
                "--targets", str(DISPATCH / "targets.json")],
    "replay": ["replay", str(DISPATCH / "model.orm.yaml"), str(DISPATCH / "candidate.pop.json"),
               str(DISPATCH / "direct.witness.json")],
    "witness-view": ["witness-view", str(DISPATCH / "direct.witness.json")],
}


@pytest.mark.parametrize("name", list(VIEW_CALLS))
def test_t22_t23_cli_views_follow_the_mode(name, monkeypatch):
    argv = VIEW_CALLS[name]
    default = cli_json(monkeypatch, *argv)
    raw = cli_json(monkeypatch, *argv, "--raw")
    assert default != raw
    assert cli_json(monkeypatch, *argv, env="customer") == default            # T22
    assert cli_json(monkeypatch, "--disclosure", "internal", *argv) == raw    # T23


def test_t24_witness_out_under_internal(tmp_path, monkeypatch):
    argv = VIEW_CALLS["witness"]
    a, b = tmp_path / "a.json", tmp_path / "b.json"
    unset = gnd(monkeypatch, *argv, "--raw", "--out", str(a))
    internal = gnd(monkeypatch, "--disclosure", "internal", *argv, "--out", str(b))
    assert (unset.returncode, unset.stdout) == (internal.returncode, internal.stdout)
    assert a.read_bytes() == b.read_bytes() and a.stat().st_size > 0
    refused = gnd(monkeypatch, *argv, "--out", str(tmp_path / "c.json"), env="customer")
    assert refused.returncode == 3 and not (tmp_path / "c.json").exists()


def test_t25_export_functions_resolve_raw(monkeypatch, tmp_path):
    from gnd import disclosure
    from gnd.export import service
    seen = {}
    with disclosure.invocation("customer"):
        for name, call in {
            "export_lean": lambda: service.export_lean("m", "p", toolchain="t", raw=True),
            "export_souffle": lambda: service.export_souffle("m", "p", raw=True),
            "run_souffle": lambda: service.run_souffle("b", raw=True),
            "souffle_witness": lambda: service.souffle_witness("b", "t", raw=True),
        }.items():
            with pytest.raises(disclosure.DisclosureRefused, match="raw=True is refused"):
                call()
            seen[name] = True
    # internal acts as raw=True, unset passes raw through: observed at the I/O seam.
    from gnd.export import souffle_io
    passed = []
    monkeypatch.setattr(souffle_io, "export_souffle", lambda *a, **kw: passed.append(kw["raw"]) or _Dump())
    service.export_souffle("m", "p")
    with disclosure.invocation("internal"):
        service.export_souffle("m", "p")
    with disclosure.invocation("customer"):
        service.export_souffle("m", "p")
    assert passed == [False, True, False]
    assert len(seen) == 4
    from gnd.export import souffle_runtime
    monkeypatch.setattr(souffle_runtime, "run_souffle",
                        lambda *a, **kw: {"extensions": {"t": [["v"]]}, "tool": {"path": "p", "sha256": "s"}})
    unset = service.run_souffle("b")
    with disclosure.invocation("internal"):
        internal = service.run_souffle("b")
    with disclosure.invocation("customer"):
        customer = service.run_souffle("b")
    assert unset == customer == {"extensions": None, "tool": {"path": None, "sha256": None}}
    assert internal == service.run_souffle("b", raw=True) and internal["extensions"]


class _Dump:
    def model_dump(self):
        return {}


# -- T26: rows that do not follow the mode ----------------------------------------------

def test_t26_every_mode_and_value_free_leaves_see_no_mode(monkeypatch):
    from gnd import disclosure
    checked = 0
    for path, parser in leaves(root_parser(monkeypatch)):
        if disclosure.bearing(path):
            continue
        argv = minimal_argv(path, parser)
        _, unset = captured_namespaces(monkeypatch, argv)
        _, internal = captured_namespaces(monkeypatch, ["--disclosure", "internal", *argv])
        _, customer = captured_namespaces(monkeypatch, argv, env="customer")
        _, malformed = captured_namespaces(monkeypatch, argv, env="Customer")
        for other in (internal, customer, malformed):
            assert {k: v for k, v in other[0].items() if k != "disclosure"} == \
                   {k: v for k, v in unset[0].items() if k != "disclosure"}, path
        checked += 1
    assert checked == 50 - 16 - 4   # minus the site leaves and the spawners


# -- T28-T34b: child processes -------------------------------------------------------------

SPAWN_SITES = {
    ("gnd/process.py", "run_bounded_process"), ("gnd/agents.py", "invoke_agent"),
    ("gnd/declared_adapter.py", "_invoke_command"), ("gnd/exp/session.py", "run_gnd_verifier"),
    ("gnd/exp/tests_runner.py", "run_tests_mode"), ("gnd/review/adapters.py", "run_reviewer_adapter"),
    ("gnd/export/applications.py", "_child"), ("gnd/export/souffle_runtime.py", "command"),
    ("gnd/export/lean_runtime.py", "run"), ("gnd/solve.py", "_run_child"), ("gnd/archsmoke.py", "run_row"),
}
SPAWN_CALLS = {"create_subprocess_exec", "create_subprocess_shell", "Popen", "run", "check_output",
               "check_call", "call", "system", "popen", "execv", "execve", "execvp", "spawnv"}


def test_t28_every_spawner_has_a_rule():
    import ast
    import json as _json
    layers = _json.loads((ROOT / "tools/gnd_layers.json").read_text())
    excluded = tuple(p.rstrip("*").rstrip("/") for p in layers["excluded"])
    found = set()
    for path in sorted((ROOT / "src").rglob("*.py")):
        rel = path.relative_to(ROOT / "src").as_posix()
        if rel.startswith(tuple(e.replace("src/", "") for e in excluded)) or "/examples/" in rel or "/skills/" in rel:
            continue
        tree = ast.parse(path.read_text())
        parents = {c: n for n in ast.walk(tree) for c in ast.iter_child_nodes(n)}
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            func = node.func
            name = func.attr if isinstance(func, ast.Attribute) else getattr(func, "id", None)
            base = getattr(getattr(func, "value", None), "id", None)
            spawn = (name in {"create_subprocess_exec", "create_subprocess_shell", "run_bounded_process"}
                     or (base in {"subprocess", "os"} and name in SPAWN_CALLS))
            if not spawn:
                continue
            owner = node
            while owner in parents and not isinstance(owner, (ast.FunctionDef, ast.AsyncFunctionDef)):
                owner = parents[owner]
            found.add((rel, getattr(owner, "name", "<module>")))
    # lean_runtime reaches souffle_runtime.command, whose row covers it.
    assert found == SPAWN_SITES - {("gnd/export/lean_runtime.py", "run")}, found


def test_t30_t31_sessions_forward_customer_only(tmp_path, monkeypatch):
    import json as _json

    import test_rf1_session_pins as pins
    environments = {}
    for version in (4, 6):
        for mode in (None, "internal", "customer"):
            work = tmp_path / f"v{version}-{mode}"
            work.mkdir()
            with monkeypatch.context() as patch:
                built = pins.BUILDERS[version](work, patch)
                if mode is None:
                    patch.delenv("GND_DISCLOSURE", raising=False)
                else:
                    patch.setenv("GND_DISCLOSURE", mode)
                run_main(built.argv, cwd=work)
                attempt = built.root / "runs/run-0001/attempts/0001/attempt.json"
                environments[version, mode] = _json.loads(attempt.read_text())["invocation"]["environment"]
        unset = environments[version, None]
        assert environments[version, "internal"] == unset, version                       # T29
        assert {"name": "GND_DISCLOSURE", "provenance": "supplied"} in environments[version, "customer"]
        assert [f for f in environments[version, "customer"] if f["name"] != "GND_DISCLOSURE"] == unset


def test_t32_solve_forwards_customer_only(monkeypatch):
    import subprocess

    from gnd import disclosure, solve
    seen = []

    def fake(argv, **kwargs):
        seen.append(kwargs)
        raise OSError("stop")

    monkeypatch.setattr(subprocess, "Popen", fake)
    for mode in (None, "internal", "customer"):
        with disclosure.invocation(mode):
            assert solve._run_child(_Spawn(), None, None).halt == "spawn-error"
    assert "env" not in seen[0] and "env" not in seen[1]
    assert seen[2]["env"]["GND_DISCLOSURE"] == "customer"


class _Spawn:
    argv = ("python", "-c", "pass")
    cwd = ROOT
    timeout_s = 1


def test_t33_reviewer_forwards_customer_only(tmp_path, monkeypatch):
    import asyncio
    import time

    from gnd import disclosure
    from gnd.review import adapters
    policy = adapters.reviewer_policies()[0]
    executable = tmp_path / policy.executable_name
    executable.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
    executable.chmod(0o755)
    info = executable.stat()
    resolved = adapters.ResolvedReviewerPolicy(policy=policy, executable=str(executable),
                                               executable_identity=(info.st_dev, info.st_ino, info.st_size,
                                                                    info.st_mtime_ns))
    seen = []

    class Stop(Exception):
        pass

    async def bounded(argv, **kwargs):
        seen.append(kwargs)
        raise Stop

    monkeypatch.setattr(adapters, "run_bounded_process", bounded)
    for mode in (None, "internal", "customer"):
        with disclosure.invocation(mode), pytest.raises(Stop):
            asyncio.run(adapters.run_reviewer_adapter(
                resolved, prompt=b"p", cwd=tmp_path, environment={"PATH": str(tmp_path)},
                deadline=time.monotonic() + 5, terminate_grace_seconds=0.1, stdout_limit_bytes=1024,
                stderr_limit_bytes=1024, total_output_limit_bytes=2048))
    assert seen[0]["env"] == seen[1]["env"] and "GND_DISCLOSURE" not in seen[0]["env"]
    assert seen[1]["disclosed_names"] == frozenset()
    assert seen[0]["disclosed_names"] == frozenset()
    assert seen[2]["env"]["GND_DISCLOSURE"] == "customer"
    assert seen[2]["disclosed_names"] == frozenset({"GND_DISCLOSURE"})


def test_t34_the_verifier_never_carries_the_mode(monkeypatch):
    from gnd import disclosure
    from gnd.exp import session_environment, tests_runner
    monkeypatch.setenv("GND_DISCLOSURE", "customer")
    with disclosure.invocation("customer"):
        assert "GND_DISCLOSURE" not in session_environment.verifier_environment()
        assert "GND_DISCLOSURE" not in tests_runner.tests_environment()


def test_t34b_disclosed_names_are_not_masked(tmp_path):
    import asyncio
    import sys

    from gnd.process import ProcessLimits, run_bounded_process
    argv = (sys.executable, "-c", "import os; print(os.environ['GND_DISCLOSURE'], os.environ['SECRET_X'])")
    env = {"GND_DISCLOSURE": "customer", "SECRET_X": "hunter22", "PATH": ""}
    limits = ProcessLimits(timeout_seconds=10, terminate_grace_seconds=0.5, stdin_limit_bytes=0,
                           stdout_limit_bytes=4096, stderr_limit_bytes=4096, total_output_limit_bytes=8192)
    plain = asyncio.run(run_bounded_process(argv, cwd=tmp_path, env=env, limits=limits))
    named = asyncio.run(run_bounded_process(argv, cwd=tmp_path, env=env, limits=limits,
                                            disclosed_names=frozenset({"GND_DISCLOSURE"})))
    assert plain.stdout.split() == [b"***", b"***"]
    assert named.stdout.split() == [b"customer", b"***"]


# -- T37-T40: isolation, example, help ------------------------------------------------------

def test_t37_the_ambient_variable_is_scrubbed():
    import os
    assert "GND_DISCLOSURE" not in os.environ


def test_t38_parity_holds_with_an_ambient_variable(tmp_path):
    import os
    import subprocess
    import sys
    env = {**os.environ, "GND_DISCLOSURE": "customer"}
    done = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider",
                           "tests/test_disclosure_mode.py::test_t16_cli_check_leaks_nothing_under_customer",
                           "tests/test_disclosure_mode.py::test_t37_the_ambient_variable_is_scrubbed",
                           "tests/test_rf1_cli_pins.py"],
                          cwd=ROOT, env=env, capture_output=True, text=True, check=False)
    assert done.returncode == 0, done.stdout[-2000:]


def test_close_r4_the_tutorial_runner_scrubs_an_ambient_variable(tmp_path, monkeypatch):
    import importlib.util
    import sys
    spec = importlib.util.spec_from_file_location("run_tutorials", ROOT / "tools" / "run_tutorials.py")
    runner = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(runner)
    page = tmp_path / "doc.md"
    page.write_text("<!-- gnd-run expect=0 -->\n```python\nimport os\n"
                    "assert 'GND_DISCLOSURE' not in os.environ\n```")
    monkeypatch.setenv("GND_DISCLOSURE", "customer")
    assert runner.run_pages([page], tmp_path / "run", Path(sys.executable)) == 1


def test_t39_the_packaged_example(monkeypatch):
    result = gnd(monkeypatch, "check", MODEL, POP, "--format", "json")
    assert result.returncode == 1 and b'"redacted": true' in result.stdout.replace(b'"redacted":true', b'"redacted": true')
    assert gnd(monkeypatch, "validate", MODEL).returncode == 0


def test_t40_help_names_the_root_option(monkeypatch):
    result = gnd(monkeypatch, "--help")
    text = " ".join(result.stdout.decode().split())
    assert "--disclosure {internal,customer}" in text and "a root option" in text


# -- NM2 review regressions (notes/phase-NM2-claude-review.md) ---------------------------

def _doccheck_case(tmp_path):
    import hashlib
    import json as _json
    import os
    import subprocess
    import sys
    sha = lambda data: hashlib.sha256(data).hexdigest()
    env = {k: v for k, v in os.environ.items() if k != "GND_DISCLOSURE"}
    subprocess.run([sys.executable, "-m", "gnd", "extract", MODEL, "--out", str(tmp_path / "artifacts")],
                   check=True, env=env, capture_output=True)
    pop = _json.loads(Path(POP).read_text())
    pop["facts"]["has_email"] = [{"customer": "c-2", "email": "bo@example.com"}]
    (tmp_path / "pop.json").write_text(_json.dumps(pop))
    doc = ("Customer c-2 is on file.\nThe office ficus is thriving.\nCustomer c-9 called.\n"
           "Customer c-2 has email zed@example.org.\n")
    (tmp_path / "doc.md").write_text(doc)
    applicable = next((tmp_path / "artifacts").glob("*.applicable.json"))
    manifest = {
        "schema_version": 1, "document": "doc.md", "document_sha256": sha(doc.encode()),
        "model": "model.orm.yaml", "model_sha256": sha(Path(MODEL).read_bytes()),
        "source_population": "pop.json", "source_population_sha256": sha((tmp_path / "pop.json").read_bytes()),
        "applicable_sha256": sha(applicable.read_bytes()), "renderer_skill": "gnd-render-doc",
        "renderer_skill_version": "1", "executing_model": "x",
        "distractors": [
            {"kind": "out-of-model", "text": "The office ficus is thriving."},
            {"kind": "near-miss-entity", "text": "Customer c-9 called."},
            {"kind": "absent-fact", "text": "Customer c-2 has email zed@example.org.", "fact_type": "has_email",
             "roles": {"customer": "c-2", "email": "zed@example.org"}}]}
    (tmp_path / "manifest.json").write_text(_json.dumps(manifest))
    return ["doccheck", MODEL, str(tmp_path / "manifest.json"), "--artifacts", str(tmp_path / "artifacts")]


def test_review_r1_doccheck_emits_values_in_every_mode(tmp_path, monkeypatch):
    from gnd.disclosure import SURFACES
    argv = _doccheck_case(tmp_path)
    unset = gnd(monkeypatch, *argv)
    customer = gnd(monkeypatch, *argv, env="customer")
    internal = gnd(monkeypatch, "--disclosure", "internal", *argv)
    assert b"bo@example.com" in unset.stdout + unset.stderr
    assert (customer.returncode, customer.stdout, customer.stderr) == (unset.returncode, unset.stdout, unset.stderr)
    assert (internal.returncode, internal.stdout) == (unset.returncode, unset.stdout)
    assert SURFACES["gnd doccheck"].kind == "every-mode"


def test_review_r2_raw_bodies_keep_the_rf4_base_algorithm():
    import ast
    import hashlib
    import json
    import subprocess

    import test_rf4_peripheral as rf4
    current = (ROOT / "src/gnd/witness/service.py").read_text()
    for name in ("witness", "replay"):
        base = subprocess.check_output(["git", "show", f"{rf4.BASE}:src/gnd/api.py"], cwd=ROOT, text=True)
        before = rf4._definition(base, name)
        after = rf4._definition(current, f"{name}_result")
        after = ast.parse(ast.unparse(after)).body[0]
        after.name = name
        assert rf4._import_bindings(before) == rf4._import_bindings(after), name
        successors = json.loads((ROOT / '.gnd-planning/milestones/model-composition/evidence/MC1/raw-view-successors.json').read_text())
        successor = next(row for row in successors if row['name'] == name)
        assert successor['reason']
        assert hashlib.sha256(rf4._algorithm(before).encode()).hexdigest() == successor['before'], name
        assert hashlib.sha256(rf4._algorithm(after).encode()).hexdigest() == successor['after'], name


def test_review_r3_only_named_values_are_unmasked(tmp_path, monkeypatch):
    import asyncio

    from gnd.agents import AgentAdapterId, invoke_agent
    (tmp_path / "codex").write_text("#!/bin/sh\necho key=$ANTHROPIC_API_KEY mode=$GND_DISCLOSURE\n")
    (tmp_path / "codex").chmod(0o755)
    monkeypatch.setenv("PATH", f"{tmp_path}:/usr/bin:/bin")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ambient-secret-1111")

    def call(**kwargs):
        return asyncio.run(invoke_agent(AgentAdapterId.codex, prompt="p", cwd=tmp_path, timeout_seconds=10,
                                        **kwargs))
    forwarded = call(extra_environment={"GND_DISCLOSURE": "customer"},
                     disclosed_names=frozenset({"GND_DISCLOSURE"}))
    assert forwarded.stdout.strip() == b"key=*** mode=customer"
    override = call(extra_environment={"ANTHROPIC_API_KEY": "sk-override-secret-2222"})
    assert b"sk-override" not in override.stdout
    assert [(f.name, f.provenance) for f in override.environment if f.name == "ANTHROPIC_API_KEY"] == [
        ("ANTHROPIC_API_KEY", "supplied")]


def test_review_r4_an_enclosing_customer_context_holds_in_process(monkeypatch):
    from gnd import disclosure
    monkeypatch.delenv("GND_DISCLOSURE", raising=False)
    with disclosure.invocation("customer"):
        refused = run_main(["check", MODEL, POP, "--unredacted"])
        loosen = run_main(["--disclosure", "internal", "check", MODEL, POP])
        default = run_main(["check", MODEL, POP, "--format", "json"])
    assert (refused.returncode, refused.stdout) == (3, b"")
    assert loosen.returncode == 3 and loosen.stderr.decode().strip() == LOOSENING
    assert default.returncode == 1 and b"example.com" not in default.stdout


def test_close_r2_a_nested_value_free_invocation_keeps_an_enclosing_customer(monkeypatch):
    """Close reader 2 F2: a value-free leaf runs with no mode of its own; it must not clear customer."""
    from gnd import cli, disclosure
    monkeypatch.delenv("GND_DISCLOSURE", raising=False)
    seen = []
    monkeypatch.setattr(cli, "_run_handler", lambda handler, args: seen.append((disclosure.resolve(), disclosure.forward())) or 0)
    with disclosure.invocation("customer"):
        assert cli.main(["doctor"]) == 0
        with disclosure.invocation(None):
            inner = disclosure.resolve()
    with disclosure.invocation(None):
        unset = disclosure.resolve()
    assert seen == [("customer", {"GND_DISCLOSURE": "customer"})]
    assert (inner, unset, disclosure.resolve()) == ("customer", None, None)


def test_review_r5_judgments_and_feedback_bypass_the_mode(tmp_path, monkeypatch):
    from gnd import api, disclosure, judgments
    from gnd.model import load_model
    from gnd.population import load_population
    monkeypatch.setattr(judgments, "read_judgment_policy", lambda raw: {})
    monkeypatch.setattr(judgments, "read_judgment_receipts", lambda raw: [])
    monkeypatch.setattr(judgments, "evaluate_judgments", lambda *a, **k: {"admission": True})
    monkeypatch.setattr(judgments, "redact_policy", lambda d: {"redacted": True})
    (tmp_path / "policy").write_text("{}")
    (tmp_path / "receipts").write_text("[]")

    def run():
        return api.judgments(MODEL, POP, tmp_path / "policy", tmp_path / "receipts", trusted_root=tmp_path)
    unset = run()
    with disclosure.invocation("customer"):
        customer = run()
    with disclosure.invocation("internal"):
        internal = run()
    assert unset["outcome"] == customer["outcome"] == 0 and customer["error"] is None
    assert customer == unset and not _emails(customer["mechanical_report"])
    assert _emails(internal["mechanical_report"]) and internal["judgment_policy"] == {"admission": True}
    model = load_model(MODEL)
    session = api.EvaluationSession(model)
    with disclosure.invocation("internal"):
        payload, _feedback = session.check_with_feedback(load_population(POP, model=model), attempt=1)
    assert not _emails(payload)


def test_review_r6_internal_reaches_every_api_check_function(monkeypatch, tmp_path):
    import shutil

    from gnd import api, disclosure
    seen = {}
    real_validate, real_transition = api._run_validate, api._run_transition
    monkeypatch.setattr(api, "_run_validate",
                        lambda *a, unredacted, **k: seen.setdefault("validate", unredacted) and real_validate(
                            *a, unredacted=unredacted, **k) or real_validate(*a, unredacted=unredacted, **k))
    monkeypatch.setattr(api, "_run_transition",
                        lambda *a, unredacted, **k: seen.setdefault("transition", unredacted) is None or
                        real_transition(*a, unredacted=unredacted, **k))
    populations = tmp_path / "pops"
    populations.mkdir()
    shutil.copy(POP, populations / "population.json")
    # Without the constraint, the diff reports the facts the constraint flagged.
    text = Path(MODEL).read_text()
    model_b = tmp_path / "model_b.orm.yaml"
    model_b.write_text(text[:text.index("    constraints:")])
    unset_diff = api.diff(MODEL, model_b, populations=populations, unredacted=True)
    assert _emails(unset_diff) and not _emails(api.diff(MODEL, model_b, populations=populations))
    with disclosure.invocation("internal"):
        api.validate(MODEL)
        try:
            api.transition(MODEL, POP, {"version": 1, "steps": []})
        except Exception:  # noqa: BLE001 -- only the flag handed to the helper matters
            seen.setdefault("transition", None)
        internal_diff = api.diff(MODEL, model_b, populations=populations)
    assert seen["validate"] is True and seen["transition"] is True
    assert internal_diff == unset_diff


def test_review_r7_discover_output_is_the_same_in_every_mode(tmp_path, monkeypatch):
    outputs = []
    modes = [([], None), ([], "customer"), (["--disclosure", "internal"], None)]
    for index, (prefix, env) in enumerate(modes):
        work = tmp_path / f"run{index}"
        work.mkdir()
        result = gnd(monkeypatch, *prefix, "discover", MODEL, POP, "--out", str(work / "out"),
                     "--report", str(work / "report.json"), "--actor", "a",
                     "--requested-at", "2026-11-01T00:00:00Z", "--format", "json", env=env)
        outputs.append((result.returncode, result.stdout.replace(str(work).encode(), b"<work>"),
                        (work / "report.json").read_bytes().replace(str(work).encode(), b"<work>")))
    assert outputs[0][0] == 0
    assert outputs[0] == outputs[1] == outputs[2]


def test_ct4_discover_show_values_follows_the_mode():
    # CT-D13 (a): the one option a site decides with values_allowed.
    from gnd.disclosure import DisclosureRefused, invocation, values_allowed

    with invocation(None):
        assert values_allowed(False, "--show-values") is False
        assert values_allowed(True, "--show-values") is True
    with invocation("internal"):
        assert values_allowed(False, "--show-values") is True
    with invocation("customer"):
        assert values_allowed(False, "--show-values") is False
        with pytest.raises(DisclosureRefused, match="--show-values"):
            values_allowed(True, "--show-values")
