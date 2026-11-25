<!-- Edited by review_tool.py sanitize: 6 absolute path(s) replaced with <repo> or <home>. The reviewer's words are otherwise unchanged; run.json holds the SHA-256 of the original. -->
All supplied SHA-256 hashes matched. I found six reproducible defects.

1. **F1 — Escaped lone surrogates cause exit 70.** [physical_binding.py:139](<repo>/src/gnd/export/physical_binding.py:139) accepts this binding:

   ```json
   {"schema":"gnd-physical-binding/1","tables":{"t":{"columns":{"c":{"sql_type":"\ud800"}}}},"roles":{}}
   ```

   Exporting with the V1 model raises `UnicodeEncodeError` when encoding the field extension. I reproduced CLI exit **70** in both JSON and YAML formats. The exporter must serialize this safely or return a named binding refusal.

2. **F2 — An admitted identifier chain makes `bind` raise `RecursionError`.** [physical_binding.py:354](<repo>/src/gnd/export/physical_binding.py:354) recursively calculates identifier widths without bounding or eliminating recursion.

   Reproduction: generate entities `e0000` through `e1100`. Give the last a popular String reference; identify each preceding entity externally through two functional binaries, one to the next entity and one to a String value, with a confirmed alethic external uniqueness over their component roles. The resulting 1.16 MB model passes `load_model_bytes` and ontology projection. Binding it to `{"schema":"gnd-physical-binding/1","tables":{"t":{"columns":{"x":{}}}},"roles":{}}` raises `RecursionError` from `arity`, reached through `identifications`. Even an entirely unbound model triggers this failure.

3. **F3 — External uniqueness uses whole-fact placement instead of its referenced roles.** [physical_binding.py:545](<repo>/src/gnd/export/physical_binding.py:545) inherits a fact’s `spans-tables` reason before examining the external constraint’s actual columns.

   Reproduction: in V3, change the `state` role of both `state_in_country` and `state_has_code` to `["city.st_country_cd","city.st_cd"]`. Leave their component roles unchanged. External uniqueness `constraints/0` still references exactly `state.country_cd` and `state.state_cd`, the State table’s primary key. The exporter lists it as **`spans-tables`**, rather than `primary_key`. A further variant without that primary key also incorrectly omits the derived unique key.

4. **F4 — Foreign-key diagnostics depend on column member order.** [physical_binding.py:442](<repo>/src/gnd/export/physical_binding.py:442) validates groups in document order.

   Reproduction: declare destination columns `x,y,w`, with primary key `[x,y,w]`. In source column order `z,a`, let `z` reference `[x,y]` and `a` reference `[x,y,w]`. Both groups have one source column. The refusal reports “1 column(s) reference **2**”. Reversing only the source column members changes it to **3**. Sorted validation should consistently select `a`; output ordering can still follow document order.

5. **F5 — The SQL lexer accepts words without the required separating space.** [physical_binding.py:170](<repo>/src/gnd/export/physical_binding.py:170) resumes word scanning immediately after `)`.

   Executed examples: `sql_datatype("double(2)precision")` returns `Float`, and `sql_datatype("timestamp(6)with time zone")` returns `DateTimeTz`. Both violate the approved grammar’s space-separated words. They should leave `datatype` absent while retaining the raw SQL type.

6. **F6 — Schema diagnostics construct invalid JSON pointers and sort them incorrectly.** [physical_binding.py:133](<repo>/src/gnd/export/physical_binding.py:133) joins path components without escaping `/` and `~`.

   Reproduction: supply tables `a/b` and `a~b`, each with `"columns":{}`. The reader reports `/tables/a/b/columns`, which does not locate the offending member. Correct escaped pointers sort as `/tables/a~0b/columns`, then `/tables/a~1b/columns`; therefore the reported first violation is also wrong.

Checks that passed:

- **149 selected tests passed**, covering the approved binding outputs, pinned schemas, cross-references, normalization, type map and baseline.
- All **50 refusal rows**, covering 19 rule IDs, produced their expected refusals using in-memory file reads.
- All **910 wrong-shape probes** were either refused by `BindingError` or accepted harmlessly.
- Independently compared current code with `ba192972`: all five artifact hashes matched across **82 baseline runs**.
- Generated 900- and 4,500-fact-type binding runs listed every fact and constraint and did not invoke the Rmap.
- Matcher checks exercised dotted, quoted, Unicode and newline-containing identifiers through both column-reference forms; fullwidth and punctuated role names; and SQL parameter boundaries. Identifier lookup, quoting and role normalization passed; the SQL boundary failure is F5.

I could not run filesystem publication tests or the upstream oracle in this read-only sandbox. Byte-input probes substituted `BytesIO` at the file-opening boundary and exercised the real reader, binder and renderer. No files were changed.

VERDICT: CHANGES_REQUESTED