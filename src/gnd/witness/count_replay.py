"""Verify COUNT membership against caller-selected inputs independently."""

from gnd.witness.count_membership import (
    INPUT_ERRORS,
    CountRefusal,
    certificate_shape,
    check_result_bound,
    make_document,
    members_from_snapshot,
    read_bytes,
    read_request,
    read_snapshot,
    refused,
    success,
)
from gnd.witness.io import parse_wire
from gnd.witness.types import DEFAULT_LIMITS, checked_limits


def replay_count(model, population, certificate_path, request_path, *, limits=DEFAULT_LIMITS):
    try:
        checked_limits(limits)
        certificate = parse_wire(read_bytes(certificate_path, limits), limits=limits)
        certificate_shape(certificate, limits)
        request, request_digest = read_request(request_path, limits)
        snapshot = read_snapshot(model, population, request_digest, limits)
        if certificate["binding"] != snapshot[2] or certificate["request"] != request:
            raise CountRefusal(3, "binding-stale")
        members = members_from_snapshot(model, population, snapshot, request, limits)
        expected = make_document(snapshot[2], request, members)
        check_result_bound(expected, limits)
        if certificate != expected:
            raise CountRefusal(1, "proof-invalid")
        return success(expected)
    except INPUT_ERRORS as error:
        return refused(error)
