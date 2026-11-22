"""Produce a snapshot-bound COUNT membership certificate."""

from gnd.witness.count_membership import (
    INPUT_ERRORS,
    check_result_bound,
    make_document,
    members_from_snapshot,
    read_request,
    read_snapshot,
    refused,
    success,
)
from gnd.witness.types import DEFAULT_LIMITS, checked_limits


def produce_count(model, population, request_path, *, limits=DEFAULT_LIMITS):
    try:
        checked_limits(limits)
        request, request_digest = read_request(request_path, limits)
        snapshot = read_snapshot(model, population, request_digest, limits)
        members = members_from_snapshot(model, population, snapshot, request, limits)
        certificate = make_document(snapshot[2], request, members)
        check_result_bound(certificate, limits)
        return success(certificate, include_certificate=True)
    except INPUT_ERRORS as error:
        return refused(error)
