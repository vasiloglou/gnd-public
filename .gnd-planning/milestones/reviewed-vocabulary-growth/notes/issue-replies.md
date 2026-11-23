# Drafted replies to issues 221, 222 and 218

Drafted by VG5 on 2026-11-23 for the owner to post (plan §5); nothing here
has been posted. Each reply names the pull request that carries the change.
None of them is released: 0.4.0 behaves as the issue describes until the
next release.

## Issue 221: `gnd check` is superlinear in the number of object types

Thank you for the measurements. `gnd check` no longer rebuilds its type
maps once per object type: the checker reads per-model tables built once
(pull request 239). On the interop example with 1,000 extra object types it
now takes under 1.2 s for each of five shapes we measured (unused value
types, entities with their own or a shared reference value type, a subtype
tree, and value types with as many fact types), where 0.4.0 took between
2.4 s and over two minutes; doubling the extra types costs about 2.1 to
2.2 times. Reports are unchanged. `gnd judgments check` and `gnd verify`
gain the same. One shape stays slow: a single subtype chain hundreds of
types deep (44.6 s at 800), whose cost is in reference resolution, which the
loader shares; it is recorded as a follow-up.

The change is on `main` once pull request 239 merges and is not in a
release yet.

## Issue 222: unattended growth cannot start from a reviewed vocabulary

An unattended root can now include an owner-reviewed model (pull request
240):

- The included elements keep their own source, status and modality and are
  exempt from the unattended rules U2 to U6. An unconfirmed inferred
  `alethic` claim inside an include is still refused (U8), and a span an
  included element carries over one of the root's documents is still
  checked and counted.
- Everything the root owns keeps every rule, including constraints it
  attaches to an included fact type.
- `gnd validate` prints one `INCLUDE` line per include, naming its pin and
  what it carries, and diagnostics on included elements carry the
  `includes[ID]:` prefix.
- Case 3: a root that includes a reviewed model and holds nothing of its own
  may omit its documents; the first `gnd evolve` round declares one.
- Included elements stay read-only to `gnd evolve`, and a growth round
  cannot re-pin an include of an unattended root.

"Unattended source" in `representation-format.md` states the rule, and
`unattended-growth.md` gains "Starting from a reviewed vocabulary". The
packaged example `src/gnd/examples/seeded_growth/` runs your path: a seed,
an empty root, two rounds, then validate, check and judgments check. Your
imported, proposed, deontic packaging still works and is described there as
the alternative when a vocabulary cannot be included.

What GND cannot check is who reviewed the included file: it checks the
bytes against the root's pin and that the file is a valid model. The page
says so.

On `main` once pull request 240 merges; not released.

## Issue 218: `gnd evolve` refuses the sources the growth guide asks for

Rule D-12 now admits a new `sample` constraint (row evidence) and a new
`common-sense` constraint (library evidence) when it is `proposed` and
`deontic`, exactly as `unattended-growth.md` tells a host to write them
(pull request 240). With `confirmed` or `alethic` it is refused by name,
exit 3; on an unattended model U2 or U8 refuses it first. The D-12 section
of `provenance-and-modality.md` and the evolution contract list the two
rules, and the growth guide is unchanged because it already said this.

On `main` once pull request 240 merges; not released.
