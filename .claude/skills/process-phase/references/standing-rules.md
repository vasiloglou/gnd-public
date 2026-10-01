# The rules that bind every phase

Two lists. The first is the plan's section 0 — design rules earlier phases
**already paid for with reproduced defects**, which bind every remaining phase.
The second is the failure classes this milestone has committed at least once, so
each is a thing to check for rather than a thing to hope about.

A spec discharges every section 0 rule **by name** — naming the specific loader,
the specific layer, the specific policy walk — or argues it inapplicable in one
sentence. Silence on a rule is a review finding.

## Section 0 — the paid-for rules

### 1. Totality belongs to the function, not the caller

"This only ever sees validated documents" is a claim about today's callers.
Any new consumer of document shapes is **total over arbitrary JSON**, with a
hostile-input test. The defect that bought this rule: a gate that consumed
proposal-supplied bytes with no validation layer in front of it, in a codebase
where every other consumer had one.

Totality is more than catching one exception class. Check all of:

- The cap is applied to the **read**, not after it. A cap applied after
  `read_bytes()` is a report, not a cap.
- Exception classes that are not the obvious one — a very long integer literal
  raises `ValueError`, not `JSONDecodeError`; deep nesting raises
  `RecursionError`.
- The non-JSON constants. `NaN` and infinities are accepted by default and are
  not JSON.
- The docstring. If it promises totality, a traceback out of that function is a
  contradiction of the shipped contract, not a rough edge.

### 2. An input cap bounds the document, not the algorithm

A rule quadratic in a count the document controls turns a legal input into
minutes of CPU under the cap. Every phase that adds work proportional to
untrusted input ships a **time-bound test over the layer it adds**.

This is the class that was caught once and that nobody searched for twice.

### 3. Validation order is part of the design, stated per boundary

Which check runs first is a design decision with a user-visible consequence: a
gated delta should report "gated", not "your candidate is invalid", or the author
is sent into the other half of the same gate. Where two orderings both reject and
no return value distinguishes them, **pin the order by source-order assertion**.

### 4. A policy governing N element kinds is enforced by one walk over all N

Not N copies of the policy. A shared policy implemented per-kind will be right in
the kinds someone remembered and absent in the rest.

The corollary bites on the fix side too: when **one** function serves both an
authoring-time warning and an evaluation-time verdict, a defect in it is wrong in
both places and is fixed once — which is the point.

### 5. Normative prose has exactly one home

A document written alongside its implementation is a second chance to make the
same mistake, not independent evidence. Keep each normative sentence in one home
so a divergence is a **bug** rather than an ambiguity; everything else cites it.

**Scope:** the rule governs normative *prose*. It does not forbid byte-identical
sync-pinned copies of an interchange schema — a canonical reference plus a
vendored copy held identical by a mechanical identity test is ONE artifact. This
scope is written down because a reviewer reading the unscoped rule literally
reported such a pair as a violation.

When a phase's work makes two homes disagree, **one of them yields in that
phase**, and the spec names which.

### 6. Resolve contested representation questions by measurement, not argument

Where the codebase can host an experiment, run it. A contested digest question
was settled by making the change and watching eight committed-payload tests go
red — the artifact's own contract decided it, in minutes, with no debate.

## The failure classes this milestone has committed

### A declared branch with no case that can fail it

**The defining defect.** Found five times in a single spec draft; found once in
the very file written to prevent it; found once by a self-audit performed
*after* an adversarial review that missed it.

- Walk the **branch table**, not the code.
- A test asserting that a string appears in a source file cannot fail when the
  behaviour is wrong. It is not a case.
- A guard that returns silently when its control invocation raises counts a
  broken control as a success.
- An exemption consulted only on a path that never names it is dead code
  reporting green.

### A class credited when only one half of it has a case

Count coverage **per branch**, not per class. A finding class whose second half
is unreachable with the fixture model is half-covered — and reachability is a
property of the fixture, so closing the gap can mean editing the **model**, not
adding cases.

### A rule made unfalsifiable by how the fixtures were built

A grading rule quantified over "any" versus "every" reads identically on fixtures
where the subject is only ever touched once. The fixture set has to contain the
discriminating case, or the rule ships unverified while its coverage row says
otherwise. Ask of every rule: *what fixture would tell the two readings apart,
and is it in the set?*

### The repair round is itself a hazard

Measured once: **five of eight** agreed concerns in a review round were defects
introduced by the *previous* round of repairs, not by the original draft. Any
repair pass over a reviewed artifact re-checks the neighbours of every edit, and
repaired bytes carry no review opinion until they are re-reviewed.

### An interchange field defined in Python-only terms

Every digest or identifier a **caller** must reproduce is defined over canonical
JSON, with a stated empty case and a shipped producer. In-process markers may use
language-specific representations only if they never cross a boundary.

Related traps, each seen:

- A digest that **coerces non-string mapping keys** loses content: two distinct
  documents hash identically. That is different in kind from a spelling
  coercion, and it is refused rather than documented.
- A canonical-form helper **re-implemented** at a second site with the same
  arguments and no guarantee they stay the same arguments.
- A digest taken over a section that something else then **writes into** — the
  digest moves and every committed artifact stops matching its own source.

### A single reviewer mistaken for a panel

Records say "one reviewer is one reviewer." The multi-reviewer panel remains the
bar for plan review and milestone close.

## Implementation traps worth a checklist

Each of these was a real finding, and each generalizes past the phase that found
it.

- **The schema's spelling and the implementation's spelling differ.** Check the
  enum members literally, and assert the implementation's map covers the enum.
- **"Not implemented" folded into the same branch as "violated."** The failure
  mode is the bad one: input that *satisfies* a rule is reported as failing it.
  Raise a distinct unknown-operator error instead of fabricating a verdict.
- **A property decided about the wrong subject** — about the type rather than
  about the binding, so the answer depends on which fact happens to come first.
- **A guard that goes quiet exactly when it matters** — a fallback to a null
  state makes every later check look clean, losing the strong finding and
  reporting only the weak one.
- **First-match where a multimap was needed** — only the first eligible item
  compiles, or a repeated variable keeps only its last role, so a pattern
  licenses more than it checks.
- **A guard that assumes history.** "This is the only writer" does not entail
  "nothing removes it"; check both directions before compiling an obligation.
