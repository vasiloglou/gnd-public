"""IL3 learner driver: wittgenstein's RIPPER over one feature table (evidence only).

Runs under the scratch Python, never under GND's (IL-R1, IL-R2):

    python -I learn_rules.py WITTGENSTEIN_DIR FEATURES_JSON

WITTGENSTEIN_DIR is the extracted, unbuilt sdist (IL3-D2 (o)); ``-I`` ignores
PYTHONPATH, so the driver puts it on ``sys.path`` itself. Settings are IL3-D9 (o):
``random_state=0``, binning off, other parameters at their defaults. It prints one
``learner`` line, one ``RULESET`` line (``str(ruleset_)``), and one ``COVERS`` line
per rule, from the learner's own ``Rule.covers`` (IL-R4).
"""

import json
import sys
from pathlib import Path

source, table_path = Path(sys.argv[1]), Path(sys.argv[2])
sys.path.insert(0, str(source))

import pandas
from wittgenstein import RIPPER

version = next(line.split(": ", 1)[1] for line in (source / "PKG-INFO").read_text().splitlines()
               if line.startswith("Version: "))
table = json.loads(table_path.read_text(encoding="utf-8"))
names = [column["name"] for column in table["columns"]]
frame = pandas.DataFrame([row["values"] for row in table["rows"]], columns=names,
                         index=[row["example"] for row in table["rows"]])
frame["label"] = [row["label"] for row in table["rows"]]
learner = RIPPER(random_state=0, n_discretize_bins=None)
learner.fit(frame, class_feat="label", pos_class="pos")
print(f"learner wittgenstein {version}")
print(f"RULESET {learner.ruleset_}")
features = frame.drop(columns=["label"])
for index, rule in enumerate(learner.ruleset_.rules):
    print(f"COVERS {index} {json.dumps(sorted(rule.covers(features).index.tolist()))}")
