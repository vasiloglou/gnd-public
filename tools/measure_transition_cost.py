"""Measure GND's counted work, report parity and wall time on the issue #24 workload.

Usage: uv run python tools/measure_transition_cost.py --out DIR [--repeat N]
       [--workload {reporter,course,all}]

TP0 of the transition-check-performance milestone. Counters are installed at test time at
every lookup owner of each counted callable (spec D1), so runtime code is unchanged.
Counters gate; timings, taken in separate uninstrumented runs, only inform.
"""
from __future__ import annotations

import argparse
import contextlib
import copy
import hashlib
import json
import platform
import statistics
import subprocess
import sys
import tempfile
import time
from collections import Counter
from collections.abc import Callable, Iterator
from pathlib import Path
from typing import Any

from gnd import api, artifacts
from gnd.branches import capture_branches
from gnd.documents import Model
from gnd.model import load_model
from gnd.population import load_population

ROOT = Path(__file__).resolve().parents[1]
REPORTER = ROOT / "tests/fixtures/transition_cost"
COURSE = ROOT / "src/gnd/examples/plan_apps/course"

#: Top-level payload fields that carry an input path on the CLI and ``None`` through the
#: API. They are the only fields blanked before hashing (spec D3).
NORMALIZED_FIELDS = ("model", "population")

#: counter key -> (module, attribute) of the defining callable. Every loaded ``gnd``
#: module attribute that IS this object is wrapped too (the lookup owners).
COUNTED = {
    "checker_runs": ("gnd.checker._core", "_check_dispatch"),
    "model_digests": ("gnd.values", "_model_digest"),
    "extension_views": ("gnd.extensions", "structured_extension_view"),
    "correspondences": ("gnd.correspondence", "correspond_snapshot"),
}
COUNTER_KEYS = (
    "checker_runs",
    "model_index_calls",
    "model_index_key_paths",
    "model_dumps_other",
    "model_digests",
    "deepcopy_calls",
    "deepcopy_nodes",
    "extension_views",
    "correspondences",
)
_GND_SOURCE = str(ROOT / "src/gnd")


@contextlib.contextmanager
def counting() -> Iterator[Counter]:
    """Count every key in COUNTER_KEYS for the duration of the block."""
    counts: Counter = Counter({key: 0 for key in COUNTER_KEYS})
    restore: list[tuple[object, str, object]] = []

    def patch(owner: object, name: str, value: object) -> None:
        # Class attributes are saved raw, so a classmethod is restored as a classmethod.
        saved = vars(owner)[name] if isinstance(owner, type) else getattr(owner, name)
        restore.append((owner, name, saved))
        setattr(owner, name, value)

    for key, (module_name, attribute) in COUNTED.items():
        original = getattr(sys.modules[_import(module_name)], attribute)

        def wrapper(*args, __key=key, __original=original, **kwargs):
            counts[__key] += 1
            return __original(*args, **kwargs)

        for module in [m for n, m in list(sys.modules.items()) if n.split(".")[0] == "gnd"]:
            for name, value in list(vars(module).items()):
                if value is original:
                    patch(module, name, wrapper)

    from gnd.model_index import ModelIndex

    for_model = ModelIndex.__dict__["for_model"]

    def counted_for_model(cls, model):
        counts["model_index_calls"] += 1
        return for_model.__func__(cls, model)

    patch(ModelIndex, "for_model", classmethod(counted_for_model))
    model_dump = Model.model_dump

    def counted_dump(self, *args, **kwargs):
        caller = sys._getframe(1).f_globals.get("__name__")
        counts["model_index_key_paths" if caller == "gnd.model_index" else "model_dumps_other"] += 1
        return model_dump(self, *args, **kwargs)

    patch(Model, "model_dump", counted_dump)

    deepcopy_code = copy.deepcopy.__code__

    def profiler(frame, event, _arg):
        # Every deepcopy invocation is a node. It is a top-level call when GND code called
        # it directly; copy's own recursion has copy.py as its caller.
        if event == "call" and frame.f_code is deepcopy_code:
            counts["deepcopy_nodes"] += 1
            if frame.f_back.f_code.co_filename.startswith(_GND_SOURCE):
                counts["deepcopy_calls"] += 1

    previous = sys.getprofile()
    sys.setprofile(profiler)
    try:
        yield counts
    finally:
        sys.setprofile(previous)
        for owner, name, value in reversed(restore):
            setattr(owner, name, value)


def _import(module_name: str) -> str:
    __import__(module_name)
    return module_name


def normalized_digest(payload: dict[str, Any]) -> str:
    document = {k: (None if k in NORMALIZED_FIELDS else v) for k, v in payload.items()}
    return "sha256:" + hashlib.sha256(artifacts.canonical_json_bytes(document)).hexdigest()


def trace_digest(branches: set[str]) -> str:
    return "sha256:" + hashlib.sha256("\n".join(sorted(branches)).encode()).hexdigest()


def _course_steps(name: str) -> dict[str, Any]:
    from gnd.examples.plan_apps.core import Example, steps_document

    plan = json.loads((COURSE / "plans" / name).read_text())
    return steps_document(Example(COURSE), plan["steps"])


def reporter_calls() -> list[dict[str, Any]]:
    return json.loads((REPORTER / "calls.json").read_text())


def surfaces(workload: str) -> list[tuple[str, Callable[[], dict[str, Any]]]]:
    """Named zero-argument calls for one workload, each returning a public payload."""
    rows: list[tuple[str, Callable[[], dict[str, Any]]]] = []
    if workload == "reporter":
        model = load_model(REPORTER / "steps.orm.json")
        calls = reporter_calls()
        for call in calls:
            index = call["index"]
            population = load_population(REPORTER / call["population"], model=model)
            if call["call"] == "check":
                for label, kwargs in (("check", {}), ("check.compiled", {"compiled_operations": True}),
                                      ("check.admission", {"admission": True})):
                    rows.append((f"{index:02d}.{label}",
                                 lambda p=population, k=kwargs: api.check(model, p, **k)))
            else:
                steps = json.loads((REPORTER / call["steps"]).read_text())
                post = load_population(REPORTER / calls[index + 1]["population"], model=model)
                rows.append((f"{index:02d}.transition",
                             lambda p=population, s=steps: api.transition(model, p, s)))
                rows.append((f"{index:02d}.transition.post",
                             lambda p=population, s=steps, q=post: api.transition(model, p, s, q)))
    else:
        model = load_model(COURSE / "model.orm.json")
        pre = load_population(COURSE / "state.pop.json", model=model)
        rows.append(("pre.check", lambda: api.check(model, pre)))
        rows.append(("pre.check.compiled", lambda: api.check(model, pre, compiled_operations=True)))
        rows.append(("pre.check.admission", lambda: api.check(model, pre, admission=True)))
        for attempt in ("attempt-1", "attempt-2", "attempt-3"):
            steps = _course_steps(f"{attempt}.steps.json")
            rows.append((f"{attempt}.transition", lambda s=steps: api.transition(model, pre, s)))
    return rows


def replay(workload: str) -> Callable[[], list[dict[str, Any]]]:
    """The workload as its caller ran it, returned unstarted.

    reporter: the model is loaded once; each of the 13 calls loads its population and makes
    its one public call, as the reporter's driver does. course: the wrapped 3-step walk.
    """
    if workload == "course":
        model = load_model(COURSE / "model.orm.json")
        steps = _course_steps("attempt-3.steps.json")

        def run_course() -> list[dict[str, Any]]:
            pre = load_population(COURSE / "state.pop.json", model=model)
            return [api.transition(model, pre, steps)]

        return run_course
    model = load_model(REPORTER / "steps.orm.json")
    calls = reporter_calls()
    steps = {c["index"]: json.loads((REPORTER / c["steps"]).read_text())
             for c in calls if c["call"] == "transition"}

    def run_reporter() -> list[dict[str, Any]]:
        payloads = []
        receipt = None
        for call in calls:
            population = load_population(REPORTER / call["population"], model=model)
            if call["call"] == "check":
                if workload == "reporter-receipts":
                    payload, receipt = api.check_with_receipt(model, population)
                    payloads.append(payload)
                else:
                    payloads.append(api.check(model, population))
            else:
                payloads.append(api.transition(model, population, steps[call["index"]],
                                               pre_receipt=receipt))
        return payloads

    return run_reporter


def _cli(*arguments: str) -> dict[str, Any]:
    result = subprocess.run([sys.executable, "-m", "gnd", *arguments, "--format", "json"],
                            capture_output=True, text=True, check=False)
    payload = json.loads(result.stdout)
    payload["_process_exit"] = result.returncode
    return payload


def cli_surfaces() -> dict[str, dict[str, Any]]:
    model = str(REPORTER / "steps.orm.json")
    results = {
        "cli.check.00": _cli("check", model, str(REPORTER / "00-check-population.json")),
        "cli.course.check.pre": _cli("check", str(COURSE / "model.orm.json"),
                                     str(COURSE / "state.pop.json")),
        "cli.transition.01": _cli("check", model, "--pre", str(REPORTER / "01-transition-population.json"),
                                  "--steps", str(REPORTER / "01-transition-steps.json"),
                                  "--post", str(REPORTER / "02-check-population.json")),
    }
    with tempfile.TemporaryDirectory() as tmp:
        for call in reporter_calls():
            if call["call"] == "check":
                (Path(tmp) / call["population"]).write_bytes((REPORTER / call["population"]).read_bytes())
        result = subprocess.run([sys.executable, "-m", "gnd", "check", model, "--populations", tmp,
                                 "--format", "json"], capture_output=True, text=True, check=False)
        results["cli.batch"] = {"exit_code": result.returncode, "payload": json.loads(result.stdout)}
    return results


def measure(workload: str) -> dict[str, Any]:
    rows = {}
    for name, call in surfaces(workload):
        with capture_branches() as branches, counting() as counts:
            payload = call()
        rows[name] = {"exit_code": payload.get("exit_code"), "counts": payload.get("counts"),
                      "payload_digest": normalized_digest(payload),
                      "trace_digest": trace_digest(branches), "counters": dict(counts)}
    run = replay(workload)
    run()  # warm-up: the first replay in a process fills one-time caches (TP0 finding 7)
    with counting() as counts:
        run()
    return {"surfaces": rows, "replay_counters": dict(counts)}


def compare_import(source: Path) -> dict[str, Any]:
    """Per-call results of the reporter's original bundle versus the committed fixture.

    Exit codes, counts, normalized payload digests, trace digests and counters must be equal;
    the transform touched only names, notes and the digests that cover them.
    """
    def per_call(directory: Path) -> list[dict[str, Any]]:
        model = load_model(directory / "steps.orm.json")
        rows = []
        for call in json.loads((directory / "calls.json").read_text()):
            population = load_population(directory / call["population"], model=model)
            with capture_branches() as branches, counting() as counts:
                if call["call"] == "check":
                    payload = api.check(model, population)
                else:
                    steps = json.loads((directory / call["steps"]).read_text())
                    payload = api.transition(model, population, steps)
            payload = {k: v for k, v in payload.items() if k != "model_digest"}
            if isinstance(payload.get("transition"), dict):
                transition = {k: v for k, v in payload["transition"].items()
                              if k not in ("model_digest", "operations_digest")}
                computed = transition.get("computed_post")
                if isinstance(computed, dict) and isinstance(computed.get("population"), dict):
                    header = {k: v for k, v in computed["population"].items() if k != "model_id"}
                    transition["computed_post"] = {**computed, "population": header}
                payload["transition"] = transition
            rows.append({"index": call["index"], "call": call["call"],
                         "exit_code": payload.get("exit_code"), "counts": payload.get("counts"),
                         "payload_digest": normalized_digest(payload),
                         "trace_digest": trace_digest(branches), "counters": dict(counts)})
        return rows

    original, imported = per_call(source), per_call(REPORTER)
    return {"schema": "transition-cost-import/1",
            "compared": ["exit_code", "counts", "payload_digest", "trace_digest", "counters"],
            "excluded_from_payload_digest": [
                "model_digest", "transition.model_digest", "transition.operations_digest",
                "transition.computed_post.population.model_id"],
            "why_excluded": "identity fields that echo the renamed model_id or digests the "
                            "transform recomputes",
            "equal": original == imported, "calls": imported}


def timings(workload: str, repeat: int) -> dict[str, Any]:
    run = replay(workload)
    samples = []
    for _ in range(repeat):
        start = time.perf_counter()
        run()
        samples.append(time.perf_counter() - start)
    return {"repeat": repeat, "samples_s": samples, "median_s": statistics.median(samples),
            "spread": (max(samples) - min(samples)) / statistics.median(samples)}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--repeat", type=int, default=5)
    parser.add_argument("--workload", choices=("reporter", "course", "all"), default="all")
    parser.add_argument("--compare-import", type=Path, metavar="SOURCE",
                        help="write import.json comparing the original bundle with the fixture")
    args = parser.parse_args(argv)
    if args.compare_import is not None:
        args.out.mkdir(parents=True, exist_ok=True)
        result = compare_import(args.compare_import)
        (args.out / "import.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
        return 0 if result["equal"] else 1
    workloads = ("reporter", "course") if args.workload == "all" else (args.workload,)
    args.out.mkdir(parents=True, exist_ok=True)
    environment = {"python": platform.python_version(), "machine": platform.machine(),
                   "system": platform.system()}
    measured = {w: measure(w) for w in workloads}
    counters = {"schema": "transition-cost-counters/1", "environment": environment,
                "workloads": {w: {"replay": m["replay_counters"],
                                  "surfaces": {n: r["counters"] for n, r in m["surfaces"].items()}}
                              for w, m in measured.items()}}
    digests = {"schema": "transition-cost-digests/1", "normalized_fields": list(NORMALIZED_FIELDS),
               "workloads": {w: {n: {k: r[k] for k in ("exit_code", "counts", "payload_digest",
                                                       "trace_digest")}
                                 for n, r in m["surfaces"].items()}
                             for w, m in measured.items()}}
    if "reporter" in workloads:
        digests["cli"] = {name: ({"exit_code": r["exit_code"], "rows": len(r["payload"]["rows"]),
                                  "summary": r["payload"]["summary"],
                                  "payload_digest": normalized_digest(r["payload"])}
                                 if name == "cli.batch" else
                                 {"exit_code": r["exit_code"], "process_exit": r["_process_exit"],
                                  "payload_digest": normalized_digest(
                                      {k: v for k, v in r.items() if k != "_process_exit"})})
                          for name, r in cli_surfaces().items()}
    timing = {"schema": "transition-cost-timings/1", "environment": environment,
              "note": "uninstrumented runs; evidence only, never a gate",
              "workloads": {w: timings(w, args.repeat) for w in workloads}}
    for name, document in (("counters", counters), ("digests", digests), ("timings", timing)):
        (args.out / f"{name}.json").write_text(json.dumps(document, indent=2, sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
