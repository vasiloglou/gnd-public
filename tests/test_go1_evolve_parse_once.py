"""GO1: one `gnd evolve` command parses each model text once per reader (#228).

Spec: .gnd-planning/milestones/growth-round-outcomes/notes/phase-GO1-spec.md
(§8, T1-T8; T9 is the existing evolve lane, which runs with the scope's write
check switched on by the autouse fixture in conftest.py). T1-T7 read no clock.
T8 is the one timed case: it is marked `slow`, which the default lane excludes,
and is run once for the phase record.
"""

from __future__ import annotations

import contextlib
import json
import shutil
import time
from collections.abc import Callable, Iterator
from pathlib import Path
from typing import Any

import pytest
import test_evolve_additive_policy as policy
import test_evolve_loading as loading
import test_mc3_evolution as mc3
import test_unattended_growth_guidance as growth
import test_unattended_model_growth_acceptance as acceptance
from ruamel.yaml import YAML
from support.cli_runner import run_main

from gnd.errors import ModelLoadError
from gnd.model import _parsing

# --- fixtures: the unattended seed grown by N groups, and one round of the acceptance replay ------


def _bulk(n: int) -> tuple[bytes, dict[str, Any]]:
    """A document and a reply of ``n`` groups: an entity, its reference value, one more value and a
    binary fact type, each citing a span of the document. 3n object types, n fact types."""
    lines, object_types, fact_types = [], [], []
    for i in range(n):
        tag = f"G{i:05d}"
        lines.append(f"{tag} widget is named. {tag} code is kept. {tag} size is measured. "
                     f"A widget-{tag} has a size-{tag}.")
        object_types += [
            acceptance._entity(f"w{i}", f"Widget{i}", f"w{i}_code", f"{tag} widget is"),
            acceptance._value(f"w{i}_code", f"Widget{i}Code", "String", f"{tag} code is"),
            acceptance._value(f"w{i}_size", f"Widget{i}Size", "Integer", f"{tag} size is"),
        ]
        fact_types.append(acceptance._fact(f"w{i}_has_size", f"{{Widget{i}}} has {{Widget{i}Size}}",
                                           (f"w{i}", f"w{i}_size"), f"widget-{tag} has a size-{tag}"))
    raw = ("\n".join(lines) + "\n").encode("utf-8")
    return raw, {"document": "bulk.txt", "object_types": object_types, "fact_types": fact_types,
                 "subtype_links": [], "constraints": []}


def _grown_workspace(root: Path, n: int) -> dict[str, Path]:
    """The acceptance replay's seed plus ``n`` groups, with round 1's proposal written."""
    ws = acceptance._workspace(root)
    if n:
        raw, reply = _bulk(n)
        grown = growth._translate(reply, raw)
        yaml = YAML()
        document = yaml.load(ws["model"].read_text(encoding="utf-8"))
        document["source"]["documents"].append(grown["source"]["documents"][0])
        document["object_types"].extend(grown["object_types"])
        document["fact_types"].extend(grown["fact_types"])
        with ws["model"].open("w", encoding="utf-8") as handle:
            yaml.dump(document, handle)
    raw = acceptance._document(1)
    acceptance._declare(ws["model"], raw, "round-1.txt")
    return acceptance._write_proposal(ws, "r1", acceptance._operations(acceptance.ROUND_1, raw))


def _round(paths: dict[str, Path]) -> list[Any]:
    """Preview (additive, shape report) then apply, as one host round runs them."""
    return [run_main(policy._preview_argv(paths, "--policy", "additive", "--shape-report")),
            run_main(policy._apply_argv(paths, "--policy", "additive"))]


# --- switches: count real parses; run with the scope off -----------------------------------------


@contextlib.contextmanager
def _counting(monkeypatch: pytest.MonkeyPatch) -> Iterator[list[str]]:
    """Record the source name of every call that reaches the real parser."""
    calls: list[str] = []
    real = _parsing._parse_model_document

    def counted(data: bytes, *, source: Any) -> Any:
        calls.append(str(source))
        return real(data, source=source)

    with monkeypatch.context() as patch:
        patch.setattr(_parsing, "_parse_model_document", counted)
        yield calls


@contextlib.contextmanager
def _scope_off(monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
    """Every `gnd evolve` scope opening becomes a no-op: the behaviour before GO1."""
    with monkeypatch.context() as patch:
        patch.setattr(_parsing, "parse_scope", contextlib.nullcontext)
        yield


# --- T1: the parse count, at two sizes and for a .json workspace ---------------------------------


@pytest.mark.parametrize("n", [10, 40])
def test_t1_preview_and_apply_parse_a_bounded_number_of_times(tmp_path: Path,
                                                              monkeypatch: pytest.MonkeyPatch, n: int) -> None:
    counts = {}
    for scope in ("on", "off"):
        paths = _grown_workspace(tmp_path / scope, n)
        with contextlib.ExitStack() as stack:
            if scope == "off":
                stack.enter_context(_scope_off(monkeypatch))
            calls = stack.enter_context(_counting(monkeypatch))
            result = run_main(policy._preview_argv(paths, "--policy", "additive", "--shape-report"))
            assert result.returncode == 0, result.stderr.decode()
            preview = len(calls)
            result = run_main(policy._apply_argv(paths, "--policy", "additive"))
            assert result.returncode == 0, result.stderr.decode()
            counts[scope] = (preview, len(calls) - preview)
    assert counts["on"][0] <= 2 and counts["on"][1] <= 3, counts
    assert counts["off"] == (6, 22), counts  # negative control: the count #228 measured


def test_t1_a_json_workspace_stays_within_the_bound(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    work, proposal = loading._orders(tmp_path, as_json=True)
    with _counting(monkeypatch) as calls:
        assert loading._preview(work, proposal, model="orders.json").returncode == 0
        preview = list(calls)
        assert loading._apply(work, proposal, model="orders.json").returncode == 0
        apply = calls[len(preview):]
    assert len(preview) <= 2, preview
    # The before text is parsed once as strict JSON and once under the YAML name
    # `_parse_model_text` gives it: two readers, within the bound.
    assert len(apply) <= 3, apply


def test_t1_the_count_does_not_depend_on_the_model_size(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    seen = []
    for n in (10, 40):
        paths = _grown_workspace(tmp_path / str(n), n)
        with _counting(monkeypatch) as calls:
            run_main(policy._preview_argv(paths, "--policy", "additive", "--shape-report"))
            run_main(policy._apply_argv(paths, "--policy", "additive"))
        seen.append(len(calls))
    assert seen[0] == seen[1], seen


# --- T2, T3: scope on and off give the same bytes; nothing writes into a shared document ---------


def _tree(root: Path) -> dict[str, bytes]:
    return {str(path.relative_to(root)): path.read_bytes() for path in sorted(root.rglob("*")) if path.is_file()}


def _observed(root: Path, steps: Callable[[], list[Any]]) -> dict[str, Any]:
    results = steps()
    return {"exits": [r.returncode for r in results], "stdout": [r.stdout for r in results],
            "stderr": [r.stderr for r in results], "tree": _tree(root)}


def _same_with_scope_on_and_off(tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
                                build: Callable[[Path], Callable[[], list[Any]]]) -> dict[str, Any]:
    """Build the case at one path, run it with the scope off, rebuild it at the same path and run it
    with the scope on (and its write check on): every exit, stream and file must be equal."""
    root = tmp_path / "case"
    observed = {}
    for scope in ("off", "on"):
        if root.exists():
            shutil.rmtree(root)
        steps = build(root)
        with contextlib.ExitStack() as stack:
            if scope == "off":
                stack.enter_context(_scope_off(monkeypatch))
            observed[scope] = _observed(root, steps)
    assert observed["on"] == observed["off"]
    return observed["on"]


def _one_round(root: Path) -> Callable[[], list[Any]]:
    paths = _grown_workspace(root, 3)
    return lambda: _round(paths)


def _policy_refusal(root: Path) -> Callable[[], list[Any]]:
    refused = (policy._op("add", policy._constraint_locator(policy.POPULATED, None, "mandatory"),
                          after=policy.NEW_CONSTRAINT),)
    paths = policy._cli_workspace(root, refused)
    return lambda: [run_main(policy._preview_argv(paths, "--policy", "additive")),
                    run_main(policy._apply_argv(paths, "--policy", "additive"))]


def _d12_refusal(root: Path) -> Callable[[], list[Any]]:
    bad = dict(policy.NEW_CONSTRAINT, source="explicit", status="confirmed", modality="alethic")
    paths = policy._cli_workspace(root, (policy._op("add", policy._constraint_locator(
        policy.POPULATED, None, "mandatory"), after=bad),))
    return lambda: [run_main(policy._preview_argv(paths, "--policy", "additive"))]


def _include_root(root: Path) -> Callable[[], list[Any]]:
    shutil.copytree(mc3.CORPUS, root)
    return lambda: [mc3.preview(root), mc3.apply_cli(root)]


def _json_model(root: Path) -> Callable[[], list[Any]]:
    root.mkdir()
    work, proposal = loading._orders(root, as_json=True)
    return lambda: [loading._preview(work, proposal, model="orders.json"),
                    loading._apply(work, proposal, model="orders.json")]


def _yaml_date(root: Path) -> Callable[[], list[Any]]:
    root.mkdir()
    work = loading._staff(root, loading._with_source("x: 2024-01-01"))
    proposal = loading._proposal(work)
    return lambda: [loading._preview(work, proposal)]


def _candidate_not_yaml(root: Path) -> Callable[[], list[Any]]:
    root.mkdir()
    work = loading._staff(root, loading.STAFF)
    proposal = loading._proposal(work, candidate_text="object_types: [\n")
    return lambda: [loading._preview(work, proposal)]


T2_CASES = {"one-round": (_one_round, [0, 0]), "policy-refusal": (_policy_refusal, [3, 3]),
            "d12-refusal": (_d12_refusal, [3]), "include-root": (_include_root, None),
            "json-model": (_json_model, [0, 0]), "yaml-date": (_yaml_date, [3]),
            "candidate-not-yaml": (_candidate_not_yaml, [3])}


@pytest.mark.parametrize("case", sorted(T2_CASES))
def test_t2_t3_scope_on_and_off_give_the_same_bytes(tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
                                                   case: str) -> None:
    build, exits = T2_CASES[case]
    observed = _same_with_scope_on_and_off(tmp_path, monkeypatch, build)
    if exits is not None:
        assert observed["exits"] == exits, [s.decode() for s in observed["stderr"]]


def test_t3_a_write_into_a_shared_document_fails_the_scope() -> None:
    from gnd.model import load_model_bytes

    data = (Path(__file__).parent / "fixtures" / "unattended" / "conforming.orm.yaml").read_bytes()
    previous = _parsing.set_parse_scope_verify(True)
    try:
        with pytest.raises(AssertionError, match="written to"), _parsing.parse_scope():
            model = load_model_bytes(data, source="model.orm.yaml")
            # A frozen Model keeps the document's nested content: this is a write into it.
            model.source["documents"].append({"sha256": "0" * 64, "label": "planted"})
        with pytest.raises(AssertionError, match="written to"), _parsing.parse_scope():
            document = _parsing.parse_model_document(b"version: 1\nflag: 1\n", source="m.orm.yaml")
            document["flag"] = True  # equal to 1, but not the same value
    finally:
        _parsing.set_parse_scope_verify(previous)


def test_t3_the_check_keeps_values_json_cannot_spell() -> None:
    previous = _parsing.set_parse_scope_verify(True)
    try:
        with _parsing.parse_scope():
            for text in (b"d: 2024-01-01\n", b"x: .nan\n", b"x: !foo 3\n", b"x: !!binary aGVsbG8=\n"):
                _parsing.parse_model_document(text, source="m.orm.yaml")
    finally:
        _parsing.set_parse_scope_verify(previous)


# --- T4: a model changed between preview and apply is refused as today ---------------------------


def _changed_before_apply(root: Path) -> Callable[[], list[Any]]:
    paths = _grown_workspace(root, 3)

    def steps() -> list[Any]:
        first = run_main(policy._preview_argv(paths, "--policy", "additive", "--shape-report"))
        paths["model"].write_text(paths["model"].read_text(encoding="utf-8") + "# edited\n", encoding="utf-8")
        return [first, run_main(policy._apply_argv(paths, "--policy", "additive"))]

    return steps


def test_t4_a_model_changed_after_preview_is_refused_as_today(tmp_path: Path,
                                                              monkeypatch: pytest.MonkeyPatch) -> None:
    observed = _same_with_scope_on_and_off(tmp_path, monkeypatch, _changed_before_apply)
    assert observed["exits"][0] == 0 and observed["exits"][1] != 0


# --- T5, T6: the lookup's branches -----------------------------------------------------------------


def test_t5_the_reader_is_part_of_the_key() -> None:
    flow = b"{version: 1, model_id: m}\n"  # YAML flow, not JSON
    with _parsing.parse_scope():
        assert _parsing.parse_model_document(flow, source="m.orm.yaml")["model_id"] == "m"
        with pytest.raises(ModelLoadError, match="model JSON input refused"):
            _parsing.parse_model_document(flow, source="m.orm.json")
        strict = b'{"version": 1}\n'
        assert (_parsing.parse_model_document(strict, source="a.orm.json")
                is not _parsing.parse_model_document(strict, source="a.orm.yaml"))


@pytest.mark.parametrize(("data", "message"), [
    (b"x" * (_parsing.MAX_MODEL_BYTES + 1), "10 MiB input cap"),
    (b"a: [\n", None),
])
def test_t5_a_refusal_is_not_remembered(data: bytes, message: str | None) -> None:
    calls = []
    real = _parsing._parse_model_document

    def counted(raw: bytes, *, source: Any) -> Any:
        calls.append(source)
        return real(raw, source=source)

    with pytest.MonkeyPatch.context() as patch, _parsing.parse_scope():
        patch.setattr(_parsing, "_parse_model_document", counted)
        for label in ("first.orm.yaml", "second.orm.yaml"):
            with pytest.raises(Exception, match=message) as raised:
                _parsing.parse_model_document(data, source=label)
            assert not isinstance(raised.value, AssertionError)
    assert calls == ["first.orm.yaml", "second.orm.yaml"]


def test_t6_scopes_nest_and_end() -> None:
    data = b"version: 1\n"
    assert _parsing.parse_model_document(data, source="m.orm.yaml") is not _parsing.parse_model_document(
        data, source="m.orm.yaml")
    with _parsing.parse_scope():
        outer = _parsing.parse_model_document(data, source="m.orm.yaml")
        with _parsing.parse_scope():
            assert _parsing.parse_model_document(data, source="m.orm.yaml") is outer
        assert _parsing.parse_model_document(data, source="m.orm.yaml") is outer
    assert _parsing._PARSE_SCOPE.get() is None
    assert _parsing.parse_model_document(data, source="m.orm.yaml") is not outer


# --- T7: two commands in one process share nothing ------------------------------------------------


def test_t7_a_second_command_parses_again(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    first = _grown_workspace(tmp_path / "a", 3)
    second = _grown_workspace(tmp_path / "b", 3)
    assert first["model"].read_bytes() == second["model"].read_bytes()
    with _counting(monkeypatch) as calls:
        run_main(policy._preview_argv(first, "--policy", "additive"))
        once = len(calls)
        run_main(policy._preview_argv(second, "--policy", "additive"))
    assert len(calls) == 2 * once and once > 0


# --- T8: the time ratio at 604 object types, recorded (slow lane) --------------------------------


@pytest.mark.slow
def test_t8_apply_with_the_scope_costs_at_most_six_tenths(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    previous = _parsing.set_parse_scope_verify(False)
    timings: dict[str, list[float]] = {"on": [], "off": []}
    try:
        for attempt in range(2):
            for scope in ("off", "on"):
                paths = _grown_workspace(tmp_path / f"{scope}{attempt}", 200)
                assert run_main(policy._preview_argv(paths, "--policy", "additive", "--shape-report")).returncode == 0
                with contextlib.ExitStack() as stack:
                    if scope == "off":
                        stack.enter_context(_scope_off(monkeypatch))
                    start = time.perf_counter()
                    assert run_main(policy._apply_argv(paths, "--policy", "additive")).returncode == 0
                    timings[scope].append(time.perf_counter() - start)
    finally:
        _parsing.set_parse_scope_verify(previous)
    ratio = min(timings["on"]) / min(timings["off"])
    print(json.dumps({"apply_seconds": timings, "ratio": round(ratio, 3)}))
    assert ratio <= 0.6, timings
