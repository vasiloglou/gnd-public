# Draft reply to #226 (interim, requests 3 and 2)

Status: interim draft, written in phase LR2 on 2026-11-23. The owner posts
it; nothing here is posted. The final draft, with request 1's figures, is
written at milestone close after LR3. Update this draft's merge status when
the pull requests merge.

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

**1. A reference recall and precision.** Not yet. It needs the host
producer interface that is being built now, and a recorded run over a
labelled set. We will follow up here with the figures and the settings that
produced them.
