# Panel Review
## Summary
Five valid close reviews identify two agreed evidence gaps. The coordinator will exercise role reversal and retain reproducible wheel and fixture checks. Gemini returned a malformed response.
## MVP Triage
**3 of 14 retained concerns are blocking** (8 hardening, 3 completeness).
## Agreed Concerns
- **MEDIUM — Reproducibility of the fixture and installed-wheel parity checks**: Record the exact build, install, parity, eight-command and fixture-sweep commands verbatim, with interpreter and module/CLI paths, or check them in as a script. Rerun them at close against the final HEAD and record the output in the close delta. Record the exact sweep command and the fixture-validity selection rule alongside the count \(or promote the sweep to a gate or regression test\) so the headline path-vs-loaded-model parity claim can be re-run and re-verified at close.
  - claude:close-wheel-parity-unreproducible — .gnd-planning/milestones/compact-growth-context/notes/compact-growth-context-plan.md at section 9, line 33 — &\#x27;At close run repository-prescribed checks, component and layer checks, wheel installation, CLI/API parity, and the packaged host example. Record measured sizes and any limitations.&\#x27;
  - glm:gc2-close-parity-sweep-not-reproducible — .gnd-planning/milestones/compact-growth-context/notes/close-delta.md at Public compatibility row, line 9 — The row states: &quot;Path and loaded-model growth outputs also matched on all 229 valid \*.orm.yaml fixtures exercised on this checkout.&quot; The number appears only as the bare output line &quot;Valid fixture pairs with byte-identical views: 229&quot; in 003-phase-GC2.md&\#x27;s Gate output; none of the five recorded gates \(pytest lane, ruff, two components\_index calls, wheel build/install/example\) produces it, no script or test in scripts/, tools/ or the suite performs the sweep, and the checkout holds 322 \*.orm.yaml files, so the rule selecting the 229 &quot;valid&quot; ones is unrecoverable from the artifacts.
- **MEDIUM — Reversed role bindings lack an executable negative case**: Have the example derive role bindings from the occurrence against the fact&\#x27;s ordered roles. Add a test showing that a swapped binding, or an occurrence like &\#x27;V-1 has version W-1&\#x27;, is not recorded as reuse. Drop the redundant inequality. Add a negative-case regression that ties the recorded bindings to the source occurrence \(for example, assert that the reversed assignment contradicts the captured span&\#x27;s subject-role order, or that a role-player search with swapped players cannot reproduce the occurrence\), so the stated acceptance criterion is machine-checked rather than pinned only to the example&\#x27;s recorded value.
  - claude:reversed-binding-check-vacuous — .gnd-planning/milestones/compact-growth-context/notes/compact-growth-context-plan.md at line 44 and line 18 — &\#x27;Check reversed role bindings are ineligible for reuse.&\#x27; and &\#x27;Check the role-specific occurrence before reusing a fact.&\#x27;
  - glm:gc2-reversed-binding-assertion-vacuous — .gnd-planning/milestones/compact-growth-context/notes/compact-growth-context-plan.md at Acceptance details, line 44 — The plan requires: &quot;Check reversed role bindings are ineligible for reuse.&quot; The only regression touching this is tests/test\_growth\_view.py:64-65, where \`assert rec\[&quot;decisions&quot;\]\[0\]\[&quot;bindings&quot;\] \!= \{&quot;work&quot;: &quot;V-1&quot;, &quot;version&quot;: &quot;W-1&quot;\}\` is logically implied by the preceding line&\#x27;s equality assertion and would pass for any recorded mapping; the README example hardcodes the directed bindings with a reason string, so ineligibility of the reversed assignment is demonstrated narratively via the captured span &quot;W-1 has version V-1&quot; and the view&\#x27;s role order, with no executable negative case that fails if a host records the reversed assignment against that occurrence.
## Divergent Views
- claude:direct-lookup-not-verified — .gnd-planning/milestones/compact-growth-context/notes/compact-growth-context-plan.md at lines 44 and 46 — &\#x27;compare a direct lookup against the resolved fact definition&\#x27; and &\#x27;shows the agent a partial flag, the full view digest and the exact selected rows at each search.&\#x27;
- claude:gc2-cli-grammar-test-unrecorded — .gnd-planning/milestones/compact-growth-context/notes/compact-growth-context-plan.md at line 44 \(Acceptance details, GC2\) — &\#x27;Verify the default against repository verbalization snapshots and the independent CLI grammar.&\#x27;
- claude:span-coordinates-unbound — .gnd-planning/milestones/compact-growth-context/notes/compact-growth-context-plan.md at line 46 — &\#x27;The runnable example retains these along with the source span and decision in a host JSON record.&\#x27;
- codex:guarded-signature-omits-operands — .gnd-planning/milestones/compact-growth-context/notes/compact-growth-context-plan.md at Acceptance details, line 40 — The plan requires: &quot;For each registered family check the signature against the family&\#x27;s expected operands and host, including their order.&quot; In src/gnd/model\_verbalization.py:582-594, a guarded constraint retains only each atom&\#x27;s path, fact ID, and sorted binding role names; it drops binding terms and comparison operands.
- qwen:gc1-family-registry-coverage-growth — .gnd-planning/milestones/compact-growth-context/notes/compact-growth-context-plan.md at Acceptance details following the first panel, GC1 paragraph — &quot;Family registration growth must cause the coverage test to fail until a signature case exists.&quot;
- qwen:gc2-defer-adds-no-fact — .gnd-planning/milestones/compact-growth-context/notes/compact-growth-context-plan.md at Acceptance details following the first panel, runnable-example paragraph — &quot;Check that the first search yields zero rows, the next finds the known included fact, and ambiguous evidence yields defer with no added fact.&quot;
- qwen:gc2-gate-output-unanchored — .gnd-planning/milestones/compact-growth-context/003-phase-GC2.md at \#\# Gate output and \#\# Review and rulings — One unattributed run is recorded: &quot;1199 passed, 2 deselected in 142.52s \(0:02:22\)&quot;. The rulings section then describes later repairs, including &quot;A failing regression test reproduced the compatibility problem; extracting the prior vocabulary-digest implementation preserved historical reference digests and fixed the regression. Claude approved the final repair.&quot; Nothing states that the gate block, the ruff/components\_index exits, or the wheel SHA-256 &quot;1f388ac0532a3c192bae867aebd8cf03955748e09cc83862ffa231ae0bc8a9b5&quot; were measured after that final loader repair rather than before it.
- qwen:gc2-reference-page-documentation-unrecorded — .gnd-planning/milestones/compact-growth-context/notes/compact-growth-context-plan.md at 5. Documentation and compatibility — &quot;Document the flag and keyword on existing CLI and Python reference pages.&quot;
- qwen:gc2-review-rounds-1-3-unpinned — .gnd-planning/milestones/compact-growth-context/003-phase-GC2.md at \#\# Review and rulings and frontmatter evidence — &quot;See the four GC2 rounds and their per-finding decisions.&quot; and &quot;The missing refusal and the stale included-row refusal both reproduced before repair.&quot; The only review artifact pinned is &quot;.gnd-planning/milestones/compact-growth-context/notes/reviews/phase-GC2-r4/review.md&quot;.
- qwen:gc2-root-identity-after-evidence-only-edit — .gnd-planning/milestones/compact-growth-context/notes/compact-growth-context-plan.md at Acceptance details following the first panel, GC2 paragraph and mutation paragraph — &quot;Verify a stale include fails and raw root identity changes after an evidence-only edit even when the view digest stays equal.&quot; and &quot;Bind expected\_model\_sha256 to the root bytes from which the view was loaded and reauthenticate pins through the existing evolution workflow.&quot;
## Prioritized Fix Plan
None.
## Response Completeness
- claude: 5 concerns, response read complete.
- codex: 1 concerns, response read complete.
- qwen: 6 concerns, response read complete.
- kimi: 0 concerns, response read complete.
- glm: 2 concerns, response read complete.
- claude reported reading .gnd-planning/milestones/compact-growth-context/notes/compact-growth-context-plan.md.
- claude reported reading .gnd-planning/milestones/compact-growth-context/003-phase-GC2.md.
- claude reported reading .gnd-planning/milestones/compact-growth-context/notes/close-delta.md.
- claude: 5 of 5 concerns anchor a verbatim quotation in the artifact bytes.
- codex reported reading .gnd-planning/milestones/compact-growth-context/notes/compact-growth-context-plan.md.
- codex reported reading .gnd-planning/milestones/compact-growth-context/003-phase-GC2.md.
- codex reported reading .gnd-planning/milestones/compact-growth-context/notes/close-delta.md.
- codex: 1 of 1 concerns anchor a verbatim quotation in the artifact bytes.
- qwen reported reading .gnd-planning/milestones/compact-growth-context/notes/compact-growth-context-plan.md.
- qwen reported reading .gnd-planning/milestones/compact-growth-context/003-phase-GC2.md.
- qwen reported reading .gnd-planning/milestones/compact-growth-context/notes/close-delta.md.
- qwen: 6 of 6 concerns anchor a verbatim quotation in the artifact bytes.
- kimi reported reading .gnd-planning/milestones/compact-growth-context/notes/compact-growth-context-plan.md.
- kimi reported reading .gnd-planning/milestones/compact-growth-context/003-phase-GC2.md.
- kimi reported reading .gnd-planning/milestones/compact-growth-context/notes/close-delta.md.
- glm reported reading .gnd-planning/milestones/compact-growth-context/notes/compact-growth-context-plan.md.
- glm reported reading .gnd-planning/milestones/compact-growth-context/003-phase-GC2.md.
- glm reported reading .gnd-planning/milestones/compact-growth-context/notes/close-delta.md.
- glm: 2 of 2 concerns anchor a verbatim quotation in the artifact bytes.
## Advisory Boundary
This panel is advisory only; no changes were applied to reviewed artifacts.
Qwen was handed the complete digest-checked artifact bytes in its prompt. The other reviewers were given artifact paths and digests and read the files themselves. For those reference-delivered seats, this run establishes what was offered and that the files did not change while it ran; it does not establish what each reviewer read. Cited evidence is evidence of engagement, never of complete reading.
