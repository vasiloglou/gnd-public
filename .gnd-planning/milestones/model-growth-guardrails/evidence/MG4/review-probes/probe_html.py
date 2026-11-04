import copy, io, tempfile, re
from pathlib import Path
from ruamel.yaml import YAML
import markdown
from gnd.extract.guidelines import render_guidelines
from gnd.model import load_model
base = YAML(typ="safe").load(Path("tests/fixtures/evolve-policy/base.orm.yaml").read_text())
for summary in ("<!-- hide", "<h2>Fact type <code>evil</code></h2>"):
    d = copy.deepcopy(base)
    next(o for o in d["object_types"] if o["id"] == "customer")["description"] = {"summary": summary}
    p = Path(tempfile.mkdtemp()) / "m.orm.yaml"; buf = io.StringIO(); YAML().dump(d, buf); p.write_text(buf.getvalue())
    html = markdown.markdown(render_guidelines(load_model(str(p))))
    print(repr(summary), "rendered <h2> count:", len(re.findall(r"<h2>", html)), "(3 fact types); visible after comment:", html.split("<!--")[-1].count("<h2>") if "<!--" in html else "-")
