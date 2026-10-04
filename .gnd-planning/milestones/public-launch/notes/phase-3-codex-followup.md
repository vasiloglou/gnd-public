# Phase 3 bounded Codex follow-up

External Codex CLI, gpt-6-astra, xhigh, read-only. Final response retained below;
absolute operator-local citation links changed to repository-relative code citations.
One reviewer is one reviewer; this is a second pass by the same reviewer.

- **Severity: medium · MVP class: blocking — Newly selected console-script test uses the ambient installation.** At `tests/test_release_acceptance.py:206`, selecting all of `test_packaged_skills.py` also selects `test_console_script_reports_the_single_sourced_version` (`tests/test_packaged_skills.py:113`). That test resolves `gnd` through `shutil.which()`, but the acceptance environment inherits the parent `PATH` without prepending the retained installation’s `bin` directory. Invoking that environment’s Python by absolute path does not change `PATH`. Consequently, a clean host without ambient `gnd` produces a skip that the gate rejects; an ambient `gnd` can instead exercise another installation, potentially encountering the macOS source-access denial. Prepend the tested environment’s executable directory to the subprocess `PATH`, or select only the intended packaged-resource checks.

Inspection was limited to `bb14d1877d6bc2ec4b81c6303640dd1bb0ea2cfc..31a987400a35d8429c7f50401db9ae1580c1708e`, the prior review/disposition, and relevant definitions in the three named test files. I checked the pinned resource-set comparison, both installation parameters, collection-skip capture, and the two regression controls. I did not run tests, installations, or hosted gates, or independently verify the reported passes. This review makes no phase-completion claim.
