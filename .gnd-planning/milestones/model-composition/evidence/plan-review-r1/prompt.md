You are an independent reviewer of a milestone plan in the GND repository (current directory; Python package under src/gnd). You have read-only access. Do not modify any file.

Review these two draft documents (uncommitted, in the working tree):

1. .gnd-planning/milestones/model-composition/notes/model-composition-plan.md (plan r1, sha256 bd661eeede495e2c3c82e9fbd81cfa6d79f7d2a8d0f77c4374f20736f6d1597a)
2. .gnd-planning/milestones/model-composition/notes/phase-MC1-spec.md (first phase spec draft, sha256 b6ebc5db0b9ecaba0992380ff43f05d865d05415a2dbcbebf9016200a4c06dff)

The request they plan for is GitHub issue 95 ("GR-D4: build a model from a shared part and a project part"): one ORM model file takes its object types and fact types from another file, bound by digest like a reference population; the including file adds constraints (and possibly fact types); `gnd validate` and `gnd check` resolve it; ids stay in one namespace. Motivation: a tool ships a fixed vocabulary to many projects, each project writes its own rules, and vocabulary updates must not overwrite the rules or leave the next check ill-formed. The project must own a real model file usable with `gnd evolve` and `gnd verbalize`.

The protocol these documents must satisfy: AGENTS.md; .codex/skills/start-milestone/SKILL.md; .codex/skills/process-phase/references/project.md (standing design rules), spec-note-contract.md and standing-rules.md. A recent plan of the same shape for comparison: .gnd-planning/milestones/rule-check-followups/notes/rule-check-followups-plan.md.

Check, against the actual source code at this commit (cite file:line):
- Implementability: can each phase deliver its criteria with the code as it is? In particular the loader (src/gnd/model/__init__.py load_model, _load_model_no_follow, load_model_bytes, _bind_at, validate_declarations, retained_root, _relative), src/gnd/documents.py Model (frozen, extra=forbid, model_dump override, private attrs), src/gnd/values.py identities (_model_digest, model_identity, reference_model_digest, _reference_identity_document), src/gnd/model/_validation.py (_layer1_structural, semantic_validate, _rule_id_unique), the meta-schema src/gnd/schema/orm-meta.schema.json and its synced copy, the CLI validate/check error mapping in src/gnd/commands/checking.py, and evolve publication in src/gnd/evolve/service.py.
- Factual claims in the plan's §1.2-§1.3 and §2.4 (the claim that the including file's raw sha256 is a complete identity of the composition; the claim that include-free models keep every byte and digest).
- The proposed validation order (spec §6.2) for contradictions (e.g. step 7 placed after step 6 but said to run before it), unreachable branches, and refusals that cannot be told apart.
- Whether every spec test can fail when the behaviour is wrong, and whether any criterion lacks a test.
- Missing consumers or risks: anything that would load or hash the including file alone and silently get a half-model; interaction with reference_populations, operations, derivations, subtypes, rejected_proposals, deontic notes, model_id; evolve and discover writing a flattened model.
- Contradictions between the plan and the spec, and decisions that should be owner decisions but are presented as settled.

Reproduce every claim you make with a read or a read-only probe (you may run python in read-only fashion, e.g. `uv run python -c ...`, without writing files). Do not report style preferences.

Output format, exactly:

DISPOSITION: approve | revise | block

then for each finding:

ID: P<n>
SEVERITY: blocking | hardening | completeness
LOCATION: <path>:<line>
QUOTE: <short exact quote from the reviewed document>
PROBLEM: <what is wrong, with source citations and probe results>
FIX: <the concrete change>

End with one line: SUMMARY: <one sentence>.
