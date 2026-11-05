# Close reader 2: witness lineage and the discover fact-type family

Verdict: approve-with-fixes. (Returned as text.) v1 witness parity byte-identical to a2e44f8; v2 replay table as contracted (forged/reordered sources 1, missing record 3 composition-required, v1+record 3 binding-stale, wrong digest 3, empty/negative 3 input-invalid, cosmetic model edit 3 -- answers CT-Q2); schema twins identical; disclosure per CT-D13 (a); deterministic; additive preview 0 on S1-S5, S8.

1. [major] types.py:167-172, service.py:284-287 -- the budget estimate (3x compact JSON, no operation envelope) underestimates the indent=2 file: 3,500 attributes x 20 entities wrote a 12.7 MB proposal that preview refuses over the 10 MiB cap.
2. [minor] types.py:155 -- two generic fact types yield identical readings and signatures; proposals from one run never shape-match each other.
3. [minor] types.py:123-127 -- one exact duplicate row marks the group multi_valued; count distinct values per entity.
4. [nit] io.py:239-246, view.py -- v2 `sources` strings unvalidated; a hand-edited certificate prints any string in customer view.
5. [nit] service.py:279-292 -- the family's row visits are outside discover's work ceiling.
6. [hypothesis] composed replay hashes and parses the files in two reads.

_Condensed by the coordinator from the reader's returned text; the reader could not write files. Probes were kept in scratch and are not committed._
