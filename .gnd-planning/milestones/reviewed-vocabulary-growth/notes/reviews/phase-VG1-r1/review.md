<!-- Edited by review_tool.py sanitize: 2 absolute path(s) replaced with <repo> or <home>. The reviewer's words are otherwise unchanged; run.json holds the SHA-256 of the original. -->
All ten SHA-256 hashes match the brief.

**F1 — High: cached kinds can change a failing report to vacuous.** [src/gnd/universe.py:350](<repo>/src/gnd/universe.py:350)

The new lookup inherits a cache-key collision: string-valued enums and plain strings serialize identically, but the original walk distinguishes their `str()` values.

Minimal reproduction:

```python
from enum import Enum
from gnd.documents import Model
from gnd.universe import _kind_of

class K(str, Enum):
    VALUE = "value"

def model(kind):
    return Model(version=2, object_types=[
        {"id": "v", "kind": kind, "primitive": "String"}
    ], fact_types=[])

_kind_of("v", model(K.VALUE))  # warms the cache
_kind_of("v", model("value"))  # returns "K.VALUE"; base returns "value"
```

I also reproduced a report change using `MOVIE_TYPES`, `MOVIE_FACTS` and the range constraint from `tests/test_reference_universe.py`. After warming the enum-kind model, I loaded its ordinary JSON representation through `load_model_bytes`. For movie value `999999` against range `1..100`, head returned **`vacuous`**. Restoring only the frozen kind lookup returned **`fail`**. This falsifies C1, C2 and C4.

**F2 — Medium: eager resolution introduces an exception for a code-built model.** [src/gnd/model_index.py:302](<repo>/src/gnd/model_index.py:302)

The table resolves every type before removing covered types. The base comprehension skips covered types before resolving them.

Reproduction: construct a `Model` containing value type `v` and entity type `e` with `"reference": "bad"`, then call `_denoting_types({"v", "e"}, model)`. The frozen body returns `set()`; head raises `AttributeError: 'str' object has no attribute 'get'`. I ran this successfully. This concerns constructor-accepted code-built models; schema loading rejects that reference shape.

What checked true:

- T1 fixture-wide parity, all supplied T2 cases, and T13 passed.
- All 25 RF1 checker pairs matched their existing goldens across in-process, text, JSON and admission JSON routes. Resolver, datetime, transition, anchored and coverage pins also passed.
- A supplementary CLI profile using the misc fixture with in-memory growth counted **7 supertype-map builds at both 300 and 600 extra value types**.
- Returned table mappings reject assignment, and returned denotation sets are detached.
- No new regex, split or slice parser was added; structured fixture edits use JSON loading.

I could not rerun the exact interop scaling, judgments or verify experiments: their setup creates files, which this brief prohibits. The supplementary profile therefore supports C3 without independently reproducing its specified fixture. No files were changed by this review.

VERDICT: CHANGES_REQUESTED