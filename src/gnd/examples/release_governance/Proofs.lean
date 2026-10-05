import Definitions

namespace ReleaseProof
open GND

-- This relates the generated Outcome-based predicate to ordinary list inclusion.
theorem holds_subset (xs ys : List T0) :
    holds (if xs.isEmpty then .satisfied else
      if xs.all (fun r => ys.contains r) then .satisfied else .violated) = true ↔
    xs.all (fun r => ys.contains r) = true := by
  cases xs with
  | nil => simp [holds]
  | cons a xs =>
    cases (a :: xs).all (fun r => ys.contains r) <;> simp [holds]

theorem subset_trans (xs ys zs : List T0)
    (hxy : xs.all (fun r => ys.contains r) = true)
    (hyz : ys.all (fun r => zs.contains r) = true) :
    xs.all (fun r => zs.contains r) = true := by
  apply List.all_eq_true.mpr
  intro r hr
  have hmem : r ∈ ys := by simpa using List.all_eq_true.mp hxy r hr
  exact List.all_eq_true.mp hyz r hmem

theorem candidate_valid : concreteWitness := by
  unfold concreteWitness
  decide

theorem policy_satisfiable : satisfiability := by
  exact ⟨concrete, candidate_valid⟩

-- c2 is approved ⊆ requested. without2 contains c0 and c1 only.
theorem approval_requested_redundant : redundant2 := by
  intro p _ h
  have both : holds (c0 p) = true ∧ holds (c1 p) = true := by
    simpa [without2] using h
  have approved_reviewed := (holds_subset p.r2 p.r1).mp both.1
  have reviewed_requested := (holds_subset p.r1 p.r0).mp both.2
  exact (holds_subset p.r2 p.r0).mpr
    (subset_trans p.r2 p.r1 p.r0 approved_reviewed reviewed_requested)

-- Carrier ordinal 2 maps to REL-103 in source-map.json. It is pending.
def pending : Population := { concrete with r2 := [0, 1, 3, 4] }

def reviewedImpliesApproved : Prop :=
  ∀ p : Population, wellTyped p = true → hard p = true →
    p.r1.all (fun r => p.r2.contains r) = true

theorem reviewed_does_not_imply_approved : ¬ reviewedImpliesApproved := by
  intro claim
  have falseConclusion : pending.r1.all (fun r => pending.r2.contains r) ≠ true := by decide
  exact falseConclusion (claim pending (by decide) (by decide))

#print axioms candidate_valid
#print axioms policy_satisfiable
#print axioms approval_requested_redundant
#print axioms reviewed_does_not_imply_approved

end ReleaseProof
