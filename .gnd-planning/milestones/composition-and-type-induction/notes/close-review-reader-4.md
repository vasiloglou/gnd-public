# Close reader 4: compatibility, architecture, docs vs behaviour

Verdict: approve-with-fixes. (Returned as text.) 332 + 367 tests passed; CLI exits, refusals, disclosure table, layering (allow_list 0), skills and release notes consistent; how-to outputs reproduce.

F1 (low-medium) src/gnd/schema/witness-result.schema.json certificate version const 1; api.witness(composition=...) result fails it (1 error); no test references the file.
F2 (low) record identity: check reports canonical-bytes record_sha256, witness binds raw-bytes composition_sha256; a re-indented record passes check but a witness over it is binding-stale against the original (CT-R4).
F3 (low) discover.md says attribute_sha256 is the value's SHA-256; types.py hashes repr((type name, value)): not recomputable, a second hash form (CT-R4).
F4 (low) python-api.md:69-70 check() signature lacks composition/sources and exclusions; no v1/v2 sidecar sentence (plan §5).
Nit compose-documents.md "values stay in the populations, where disclosure mode governs them" misleading: compose is every-mode.

_Condensed by the coordinator from the reader's returned text; the reader could not write files. Probes were kept in scratch and are not committed._
