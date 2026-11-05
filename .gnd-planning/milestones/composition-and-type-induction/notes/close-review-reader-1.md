# Close reader 1: correctness of the anchor and composition core

Verdict: approve-with-fixes. (Returned as text; the reader could not write files.)

Holds: every source re-bound on check and the record re-derived and compared; row lineage through dedup and renaming; record value-free; bytes identical under PYTHONHASHSEED 1, 2, 3; exits 3 and 64 as documented; every-anchor rule over composed facts. 82 tests passed (test_composition, test_anchor_sidecar_v2, test_composition_example).

1. [major] composition.py:276-285 -- an instance-only renaming counts as used, so a renaming matching no fact row is accepted and can hide a mandatory violation (Ghost instance renamed to Acme Corp.; check pass=5 fail=0; per-fact record renamings unchanged).
2. [major] composition.py:233-241 -- instance renaming is inferred with setdefault (first wins): divergent `to` values for one (source, object type, from) are silently settled (P2), and an instance is rewritten while another fact type still uses the old value (P1), splitting an entity.
3. [minor] commands/checking.py:773-790 -- staging not all-or-nothing: --record an existing directory exits 74 after --out was already renamed into place; outputs left at mode 0600.
4. [minor] checking.py:757-761 -- --out/--record may name the model file and overwrite it.
5. [minor] anchors.py:161, api.py:943, checking_service.py:154 -- any `..` or symlinked ancestor (e.g. /tmp on macOS) is refused, reported as "invalid model"; docs mention only symlinked files.
6. [minor] composition.py:104-109 -- source ids differing only in case open one folder twice on a case-insensitive filesystem; lineage lists both.
7. [nit, hypothesis] the check path reads model_raw again after loading the model; a change in between would desynchronise digest and model.

_Condensed by the coordinator from the reader's returned text; the reader could not write files. Probes were kept in scratch and are not committed._
