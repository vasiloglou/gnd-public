# Requirements — fixture project

A stand-in for a GSD `.planning/REQUIREMENTS.md`. Five ids, in the checkbox
grammar `verify_migration.py` reads (D3): three closed, two open. The mix is
deliberate — A4 forbids `history` on an unclosed id, so the corpus needs at
least one of each to have a case that can fail it.

## Core

- [x] **CORE-01**: Every event carries exactly one kind, fixed at the moment it is raised.
- [x] **CORE-02**: Every event names the actor that raised it, and never more than one.
- [x] **CORE-03**: Recording an event changes nothing but that event's own facts.

## Deferred

- [ ] **CORE-04**: Events can be amended after the fact — deferred, no evidence anyone needs it.
- [ ] **CORE-05**: Cross-project event search — deferred until more than one project exists.

## Notes

Case c03 anchors on a short paraphrase of CORE-01 that this file deliberately
does not contain. The paraphrase is not written here even in quotation --
a byte-exact substring search would find a quoted denial just as happily as an
assertion, which is exactly the mistake the first draft of this file made and a
four-seat review panel caught.
