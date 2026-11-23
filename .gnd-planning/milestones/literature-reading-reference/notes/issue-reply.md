# Draft reply to #226 (all three requests)

Status: draft, first written in phase LR2 on 2026-11-23 and completed in
phase LR3 the same day. The owner posts it; nothing here is posted. Update
the merge status before posting: on 2026-11-23 the three phases are in pull
requests 243 (LR1), 244 (LR2) and the LR3 pull request, none merged and none
released.

---

Thanks for the detailed measurements. Two of your three requests have
answers on `main` once the open pull requests for them merge; neither is in
a release yet.

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

**1. A reference recall and precision.** The literature example now ships
a reference set: the twelve development papers of the regression corpus
with 31 labelled facts, and one recorded run of the reading stages over it
with Claude Sonnet as the reading agent. After the broad pass it found 9 of
31 facts (precision 9 of 10); after the targeted pass, 27 of 31 (precision
of the targeted rows 18 of 23, two of the misses a right pair of names under
the wrong predicate). The run cost USD 0.29 and replays with no model call;
the record names the model, the CLI flags and the prompt.

Please read those figures as a measurement of one run on this set, not as
what you should get. The papers are short paraphrases written to state their
claims plainly, and the set scores a fact by the section it was read from,
while you scored quotes, so the two are not directly comparable and the run
does not say where your gap comes from. What it gives you is a labelled set
your own producer can run over, scored the same way
(`reference_set.score(your_run)`), next to this one.
