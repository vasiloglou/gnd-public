"""model id -> Python symbol: the ONE mapping, published (G-21).

**The hazard.** ``src/gnd/schema/orm-meta.schema.json``'s ``$defs.identifier``
is ``^[a-z][a-z0-9_]*$``, and ``object_type.id``, ``fact_type.id``,
``role.role_name`` and ``role.object_type`` all ``$ref`` it. Thirty-five Python
keywords match that pattern. A model declaring ``id: import`` with roles
``from`` and ``return`` passes ``gnd validate`` at exit 0 and ``gnd extract`` at
exit 0 — extract is immune because JSON keys are unconstrained — and naive
codegen then emits ``def import(from, return):``, a ``SyntaxError`` sitting on
the user's disk. ``tests/fixtures/models/keywords.orm.yaml`` is that model, made
a committed artifact.

GND has been bitten by this exact hazard once already, inside its own CLI:
``cli.py``'s ``--global`` flag cannot use argparse's derived attribute name
because ``global`` is a keyword.

**Suffix, do not refuse — and here is the alternative that was rejected.**
Appending ``_`` is PEP 8's convention for a name that clashes with a keyword,
and it keeps the mapping **total**: every valid ORM identifier has a Python
symbol, so no valid model becomes ungeneratable. Refusing is louder, and that
was its appeal, but it makes the mapping PARTIAL — and a partial mapping turns a
model the author just saw ``gnd validate`` accept at exit 0 into a codegen
failure for a reason nothing upstream showed them. Loudness is worth having
where the alternative is silent corruption; here the alternative is a correct,
conventional, mechanical rename, so total wins.

What is NOT total: a *collision*. Sanitizing ``import`` to ``import_`` collides
with a model that already declares ``import_``, and merging them would emit one
tool for two fact types with the loss invisible. :func:`symbol_table` refuses,
naming both source ids. That refusal is honest partiality — the model really
does contain two things that cannot both keep their name — and it is the one
place this module says no.

**No hand-maintained keyword list.** ``keyword.iskeyword`` and
``keyword.issoftkeyword`` come from the stdlib because the soft-keyword set
changes per Python version (``match``/``case`` arrived in 3.10, ``type`` in
3.12): a list written today is stale on the next upgrade, and stale in the
direction that emits invalid code. ``tests/test_codegen_identifiers.py`` walks
this module's AST and reds on any string literal that is a keyword.
"""

from __future__ import annotations

import keyword
import re
from collections.abc import Callable, Iterable

__all__ = [
    "KEYWORD_SUFFIX",
    "RESERVED_IDENTIFIERS",
    "IdentifierError",
    "module_name",
    "python_symbol",
    "smoke_discriminator",
    "symbol_table",
    "tool_symbol",
]

#: The PEP 8 disambiguating suffix. Published as DATA rather than inlined at the
#: two append sites (``projection.py:43``'s publish-the-table discipline) so a
#: reviewer reads the convention once, and so the collision message and the
#: emitter cannot drift from what the sanitizer actually appends.
KEYWORD_SUFFIX = "_"

#: Names the EMITTED modules bind themselves, so a model id cannot shadow the
#: generated code's own machinery. Each entry earns its place:
#:
#: * ``annotations`` — bound by ``from __future__ import annotations``, which
#:   every emitted module carries; a fact type named ``annotations`` would
#:   rebind the future import's name at module scope.
#: * ``tools`` — the emitted tools module's own basename, and the name the
#:   generated ``SKILL.md`` and the package ``__init__`` import through.
#: * ``gnd`` — the shipped package the generated project's verifier half calls;
#:   a module named ``gnd`` inside a generated project shadows it on the path.
#:
#: Not a security boundary and not a style list: strictly the names whose
#: shadowing would change the MEANING of emitted code. Keywords are handled by
#: the stdlib and are deliberately absent here.
RESERVED_IDENTIFIERS = frozenset({"annotations", "tools", "gnd"})

#: Defensive bound on the suffix loop. Unreachable — the reserved set and the
#: keyword sets are finite and none of their members ends in ``_`` — but a
#: silent infinite loop inside an emitter is a worse failure than a raise.
_MAX_SUFFIXES = 8


class IdentifierError(ValueError):
    """A model id could not be mapped to a distinct, valid Python symbol.

    Raised for a sanitization COLLISION (two ids, one symbol) and for input the
    meta-schema could not have produced. Both are refusals rather than
    best-effort renames: an emitter that silently merged two fact types would
    produce a project that passes every syntactic check while missing a tool,
    and conformance assertion #3 would then red on output the user cannot
    diagnose (the refuse-never-default register of
    ``projection.ProjectionGateError``).
    """


def _is_reserved(symbol: str) -> bool:
    return (
        keyword.iskeyword(symbol)
        or keyword.issoftkeyword(symbol)
        or symbol in RESERVED_IDENTIFIERS
    )


def python_symbol(model_id: str) -> str:
    """The Python symbol for ``model_id`` — total over valid ORM identifiers.

    Unchanged when the id is already a safe identifier; suffixed with
    :data:`KEYWORD_SUFFIX` while it is a hard keyword, a soft keyword, or on
    :data:`RESERVED_IDENTIFIERS`. The result always satisfies
    ``str.isidentifier()`` and is never a keyword, and the function is a fixed
    point on its own output — a symbol read back out of emitted code and
    re-sanitized by conformance assertion #3 must not drift.

    Input the meta-schema cannot produce (spaces, a leading digit, the empty
    string) raises :class:`IdentifierError` rather than being mangled into
    something plausible. That path is a caller bug inside GND, not a user's
    model, and it fails closed.
    """
    symbol = str(model_id)
    if not symbol.isidentifier():
        raise IdentifierError(
            f"{symbol!r} is not a Python identifier and no valid ORM model can "
            f"contain it (the meta-schema's $defs.identifier is "
            f"^[a-z][a-z0-9_]*$); refusing to invent a symbol for it"
        )
    for _ in range(_MAX_SUFFIXES):
        if not _is_reserved(symbol):
            return symbol
        symbol += KEYWORD_SUFFIX
    raise IdentifierError(
        f"{model_id!r} did not escape the reserved set after {_MAX_SUFFIXES} "
        f"suffixes — the reserved table is self-referential"
    )


def tool_symbol(fact_type_id: str) -> str:
    """The name of the emitted tool function for ``fact_type_id``.

    **One published mapping, two callers.** This function is used by the emitter
    in :mod:`gnd.codegen.emit` AND by conformance assertion #3 (plan 03-06),
    which recomputes the expected tool surface FROM the model to prove the
    generator emitted something model-relative rather than well-formed nothing.
    If those two ever grow separate copies they will disagree, and #3 will red
    on correct output — a gate that fails on the truth is worse than no gate.
    Sharing the function is the point (``install.py``'s ``REMOVABLE_STATES``
    comment is the shape this follows).

    It composes :func:`python_symbol` rather than re-deriving the sanitization,
    and exists as a separate published name so that a later decision to prefix
    tool functions changes exactly one place — while assertion #3, which imports
    *this* name, follows automatically.
    """
    return python_symbol(fact_type_id)


def module_name(stem: str) -> str:
    """The module/package basename for a model FILENAME stem.

    Separately named for the same reason as :func:`tool_symbol` — the call site
    is different and a future divergence (a ``_pkg`` suffix, say) should land in
    one function rather than in a walk — but it also does one thing
    :func:`python_symbol` deliberately will not.

    A stem is not a model id. It comes from ``paths.slug`` over a FILENAME, and
    ``slug``'s output alphabet is ``[a-z0-9._-]``, so ``my-model.orm.yaml``
    yields ``my-model`` — a perfectly reasonable filename and not a Python
    identifier. :func:`python_symbol` refuses that input on purpose (no valid
    ORM *id* can look like it), so refusing here too would make a legitimately
    named model file ungeneratable for a reason the author cannot see in
    ``gnd validate``'s exit 0 — the exact partiality the suffix decision was
    taken to avoid. Filename-space characters are therefore folded to ``_``
    first, and a leading digit gets a prefix, before the shared mapping runs.
    """
    folded = "".join(
        character if character.isalnum() or character == "_" else "_"
        for character in str(stem)
    )
    if not folded or folded[0].isdigit():
        folded = f"m_{folded}"
    return python_symbol(folded)


_DISCRIMINATOR_VERSION_SUFFIX = re.compile(r"@[^:@]*$")
_DISCRIMINATOR_UNSAFE = re.compile(r"[^a-z0-9_]")


def smoke_discriminator(model_id: object, *, package: str) -> str:
    """The project-scoped smoke-basename discriminator (v5.1 D-P1.8, D-P1.9).

    The slug of ``model_id``: a trailing ``@<version>`` stripped first, so a
    model evolution never re-stales a create-once file; then the last
    ``:``-separated segment, lowercased, with every character outside
    ``[a-z0-9_]`` folded to ``_``.

    ``model_id`` is OPTIONAL by D-06, and a model that ``gnd validate`` accepts
    must never become ungeneratable (the partiality :func:`module_name`
    documents). So a model that declares none — or one whose id slugs to
    nothing — keeps the PRE-PHASE rule and derives from ``package``. That
    leaves exactly today's limitation for those projects, unchanged rather than
    newly introduced: two ``model_id``-less projects still collide, and the
    create-once refusal still protects both trees. Declaring a ``model_id`` is
    what buys the discrimination.
    """
    tail = _DISCRIMINATOR_VERSION_SUFFIX.sub("", str(model_id or "")).rsplit(":", 1)[-1]
    slug = _DISCRIMINATOR_UNSAFE.sub("_", tail.lower())
    return slug or package


def symbol_table(
    model_ids: Iterable[str],
    *,
    kind: str,
    symbol: Callable[[str], str] = python_symbol,
) -> dict[str, str]:
    """``{model_id: python_symbol}`` in DECLARATION ORDER, collisions refused.

    ``kind`` names what is being mapped ("fact type", "role") and appears in the
    refusal so the reader knows which part of the model to fix. ``symbol`` is
    the per-id mapping — :func:`python_symbol` by default,
    :func:`tool_symbol` for the fact-type table — so there is ONE bulk
    implementation parameterized by the mapping, never a second sanitization
    walk that could disagree with the published function.

    Order is preserved, not sorted: emission order is declaration order, and a
    sort here would make the emitted file's function order depend on a detail
    the model author never chose.

    Raises :class:`IdentifierError` when two distinct ids sanitize to one
    symbol. Both ids appear in the message, ``repr``-quoted, because the
    interesting collision is ``import`` against ``import_`` and an unquoted
    rendering of the first is a substring of the second.
    """
    table: dict[str, str] = {}
    origin: dict[str, str] = {}
    for raw in model_ids:
        model_id = str(raw)
        mapped = symbol(model_id)
        previous = origin.get(mapped)
        if previous is not None and previous != model_id:
            raise IdentifierError(
                f"the {kind} ids {previous!r} and {model_id!r} both sanitize to "
                f"the Python symbol {mapped!r}; emitting one symbol for two "
                f"{kind}s would silently drop one of them, so codegen refuses "
                f"rather than merging (rename one in the model)"
            )
        origin[mapped] = model_id
        table[model_id] = mapped
    return table
