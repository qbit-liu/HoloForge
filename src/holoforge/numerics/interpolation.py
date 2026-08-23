"""Deterministic interpolation helpers shared by spectral benchmarks."""

from __future__ import annotations

import inspect
from typing import Any

from scipy.interpolate import BarycentricInterpolator


_RANDOM_KEYWORD = (
    "rng"
    if "rng" in inspect.signature(BarycentricInterpolator).parameters
    else "random_state"
)


def deterministic_barycentric_interpolator(
    nodes: Any,
    values: Any,
) -> BarycentricInterpolator:
    """Return SciPy's barycentric interpolator with a version-stable seed.

    SciPy renamed the keyword controlling its deterministic weight
    permutation from ``random_state`` to ``rng``. Centralizing that API shim
    keeps every benchmark on the same maintained implementation without
    introducing a HoloForge interpolation algorithm.
    """

    return BarycentricInterpolator(
        nodes,
        values,
        **{_RANDOM_KEYWORD: 0},
    )


__all__ = ["deterministic_barycentric_interpolator"]
