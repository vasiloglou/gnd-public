Retained local renewed-close opinion. Original response SHA256 971ea96a67aecabbe1a906c62a7f51d384667378b4d087d7adcb369eae8acb46. Only repository-root substitution to <REPO> is permitted; body otherwise unchanged.

# IE6 renewed close review — measurement

Verdict: close-with-carryovers. No surviving measurement blocker found. The bounded optimization has live deterministic evidence and observed lower session medians against its archived predecessor; it remains slower than full receipts on the tested controls. Remaining performance debt and the absent downstream workload must remain explicit.

## Subject and checked identities

Read-only review of committed HEAD202710d47d4846e62b9b06c2cf20a0ceceb0d311. Principal subjects:

- 011-phase-IE6.md SHA256 ca66e6cda6ec611f9a192bf55fd266f91dc60eca38be7b6f45c8ae100a0c7380.
- notes/IE6-close-question-sweep.md SHA256 60b89fd51b329aaef5c7023dbc106ab9dffbacba9864ad1a2af3eb7f94197b68.
- evidence/IE6/revision-comparison.json SHA256 c56628ae2204d8f633cdbbb9fe546d1126e244487d9a7e63cd3f74d919522954.
- evidence/IE6/measurement.json SHA256 23a17c57b7c771042b3c84148b93bb3fb119a0d952bd3169b79aac47931c2405.

Also read the final comparison driver, identity negatives and RED/GREEN outputs, descendant instrument mutant/outputs, measurement sanitation declaration, audit implementation, relevant oracle/timing tools, and both updated public documentation surfaces. Data-only calculations/hash reads below were independent checks, not reruns of product verification or timing.

## Exact checked claims

1. Final dependency closure is materially stronger than the initial exploratory comparison. Each revision map has2876 entries:989 package files,23 Python tool files,1862 fixture files and2 configuration files. I independently hashed all entries against the current candidate tree and the available archived baseline; both maps match. Candidate package coverage has no unlisted file outside excluded __pycache__ directories. Baseline/candidate maps differ only at src/gnd/incremental_state.py. Both tools/measure_transition_cost.py and packaged course model.orm.json are present. The driver itself matches the separately retained driver digest; all27 worker observations record that digest. This closes the specifically reproduced legacy-helper and packaged-course guard omissions. The initial comparison is explicitly superseded, not silently reused for final public percentages.

2. The final driver runs separate serial workers with the same executable, strips PYTHONPATH, sets the selected tree's src/tools search roots, checks the actual api module path, warms once and excludes startup/import time from each complete-replay timing. Rotation is ABC/BCA/CAB, with A=old session+receipts, B=new session+receipts and C=new full+receipts. It checks expected exit census for warm and timed results. It rejects profiling/tracemalloc, checks both identity maps after the run, and checks its own hash in each worker and at completion. Retained observation order and arm/root identities match this design. This is descriptive shared-host measurement; it does not establish statistical reliability.

3. I recomputed every median and max-minus-min range from the final revision samples. Exact session median decreases are5.8724709% reporter,17.3740303% course and5.9038146% localized. Rounded5.87%/17.37%/5.90% in011 and approximately6%/17%/6% in docs are correct. Old/new/full medians are respectively9.5940556/9.0306475/8.4962135 seconds;2.4105168/1.9917129/0.8551495;0.5744528/0.5405381/0.4226384. New session/full-receipt ratios are1.06290,2.32908 and1.27896: all sessions remain slower than the full control. Reporter new-session samples span0.8917140 seconds, exceeding the median decrease of0.5634081 seconds; the prose appropriately avoids a reliable/general speedup claim.

4. The separately executed integrated tool retains its original A=full, B=full receipts, C=session receipts meanings. I recomputed its reported medians/ranges and independently compared retained calls: all three arms have frozen expected exit/census, full payload/exit/branch equality, and B/C nonempty ordered complete-calculation equality. Reporter derivation bodies are4878/4878/179, course93/93/24 and localized24/24/6. All238 source and346 fixture/configuration map entries match current bytes. These are retained-result arithmetic/parity checks, not runtime reproduction. The final revision comparison's correctness scope is only expected exits/census; stronger current-source correctness belongs to this separate integrated oracle and focused gates, as the artifacts explicitly say.

5. Deterministic instrumentation liveness received an actual negative. The injected descendant rescan passed the prior two tests, then failed the strengthened two tests with actual descriptor visits7840 versus expected160 and1280 versus320. This addresses the root-only counter blindspot rather than asserting an unchanged passing counter. 011 preserves the unsafe hash-removal RED and withdrawal, distinguishes prepared-policy and raw-policy work, and retains full live hashing/exact equality. I read these artifacts; I did not reexecute the mutant or certify future instrument variants.

6. Public docs use the final same-run comparison values and expressly prohibit chaining historical IE5 absolute timings into a speedup claim. They preserve slower-than-full and small shared-host sample limits. The renewed question sweep retains missing547 workload, projected-footprint-versus-RSS limits, optional setup/freeze optimization debt and separately selected wider lanes. No downstream acceptance, date, default activation, release or merge claim is made by this measurement evidence.

## Carryovers and limits

- Full receipts remain faster on all three controls. Optional constraint-policy setup, extension planning and combined freeze work remain framework-maintainer follow-ups requiring explicit selection; this close does not start them.
- Three samples on one shared host are descriptive. Do not assert that all individual paired samples improved, that the median decrease is statistically reliable, or that historical IE5/current IE6 differences have an established cause.
- The offered547-program workload is absent and reporter-owned; public/synthetic controls do not establish its performance acceptance.
- Footprint projection is retained-cache accounting, not RSS, whole-process allocation or caller/observer storage. Fewer derivation bodies and descriptor visits are not every Python instruction.
- Both temporary baseline and raw artifact trees were available for this read-only identity check. Their future availability is not guaranteed by committing manifests.

No production/test edits, candidate imports, tests, benchmark/profile reruns, providers, credentials or agent spawning were used. Only file inspection and standard-library data/hash arithmetic, plus read-only Git HEAD identification, were performed. This review is one independent measurement opinion on the named committed subjects, not a certification or an opinion on later close artifact bytes.
