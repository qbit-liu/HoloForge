"""Small numerical helpers for controlled observable comparisons.

The functions in this module encode transformations shared by more than one
benchmark without imposing a common differential-equation solver.  In
particular, normalizing a spectrum to one of its masses creates correlated
ratios because every ratio shares the same denominator.
"""

from __future__ import annotations

from dataclasses import dataclass
from numbers import Integral
from typing import Any, Dict, Optional, Sequence

import numpy as np
from numpy.typing import ArrayLike, NDArray


@dataclass(frozen=True)
class NormalizedSpectrum:
    """Mass ratios and the covariance produced by their Jacobian.

    The anchor ratio is retained as an exact value of one.  Its Jacobian row is
    zero, so its propagated variance and covariance are also zero.  A later
    goodness-of-comparison calculation should omit that calibrated entry
    rather than attempting to invert the resulting singular covariance.
    """

    masses: NDArray[np.float64]
    mass_covariance: NDArray[np.float64]
    anchor_index: int
    ratios: NDArray[np.float64]
    ratio_covariance: NDArray[np.float64]
    jacobian: NDArray[np.float64]

    @property
    def standard_deviations(self) -> NDArray[np.float64]:
        """Return one-sigma uncertainties of the normalized ratios."""

        return np.sqrt(np.maximum(np.diag(self.ratio_covariance), 0.0))

    def to_dict(self, labels: Optional[Sequence[str]] = None) -> Dict[str, Any]:
        """Return a JSON-serializable record of the transformation."""

        if labels is None:
            resolved_labels = [str(index) for index in range(len(self.ratios))]
        else:
            resolved_labels = list(labels)
            if len(resolved_labels) != len(self.ratios):
                raise ValueError("labels must have the same length as masses")
            if not all(
                isinstance(label, str) and label for label in resolved_labels
            ):
                raise ValueError("labels must contain non-empty strings")

        return {
            "anchor_index": self.anchor_index,
            "entries": [
                {
                    "label": label,
                    "mass": float(mass),
                    "ratio": float(ratio),
                    "ratio_standard_deviation": float(standard_deviation),
                }
                for label, mass, ratio, standard_deviation in zip(
                    resolved_labels,
                    self.masses,
                    self.ratios,
                    self.standard_deviations,
                )
            ],
            "mass_covariance": self.mass_covariance.tolist(),
            "ratio_covariance": self.ratio_covariance.tolist(),
            "jacobian": self.jacobian.tolist(),
        }


def normalize_spectrum(
    masses: ArrayLike,
    mass_covariance: Optional[ArrayLike] = None,
    anchor_index: int = 0,
) -> NormalizedSpectrum:
    """Normalize masses to an anchor and propagate covariance analytically.

    For ``R_i = m_i / m_a``, the exact Jacobian is

    ``dR_i/dm_j = delta_ij/m_a - m_i delta_aj/m_a**2``.

    Args:
        masses: One-dimensional, finite, positive mass values.
        mass_covariance: Symmetric positive-semidefinite covariance of the
            masses.  If omitted, a zero covariance is used.
        anchor_index: Position of the mass used as the shared denominator.
    """

    values = np.asarray(masses, dtype=float)
    if values.ndim != 1 or values.size < 2:
        raise ValueError("masses must be a one-dimensional array of length >= 2")
    if not np.all(np.isfinite(values)) or np.any(values <= 0.0):
        raise ValueError("masses must contain only finite positive values")
    if isinstance(anchor_index, bool) or not isinstance(anchor_index, Integral):
        raise ValueError("anchor_index must be an integer")
    resolved_anchor = int(anchor_index)
    if not 0 <= resolved_anchor < values.size:
        raise ValueError("anchor_index is outside the mass array")

    covariance = _validated_covariance(mass_covariance, values.size)
    anchor = values[resolved_anchor]
    ratios = values / anchor

    jacobian = np.eye(values.size, dtype=float) / anchor
    jacobian[:, resolved_anchor] -= values / anchor**2
    ratio_covariance = jacobian @ covariance @ jacobian.T
    ratio_covariance = 0.5 * (ratio_covariance + ratio_covariance.T)

    return NormalizedSpectrum(
        masses=values.copy(),
        mass_covariance=covariance,
        anchor_index=resolved_anchor,
        ratios=ratios,
        ratio_covariance=ratio_covariance,
        jacobian=jacobian,
    )


def _validated_covariance(
    mass_covariance: Optional[ArrayLike], size: int
) -> NDArray[np.float64]:
    if mass_covariance is None:
        return np.zeros((size, size), dtype=float)

    covariance = np.asarray(mass_covariance, dtype=float)
    if covariance.shape != (size, size):
        raise ValueError("mass_covariance must have shape (len(masses), len(masses))")
    if not np.all(np.isfinite(covariance)):
        raise ValueError("mass_covariance must contain only finite values")
    if not np.allclose(covariance, covariance.T, rtol=1.0e-12, atol=1.0e-14):
        raise ValueError("mass_covariance must be symmetric")

    symmetric = 0.5 * (covariance + covariance.T)
    eigenvalues = np.linalg.eigvalsh(symmetric)
    scale = max(float(np.max(np.abs(eigenvalues))), 1.0)
    if float(np.min(eigenvalues)) < -1.0e-12 * scale:
        raise ValueError("mass_covariance must be positive semidefinite")
    return symmetric.copy()
