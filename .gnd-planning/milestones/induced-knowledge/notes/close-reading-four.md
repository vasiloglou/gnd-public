# Close reading four: a newcomer with an installed package

Lens: a newcomer reads `docs/tutorials/learn-rules.md` and then follows
`docs/how-to/learn-rules-commands.md` word for word, using an installed package.

Setup: a fresh `uv venv` at `<scratch>/venv`, with
`get_nick_done-0.1.0-py3-none-any.whl` (built from HEAD 5e25dbb) installed into
it. `PATH` put that venv first, and `which gnd python` showed both came from the
venv. I ran every block in order, in one shell (zsh), in the empty folder
`<scratch>/walk` (0 entries before the copy). I did not use the repository's
source to run anything.

## Step table

| Block | Expected (page text block) | Observed | Match |
|---|---|---|---|
| 0 copy + `gnd validate` | `OK: model.orm.yaml is a valid GND ORM model` | identical, exit 0 | yes |
| 1 `gnd measure ... \| grep fired_on` | `fired_on_negative=2/4 fired_on_positive=0/4 silent_on_negative=2/4 silent_on_positive=4/4 vacuous=0/8 unchecked=0/8` | identical, exit 0 | yes |
| 2 `gnd export ilp ... > /dev/null` + stand-in learner | `searched 40 rules; 4 hold ...` / `learned: wrong(A) :- f_refund_amount(A,V0,V1), V1 > 500   covers harbor, market, airport, station` | identical; both exit 0 | yes |
| 3 `gnd import ilp-rules` (learned) | `IMPORTED 1 learned clauses -> learned.proposal.json` / `clause 0 constraints[1]: covers 4 (support 4/4), vacuous 0, unchecked 0` | identical, exit 0 | yes |
| 4a stand-in `--also-claim north` | three lines, ending `deliberate mistake: also claiming that rule 0 covers north` | identical, exit 0 | yes |
| 4b `gnd import ilp-rules` (faulty), expect=3, stderr | `clause 0: coverage-mismatch: GND covers [] that the learner did not report, and the learner reports ['north'] that GND does not cover; vacuous [], unchecked []` | identical text on stderr, stdout empty, exit 3, no `faulty.proposal.json` | yes |
| 5 `gnd discover ... \| grep -E` | `EMITTED 10` / `SUPPRESSED declared=1 spanning-uniqueness=3` | identical, exit 0 | yes |
| 6a two `gnd evolve preview ... \| grep breaking` | `breaking: false` twice | identical | yes |
| 6b `gnd evolve apply` + grep verbalization | `[from induced, proposed; modality=deontic] If refund_amount(refund = $v_v0, amount = $v_v1), then $v_v1 is at most 500.` | identical, apply exit 0 | yes |
| 6c `gnd check batches/market.yaml \| grep -A1 ADVISORY` | `ADVISORY (deontic)` / `[warning] constraints[1]: ... {'$v_v0': '601', '$v_v1': '750'}.` | identical; full `gnd check` exits 0 (`pass=2 fail=0 warning=1`) | yes |

Tutorial numbers checked against the run and the shipped data:
- The data table matches every batch file (north 40/120/75, ..., station 640/95), and `labels.json` matches the clean and flagged split.
- Written rule: 2 of 4 flagged, 0 of 4 clean. Matches block 1.
- Learned rule: 4 of 4 flagged. Matches block 3. "0 of 4 clean" follows from `covers 4` minus `support 4/4`, and from `counterexamples: []` in the proposal (see finding 5).
- Step 5: 10 emitted, then 1 declared and 3 spanning suppressed. The 5/2/3 grouping matches `discovered.json` exactly:
  - uniqueness on refund_amount.refund and refund_channel.refund, plus three mandatory refund roles, is 5 sensible rules;
  - uniqueness on refund_by.customer and refund_amount.amount is 2 accidents;
  - mandatory customer, amount and channel is 3 rules about how the file is written.
- Step 6: in a fresh copy (`<scratch>/before`), market before the apply gives `ADVISORY (none)`, so the written rule is quiet. After the apply there is one warning, on 601 for 750. Matches the before/after table.
- Both SVG figures' text matches the data (1200, 750, 1500, 640; north's largest refund is 120; exit 3).

Links: every relative link in the five pages resolves under `docs/`, including both SVGs and `course-planner.md#what-youll-build`, which is the heading "What you'll build". All the GitHub "Files on GitHub" targets exist at HEAD under `src/gnd/examples/refunds/` and `src/gnd/skills/gnd-model-evolve/`.

## Findings

1. **Blocking. The tutorial's "Before you start" installs a GND that cannot run the walk.**
   - Claim: `learn-rules.md` says to "Install GND and the Claude Code plugin as the [plugin page] shows". `marketplace-plugins.md` installs `uv tool install get-nick-done==0.1.0`, the PyPI release.
   - Reproduction: I took the `v0.1.0` tag's `src` with `git archive` into `<scratch>/v010src` and used it as an installed package (PYTHONPATH). The page's copy step failed with `FileNotFoundError: .../gnd/examples/refunds`, and `gnd discover` gave `invalid choice: 'discover'`.
   - Contrast: the commands page links to the course planner's setup, which says "These pages need a GND newer than the 0.1.0 release on PyPI" and installs from a checkout. The tutorial gives no such warning.
   - Aggravating: the HEAD wheel also reports `gnd 0.1.0`, so `gnd --version` cannot tell a newcomer which install they have.
   - Caveat: PyPI was not contacted. This assumes the PyPI 0.1.0 equals the `v0.1.0` tag.
   - Disposition: point the tutorial's "Before you start" at the same install-from-checkout note the course planner uses (or at the commands page's setup), until a release ships these commands.

2. **Blocking (false reference claim). `docs/reference/discover.md` "Limits" says `gnd evolve preview` "cannot preview a model that declares reference populations".**
   - Contradicted by: the release notes ("`gnd evolve` binds a model's reference populations as `gnd validate` does") and by the code (`src/gnd/evolve/service.py`, `_load_model_bytes`, IK4-Q2).
   - Reproduction: I copied the installed `examples/dispatch` folder, whose model declares reference population `catalog`, into `<scratch>/refpop`. `gnd discover model.orm.json seed.pop.json ...` emitted 55. Then `gnd evolve preview model.orm.json d.json --workspace . --records records --out p.json` succeeded with `breaking: false`, exit 0.
   - Disposition: delete or reword that limit. The second limit (YAML-only values such as an unquoted date) was not tested.

3. **Hardening. The suppression names that discover prints are not named in its reference.**
   - Block 5 prints `SUPPRESSED declared=1 spanning-uniqueness=3`, and the dispatch run adds `redundant-subset` and `redundant-frequency`. `discover.md` lists the suppression rules only in prose and never gives these keys.
   - A newcomer cannot map `spanning-uniqueness` to "a key spanning all roles is trivially unique" except by guessing.
   - Disposition: add each report key beside its rule in the suppression list.

4. **Hardening. `discover.md` says example ids have the form `ft<k>#<i>`, but mandatory suggestions carry `ot<k>#<i>`.**
   - Reproduction: `discovered.json` from block 5 contains `"ot0#0"`, `"ot2#0"`, `"ot4#0"` and `"ot5#0"`.
   - Disposition: document the `ot` (object-type roster) form.

5. **Hardening. The learned rule's "0 of 4 clean weeks accused" is never printed by any command on the page.**
   - The import prints `covers 4 (support 4/4)`. The reader must work out that 4 covered minus 4 flagged leaves 0 clean, or know that `support` is "covered negatives over all covered examples" (`ilp-bridge.md`). The commands page does not explain `covers` or `support`.
   - After the apply, the newcomer cannot re-score with `gnd measure`. `labels.json` binds the old model digest: `ERROR: label manifest labels.json was written for model sha256 8e03..., not this model (6e77...)`, exit 3. That is correct behaviour, but the page does not say so.
   - Disposition: one sentence under block 3 explaining covers and support, and that the manifest binds the pre-apply model.

6. **Hardening. `gnd measure --labels` prints a confusing header.**
   - Its first stdout line is `REDACTION applied: ` with nothing after the colon, although the refunds model declares no redaction. `measure.json` holds `redaction: {declarations: [], mode: applied}`.
   - The page hides the line with `grep`. A newcomer who drops the grep sees an unexplained line, and `measure-labels.md` does not mention it.
   - Disposition: omit the header when there are no declarations, or document it.

7. **Hardening. The tutorial says "in its own words" twice for a paraphrase.**
   - Step 3: "**a refund amount is at most 500**". Step 6: "*if a refund has an amount, that amount is at most 500*".
   - The model's own words, as block 6b prints them, are `If refund_amount(refund = $v_v0, amount = $v_v1), then $v_v1 is at most 500.`
   - Disposition: say "in plain English", or quote the real verbalization.

8. **Hardening. "The exact files the claim was checked against" overstates the provenance.**
   - The applied constraint's evidence refs are `ilp/export.json`, `ilp/clauses` and `ilp/run`. The last two are fixed labels, documented in `ilp-bridge.md`, not files. The real files are `learned/learned.clauses.json` and `learned/learned.run.json`.
   - The digests do match those files, which I checked with shasum.
   - Disposition: "the digests of the files ..." would be exact.

9. **Completeness. Terms.**
   - The tutorial defines the following:
     - proposal, induced, proposed and advisory (the label table);
     - Popper (linked);
     - the stand-in learner.
   - The commands page defines the negative/positive class words, and `V1` as the amount.
   - "ILP" is never expanded on either learn-rules page; only `ilp-bridge.md` expands it. That is acceptable for the business page, and a gap on the commands page, which uses `gnd export ilp` with no gloss.
   - "deontic" appears in outputs 6b and 6c and is never tied to "advisory" on the commands page, though `ADVISORY (deontic)` hints at it.
   - "label" means two things: the auditors' verdicts in `labels.json`, and the three rule labels in step 6. A newcomer may conflate them.
   - Disposition: a one-line gloss for ILP and for deontic = advisory on the commands page.

10. **Completeness. Re-running in the same folder.**
    - A second pass of the page in the same folder exits 11 at the export: `--out ilp already exists; nothing was written`. Later outputs are refused the same way, as the discover rerun showed.
    - The page does say "In an empty folder", and the exit is documented in `ilp-bridge.md` and `discover.md`.
    - Also, `gnd evolve apply` rewrites `model.orm.yaml` from a commented YAML file into one line of JSON, so the example's header comment is lost. That is unmentioned and could surprise a reader who opens the file.
    - Disposition: optional note.

11. **Completeness. Each failure shown has its reason and how GND caught it.**
    - Step 4 (the overstated claim) gives both, the figure repeats them, and they match the stderr exactly.
    - Step 1's "lets half the flagged weeks through" is explained (750 and 640 are under 1000).
    - No gap found.

## What I did not check

- The PyPI 0.1.0 artifact itself. Finding 1 used the `v0.1.0` git tag as a stand-in; I made no network install.
- The Claude Code prompts and the `/gnd:gnd-model-evolve` skill conversation. In particular, I did not check whether the skill can apply "only the ones I accept" from one multi-rule proposal (`discovered.json`).
- `--target popper` export and import, and any real Popper run.
- The YAML-only-value limit in `discover.md`, and the other discover families (value, frequency, subset, equality, exclusion), beyond the one dispatch run.
- The rendered MkDocs site: admonitions, the `app-figure` scrolling, anchors as the site generator slugs them. Links were checked as files and headings only.
- The `measure-labels.md` expected-state mode, which the walk does not use.
- Python versions other than the venv's default (3.14).
