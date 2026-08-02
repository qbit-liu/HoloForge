"""Quadratic soft-wall transverse-vector spectrum.

The benchmark follows Eqs. (8)-(15) of Karch, Katz, Son, and
Stephanov, Phys. Rev. D 74, 015005 (2006), arXiv:hep-ph/0602229.
After restoring the soft-wall scale ``kappa``, the normal-mode problem is

    -psi'' + (kappa**4 * z**2 + 3 / (4 * z**2)) psi = m**2 psi,

with exact eigenvalues ``m_n**2 = 4 * kappa**2 * (n + 1)``.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from numbers import Real
import platform
from typing import Any, Dict, List, Optional

import numpy as np
from numpy.typing import ArrayLike, NDArray
import scipy
from scipy.linalg import eigvalsh_tridiagonal


DEFAULT_GRID_POINTS = 1_200
DEFAULT_NUM_MODES = 4
DEFAULT_TOLERANCE = 2.0e-4
DEFAULT_DIMENSIONLESS_Z_MAX = 10.0
EIGENSOLVER = "scipy.linalg.eigvalsh_tridiagonal"
DISCRETIZATION = "second-order centered finite difference"


@dataclass(frozen=True)
class SoftWallConfig:
    """Numerical and physical inputs for the vector-spectrum benchmark.

    Args:
        kappa_gev: Positive soft-wall scale in GeV.
        grid_points: Number of uniformly spaced interior points.
        z_max_gev_inverse: Finite IR boundary in GeV^-1. If omitted, use
            ``10 / kappa``, keeping the dimensionless domain fixed.
    """

    kappa_gev: float = 1.0
    grid_points: int = DEFAULT_GRID_POINTS
    z_max_gev_inverse: Optional[float] = None

    def __post_init__(self) -> None:
        if not _is_finite_positive_real(self.kappa_gev):
            raise ValueError("kappa_gev must be a finite positive number")
        if isinstance(self.grid_points, bool) or not isinstance(self.grid_points, int):
            raise ValueError("grid_points must be an integer")
        if self.grid_points < 3:
            raise ValueError("grid_points must be at least 3")
        if self.z_max_gev_inverse is not None:
            if not _is_finite_positive_real(self.z_max_gev_inverse):
                raise ValueError(
                    "z_max_gev_inverse must be a finite positive number"
                )

    @property
    def resolved_z_max_gev_inverse(self) -> float:
        """Return the explicit IR boundary used by the solver."""

        if self.z_max_gev_inverse is not None:
            return float(self.z_max_gev_inverse)
        return DEFAULT_DIMENSIONLESS_Z_MAX / float(self.kappa_gev)


@dataclass(frozen=True)
class SpectrumResult:
    """Numerical spectrum together with its exact benchmark values."""

    config: SoftWallConfig
    mode_numbers: NDArray[np.int64]
    numerical_mass_squared_gev2: NDArray[np.float64]
    analytic_mass_squared_gev2: NDArray[np.float64]
    relative_errors: NDArray[np.float64]
    grid_spacing_gev_inverse: float

    @property
    def max_relative_error(self) -> float:
        """Largest relative eigenvalue error among the requested modes."""

        return float(np.max(self.relative_errors))

    @property
    def dimensionless_z_max(self) -> float:
        """Return the scale-free IR boundary ``kappa * z_max``."""

        return float(
            self.config.kappa_gev
            * self.config.resolved_z_max_gev_inverse
        )

    def to_dict(self, tolerance: float) -> Dict[str, Any]:
        """Return a JSON-serializable verification record."""

        records: List[Dict[str, Any]] = []
        for n, numerical, analytic, error in zip(
            self.mode_numbers,
            self.numerical_mass_squared_gev2,
            self.analytic_mass_squared_gev2,
            self.relative_errors,
        ):
            records.append(
                {
                    "n": int(n),
                    "numerical_mass_squared_gev2": float(numerical),
                    "analytic_mass_squared_gev2": float(analytic),
                    "numerical_mass_gev": float(np.sqrt(numerical)),
                    "relative_error": float(error),
                }
            )

        return {
            "benchmark": "soft-wall-vector",
            "support_level": "reproduced",
            "configuration": {
                "kappa_gev": float(self.config.kappa_gev),
                "num_modes": len(self.mode_numbers),
                "grid_points": self.config.grid_points,
                "z_max_gev_inverse": self.config.resolved_z_max_gev_inverse,
                "dimensionless_z_max": self.dimensionless_z_max,
                "grid_spacing_gev_inverse": self.grid_spacing_gev_inverse,
            },
            "numerical_method": {
                "discretization": DISCRETIZATION,
                "operator_structure": "real symmetric tridiagonal",
                "eigensolver": EIGENSOLVER,
                "lapack_driver": "auto",
                "boundary_conditions": "psi(0) = psi(z_max) = 0",
            },
            "software_versions": {
                "python": platform.python_version(),
                "numpy": np.__version__,
                "scipy": scipy.__version__,
            },
            "results": records,
            "tolerance": float(tolerance),
            "max_relative_error": self.max_relative_error,
            "passed": self.max_relative_error <= tolerance,
            "scope": (
                "Numerical reproduction of the published mode equation; "
                "not empirical validation of the model."
            ),
        }


def schrodinger_potential(
    z_gev_inverse: ArrayLike, kappa_gev: float
) -> NDArray[np.float64]:
    """Evaluate ``kappa^4 z^2 + 3/(4 z^2)`` in GeV squared."""

    z = np.asarray(z_gev_inverse, dtype=float)
    if not np.all(np.isfinite(z)) or np.any(z <= 0.0):
        raise ValueError("z_gev_inverse must contain only finite positive values")
    if not _is_finite_positive_real(kappa_gev):
        raise ValueError("kappa_gev must be a finite positive number")
    return kappa_gev**4 * z**2 + 3.0 / (4.0 * z**2)


def analytic_mass_squared(
    num_modes: int, kappa_gev: float
) -> NDArray[np.float64]:
    """Return exact ``m_n^2 = 4 kappa^2 (n + 1)`` values in GeV squared."""

    _validate_num_modes(num_modes)
    if not _is_finite_positive_real(kappa_gev):
        raise ValueError("kappa_gev must be a finite positive number")
    n = np.arange(num_modes, dtype=float)
    return 4.0 * kappa_gev**2 * (n + 1.0)


def solve_spectrum(
    config: Optional[SoftWallConfig] = None,
    num_modes: int = DEFAULT_NUM_MODES,
) -> SpectrumResult:
    """Solve the finite-domain soft-wall eigenvalue problem.

    A second-order centered finite difference is used on ``grid_points``
    interior sites. Dirichlet values at ``z=0`` and ``z=z_max`` are implicit in
    the tridiagonal kinetic operator.
    """

    if config is None:
        config = SoftWallConfig()
    _validate_num_modes(num_modes)
    if num_modes > config.grid_points:
        raise ValueError("num_modes cannot exceed grid_points")

    z_max = config.resolved_z_max_gev_inverse
    spacing = z_max / (config.grid_points + 1)
    z = spacing * np.arange(1, config.grid_points + 1, dtype=float)

    inverse_spacing_squared = 1.0 / spacing**2
    diagonal = (
        2.0 * inverse_spacing_squared
        + schrodinger_potential(z, config.kappa_gev)
    )
    off_diagonal = np.full(
        config.grid_points - 1, -inverse_spacing_squared, dtype=float
    )

    numerical = eigvalsh_tridiagonal(
        diagonal,
        off_diagonal,
        select="i",
        select_range=(0, num_modes - 1),
        check_finite=True,
    )
    analytic = analytic_mass_squared(num_modes, config.kappa_gev)
    relative_errors = np.abs(numerical - analytic) / analytic

    return SpectrumResult(
        config=config,
        mode_numbers=np.arange(num_modes, dtype=np.int64),
        numerical_mass_squared_gev2=np.asarray(numerical, dtype=float),
        analytic_mass_squared_gev2=analytic,
        relative_errors=relative_errors,
        grid_spacing_gev_inverse=float(spacing),
    )


def _validate_num_modes(num_modes: int) -> None:
    if isinstance(num_modes, bool) or not isinstance(num_modes, int):
        raise ValueError("num_modes must be an integer")
    if num_modes < 1:
        raise ValueError("num_modes must be at least 1")


def _is_finite_positive_real(value: object) -> bool:
    return (
        isinstance(value, Real)
        and not isinstance(value, bool)
        and math.isfinite(float(value))
        and float(value) > 0.0
    )
