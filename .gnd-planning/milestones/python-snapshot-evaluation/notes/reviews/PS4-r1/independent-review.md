# PS4-r1 review: persistent local worker and the Pydantic range

All 15 files in the brief match their SHA-256 values. HEAD is `5b52e43f18c1`. Most of the worker behaves as the spec asks, but missing or unreadable model paths get the wrong error code and throw away the loaded model, so I'm requesting changes.

**Scratch files I wrote:** the files I created are all under `/tmp/ps4rev` (probe scripts, temporary model directories and a `link` symlink). The repository is untouched. This review runs in plan mode, so I also wrote my summary to the session's plan file.

**Files that appeared during the review:** the evidence folder now contains `integrated_replay.py`, `independent-integrated.json` and `locked-integrated.json`, and the notes folder contains `close-delta.md` and `close-results.md`. All are untracked, were not in the starting status and were written at 10:27, after the commit. Another session seems to be writing into this worktree. I did not review them.

## 1. Findings

**F1 — `src/gnd/snapshot_worker.py:71`: a bad model path is reported as a checker crash, and the healthy loaded model is dropped.**
- **What's wrong:** `read_regular_path` raises `gnd.artifacts.ArtifactError` when the model path is missing, is a directory, passes through a symlink, or is too large. That class is not in the `invalid-input` list, so it falls into the general `except Exception` branch. That branch calls `self.close()` and returns `evaluation-error`.
- **What you'd see:** a typo in the model path looks like a checker failure, not an input error. That contradicts the docs, which promise a stable code for "a protocol or input failure". It also discards a good loaded model and `EvaluationSession` that another request is still using.
- **Reproduce (run):** send requests `a` (valid), `m` (model path `missing.json`), then `b` (same as `a`) to `serve()`. Result: `[('a','evaluated',None,False), ('m','error','evaluation-error',None), ('b','evaluated',None,False)]`. Request `b` should report `model_reused: True`.
- **Tests:** the tests only replace the model with invalid YAML, which raises `ModelValidationError`. No test covers a missing, directory or symlinked path.

**F2 — `src/gnd/snapshot_worker.py:41`: the worker refuses any model path that goes through a symlink; `api.check` accepts the same path.**
- **What's wrong:** `Path(...).absolute()` does not resolve symlinks, and `read_regular_path` refuses a symlink at any step of the path. On macOS `/tmp` is a symlink to `/private/tmp`, so every `/tmp/...` model path fails.
- **What you'd see:** a model behind a symlinked directory works in a direct Python call but fails in the worker (`evaluation-error`, because of F1). The docs only say "The model path is local to the worker" and do not mention this.
- **Reproduce (run):** `api.check(link/model.orm.json, pop)` returns exit 1. The worker returns `evaluation-error` for the same path, and also for `/tmp/...` versus `/private/tmp/...`.
- **Evidence script:** `installed_replay.py` calls `.resolve()` on its temp directory, which hides this.
- **What to decide:** either document the refusal and give it its own error code, or resolve the path the way the direct API does.

**F3 — `src/gnd/snapshot_worker.py:48`: the `model.includes` part of the dependency check never runs.**
- **What's wrong:** `load_model_bytes` already refuses any document that declares includes, raising `ModelValidationError` with rule `include:unresolved` (`src/gnd/model/__init__.py:299`, `_includes.py:46`).
- **What you'd see:** include-dependent models get `invalid-input`, while reference-population models get `external-model-dependencies`. Two kinds of unsupported dependency get different codes, although the docs present them as one case ("outside protocol v1").
- **Status:** read only, then confirmed through the `_refuse` path.

**F4 — `evidence/PS4/*.json` and `installed_replay.py`: the installed-wheel evidence is narrower than the dependency range it supports.**
- **No wheel identity.** The spec says "Record wheel and environment identities". The evidence records only `"gnd": "0.5.2"`, the same version string as the existing tag-only 0.5.2. There is no wheel hash and no resolver or freeze output, so nothing ties the result to a wheel built from this commit.
- **Thin worker run.** In the installed host the worker ran only two valid requests and one bad-version request. Invalidation on model replacement, the kill and cold restart, oversized lines and session isolation were tested only in the source tree with Pydantic 2.13.4.
- **No pass/fail decision exercised.** The recorded `run_status` is `"unchecked"`. The installed run compares verdicts but never runs a constraint that can pass or fail.
- **Untested part of the range.** `pyproject.toml` now accepts `>=2.12.5,<2.14`. Only 2.12.5 and 2.13.4 were exercised, and 2.13.0–2.13.3 were not.
- **Most Pydantic code not run on 2.12.5.** 47 modules import pydantic, and there is no evidence the test suite ran on 2.12.5. The docs sentence is accurate. The risk is the scope of the range: the base dependency is widened for all of GND on a two-request fixture.

**F5 — `src/gnd/snapshot_worker.py:80` (minor, mostly a docs mismatch): the 4 MiB limit counts the newline.**
- **What you'd see:** a request of exactly 4 MiB plus its newline is rejected with `request-too-large`. The docs say "Maximum input is 4 MiB per line".
- **Status:** run. The next line still evaluates correctly, so recovery works.

## 2. What I checked and found true
- **Valid requests:** a valid request evaluates and the reused model is flagged. The report matches `api.check` except that `model` and `population` are `None` in the worker's report.
- **Recovery after a model error:** an invalid replacement at the same path is never evaluated against the old model, because the loaded state is cleared before the reload. A valid replacement loads a fresh model and session.
- **Population and dependency errors:** a bad population keeps the loaded model, as it should. `external-model-dependencies` and unexpected exceptions both leave no stale identity.
- **Overlong lines:** an overlong line is read to its end before the next request, including at the exact limit. A last line without a newline still evaluates.
- **Population header:** a population whose header names another model gets the same result as a direct check (exit 4, indeterminate).
- **The two new tests pass:** `pytest tests/test_snapshot_worker.py` gives 2 passed.
- **Lock and docs:** `uv.lock` still resolves Pydantic 2.13.4, and the docs describe that accurately.

**Matchers and special cases I tried, per the standing check:**

| Matcher / branch | Input tried | Result |
|---|---|---|
| ID rule (string, 1–128 characters) | lone surrogate `"\ud800"` | evaluated; output stays ASCII |
| `type(version) is int` | `version: true` | `unsupported-version` (correct) |
| exact field-set check | the four required fields | accepted |
| JSON parser (`input_policy.loads`) | nesting 100 deep, duplicate key, 5000-digit integer | `invalid-input`, ID null |
| line limit | 4 MiB + newline | `request-too-large`; see F5 |
| path reading | relative path | works |
| path reading | symlinked directory, `/tmp` alias | refused; see F1/F2 |

The worker uses the existing JSON parser and path reader. It adds no regular expression or string splitting.

## 3. What I could not check
- **The full test suite on Pydantic 2.12.5 or 2.13.0–2.13.3:** it needs a newly resolved environment, which I did not build while reviewing read-only.
- **Rebuilding the wheel and rerunning `installed_replay.py`:** not done, for the same reason.
- **Worker stderr staying free of request values (the spec's "subprocess output") under warnings:** I only read the code for this. Responses carry fixed codes.
- **The untracked `*-integrated` files and close notes:** not in the brief, so not reviewed.

VERDICT: CHANGES_REQUESTED
