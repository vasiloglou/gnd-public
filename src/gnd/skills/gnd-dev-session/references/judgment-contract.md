# Saved external judgments (contract version 8)

Select version 8 explicitly for saved opinions. Versions 1–7 retain their old
meanings. A case has a required nullable judgment_gate: policy is a DigestBoundPath,
receipts_path is a candidate-relative file, and trusted_root is a protected
experiment-relative directory. A nonnull gate requires snapshot check with
constraint-satisfaction acceptance. Candidate paths cannot overlap authority.

The policy has schema_version 1, policy_id, trust_mode, ordered unique judges
and candidate occurrence targets, admission.minimum_approvals,
repair.minimum_rejections, nullable evidence_floor on both actions, and
trusted_receipts (judge_id/receipt_sha256 pins). Thresholds are per target.
Missing cells force false admission and false repair for that target. Abstention
counts toward neither. Overall admission requires every target to satisfy both
opinion and mechanical admission; repair requires any target's rejection floor.
Required gates conjunct session acceptance after its original mechanics and
coverage floors. Diagnostic gates are observable and do not veto acceptance.
Ranking remains mechanical; it does not certify policy admission.

Consumer-pinned-bytes-v1 checks saved content against consumer pins. It does
not authenticate a human, prove source truth, establish judge independence,
or calibrate confidence. Self-asserted mode requires an empty pin catalog.
Judgment assurance is always none. The mechanical report remains unchanged.

Receipts bind exact consumed model/population bytes, bound reference identity,
and one supplied candidate occurrence: fact_type/index/fact_sha256. Fact and
receipt digests use GND canonical JSON with exact numbers. Derived/reference
occurrences cannot be targets. Sources bind safe relative regular files by
whole-file hash and optional half-open byte-range quote hash. No source text
is executed. Normalization contracts must themselves be bound sources.

External evidence is nullable. Otherwise it has producer (system, nullable
model/version), normalization_contract (path/hash), answer and calibration_claim
(unspecified/provider-reported). Answers support choice distributions, numeric
score/legend distributions, binary p(yes), and verdict-confidence. A closed
version-1 normalization maps every choice label to a verdict, or supplies
inclusive approve/reject thresholds with reject strictly below approve. A
verdict-confidence normalization is identity. The reconstructed verdict must
equal the receipt verdict. Probabilities are finite unit values with sum within
0.000001 of one, unique labels/levels and no implicit renormalization. Provider
confidence is not assumed to be probability of correctness. Binary p(yes)
qualifies a rejection using 1-p(yes); no confidence is invented.

An evidence_floor selects reported-confidence with matching semantics
(distribution-concentration, provider-defined or estimated-verdict-correctness),
or verdict-probability with mapped-verdict-probability semantics, plus minimum.
Comparison is inclusive and uses exact numeric values. Missing evidence or
mismatched semantics makes a vote unqualified, not malformed or rejected.
Below-floor rejection does not trigger repair. review_required observes missing
or unqualified votes without adding an implicit third admission gate.

Read/shape validation precedes raw correspondence, semantic mechanical partition
validation, occurrence/source binding, duplicate/unexpected/trust checks, then
policy evaluation. Refusals produce no successful policy artifact. Judgment
command outcomes: 0 satisfied, 1 valid unsatisfied, 3 invalid, 4 unavailable or
resource-limited. A session that remains nonaccepted retains exit 15.

Limits: policy 1 MiB, bundle 10 MiB; 32 judges, 1024 targets, 4096 grid cells,
4096 receipts, 8192 pins, 8 source refs per receipt, 128 distinct sources,
1 MiB per source and 16 MiB aggregate; 64 answer options and 100000 distribution
cells; IDs 256 UTF-8 bytes, paths 4096 bytes; JSON depth 64 and numeric digits
128. Added work is bounded at 100000 indexed visits and a polled 10-second
layer deadline. Regular reads are retained-descriptor reads, not a promise to
interrupt blocked kernel I/O. Count/arity/path shape excess is outcome 3;
byte-read, aggregate-byte, indexed-work and deadline excess is outcome 4. Error
messages are bounded and omit input values.

Raw protected evidence retains policy, receipts, sources and separate report.
Attempt10/feedback9/launch4/result7 are version-8 successors; earlier families
remain closed. Replay recomputes the policy and validates every retained byte,
original authority and best pointer before further invocation. Candidate/operator
presentation is redacted and is not replayable evidence. No command obtains
judgments, invokes Jev or another provider, regenerates code, or runs a sibling.

Saved examples can represent TypeSafe-shaped Choice, Score and binary answers.
They demonstrate normalization contracts, not live provider interoperability.
Use gnd judgments check MODEL POPULATION --policy POLICY --receipts RECEIPTS
--trusted-root ROOT --format json for explicit saved evaluation. Set
--reference-root for bound reference populations and --unredacted only for an
explicit raw operator view. The dispatch/release fixtures in this repository
exercise real bounded local file producers without network calls.
