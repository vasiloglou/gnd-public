Retained text of the reader's final message. The longer report it names at `<scratch>/close-r2/report.md` was not found after the run (its write was not retained), so this summary is the retained record. Local paths read `<repo>`, `<scratch>`.

# Close reader 2: UG3, the unattended source header as a security control

Verdict: approve-with-fixes. Nothing blocking; four hardening findings and five completeness findings. I edited no repository file; every reproduction ran in `<scratch>`, with the `5c6a0c5f` base loaded from `<scratch>/base/src` through PYTHONPATH.

**Answers to the questions:**
- **Can the gate pass with a span unchecked under `--require-documents`?** Not for the three walked locations (element, constraint, sample). It can for spans on operations or obligations (F1) and for a near-miss mode spelling (F2).
- **Is any span counted as re-hashed that was not?** No.
- **Can a source-document operation reach a constraint branch, or enter a v1/v2 proposal, record or preview?** No to both.
- **Silent reorder or duplicate?** No. A reorder in the candidate alone and a duplicate add (including twice in one proposal) both exit 3. A delete then re-add of the same digest does reorder, but explicitly (F8).
- **Wrong exit band?** No source-document message hits a wrong band through substring matching. The one wrong band found is F3, a raw validation error that falls to 70.
- **Does flag-free output differ from 5c6a0c5f?** Yes, on one route only, beyond the approved carve-out (F5).
- **Can document text leak into output?** No.
- **PR 150 (42a34aca)?** It changed only layer-one U5. The span walk and counting are untouched, and no UG3 guarantee is broken.

**Findings:**
- **R2-F1 (hardening), `src/gnd/model/_unattended.py:322-340`:** spans in `provenance.spans` on an operation or obligation are never U7-checked, re-hashed or counted. An unattended v2 model whose operation cites an undeclared document with a made-up excerpt digest gives exit 0 and no issues under `--require-documents --document ledger --document annex`. The flag's help promises "every source span". Fix: refuse such spans in unattended mode, or extend the walk and U7 to those locations.
- **R2-F2 (hardening), `src/gnd/commands/checking.py:96-117`:** with `source.mode: "unattended "` (trailing space), `--require-documents` with no documents exits 0. It prints only the near-miss U1 warning while all 10 spans are unchecked. Fix: escalate the near-miss to an error under the flag.
- **R2-F3 (hardening), `src/gnd/evolve/service.py:1520`:** a source-document proposal that changes nothing exits 70 with a raw BlastRadiusReport `min_length` error, even under `--policy additive`, so no `source_document.modify` cell is reported. Two routes: a no-op label modify, and delete then re-add of the last entry. The class predates UG3 (a no-op element modify also gives 70 on 5c6a0c5f). It contradicts spec B14 and the contract's "always non-empty" claim. Fix: raise an `EvolutionError` (exit 3) when the net change is empty.
- **R2-F4 (hardening, carried UG3-Q1, still live):** `gnd validate <redacted model> --format json --document /nonexistent.txt` exits 66 with a schema_version 9 payload that has no `redaction` key and fails `report.schema.json`. The close must dispose of it.
- **R2-F5 (completeness):** across 2240 validate runs over all 280 fixture models, runs without `--document` are identical to 5c6a0c5f. But 189 exit-3 `--document` refusals on 36 redacted or reference models without the mode now emit the projected report: an extra "REDACTION applied" line in text, the projected payload in JSON. Of the 114 differing JSON payloads, 108 were schema-invalid on the base and 0 are on head. It is review fix 1, so a correction, but it is outside UG-R1's carve-out and neither the release note nor record 004 mentions it.
- **R2-F6 (completeness):** a mutant that counts out-of-range spans as unchecked survives every test. The "supplied but not UTF-8" counting row has no count assertion.
- **R2-F7 (completeness):** mutants that drop the non-blank label check or the `before.sha256` check (`evolve/models.py:380-384`) survive every test. Both are currently masked by U1 and replay, which still exit 3.
- **R2-F8 (completeness):** the contract's "No operation reorders the list" is wrong: delete then add of the same digest moves the entry. It is explicit and flagged breaking, so not silent, and a mutant on that path survives every test. Fix: reword the sentence and add a test.
- **R2-F9 (informational):** duplicate digests in `source.documents` still pass U1 (UG3-Q2); the close should rule on it.

**No finding in these categories:** blocking; document-text leakage; constraint fall-through; v1/v2 leakage (proposals, records and previews checked); wrong exit band through substring matching (the locator digest is pattern-checked hex, and labels never appear in service messages).

The focused tests (span coverage, source document, unattended mode) pass: 131 tests.
