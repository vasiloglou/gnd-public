# Final external gate — PR158

Owner explicitly approved only PR157c6dad88d and PR155396f86f3, already merged in order ed091709/a9b67d8b. The final PR158 fixed head must receive separate explicit owner merge authorization.

After that approval: verify actual head equals approved SHA, live reviews/threads are resolved, and base/current main state; SHA-guarded merge through GitHub. Fetch actual main. Assert every nonplanning tracked path/mode/blob equals measured b7da04b1 (all4698 paths), with only separately identified planning/evidence differences. No changed runtime byte inherits prior tests. If unexpected relevant differences appear, invalidate affected attribution and perform selected rechecks before completion.

Only after main equality succeeds, close issue95 as completed under the explicitly invoked milestone workflow. Retain the actual GitHub merge and issue-state events and report the measured main SHA; local close033 records pending external gates at its own snapshot, never a future event. PR158 merge event/issue95 state are authoritative post-record disposition evidence. This sequence requires no new product commit merely to restate a merge event. Do not publish, certify or start a successor milestone.
