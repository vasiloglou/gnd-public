# CT4 diff review: the `fact-type` discover family

Subject: the uncommitted working tree on top of `4584415` (`git diff` plus the untracked
`src/gnd/discover/types.py`, `tests/test_discover_fact_type_family.py`, the CT4 spec and
`evidence/CT4/`). `.claude/launch.json` was ignored. I made no edits to the repository.

## Verdict: approve-with-fixes

The core behaviour holds up. No population value leaks without the flag: the proposal,
report and stdout use opaque `ft<k>#<i>` ids, the readings use object type names, and
`value` is gated by `values_allowed`. Support counting, thresholds and the deontic
envelope are correct. A combined `uniqueness,mandatory,fact-type` run passes
`evolve preview --policy additive` and `evolve apply`, and the applied model validates.
CT-R1 parity reproduces byte for byte. The focused gate passes: 572 passed.

Two findings break standing rules and should be fixed before commit. F1 is a traceback,
which breaks totality. F2 is an output over the proposal size cap, which breaks the
input-cap rule. F3 and F4 are design gaps that need either a fix or a recorded ruling.
The rest are low.

## Findings

### F1 (high): an id collision crashes with a traceback (exit 1) and writes no report
`src/gnd/discover/types.py:119,123` and `src/gnd/discover/service.py:395-399`.
The new ids `<generic>_induced_<n>` and `<generic>_induced_<n>_value` are never checked
against the ids already in the model. When one already exists,
`output.candidate_document` → `_apply_declared_operations` raises
`EvolutionError: add target fact_types[item_has_attribute_induced_0] already exists`.
`_cmd_discover` catches only `OSError` there, so the run ends with a Python traceback
and exit 1.

Reproduction: take the test fixture and add a fact type with id
`item_has_attribute_induced_0`. Then run
`gnd discover ... --families fact-type` (scratch `exp/e3.py`, case `c1`).

Fix: skip ids already in the model, for example by advancing `n` past any taken id, or
by counting the group under a `skipped.id_collisions` counter. Check both the fact type
id and the `_value` object type id. Also consider validating the combined candidate model
the way the other families do (`load_model_bytes` at service.py ~232). Any defect would
then surface as a `DiscoveryDefect` (exit 70) instead of an uncaught exception.

### F2 (medium): the family's operations ignore the proposal size budget
`src/gnd/discover/service.py:396`. The other families go through `_within_budget`
(service.py:153), which keeps the proposal under
`min(MAX_MODEL_BYTES, MAX_EVOLUTION_PROPOSAL_BYTES)`. The type operations are appended
after that step and are never budgeted.

Reproduction: 2,700 attributes × 30 entities (81,000 rows, a 6 MB population) at the
default `--min-support 20`. Discover exits 0 and writes an 11,215,456-byte proposal.
`gnd evolve preview` then refuses it: `74 ... over the 10485760-byte cap`
(`exp/e7.py`, case `h3`). Discover produced a proposal that its own consumer cannot read.

Fix: put the type operations' cost under the same budget, with a counted
`skipped.over_budget`, or refuse with a named error. Each group also emits up to 288
example ids. Capping `rows` in the report should be considered too: 2.7 MB in the case
above.

### F3 (medium): a fully violated uniqueness is still proposed
`types.py:129-162`. A group whose entities all have two or more rows gets
`support: {numerator: 0, denominator: 25}`, and its uniqueness is still emitted as an
`ADD` (`exp/e6.py`: exit 0, proposal written). Every other family drops failing
candidates and lists them as near misses (service.py:254-266). D4 only defines the
numerator; it does not license proposing a uniqueness the evidence contradicts. A
multi-valued attribute such as "tag" is the normal case for this.

Fix, one of:
- (a) still propose the fact type, but add the uniqueness only when it passes or is a
  near miss;
- (b) record a ruling that deontic induced uniqueness is proposed whatever the support.

### F4 (medium): redaction on the value or entity role is not carried to the new fact type
`types.py:91-93,139-144`. Only a redacted attribute role is skipped. When the generic
fact type's value role (or entity role) carries `redact: true`, the proposed binary fact
type's `value`/`entity` role does not. Admitting the proposal and later migrating the rows
would move redacted values into an unredacted role (`exp/e3.py`, cases `c4` and `c5`: the
proposal is emitted and the roles have no `redact`). Redaction declared on the object type
is unaffected, because the type is reused.

Fix: copy `redact: true` onto the matching new role when
`(generic, spec[role]) in redacted`. Alternatively, skip and count the group as for the
attribute role. Either way, add a test.

### F5 (low/medium): the disclosure table misstates `gnd discover`
`src/gnd/disclosure.py:94-95` and `docs/reference/disclosure.md:206`. Discover is
registered as `Surface("site", convention="declared")`, so the generated table now groups
it with check/validate and says "declared roles: shown under `internal`, redacted under
`customer`; `--unredacted` ... refused under `customer`". That is wrong for discover:

- It has no `--unredacted`.
- Redacted roles never get value candidates in any mode, including `internal`.
- Its other value-family outputs (`allowed` lists of undeclared values) are the same in
  every mode, which plan CT-R7 requires to stay unchanged.

The diff also deletes the explanatory row at disclosure.md:122 ("candidate constraints;
never value candidates for redacted roles") without replacing it.

Fix: give the row its own note or convention text: "`--show-values` follows
`values_allowed`; everything else the same in every mode". Restore the explanatory line
under the site section.

### F6 (low): the E1 parity explanation is misattributed
I reproduced the T6 tables. `capture_parity.py` against a `git archive a2e44f8` tree
matches `parity-a2e44f8.json` byte for byte, and the current tree matches
`parity-after.json`. Only E1 and E6 differ, both in stderr only:

- **E6** differs because the discover usage line gains `[--min-support MIN_SUPPORT] [--show-values]`, as claimed.
- **E1** (`--bogus`) differs only because the top-level command list gains `compose`,
  which came from CT2. Against a `4584415` tree, E1 stderr is identical.

The claim "usage text now lists new options" is therefore accurate for E6 only. Record the
E1 cause precisely.

### F7 (low): text output leaves out the family
`src/gnd/discover/output.py:163-181`. Under `--format text` (the default), nothing about
`fact_type_proposals` is printed; only `PROPOSAL <path>` appears. Add a
`FACT TYPES proposed=.. shape_matches=.. skipped ...` line with counts only, so no values
appear. The proposal rationale (output.py:143) also counts fact type and object type ADDs
as "candidate constraints".

### F8 (low): recorded deviation, family row visits are kept out of `work`
Spec standing rule 2 says the family "adds its row visits to discover's `work` counters
and ceiling". The implementation reports `row_visits` inside its own key and has no
ceiling check. I judge this acceptable: it is one pass, linear and bounded by the
population cap, and it keeps CT-R1 byte parity, which the spec's own rule would break for
fact-type runs only. But the spec text still states the opposite. Amend standing rule 2 in
the spec, or record the deviation in the phase record. `docs/reference/discover.md:155`
should say that the work counter excludes the family.

### F9 (low): test gaps (from mutants, below)
- No test reaches the new-value-type branch. With a validated population, that branch is
  reachable only when the value role's primitive cannot be resolved, for example an entity
  subtype with `inherits_reference: false`. I checked it by hand (`exp/e5.py`): ints give
  `Number`, strings `String`, bools `Boolean`, and all pass preview. The `Date`/`DateTime`
  entries of `_PRIMITIVE_FOR_KIND` are dead code, because without a primitive a date string
  has kind `string`.
- T5 as specified ("while another group in the run is proposed") is not what the test
  checks: both groups match and none is proposed. With one validated generic, every group
  shares the value type, so the spec case needs two generic fact types or the
  unresolved-primitive path.
- T6 is only partly in pytest. The table is recorded evidence, which the spec allows.
- There is no test for `--families uniqueness,fact-type` with preview or apply, and none
  for an id collision (F1).

### F10 (informational)
- **Shape-check consequence (D2):** one unrelated existing binary over
  (entity type, value type), such as `item_has_label`, blocks every group of that generic
  forever. This follows the ruling, but it is worth stating in the discover docs.
- **Numbering:** `n` counts every group in first-seen order, including skipped ones, so
  ids have gaps. That keeps ids stable across `--min-support` changes, which is good. They
  do shift when a new attribute appears earlier in the rows.
- **Attribute digest:** `sha256(repr((type, value)))` is unsalted. Short attribute names
  are easy to guess-and-check under `customer`. CT-D9 allows SHA-256, so this is advisory
  only.
- **Validation order:** an invalid declaration refuses before candidate generation
  (service.py:199). M14 shows the order itself is not pinned; the exit code is the same
  either way.
- **Edge cases that work:** an entity role and value role of the same type gives the
  reading `{Item} has induced attribute 0 {Item}`, which passes preview. A new value type
  name that collides with an existing object type's name is accepted by preview, giving
  two types named `ItemHasAttributeInduced0Value`.
- **Flags:** `--min-support` rejects 0, -1 and `abc` (64). An explicit `--min-support 20`
  without the family is also refused, which is stricter than the spec's "non-default" and
  fine. Under `customer` without `--show-values`, the run exits 0 and no `value` keys
  appear.
- **Anonymity:** a scan of the diff and new files finds no downstream names.

## Mutants (scratch copy of `src`, PYTHONPATH, `tests/test_discover_fact_type_family.py`)

| Mutant | Result |
|---|---|
| M1 always emit `value` | killed |
| M2 numerator = all entities | killed |
| M3 `support <= min_support` | killed |
| M4 no redacted-attribute skip | killed |
| M5 support = rows, not entities | killed |
| M6 no mixed-type check | killed |
| M8 no shape check | killed |
| M9 modality alethic | killed |
| M10 bypass `values_allowed` in the CLI | killed |
| M12 never add a new value type | **survived** |
| M13 `number` → `Integer` primitive | **survived** |
| M14 drop the early declaration check | **survived** (same exit, ordering only) |
| M15 drop type ops when no other candidate | killed |
| M16 dense numbering | killed |
| M17 examples = all rows | killed |
| M18 allow flags without the family | killed |
| M19 keep rows with no entity or value identity | **survived** |

## Gate
The focused gate in the brief gives `572 passed in 87.03s`.

## Could not check
- The full test suite: I ran only the focused gate.
- Behaviour on a non-macOS filesystem.
- The `rf1` goldens' content beyond their passing tests.
- Whether the plan owner intends F3 (b).

Scratch reproductions are under
`<scratch>/exp/`
(`h.py` harness; `e1`–`e7`), with `mut.py` and the parity runs beside them.
