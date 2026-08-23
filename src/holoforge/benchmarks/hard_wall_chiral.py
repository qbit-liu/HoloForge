"""Spectral reproduction of the hard-wall chiral AdS/QCD Model A table.

The benchmark implements the two-flavor model of Erlich, Katz, Son, and
Stephanov, arXiv:hep-ph/0501128v2.  Normalizable vector, transverse-axial,
and pion modes use exact-endpoint Chebyshev generalized eigenproblems after
their quadratic UV powers are factored.  Adaptive ``solve_bvp`` solutions and
a backward DOP853 axial zero mode provide independent checks.

Passing this benchmark reproduces a calculation in a truncated bottom-up
effective model.  It is not empirical validation of QCD or of the hard-wall
boundary condition in nature.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
import math
from numbers import Integral, Real
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple

import numpy as np
from numpy.polynomial.legendre import leggauss
from numpy.typing import NDArray
from scipy.integrate import quad, solve_bvp, solve_ivp
from scipy.linalg import eig, solve
from scipy.optimize import root_scalar
from scipy.special import j0, j1, jn_zeros

from holoforge.benchmarks.hard_wall_vector import (
    HardWallConfig,
    solve_hard_wall_spectrum,
)
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
from holoforge.numerics import ChebyshevGrid, chebyshev_lobatto_grid
from holoforge.numerics.interpolation import (
    deterministic_barycentric_interpolator as _interpolator,
)


SOURCE_ID = "arXiv:hep-ph/0501128v2"
SOURCE_PDF_SHA256 = (
    "b2f29ea72e37467b0f54d169948bce86b873f138009443de333512b4350b0881"
)
SOURCE_ARCHIVE_SHA256 = (
    "3591ab1c15b727f31219a4f3b581b45af396de87fea18f8d49b65833e463b3aa"
)

N_C = 3
G5 = 2.0 * math.pi
Z_M_INVERSE_MEV = 323.0
M_Q_MEV = 2.29
SIGMA_CUBE_ROOT_MEV = 327.0
M_HAT = M_Q_MEV / Z_M_INVERSE_MEV
SIGMA_HAT = (SIGMA_CUBE_ROOT_MEV / Z_M_INVERSE_MEV) ** 3
SOURCE_EPSILON_Z_MEV_INVERSE = 1.0e-10
SOURCE_EPSILON = SOURCE_EPSILON_Z_MEV_INVERSE * Z_M_INVERSE_MEV

DEFAULT_DEGREES = (64, 80, 96)
DEFAULT_DIAGNOSTIC_EPSILONS = (2.0e-5, 1.0e-5, 5.0e-6)
DEFAULT_EQUATION_TOLERANCE = 1.0e-7
DEFAULT_BOUNDARY_TOLERANCE = 1.0e-8
DEFAULT_NORMALIZATION_TOLERANCE = 1.0e-8
DEFAULT_IMAGINARY_TOLERANCE = 1.0e-10
DEFAULT_REFINEMENT_TOLERANCE = 2.0e-4
DEFAULT_REFINEMENT_ORDER_FLOOR = 1.0e-10
DEFAULT_INDEPENDENT_TOLERANCE = 1.0e-3
DEFAULT_CUTOFF_TOLERANCE = 2.0e-4
DEFAULT_TABLE_TOLERANCE = 1.0e-2
DEFAULT_GMOR_TOLERANCE = 1.0e-2
DEFAULT_DETERMINISM_TOLERANCE = 1.0e-11
DEFAULT_FPI_ROUTE_TOLERANCE = 1.0e-7
DEFAULT_FPI_LOG_SLOPE_TOLERANCE = 1.0e-5
DEFAULT_GMOR_FACTORS = (1.0, 0.5, 0.25, 0.125)

TABLE_TARGETS: Mapping[str, float] = {
    "m_pi_MeV": 139.6,
    "m_rho_MeV": 775.8,
    "m_a1_MeV": 1363.0,
    "f_pi_MeV": 92.4,
    "sqrt_F_rho_MeV": 329.0,
    "sqrt_F_a1_MeV": 486.0,
    "g_rho_pi_pi": 4.48,
}
SOURCE_FIT_TARGETS = frozenset(("m_pi_MeV", "m_rho_MeV", "f_pi_MeV"))


HARD_WALL_CHIRAL_DEFINITION = BenchmarkDefinition(
    identifier="hard-wall-chiral",
    support_level="reproduced",
    background=BackgroundSpec(
        identifier="hard-wall-ads5-two-flavor-chiral",
        dimension=5,
        coordinate="u = z/z_m in [0, 1]",
        description=(
            "Fixed AdS5 slice with SU(2)_L x SU(2)_R gauge fields and the "
            "source scalar background v = mhat u + sigmahat u^3."
        ),
    ),
    equations=(
        EquationSpec(
            identifier="transverse-vector",
            kind="Sturm--Liouville eigenproblem",
            dependent_fields=("V",),
            expression="d_u[(1/u)V'] + (lambda/u)V = 0",
            source_reference="Erlich et al., Eq. (5)",
        ),
        EquationSpec(
            identifier="transverse-axial",
            kind="Sturm--Liouville eigenproblem",
            dependent_fields=("A",),
            expression=(
                "d_u[(1/u)A'] + (lambda/u)A - g5^2 v^2 A/u^3 = 0"
            ),
            source_reference="Erlich et al., Eq. (16)",
        ),
        EquationSpec(
            identifier="pion-longitudinal-axial",
            kind="coupled generalized eigenproblem",
            dependent_fields=("phi", "pi"),
            expression=(
                "u^2 phi''-u phi'+g5^2 v^2(pi-phi)=0; "
                "-lambda phi'+g5^2(v/u)^2 pi'=0"
            ),
            source_reference="Erlich et al., Eqs. (17)-(18)",
        ),
        EquationSpec(
            identifier="axial-zero-mode",
            kind="regulated boundary-value problem",
            dependent_fields=("A_0",),
            expression="A_0''-A_0'/u-g5^2 v^2 A_0/u^2=0",
            source_reference="Erlich et al., Eq. (20) and public v2 TeX note",
        ),
    ),
    boundary_conditions=(
        BoundaryConditionSpec(
            field="V,A",
            location="u = 0, 1",
            role="normalizable UV and hard-wall IR",
            expression="V(0)=A(0)=0; V'(1)=A'(1)=0",
            interpretation="Exact endpoints are retained after V,A = u^2 times finite factors.",
        ),
        BoundaryConditionSpec(
            field="phi,pi",
            location="u = 0, 1",
            role="normalizable pion and longitudinal axial mode",
            expression="phi(0)=pi(0)=0; phi'(1)=0",
            interpretation="The common homogeneous scale is fixed only by canonical normalization.",
        ),
        BoundaryConditionSpec(
            field="A_0",
            location="u = epsilon, 1",
            role="regulated source and hard-wall IR",
            expression="A_0(epsilon)=1; A_0'(1)=0",
            interpretation=(
                "The full nonzero-mq equation has a u^2 log(u) UV term, so "
                "the public-source regulator is explicit."
            ),
        ),
    ),
    solvers=(
        SolverSpec(
            problem_type="normalizable generalized eigenproblems",
            library_function="scipy.linalg.eig",
            method="UV-factorized Chebyshev--Gauss--Lobatto collocation",
            description=(
                "Exact-endpoint dense QZ pencils at degrees 64, 80, and 96, "
                "followed by source-blind bordered eigenpair refinement."
            ),
        ),
        SolverSpec(
            problem_type="independent finite-cutoff boundary-value problems",
            library_function="scipy.integrate.solve_bvp",
            method="adaptive fourth-order residual-controlled collocation",
            description="Physical unfactored equations on three decreasing UV cutoffs.",
        ),
        SolverSpec(
            problem_type="axial zero-mode initial-value problem",
            library_function="scipy.integrate.solve_ivp",
            method="backward DOP853 integration",
            description="IR Neumann data followed by source-regulator normalization.",
        ),
    ),
    observables=tuple(
        ObservableSpec(identifier, symbol, extraction, normalization)
        for identifier, symbol, extraction, normalization in (
            ("pion-mass", "m_pi", "lowest admissible pion eigenvalue", "MeV"),
            ("rho-mass", "m_rho", "lowest vector eigenvalue", "MeV"),
            ("a1-mass", "m_a1", "lowest transverse-axial eigenvalue", "MeV"),
            ("pion-decay-constant", "f_pi", "regulated axial zero-mode UV derivative", "MeV"),
            ("rho-decay-constant", "sqrt(F_rho)", "factored vector UV derivative", "MeV"),
            ("a1-decay-constant", "sqrt(F_a1)", "factored axial UV derivative", "MeV"),
            ("rho-pion-pion", "g_rho_pi_pi", "canonically normalized overlap", "dimensionless"),
        )
    ),
)


@dataclass(frozen=True)
class SpectralMode:
    """One source-blind accepted spectral mode and its diagnostics."""

    kind: str
    degree: int
    eigenvalue: float
    nodes: NDArray[np.float64]
    first_factor: NDArray[np.float64]
    second_factor: Optional[NDArray[np.float64]]
    raw_count: int
    finite_count: int
    positive_real_count: int
    admissible_count: int
    rejected_counts: Mapping[str, int]
    relative_imaginary_part: float
    maximum_equation_residual: float
    maximum_boundary_residual: float
    normalization_residual: float

    @property
    def mass_mev(self) -> float:
        return math.sqrt(self.eigenvalue) * Z_M_INVERSE_MEV

    def to_dict(self, *, include_profile: bool = False) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "kind": self.kind,
            "degree": self.degree,
            "eigenvalue_m2_zm2": self.eigenvalue,
            "mass_MeV": self.mass_mev,
            "spectrum_accounting": {
                "raw_count": self.raw_count,
                "finite_count": self.finite_count,
                "positive_real_count": self.positive_real_count,
                "admissible_count": self.admissible_count,
                "rejected_counts": dict(self.rejected_counts),
                "selection": "lowest ascending admissible positive real eigenvalue",
                "source_value_used_for_selection": False,
            },
            "diagnostics": {
                "relative_imaginary_part": self.relative_imaginary_part,
                "maximum_equation_residual": self.maximum_equation_residual,
                "maximum_boundary_residual": self.maximum_boundary_residual,
                "normalization_residual": self.normalization_residual,
            },
        }
        if include_profile:
            payload["profile"] = {
                "u": self.nodes.tolist(),
                "first_factor": self.first_factor.tolist(),
                "second_factor": (
                    None if self.second_factor is None else self.second_factor.tolist()
                ),
            }
        return payload


def _relative_error(value: float, reference: float) -> float:
    return abs(value - reference) / max(abs(reference), 1.0e-300)


def _operator_scaled_residual(
    residual: NDArray[np.float64],
    operator_and_field_norms: Sequence[Tuple[float, float]],
) -> float:
    """Return the standard normwise backward error of a linear equation.

    Exact-endpoint Chebyshev second-derivative matrices are ill-conditioned in
    floating point.  Scaling by the operator infinity norms records whether a
    nearby pencil has the displayed profile as an exact solution without
    hiding a physical mismatch behind a pointwise cancellation.
    """

    denominator = sum(
        operator_norm * field_norm
        for operator_norm, field_norm in operator_and_field_norms
    )
    return float(np.max(np.abs(residual))) / max(denominator, 1.0e-300)


def _quadrature_data(points: int = 256) -> Tuple[NDArray[np.float64], NDArray[np.float64]]:
    nodes, weights = leggauss(points)
    return 0.5 * (nodes + 1.0), 0.5 * weights


def _mode_normalization(
    kind: str,
    nodes: NDArray[np.float64],
    first: NDArray[np.float64],
    second: Optional[NDArray[np.float64]],
    *,
    mhat: float,
) -> float:
    u, weights = _quadrature_data()
    p = np.asarray(_interpolator(nodes, first)(u), dtype=float)
    if kind in {"vector", "axial"}:
        norm_squared = float(np.sum(weights * u**3 * p**2))
    else:
        if second is None:
            raise ValueError("pion normalization requires two factors")
        q = np.asarray(_interpolator(nodes, second)(u), dtype=float)
        p_prime = np.asarray(_interpolator(nodes, first).derivative(u), dtype=float)
        w = mhat + SIGMA_HAT * u**2
        integrand = (
            u * (2.0 * p + u * p_prime) ** 2 / G5**2
            + u**3 * w**2 * (q - p) ** 2
        )
        norm_squared = float(np.sum(weights * integrand))
    if not math.isfinite(norm_squared) or norm_squared <= 0.0:
        raise RuntimeError(f"{kind} mode has non-positive normalization")
    return math.sqrt(norm_squared)


def _mode_diagnostics(
    kind: str,
    degree: int,
    eigenvalue: float,
    nodes: NDArray[np.float64],
    first: NDArray[np.float64],
    second: Optional[NDArray[np.float64]],
    *,
    mhat: float,
) -> Tuple[float, float, float]:
    dense = chebyshev_lobatto_grid(2 * degree, 0.0, 1.0)
    u = dense.nodes
    p = np.asarray(_interpolator(nodes, first)(u), dtype=float)
    p_prime = dense.first_derivative @ p
    p_second = dense.second_derivative @ p
    radial = np.divide(3.0, u, out=np.zeros_like(u), where=u > 0.0)
    w = mhat + SIGMA_HAT * u**2

    if kind in {"vector", "axial"}:
        potential = np.zeros_like(u) if kind == "vector" else G5**2 * w**2
        residual = p_second + radial * p_prime + (eigenvalue - potential) * p
        residual[0] = 4.0 * p_second[0] + (eigenvalue - potential[0]) * p[0]
        equation = _operator_scaled_residual(
            residual,
            (
                (float(np.linalg.norm(dense.second_derivative, np.inf)), float(np.max(np.abs(p)))),
                (
                    float(np.linalg.norm(np.diag(radial) @ dense.first_derivative, np.inf)),
                    float(np.max(np.abs(p))),
                ),
                (float(np.max(np.abs(eigenvalue - potential))), float(np.max(np.abs(p)))),
            ),
        )
        boundary = max(
            abs(p_prime[0]),
            abs(p_prime[-1] + 2.0 * p[-1]),
        ) / max(float(np.max(np.abs(p))), 1.0e-300)
    else:
        if second is None:
            raise ValueError("pion diagnostics require two factors")
        q = np.asarray(_interpolator(nodes, second)(u), dtype=float)
        q_prime = dense.first_derivative @ q
        potential = G5**2 * w**2
        first_residual = p_second + radial * p_prime + potential * (q - p)
        first_residual[0] = 4.0 * p_second[0] + G5**2 * mhat**2 * (q[0] - p[0])
        first_error = _operator_scaled_residual(
            first_residual,
            (
                (float(np.linalg.norm(dense.second_derivative, np.inf)), float(np.max(np.abs(p)))),
                (
                    float(np.linalg.norm(np.diag(radial) @ dense.first_derivative, np.inf)),
                    float(np.max(np.abs(p))),
                ),
                (float(np.max(potential)), float(np.max(np.abs(p)))),
                (float(np.max(potential)), float(np.max(np.abs(q)))),
            ),
        )
        first_order = 2.0 * np.eye(dense.size) + np.diag(u) @ dense.first_derivative
        second_residual = potential * (2.0 * q + u * q_prime) - eigenvalue * (
            2.0 * p + u * p_prime
        )
        second_error = _operator_scaled_residual(
            second_residual,
            (
                (
                    float(np.linalg.norm(np.diag(potential) @ first_order, np.inf)),
                    float(np.max(np.abs(q))),
                ),
                (
                    abs(eigenvalue) * float(np.linalg.norm(first_order, np.inf)),
                    float(np.max(np.abs(p))),
                ),
            ),
        )
        equation = max(first_error, second_error)
        scale = max(
            float(np.max(np.abs(p))), float(np.max(np.abs(q))), 1.0e-300
        )
        boundary = max(
            abs(p_prime[0]), abs(p_prime[-1] + 2.0 * p[-1])
        ) / scale

    norm = _mode_normalization(kind, nodes, first, second, mhat=mhat)
    return float(equation), float(boundary), abs(norm - 1.0)


def _bordered_profile_refinement(
    operator: NDArray[np.float64],
    weight: NDArray[np.float64],
    candidate: float,
    first_block_size: int,
) -> Tuple[float, NDArray[np.float64]]:
    """Refine one QZ candidate without using a literature target.

    A middle physical-equation row is replaced by ``first_factor(0)=1``.
    The omitted-row residual is then zeroed in a deterministic local bracket.
    This improves the eigenvector backward error of the singular pencil while
    retaining the source-blind ordering delivered by ``scipy.linalg.eig``.
    """

    row = first_block_size // 2

    def profile_and_residual(value: float) -> Tuple[NDArray[np.float64], float]:
        matrix = (operator - value * weight).copy()
        right_hand_side = np.zeros(matrix.shape[0])
        matrix[row] = 0.0
        matrix[row, 0] = 1.0
        right_hand_side[row] = 1.0
        profile = solve(matrix, right_hand_side, assume_a="gen")
        residual = float(((operator - value * weight) @ profile)[row])
        return np.asarray(profile, dtype=float), residual

    bracket: Optional[Tuple[float, float]] = None
    for fraction in (1.0e-6, 1.0e-5, 1.0e-4, 1.0e-3):
        lower = max(candidate * (1.0 - fraction), 1.0e-14)
        upper = candidate * (1.0 + fraction)
        _, left = profile_and_residual(lower)
        _, right = profile_and_residual(upper)
        if left == 0.0 or right == 0.0 or left * right < 0.0:
            bracket = (lower, upper)
            break
    if bracket is None:
        raise RuntimeError("could not bracket the bordered eigenvalue residual")
    root = root_scalar(
        lambda value: profile_and_residual(value)[1],
        bracket=bracket,
        method="brentq",
        xtol=1.0e-13,
        rtol=1.0e-13,
        maxiter=100,
    )
    if not root.converged:
        raise RuntimeError("bordered eigenvalue refinement did not converge")
    profile, _ = profile_and_residual(float(root.root))
    return float(root.root), profile


def solve_spectral_mode(
    kind: str,
    degree: int,
    *,
    mhat: float = M_HAT,
) -> SpectralMode:
    """Return the lowest source-blind admissible mode for one sector."""

    if kind not in {"vector", "axial", "pion"}:
        raise ValueError("kind must be vector, axial, or pion")
    if isinstance(degree, bool) or not isinstance(degree, Integral) or degree < 32:
        raise ValueError("degree must be an integer at least 32")
    if isinstance(mhat, bool) or not isinstance(mhat, Real):
        raise ValueError("mhat must be a finite non-negative real number")
    mhat = float(mhat)
    if not math.isfinite(mhat) or mhat < 0.0:
        raise ValueError("mhat must be a finite non-negative real number")

    grid = chebyshev_lobatto_grid(int(degree), 0.0, 1.0)
    u = grid.nodes
    d1 = grid.first_derivative
    d2 = grid.second_derivative
    size = grid.size
    w = mhat + SIGMA_HAT * u**2
    radial = np.divide(3.0, u, out=np.zeros_like(u), where=u > 0.0)

    if kind in {"vector", "axial"}:
        potential = np.zeros_like(u) if kind == "vector" else G5**2 * w**2
        operator = -d2 - np.diag(radial) @ d1 + np.diag(potential)
        weight = np.eye(size)
        operator[0] = d1[0]
        weight[0] = 0.0
        operator[-1] = d1[-1]
        operator[-1, -1] += 2.0
        weight[-1] = 0.0
    else:
        operator = np.zeros((2 * size, 2 * size))
        weight = np.zeros_like(operator)
        identity = np.eye(size)
        potential = G5**2 * w**2
        operator[:size, :size] = -d2 - np.diag(radial) @ d1 + np.diag(potential)
        operator[:size, size:] = -np.diag(potential)
        operator[0, :] = 0.0
        operator[0, :size] = d1[0]
        operator[size - 1, :] = 0.0
        operator[size - 1, :size] = d1[-1]
        operator[size - 1, size - 1] += 2.0
        derivative_factor = 2.0 * identity + np.diag(u) @ d1
        operator[size:, size:] = np.diag(potential) @ derivative_factor
        weight[size:, :size] = derivative_factor

    eigenvalues, eigenvectors = eig(operator, weight)
    finite = np.isfinite(eigenvalues.real) & np.isfinite(eigenvalues.imag)
    positive = finite & (eigenvalues.real > 1.0e-12)
    relative_imaginary = np.full(len(eigenvalues), math.inf)
    relative_imaginary[finite] = np.abs(eigenvalues[finite].imag) / np.maximum(
        np.abs(eigenvalues[finite].real), 1.0e-300
    )
    algebraic = positive & (relative_imaginary <= DEFAULT_IMAGINARY_TOLERANCE)
    indices = np.flatnonzero(algebraic)
    indices = indices[np.argsort(eigenvalues.real[indices])]
    residual_rejections = 0

    for index in indices:
        candidate = float(eigenvalues[index].real)
        try:
            refined_eigenvalue, vector = _bordered_profile_refinement(
                operator, weight, candidate, size
            )
        except (RuntimeError, ValueError):
            residual_rejections += 1
            continue
        first = vector[:size].copy()
        second = None if kind != "pion" else vector[size:].copy()
        combined_scale = max(
            float(np.max(np.abs(first))),
            0.0 if second is None else float(np.max(np.abs(second))),
        )
        if not math.isfinite(combined_scale) or combined_scale == 0.0:
            residual_rejections += 1
            continue
        first /= combined_scale
        if second is not None:
            second /= combined_scale

        sign_array = first[1:-1]
        nonzero = np.flatnonzero(np.abs(sign_array) > 1.0e-12)
        if len(nonzero) and sign_array[nonzero[0]] < 0.0:
            first *= -1.0
            if second is not None:
                second *= -1.0

        norm = _mode_normalization(kind, u, first, second, mhat=mhat)
        first /= norm
        if second is not None:
            second /= norm
        equation, boundary, normalization = _mode_diagnostics(
            kind,
            int(degree),
            refined_eigenvalue,
            u,
            first,
            second,
            mhat=mhat,
        )
        if equation > DEFAULT_EQUATION_TOLERANCE or boundary > DEFAULT_BOUNDARY_TOLERANCE:
            residual_rejections += 1
            continue
        return SpectralMode(
            kind=kind,
            degree=int(degree),
            eigenvalue=refined_eigenvalue,
            nodes=u.copy(),
            first_factor=first,
            second_factor=second,
            raw_count=len(eigenvalues),
            finite_count=int(np.count_nonzero(finite)),
            positive_real_count=int(np.count_nonzero(positive)),
            admissible_count=int(np.count_nonzero(algebraic)),
            rejected_counts={
                "nonfinite": int(np.count_nonzero(~finite)),
                "nonpositive_real": int(np.count_nonzero(finite & ~positive)),
                "excess_imaginary_part": int(np.count_nonzero(positive & ~algebraic)),
                "equation_or_boundary": residual_rejections,
            },
            relative_imaginary_part=float(relative_imaginary[index]),
            maximum_equation_residual=equation,
            maximum_boundary_residual=boundary,
            normalization_residual=normalization,
        )
    raise RuntimeError(f"no admissible {kind} eigenmode at degree {degree}")


def _decay_constant(mode: SpectralMode) -> float:
    endpoint = abs(2.0 * float(mode.first_factor[0]))
    return Z_M_INVERSE_MEV * math.sqrt(endpoint / G5)


def _rho_pion_coupling(vector: SpectralMode, pion: SpectralMode) -> float:
    u, weights = _quadrature_data()
    vector_factor = np.asarray(
        _interpolator(vector.nodes, vector.first_factor)(u), dtype=float
    )
    p_interp = _interpolator(pion.nodes, pion.first_factor)
    p = np.asarray(p_interp(u), dtype=float)
    p_prime = np.asarray(p_interp.derivative(u), dtype=float)
    if pion.second_factor is None:
        raise ValueError("pion coupling requires the pion factor")
    q = np.asarray(_interpolator(pion.nodes, pion.second_factor)(u), dtype=float)
    w = M_HAT + SIGMA_HAT * u**2
    pion_density = (
        u * (2.0 * p + u * p_prime) ** 2 / G5**2
        + u**3 * w**2 * (q - p) ** 2
    )
    physical_vector = u**2 * vector_factor
    return abs(float(G5 * np.sum(weights * physical_vector * pion_density)))


def solve_axial_zero_dop853(epsilon: Real, *, mhat: float = M_HAT) -> float:
    """Return regulated ``f_pi`` from backward IR-to-UV DOP853 integration."""

    epsilon = _validate_epsilon(epsilon)

    def equation(u: float, fields: NDArray[np.float64]) -> NDArray[np.float64]:
        value, derivative = fields
        w = mhat + SIGMA_HAT * u**2
        return np.array(
            [derivative, derivative / u + G5**2 * w**2 * value]
        )

    solution = solve_ivp(
        equation,
        (1.0, epsilon),
        np.array([1.0, 0.0]),
        method="DOP853",
        rtol=1.0e-12,
        atol=1.0e-14,
    )
    if not solution.success:
        raise RuntimeError(solution.message)
    value = float(solution.y[0, -1])
    derivative = float(solution.y[1, -1])
    slope = derivative / value
    if slope >= 0.0:
        raise RuntimeError("axial zero mode has non-negative regulated UV slope")
    return Z_M_INVERSE_MEV * math.sqrt(-slope / (G5**2 * epsilon))


def _validate_epsilon(value: Real) -> float:
    if isinstance(value, bool) or not isinstance(value, Real):
        raise ValueError("epsilon must be a finite fraction in (0, 1)")
    resolved = float(value)
    if not math.isfinite(resolved) or not 0.0 < resolved < 1.0:
        raise ValueError("epsilon must be a finite fraction in (0, 1)")
    return resolved


def _finite_mesh(epsilon: float, points: int = 600) -> NDArray[np.float64]:
    split = max(1.0e-3, 20.0 * epsilon)
    left = np.geomspace(epsilon, split, points // 2)
    right = np.linspace(split, 1.0, points // 2 + 1)
    return np.unique(np.concatenate((left, right)))


def _axial_zero_bvp(epsilon: float) -> Tuple[Any, float]:
    u = _finite_mesh(epsilon)

    def equation(x: NDArray[np.float64], fields: NDArray[np.float64]) -> NDArray[np.float64]:
        value, derivative = fields
        w = M_HAT + SIGMA_HAT * x**2
        return np.vstack((derivative, derivative / x + G5**2 * w**2 * value))

    def boundary(left: NDArray[np.float64], right: NDArray[np.float64]) -> NDArray[np.float64]:
        return np.array([left[0] - 1.0, right[1]])

    solution = solve_bvp(
        equation,
        boundary,
        u,
        np.vstack((1.0 - 0.5 * u**2, -u)),
        tol=1.0e-9,
        max_nodes=50_000,
    )
    if not solution.success:
        raise RuntimeError(solution.message)
    derivative = float(solution.sol(epsilon)[1])
    f_pi = Z_M_INVERSE_MEV * math.sqrt(-derivative / (G5**2 * epsilon))
    return solution, f_pi


def _axial_mode_bvp(epsilon: float) -> Any:
    u = _finite_mesh(epsilon)

    def equation(x: NDArray[np.float64], fields: NDArray[np.float64], parameter: NDArray[np.float64]) -> NDArray[np.float64]:
        value, derivative = fields
        mass = parameter[0]
        w = M_HAT + SIGMA_HAT * x**2
        return np.vstack((derivative, derivative / x - (mass**2 - G5**2 * w**2) * value))

    def boundary(left: NDArray[np.float64], right: NDArray[np.float64], parameter: NDArray[np.float64]) -> NDArray[np.float64]:
        del parameter
        return np.array([left[0], right[1], right[0] - 1.0])

    guess_mass = 4.2
    value = u * j1(guess_mass * u)
    solution = solve_bvp(
        equation,
        boundary,
        u,
        np.vstack((value, np.gradient(value, u))),
        p=np.array([guess_mass]),
        tol=1.0e-8,
        max_nodes=50_000,
    )
    if not solution.success:
        raise RuntimeError(solution.message)
    return solution


def _pion_mode_bvp(epsilon: float) -> Any:
    u = _finite_mesh(epsilon, points=1000)

    def equation(x: NDArray[np.float64], fields: NDArray[np.float64], parameter: NDArray[np.float64]) -> NDArray[np.float64]:
        phi, derivative, pion = fields
        mass = parameter[0]
        v = x * (M_HAT + SIGMA_HAT * x**2)
        return np.vstack(
            (
                derivative,
                derivative / x - G5**2 * v**2 * (pion - phi) / x**2,
                mass**2 * x**2 * derivative / (G5**2 * v**2),
            )
        )

    def boundary(left: NDArray[np.float64], right: NDArray[np.float64], parameter: NDArray[np.float64]) -> NDArray[np.float64]:
        del parameter
        return np.array([left[0], left[2], right[1], right[0] - 1.0])

    guess_mass = 0.45
    phi = u**2 * (2.0 - u**2)
    derivative = 4.0 * u * (1.0 - u**2)
    pion = (guess_mass**2 / (G5**2 * M_HAT**2)) * u**2
    solution = solve_bvp(
        equation,
        boundary,
        u,
        np.vstack((phi, derivative, pion)),
        p=np.array([guess_mass]),
        tol=1.0e-8,
        max_nodes=100_000,
    )
    if not solution.success:
        raise RuntimeError(solution.message)
    return solution


def _quad(function: Any, epsilon: float) -> float:
    value, _ = quad(
        function, epsilon, 1.0, epsabs=1.0e-11, epsrel=1.0e-11, limit=400
    )
    return float(value)


def _independent_level(epsilon: float) -> Dict[str, Any]:
    zero, f_pi_bvp = _axial_zero_bvp(epsilon)
    f_pi_dop853 = solve_axial_zero_dop853(epsilon)
    axial = _axial_mode_bvp(epsilon)
    pion = _pion_mode_bvp(epsilon)
    root = float(jn_zeros(0, 1)[0])

    def vector_profile(x: float) -> float:
        return x * float(j1(root * x))

    vector_norm = math.sqrt(_quad(lambda x: vector_profile(x) ** 2 / x, epsilon))
    axial_norm = math.sqrt(_quad(lambda x: axial.sol(x)[0] ** 2 / x, epsilon))
    pion_norm = math.sqrt(
        _quad(
            lambda x: (
                pion.sol(x)[1] ** 2 / (G5**2 * x)
                + (M_HAT * x + SIGMA_HAT * x**3) ** 2
                * (pion.sol(x)[2] - pion.sol(x)[0]) ** 2
                / x**3
            ),
            epsilon,
        )
    )
    coupling = G5 * _quad(
        lambda x: vector_profile(x)
        / vector_norm
        * (
            (pion.sol(x)[1] / pion_norm) ** 2 / (G5**2 * x)
            + (M_HAT * x + SIGMA_HAT * x**3) ** 2
            * ((pion.sol(x)[2] - pion.sol(x)[0]) / pion_norm) ** 2
            / x**3
        ),
        epsilon,
    )
    return {
        "epsilon": epsilon,
        "f_pi_bvp_MeV": f_pi_bvp,
        "f_pi_dop853_MeV": f_pi_dop853,
        "f_pi_route_relative_difference": _relative_error(f_pi_bvp, f_pi_dop853),
        "m_a1_MeV": float(axial.p[0]) * Z_M_INVERSE_MEV,
        "sqrt_F_a1_MeV": Z_M_INVERSE_MEV
        * math.sqrt(abs(float(axial.sol(epsilon)[1])) / (axial_norm * epsilon * G5)),
        "m_pi_MeV": float(pion.p[0]) * Z_M_INVERSE_MEV,
        "g_rho_pi_pi": abs(float(coupling)),
        "maximum_bvp_rms_residual": max(
            float(np.max(zero.rms_residuals)),
            float(np.max(axial.rms_residuals)),
            float(np.max(pion.rms_residuals)),
        ),
    }


def _spectral_observables(
    degree: int, *, mhat: float = M_HAT
) -> Tuple[Dict[str, float], Mapping[str, SpectralMode]]:
    vector = solve_spectral_mode("vector", degree, mhat=mhat)
    axial = solve_spectral_mode("axial", degree, mhat=mhat)
    pion = solve_spectral_mode("pion", degree, mhat=mhat)
    f_pi = solve_axial_zero_dop853(SOURCE_EPSILON, mhat=mhat)
    observables = {
        "m_pi_MeV": pion.mass_mev,
        "m_rho_MeV": vector.mass_mev,
        "m_a1_MeV": axial.mass_mev,
        "f_pi_MeV": f_pi,
        "sqrt_F_rho_MeV": _decay_constant(vector),
        "sqrt_F_a1_MeV": _decay_constant(axial),
        "g_rho_pi_pi": _rho_pion_coupling(vector, pion),
    }
    return observables, {"vector": vector, "axial": axial, "pion": pion}


def _maximum_numeric_difference(left: Any, right: Any) -> float:
    if isinstance(left, Mapping) and isinstance(right, Mapping):
        if set(left) != set(right):
            return math.inf
        return max(
            (_maximum_numeric_difference(left[key], right[key]) for key in left),
            default=0.0,
        )
    if isinstance(left, list) and isinstance(right, list):
        if len(left) != len(right):
            return math.inf
        return max(
            (_maximum_numeric_difference(a, b) for a, b in zip(left, right)),
            default=0.0,
        )
    if isinstance(left, (int, float)) and isinstance(right, (int, float)):
        return abs(float(left) - float(right)) / max(
            abs(float(left)), abs(float(right)), 1.0
        )
    return 0.0 if left == right else math.inf


def _verify_once() -> Dict[str, Any]:
    levels: List[Dict[str, Any]] = []
    modes_by_degree: Dict[int, Mapping[str, SpectralMode]] = {}
    for degree in DEFAULT_DEGREES:
        observables, modes = _spectral_observables(degree)
        modes_by_degree[degree] = modes
        levels.append(
            {
                "degree": degree,
                "observables": observables,
                "modes": {
                    key: value.to_dict(include_profile=degree == DEFAULT_DEGREES[-1])
                    for key, value in modes.items()
                },
            }
        )

    refinement: Dict[str, Any] = {}
    ordering_failures = 0
    for key in TABLE_TARGETS:
        earlier = _relative_error(
            levels[1]["observables"][key], levels[0]["observables"][key]
        )
        final = _relative_error(
            levels[2]["observables"][key], levels[1]["observables"][key]
        )
        ordered = earlier <= DEFAULT_REFINEMENT_ORDER_FLOOR or final < earlier
        if not ordered:
            ordering_failures += 1
        refinement[key] = {
            "N64_to_N80": earlier,
            "N80_to_N96": final,
            "ordered_when_resolved": ordered,
        }

    independent = [_independent_level(epsilon) for epsilon in DEFAULT_DIAGNOSTIC_EPSILONS]
    cross_keys = ("m_pi_MeV", "m_a1_MeV", "sqrt_F_a1_MeV", "g_rho_pi_pi")
    cutoff_changes = {
        key: _relative_error(independent[-1][key], independent[-2][key])
        for key in cross_keys
    }
    final_observables = levels[-1]["observables"]
    cross_differences = {
        key: _relative_error(independent[-1][key], final_observables[key])
        for key in cross_keys
    }
    fpi_log_slopes = []
    for coarse, fine in zip(independent[:-1], independent[1:]):
        ratio = (
            fine["f_pi_dop853_MeV"] ** 2 - coarse["f_pi_dop853_MeV"] ** 2
        ) / (M_Q_MEV**2 * math.log(2.0))
        fpi_log_slopes.append(ratio)

    gmor: List[Dict[str, float]] = []
    sigma_mev_cubed = SIGMA_CUBE_ROOT_MEV**3
    for factor in DEFAULT_GMOR_FACTORS:
        mhat = M_HAT * factor
        pion = solve_spectral_mode("pion", DEFAULT_DEGREES[-1], mhat=mhat)
        f_pi = solve_axial_zero_dop853(SOURCE_EPSILON, mhat=mhat)
        m_q = M_Q_MEV * factor
        ratio = pion.mass_mev**2 * f_pi**2 / (2.0 * m_q * sigma_mev_cubed)
        gmor.append(
            {
                "m_q_factor": factor,
                "m_q_MeV": m_q,
                "m_pi_MeV": pion.mass_mev,
                "f_pi_MeV": f_pi,
                "R_GMOR": ratio,
                "absolute_error": abs(ratio - 1.0),
            }
        )

    protected_shooting = solve_hard_wall_spectrum(
        HardWallConfig(), num_modes=4, method="shooting"
    )
    protected_collocation = solve_hard_wall_spectrum(
        HardWallConfig(), num_modes=4, method="collocation"
    )
    protected_difference = float(
        np.max(
            np.abs(
                protected_shooting.mass_ratios[1:]
                - protected_collocation.mass_ratios[1:]
            )
            / protected_collocation.mass_ratios[1:]
        )
    )
    vector_anchor = _relative_error(
        math.sqrt(modes_by_degree[96]["vector"].eigenvalue),
        float(jn_zeros(0, 1)[0]),
    )

    table = []
    for key, target in TABLE_TARGETS.items():
        computed = final_observables[key]
        table.append(
            {
                "observable": key,
                "source_role": "source fit target" if key in SOURCE_FIT_TARGETS else "source prediction",
                "computed": computed,
                "target": target,
                "relative_error": _relative_error(computed, target),
            }
        )

    summary = {
        "source_convention_error": max(
            _relative_error(G5**2, 12.0 * math.pi**2 / N_C),
            _relative_error(G5, 2.0 * math.pi),
        ),
        "vector_anchor_error": vector_anchor,
        "protected_vector_passed": bool(
            protected_shooting.to_dict()["passed"]
            and protected_collocation.to_dict()["passed"]
        ),
        "protected_vector_cross_route_error": protected_difference,
        "maximum_equation_residual": max(
            mode.maximum_equation_residual
            for mode in modes_by_degree[96].values()
        ),
        "maximum_boundary_residual": max(
            mode.maximum_boundary_residual for mode in modes_by_degree[96].values()
        ),
        "maximum_normalization_residual": max(
            mode.normalization_residual for mode in modes_by_degree[96].values()
        ),
        "maximum_relative_imaginary_part": max(
            mode.relative_imaginary_part for mode in modes_by_degree[96].values()
        ),
        "maximum_final_refinement": max(
            item["N80_to_N96"] for item in refinement.values()
        ),
        "refinement_ordering_failures": ordering_failures,
        "maximum_cutoff_change": max(cutoff_changes.values()),
        "maximum_cross_route_difference": max(cross_differences.values()),
        "maximum_fpi_route_difference": max(
            row["f_pi_route_relative_difference"] for row in independent
        ),
        "maximum_fpi_log_slope_error": max(abs(value - 1.0) for value in fpi_log_slopes),
        "maximum_table_error": max(row["relative_error"] for row in table),
        "gmor_ordering_failures": sum(
            1
            for earlier, later in zip(gmor[:-1], gmor[1:])
            if earlier["absolute_error"] >= 1.0e-5
            and not later["absolute_error"] < earlier["absolute_error"]
        ),
        "final_gmor_error": gmor[-1]["absolute_error"],
    }
    state = {
        "observables": final_observables,
        "gmor": [row["R_GMOR"] for row in gmor],
        "independent": [
            {key: row[key] for key in ("f_pi_bvp_MeV", "f_pi_dop853_MeV", *cross_keys)}
            for row in independent
        ],
    }
    return {
        "levels": levels,
        "refinement": refinement,
        "independent": independent,
        "cutoff_changes": cutoff_changes,
        "cross_route_differences": cross_differences,
        "fpi_log_slope_ratios": fpi_log_slopes,
        "gmor": gmor,
        "table": table,
        "summary": summary,
        "determinism_state": state,
    }


def verify_hard_wall_chiral(
    *, repeat_for_determinism: bool = True
) -> VerificationRecord:
    """Run the frozen Phase 3 contract and return inspectable evidence."""

    first = _verify_once()
    determinism_error: Optional[float] = None
    if repeat_for_determinism:
        second = _verify_once()
        determinism_error = _maximum_numeric_difference(
            first["determinism_state"], second["determinism_state"]
        )
    summary = first["summary"]
    checks = (
        AcceptanceCheck(
            "source-conventions",
            "g5 and the frozen Model A parameters match the public source contract",
            summary["source_convention_error"] <= 1.0e-13,
            summary["source_convention_error"],
            "relative error <= 1e-13 and no refit",
        ),
        AcceptanceCheck(
            "protected-vector-anchor",
            "the existing hard-wall vector routes pass and the Phase 3 rho matches J0",
            summary["protected_vector_passed"]
            and summary["protected_vector_cross_route_error"] <= 1.0e-3
            and summary["vector_anchor_error"] <= 1.0e-6,
            max(summary["protected_vector_cross_route_error"], summary["vector_anchor_error"]),
            "protected routes pass; cross route <= 1e-3; J0 anchor <= 1e-6",
        ),
        AcceptanceCheck(
            "direct-equations-and-boundaries",
            "twice-denser equations and all endpoint conditions",
            summary["maximum_equation_residual"] <= DEFAULT_EQUATION_TOLERANCE
            and summary["maximum_boundary_residual"] <= DEFAULT_BOUNDARY_TOLERANCE,
            max(summary["maximum_equation_residual"], summary["maximum_boundary_residual"]),
            "equations <= 1e-7 and boundaries <= 1e-8",
        ),
        AcceptanceCheck(
            "admissible-spectra",
            "accepted eigenvalues are finite positive and source-blind with negligible imaginary part",
            summary["maximum_relative_imaginary_part"] <= DEFAULT_IMAGINARY_TOLERANCE,
            summary["maximum_relative_imaginary_part"],
            "relative imaginary part <= 1e-10",
        ),
        AcceptanceCheck(
            "normalization-and-extraction",
            "vector axial and pion normalizations and factored UV extraction",
            summary["maximum_normalization_residual"] <= DEFAULT_NORMALIZATION_TOLERANCE,
            summary["maximum_normalization_residual"],
            "normalization residual <= 1e-8",
        ),
        AcceptanceCheck(
            "spectral-refinement",
            "all seven observables stabilize from N=64 through N=96",
            summary["maximum_final_refinement"] <= DEFAULT_REFINEMENT_TOLERANCE
            and summary["refinement_ordering_failures"] == 0,
            summary["maximum_final_refinement"],
            "N80-to-N96 <= 2e-4 and zero resolved ordering failures",
        ),
        AcceptanceCheck(
            "independent-normalizable-routes",
            "finite-cutoff axial and pion quantities stabilize and agree with spectral values",
            summary["maximum_cutoff_change"] <= DEFAULT_CUTOFF_TOLERANCE
            and summary["maximum_cross_route_difference"] <= DEFAULT_INDEPENDENT_TOLERANCE,
            max(summary["maximum_cutoff_change"], summary["maximum_cross_route_difference"]),
            "cutoff change <= 2e-4 and cross-route difference <= 1e-3",
        ),
        AcceptanceCheck(
            "regulated-fpi",
            "DOP853 and solve_bvp agree and reproduce the analytic mq-squared UV logarithm",
            summary["maximum_fpi_route_difference"] <= DEFAULT_FPI_ROUTE_TOLERANCE
            and summary["maximum_fpi_log_slope_error"] <= DEFAULT_FPI_LOG_SLOPE_TOLERANCE,
            max(summary["maximum_fpi_route_difference"], summary["maximum_fpi_log_slope_error"]),
            "route difference <= 1e-7 and log-slope error <= 1e-5",
        ),
        AcceptanceCheck(
            "table-ii-reproduction",
            "all seven Model A entries reproduce the rounded source table",
            summary["maximum_table_error"] <= DEFAULT_TABLE_TOLERANCE,
            summary["maximum_table_error"],
            "every relative error <= 1%",
        ),
        AcceptanceCheck(
            "gmor-limit",
            "the GMOR ratio approaches one under four quark-mass halvings",
            summary["gmor_ordering_failures"] == 0
            and summary["final_gmor_error"] <= DEFAULT_GMOR_TOLERANCE,
            summary["final_gmor_error"],
            "zero ordering failures and final absolute error <= 1%",
        ),
        AcceptanceCheck(
            "determinism",
            "duplicate complete runs agree in all physical observables",
            determinism_error is not None
            and determinism_error <= DEFAULT_DETERMINISM_TOLERANCE,
            determinism_error,
            "maximum scaled difference <= 1e-11",
        ),
    )
    results = {
        key: first[key]
        for key in (
            "levels",
            "refinement",
            "independent",
            "cutoff_changes",
            "cross_route_differences",
            "fpi_log_slope_ratios",
            "gmor",
            "table",
            "summary",
        )
    }
    results["determinism"] = {
        "repeat_enabled": repeat_for_determinism,
        "maximum_scaled_difference": determinism_error,
    }
    record = VerificationRecord(
        definition=HARD_WALL_CHIRAL_DEFINITION,
        configuration={
            "N_c": N_C,
            "g5": G5,
            "z_m_inverse_MeV": Z_M_INVERSE_MEV,
            "m_q_MeV": M_Q_MEV,
            "sigma_cube_root_MeV": SIGMA_CUBE_ROOT_MEV,
            "spectral_degrees": list(DEFAULT_DEGREES),
            "diagnostic_epsilons": list(DEFAULT_DIAGNOSTIC_EPSILONS),
            "source_epsilon_z_MeV_inverse": SOURCE_EPSILON_Z_MEV_INVERSE,
            "source_epsilon_dimensionless": SOURCE_EPSILON,
            "gmor_mq_factors": list(DEFAULT_GMOR_FACTORS),
            "fit_performed": False,
        },
        numerical_method={
            "primary_route": (
                "exact-endpoint UV-factorized Chebyshev generalized "
                "eigenproblems with source-blind bordered refinement"
            ),
            "normalizable_eigensolver": "scipy.linalg.eig",
            "eigenpair_refinement": (
                "scipy.linalg.solve bordered profile and scipy.optimize.root_scalar "
                "on the omitted-row residual in a deterministic local QZ bracket"
            ),
            "axial_zero_route": "backward scipy.integrate.solve_ivp(method='DOP853')",
            "independent_route": "scipy.integrate.solve_bvp on three finite cutoffs",
            "quadrature": "256-point numpy.polynomial.legendre.leggauss",
            "equation_residual_scaling": (
                "twice-denser normwise operator backward error in the infinity norm"
            ),
            "source_based_mode_selection": False,
            "full_v_squared_retained": True,
        },
        results=results,
        acceptance_checks=checks,
        software_versions=runtime_versions(),
        scope=(
            "AI-assisted, owner-approved numerical reproduction of the public "
            "two-flavor hard-wall chiral Model A "
            "calculation and Table II. The three source fit targets are labeled "
            "separately from four source predictions. Passing is not empirical "
            "validation of QCD, the hard wall, or omitted higher operators."
        ),
        extra={
            "primary_source": {
                "id": SOURCE_ID,
                "doi": "10.1103/PhysRevLett.95.261602",
                "pdf_sha256": SOURCE_PDF_SHA256,
                "source_archive_sha256": SOURCE_ARCHIVE_SHA256,
                "equations_in_scope": ["(1)-(3)", "(5)", "(11)", "(14)", "(16)-(20)", "(22)"],
                "table_in_scope": "Table II Model A",
                "source_figure_in_scope": False,
            },
            "contract_review": {
                "review_state": "approved",
                "reviewed_by": "Xin-Yi Liu",
                "reviewed_on": "2026-08-20",
                "amendments": ["R1 explicit public-source regulator", "R2 axial-zero-mode method and UV-log gate", "R3 bounded local resume"],
            },
            "result_review_state": "approved",
            "result_reviewed_by": "Xin-Yi Liu",
            "result_reviewed_on": "2026-08-20",
            "generated_by_ai": True,
        },
    )
    json.dumps(record.to_dict(), allow_nan=False, sort_keys=True)
    return record


def _save_plot(payload: Mapping[str, Any], path: Path) -> None:
    try:
        import matplotlib

        matplotlib.use("Agg")
        from matplotlib import pyplot as plt
    except ImportError as exc:
        raise RuntimeError(
            "Matplotlib is required for --output-dir; install holoforge[plot]"
        ) from exc

    table = payload["results"]["table"]
    labels = [row["observable"].replace("_MeV", "") for row in table]
    ratios = [row["computed"] / row["target"] for row in table]
    colors = ["#2962ff" if row["source_role"] == "source fit target" else "#00897b" for row in table]
    gmor = payload["results"]["gmor"]
    figure, axes = plt.subplots(1, 2, figsize=(12.0, 4.8), constrained_layout=True)
    axes[0].bar(np.arange(len(labels)), ratios, color=colors)
    axes[0].axhline(1.0, color="black", linewidth=1.2)
    axes[0].axhspan(0.99, 1.01, color="0.85", alpha=0.5, label="1% gate")
    axes[0].set_ylim(0.985, 1.015)
    axes[0].set_xticks(np.arange(len(labels)), labels, rotation=35, ha="right")
    axes[0].set_ylabel("HoloForge / source Model A")
    axes[0].set_title("Table II reproduction")
    axes[0].scatter([], [], color="#2962ff", label="source fit target")
    axes[0].scatter([], [], color="#00897b", label="source prediction")
    axes[0].legend(fontsize=8)
    axes[1].plot(
        [row["m_q_factor"] for row in gmor],
        [row["R_GMOR"] for row in gmor],
        marker="o",
        color="#6a1b9a",
    )
    axes[1].axhline(1.0, color="black", linestyle="--", linewidth=1.2)
    axes[1].set_xscale("log", base=2)
    axes[1].invert_xaxis()
    axes[1].set_xlabel(r"$m_q/m_q^{\rm Model\ A}$")
    axes[1].set_ylabel(r"$m_\pi^2 f_\pi^2/(2m_q\sigma)$")
    axes[1].set_title("GMOR approach")
    figure.suptitle("HoloForge hard-wall chiral verification (not a source figure)")
    figure.savefig(path, dpi=180)
    plt.close(figure)


def save_hard_wall_chiral_artifacts(
    record: VerificationRecord, output_directory: Path
) -> Mapping[str, Path]:
    """Save strict JSON, combined Table/GMOR CSV, and verification plot."""

    directory = Path(output_directory)
    directory.mkdir(parents=True, exist_ok=True)
    paths = {
        "json": directory / "hard-wall-chiral-result.json",
        "csv": directory / "hard-wall-chiral-evidence.csv",
        "plot": directory / "hard-wall-chiral-verification.png",
    }
    existing = [path for path in paths.values() if path.exists()]
    if existing:
        raise ValueError(
            "refusing to overwrite existing artifact: "
            + ", ".join(str(path) for path in existing)
        )
    payload = record.to_dict()
    paths["json"].write_text(
        json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    rows = ["section,identifier,computed,target,error_or_factor,source_role"]
    for row in payload["results"]["table"]:
        rows.append(
            f"table,{row['observable']},{row['computed']:.17g},{row['target']:.17g},"
            f"{row['relative_error']:.17g},{row['source_role']}"
        )
    for row in payload["results"]["gmor"]:
        rows.append(
            f"gmor,R_GMOR,{row['R_GMOR']:.17g},1,{row['m_q_factor']:.17g},derived limit check"
        )
    paths["csv"].write_text("\n".join(rows) + "\n", encoding="utf-8")
    _save_plot(payload, paths["plot"])
    return paths


__all__ = [
    "DEFAULT_DEGREES",
    "HARD_WALL_CHIRAL_DEFINITION",
    "SOURCE_ARCHIVE_SHA256",
    "SOURCE_PDF_SHA256",
    "SpectralMode",
    "save_hard_wall_chiral_artifacts",
    "solve_axial_zero_dop853",
    "solve_spectral_mode",
    "verify_hard_wall_chiral",
]
