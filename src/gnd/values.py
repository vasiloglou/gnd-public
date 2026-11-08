"""RF3 shared dependency home; algorithms retain predecessor semantics."""
from __future__ import annotations

from collections.abc import Iterable
from collections.abc import Set as AbstractSet
from typing import Any, Literal


def _identity_key(value: Any) -> tuple[Any, ...]:
    """Canonical ORM scalar/tuple identity, independent of Python coercions.

    Booleans are a separate scalar domain from numbers even though Python makes
    ``True == 1`` and gives them the same hash. Integers and floats share the
    numeric domain because Float/Number roles deliberately accept either JSON
    rendering (``1`` and ``1.0``).
    """
    if isinstance(value, bool):
        return ("boolean", value)
    if isinstance(value, (int, float)):
        return ("number", value)
    if isinstance(value, str):
        return ("string", value)
    if value is None:
        return ("null",)
    if isinstance(value, tuple):
        return ("tuple", *(_identity_key(item) for item in value))
    return (f"python:{type(value).__qualname__}", repr(value))


class _IdentitySet(AbstractSet[Any]):
    """Set semantics over :func:`_identity_key`, yielding original values."""

    def __init__(self, values: Iterable[Any] = ()):
        self._values = {_identity_key(value): value for value in values}

    def __contains__(self, value: object) -> bool:
        return _identity_key(value) in self._values

    def __iter__(self):
        return iter(self._values.values())

    def __len__(self) -> int:
        return len(self._values)


_INVALID_LITERAL = object()


def _literal(operand: Any, primitive: str | None, *, legacy: bool) -> Any:
    """Interpret a literal in the compared role's declared primitive domain."""
    if primitive in ("String", "Binary", "Date", "DateTime"):
        return operand if isinstance(operand, str) else _INVALID_LITERAL
    if primitive == "Boolean":
        if isinstance(operand, bool):
            return operand
        if legacy and isinstance(operand, str) and operand.lower() in ("true", "false"):
            return operand.lower() == "true"
        return _INVALID_LITERAL
    if primitive == "Integer":
        if isinstance(operand, int) and not isinstance(operand, bool):
            return operand
        if legacy and isinstance(operand, str):
            try:
                return int(operand)
            except ValueError:
                return _INVALID_LITERAL
        return _INVALID_LITERAL
    if primitive in ("Float", "Number"):
        if isinstance(operand, (int, float)) and not isinstance(operand, bool):
            return operand
        if legacy and isinstance(operand, str):
            try:
                return float(operand)
            except ValueError:
                return _INVALID_LITERAL
        return _INVALID_LITERAL
    return _INVALID_LITERAL


INVALID_LITERAL = _INVALID_LITERAL
IdentitySet = _IdentitySet
identity_key = _identity_key
literal = _literal


import datetime as _datetime

from gnd import artifacts
from gnd.errors import TransitionLoadError, ValidationIssue

_ISO_TYPES = (_datetime.datetime, _datetime.date, _datetime.time)


def _refuse(path: str, message: str, rule_id: str, supplied: dict[str, Any] | None = None):
    raise TransitionLoadError(
        [ValidationIssue(path=path, message=message, rule_id=rule_id)],
        supplied=supplied,
    )


def _canonical(value: Any, path: str) -> Any:
    """Everything JSON can carry, unchanged; dates as ISO text; nothing else.

    Totality belongs to the function (design rule 1). ``json.dumps`` refuses the
    ``datetime.date`` the YAML loader returns for an unquoted ISO date, and a
    model carrying one in a provenance note VALIDATES AT EXIT 0 -- so the
    digest, which every steps.json is required to carry, would raise an
    uncaught TypeError on a legal model and no walk against it could be
    authored. Two consequences, both deliberate:

    * quoted and unquoted spellings of one date produce the SAME digest, so the
      value identifies operations up to scalar spelling, and re-quoting a
      comment does not invalidate existing steps files;
    * anything outside the closed set is REFUSED with a rule id rather than
      crashing. Every input gets an answer, including "no".
    """
    if isinstance(value, dict):
        for key in value:
            if not isinstance(key, str):
                _refuse(
                    path,
                    f"mapping key {key!r} is a {type(key).__name__}, not a string; "
                    f"quote it in the model. Coercing it would let two different "
                    f"sections hash identically",
                    "transition:operations-digest-unrepresentable",
                )
        return {str(k): _canonical(v, f"{path}.{k}") for k, v in value.items()}
    if isinstance(value, list):
        return [_canonical(v, f"{path}[{i}]") for i, v in enumerate(value)]
    if isinstance(value, bool) or value is None or isinstance(value, (str, int, float)):
        return value
    if isinstance(value, _ISO_TYPES):
        return value.isoformat()
    _refuse(
        path,
        f"value of type '{type(value).__name__}' cannot be represented in the "
        f"operations digest; quote it in the model or remove it",
        "transition:operations-digest-unrepresentable",
    )
    return None  # pragma: no cover - _refuse always raises


ISO_TYPES = _ISO_TYPES
canonical = _canonical
refuse = _refuse


import hashlib


def _content_digest(population: Population) -> str:
    """A stable digest of everything layer 2 validated and the checker reads.

    ``warnings`` is excluded deliberately: it is layer 2's own OUTPUT, written
    onto the population after validation ran, and no checker verdict depends on
    it. Every other field is included, because every other field is either
    validated by layer 2 (``facts``, ``instances``, ``covers``, ``model_id``) or
    reported verbatim (``model``, ``source``, ``label``).

    ``repr`` rather than ``json.dumps`` because it is TOTAL: ``facts`` values are
    ``Any``, so a population may legitimately carry a value ``json.dumps``
    refuses (and ``sort_keys=True`` additionally raises on mixed-type nested
    keys, which WR-02 shows a population can supply). A digest that raises on
    hostile input would convert the guard into a denial of service. ``repr`` of
    a dict preserves insertion order, so re-ordering counts as mutation — the
    conservative direction.
    """
    payload = population.model_dump(exclude={"warnings"})
    # Keep the historical v1 marker byte-identical while binding v2's changed
    # role-value grammar to the validation stamp.
    if population.format_version != 1:
        payload["format_version"] = population.format_version
    return hashlib.sha256(repr(payload).encode("utf-8", "surrogatepass")).hexdigest()


MODEL_DIGEST_EXCLUDED_FIELDS = frozenset({"warnings", "operations"})


def _model_digest(model: Model) -> str:
    """Stable digest of model content that layer 2 validated/checker reads.

    Everything outside :data:`MODEL_DIGEST_EXCLUDED_FIELDS` is included, so
    nested mutation invalidates the population's marker even when the same Model
    object is retained.
    """
    if model.reference_populations:
        return reference_model_digest(model).removeprefix("sha256:")
    payload = model.model_dump(
        exclude=set(MODEL_DIGEST_EXCLUDED_FIELDS) | {"reference_populations"}
    )
    return hashlib.sha256(repr(payload).encode("utf-8", "surrogatepass")).hexdigest()


content_digest = _content_digest
model_digest = _model_digest


from typing import TYPE_CHECKING, ForwardRef


def _reference_identity_document(model: Model) -> dict[str, Any]:
    """The version-1 identity envelope of a reference-bearing model: its one home."""
    document = model.model_dump(exclude={"warnings", "reference_populations"})
    # Through the same walk as the model: a declaration is refused, never coerced
    # (unchanged bytes for every declaration the loader accepts: strings and lists).
    declarations = [
        _canonical(dict(d, fact_types=sorted(d["fact_types"])), f"$.reference_populations[{index}]")
        for index, d in enumerate(model.reference_populations)
    ]
    return {
        "identity_version": 1,
        "model": _canonical(document, "$"),
        "reference_populations": sorted(declarations, key=lambda d: d["id"]),
    }


def reference_model_digest(model: Model) -> str:
    if not model.reference_populations:
        return "sha256:" + _model_digest(model)
    payload = _reference_identity_document(model)
    return "sha256:" + hashlib.sha256(artifacts.canonical_json_bytes(payload)).hexdigest()


IDENTITY_VERSION = 2


class ModelIdentityError(ValueError):
    """A loaded model that has no canonical identity, or a version it does not define.

    A refusal, never a mismatch: a verifier that meets one falls back to the
    legacy identity and says so (plan section 2, item 10).
    """

    rule_id = "model:identity-unrepresentable"

    def __init__(self, path: str, message: str) -> None:
        super().__init__(f"{path}: {message}")
        self.path = path
        self.message = message


def _identity_parts(model: Model) -> tuple[dict[str, Any], bytes]:
    """The identity document and the bytes it is written as, or :class:`ModelIdentityError`.

    One place decides representability, so the document and the bytes refuse the
    same models: the canonical walk's refusal, a malformed declaration, a string
    that is not UTF-8, and nesting past the interpreter's depth.
    """
    try:
        if model.reference_populations:
            document = _reference_identity_document(model)
        else:
            dumped = model.model_dump(exclude={"warnings", "operations", "reference_populations"})
            document = {"identity_version": IDENTITY_VERSION, "model": _canonical(dumped, "$")}
        return document, artifacts.canonical_json_bytes(document)
    except TransitionLoadError as error:
        issue = error.issues[0] if getattr(error, "issues", None) else None
        path = issue.path if issue is not None else "$"
        message = issue.message if issue is not None else str(error)
        raise ModelIdentityError(path, message) from None
    except UnicodeEncodeError as error:
        raise ModelIdentityError(
            "$", f"a string cannot be written as UTF-8 ({error.reason}); quote it differently in the model"
        ) from None
    except RecursionError:
        raise ModelIdentityError("$", "the model is nested too deeply to write as canonical JSON") from None
    except (TypeError, ValueError, KeyError) as error:
        raise ModelIdentityError("$", f"a value cannot be written as canonical JSON ({error})") from None


def model_identity_document(model: Model) -> dict[str, Any]:
    """The canonical identity document of a loaded model.

    Version 2 for a model without reference populations: the loaded model
    without ``warnings``, ``operations`` and ``reference_populations``, through
    the one canonical walk. Version 1 for a reference-bearing model: the
    envelope ``reference_model_digest`` hashes. The normative definition is the
    "Model identity" subsection of the gnd-orm-core ``representation-format.md``.
    Raises :class:`ModelIdentityError` for a model that has no canonical bytes.
    """
    return _identity_parts(model)[0]


def model_identity_bytes(model: Model) -> bytes:
    """The canonical bytes the identity hashes; :class:`ModelIdentityError` if there are none."""
    return _identity_parts(model)[1]


def model_identity(model: Model, version: int | None = None) -> str:
    """``sha256:<hex>`` over :func:`model_identity_bytes`: the model's canonical identity.

    ``version`` None means the model's own: 2 without reference populations, 1
    with them. Asking for a version the model does not define is refused.
    """
    own = 1 if model.reference_populations else IDENTITY_VERSION
    if version is not None and version != own:
        raise ModelIdentityError("$", f"identity version {version} is not defined for this model")
    return "sha256:" + hashlib.sha256(model_identity_bytes(model)).hexdigest()


IdentityMatch = Literal["legacy-repr", "canonical-v1", "canonical-v2"]


def model_identity_matches(
    supplied: object, model: Model, *, prefixed: bool = True
) -> IdentityMatch | None:
    """Which identity of ``model`` the ``supplied`` value names, or None.

    The one place that decides whether a supplied model identity is accepted
    (the acceptance rule's home is the digest table of the gnd-orm-core
    ``representation-format.md``). ``prefixed`` compares the ``sha256:<hex>``
    spelling (steps, reports, certificates); ``prefixed=False`` compares bare
    hex (measure sidecars). The legacy identity is compared first, so a legacy
    pin never computes the canonical one. A reference-bearing model's legacy
    value is its version-1 identity, its only one. A canonical identity the
    model cannot have (:class:`ModelIdentityError`) is "not this identity":
    None, never an exception. The legacy digest is computed as every caller
    computed it before, failures included.
    """
    if not isinstance(supplied, str):
        return None
    prefix = "sha256:" if prefixed else ""
    if supplied == prefix + _model_digest(model):
        return "canonical-v1" if model.reference_populations else "legacy-repr"
    if model.reference_populations:
        return None
    try:
        canonical = model_identity(model)
    except ModelIdentityError:
        return None
    return "canonical-v2" if supplied == prefix + canonical.removeprefix("sha256:") else None


def accepted_model_identities(model: Model, *, prefixed: bool = True) -> tuple[str, ...]:
    """The identities :func:`model_identity_matches` accepts, legacy first.

    The version-2 identity is omitted when the model has none. For messages
    and tests; acceptance is decided only by :func:`model_identity_matches`.
    """
    prefix = "sha256:" if prefixed else ""
    accepted = [prefix + _model_digest(model)]
    if not model.reference_populations:
        try:
            accepted.append(prefix + model_identity(model).removeprefix("sha256:"))
        except ModelIdentityError:
            pass
    return tuple(accepted)


from gnd.documents import Model

if TYPE_CHECKING:
    from gnd.population import Population

# Resolve the historical population annotation in its defining module without
# adding a runtime values -> population import cycle.
_content_digest.__annotations__["population"] = ForwardRef("Population", module="gnd.population")

_identity_key.__module__ = 'gnd.checker'

_IdentitySet.__module__ = 'gnd.checker'

_literal.__module__ = 'gnd.checker'

_refuse.__module__ = 'gnd.transition'

_canonical.__module__ = 'gnd.transition'

_content_digest.__module__ = 'gnd.population'

_model_digest.__module__ = 'gnd.population'

reference_model_digest.__module__ = 'gnd.references'
