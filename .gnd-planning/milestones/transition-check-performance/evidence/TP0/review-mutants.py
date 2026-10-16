"""Load mutated copies of the TP0 tool and show each review-successor test turns red."""
import importlib.util, sys, tempfile, pathlib, traceback
ROOT = pathlib.Path.cwd()
src = (ROOT / "tools/measure_transition_cost.py").read_text()
sys.path.insert(0, str(ROOT / "tests"))
import test_transition_cost_workload as t  # noqa: E402

MUTANTS = {
    "F5 pre-fix restore (getattr)": ('saved = vars(owner)[name] if isinstance(owner, type) else getattr(owner, name)',
                                     'saved = getattr(owner, name)', "test_review_f5_counting_restores_the_classmethod"),
    "F3 swapped dump attribution": ('"model_index_key_paths" if caller == "gnd.model_index" else "model_dumps_other"',
                                    '"model_dumps_other" if caller == "gnd.model_index" else "model_index_key_paths"',
                                    "test_review_f3_key_path_attribution"),
    "F4 trace digest of count only": ('hashlib.sha256("\\n".join(sorted(branches)).encode())',
                                      'hashlib.sha256(str(len(branches)).encode())',
                                      "test_review_f4_trace_digest_covers_identity_not_count"),
    "F7 every node counted top-level": ('            if frame.f_back.f_code.co_filename.startswith(_GND_SOURCE):\n                counts["deepcopy_calls"] += 1',
                                        '            counts["deepcopy_calls"] += 1',
                                        "test_review_f7_top_level_calls_only_from_gnd_frames"),
    "F1 pre-fix: no course admission surface": ('        rows.append(("pre.check.admission", lambda: api.check(model, pre, admission=True)))\n', '',
                                                "test_review_f1_f2_course_surfaces_and_batch_digest"),
}
for label, (old, new, test) in MUTANTS.items():
    assert old in src, label
    path = pathlib.Path(tempfile.mkdtemp()) / "measure_transition_cost.py"
    path.write_text(src.replace(old, new))
    spec = importlib.util.spec_from_file_location("mutant", path)
    mutant = importlib.util.module_from_spec(spec); spec.loader.exec_module(mutant)
    mutant.ROOT = ROOT; mutant.REPORTER = ROOT / "tests/fixtures/transition_cost"
    mutant.COURSE = ROOT / "src/gnd/examples/plan_apps/course"; mutant._GND_SOURCE = str(ROOT / "src/gnd")
    t.tool = mutant
    fn = getattr(t, test)
    try:
        fn(pathlib.Path(tempfile.mkdtemp())) if fn.__code__.co_argcount else fn()
        print(f"SURVIVED  {label}")
    except (AssertionError, KeyError, TypeError, AttributeError) as error:
        print(f"KILLED    {label}: {type(error).__name__}")
