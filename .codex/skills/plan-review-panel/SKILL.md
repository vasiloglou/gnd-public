---
name: plan-review-panel
description: Compatibility entry point for an explicitly selected advisory plan review using the maintained GND panel; no inherited vendor runner.
---

# Plan review compatibility route

This owned compatibility entry point replaces an excluded historical vendor
implementation. It does not preserve that implementation's fixed five-model
roster or shell interface. Select the maintained GND advisory plan-review route
explicitly: [gnd-review-panel](../../../src/gnd/skills/gnd-review-panel/SKILL.md).
That skill and installed CLI own roster, quorum, evidence, failure retention and
no-fix boundaries. This entry point invokes no sibling on your behalf.

During P1 the panel command is conditional on the source-pinned bootstrap in
`docs/development/bootstrap.md`; it is unavailable to an outsider without that
declared tool. A panel sends reviewed artifacts to providers and needs explicit
scope/recipient authorization. Never read or source a repository `.env`.
For a selected all-six run, the maintained launcher imports only named keys
from the parent environment or optional owner-only `~/.codex/.env` parsed as data.
No panel or credential check is required for ordinary scaffold development.
Missing names refuse before panel spending. One reviewer is not a panel;
retain every failure/dissent and never turn advisory review into an owner gate.
