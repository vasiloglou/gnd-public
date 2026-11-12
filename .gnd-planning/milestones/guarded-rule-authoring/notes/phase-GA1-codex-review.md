# GA1 independent diff review

Codex CLI gpt-6-sol, high effort, read-only, public candidate `9e2880b9`.
The response below is retained verbatim. One reviewer is one reviewer.

**Verdict: changes requested.** This is a static review of the supplied diff. I did not run commands or tests.

| Finding | Reproduction from the diff |
|---|---|
| **The scoped ordinary model retains fact-type-local guarded rules.** | Put a guarded constraint on a fact type alongside an ordinary mandatory constraint. `run_guarded_cases` recognizes the local guard (`fact_type is not None`) and refuses its pair, but `_ordinary_corpus` removes guarded constraints only from the top-level `constraints` list. The local guard remains in `ordinary/scoped.orm.yaml`, contrary to the approved scope, and can affect or prevent ordinary synthesis. |
| **The fresh root is exposed before the corpus is published.** | On commit, `_SynthCorpusTransaction` calls `final_root.mkdir()` before `os.replace(stage_root, final_root)`. A reader between those calls sees an existing, empty output root. This refutes the promised fresh-root atomic publication. |
| **The checker work preflight omits atom and absence consequents.** | `confirmation_work` adds consequent atoms only for `exists`. For an atom or absence rule, it charges antecedent joins but omits witness probes for each resulting binding. A collateral guard with many antecedent bindings and multiple witness rows can therefore enter checker confirmation under a charged “upper bound” that is lower than its possible join work. |

**Confirmed from the code:** proposed pairs have a positive independent antecedent count and receive checker confirmation of both target verdict and binding count before being saved. Deontic failure maps to `warning`; other non-pass findings are recorded. The route rejects an output root already present at transaction creation. The ordinary lane uses a private JSON sink, leaving the guarded response as the public JSON document.

Bounded search can leave a satisfiable rule unavailable; that is an allowed limitation when reported honestly. The explicit refusals for `exists` with `where` and reference populations are future feature scope, not defects identified here. I cannot confirm runtime behavior or test coverage from this review.