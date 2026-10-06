# RF9 reviewer A: behavior

Native Codex gpt-6-sol/xhigh, one read-only run, exit0. Fixed source:d440b2e37449ef46647d18c491c46d9bb8d3e851; base:f5a83186f7c2215ac2b2afb0a010c2294eaa433a.
Prompt SHA-256:f311732cc84ced4ce3a11b1809edec6a7053e75748a33236c9951cb0b2f11086.
The return below is verbatim except absolute worktree/home paths replaced by <worktree>/<home>. It is an advisory candidate list; primary reproductions and dispositions are separate.

## RF9 Area A review

**One confirmed finding (P3): relocated population digest helpers break runtime annotation introspection.** [`_content_digest` and `_model_digest`](<worktree>/src/gnd/values.py:151) retain `Population` and `Model` annotations, but those names are imported only under `TYPE_CHECKING` at [values.py:216](<worktree>/src/gnd/values.py:216). The legacy names in [population.py:60](<worktree>/src/gnd/population.py:60) point to those same function objects.

Minimal read-only reproduction with `.venv/bin/python`:

```python
from typing import get_type_hints
from gnd.population import _content_digest, _model_digest

get_type_hints(_content_digest)  # NameError: Population
get_type_hints(_model_digest)    # NameError: Model
```

At the fixed base, `population.py` imported `Model` at runtime and defined `Population` before both helpers (`f5a8318:src/gnd/population.py:50,101,216,262`). The failure was introduced by the RF3 move. Digest calls still work; the consequence is confined to consumers that resolve these annotations at runtime. I excluded `references.reference_model_digest` from this finding because its unresolved `Model` annotation was already present at the base.

**Coverage and test masking.** I compared the base CLI dispatch with selected final command branches, checked selected CLI/API name and alias identities, digest variants, class pickling, three live handler lookups, and six read-only CLI refusal paths. The sampled routes preserved their expected handlers and exits. I found no concrete masked test; the compatibility identity tests do not check annotation resolution.

I did not inspect every successful command path, every canonical encoder variant, provider execution, model cache or loader internals, the full import graph, or platform behavior. No broad suite ran. `git diff d440b2e -- src tests tools` was empty, and I made no changes. This is an advisory Area A reading, not certification.
