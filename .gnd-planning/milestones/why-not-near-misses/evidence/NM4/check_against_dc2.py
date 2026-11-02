"""NM4 T7: the shipped pages equal the DC2 drafts the owner saw, apart from the stated differences.

New pages: equal to the drafts minus the DC2 header comment and the two table markers.
Existing pages: every new passage in apply_edits.EDITS is on its page; each was taken from DC2's changes.md,
whose quoted new text this script also finds in the edits (python-api's new section differs only by
dropping the targets.json setup, as the spec states).
"""
import pathlib, re, sys
here = pathlib.Path(__file__).parent
sys.path.insert(0, str(here))
import apply_edits

dc2 = here.parents[1] / "checkpoints/DC2"
# Stated differences (NM4 T8 review, R1-R4): accuracy fixes found by the docs reviewer.
REVIEW_FIXES = {
    "docs/reference/disclosure.md": [
        ("value-free unless `--raw`; the Python functions return raw values",
         "value-free unless `--raw` or `raw=True`; `api.witness`, `api.replay` and `api.why_not` return raw values"),
        ("""The value is exactly `internal` or `customer`. GND resolves the mode in this
order:

1. If `GND_DISCLOSURE` holds anything else (`Customer`, a trailing space,
   the empty string), every command that can emit values refuses with exit 3,
   even when `--disclosure` is given. A mistyped lock never opens.""",
         """The value is exactly `internal` or `customer`. The mode governs the commands
in the table below that withhold or refuse values, and the commands that start
processes. For those, GND resolves it in this order:

1. If `GND_DISCLOSURE` holds anything else (`Customer`, a trailing space,
   the empty string), the command refuses with exit 3, even when
   `--disclosure` is given. A mistyped lock never opens."""),
        ("""   environment; else the mode is unset.
""", """   environment; else the mode is unset.

The commands listed under
[outputs that are the same in every mode](#outputs-that-are-the-same-in-every-mode)
and the commands that emit no values ignore the variable and the option's
value.
"""),
        ("`--unredacted` / `unredacted=True` refused under `customer`",
         "`--unredacted` or `unredacted=True`, where taken, refused under `customer`"),
        ("`--raw` / `raw=True` refused under `customer`",
         "`--raw` or `raw=True`, where taken, refused under `customer`"),
    ],
    "docs/how-to/disclosure-mode.md": [
        ("""print three fields of the check report: the violation
message, the offending facts and the redaction mode.""",
         """print two fields of the check report: the violation
message and the offending facts."""),
    ],
}
# Stated differences (NM4 F4): how-to prose names no exit code and no banned term.
HOUSE_STYLE = {"docs/how-to/disclosure-mode.md": [
    ("The check still fails with exit 1. The report", "The check still fails. The report"),
    ("can loosen it. In production you export it once", "can loosen it. In a real deployment you export it once"),
    ("Under `customer` GND refuses it with exit 3 and prints nothing on stdout,",
     "Under `customer` GND refuses it and prints nothing on stdout,"),
]}
failures = []
for rel in ("docs/reference/disclosure.md", "docs/how-to/disclosure-mode.md"):
    draft = re.sub(r"\A<!--.*?-->\n\n", "", (dc2 / rel).read_text(), count=1, flags=re.S)
    shipped = pathlib.Path(rel).read_text()
    shipped = shipped.replace("<!-- disclosure-table:start -->\n", "").replace("\n<!-- disclosure-table:end -->", "")
    for drafted, house in HOUSE_STYLE.get(rel, ()):  # F4: test_plan_app_docs prose rule
        draft = draft.replace(drafted, house)
    for drafted, fixed in REVIEW_FIXES.get(rel, ()):  # T8 findings R1-R4
        assert drafted in draft, (rel, drafted[:50])
        draft = draft.replace(drafted, fixed)
    if shipped != draft:
        failures.append(rel)
for path, edits in apply_edits.EDITS.items():
    text = pathlib.Path(path).read_text()
    for _, new in edits:
        if new not in text:
            failures.append(f"{path}: {new[:50]!r}")
changes = (dc2 / "changes.md").read_text()
norm = lambda s: re.sub(r"\s+", " ", s).strip()
targets = norm(" ".join(pathlib.Path(p).read_text() for p in apply_edits.EDITS))
# Stated differences: D5 (s5) dropped the three skill edits a closed milestone's census forbids.
DROPPED = {"Under `GND_DISCLOSURE=customer` every `--raw` is refused with exit 3 and nothing is written; under `internal` the raw view is the default.",
           "Under `GND_DISCLOSURE=customer`, `--unredacted` is refused with exit 3.",
           "Feedback redaction is the same in every disclosure mode; `internal` does not lift it."}
STATED = {}
blocks, current = [], []
for line in changes.splitlines() + [""]:
    if line.startswith(">"):
        current.append(line[1:].strip())
    elif current:
        blocks.append(current); current = []
sentences = []
for block in blocks:
    rows = [l for l in block if l.startswith("|")]
    prose = norm(" ".join(l for l in block if not l.startswith("|") and not l.startswith("#")))
    prose = re.sub(r"^`(discover|ilp-bridge)`: ", "", prose)
    sentences += rows + [s for s in re.split(r"(?<=[.;:])\s", prose) if len(s) > 20]
missing = [s for s in sentences if not any(s in d for d in DROPPED) and norm(STATED.get(s, s)) not in targets]
failures += [f"changes.md text not shipped: {s[:70]!r}" for s in missing]
print("\n".join(failures) or f"2 new pages equal their drafts; {sum(map(len, apply_edits.EDITS.values()))} edits present; {len(sentences)} DC2 sentences and rows shipped")
sys.exit(bool(failures))
