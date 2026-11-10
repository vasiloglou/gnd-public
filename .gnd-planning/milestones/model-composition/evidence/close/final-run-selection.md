# Final candidate comparison selection — 2026-11-10, before execution

Authority: owner's explicit answer authorizing named baseline459ca8d2 and final candidate full default suite and model-composition compatibility census on beast-3. This is not inferred from auto. Candidate6de7189a47dfc11a385dd60de0f0ebb942dfa452 includes completed MC3 and repaired final MC4 source; phase confirmation/completion and merges remain separate.

Use the clean isolated beast-3 checkout prepared at9f3d22f7, fetch the repaired bundle, detach6de7189a, synchronize locked dev dependencies using uv0.10.10 and Python3.11. Remote baseline environment and prior corrected-candidate runtime use3.11.18; current remote environment matches3.11.18. Local phase gates use3.11.15 and are labelled separately. No env file or secret variables are read.

Run the existing tools/mc1_model_census.py producer over tracked ORM paths, then exactly:

    uv tool run --from uv==0.10.10 uv run pytest -q -s -m "evidence or census" tests/test_mc1_census.py --tb=short
    uv tool run --from uv==0.10.10 uv run pytest -q --tb=short

Producer writes per-observable JSON. Compare all400 frozen original members, with load/dump/dump_json/digests/identities/validate observations unchanged; no historical expected answers regenerated. Current inventory has423 members,23 additions; capture and explicitly disposition every new member rather than reducing the baseline or silently ignoring them. Existing dirty control distinguishes changed identity and missing originals. This tests the declared tracked-file census, not every possible model.

Full default expected failure-name set is exactly the six independently measured baseline failures: grow-a-model prose plus five RF5 source pins. Compare actual names and summaries; no xfail or baseline refresh. Native/external/excluded lanes retain default addopts and are not claimed executed. Capture each process exit independently, raw output with declared path sanitization, runtime/source identities and before/after status. A nonzero full suite is only accepted if exactly the baseline set remains; unexpected failures require reproduction/triage before close. These runs do not establish main-branch completion before merges, certify or publish anything.
