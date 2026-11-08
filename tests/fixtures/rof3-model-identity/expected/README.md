# ROF3 corpus answer key

The expected results for the cases in `../README.md`, kept apart so a reader
can work them out from the stories and the normative definition alone.

## Files

- `<case>.identity.json`: the canonical document, exactly the bytes that are
  hashed (one JSON line and a trailing newline).
- `<case>.digest`: `sha256:` and the hex digest of those bytes.
- `<case>.stdout.txt`: what `gnd validate <model> --identity` prints: the line
  `MODEL IDENTITY <digest> (identity_version <N>)`, then the document line.
  Exit 0.
- `<case>.legacy`: the existing `model_digest` (hex, Python `repr`), pinned
  because ROF3 must not change it (spec D6).
- `vectors.json`: per case, the model path, the identity and its version, or
  the refusal.

The `surrogate` case has no document, digest or stdout file. Its expected
result is a refusal with rule `model:identity-unrepresentable` and exit 3.
The runner pins the rule id and the exit, not the message wording.

## How it was written

`derive_vectors.py` loads each model with GND's own loader (the identity is
defined over the loaded model) and builds the envelope and the canonical bytes
itself from the definition, using only `json` and `hashlib`, not GND's
canonical helpers. As a cross-check, the existing helpers (`values.canonical`
with `artifacts.canonical_json_bytes`, and `values.reference_model_digest` for
version 1) were run over the same models and agreed on all nine digests. That
is the evidence that D3's byte form is the existing one. Run it from this
directory with the ROF3 base source importable.

Honest limits: the vectors cover the loaded model, so a caller who starts from
the YAML text needs GND's defaults (or the `--identity` output) to rebuild the
document. There are no astral-plane or control characters in any vector; the
normative text states those rules, and only the payload-level tests exercise
them.
