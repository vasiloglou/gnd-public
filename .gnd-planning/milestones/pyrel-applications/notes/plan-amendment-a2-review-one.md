# Amendment A2 review one — implementability

Date: 2026-10-13
Instrument: owner-selected independent local reviewer (read-only)
Subject: `notes/plan-amendment-a2.md`, SHA-256 `555a0e76ed41364bb05c9db34897727c85a556640171de01e363b07b6589c3d1`

**Verdict: pass with findings** (none blocking; 1–3 should be repaired before the PA5R spec).

Premises verified: the query runs isolated (src/gnd/export/applications.py:183); the runtime is
concatenated into the emitted program (src/gnd/export/emit.py:31-34); the packaged
runtime-environment matches tutorials/runtimes byte for byte and is already gated
(tests/test_external_runtime_tutorials.py:110, tools/accept_pyrel_applications_install.py:35,115).

1. D1 surface too small: BookRec also uses `_profile_derivations`, prepares coverage before
   admission (native_query.py:23-39), reads `oracle.computed`; Expense reads `index.fact_types`;
   both must emit binding digests (applications.py:192-193). Add derivation order/computed facts,
   fact-type membership, envelope/refuse helpers and pre-admission computed coverage (or move it into the seam).
2. D3 `python …` resolves to the PyRel interpreter in pyrel-lane shell blocks (run_tutorials.py:88,113-115);
   blocks run under `bash -euo pipefail` with one expect. Fix the visible convention; one checked command per block.
3. D3 needs a new marker grammar (run_tutorials.py:17,24 only hash stdout at :125); name normalized tokens
   (run temp dir, native/checker temp prefixes, elapsed); keep count invariant and receipt fields.
4. BookRec bad proposal must be a shipped candidate file/flag, not native proposer output (native_query.py:79).
5. Layer-map coverage is a no-op; no emitted-program golden exists. Pin the seam's public name set via runpy
   in the PyRel lane, and test the private names still resolve.
6. D2 conflicts with chapter 2's `cli/` layout (expense/extension.py:12, docs/expense/02-application.md:25,41-44,
   tests/test_public_generated_examples.py:41). Continue in chapter 2's project or make the import layout-independent;
   name the lower-cap file.
7. Editorial: mark O3's retained option text superseded.

D5: pointing to the existing copy avoids a third byte-gated twin; setup runs outside the runner (needs uv/network).
