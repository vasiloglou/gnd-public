# MC2 narrated corpus (r1; gate inputs)

The anchored directory contains two independent source documents, their populations and anchors from the existing CT2 fixture, and its include-free model. contracts-v1.orm.json is a standalone vocabulary; project.orm.json pins that vocabulary and keeps the project identity. All anchored facts and constraints are unchanged by the split.

Cases:
1. Render the include-free model through Model and path entry points. Compare its exact retained text.
2. Render the project file: show the include declaration in its header and all vocabulary semantics.
3. Compose the same anchored sources under the project model, then replay-check the population and record.
4. Change vocabulary bytes while leaving the project pin unchanged. Both rooted routes refuse before derivation/output.
5. Replace includer bytes between loading and composition replay; refuse before record verification.
6. Leave codegen/conformance/copy routes refused even if the include files are present.
7. Render two includes declared z-contracts then a-labels; preserve that authored order.
8. Construct a Model directly from unresolved-model.json rather than loading the file; refuse missing resolution metadata before rendering.
9. Ask the new model CLI to render an absent model; return66 without review text.
10. Ask it to render malformed JSON; return3 without review text.
11. Load a vocabulary declaration whose ID/path carry control characters; each include still occupies one escaped header line.
12. Ask composition replay to consume an include-bearing in-memory Model without a path coordinate; retain its explicit unsupported refusal.
13. Render owned-inline/project.orm.yaml; show project_no_loops and project_owner_required once each alongside the included semantics.

Expected outcomes are deliberately separate in answers.json. No candidate implementation produced them. Existing include-free observable outputs were frozen from c7fc66dd before MC2 edits. Absolute temporary fixture paths in the compose baseline are coordinates to normalize to the fixture root, not model values. First preparation attempted /tmp on macOS, which correctly refused a symlink ancestor; corrected to /private/tmp before freezing this successful control.

Replay expected output normalizes only the fixture-root coordinate to <CORPUS>; all other retained fields remain exact.
