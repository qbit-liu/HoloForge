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
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
from numpy.typing import ArrayLike, NDArray
from scipy.linalg import eigvals, eigvalsh_tridiagonal

from holoforge.core import (
    AcceptanceCheck,
    BackgroundSpec,
    BenchmarkDefinition,
    BoundaryConditionSpec,
    EquationSpec,
    ObservableSpec,
    SolverSpec,
    VerificationRecord,
    runtime_versions,
)
from holoforge.numerics import chebyshev_lobatto_grid


DEFAULT_GRID_POINTS = 1_200
DEFAULT_NUM_MODES = 4
DEFAULT_TOLERANCE = 2.0e-4
DEFAULT_DIMENSIONLESS_Z_MAX = 10.0
DEFAULT_SPECTRAL_DEGREE = 40
DEFAULT_SPECTRAL_CONVERGENCE_TOLERANCE = 1.0e-8
EIGENSOLVER = "scipy.linalg.eigvalsh_tridiagonal"
DISCRETIZATION = "second-order centered finite difference"
SPECTRAL_EIGENSOLVER = "scipy.linalg.eigvals"
SPECTRAL_DISCRETIZATION = "Chebyshev--Gauss--Lobatto pseudospectral collocation"


SOFT_WALL_DEFINITION = BenchmarkDefinition(
    identifier="soft-wall-vector",
    support_level="reproduced",
    background=BackgroundSpec(
        identifier="quadratic-soft-wall-ads5",
        dimension=5,
        coordinate="z in (0, infinity)",
        description=(
            "Fixed AdS_5 background with dilaton Phi(z) = kappa^2 z^2."
        ),
    ),
    equations=(
        EquationSpec(
            identifier="vector-schrodinger",
            kind="Sturm-Liouville eigenvalue problem",
            dependent_fields=("psi_n",),
            expression=(
                "-psi_n'' + (kappa^4 z^2 + 3/(4 z^2)) psi_n "
                "= m_n^2 psi_n"
            ),
            source_reference=(
                "Karch et al., arXiv:hep-ph/0602229v2, Eqs. (8)-(15)"
            ),
        ),
    ),
    boundary_conditions=(
        BoundaryConditionSpec(
            field="psi_n",
            location="z = 0",
            role="UV normalizability",
            expression="psi_n(0) = 0",
            interpretation="Dirichlet approximation to the normalizable UV mode.",
        ),
        BoundaryConditionSpec(
            field="psi_n",
            location="z = z_max",
            role="IR truncation",
            expression="psi_n(z_max) = 0",
            interpretation="Finite-domain approximation to IR normalizability.",
        ),
    ),
    solvers=(
        SolverSpec(
            problem_type="real symmetric tridiagonal eigenproblem",
            library_function=EIGENSOLVER,
            method="LAPACK driver selected by SciPy",
            description=DISCRETIZATION,
        ),
        SolverSpec(
            problem_type="dense collocation eigenproblem",
            library_function=SPECTRAL_EIGENSOLVER,
            method="dense nonsymmetric eigenvalue solve",
            description=SPECTRAL_DISCRETIZATION,
        ),
    ),
    observables=(
        ObservableSpec(
            identifier="vector-mode-masses",
            symbol="m_n^2",
            extraction="Ordered lowest eigenvalues of the discrete operator.",
            normalization="GeV^2 with the input scale kappa expressed in GeV.",
        ),
    ),
)


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
    spectral_degree: int = DEFAULT_SPECTRAL_DEGREE

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
        if isinstance(self.spectral_degree, bool) or not isinstance(
            self.spectral_degree, int
        ):
            raise ValueError("spectral_degree must be an integer")
        if self.spectral_degree < 24:
            raise ValueError("spectral_degree must be at least 24")

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
    method: str = "finite-difference"
    spectral_degree: Optional[int] = None
    spectral_refinement_degrees: Tuple[int, ...] = ()
    spectral_refinement_errors: Tuple[float, ...] = ()

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

        checks = [AcceptanceCheck(
            identifier="exact-spectrum-relative-error",
            description=(
                "Maximum relative error of the requested eigenvalues is within "
                "the declared tolerance."
            ),
            value=self.max_relative_error,
            criterion=f"value <= {float(tolerance):.16g}",
            passed=self.max_relative_error <= tolerance,
        )]
        if self.method == "spectral":
            refinement_improves = bool(
                len(self.spectral_refinement_errors) >= 3
                and np.all(np.diff(self.spectral_refinement_errors) < 0.0)
            )
            refinement_passed = bool(
                refinement_improves
                and self.spectral_refinement_errors[-1]
                <= DEFAULT_SPECTRAL_CONVERGENCE_TOLERANCE
            )
            checks.append(
                AcceptanceCheck(
                    identifier="spectral-degree-refinement",
                    description=(
                        "The analytic spectrum error decreases across three "
                        "polynomial degrees and the final error is below the "
                        "declared spectral convergence tolerance."
                    ),
                    value=float(self.spectral_refinement_errors[-1]),
                    criterion=(
                        "strictly decreasing across three degrees and value <= "
                        f"{DEFAULT_SPECTRAL_CONVERGENCE_TOLERANCE:.16g}"
                    ),
                    passed=refinement_passed,
                )
            )

        configuration: Dict[str, Any] = {
            "kappa_gev": float(self.config.kappa_gev),
            "num_modes": len(self.mode_numbers),
            "z_max_gev_inverse": self.config.resolved_z_max_gev_inverse,
            "dimensionless_z_max": self.dimensionless_z_max,
        }
        if self.method == "spectral":
            configuration["spectral_degree"] = int(self.spectral_degree)
            configuration["maximum_node_spacing_gev_inverse"] = (
                self.grid_spacing_gev_inverse
            )
        else:
            configuration["grid_points"] = self.config.grid_points
            configuration["grid_spacing_gev_inverse"] = (
                self.grid_spacing_gev_inverse
            )

        if self.method == "finite-difference":
            numerical_method: Dict[str, Any] = {
                "discretization": DISCRETIZATION,
                "operator_structure": "real symmetric tridiagonal",
                "eigensolver": EIGENSOLVER,
                "lapack_driver": "auto",
                "boundary_conditions": "psi(0) = psi(z_max) = 0",
            }
        else:
            numerical_method = {
                "route": "spectral",
                "discretization": SPECTRAL_DISCRETIZATION,
                "operator_structure": "dense real collocation operator",
                "eigensolver": SPECTRAL_EIGENSOLVER,
                "boundary_conditions": "psi(0) = psi(z_max) = 0",
                "spectral_convergence_tolerance": (
                    DEFAULT_SPECTRAL_CONVERGENCE_TOLERANCE
                ),
            }

        extra: Dict[str, Any] = {
            "tolerance": float(tolerance),
            "max_relative_error": self.max_relative_error,
        }
        if self.method == "spectral":
            extra["spectral_convergence"] = {
                "levels": [
                    {
                        "degree": int(degree),
                        "max_relative_error": float(error),
                    }
                    for degree, error in zip(
                        self.spectral_refinement_degrees,
                        self.spectral_refinement_errors,
                    )
                ],
                "improves_at_every_level": bool(
                    np.all(np.diff(self.spectral_refinement_errors) < 0.0)
                ),
            }

        record = VerificationRecord(
            definition=SOFT_WALL_DEFINITION,
            configuration=configuration,
            numerical_method=numerical_method,
            results=records,
            acceptance_checks=tuple(checks),
            software_versions=runtime_versions(),
            scope=(
                "Numerical reproduction of the published mode equation; "
                "not empirical validation of the model."
            ),
            extra=extra,
        )
        return record.to_dict()


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
    method: str = "finite-difference",
) -> SpectrumResult:
    """Solve the finite-domain soft-wall eigenvalue problem.

    The protected default is a centered finite difference on ``grid_points``
    interior sites.  The opt-in ``spectral`` route uses Lobatto collocation and
    removes both Dirichlet endpoint rows and columns.
    """

    if config is None:
        config = SoftWallConfig()
    _validate_num_modes(num_modes)
    if num_modes > config.grid_points and method == "finite-difference":
        raise ValueError("num_modes cannot exceed grid_points")

    if method == "finite-difference":
        numerical, spacing = _finite_difference_spectrum(config, num_modes)
        refinement_degrees: Tuple[int, ...] = ()
        refinement_errors: Tuple[float, ...] = ()
        spectral_degree: Optional[int] = None
    elif method == "spectral":
        if num_modes > config.spectral_degree - 17:
            raise ValueError(
                "num_modes must not exceed spectral_degree - 17 so the "
                "three-level refinement has enough interior modes"
            )
        refinement_degrees = (
            config.spectral_degree - 16,
            config.spectral_degree - 8,
            config.spectral_degree,
        )
        analytic = analytic_mass_squared(num_modes, config.kappa_gev)
        refinement_solutions = tuple(
            _spectral_spectrum(config, num_modes, degree)
            for degree in refinement_degrees
        )
        refinement_values = tuple(
            values for values, _ in refinement_solutions
        )
        refinement_errors = tuple(
            float(np.max(np.abs(values - analytic) / analytic))
            for values in refinement_values
        )
        numerical = refinement_values[-1]
        spacing = refinement_solutions[-1][1]
        spectral_degree = config.spectral_degree
    else:
        raise ValueError("method must be 'finite-difference' or 'spectral'")

    analytic = analytic_mass_squared(num_modes, config.kappa_gev)
    relative_errors = np.abs(numerical - analytic) / analytic

    return SpectrumResult(
        config=config,
        mode_numbers=np.arange(num_modes, dtype=np.int64),
        numerical_mass_squared_gev2=np.asarray(numerical, dtype=float),
        analytic_mass_squared_gev2=analytic,
        relative_errors=relative_errors,
        grid_spacing_gev_inverse=float(spacing),
        method=method,
        spectral_degree=spectral_degree,
        spectral_refinement_degrees=refinement_degrees,
        spectral_refinement_errors=refinement_errors,
    )


def _finite_difference_spectrum(
    config: SoftWallConfig, num_modes: int
) -> Tuple[NDArray[np.float64], float]:
    """Return the protected finite-difference result and uniform spacing."""

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
    return np.asarray(numerical, dtype=float), float(spacing)


def _spectral_spectrum(
    config: SoftWallConfig, num_modes: int, degree: int
) -> Tuple[NDArray[np.float64], float]:
    """Return a finite-domain Lobatto-collocation spectrum."""

    grid = chebyshev_lobatto_grid(
        degree, 0.0, config.resolved_z_max_gev_inverse
    )
    interior = slice(1, -1)
    nodes = grid.nodes[interior]
    operator = (
        -grid.second_derivative[interior, interior]
        + np.diag(schrodinger_potential(nodes, config.kappa_gev))
    )
    eigenvalues = eigvals(operator, check_finite=True)
    real = eigenvalues.real
    admissible = (
        np.isfinite(real)
        & np.isfinite(eigenvalues.imag)
        & (real > 0.0)
        & (np.abs(eigenvalues.imag) <= 1.0e-8 * np.maximum(real, 1.0))
    )
    ordered = np.sort(real[admissible])
    if len(ordered) < num_modes:
        raise RuntimeError(
            "spectral eigensolver returned too few finite positive real modes"
        )
    return (
        np.asarray(ordered[:num_modes], dtype=float),
        grid.maximum_spacing,
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
