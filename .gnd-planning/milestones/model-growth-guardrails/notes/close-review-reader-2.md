Retained text of the reader's report. Local paths read `<repo>`, `<scratch>`.

# Close review, reader 2: rule verbalization (MG1) and extraction guidelines (MG4)

Subject: branch `claude/process-milestone-model-growth-guardrails-4cac43` at `2ed15f8`
(MG3 41be029, MG4 9e36e70, MG5 7961119, MG6 2ed15f8 since main `9b069e2`).
Lens: plan §2.1, §2.4, predicates 1 and 4. I looked for constraint leakage, forgery,
drift in the flag-free bundle, partial renderings, and docs that contradict the code.
I treated the repository as read-only. Every probe wrote only under
`<scratch>/close/r2/`.

## Verdict

**approve-with-fixes.** Nothing is blocking. Predicates 1 and 4 hold by my own
measurements. Findings 1 to 3 are text or completeness fixes. Finding 4 is hardening
that MG4 inherited. Findings 5 and 6 are small.

## What holds (reproduced)

- **The flag-free bundle does not drift (predicate 4, MG-R1).** I ran `gnd extract`
  without the flag over all 250 `*.orm.yaml` files under `tests/fixtures`, `examples`
  and `src/gnd/examples`. I ran it once against a `git archive 9b069e2` copy of `src`
  (`PYTHONPATH`, with the same venv) and once at HEAD. For each file I compared the
  exit code, the SHA-256 of every bundle file, and the stdout and stderr digests with
  the temp path normalized. Result: 0 differences (189 exit 0, 61 exit 3). Script:
  `r2/parity.py`; tables: `r2/par-before.json` and `r2/par-after.json`.
- **The guideline is constraint-blind (predicate 4, O11).** I loaded each of the 191
  loadable corpus models and compared its guideline with the guideline of the same
  model stripped of every constraint except external uniqueness. I removed inline and
  top-level constraints and `rejected_proposals`. Result: 186 identical, 0 different,
  and 5 stripped models no longer loaded, so they were not compared. Script:
  `r2/blind.py`. `resolve_reference_value_type` and `primitive` read no constraints.
- **No line forgery (O21).** I put each line boundary that `str.splitlines()` knows into
  a description `summary`, a description `notes`, an object-type `name` and an
  `inverse_reading`. The payloads were heading-shaped and `- Identified by:`-shaped.
  The boundaries were `\n \r \v \f \x1c \x1d \x1e \x85 U+2028 U+2029 \r\n`. Every
  variant loaded, rendered exactly one `#` title and one `## Fact type` per fact type,
  forged no `Identified by` line, and leaked no description extra key. Script:
  `r2/forge.py`. Duplicate and missing role names are refused by validation, so
  `role_object_types` cannot collapse two roles into one section.
- **`--guidelines` records the digest.** `gnd extract src/gnd/examples/growth/model.orm.yaml --out … --guidelines`
  exits 0, writes five files, and lists `model.guidelines.md` in `artifacts.json` with
  the file's SHA-256.
- **MG1 parity (predicate 1).** For every corpus model with rules (108 models, 280
  rules, 19 of them prose), every `rendered` text appears in that fact type's
  `[fact-type:<id>]` line of `render_model_verbalization`, as
  `This fact type is derived: <text> reading=`. Result: 0 missing.
  `render_model_verbalization(path)` equals the output for the loaded model on all 108
  and raises on none. Script: `r2/par1.py`. My glob differs from MG1-C2's, so my
  counts are not its floors.
- **MG1 edge cases.** Probe: `r2/mg1.py`.
  - A `derivation: derived` fact type with no rule returns exit 3.
  - `fact_types=[]` returns no rules, and duplicate ids are collapsed. Both match the
    reference page.
  - A non-derived id or an unknown id returns exit 3.
  - A `str`, `[1]` or `dict` passed as `fact_types` raises `TypeError`.
  - An in-memory `Model` mutated to a ghost body fact type, or to a head term
    containing a newline, returns exit 3 with no text. There is no partial rendering.
- The text of `docs/reference/rule-verbalization.md` matches the code.

## Findings

### 1. completeness: the guideline does not print the reference mode, though the plan, the header and the docs say it does

The plan says, in §2.4, "per role: … its reference mode". The guideline's own header
says "Constraint-blind: readings, role players, object-type descriptions, reference
modes and primitives only". `docs/guides/documents.md` and SKILL.md say the same. The
generator never prints `reference.mode`. It prints only the three
`entity_reference` kinds, and in two cases it says less than the constraint-blind
verbalization in the same bundle:

- **Unit-based entity.** In `tests/fixtures/models/library.orm.yaml`, `loan_period` is
  declared as `reference: {mode: unit-based, unit: day, measure_type: Duration}`.
  - Verbalization: "LoanPeriod is identified by a value in day (Duration)."
  - Guideline: "- Identified by: no printable reference value".
  - The extractor loses the unit, which is part of what the role means.
- **Composite entity.** For `copy`, the verbalization names the component roles ("the
  combination of work (in fact type copy_is_of_title) and mark (…)"). The guideline
  says only "a combination of roles (composite reference)".

Reproduce:
`uv run gnd extract tests/fixtures/models/library.orm.yaml --out $T --guidelines`, then
compare `library.verbalization.txt` line 22 with the `### Role \`term\`` section of
`library.guidelines.md`.

Corpus census (`r2/cmp.py`): 10 unit-based entities, 5 composite entities and 13
subtype entities all fall to the generic sentences.

Fix, either of:
- (a) print `reference.mode`. For `unit-based`, also print the unit and measure type.
  For `composite`, also print the component role and fact-type pairs. This is model
  content and reads no new constraint.
- (b) change the header, the plan text and the docs to "identifying value type", and
  record that the mode is omitted.

### 2. completeness: the CLI help still describes a four-file bundle

`src/gnd/commands/extract.py`:
- The parser description lists the four files and does not mention the optional
  guideline file.
- The `--out` help still says "output directory for the four-file bundle".
- The MG4 spec Design section said "the description mentions the optional fifth file".
- `SKILL.md` line 63 still opens "That writes four files named after the model's stem",
  although the table under it now has five rows.

Reproduce: `uv run gnd extract --help`.

Fix: name `<stem>.guidelines.md` as optional in the description and in the `--out` help,
then recapture the `gnd extract` RF1 help golden (O23). Change the SKILL sentence to
"four files, five with `--guidelines`".

### 3. completeness (docs vs code): "the guide states no constraint" is not literally true

These say the guideline states no constraint:
- `docs/how-to/grow-a-model.md` ("The guide states no constraint").
- `docs/agents/documents.md`.
- `docs/guides/documents.md` ("It stays constraint-blind").

They do not mention the one exception that the contract §4a and the module docstring do
state: an anchoring external uniqueness is read, and it shows up as "Identified by: a
combination of roles". Reproduce with T2d's fixture, or with `r2/deon.py`.

Fix: add the exception sentence on each page, or link to contract §4a.

### 4. hardening (MG-R8 adjacency, inherited): an unreviewed deontic external uniqueness becomes an identity statement

`r2/deon.py` adds an external uniqueness with `source: llm-inferred`,
`status: proposed` and `modality: deontic` over two fact types of an
external-reference entity. The model loads. The guideline then prints, for both roles,
"- Identified by: a combination of roles (composite reference)". So an unconfirmed
deontic constraint is presented as how the entity is identified.

`render_verbalization` does the same at `9b069e2`, because `reference_identity` ignores
status and modality. MG4 therefore inherits this rather than introducing it, and
ruling D2 (a) accepted that external uniqueness counts as reference content. Even so,
MG-R8 says "the guideline … never presents a constraint as fact", and an unattended
model (MG5) is exactly where such constraints arise.

Fix: record this as a milestone-close open question beside MG4-Q2. Options:
- restrict composite identity to non-deontic, non-proposed constraints, in both
  renderers together;
- or annotate the sentence as "(from a proposed constraint)".

### 5. hardening (minor): derived fact types are not marked

The guideline lists `customer_is_active`, a `derivation: derived` fact type, exactly
like an asserted one. Yet `artifacts.json`'s `header_template.covers` leaves it out, so
the extractor must not extract it. Reproduce:
`gnd extract src/gnd/examples/growth/model.orm.yaml --out $T --guidelines`, then compare
`model.guidelines.md` with `covers`.

The flag-free verbalization behaves the same way, so the guideline is not inconsistent
with the rest of the bundle. But the guideline is the file that tells the extractor
what to extract.

Fix: add a "- Derived: not extracted (see covers)" line for derived fact types, or
leave them out of the guideline. Either way the change touches only `--guidelines`
bytes, not MG-R1.

### 6. hardening (documented, not a defect): raw HTML and Markdown pass through

A description such as `<script>alert(1)</script> [link](http://x) ![i](http://x/a.png)`
is repeated verbatim inside quotes. Reproduce with `r2/edge.py`. This is already
disclosed as R-F5 and MG4-Q1 ("plain text, do not render"). I list it only so the
close carries MG4-Q1 forward. A rendering viewer, such as a docs site or an IDE
preview, would fetch the image URL.

## What I ran

- `uv run pytest -q -p no:cacheprovider tests/test_extract_guidelines.py tests/test_extract_vocabulary.py tests/test_extract_cli.py tests/test_rule_verbalization.py`:
  86 passed.
- Probes, all under `r2/`, all run with `PYTHONDONTWRITEBYTECODE=1`:
  - `parity.py`: flag-free parity, base against HEAD.
  - `blind.py`: corpus constraint stripping.
  - `forge.py`: line-boundary forgery.
  - `edge.py` and `edge2.py`: duplicate and missing role names, HTML.
  - `deon.py`: proposed deontic external uniqueness.
  - `cmp.py`: identity-kind census.
  - `mg1.py`: verbalize_rules refusals and mutations.
  - `par1.py`: MG1 corpus parity and the path fix.
- I also ran `gnd extract` by hand on the growth and library models.

## What I did not run

- The full MG4 gate list in the spec: RF1 pins, layering, RF6, disclosure, arch, the
  fidelity and doccheck consumers on a five-file bundle, and T12 timing.
- The docs gates: `zensical build --strict`, `tools/check_docs.py`,
  `tools/run_tutorials.py`, which would include the how-to's
  `grep "Same role players"` block.
- The anonymity scan and the broad test lanes.
- MG1's asserted corpus floors under its own glob.
- I did not verify the MG2, MG3 or MG5 lanes beyond their shared docs.
