# Close metadata repair gate — 2026-11-10

Delegated approval (auto=true), authority named model-composition milestone,
before the edits below. This is a mandatory close-discovered reference-fidelity
repair, not a new runtime feature or a retroactive phase-review opinion.

The current-checkout reference check first fails on an unrelated untracked nested
worktree. The exact existing check rerun in an isolated tracked archive of8efd3409
then fails on retained notes/phase-MC4-fable-draft.md and its relative expense SVG
link. The draft's original intended home is docs/tutorials/shared-expense-policies.md.
Its immutable raw SHA256 is4a3cdd3d4cb802fc91eaa7ebb75ef3f9374c5391eae5a747483eb789b3b05ea7.
The draft also contains exactly one proposed, never-shipped placeholder target,
../reference/model-includes.md; final implemented pages instead cite the canonical
representation-format includes section. Preserve Fable's verbatim draft.

Reuse tests/test_development_scaffold.py's existing exact
RETAINED_DOCUMENT_ORIGINS mapping for that draft/hash/intended home, and its exact
RETAINED_EXTERNAL_REFERENCES table for only this draft's one historical placeholder.
All real targets remain checked, the entire retained draft is hash-pinned, and no
other document/target is exempt. Existing parametrized none/changed-snapshot/
missing-target origin controls automatically exercise this new mapping. Run those
three cases plus reference closure/twins and the existing bounded external-reference
controls. Expect0 after repair; the isolated original test is observed red first.
No new helper, production code, schema, semantic exit or fixture model changes.

Estimate at most six added test/support Python lines, taking MC4-attributable
support from114 to at most120, its existing stop. Count immediately; stop before
any further edit if exceeded. Existing phase reviews remain bound to9f3d22f7/6de7189a;
the separate already-declared close reviewer will inspect this patch. No third
phase review is invented and no close review invoked before its prerequisites.

The in-flight full suite at6de7189a is invalidated and was explicitly stopped
through its exact remote process tree, leaving unrelated jobs untouched. It is
an incomplete historical run, not a full result or a compatibility success.
Restart the named final default/census at the corrected concrete candidate after
focused metadata controls pass, so final acceptance uses actual corrected bytes.
Keep PR155's pending fixed head unchanged; this bounded repair belongs to draft
close PR158, and disclose it in PR155's status. No merge or issue closure occurs.
