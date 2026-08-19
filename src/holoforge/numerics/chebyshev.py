"""Chebyshev--Gauss--Lobatto differentiation on a finite interval.

The implementation follows the standard dense collocation construction in
L. N. Trefethen, *Spectral Methods in MATLAB*, Chapter 6.  It deliberately
provides only the coordinate grid and differentiation matrices.  Equations,
boundary rows, gauge choices, and acceptance gates remain benchmark-specific.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from numbers import Integral, Real

import numpy as np
from numpy.typing import NDArray


@dataclass(frozen=True)
class ChebyshevGrid:
    """Ascending Lobatto nodes and dense derivative matrices on ``[a, b]``."""

    degree: int
    lower_bound: float
    upper_bound: float
    nodes: NDArray[np.float64]
    first_derivative: NDArray[np.float64]
    second_derivative: NDArray[np.float64]

    @property
    def size(self) -> int:
        """Number of collocation nodes, including both endpoints."""

        return self.degree + 1

    @property
    def minimum_spacing(self) -> float:
        """Smallest adjacent-node separation."""

        return float(np.min(np.diff(self.nodes)))

    @property
    def maximum_spacing(self) -> float:
        """Largest adjacent-node separation."""

        return float(np.max(np.diff(self.nodes)))


def chebyshev_lobatto_grid(
    degree: int,
    lower_bound: Real = -1.0,
    upper_bound: Real = 1.0,
) -> ChebyshevGrid:
    """Return Chebyshev--Gauss--Lobatto nodes and ``d/dz``, ``d^2/dz^2``.

    ``degree`` is the polynomial degree, so the returned arrays contain
    ``degree + 1`` nodes.  Nodes are ordered from ``lower_bound`` to
    ``upper_bound`` to make UV/IR or boundary/horizon row placement explicit.
    The arrays are read-only; callers replacing boundary rows must first copy
    the relevant operator.
    """

    if isinstance(degree, bool) or not isinstance(degree, Integral):
        raise ValueError("degree must be an integer")
    if int(degree) < 2:
        raise ValueError("degree must be at least 2")
    if isinstance(lower_bound, bool) or not isinstance(lower_bound, Real):
        raise ValueError("lower_bound must be a finite real number")
    if isinstance(upper_bound, bool) or not isinstance(upper_bound, Real):
        raise ValueError("upper_bound must be a finite real number")

    lower = float(lower_bound)
    upper = float(upper_bound)
    if not math.isfinite(lower):
        raise ValueError("lower_bound must be a finite real number")
    if not math.isfinite(upper):
        raise ValueError("upper_bound must be a finite real number")
    if lower >= upper:
        raise ValueError("lower_bound must be less than upper_bound")

    resolved_degree = int(degree)
    indices = np.arange(resolved_degree + 1)
    descending_nodes = np.cos(np.pi * indices / resolved_degree)

    endpoint_weights = np.ones(resolved_degree + 1)
    endpoint_weights[0] = 2.0
    endpoint_weights[-1] = 2.0
    endpoint_weights *= (-1.0) ** indices

    differences = (
        descending_nodes[:, np.newaxis]
        - descending_nodes[np.newaxis, :]
    )
    derivative = np.outer(endpoint_weights, 1.0 / endpoint_weights) / (
        differences + np.eye(resolved_degree + 1)
    )
    derivative -= np.diag(np.sum(derivative, axis=1))

    # Reverse both axes so the public grid is ordered from lower to upper.
    canonical_nodes = descending_nodes[::-1].copy()
    canonical_derivative = derivative[::-1, ::-1].copy()
    half_width = 0.5 * (upper - lower)
    midpoint = 0.5 * (upper + lower)
    nodes = midpoint + half_width * canonical_nodes
    nodes[0] = lower
    nodes[-1] = upper
    first_derivative = canonical_derivative / half_width
    second_derivative = first_derivative @ first_derivative

    for array in (nodes, first_derivative, second_derivative):
        array.setflags(write=False)

    return ChebyshevGrid(
        degree=resolved_degree,
        lower_bound=lower,
        upper_bound=upper,
        nodes=np.asarray(nodes, dtype=float),
        first_derivative=np.asarray(first_derivative, dtype=float),
        second_derivative=np.asarray(second_derivative, dtype=float),
    )
