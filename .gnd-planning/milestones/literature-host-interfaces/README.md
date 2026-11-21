# Literature host interfaces

Outline r1, 2026-11-21, from [issue #216](https://github.com/vasiloglou/gnd-public/issues/216)
and [issue #215](https://github.com/vasiloglou/gnd-public/issues/215).
Not reviewed and not approved.

| Phase | Deliverable |
|---|---|
| LH1 | A public producer protocol for the literature reading example over a caller corpus and vocabulary, with the caps as parameters and a per-document stop rule |
| LH2 | `replay()` of a live run from its own folder, with zero producer calls |
| LH3 | Model-generic assertion admission: caller-named assertion entity, its own identity, optional roles, every attached fact kept |
| LH4 | Admission policy as data, a distinct disposition for a policy failure, and `MAX_TARGETS` as a parameter |

[Plan outline](notes/literature-host-interfaces-plan.md). Third in the
[roadmap after 0.4.0](../../PROJECT.md#roadmap-after-040--planned-2026-11-21):
the reporter has working workarounds for both issues.
