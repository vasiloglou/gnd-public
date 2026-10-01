# Separate proposed answer key — not run evidence

| ID | Required observation |
|---|---|
| C0 | validate/check CLI exit 0; API band 0; clean semantic decision accept |
| C1 | check CLI exit 1; API band 1; semantic decision refuse; value violation present |
| C2 | check CLI exit 2; API band 2; semantic decision indeterminate; vacuous verdict present |
| C3 | validate CLI exit 3; semantic cross-reference refusal, no traceback |
| C4 | check CLI exit 4; API band 4; semantic decision indeterminate; textual unchecked verdict preserves expression |
| C5 | check CLI exit 1; API band 1; fail takes precedence over unchecked |
| C6 | usage exit 64; no traceback |
| C7 | reader available=false, reason=unavailable-or-invalid-evidence; level none, all five assurance digests null, assumptions []; semantic band unchanged |
| C8 | accepting control available=true with zero covered_scope_ids; stale roster direct _load rejects; public loader unavailable; API report changes only assurance projection |
| C9 | accepting control available=true; direct _load rejects with stale runtime identity; public loader unavailable; no positive coverage |
| C10 | accepting control available=true; direct _load rejects with stale release manifest; public loader unavailable; no positive coverage |
| C11 | artifact audit exit 1, naming missing path; unmodified artifact audit exit 0 |
| C12 | contaminated control resolves checkout; scrubbed installed probe exit 0 and resolves wheel environment outside both checkouts; a failed control is failure, never a skip |
| C13 | each scratch mutant audit exit 1; actual manifest audit exit 0 |
| C14 | each scratch mutant check exit 1; actual discovery/twin check exit 0 |

For check reports CLI JSON and API payload must agree for identical inputs.
Source/target comparison uses the same fixture paths and normalization only for
explicit absolute input coordinates and assurance projection. Full semantic
payload must otherwise agree; never remove diagnostics to manufacture parity.
Unavailable projection follows src/gnd/assurance.py, not a second implementation.
C8 uses a fresh test-only package copy and resets reader cache at test boundaries;
it proves an accepting control before adding an unlisted module. No synthetic
bundle is copied into the distribution or claimed as installed certification.
