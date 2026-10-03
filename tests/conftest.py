"""Current P2 fixture registration only; no historical session/collection hooks."""

import sys
from pathlib import Path
from typing import Any

from test_public_distribution import (
    package_probe as package_probe,  # noqa: PLC0414 -- pytest fixture export
)

from gnd.model import Model
from gnd.population import Population, _stamp_validated_against


def make_population(model: Model, /, **kwargs: Any) -> Population:
    """Build a Population and stamp it as validated against ``model``.

    Use ONLY when the population is deliberately not loadable — a shape layer 2
    would reject, built to test a checker guard. Anything that can come from a
    file must go through ``load_population(path, model=model)`` so that layer 2
    actually runs.

    The :class:`~gnd.model.Model` is **positional-only**: ``Population`` has a
    field literally named ``model`` (the free-form header path string), so a
    keyword parameter of the same name would collide with it. The ``/`` lets
    ``make_population(model_obj, model="m.orm.yaml", ...)`` read naturally.
    """
    population = Population(**kwargs)
    _stamp_validated_against(population, model)
    return population


# Exact original tests import local helpers through the tests namespace.
# Include only this public checkout/sandbox root; installed gnd stays separately resolved.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
