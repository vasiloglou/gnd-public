# Close reading one — completion predicates 1-3

Date: 2026-10-13. Instrument: owner-selected independent local reader (read-only), one of four close readers; condensed by the orchestrator with findings, verdicts and cited lines preserved. Subject: HEAD cd80edd.

| # | Verdict | Evidence |
|---|---|---|
| 1 Local public PyRel/DuckDB, no credentials/checkout | MET WITH RESIDUAL | 013 gates; e-receipt.json runtime 1.30.1/1.5.5, gnd_absent, installed origin; harness env allowlist :97-98, origin refusal :23-25; applications.py:97-100 child env; pins pyrel_runtime.py:1724,1787 |
| 2 Every rule satisfied + discriminating control | MET | e-native-corpus.json 137/137; per model/rule {satisfied, violated}, deontic {satisfied, warning}; counts baseline 5, strict 5, complete 6+2 derivations, expense 20, currency 23; applications.py:52-87 |
| 3 Publish only after selected PyRel gate | MET | applications.py:146-176, :29-89, :251-253, :295-297; tests bookrec :68-99, :104-134, publication :235-251, expense :81-232; warning stays warning (bookrec :53; 07-native.md:112-119) |

Findings (none blocking):
1. Note: Field imported via relationalai.semantics.frontend.base (pyrel_runtime.py:197,251,301,1493,1552,1666); the symbol is public (re-exported in relationalai.semantics, __all__), only the path is internal. Repair: import from relationalai.semantics; record digest change.
2. Residual: receipt omits wheel build inputs and approval.json (013 open question).
3. Note: docs/overrides/zensical/corpus fixtures come from the checkout (harness :121,:125); application inputs from the wheel (:113,:116). State the split.
4. Note: BookRec CLI defaults to --backend gnd; "selected PyRel gate" applies under --backend pyrel.
5. Note: seam names differ from A2 D1's "e.g." names; pinned public set is authoritative.
