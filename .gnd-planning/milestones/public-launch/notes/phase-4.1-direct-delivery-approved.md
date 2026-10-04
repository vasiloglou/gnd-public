# Owner authorization — temporary PR and CI requirement removal

On 2026-10-04 the owner explicitly authorized temporary disabling of PR and CI
requirements: “but I am an admin, can we disable PRs for the moment and CI
requirements”. This clears the prior automatic-review authorization blocker.

Selected scope: temporarily disable the main-only CI ruleset and its required
PR-review gate, push the completed documentation directly to main, then restore
both exact original configurations. Other branch protections remain in place.
No force push, account billing change, cloud pass, certification or Phase 5
publication is included. The superseded draft PR will be closed after delivery.
