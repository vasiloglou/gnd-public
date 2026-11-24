# 13: Own table with two candidate keys, one preferred

**The model says.** A Room at a Slot is taught by a Lecturer. A room holds one lecture per slot, and a lecturer teaches once per slot; the second key is marked preferred.

**A Halpin reader expects.** One table, `room_slot_lecturer`. The preferred key is the primary key (slot and lecturer, in role order), and the other is a unique key. Test T3b removes `preferred` and swaps the declarations, and expects the same primary key from the role-position tie-break.
