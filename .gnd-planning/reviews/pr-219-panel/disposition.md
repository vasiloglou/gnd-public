# Disposition of the PR 219 panel

Run `f4c54e22117b22302b994336dc0a3ac0543421febcef902b0d2668aa46cb45db`,
synthesis `621f2613ecf00f854226a3ffa14ca2662c8a1753eea96c2e1e0542a857ec9c48`.
Every retained concern was checked against the code at `17d7a531` before its
fix. All nine fixes of the plan are applied in `44de695c`; those repaired
bytes have no panel opinion of their own.

| Concern | Checked | Disposition |
|---|---|---|
| claude:rules-route-has-no-temporal-refusal, kimi:roadmap-irr-d3-temporal-refusal-rules-mode | yes: `emit.py:35-36` refuses temporal models in `render_pyrel` only; `render_pyrel_rules` (`emit.py:60-64`) lowers `date_add`/`date_sub` (`pyrel_rules.py:357`) | fixed: IR3 criteria per mode, D2 and D3 restated, RP5 expects the temporal root to export under `--rules lqp` |
| claude:quantity-fixture-value-family | yes: `time.orm.yaml:22-37` holds two `role_ref` value constraints; `pyrel_rules.py:864` and `:473` refuse them | fixed: new RP4, owner decision D3; end to end renumbered RP5 |
| claude:rp1-require-not-enforced-offline, codex:rp1-require-enforcement | yes: lqp is compile-only offline; DuckDB denial rows are checked only in the opt-in `pyrel_oracle` lane (`pyproject.toml` addopts) | fixed: RP1 criteria name the default-lane compile check, the `pyrel_oracle` denial-row oracle and the opt-in live run |
| claude:rp1-cites-wrong-refusal-site | yes: the top-level branch at `pyrel_rules.py:882` | fixed: RP1 cites `:855` and `:882`; external frequency out of scope at `:596`, `:860`, `:882` |
| claude:lh2-replay-root-already-exists, codex:lh-live-inputs | yes: `replay(folder, ...)` at `reading.py:574`; `ReadingInputs` pins saved responses (`:72-75`, `:113`) and loads the packaged vocabulary (`:135`) | fixed: LH1-LH2 restated around the input binding, with a caller corpus and vocabulary criterion |
| claude:lh-carryover-not-discharged | yes: literature-depth close row "Host-scale reading and extraction" names a corpus and provider budget | fixed: the outline takes the interface half; the run stays with its assigned owner |
| claude:ir3-staleness-untested | yes: the default program embeds its model text (`emit.py:53-55`) | fixed: IR3 records include digests; post-export staleness detection is out of scope |
| claude:d12-one-home-not-updated, qwen:roadmap-d12-identifier-unattributed | yes: `provenance-and-modality.md:209` is D-12's one home; `evolution-contract.md:279-280` restates it | fixed: the roadmap row links the home; the maintenance note names both files |
| claude:order-statement-mismatch | yes | fixed: one dependency statement in both files; RP5 needs IR3 merged |
| qwen:roadmap-milestone3-independence-vs-rp4 | yes, the relation was unstated | fixed: RP5 exports packaged models and uses no literature-host-interfaces deliverable |
| qwen:roadmap-order0-blocks-217-without-rationale | yes | fixed: the maintenance pass is ordered "any time"; no milestone waits for its ruling |
| qwen:roadmap-040-and-ga1-premises-unlinked | yes: unlinked; the top "Current status" still named 0.1.0 | fixed: links to the 0.4.0 close and the GA1 record; a pointer under "Current status" |
| qwen:roadmap-row0-overlaps-approved-mg-scope | partly: Qwen saw only PROJECT.md. model-growth-guardrails has a close record (`008-milestone-close.md`), so no approved work is unfinished, but PROJECT.md still called it planned | fixed: the roadmap says every earlier planned milestone has closed |
| qwen:roadmap-partition-not-traceable-from-table | yes | fixed: each outline's §1 maps requests to phases; the roadmap states #214's four items |

## Evidence boundary

- The raw run directory is held outside history, as the release-0.4.0 close
  panel did: two of its digest-bound streams contain this machine's home
  path, and editing them would break the run's integrity check. The request,
  synthesis and report committed here bind it by digest.
- Qwen received only `PROJECT.md` inline (its seat makes no tool calls), so
  its concerns rest on that file alone. Kimi's response was retained as
  incomplete (one preamble line; nothing dropped).
