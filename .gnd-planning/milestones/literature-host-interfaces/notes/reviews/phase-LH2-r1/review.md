<!-- Edited by review_tool.py sanitize: 3 absolute path(s) replaced with <repo> or <home>. The reviewer's words are otherwise unchanged; run.json holds the SHA-256 of the original. -->
All twelve SHA-256 values match the brief.

1. **F1 — Valid live receipts can become unreplayable.** [reading.py:364](<repo>/src/gnd/examples/literature/reading.py:364)

   Replay applies `response_bytes` to the enriched receipt, including two hashes. Run-time validation applies that cap before adding those hashes.

   **Reproduce:** Enable review, set `response_bytes=512`, and return a supported receipt whose serialized `decision` and `basis` occupy exactly 512 bytes. The run’s receipt handling accepts it and retains 678 bytes; replay rejects it with `ExampleError: invalid saved reviews`.

   Confirmed with an in-memory probe using real caller inputs and receipt processing. This breaks the completed-run round trip promised by C3.

2. **F2 — Malformed manifest settings reach artifact reads.** [reading.py:904](<repo>/src/gnd/examples/literature/reading.py:904)

   The initial validation omits top-level `budget_bytes` and `scenario`. Their validation happens later in `_evaluate`, after retained files and caller inputs have been read.

   **Reproduce:** Change a caller manifest’s `budget_bytes` to `true`, retaining otherwise valid settings and roster. Instrument `_read_run_file`: replay requests `stage-0.json` before rejecting the invalid budget.

   Confirmed through public `replay()` with in-memory readers. This violates C4’s validation order.

3. **F3 — Malformed retained payloads leak `KeyError`.** [reading.py:842](<repo>/src/gnd/examples/literature/reading.py:842)

   The retained reader indexes `payload["attempts"]` and its rows without validating their shape.

   **Reproduce:** Replace `payload-1.json` with `{}`, update its digest, recompute the stage chain, and update the manifest. Replay raises `KeyError: 'attempts'`, rather than `ExampleError` or `ArtifactError`.

   Confirmed through public `replay()` with digest-consistent in-memory artifacts. This violates C1’s refusal contract.

What I checked and found true:

- All 56 tested invalid limit values refused with `ExampleError`.
- All 16 step combinations produced the expected optional-file roster.
- The caller reader used the recorded cap for all 16 required artifacts and checked all six stages before payload reads.
- A single artifact-byte mutation refused; matching and mismatching expected digests behaved correctly.
- The three retained packaged fixtures passed stage-chain, artifact-hash, retained-response and input-pin checks.
- Static inspection found no producer/reviewer invocation on replay and no added regex, split, or slice used to parse structured text.

I could not run the full pytest or tutorial lanes, including complete packaged replay: they create temporary files, contrary to the brief’s read-only rule. The probes created no files; F1 exercised receipt processing and input reconstruction, not a complete run through public routes.

VERDICT: CHANGES_REQUESTED