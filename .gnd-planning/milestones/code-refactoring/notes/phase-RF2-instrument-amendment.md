# RF2 instrument amendment — awaiting owner review

2026-10-05. This proposal changes no production behavior and regenerates no
RF1 golden. It is required before the RF2 move commit: G1 is currently red
(6 failed, 389 passed, 16 xfailed), while G3, G4 and G5 exit 0. Approval of the
original RF2 spec did not authorize a support-module repair (D10).

## Reproduced contradictions

1. `test_cli_exit_map` captures every EXIT_* attribute of gnd.exits. Moving the
   existing CLI allocations into exits adds existing names to that namespace.
   The observable command exits are unchanged, but the layout observation differs.
   The unamended whole-namespace pin cannot stay identical while meeting the
   approved centralization requirement. Its recorded behavior claim needs a
   layout adaptation, not new expected exit values.
2. `test_mutation_table_rows_of_their_own` requires every mutation snippet to
   occur at its old source location. The move deletes those definitions by
   design. Mutation stimuli must be retargeted to the shared definitions and
   renamed functions, retaining every row id and expected failing node.
3. Four v1/v2 fresh/resume session answers contain literal authenticated execution
   identities. `_mint_execution` hashes production_roster_digest as part of its
   full identity input. Changing any src/gnd source therefore changes these
   identifiers, even though top-level production identities are normalized by
   RF1 rule N9. Scratch v1 observation against the correct py314 golden differs
   only in the two process_receipt.execution.identity fields. This is a missing
   transitive normalization, not evidence of a verdict change.

## Proposed amendment

- Preserve all original RF1 golden files, goldens.sha256, ids and expected exit,
  verdict, ordering, message and refusal meanings unchanged.
- Adapt the CLI observation to pin the **old exposed name set** in each original
  namespace, and add a separate RF2 assertion over the complete current allocation
  union, with every constant defined once in exits and all old imports preserved.
  Negative controls change a constant and introduce an unallocated extra name;
  both must fail. Do not silently exclude newly invented allocations.
- Retarget affected mutation-table source paths and snippets to the actual new
  definition. Keep ids and expect_red sets; run all changed rows and require
  call-phase failures. Preserve recorded original mutation table by its RF1
  commit/digest; bind the updated instrument separately in the RF2 record.
- Add a **verified** transitive normalization for authenticated execution identity.
  Capture the complete input of the mint's canonical encoder in the session test
  harness; independently recompute its digest and reject a mismatch. Normalize
  only the production_roster_digest component, after checking that it equals the
  actual current production identity. Compare the remaining mint-input semantics
  with separately retained baseline input. Bind each occurrence by attempt/path;
  never wildcard-erase every 64-hex value or accept unmatched digests.
- Because original literal identity answers cannot compare directly to a stable
  placeholder, retain them untouched and create an explicitly labelled RF2
  successor observation for the four affected session cases. Generate its expected
  representation from a source-base run, not from moved code. Record the historical
  answer and its successor together; the owner approves this normalization meaning
  here, and every source-dependent field being transformed is listed by path.
- If tests/support/rf1_pins.py needs editing, discharge RF1-OQ7 in the same repair:
  unify token replacement with consistent escaping and bind declared input bytes
  or a pinned semantic projection. Prove hostile escaped-path and changed-input
  controls red before fixing them. If the normalization can stay in a separate
  RF2 session support file, leave RF1-OQ7 with its original owner and explicitly
  record why that support module was not edited.

## Gates and limits

G1 remains a prerequisite to any move commit. The four successor session cases
also run on the original production source in an isolated temporary checkout.
Negative controls must detect changed identity input semantics, bad digest, stale
production roster, wrong occurrence binding and changed declared-input bytes.
The full selected G1–G5 and direct RF2 controls then run on current bytes.
If the existing approved ceilings are exceeded, return the measured budget to
owner; this amendment grants no budget extension, broad replay or certification.

This proposes an explicit amendment to SM1's **instrument**, not permission to
change a production exit, verdict, encoder or digest algorithm. The original
RF1 artifact's boundary remains historical. The completion record must distinguish
original byte preservation from this bounded successor claim.

## Independent-review prerequisite (separate authorization)

Automatic approval review rejected the Codex CLI reviewer command because it
would send the prompt and implicitly inspected repository source/diff to the
Codex provider without explicit destination-specific authorization. No reviewer
was launched and no workaround was attempted. This requires separate owner
permission; instrument-amendment approval alone does not grant it.

## Review authorization update

On 2026-10-05 the owner explicitly authorized the named Codex provider review.
The reviewer has now been launched. The separate instrument amendment above
remains awaiting owner approval.

## Clarification from independent review (still proposed)

The four existing nodes test_session_fresh[1], test_session_fresh[2],
test_session_resume[1] and test_session_resume[2] will explicitly route
their observations through a new RF2-only assertion helper. Other versions
continue to call the existing assert_golden unchanged. The successor helper
will verify the retained original golden SHA-256, authenticate the captured
mint inputs and field/path bindings, apply only the declared producer-component
normalization, then compare the entire remaining observation to the source-base
successor. No blanket skip or xfail replaces these four G1 nodes. The original
RF1 support module need not be edited; RF1-OQ7 remains with its original owner.

Current-byte diagnostic capture of all four cases is now available in
evidence/RF2-session-structured-diff.json. Capture went only to a temporary
directory, never to the approved golden tree. This is diagnostic evidence,
not a green preservation gate or proof of the proposed normalization.

## Owner approval

2026-10-05: owner answered “approved” for this instrument amendment,
including the independent-review clarification. Approved artifact SHA-256:
5edfe0ed33c8a133eb9cb92ecdcfa25bf54bc221ea17f2a39b7dab9cc3bd4138. Explicit implementation go-ahead; auto=false.
