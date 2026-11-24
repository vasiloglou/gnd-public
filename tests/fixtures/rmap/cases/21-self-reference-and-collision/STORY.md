# 21: Self-referencing binary and a column-name collision (S10)

**The model says.** Each Person reports to at most one manager Person. A second fact type gives a Person a ManagerRef whose role is literally named `manager_person_id`.

**A Halpin reader expects.** Both facts go into `person`. The ManagerRef fact type sorts first and takes the name `manager_person_id`. The reporting line would also be `manager_person_id`, so it becomes `manager_person_id_2`, a foreign key back to `person` itself.
