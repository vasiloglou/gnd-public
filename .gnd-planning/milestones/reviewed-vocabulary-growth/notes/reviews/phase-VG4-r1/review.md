<!-- Edited by review_tool.py sanitize: 2 absolute path(s) replaced with <repo> or <home>. The reviewer's words are otherwise unchanged; run.json holds the SHA-256 of the original. -->
The working-tree phase spec does not match the brief: expected SHA-256 `05022d34…6043d90`, observed `681a95ff…39d4f`. The spec at `HEAD` matches the expected hash; the working copy appends implementation notes. All other listed hashes match.

1. **F1 — P2: `documents: null` passes validation but cannot receive its first document.**  
   At [_unattended.py:118](<repo>/src/gnd/model/_unattended.py:118), `documents is None` conflates an absent key with an explicitly null value. Evolution distinguishes them at [service.py:1011](<repo>/src/gnd/evolve/service.py:1011).

   **Reproduction:** Take the seeded, otherwise empty root from `vg3_cases`, set `source.documents` to `null`, and validate: exit **0**. Propose a `source-document` add with a candidate containing the document list: preview raises `EvolutionError: …the model declares no source.documents to append to`, under both policy settings.

   I reproduced this through CLI validation and service preview using in-memory file reads. The exemption should distinguish an absent key from a present, non-list value and retain U1 for null.

2. **Checked and found true**
   - Absent-key and empty-list roots both support first-document previews adding owned elements and an attached constraint; candidates validate without policy issues.
   - Owned elements, attachments and the tested other sections retain U1.
   - Unattended re-pins are refused before policy evaluation under both supported settings. Mode-free controls retain their previous behavior.
   - Eleven ownership probes refused modifications, renames and deletions across included objects, facts, roles and constraints.
   - Nine selected read-only pytest cases passed; all 21 existing unattended-rule branch probes passed.
   - Added production code reads parsed structures and introduces no regex, split or slice.

3. **Could not check**
   
   Apply, finalize and the complete integration suite require filesystem writes, which the brief forbids. Their end-to-end success remains unverified.

VERDICT: CHANGES_REQUESTED