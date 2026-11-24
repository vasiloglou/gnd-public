# V5: a declared unique key

**Model.** 13: a Room at a Slot is taught by a Lecturer. Two rules hold: a
room and slot have one lecturer, and a slot and lecturer have one room.

**Binding.** One table, `timetable`, with primary key (`slot_cd`,
`staff_no`) and a declared unique key (`room_no`, `staff_no`). No column is
marked as an identifier, so no object type has a home table.

**Semantic model.** The dataset carries the caller's keys as given. The
declared unique key is one the model does not state; it is kept, because
the binding describes the delivered table.

**Mapping.** No object mappings. One link tree of three levels, one per
role: the Room, then the Slot, then the Lecturer, which names the
relationship.

**Extension.**
- The slot-and-lecturer rule is the table's primary key.
- The room-and-slot rule is **`not-in-binding`**: the model has it, the
  delivered table does not declare it, and since the binding lists its
  unique keys nothing is added.
