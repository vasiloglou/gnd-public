# OS2 pre-implementation corpus candidate

Date 2026-11-10. Base `2a30ebe3`, the reviewed OS1 result. The
[draft spec](notes/phase-OS2-spec.md) proposes exact formula shapes and the
[corpus](evidence/OS2/corpus-r1/README.md) holds a model, explicit populations,
expected formula scopes, and hand-derived verdicts.

The corpus replay exited 0 with `20 hand-authored verdicts matched the GND
checker.` Each of nine constraint families and one structured derivation
has a satisfying and violating case. The expected values were authored
before the replay. The fixture's population envelope was corrected to use
GND's required `population` header. The verdict table remained the same.

The required independent semantic review and separately selected parser
gate remain pending. Those gates may narrow or repair formula shapes. The
approved corpus will be digest-bound before the renderer starts.

The [early OS5 checkpoint](notes/OS5-draft-checkpoint.md) records the refunds
and growth walkthrough. Both commands exited 0 against the reviewed
exporter. Refunds has 59 native and 45 extension pointers. Growth has
48 native, 30 extension and seven refused population pointers.
