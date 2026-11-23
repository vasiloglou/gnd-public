# The commands behind the papers story

This page reproduces every result in
[An ontology from a stack of papers](index.md). Each block runs from a
checkout of the repository with no model account and no network
connection. The whole page takes about a minute.

The extraction agent's answers are saved in the example, so the same run
gives the same result every time. GND does the checking, composing,
proving and replaying for real.

## Get the example

<!-- gnd-run expect=0 -->
```sh
python -c "import gnd, pathlib, shutil; shutil.copytree(pathlib.Path(gnd.__file__).parent / 'examples/literature', 'papers', dirs_exist_ok=True)"
```

The sixteen paper notes are in `papers/corpus/documents/`. Each one is a
short synthetic paraphrase of a public work, and names that work's
identifier:

<!-- gnd-run expect=0 output=stdout -->
```sh
ls papers/corpus/documents
```

```text
apinn.md
asam.md
boltz-1.md
flows-review.md
opencap-monocular.md
pinn-failure-modes.md
posex.md
roberta.md
sbi-frontier.md
segment-anything.md
sensor-placement.md
vampnet.md
vampnets.md
wham-pose.md
wham-whale.md
xlnet.md
```

## Act 1. The whale chain

Two small notes use the same spellings for different methods:

<!-- gnd-run expect=0 output=stdout -->
```sh
cat papers/resolution/cases/W-flat/whale-a/document.txt papers/resolution/cases/W-flat/whale-b/document.txt
```

```text
# Notes A: a Koopman method and a pose model (synthetic fixture)
VampNet builds on DMD.
OpenCap Monocular builds on WHAM.
# Notes B: a music model and a whale model (synthetic fixture)
WHAM builds on VampNet.
```

Combine them twice: once by spelling alone, once with the reviewer's
identity decisions. Then ask GND to prove that OpenCap Monocular descends
from DMD.

<!-- gnd-run expect=0 output=stdout -->
```python
import json, subprocess

def gnd(*args):
    return subprocess.run(["gnd", *args], capture_output=True, text=True)

model = "papers/resolution/model.orm.yaml"
json.dump({"version": 1, "targets": [{"fact_type": "method_has_ancestor_method", "tuple": [
    {"primitive": "String", "value": "OpenCap Monocular"},
    {"primitive": "String", "value": "DMD"}]}]}, open("whale-target.json", "w"))
for case in ("W-flat", "W-resolved"):
    gnd("compose", model, f"papers/resolution/cases/{case}", "--out", f"{case}.population.json",
        "--record", f"{case}.record.json")
    edges = json.load(open(f"{case}.population.json"))["facts"]["method_builds_on_method"]
    print(case)
    for edge in edges:
        print(f"  {edge['method']} builds on {edge['base_method']}")
    done = gnd("witness", model, f"{case}.population.json", "--targets", "whale-target.json",
               "--composition", f"{case}.record.json", "--raw", "--out", f"{case}.witness.json")
    status = json.loads(done.stdout)["results"][0]["status"]
    print(f"  OpenCap Monocular has ancestor DMD: {status} (exit {done.returncode})")
```

```text
W-flat
  VampNet builds on DMD
  OpenCap Monocular builds on WHAM
  WHAM builds on VampNet
  OpenCap Monocular has ancestor DMD: proved (exit 0)
W-resolved
  VampNet builds on DMD
  OpenCap Monocular builds on WHAM
  WhAM [whale] builds on VampNet [music]
  OpenCap Monocular has ancestor DMD: missing (exit 2)
```

When a resolution is present but forgets a pair that spelling would join,
composition refuses instead of guessing:

<!-- gnd-run expect=3 output=stderr -->
```sh
gnd compose papers/resolution/model.orm.yaml papers/resolution/cases/R-uncovered --out uncovered.json --record uncovered.record.json
```

```text
ERROR: composition:invalid: keys at whale-a method_builds_on_method#0.method and whale-b method_builds_on_method#0.base_method (object type method) are joined without a same decision
```

## Act 1. Lineage over the whole stack

Assemble the reviewed statements from the sixteen notes, then score every
labelled lineage path in the answer key. A supported path must be proved,
and a false one must be missing.

<!-- gnd-run expect=0 output=stdout -->
```python
import json, subprocess, sys

def example(*args):
    return subprocess.run([sys.executable, "-m", "gnd.examples.literature.lineage_run", *args],
                          capture_output=True, text=True)

model = "papers/lineage/model.orm.yaml"
example("assemble", "papers", model, "papers/lineage/development-input.json", "lineage-run")
score = json.loads(example("score", model, "lineage-run", "papers/answers/answer-key.json").stdout)
chains = {c["id"]: c for c in json.load(open("papers/answers/answer-key.json"))["chains"]}
for path in score["paths"]:
    chain = chains[path["id"]]
    found = "proved" if path["witness_exit"] == 0 else "missing"
    print(f"{chain['label']:9} {' -> '.join(chain['path'])}: {found}")
kept, excluded = score["counts"]["supported"], score["counts"]["excluded"]
print(f"supported paths kept {kept[0]}/{kept[1]}, false paths excluded {excluded[0]}/{excluded[1]}")
```

```text
supported bidirectional transformer -> VampNet -> WhAM: proved
supported PINNs -> XPINN -> $PINN: proved
supported SLAM -> WHAM -> OpenCap Monocular: proved
false     VAMPnet -> WhAM -> OpenCap Monocular: missing
false     XPINN -> PINNs -> curriculum regularization: missing
false     PINNs -> XPINN -> PINNs: missing
false     Boltz-1 -> PoseX: missing
false     normalizing flows -> simulation-based inference -> deep optimal sensor placement: missing
supported paths kept 3/3, false paths excluded 5/5
```

## Act 2. Two papers, one vocabulary

Extract two papers against a shared vocabulary, merge their spellings of
the parent method, check the result against a reference method catalogue,
and prove one claim.

<!-- gnd-run expect=0 output=stdout -->
```python
import json, subprocess, sys

subprocess.run([sys.executable, "-m", "gnd.examples.literature.interop", "run", "--out", "interop-run"], check=True)
for name in ("survey", "replication"):
    print(open(f"papers/interop_fixture/{name}.md").read().strip())
facts = json.load(open("interop-run/composed.population.json"))["facts"]
for row in facts["paper_names_parent_method"]:
    print(f"composed: {row['work']} names parent method {row['method']}")
print("check against the catalogue:", json.load(open("interop-run/check.json"))["outcome"])
for result in json.load(open("interop-run/witness.json"))["results"]:
    values = ", ".join(v["value"] for v in result["target"]["tuple"])
    print(f"witness {result['target']['fact_type']}({values}): {result['status']}")
```

```text
example:survey-2026 names P.I.N.N.s as a parent method. It was submitted on 2026-01-05 and published on 2026-03-03.
example:replication-2019 names PINNs as a parent method. It was submitted on 2019-04-12 and published on 2019-06-08.
composed: example:survey-2026 names parent method PINNs
composed: example:replication-2019 names parent method PINNs
check against the catalogue: accepted
witness paper_names_parent_method(example:survey-2026, PINNs): proved
witness catalog_method(PINNs): proved
```

Ask whether each "extends" edge respects publication order. The answer is
advice, never a refusal:

<!-- gnd-run expect=0 output=stdout -->
```python
import json, subprocess, sys

advice = json.loads(subprocess.run([sys.executable, "-m", "gnd.examples.literature.interop", "dates", "interop-run"],
                                   capture_output=True, text=True, check=True).stdout)
for edge in advice["edges"]:
    print(f"{edge['id']:10} {edge['outcome']:10} {edge['reason'] or ''}")
print(advice["counts"])
```

```text
new-to-old pass
same-year  pass
pinn       advisory   parent-published-later
unknown    unresolved unknown-work
conflict   unresolved conflicting-date
missing    unresolved missing-date
mixed      unresolved mixed-precision
preprint   unresolved publication-date-missing
{'advisory': 1, 'pass': 2, 'unresolved': 5}
```

## Act 3. A scientist's questions

Run the three competency examples (physics, molecular simulation and
algorithms) and list each question's answer.

<!-- gnd-run expect=0 output=stdout -->
```python
import json, subprocess, sys

subprocess.run([sys.executable, "-m", "gnd.examples.literature.depth", "--out", "depth-run"], check=True)
report = json.load(open("depth-run/report.json"))
for name in ("dynamics", "molecular", "algorithms"):
    case = report["cases"][name]
    print(f"{case['labels'][0]['label']} (verify {case['binding']['verification']}, check {case['binding']['check']})")
    for question in case["questions"]:
        print(f"  {question['id']}: {question['status']}")
```

```text
Shallow-water dam break (verify accepted, check accepted)
  equation-and-regime: supported
  boundaries: supported
  discretization: supported
  conservation-residual: unknown
OPES-eABF alanine example (verify accepted, check accepted)
  system-and-energy: supported
  sampling: supported
  approximation: supported
  transfer-validity: unknown
Randomized SVD (verify accepted, check accepted)
  operator-and-objective: supported
  components: supported
  qualified-complexity: supported
  device-runtime: unknown
```

The exact time step. The source states one step in three units, next to
an energy and a shorter duration that must not be confused with it:

<!-- gnd-run expect=0 output=stdout -->
```sh
cat papers/quantity_fixture/source.txt
```

```text
The reported time step is 2 fs.
The same step is 0.002 ps or 0.000002 ns.
The disturbance energy is 2 eV and a smaller duration is 0.0001 ps.
A separate step is 3 fs.
```

The population records `0.002 ps` as the exact pair 2 and 3 decimal
places, anchored to the second line. Check the anchor, prove the value and
replay the proof:

<!-- gnd-run expect=0 output=stdout -->
```python
import json, subprocess

def gnd(*args):
    return subprocess.run(["gnd", *args], capture_output=True, text=True, cwd="papers/quantity_fixture")

checked = gnd("check", "time.orm.yaml", "time.population.json", "--document", "source.txt",
              "--anchors", "time.anchors.json", "--format", "json")
print("check:", json.loads(checked.stdout)["outcome"])
proved = gnd("witness", "time.orm.yaml", "time.population.json", "--targets", "time.targets.json",
             "--raw", "--out", "time.witness.json")
target = json.loads(proved.stdout)["results"][0]
print("witness:", [v["value"] for v in target["target"]["tuple"]], target["status"])
replayed = gnd("replay", "time.orm.yaml", "time.population.json", "time.witness.json", "--raw")
print("replay exit:", replayed.returncode)
```

```text
check: accepted
witness: [2, 3, 'ps'] proved
replay exit: 0
```

## Act 3. Read again, and find more each time

Run the multipass reading example. First, list what each pass read, what
the agent returned, and which facts were kept after it:

<!-- gnd-run expect=0 output=stdout -->
```python
import json, subprocess, sys

done = subprocess.run([sys.executable, "-m", "gnd.examples.literature.reading", "run", "--out", "reading-run"],
                      capture_output=True, text=True, check=True)
report = json.loads(done.stdout)
json.dump(report, open("reading-report.json", "w"))
for stage, name in ((1, "broad"), (3, "targeted")):
    payload = json.load(open(f"reading-run/payload-{stage}.json"))
    print(f"{name} pass:")
    for attempt in payload["attempts"]:
        found = [f"{k}={r['value']}" for k, rows in attempt["response"]["facts"].items() for r in rows]
        print(f"  {attempt['section']}: {attempt['outcome']} {found}")
    facts = json.load(open(f"reading-run/{name}.population.json"))["facts"]
    print(f"  facts kept: {sum(len(rows) for rows in facts.values())}")
print("new vocabulary proposed:", sorted({k for a in json.load(open("reading-run/payload-3.json"))["attempts"]
                                         for k in a["response"]["proposal_keys"]}))
print("re-read:", report["revisit"])
print("gain:", report["supported_fact_gain"], "facts,", report["newly_answered"], "questions,",
      report["reading_bytes"], "bytes read")
print("producer calls:", report["producer_calls"])
print("conflicting labels, verify and check exits:", report["public_routes"]["reported-conflict"])
print("absence:", report["absence"], "recall", report["fidelity"])
```

```text
broad pass:
  study-opening: accepted ['system=alanine dipeptide in vacuum']
  annex-opening: empty []
  control-table: refused []
  facts kept: 2
targeted pass:
  study-methods: accepted ['approximation=Langevin integration at 300 K with 2 fs steps']
  study-limits: accepted ['explicit_denial=no barostat']
  facts kept: 4
new vocabulary proposed: ['method-family']
re-read: ['study-opening']
gain: 2 facts, 2 questions, 234 bytes read
producer calls: {'broad-extraction': 3, 'targeted-extraction': 2}
conflicting labels, verify and check exits: {'check': 1, 'verify': 1}
absence: {'below_floor_status': 'unavailable', 'status': 'qualified'} recall {'high': [2, 2], 'low': [1, 2]}
```

Then list what the run says about each question:

<!-- gnd-run expect=0 output=stdout -->
```python
import json

report = json.load(open("reading-report.json"))
for row in report["coverage"]:
    print(f"{row['question']:13} {row['section']:16} inspected={str(row['inspected']).lower():5} {row['state']}")
print("reads:", report["read_denominator"])
print("stop:", report["stop"])
```

```text
system        study-opening    inspected=true  supported
method        study-methods    inspected=true  supported
denial        study-limits     inspected=true  explicitly-denied
alternative   study-methods    inspected=true  inspected-not-found
annex-method  annex-methods    inspected=false unavailable
equation      control-equation inspected=false not-applicable
reads: {'attempted': 5, 'omitted': 0, 'scheduled': 6, 'unavailable': 1}
stop: required-coverage-completed
```

### Drive it from your host

The same loop reads your own documents with your own model. Put a
`profile.json` beside your roster, sources and model, and call
`reading.run(out, fixture=your_root, producer=your_producer)` from Python:
your producer gets each section's bytes and answers with facts, and the run
records what it read, what it skipped and why. `reading.replay(out,
fixture=your_root)` re-derives the run without calling your producer again.
The profile, the producer protocol, the limits and the run format are
described in the example's
[README](https://github.com/vasiloglou/gnd-public/blob/main/src/gnd/examples/literature/reading_fixture/README.md#drive-it-from-your-host).

## Act 3. Change your mind, and keep the verdicts honest

Publish a release from the reading run, apply the vocabulary change that
separates the whale senses, and report which lineage answers changed.

<!-- gnd-run expect=0 output=stdout -->
```python
import json, subprocess, sys

done = subprocess.run([sys.executable, "-m", "gnd.examples.literature.revision", "run", "reading-run",
                       "--out", "revision-run"], capture_output=True, text=True, check=True)
report = json.loads(done.stdout)
for method, ancestor, before, after in report["queries"]:
    print(f"{method} has ancestor {ancestor}: before {before}, after {after}")
print("still ambiguous:", report["ambiguous"])
print("coverage:", report["coverage"]["affected"], report["coverage"]["unrelated"])
print("saved review:", report["evolution"]["old_review"], "-> renewed:", report["evolution"]["new_review"])
```

```text
OpenCap Monocular has ancestor VampNet: before True, after False
OpenCap Monocular has ancestor DMD: before True, after False
WHAM has ancestor DMD: before True, after False
OpenCap Monocular has ancestor WHAM: before True, after True
VampNet has ancestor DMD: before True, after True
still ambiguous: {'candidates': ['WHAM', 'WhAM [whale]'], 'mention': 'WHAM'}
coverage: {'alternative': 'stale'} {'denial': 'current'}
saved review: stale -> renewed: current
```

Now give "VampNet descends from DMD" a verdict under each set of saved
opinions on its two independent supports:

<!-- gnd-run expect=0 output=stdout -->
```python
import json, subprocess, sys

for case, edition in [("both-approved", "current"), ("reject-whale-a", "current"),
                      ("reject-both", "current"), ("both-approved", "revised")]:
    done = subprocess.run([sys.executable, "-m", "gnd.examples.literature.verdict", "evaluate", "revision-run",
                           "--case", case, "--edition", edition], capture_output=True, text=True)
    verdict = json.loads(done.stdout)
    print(f"{case} ({edition} definition): {verdict['decision']}, exit {done.returncode}")
```

```text
both-approved (current definition): supported, exit 0
reject-whale-a (current definition): supported, exit 0
reject-both (current definition): unsupported, exit 2
both-approved (revised definition): revalidation-required, exit 3
```
