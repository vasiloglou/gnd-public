# OS3 identity report amendment

Delegated approval (auto=true), 2026-11-10, under the named milestone
invocation. The [approved OS3 spec](013-OS3-spec-gate.md) remains the
basis for admission order and reconstruction. The
[independent review](notes/phase-OS3-claude-review.md) found that a
missing report or an impossible refused pointer could hide an identity
mismatch. An impossible refused pointer is now a report refusal.

Decision D1 still permits an absent source report, including a custom
report location. The import result always compares identities when a
sidecar supplies one. Its additive `source_identity_verified` field
makes the outcome explicit. A mismatched identity with a present
lossless report refuses. A sidecar is bound to ontology bytes, and the
source identity is a comparison value. Neither is a digital signature.
The addendum stays within the offline import and report scope. The
independent review already exercised the candidate and the focused
regressions witness each reproduced repair.
