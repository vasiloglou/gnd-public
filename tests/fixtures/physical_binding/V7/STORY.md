# V7: a unique key derived from the model

**Model.** 13 again.

**Binding.** V5's, without the `unique_keys` member.

**Semantic model.** The dataset gains the unique key (`room_no`, `slot_cd`).
The binding did not list its unique keys, so each of the model's confirmed
uniqueness rules whose roles all sit in this table, and that is not the
primary key, becomes one.

**Extension.** The room-and-slot rule is now carried as that unique key,
where V5 listed it as `not-in-binding`.
