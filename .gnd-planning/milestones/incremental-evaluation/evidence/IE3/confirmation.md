Retained output; edited only to replace machine repository/user paths.
Original SHA256: 5c390efe6408dc802f0c390819bf5928d7a1643de51e3e1952b1b4971cffaeef

One remaining static correctness finding:

- **[P2] String-resolved registry hooks bypass configuration capture.** [correspondence.py:1007](<REPO>/src/gnd/correspondence.py:1007) captures defaults and closures only when the registry field directly contains a function. String hooks resolve through their defining namespace; `homes` binds those functions by identity/code, leaving configuration changes invisible.

  **Concrete falsifier:** adapt the new frequency regression to install `evaluator(constraint, snapshot, state=1)` as `semantic_spec._family_result_frequency`, leaving `FAMILIES` unchanged. Warm the session, change `evaluator.__defaults__` to `(0,)`, then compare session and fresh checks. The signature remains unchanged, permitting cached acceptance while fresh evaluation reports violation. This falsifier was **not executed**.

  Capture configuration from the resolved hook using its actual lookup namespace, with fresh fallback for unsupported captures.

The direct-callable repair addresses the original reproduced route on inspection. The new declared-post and reference controls discriminate forwarding, closing the previous coverage gap. One limit: `dataclasses.replace(references, ...)` creates an unregistered context, so refusal occurs at context identity validation before the digest comparison; it does not isolate that digest guard.

No additional actionable defect found in the inspected evaluator extraction, receipt detachment, facade forwarding, or refactoring changes against `46c76ad`. This was read-only static inspection: no tests, agents, network, credentials, or writes, and no certification, timing, or installed-assurance claim.