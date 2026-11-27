Claim C1 does not fully hold. On the Python API, `for_growth=True` will render a loaded model that was changed after loading and no longer validates. The CLI can never do that, so the two surfaces disagree, and the guidance says the view is the inventory of "the validated model". All 16 SHA-256 values match the brief.

## 1. Findings

**F1. The API's growth view renders a model that fails validation. The CLI cannot produce that output, and the guidance promises a validated model.** (`src/gnd/api.py:1029-1031`; the guidance is in `src/gnd/skills/gnd-model-from-text/references/unattended-growth.md`, at its "Current model in the growth prompt" section)
- **What's wrong:** when the caller passes a `Model` object, `verbalize_model(model, for_growth=True)` goes to `_resolve_model` (`checking_service.py:73-80`), which hands the object back unchanged. `render_growth_view` then renders it without validating it again. The CLI only takes paths, and paths always go through `load_model`, which validates.
- **Why it matters here:** the guidance says "Both supply the same complete inventory of the validated model", and the packaged README example takes this `Model` route. The repository already has a way to recheck a changed model: `api.validate` re-checks nested mutation.
- **Observed effect:** a host that edits a loaded model in memory gets a view of an invalid model. That view carries a SHA-256 the protocol treats as authoritative, so the agent can name role players that do not exist. The new test `test_public_growth_view_options_and_fact_metadata` edits a loaded model and renders it without validating, so it locks this behaviour in.
- **Reproduce** (I ran this):
  ```
  m = load_model('tests/fixtures/rmap/cases/17-objectification/model.yaml')
  m.fact_types[0]['roles'][0]['object_type'] = 'no_such_type'
  m.fact_types[0]['reading'] = 'totally unrelated'
  api.verbalize_model(m, for_growth=True)
  ```
  - It returns `{"id":"student_has_name","reading":"totally unrelated","roles":[["student","no_such_type"],...]}`.
  - `api.validate(m)` on the same object reports exit 3 with `semantic:role-ref`.
  - It should either refuse, or render only after validating again, as the path route does.
  - The default review mode has always skipped this check for `Model` input (the earlier `verbalize_model` already did). GC2 is the change that adds the "validated model" promise and the claim that the surfaces agree.

**F2. Two of the spec's acceptance checks are not run.** (`tests/test_growth_view.py:54-72`, `src/gnd/examples/seeded_growth/README.md`)
- **Direct reading match:** the spec asks to "Verify a direct reading match and ambiguous deferral."
  - The README only says in prose that searching for `has version` finds the fact by its reading. No search is run on that query.
  - Line 72 of the test checks for "has version" in the result of the *role-player* search, not a reading search.
- **Ambiguous deferral:** the example defers `W-1`, a substring of the occurrence it has just reused, with the reason "W-1 alone does not establish a relationship." That is not an ambiguous occurrence (one the agent can't resolve and so defers), so ambiguous deferral is never shown.
- **Consequence:** a regression in either path would pass the suite. This is a gap in test coverage, not a wrong output.

**Style (no observable consequence):**
- `VOCAB` at `tests/test_growth_view.py:17` is never used.
- The test pulls the README's code block out with `split("```python\n")`. It works on the committed README, which this project writes itself. It would break if an earlier Python block were added.
- The conditional call at `checking.py:395` could simply pass the keyword through.

## 2. What I checked and found true

- **The two surfaces agree on path input:**
  - CLI and API produced the same output for a model under a directory named `café/`, with `PYTHONIOENCODING=ascii` (SHA `b3be49…` both ways).
  - Redirecting stdout to a buffer-less `StringIO` falls back to `print` and still emits the same text.
  - A stale include gives `include:hash-mismatch` and exit 3 under the ascii encoding, with no view written.
  - A missing model gives exit 66.
  - Both surfaces refuse the same way when the path goes through the `/tmp` symlink (`include:unreadable`). That refusal comes from the existing include-safety rules, not from GC2.
- **The agent can check role direction:** placeholders bind to roles by position (`representation-format.md:276,283`). The view keeps the authored reading and the ordered `[role_name, object_type]` pairs.
- **The agent can change route, widen or defer:**
  - The view includes `subtypes`, the object-type `reference` field and `inverse_reading`.
  - The guidance tells the agent to retry with a synonym, look at a role player's facts, follow a subtype or reference, widen to the full inventory, and defer into `open_questions`.
  - It states that a missing shortlist entry is not evidence of novelty.
- **The README's spans follow the repository convention:** code points of the NFC-normalised text (`representation-format.md:756`), and the occurrence is checked to be unique.
- **Inputs:** `for_growth="yes"` raises `TypeError`, and output without the flag is unchanged.
- **Tests:** the four affected files pass (172 tests). `__all__` already included `verbalize_model`, so "twelve functions" is consistent. No other page cites the old count of eleven.
- **Standing check (code fitted to its examples):**
  - The README filters (`"edition" in reading.casefold()`, `player == "version"`) are illustrative host choices, not product code.
  - The CLI's `isinstance(…, bool)` check is complete for its input.
  - The README extraction in the test is the only structural split. It reads text the project writes itself, and I found no legal breaking input that matters.
  - No product regex or special-case branch was added.

## 3. What I could not check

- I did not build a wheel or install it into a fresh environment, though the spec requires it.
- I did not check the repository guard output, lint, or fixture byte sizes. These were outside a read-only review's time budget.
- I did not run the README example after a real round 1 has been applied.

VERDICT: CHANGES_REQUESTED
