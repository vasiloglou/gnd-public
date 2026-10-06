"""RF3 shared dependency home; algorithms retain predecessor semantics."""
from __future__ import annotations

import json  # noqa: F401 -- historical compatibility binding
from importlib.resources import files
from typing import Any

from gnd import input_policy as _rf7_input


def load_report_schema() -> dict[str, Any]:
    """The Draft 2020-12 schema describing this payload.

    Loaded through ``importlib.resources`` like the model and population
    schemas, so the contract ships with the installed package rather than
    living only in the source tree.
    """
    schema_text = files("gnd").joinpath("report.schema.json").read_text(encoding="utf-8")
    return _rf7_input.loads(schema_text)


load_report_schema.__module__ = 'gnd.report'
