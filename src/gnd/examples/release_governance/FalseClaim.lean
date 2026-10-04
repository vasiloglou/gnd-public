import Definitions

open GND
def pending : Population := { concrete with r2 := [0, 1, 3, 4] }

-- Deliberate failure: REL-103 is reviewed but absent from approved.
theorem every_reviewed_release_is_approved :
    pending.r1.all (fun r => pending.r2.contains r) = true := by decide
