from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
import json
import runpy
import sys

from gnd.export import ossie

render = ossie.render_ossie
mapped = set()

def collect(path, **options):
    result = render(path, **options)
    if result.mapping is not None:
        mapped.add(str(path))
    return result

ossie.render_ossie = collect
assert Path(ossie.__file__).resolve().is_relative_to(Path.cwd())
with redirect_stdout(StringIO()):
    data = runpy.run_path(sys.argv[1])

print(json.dumps({
    "mapped": sorted(mapped),
    "identification_differs": [
        {"kind": kind, "cause": cause, "rows": count, "models": sorted(data["models"][kind, cause])}
        for (kind, cause), count in sorted(data["rows"].items())
    ]
}, indent=2))
