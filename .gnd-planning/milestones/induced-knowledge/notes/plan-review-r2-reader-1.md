# Confirmation reader 1 — semantics and admission safety

Plan r2 SHA-256 `d1a40a89…7c85` and IK1 spec r2 SHA-256 `4f4cb8b5…cac1` — both match.

**Verdict: approve-with-fixes.** Most round-1 blockers are repaired; one
r2-introduced blocking defect (C1-F1, IK5 polarity mapping) is a text repair that
does not reopen D8.

## Round-1 blocking findings

| Finding | Status | Citations |
|---|---|---|
| R1-F1 derivation rules bypass D-12 | resolved | plan 67–68, 90, 338, 403 (D8); `guarded` is top-level so `_constraints()` sees it (service.py:203–209); deontic violation → `warning`, not `fail` (representation-format.md:563–568) |
| R1-F2 / R4-F1 exit 0 ≠ holds | resolved | plan 56–58, 233–235, 329 (per-ref `pass`, support > 0, vacuous never emitted, seeded wrong-discoverer test), 391 |
| R1-F3 entailment suppression | partially resolved | closed modality-blind catalogue named and fixed in spec before code (236–245, 333); candidate-vs-candidate redundancy open (C1-F4) |
| R1-F5 / R4-F2 IK3 truth table | resolved | two modes (204–226; D10 at 481); class mode keeps `no-subjects` with GND (222); vacuous/unchecked separate (218–219); IK5 now guarded, so `derivation:` ref refusal (truth.py:88–97) no longer blocks scoring |
| R1-F6 ILP faithfulness | partially resolved | fragment table, set comparison, "necessary not sufficient" present (259–272, 339); polarity mapping ill-formed (C1-F1); vacuous handling undefined (C1-F2) |

## New findings

- **C1-F1** (blocking, high; r2-introduced: yes). Plan 261–266 maps a "wrong"
  clause to a guarded constraint with antecedent = body and consequent = "the
  negated head". The head `wrong(P)` is a host label, not a model fact type, and
  the guarded grammar has no false consequent — only `atom`/`comparison`/`absence`/`exists`
  (representation-format.md:495–500); antecedents are positive atoms only
  (495–496), so the listed NAF and aggregates (265–266) are inexpressible. IK5-C2
  cannot emit a well-formed constraint for any clause. Reproduce: try
  `wrong(P) :- a(P,V), V>10` with consequent "not wrong(P)" — it needs a
  non-existent fact type. Fix: body rewriting — move one body literal into the
  consequent (negate a comparison: `V>10` → `V<=10`; an atom → `absence`),
  restrict the fragment to positive-atom bodies, refuse NAF/aggregates by name.
- **C1-F2** (hardening, medium; r2-introduced: yes). Plan 267–269 counts vacuous
  "explicitly" but does not say whether vacuous = covered or not covered; a guarded
  constraint is `vacuous` whenever any antecedent fact type is empty in an example
  (representation-format.md:533–534). IK5-C3's refusal depends on an unstated
  choice. Fix the rule (vacuous = not-covered and reported separately, or refuse).
- **C1-F3** (hardening, medium; r2-introduced: yes). D9 (197–201) admits
  `induced`+`confirmed` whenever `reviewed_in` is present, which is any non-empty
  string (orm-meta.schema.json:905–907). The cited "imported precedent" is not an
  admission precedent: `_enforce_d12` refuses `imported` outright
  (service.py:251–255). One proposal — including IK4/IK5 output — could create an
  induced constraint already confirmed (and alethic) by a self-asserted string,
  short of the plan's "recorded owner review" (26–27, 46, 90). Fix: allow only a
  status change on an existing `proposed` induced constraint; forbid `reviewed_in`
  in discover/import output, with a test.
- **C1-F4** (hardening, low; r2-introduced: yes). The catalogue (236–245)
  suppresses only against declared constraints; redundancy among candidates
  (equality with its two subsets, uniqueness with frequency `[1,1]`) is
  unaddressed, and whether "min 1 alone" excludes `[1,1]` is ambiguous. Emitted
  sets and IK4-C5 counts depend on unstated choices.
- **C1-F5** (hardening, low; r2-introduced: yes). Under D11 the description
  renders into the extraction vocabulary but `vocabulary_digest` excludes it
  (anchors.py:193–200, 222): an extraction sidecar still binds after the
  description text the extractor read changes. The ruling stands; state that the
  digest no longer identifies the rendered vocabulary text and pin it with a test.

Counts: 5 new findings, all r2-introduced (1 blocking, 4 hardening).

## Limits

Static reading of `b554f3f`; nothing executed; overlap with reader 4 limited to
R4-F1/R4-F2; IK1 checked only for admission/semantic effects (clean except
C1-F5); Popper clause format unchecked; no files written.
