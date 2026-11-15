# LI2 unscored-label correction

The approved LI2 test in corpus commit `3ef46384`,
`tests/test_li1_assurance_report.py::test_dormant_stages`, expects
`{"chains", "reuse_cases", "identity_pairs", "name_pairs"}` in the reference
report's unscored labels. LI2 spec D8 and §6.7 activate scoring for
`identity_pairs`. The harness README defines this field as label groups
the report did not score.

Keep the prior assertion in the corpus commit. Replace it in the current
test with `{"chains", "reuse_cases", "name_pairs"}`. Omit the
`identity_pairs` entry exactly when the stage has a precision observation.
A missing or refused route still lists the unscored pair count.
The case exits, statuses, numerators and denominators in the approved
`*.expected.json` files and the resolution case messages stay as approved.

An implementation can use the same stage payload to decide both field
presence and unscored label reporting. The reference report witnesses the
scored branch. A run with a refused composition witnesses the other branch.
