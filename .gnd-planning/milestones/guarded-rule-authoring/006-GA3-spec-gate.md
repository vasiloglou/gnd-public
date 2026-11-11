---
milestone: guarded-rule-authoring
station: GA3-spec-gate
skill: "n/a -- repository development under process-milestone auto=true"
scope: GA3
date: 2026-11-11
gate:
  command: "review GA3 spec against approved plan and completed GA2"
  exit: 0
  output: "GA3 delegated implementation approved"
evidence:
  - path: .gnd-planning/milestones/guarded-rule-authoring/notes/phase-GA3-spec.md
    sha256: 8cd97d0bffc9281b5cc006568bed406289e404e600bb2f50eab99882b62efbad
  - path: .gnd-planning/milestones/guarded-rule-authoring/005-phase-GA2.md
    sha256: 06e0297c7c38a22cccf6c80cff90f6870e498ab2ff9a6418d51ce66ae5348701
  - path: .gnd-planning/milestones/guarded-rule-authoring/corpus/GA3/model.orm.yaml
    sha256: 646c93928aa096d38c7b2ed98bd199ef8b47b8679c25c1c406f213b1becfb516
  - path: .gnd-planning/milestones/guarded-rule-authoring/corpus/GA3/population.json
    sha256: e48b3ddb585abb09738ea1cc426ca1229ae4e115845cda846a8566c5b13119ec
  - path: .gnd-planning/milestones/guarded-rule-authoring/corpus/GA3/rules.tsv
    sha256: 312ba41f4c7dc5457bfb7dc682a28ad52dff29977cf708d0eadbbbefe1f8b58d
---

GA2 is complete. The prior owner selection and delegated plan cover the
role-typed literal codec, narrow same-predicate exception, and two recount
bounds. The red fixture precedes implementation.
