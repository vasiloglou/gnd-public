# Reply to #226 (all three requests)

Status: posted. First written in phase LR2 on 2026-11-23, completed in
phase LR3 the same day, and updated for the merged state on 2026-11-23. The
text below the line was posted by the owner's instruction on 2026-11-23 as
https://github.com/vasiloglou/gnd-public/issues/226#issuecomment-7118566523,
and #226 was then closed as completed. At posting, the three phases were
merged on `main` (PRs 243, 244 and 252) and in no release.

---

Thanks for the detailed measurements. All three requests are answered on
`main` (pull requests 243, 244 and 252). They are not in a release yet, so
to use them now, install GND from `main`.

**3. Why `verify` reports a failure, by constraint and row.** The JSON
report already carries this. The documents guide now has a section,
"Reading a failed verification", with the steps and a runnable example: the
failing constraints are the `verdicts` with `verdict: "fail"` and
`modality: "alethic"`, each with its `constraint_ref`, `constraint_type`,
`message` and `offending_facts`, and the failing derivations are the
`derivations` with `verdict: "fail"`. For a model with includes,
`constraint_ref` is an address in the composed model; `gnd flatten` writes a
record that maps it back to the declaring file and the constraint's `id`.
`gnd verify` itself is unchanged.

**2. Must a quote lie inside the section the model was shown?** No. An
anchor binds a span to the document whose digest the sidecar names, and the
span may lie anywhere in it; GND has no notion of a section. If your host
names the whole source version as the anchor document, a correct quote from
another section binds, and you can record the shown section in `block_id`.
If it names only the shown section, that quote is refused with
`anchor:binding-mismatch`. So the 44 claims you dropped for quoting outside
the shown section were dropped by your host's rule, not GND's. The other 38,
where the participant or predicate was not in the quote, are a host rule
GND's anchor check does not make. The anchor reference states the rule, and
an anchor still shows where a value occurs, not that the text supports the
claim.

**1. A reference recall and precision.** The literature example now has a
reference set: the twelve development papers of the regression corpus, with
31 labelled facts, and one recorded run of the reading stages over it
with Claude Sonnet as the reading agent. After the broad pass it found 9 of
31 facts (precision 9 of 10); after the targeted pass, 27 of 31 (precision
of the targeted rows 18 of 23). Of the four misses, one fact was never
produced, one was the right pair of names under another predicate, and two
named the work by the source's id rather than the paper's identifier. Both
passes used one prompt and no question, so the two rows differ only in
which sections were read. The run cost USD 0.29 and replays with no model call;
the record names the model, the CLI flags and the prompt.

Please read those figures as a measurement of one run on this set, not as
what you should get. The papers are short paraphrases written to state their
claims plainly, and the set scores a fact by the section it was read from,
while you scored quotes, so the two are not directly comparable and the run
does not say where your gap comes from. What it gives you is a labelled set
your own producer can run over, scored the same way
(`reference_set.score(your_run)`), next to this one.
