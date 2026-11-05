# Close fixes: independent re-review

One local reader, read-only, over the uncommitted close-fix diff (on top of
`2bc4047`). Verdict: approve-with-fixes. 196 tests passed on the diff.
Condensed by the coordinator from the reader's returned text; probes stayed in
scratch.

1. [medium] `_cmd_discover` raised an uncaught `DiscoveryDefect` when the
   other families' operations alone were over a cap (no type groups left to
   drop): traceback, exit 1, no report. Before the fix the proposal was
   written. -- fixed: without type groups the proposal is written as before;
   test `test_other_families_over_the_cap_still_write_their_proposal`.
2. [medium] `gnd compose` compared output paths textually; on a
   case-insensitive filesystem `--record MODEL.ORM.YAML` overwrote the model
   and `--record COMPOSITION/rec.json` wrote into DIR. -- fixed: files compared
   by identity (`samefile`, or case-folded name in the same directory);
   test `test_compose_compares_outputs_by_identity`.
3. [low] the instance-split refusal fires only when the value is listed as an
   instance; per-role renaming without instances may split a value across fact
   types; the message named "another fact type" though a ring role also
   counts. -- message fixed ("another role of that source"); per-role
   behaviour documented in composition.md; owner question CT-close-Q4.
4. [nit] the trim drops about 1/16 of the remaining groups per step, so it
   can drop more than needed. -- docs say "in steps"; accepted.
5. [nit] the umask was read per output. -- read once.

Held: no false split refusals on legitimate manifests (two fact types both
renamed; same value in a role of another object type; two sources); the
different-`to` check; canonical-record refusal does not affect api dicts,
`gnd compose` output, the example test or the docs runner; witness source id
pattern in io and both schema twins; result schema pinned to the witness
schema; `drop_last` keeps operations, proposals and group sizes aligned;
distinct-value counting; reading and digest as documented; read-failure
message; docs claims on `..` and `/tmp`.
