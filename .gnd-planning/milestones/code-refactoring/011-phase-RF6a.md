---
milestone: code-refactoring
station: phase-RF6a
skill: "n/a -- repository development, not a gnd-solve station over a domain model"
scope: phase-RF6a
date: 2026-10-06
source_base: 523cdd1a2ae1ad6ea0e8ca092fe29629dd10607c
verified_source_commit: cc39b3eb11be8b6b8bbbae70fe4fc84a798613fa
gate:
  command: ".venv/bin/python -m pytest -q tests/test_rf6_query_policy.py tests/test_rf6_index.py tests/test_rf6_registry.py tests/test_rf6_moves.py tests/test_rf1_layering.py tests/test_rf1_pin_harness.py --tb=short"
  exit: 0
  output: "110 passed in 14.33s"
slow_cadence:
  command: "uv run pytest -q"
  trigger: "explicit owner request or separately scoped CI selection"
  reason: "Full default, historical, proof, census, evidence, distribution and native lanes were not selected."
evidence:
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF6/A1-spec.md, sha256: 787bd2641a08f907d5a3764127d4421ae0705b7361ce57b71ed3f3dcd5db1ccd}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF6/A2-spec.md, sha256: d820bfbf580c29dc5039b292665a3b1737a80593c56bb6fee74789ac6b575a6b}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF6/A3-spec.md, sha256: 2476d640ef29597b379ef43c16cf118952f8a8d42d1c17aa2d293b9ee4dd6621}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF6/A4-spec.md, sha256: 125b9916bf1587e14d567550310c29f4fad21d6337d18ce025cc63bdc2bc7253}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF6/A5-spec.md, sha256: f0b005d250642ec8a5bf8c61db3526e425305ffedb2b598fa3c9aa153fbc231f}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF6/A6-spec.md, sha256: a4bcf28c35ac026a0d7ad7b1403a976c3cf6186cabc01c5bad0c405efc7ab354}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF6/RF6a-approval.json, sha256: b445e7b55fb8b183b2b8e7707cc030e359cc5fdff6d7d336909b522c5abfc695}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF6/RF6a-approved-spec.md, sha256: 8551d7a5e2c4b869ed90746e13d49bde58867bfdcd5314fe03e8f78144c9e504}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF6/RF6a-budget.json, sha256: 363a7e889ee46ebd83c0dc5a5af73d60032e9ed6fe33ea7170485813d376edd5}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF6/RF6a-compare.json, sha256: 0bb0378bbc8bd0273d43f03912b300e70616a12d7b22b305a6f8b623d3c8633e}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF6/RF6a-final-budget.json, sha256: 1b4db61c21cbee96067bf964ab4786352579795159f5da8b2b15c4d87cd23633}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF6/RF6a-hardening-final.json, sha256: 97bf9b3f4eca9154d099e91efe3b4ed9b211d3a839545ca7e866346eeeb138c1}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF6/RF6a-hardening-final.txt, sha256: d71f50709298d20a31824371b40fc15f99e68785555d0ff8b874f914ab85b48f}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF6/RF6a-hardening-lint.json, sha256: 6612b40190880612807f29d866b70f2c9db09f8eef9a029b9743043c97f1f262}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF6/RF6a-hardening-lint.txt, sha256: 921c576d6f6df9c9caa27d80bcba62b835ab6431844f948b87959ec308543dd7}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF6/RF6a-hardening-manifest-adaptations.json, sha256: d5229cf8ff13b0a537c477734d3dea30ecd7ec28335d7ae53122e2b86036f7e6}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF6/RF6a-impact-final.json, sha256: 5e3de5e1ff41ea63068122425ec05f9ee24927ce09ac51542d8245846197be5e}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF6/RF6a-impact-final.txt, sha256: 1792bd7acf8de7cf15e97872e7f203b6c7cc3a515082b02b446c9312df4ca037}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF6/RF6a-manifest-adaptations.json, sha256: c089f484bf56c7c1e4ab28084305ddd216c7ddd487b88e9398f1151906e87a5b}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF6/RF6a-py311.json, sha256: f2c7d9a9cbb4385b2c4cb6230d6c5055c4003e9f60a62d7199172010e38256b0}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF6/RF6a-py311.txt, sha256: 35f1974cd1e110bcc27c45952e7f1ed54597aeaa63d5992b1246b87eccce1150}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF6/RF6a-py313.json, sha256: c79210618262b4cc37ad837ae0ee4afeaef48cb93a53f1db1e1e968c488777ae}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF6/RF6a-py313.txt, sha256: d4ca1ab0812489f051084d51977d14878cc71136f30b2b557f68b780d5d8322b}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF6/RF6a-repair-review-prompt.txt, sha256: 09ec3fe6dcd7d49971f551e69440fa27f792c0f049fc4988aa0d24b6bf9cb9ad}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF6/RF6a-repair-review-run.json, sha256: 80e6e69cbc2837636c8f9a3aedd2b81425baf02ff07ced18854dcfee5a0e74ce}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF6/RF6a-review-hardening-red.json, sha256: 103c9a72e0a53d90b51dbdb8726d994aec7ec67098b4a639b13be75a8ce7ab0b}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF6/RF6a-review-hardening-red.txt, sha256: 7cb00641fe453ce47ea641904ea2ab49f50a81677be1fe6d0d7817a71a65d4f5}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF6/RF6a-review-manifest-adaptations.json, sha256: 6d67ac3eb8f9cd0bf747c89417c7cd79e1a5ca700f1e89da82146af4bf3d2ffa}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF6/RF6a-review-prompt.txt, sha256: 06503e0e27bb6db1b9ace0d56d04fe4ffe53504d167f80398464c755015bbb4e}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF6/RF6a-review-repair-controls.json, sha256: 876a333dee9307e3914586f6fcb4e8011878af5ada9444d3b4253488d1164f9d}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF6/RF6a-review-repair-controls.txt, sha256: 1ef3755f539e3042162d1a194177762f3a3a0de8866f18762e092d46a6b715e7}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF6/RF6a-review-repair-final.json, sha256: 6f16d0ec5d0a743984ecaae425d979c1293c121f690af6a7d0252d152a47a55c}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF6/RF6a-review-repair-final.txt, sha256: 81f84bb02354d63e00067a8a6fdc4eda51e3393cc34634a79dc308d9b5425096}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF6/RF6a-review-repair-lint.json, sha256: efd31f65e0583ac9ac541d36e604a0f2df261b224ab74999fc7d7b5df1e4b2b3}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF6/RF6a-review-repair-lint.txt, sha256: 921c576d6f6df9c9caa27d80bcba62b835ab6431844f948b87959ec308543dd7}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF6/RF6a-review-run.json, sha256: 8f2314d8d751f8f435a2944de017b4ad0564f71dce0c233763146fd93ba89011}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF6/RF6a-review-subscription-red.json, sha256: 6cb8fde51be60a1330f02a5ce75743164bc82ccac0cedfef128d07a2100103c8}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF6/RF6a-review-subscription-red.txt, sha256: 220bd417e6776745ff3e009e4f0a633c0538b864a0cd29f80d4614614661dab9}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF6/RF6a-semantic-final.json, sha256: a42d450a695f49a14d5b37998558cddcba3a4850bcf78a3d8976b08d5e89b7ab}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF6/RF6a-semantic-final.txt, sha256: 9a3952a1cc3457989683232df632f30f2d066c4a1189c8da2702accec59d5a46}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF6/affected-mutations/control.txt, sha256: 9f2f575b1731235a9b6825c2c7038f6b4dc62fd8b4fec9fce07dee995ca61677}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF6/affected-mutations/mutation-report.json, sha256: 8d159cf97b7c113efd89c9f0458d96f0e6926ad97dd1a2b34df13668975a54e6}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF6/baseline.json, sha256: 1eb2a4054629aadb9c798c46f8ac443784a3250ee1d05003b06fd17d4441516a}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF6/compatibility-repair-final.txt, sha256: 81e7202d9caff528a704935dc7f2abe0297a8b69882e9c310b09ab2bf4ae9d82}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF6/compatibility-repair.txt, sha256: 02aec9cf5fe50e7e88ea88c95fcd6794891b74a210e65d701b1b03751ac34602}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF6/controls-final.txt, sha256: c7ef0a77fd64d2a7675f6cfc3e8b54640c37297ae437a9902ac792a4fea573d6}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF6/controls.txt, sha256: f53c7a479cacc97c42287ffc4a5f374f76bca4d45d4604300605c7dfe9a37ef9}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF6/direct-final.txt, sha256: 3762df3475cc1d0c00b61fa1d4a5a5267141b0cf2766ccb0489fb90e1510f728}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF6/dynamic-query-candidates.json, sha256: 49fb5f8ea6856e8ba59de2d45e9e3a41372daa69eea3f008552efacad2962e22}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF6/frozen-authority-and-mutation-meanings.json, sha256: a2916922d01f6284fced798681e4f513c7d5e0a195e91aee3892c976bf4ec648}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF6/g0.txt, sha256: a5a6095dc05f51913f85dd2bb04b4e3536e00e5869a27ab1aba04a7c41df5126}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF6/g2-final.txt, sha256: 39f9400faa6f6adc06ef25de7da76771474610a95e522ddb518026108054e136}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF6/g2.txt, sha256: 1695ebab40462d68d1bfbf76d76b7cf25b89c467369e561bfad3fb283200d172}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF6/g3.txt, sha256: 5193ff760a31ea20dbeb53d14ce6ab25a83e542866a07322d47099ae1a79581e}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF6/helper-shape-red.txt, sha256: 894a48ccaf3f5c41464008584f4d4dab745f3fc0a425388de99162706831accb}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF6/impact.txt, sha256: 9e0c7f6d83c531150e99350cb9f3764c4eafbf8ceb5fca7904972acf0e241644}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF6/index-green.txt, sha256: 4d5d19ef04827b0f6265a2b090588b95a47f380b6ed437cafd32a1c58f97b0a4}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF6/index-red.txt, sha256: a39a43e00c0a1b1ab24227316a54aecd7160256dbb3e5bdb5910882ccf10fe73}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF6/key-red.txt, sha256: 6ac5ada80f5507f3b9fe40bc23a1fe254ff80a002994b9750e886cdc2a13f0cc}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF6/lint-final.txt, sha256: 5fd18f0eb26c80319e5c956ed0193b4a4a8604733fdc8d58b9f2aa5245af3102}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF6/lint.txt, sha256: 6222e52953494784e23bc9069a0960629f9fa462bc535919377451db4805f0ac}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF6/malformed-red.txt, sha256: 3243ea6a9863cf670d4f1325a8fa4a0b4cd6b4b5baf443ace5f64ae059c471da}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF6/metrics-RF6a-final.json, sha256: de9d3970eb0c60ab1718cc3ee5ea180596d301648650a5b307ecc9b9d42709a5}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF6/metrics-RF6a.json, sha256: 5ba2e6e53dc1225f6d90176e974d5cf0625439aa8740f679696ff049e5656121}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF6/mutation-retarget-originals.json, sha256: 933484d0588d4c2b655b23cbc60792412c84669220e257b5c44db4086efc3fce}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF6/mutations.txt, sha256: cb1cb26da19db4f370087557ec7496137dd7dc7ed9f9e5da2266d77876cf3260}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF6/preexisting-RF3-metric-red.txt, sha256: 8078da74181e5af84bec84b21c1eb69116efa2775d5c34f1b58fae2c03422db8}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF6/primitive-move.txt, sha256: 9ba07872e76f444490ff0674a153377a9462a75673adeb482a834a3537c4ff15}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF6/primitive-moves.json, sha256: f898b56240659669e62b37ad874cb702f17af2659b3bb605e207c4fc7ff9ad72}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF6/provider-review-authorization.json, sha256: e3f22c35ee7dda435239f67d57633d8e3da2f687e5f8a8196f4521037ef8ec5a}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF6/query-allow-list.json, sha256: 26cb16bf1da5d8873ad1e24c6989ae0d2bcfb5222e980d39e320bed5e41b142b}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF6/query-baseline.json, sha256: f8f13b9827b31273f4e11e1b18466e1e3198022f8d77a53ffe3fddab520dd02e}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF6/registry-base-red.txt, sha256: 5cde275835ef03eb2454370e6ced29b5b53acc73dd351725002a3a38c7e57c10}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF6/registry-extraction.json, sha256: 2efcf7b6f551794b55f9be9e5401d4a8d66869dc009e8515be6ba9745d6deabf}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF6/row-identity-red.txt, sha256: 196e180f027aa2d4efd6ee48e977128a955ce12907d69626e3a361553ec3f1c0}
  - {path: .gnd-planning/milestones/code-refactoring/notes/phase-RF6a-spec.md, sha256: a4bcf28c35ac026a0d7ad7b1403a976c3cf6186cabc01c5bad0c405efc7ab354}
  - {path: .gnd-planning/milestones/code-refactoring/notes/phase-RF6a-amendments.json, sha256: 5e4192a7e4040016126eb2b121ad0e6d24d6de234532046c044553cbeecf6351}
  - {path: .gnd-planning/milestones/code-refactoring/notes/phase-RF6a-codex-review.md, sha256: 1f4fc251e1a0821c9b02921f1982ecc646734b2f2db7de4eb44b5d2abe005035}
  - {path: .gnd-planning/milestones/code-refactoring/notes/phase-RF6a-codex-repair-review.md, sha256: cf09bf2f47a31be8c3e7047e8ac4146754f79ac4aae95a7a01306bb2394a6189}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF6/RF6a-record-controls.json, sha256: 0b4f9ce56f1eefbe1110cb969a59ec37c8625f114b3472a507dfbf51f6e71ca2}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF6/RF6a-record-controls.txt, sha256: 40ecdef10ec09d0c01b572bf057a1e4226e8e583c67aff096d3bd5463199fd25}
---

## What shipped and measured criteria

RF6a supplies ModelIndex's detached snapshot API, full-document internal canonical cache key, bounded32 LRU, canonical constraint iteration, both retained primitive policies, and stateless historical object/role/fact lookup aliases. Compatibility aliases keep original live-row identity, malformed errors and SimpleNamespace shapes; they deliberately do not universally route through snapshots (A4). Six primitive bodies move verbatim to model_queries with live historical shims. value_domain.in_range exposes the unchanged old callable and old metadata under RF-D8/D10. Family-specific adapter/evaluator/witness/message/scope/implemented hooks resolve from one registry entry in existing defining namespaces; the fake-family test changes only its registry entry and exercises all six surfaces, without adding a public schema family.

RF6-C1 original attribute/get count320→299 meets ceiling310; exact exemptions243 original rows. The independent review exposed missing subscription evidence. A5 adds51 literal subscriptions, total371→350, ceiling361, exact281 reasoned rows. All literal occurrences are checked, with missing/new/stale/extra negatives. Dynamic inventory has5756 rows /7257 syntax candidates and refuses omitted/new/duplicate candidates. This is candidate enumeration, not semantic alias resolution. All six layers remain clean,216 modules, no wrong-way/unresolved edges; only the pre-existing seven-module RF8 session SCC remains. Private imports319→324: additional query/registry boundaries and primitive ownership imports explain the increase; no reduction claim. RF6b package/import criteria remain owed.

SM1 original RF1 golden/input bytes and167 mutation IDs/expected-red answers stay unchanged. Six source-location/stimulus adapters retain original rows and unchanged injected exception/resolver meaning; all six affected mutants killed with green control. SM2 primitive aliases/range alias retain identity and original metadata, with inventory retirement trigger. SM3 actual full source observers reach all new homes and a missing-query-home negative is red. SM4 every new module has a layer entry and full six-layer guards pass. Bounded b3 adaptations update only phase-owned rows; units.json and the distribution authority test remain frozen. Historical production/release identity and certificates are unavailable over changed source.

## Findings, red histories and refuted premises

Initial G0:509passed/1failed. The original RF3 numeric private-count predicate expects64 and observes242 on the archived base523cdd1 before RF6. It is explicitly deselected, all other RF3 controls retained with full current graph/layer successor. Initial index11red because absent; A1 corrects this newly authored inline-reference expected spelling, preserving existing canonical address. Family extraction/routing occurred in one same-module behavioral commit rather than the originally promised separate extraction-only commit (A3); this procedural exception is recorded, not retroactively described as separate. Physical primitive move is its own unchanged-body checkpoint.

Cache key coercion nonstring/string collision reproduced red before uncached bypass; no canonical encoder changed. Non-Model fallback, malformed object-map exception, unhashable raw target and row-identity regressions each reproduced before A4 stateless compatibility repair. A mechanical edit briefly removed interstitial imports and collection refused; restored before shipment. Initial G2 mutation source-precondition failure led to A2 source-location adapters preserving167 original meanings. Initial lint refused13 findings; import-only repairs preserve body hashes. Original red artifacts remain bound above.

Independent initial review of523cdd1..e404262 found one medium blocking instrument defect: subscription injection escaped. Observed one-test red before A5 scanner expansion. Repair review ofe404262..464d223 independently confirms literal counts/reasons, original and combined arithmetic, no production algorithms changed and current dynamic inventory. It found two low hardening defects: injection-only negative could pass for baseline mismatch, and duplicate inventory rows collapsed. Both independently observed red (two failures) before A6 repairs. Final110pass/lint0 checks actual hardened bytes. The second review did not inspect later A6 fixes; no reviewer opinion is claimed over those final bytes. Initial+one repair exhausted; no third review. One reviewer is one reviewer. Read-only reviewer ran small probes and read retained gates, not the selected pytest suites or prohibited lanes.

Branch-table audit: all declared factory/cache/detachment/mutation/eviction/fallback/query/ref/primitive variants and existing registry/fake/unknown/unimplemented/common-refusal lanes have direct controls. All literal policy directions and dynamic duplicate/new/omission controls are falsifiable. Explicit two-parent closure and committed rejected_proposals/deontic_notes cases are completeness observations, deferred to model-query successor after reviewer probes found no failure; this does not claim those committed cases exist.

## Refactoring review

What did this work reveal about existing structure that should change? Refactors EXECUTED: shared six primitive algorithms in model_queries; one historical map/fact lookup home with explicit identity-compatible methods; local family handlers selected by one registry; range visibility alias. Selected semantic/affected-consumer gates remain green over their algorithm bytes. Seen but deferred: individually allowed domain/raw/IR traversals need separately pinned model-query successor routing; standalone PyRel copy/emitted runtime retains RF2-OQ2 no-GND-import boundary. RF6b owns physical model/checker organization and owed import pins. RF7 owns tightening/variant mergers; RF8 owns session SCC/version/resume; milestone close owns normative wording reconciliation.

## Boundary -- what this phase does NOT establish

No new semantics/commands/flags/schema/version, strictness, performance claim, variant merger, broad historical repair, new acceptance/certification/publishing or source-owned transfer. One reviewer is one reviewer. Local selected results do not establish other OS/installed acceptance. RF7 strictness, RF8 sessions, milestone-close wording/helper questions and source-owned OQs remain owned there. Prior source control is not a new human attestation; source-side comparison remains unavailable as inherited from RF5. Original corpus meanings/bytes stay unchanged. Dynamic syntax inventory does not resolve selector meanings. Frozen dataclass private snapshot internals are implementation state; detached public queries are tested. RF6b is not established by this record. Approval and amendment marks are delegated agent decisions under RF6 auto, not human readings.

## Open questions

RF6b package split/import pins remain owed; model-query successor owns remaining reasoned direct traversals, dynamic semantic routing and completeness controls. RF2-OQ2 export-format successor owns standalone PyRel consolidation. RF-D5 retirement needs first public release after RF6 and separate approval. RF7/RF8/close and source-owned responsibilities above retain their owners. The recorded A3 procedural departure stands; no plan is rewritten during a phase.

## Gate output (verbatim)

Counts overlap and do not define a combined acceptance universe. Exact sanitized retained outputs follow; initial reds and their explanations are separately bound above.

### RF6a-semantic-final

    Retained output edited to replace machine paths.
    Command: .venv/bin/python -m pytest -q tests/test_rf1_helper_pins.py tests/test_rf1_semantic_pins.py tests/test_checker_families.py tests/test_public_semantic_adapter.py tests/test_rf3_core.py tests/test_reference_universe.py tests/test_subtype_universe.py tests/test_ring_frozen.py tests/test_vacuity.py tests/test_rf6_index.py tests/test_rf6_registry.py tests/test_rf6_moves.py tests/test_rf6_query_policy.py tests/test_rf1_pin_harness.py tests/test_rf1_layering.py --deselect=tests/test_rf3_core.py::test_full_current_and_original_core --tb=short
    ........................................................................ [  9%]
    ........................................................................ [ 19%]
    ........................................................................ [ 29%]
    ........................................................................ [ 38%]
    ........................................................................ [ 48%]
    ........................................................................ [ 58%]
    ........................................................................ [ 67%]
    ........................................................................ [ 77%]
    ........................................................................ [ 87%]
    ........................................................................ [ 96%]
    ........................                                                 [100%]
    744 passed, 1 deselected in 53.23s
    
    Exit: 0

### RF6a-impact-final

    Retained output edited to replace machine paths.
    Command: .venv/bin/python -m pytest -q tests/test_model_validation.py tests/test_model_v2.py tests/test_model_guarded.py tests/test_model_identity.py tests/test_model_verbalization.py tests/test_poolfile.py tests/test_synth_boundary.py tests/test_synth_mutate.py tests/test_synth_oracle_value_range.py tests/test_synth_tagged_comparison.py tests/test_synth_conforming.py tests/test_conformance_structural.py tests/test_codegen_emit.py tests/test_development_scaffold.py --tb=short
    ........................................................................ [ 13%]
    ........................................................................ [ 26%]
    ........................................................................ [ 39%]
    ........................................................................ [ 52%]
    ........................................................................ [ 65%]
    ........................................................................ [ 78%]
    ........................................................................ [ 91%]
    ................................................                         [100%]
    552 passed, 1 deselected in 68.74s (0:01:08)
    
    Exit: 0

### RF6a-py311

    Retained output edited to replace machine paths.
    Command: /private/tmp/rf2-py311/bin/python -m pytest -q tests/test_rf6_index.py tests/test_rf6_registry.py tests/test_rf6_query_policy.py tests/test_rf6_moves.py --tb=short
    ........................................                                 [100%]
    40 passed in 4.27s
    
    Exit: 0

### RF6a-py313

    Retained output edited to replace machine paths.
    Command: /private/tmp/rf2-py313/bin/python -m pytest -q tests/test_rf6_index.py tests/test_rf6_registry.py tests/test_rf6_query_policy.py tests/test_rf6_moves.py --tb=short
    ........................................                                 [100%]
    40 passed in 3.94s
    
    Exit: 0

### RF6a-review-repair-final

    Retained output edited to replace machine paths.
    Command: .venv/bin/python -m pytest -q tests/test_rf6_query_policy.py tests/test_rf6_index.py tests/test_rf6_registry.py tests/test_rf6_moves.py tests/test_rf1_layering.py tests/test_rf1_pin_harness.py --tb=short
    ........................................................................ [ 66%]
    ....................................                                     [100%]
    108 passed in 14.84s
    
    Exit: 0

### RF6a-hardening-final

    Retained output edited to replace machine paths.
    Command: .venv/bin/python -m pytest -q tests/test_rf6_query_policy.py tests/test_rf6_index.py tests/test_rf6_registry.py tests/test_rf6_moves.py tests/test_rf1_layering.py tests/test_rf1_pin_harness.py --tb=short
    ........................................................................ [ 65%]
    ......................................                                   [100%]
    110 passed in 14.33s
    
    Exit: 0

### RF6a-hardening-lint

    Retained output edited to replace machine paths.
    Command: .venv/bin/ruff check tests/test_rf6_query_policy.py
    All checks passed!
    
    Exit: 0

### lint-final

    Retained output edited to replace machine paths.
    All checks passed!

### mutations

    Retained output edited to replace absolute machine paths.
    rows: 6  killed: 6  not killed: 0

### RF6a-record-controls

    Retained output edited to replace machine paths.
    Command: .venv/bin/python -m pytest -q tests/test_development_scaffold.py tests/test_contributor_preparation.py --tb=short
    ...................                                                      [100%]
    19 passed, 1 deselected in 4.64s
    
    Exit: 0
