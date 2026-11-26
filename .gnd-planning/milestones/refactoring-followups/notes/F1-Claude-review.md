The change does what it claims: the pool loader checks the on-disk byte count before it decodes anything, its work stays bounded, and the inputs and error messages it supported before are unchanged. I found no defects, only two style notes.

All five files matched the SHA-256 values in the brief, so I reviewed the named bytes.

## 1. Findings

No finding has an observable consequence. Two style notes:

- **S1 (style), `src/gnd/synth/poolfile.py:414`.** The message `"input: JSON input exceeds byte cap"` is written out by hand. It copies the text of `input_policy._text`'s `ValueError` rather than coming from that module. If `input_policy` rewords its message, pool messages and other consumers will differ. Nothing breaks today.
- **S2 (style), `poolfile.py:416`.** The `.replace("\r\n","\n").replace("\r","\n")` chain rebuilds the newline handling of Python's text reader. `io.TextIOWrapper(io.BytesIO(raw), encoding="utf-8").read()` would reuse the standard reader instead. I looked for an input where the two differ and found none (list in §2), so this is a second matcher for something the standard library already does, with no input that breaks it.

## 2. What I checked and found true

**C1: oversized pools raise `PoolValidationError` before decode, with bounded work.** I tried to break it with these inputs:
- **Exact limit:** a file of exactly `MAX_BYTES` (10 MiB, `{}` plus spaces) reaches the schema gate, `schema: $ — 'object_types' is a required property`. One byte more gives exactly `['input: JSON input exceeds byte cap']`.
- **Unbounded sources:** `/dev/zero` and a 4 GiB sparse file are each refused in about 0.0 s. Before this change, both would have been read in full.
- **Oversize checked first:** an oversized file of invalid UTF-8 is refused by the size check before decoding, both in the patched-reader test and in the 11 MiB all-spaces file, which is also malformed JSON.
- **The second size check in `input_policy`:** after strict UTF-8 decoding and newline conversion, the text is never longer than the raw bytes. That check therefore cannot fire with a different result.
- **Callers:** `synth/service.py:331` catches `PoolValidationError` and reports "pool rejected". Before this change an oversized pool raised a plain `ValueError` there and was reported as "could not be prepared". `measure/service.py:193` catches every exception, so it is unaffected.

**Supported inputs and messages unchanged.** I compared the old `Path.read_text(encoding="utf-8")` with the new decode-and-replace on these inputs, and each gave the same result:
- a UTF-8 BOM, which both keep;
- line-ending mixes: lone `\r`, `\r\r\n`, `\n\r\n…\r` and `\r\n\r`;
- multibyte text;
- a UTF-8-encoded surrogate, `\xed\xa0\x80`;
- `\xff` and a truncated multibyte sequence, `\xe2\x82`;
- NUL, U+2028 and U+0085.

`UnicodeDecodeError.start` and its message are identical at offsets 5, 100 000 and 3 000 000, so there is no chunk-offset drift.

**Other error types kept:**
- a missing file still raises `FileNotFoundError`;
- a directory still raises `IsADirectoryError`;
- `{` still raises `JSONDecodeError`;
- duplicate keys still give `['input: duplicate JSON key']`;
- 100-deep nesting still gives `['input: JSON depth exceeds cap']`.

**Tests:** the focused command from the spec gives `183 passed`. The CRLF boundary test does pin D1 (counting on-disk bytes): its one-over case shrinks to exactly the limit after newline conversion, so the old code would have admitted it. The `signal.alarm` subprocess test only works on POSIX systems, and CI runs only Ubuntu and macOS, so it is not a problem there.

## 3. What I could not check

- **Base run:** I did not run the new tests against the base commit. I worked out from the code that the old loader raises `ValueError` for these cases.
- **Ruff:** I did not run ruff.

VERDICT: APPROVE
