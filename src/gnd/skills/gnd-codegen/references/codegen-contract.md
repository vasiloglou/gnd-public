# The codegen contract

Everything [`../SKILL.md`](../SKILL.md) states as a rule, with the field tables,
the state machine, and the failure semantics behind it. Read this once before
your first `gnd codegen` run.

## 1. Ownership: a "region" is a FILE

There are no in-file merge markers, and there never will be in v1. Ownership is
per file, and the reason is normative rather than aesthetic: GND puts
**round-trip engineering** out of scope by name. Once a generator has to preserve
your edits *inside* a file it regenerates, it is merging, and merging is the
thing that was ruled out. File granularity also makes the review trivial — the
diff of a regeneration is a file diff.

| Ownership | Means | Digest-gated? | Regeneration |
|---|---|---|---|
| `derived` | emitted by CODE from the model | yes | rewritten whenever it is stale |
| `extension` | authored by a human or an LLM | **no** | created once, then never touched |

**`derived` means code-emitted, and the boundary falls out of the digest rather
than out of taste.** An LLM-authored file is not byte-reproducible: ask for it
twice and the bytes differ. So it cannot carry a meaningful digest, and calling
it derived would force one of two bad outcomes — the conformance check
false-fails on every regeneration, or the digest is quietly dropped "for prose
files" and the gate is weakened to nothing over exactly the files nobody is
watching.

**`pyproject.toml` is the one file where the two rules genuinely conflict.**
"Derived files are rewritten" and "regeneration never overwrites an extension
file" cannot both hold for it, because you are explicitly allowed to add a
provider client and that lands in its dependencies. **Extension wins**: a lost
dependency list is unrecoverable, while a stale generated skeleton is visible and
one edit from being fixed.

`architecture.contract.yaml` follows the same extension rule. Its fields,
validation order, substitutions, and limits have one normative home:
[`architecture-contract.md`](architecture-contract.md).

## 2. The emitted layout

```
my-project/
  .gnd-codegen.json                          the record
  <package>/__init__.py                      derived
  <package>/tools.py                         derived
  artifacts/<stem>.projection.schema.json    derived
  artifacts/<stem>.verbalization.txt         derived
  artifacts/<stem>.applicable.json           derived
  artifacts/<stem>.artifacts.json            derived
  SKILL.md                                   derived
  architecture.contract.yaml                 EXTENSION — yours
  test_architecture_smoke_<package>.py       EXTENSION — yours
  references/<skill>-notes.md                EXTENSION — yours
  pyproject.toml                             EXTENSION — yours
```

`<package>` is the model's filename stem folded into a legal Python module name;
`<stem>` is the same stem slugged. The four `artifacts/` files are
**byte-identical** to what `gnd extract MODEL --out DIR` produces, which is why
the generated project's verifier half is the shipped `gnd verify` with no
adapter — see [`../../gnd-extract/references/extraction-contract.md`](../../gnd-extract/references/extraction-contract.md)
for what each of the four gives a reader.

### `tools.py`

One module-level constructor function per **constructor-bearing** fact type.
Asserted fact types are constructor-bearing. A fact type with the legacy string
`derivation_rule` also retains its constructor for exact pre-v5 compatibility;
the string remains opaque and unchecked. A fact type with a structured
`derivation_rule` is computed and emits **no constructor**: the population
claims its extension and `gnd check`/`gnd verify` verifies that claim. The
emitter and conformance use the same published structured-rule predicate.

For each emitted constructor, the function name and every parameter name come
from the published model-id → Python-symbol mapping, so a model whose ids are
Python keywords still emits code that parses:

```python
def import_(from_, return_):
    '''Class imports Lambda

    Derived from fact type 'import'. Roles, in declared order:
      - from: Class (String)
      - return: Lambda (Integer)
    '''
    return {'from': from_, 'return': return_}
```

Note the **return value keys are the model's RAW role names**, not the sanitized
Python parameter names. JSON keys are unconstrained and the projection schema
enumerates the raw names, so sanitizing them would emit a fact the checker
rejects.

## 3. The six file states

Every path in the layout is classified before anything is written. `gnd codegen`
performs no write it has not classified first.

| State | Reached when | Written without `--force`? | With `--force`? |
|---|---|---|---|
| `create` | nothing is there and nothing records it | yes | yes |
| `current` | the bytes are what this run would emit | no write needed | no write needed |
| `stale` | the bytes are what the record holds, and the emission moved on | yes | yes |
| `missing` | the record holds it and the disk does not | yes (restored) | yes |
| `modified` | the bytes match NEITHER the record nor this emission | **no — refused** | yes, if derived |
| `collided` | something occupies the path and no record claims it | **no — refused** | yes, if derived |

**An `extension` file is writable in `create` and in no other state, ever, with
or without `--force`.** That rule cuts across the table above and it is
unconditional.

**A refused file keeps its previous record entry.** If your hand edit is refused,
the manifest is *not* updated to the edited bytes. Recording them would make the
next run see the file as `stale` and rewrite it — destroying the edit one run
later, through the mechanism that refused to destroy it now.

**Nothing is ever deleted.** If a model rename changes the artifact stem, the old
files are reported as no longer emitted and left in place; codegen does not take
on the right to remove files from a directory you own.

**Only the layout above is ever classified or touched.** A file you keep beside
your generated project at any other path is invisible to codegen, with or
without `--force`.

## 4. Idempotence, and how to check it yourself

> A second run over an unchanged model performs **zero writes** and leaves
> **identical hashes**.

Both halves, not either. You can verify it directly:

```
gnd codegen model.orm.yaml --out my-project/
find my-project -type f -exec shasum -a 256 {} \; | sort > before.txt
gnd codegen model.orm.yaml --out my-project/     # prints "0 written"
find my-project -type f -exec shasum -a 256 {} \; | sort > after.txt
diff before.txt after.txt                        # empty
```

The command reports the write count; the digests confirm the bytes. A run that
rewrote every file with identical bytes would pass the digest check alone, and a
run that rewrote everything from a changed model would pass the count alone.

## 5. Exit bands

| Exit | Meaning | What to do |
|---|---|---|
| 0 | the tree was written, or was already current | nothing |
| 3 | the model did not load, two ids sanitize to one Python symbol, or the existing `.gnd-codegen.json` is unreadable | fix the model, or the record |
| 11 | a write was **refused** and nothing was destroyed | move the edit into an extension file, or re-run with `--force` |
| 64 | usage error | check the arguments |
| 70 | an emitter invariant broke over an already-valid model | this is a GND bug; report it with the model |
| 74 | the output path was refused or is unwritable | check the path and permissions |

Band 11 is not new and does not mean "failure". It has meant *"an unmanaged file
blocked a write; nothing was destroyed"* since `gnd install`, and it means
exactly that here.

Report exit codes **verbatim**. A band is a fact about what happened, not an
adjective to be softened.

## 6. What a green conformance does and does not say

When the conformance check passes, two things are established:

1. **Integrity** — every derived file's bytes hash to what the record holds.
2. **Currency** — the model digest the record holds equals the model's digest now.

Neither of those is a claim about correctness, and neither is a claim of any kind
about your extension files. **Extension code is unexamined by construction.** An
extension file may contradict the model freely and conformance will stay green;
within GND's claims, what exercises it is `gnd verify` over what the agent actually
produced — see [`../../gnd-orm-core/references/population-format.md`](../../gnd-orm-core/references/population-format.md)
for the shape that command reads — and that is a population claim only: your
dependency/build checks, focused tests, and smoke run remain the conventional
verification of extension code, and GND neither generates nor gates them.

Two further bounds, stated because a limit that lives only in prose is one skim
away from not existing:

- **The record cannot record itself.** A digest comparison detects a unilateral
  edit to a derived file, not a co-edit of that file together with its entry.
  This is an integrity bound, not tamper evidence.
- **The banner is corroboration, not a gate.** `# Code generated by gnd codegen
  …; DO NOT EDIT.` can be forged, and nothing treats it as evidence.

## 7. Offline by construction

The generated project imports no provider SDK and no network library, and the
emitter enforces that on its own output before any byte reaches disk. So a fresh
generated project is CI-runnable with zero network and no API key.

That rule binds **GND's package and the template GND emits** — not your project.
Adding a provider client to your own generated project is allowed, is your
extension, and lands in `pyproject.toml`. See §1 for why that file is an
extension.
