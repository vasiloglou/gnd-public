# OS0 spec gate

**Delegated approval (auto=true), 2026-11-10.** The current request,
`gnd:process-milestone ossie-interchange auto`, delegates this ruling.
The approved artifact is `notes/phase-OS0-spec.md` r4, SHA-256
`47b62ba0eac4edb5772e4886b5b1a360343a6cfc9a5330e24e6f4cb4b1c5eefd`. This records the agent's ruling.

Scope includes the pinned OS0 measurements, scratch environments, evidence and
checkpoint, and the OS0 record and commits within the spec. D2 adopts in-tree
evidence retention. D1 preserves the owner's approval for both isolated
RelationalAI versions. The controls define the census, pointer accounting,
oracle liveness and version selection. The independent evidence review uses
one different tool as specified by the plan. No paid panel run is selected here.

Plan gate 001 approved the pre-tag r3 digest and describes the later status
edits. The committed post-tag digest is
`f9b2a9c9bc56da27a52bdae7e1b7c0903fd81cd2a4fff3299df2ee67c4080bae`.
The retained r2 panel evidence has the documented sanitization boundary.

| Phase | Hard prerequisites | State at this gate |
|---|---|---|
| OS0 | r3 plan and OS0 spec gate | ready for measurements |
| OS1 | OS0, explicit OD6 confirmation | pending |
| OS2, OS3, OS4 | OS1 | pending |
| OS5-draft | OS1 | pending |
| OS5 | OS1–OS4 | pending |
| OS6 | OS2 and OS4 | pending, separate upstream disposition |
| Close | OS5 and OS6 end state | pending, light-panel run requires go-ahead |

The archived approved spec is `evidence/OS0/spec-r4.md`.

**Delegated retention amendment (auto=true), 2026-11-10.** Retain the
measurement scripts as reproduction evidence under the scope described in
the amended spec. No oracle results were redefined. Amended spec SHA-256
`dba5082642309b65c5f8b07ae716f27c5037224a47bc2b2a8d778307380aa9c2`.
