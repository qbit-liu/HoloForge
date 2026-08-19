"""Coupled spectral control benchmark for the Gubser--Rocha charged EMD brane.

The primary route solves the four Einstein--Maxwell--dilaton background
equations on an exact Chebyshev--Gauss--Lobatto interval after factoring the
known asymptotic powers.  The closed-form source solution is used only as an
independent verification target, never as a charged initial guess.  Agreement
verifies this implementation of a top-down consistent-truncation background;
it does not establish stability, a Fermi liquid, QCD, empirical validity, or
the paper's separate charged-fermion result.
"""

from __future__ import annotations

from dataclasses import dataclass
import inspect
import json
import math
from numbers import Integral, Real
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple

import numpy as np
from numpy.typing import NDArray
from scipy.interpolate import BarycentricInterpolator
from scipy.optimize import least_squares, root

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


SOURCE_ID = "arXiv:0911.2898v2"
SOURCE_PDF_SHA256 = (
    "7a6fadd4c420caaa443fb6b47c770436638bfb95ecf55b1bb1232c80421f7e97"
)
SOURCE_ARCHIVE_SHA256 = (
    "4b024dab3abe6d2b4f3f58830e246771a1e6934690c9b7b582ae9e4e496cbe66"
)
DEFAULT_REPORTED_XI = (0.0, 0.5, 1.0, 2.0, 4.0, 8.0, 16.0)
DEFAULT_CONTINUATION_XI = (
    0.0,
    0.25,
    0.5,
    0.75,
    1.0,
    1.5,
    2.0,
    3.0,
    4.0,
    6.0,
    8.0,
    12.0,
    16.0,
)
DEFAULT_DEGREES = (40, 60, 80)
DEFAULT_POLISH_MAXIMUM_EVALUATIONS = 32
DEFAULT_COLLOCATION_TOLERANCE = 1.0e-9
DEFAULT_EQUATION_TOLERANCE = 1.0e-7
DEFAULT_CONSTRAINT_TOLERANCE = 1.0e-7
DEFAULT_BOUNDARY_TOLERANCE = 1.0e-8
DEFAULT_FLUX_TOLERANCE = 1.0e-8
DEFAULT_FIELD_TOLERANCE = 2.0e-7
DEFAULT_REFINEMENT_TOLERANCE = 2.0e-6
DEFAULT_REFINEMENT_ORDER_FLOOR = 5.0e-10
DEFAULT_THERMODYNAMIC_TOLERANCE = 2.0e-7
DEFAULT_EOS_TOLERANCE = 2.0e-7
DEFAULT_LOW_TEMPERATURE_IDENTITY_TOLERANCE = 2.0e-6
DEFAULT_LOW_TEMPERATURE_FIT_TOLERANCE = 2.0e-5
DEFAULT_NEUTRAL_TOLERANCE = 1.0e-10
DEFAULT_DETERMINISM_TOLERANCE = 1.0e-12
_MAXWELL_EXPONENT = math.sqrt(2.0 / 3.0)


_BARYCENTRIC_RANDOM_KEYWORD = (
    "rng"
    if "rng" in inspect.signature(BarycentricInterpolator).parameters
    else "random_state"
)


def _barycentric_interpolator(
    nodes: NDArray[np.float64],
    values: NDArray[np.float64],
) -> BarycentricInterpolator:
    """Construct a deterministic interpolator across supported SciPy versions."""

    return BarycentricInterpolator(
        nodes,
        values,
        **{_BARYCENTRIC_RANDOM_KEYWORD: 0},
    )


GUBSER_ROCHA_DEFINITION = BenchmarkDefinition(
    identifier="gubser-rocha-emd",
    support_level="reproduced",
    background=BackgroundSpec(
        identifier="five-dimensional-gubser-rocha-charged-dilatonic-brane",
        dimension=5,
        coordinate="u = z/z_H in [0, 1]",
        description=(
            "Top-down-derived homogeneous equal-charge asymptotically AdS "
            "Einstein--Maxwell--dilaton black brane with L = r_H = 1, used "
            "as a control for the coupled spectral infrastructure."
        ),
    ),
    equations=(
        EquationSpec(
            identifier="warp-equation",
            kind="coupled nonlinear boundary-value equation",
            dependent_fields=("A", "phi"),
            expression="A'' - A'^2 + phi'^2/6 = 0",
            source_reference=(
                "Gubser and Rocha, arXiv:0911.2898v2, Eq. (1), "
                "derived in conformal gauge"
            ),
        ),
        EquationSpec(
            identifier="blackening-equation",
            kind="coupled nonlinear boundary-value equation",
            dependent_fields=("f", "A", "Phi", "phi"),
            expression="f'' + 3 A' f' - exp(-2A) Z Phi'^2 = 0",
            source_reference=(
                "Gubser and Rocha, arXiv:0911.2898v2, Eq. (1), "
                "derived in conformal gauge"
            ),
        ),
        EquationSpec(
            identifier="maxwell-equation",
            kind="coupled nonlinear boundary-value equation",
            dependent_fields=("Phi", "A", "phi"),
            expression="Phi'' + [A' + (Z_phi/Z) phi'] Phi' = 0",
            source_reference=(
                "Gubser and Rocha, arXiv:0911.2898v2, Eq. (1), "
                "derived in conformal gauge"
            ),
        ),
        EquationSpec(
            identifier="scalar-equation",
            kind="coupled nonlinear boundary-value equation",
            dependent_fields=("phi", "A", "f", "Phi"),
            expression=(
                "f phi'' + (3 A' f + f') phi' - exp(2A) V_phi "
                "+ exp(-2A) Z_phi Phi'^2/2 = 0"
            ),
            source_reference=(
                "Gubser and Rocha, arXiv:0911.2898v2, Eq. (1), "
                "derived in conformal gauge"
            ),
        ),
        EquationSpec(
            identifier="einstein-constraint",
            kind="independent radial constraint",
            dependent_fields=("A", "f", "phi", "Phi"),
            expression=(
                "6 A' f' + f(24 A'^2 - phi'^2) + 2 exp(2A) V "
                "+ exp(-2A) Z Phi'^2 = 0"
            ),
            source_reference=(
                "Gubser and Rocha, arXiv:0911.2898v2, Eq. (1), "
                "derived in conformal gauge"
            ),
        ),
    ),
    boundary_conditions=(
        BoundaryConditionSpec(
            field="A",
            location="u = 0",
            role="asymptotically AdS boundary metric",
            expression="A = -log(z) + u^4 a(u)",
            interpretation="The source metric and lower forbidden powers are fixed.",
        ),
        BoundaryConditionSpec(
            field="f",
            location="u = 0 and u = 1",
            role="normalized boundary and regular horizon",
            expression="f = 1 - u^4 b(u), b'(0) = 0, b(1) = 1",
            interpretation="Both exact endpoints are collocation nodes.",
        ),
        BoundaryConditionSpec(
            field="phi",
            location="u = 0 and u = 1",
            role="zero BF-bound logarithmic source and regular horizon",
            expression="phi = u^2 p(u), p'(0) = 0; retain scalar equation at u=1",
            interpretation="The z^2 coefficient is a response, not a source.",
        ),
        BoundaryConditionSpec(
            field="Phi",
            location="u = 0 and u = 1",
            role="fixed chemical-potential source and regular horizon gauge",
            expression="Phi = -Omega + u^2 v(u), v(1) = Omega",
            interpretation="Phi(0) = -Omega and Phi(1) = 0.",
        ),
    ),
    solvers=(
        SolverSpec(
            problem_type="coupled nonlinear EMD boundary-value problem",
            library_function="scipy.optimize.root and scipy.optimize.least_squares",
            method=(
                "Chebyshev--Gauss--Lobatto collocation, hybr solve, frozen "
                "thirty-two-evaluation TRF polish"
            ),
            description=(
                "Neutral initialization followed by deterministic charge and "
                "degree continuation; no shooting or charged exact seed."
            ),
        ),
    ),
    observables=(
        ObservableSpec(
            identifier="temperature",
            symbol="T",
            extraction="absolute exact-horizon derivative abs(f'(z_H))/(4 pi)",
            normalization="L = r_H = 1",
        ),
        ObservableSpec(
            identifier="entropy-density",
            symbol="hat s",
            extraction="exp(3 A(z_H))/(2 pi)",
            normalization="source hatted density with L = r_H = 1",
        ),
        ObservableSpec(
            identifier="charge-density",
            symbol="hat rho",
            extraction="abs(-exp(A) Z Phi')/(8 pi^2)",
            normalization="source hatted density with L = r_H = 1",
        ),
        ObservableSpec(
            identifier="energy-density",
            symbol="hat epsilon",
            extraction="3 mu_bh/(8 pi^2) from the boundary f coefficient",
            normalization="source hatted density with L = r_H = 1",
        ),
    ),
)


@dataclass(frozen=True)
class EMDSolverConfig:
    """Frozen maintained-library controls for one coupled solve."""

    root_tolerance: float = 1.0e-11
    maximum_evaluations_factor: int = 500
    polish_tolerance: float = 1.0e-14
    polish_maximum_evaluations: int = DEFAULT_POLISH_MAXIMUM_EVALUATIONS
    oversampling_factor: int = 2

    def __post_init__(self) -> None:
        _validate_positive("root_tolerance", self.root_tolerance)
        _validate_integer(
            "maximum_evaluations_factor",
            self.maximum_evaluations_factor,
            minimum=1,
        )
        _validate_positive("polish_tolerance", self.polish_tolerance)
        _validate_integer(
            "polish_maximum_evaluations",
            self.polish_maximum_evaluations,
            minimum=1,
        )
        _validate_integer("oversampling_factor", self.oversampling_factor, minimum=2)


@dataclass(frozen=True)
class EMDNonlinearDiagnostics:
    """Both stages of the frozen nonlinear solve."""

    root_success: bool
    root_message: str
    root_function_evaluations: int
    root_scaled_residual: float
    polish_applied: bool
    polish_success: bool
    polish_message: str
    polish_function_evaluations: int
    final_scaled_residual: float

    @property
    def success(self) -> bool:
        return bool(
            math.isfinite(self.final_scaled_residual)
            and self.final_scaled_residual <= DEFAULT_COLLOCATION_TOLERANCE
            and (
                (self.root_success and not self.polish_applied)
                or (self.polish_applied and self.polish_success)
            )
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "root": {
                "success": self.root_success,
                "message": self.root_message,
                "function_evaluations": self.root_function_evaluations,
                "scaled_residual": self.root_scaled_residual,
            },
            "polish": {
                "applied": self.polish_applied,
                "library_success": self.polish_success,
                "message": self.polish_message,
                "function_evaluations": self.polish_function_evaluations,
            },
            "final_success": self.success,
            "final_scaled_residual": self.final_scaled_residual,
        }


@dataclass(frozen=True)
class EMDProfile:
    """One UV-factorized coupled EMD collocation solution."""

    xi: float
    degree: int
    z_h: float
    omega: float
    u: NDArray[np.float64]
    warp_factor: NDArray[np.float64]
    blackening_factor: NDArray[np.float64]
    scalar_factor: NDArray[np.float64]
    gauge_factor: NDArray[np.float64]
    nonlinear: EMDNonlinearDiagnostics

    def interpolators(self) -> Tuple[BarycentricInterpolator, ...]:
        return tuple(
            _barycentric_interpolator(self.u, values)
            for values in (
                self.warp_factor,
                self.blackening_factor,
                self.scalar_factor,
                self.gauge_factor,
            )
        )


@dataclass(frozen=True)
class EMDEquationDiagnostics:
    """Independent equation, constraint, endpoint, flux, and exact-field checks."""

    warp_equation: float
    blackening_equation: float
    scalar_equation: float
    maxwell_equation: float
    einstein_constraint: float
    boundary_and_source: float
    horizon_scalar_equation: float
    maxwell_flux_drift: float
    exact_warp_error: float
    exact_blackening_error: float
    exact_scalar_error: float
    exact_gauge_error: float

    @property
    def maximum_equation_residual(self) -> float:
        return max(
            self.warp_equation,
            self.blackening_equation,
            self.scalar_equation,
            self.maxwell_equation,
        )

    @property
    def maximum_exact_field_error(self) -> float:
        return max(
            self.exact_warp_error,
            self.exact_blackening_error,
            self.exact_scalar_error,
            self.exact_gauge_error,
        )

    def to_dict(self) -> Dict[str, float]:
        return {
            "warp_equation": self.warp_equation,
            "blackening_equation": self.blackening_equation,
            "scalar_equation": self.scalar_equation,
            "maxwell_equation": self.maxwell_equation,
            "maximum_equation_residual": self.maximum_equation_residual,
            "einstein_constraint": self.einstein_constraint,
            "boundary_and_source": self.boundary_and_source,
            "horizon_scalar_equation": self.horizon_scalar_equation,
            "maxwell_flux_drift": self.maxwell_flux_drift,
            "exact_warp_error": self.exact_warp_error,
            "exact_blackening_error": self.exact_blackening_error,
            "exact_scalar_error": self.exact_scalar_error,
            "exact_gauge_error": self.exact_gauge_error,
            "maximum_exact_field_error": self.maximum_exact_field_error,
        }


@dataclass(frozen=True)
class EMDThermodynamics:
    """Source-normalized thermodynamic quantities at one charge point."""

    xi: float
    degree: int
    mu_bh: float
    energy_density: float
    entropy_density: float
    charge_density: float
    temperature: float
    chemical_potential: float
    maxwell_flux: float

    def to_dict(self) -> Dict[str, float]:
        return {
            "xi": self.xi,
            "degree": self.degree,
            "mu_bh": self.mu_bh,
            "hat_epsilon": self.energy_density,
            "hat_s": self.entropy_density,
            "hat_rho": self.charge_density,
            "temperature": self.temperature,
            "Omega": self.chemical_potential,
            "maxwell_flux": self.maxwell_flux,
        }


@dataclass(frozen=True)
class EMDContinuation:
    """Aligned three-degree solutions along the frozen charge path."""

    charge_path: Tuple[float, ...]
    reported_xi: Tuple[float, ...]
    degrees: Tuple[int, int, int]
    profiles: Mapping[int, Mapping[float, EMDProfile]]


def gauge_coupling(phi: Any) -> Any:
    """Return ``Z(phi)`` in the approved canonical normalization."""

    return np.exp(_MAXWELL_EXPONENT * np.asarray(phi))


def scalar_potential(phi: Any) -> Any:
    """Return ``V(phi)`` for ``L = 1``."""

    values = np.asarray(phi)
    return -(
        8.0 * np.exp(values / math.sqrt(6.0))
        + 4.0 * np.exp(-2.0 * values / math.sqrt(6.0))
    )


def scalar_potential_prime(phi: Any) -> Any:
    """Return ``dV/dphi`` for ``L = 1``."""

    values = np.asarray(phi)
    return -(8.0 / math.sqrt(6.0)) * (
        np.exp(values / math.sqrt(6.0))
        - np.exp(-2.0 * values / math.sqrt(6.0))
    )


def scalar_potential_second(phi: Any) -> Any:
    """Return ``d^2V/dphi^2`` for source-algebra checks."""

    values = np.asarray(phi)
    return -(4.0 / 3.0) * (
        np.exp(values / math.sqrt(6.0))
        + 2.0 * np.exp(-2.0 * values / math.sqrt(6.0))
    )


def charge_geometry(xi: Real) -> Tuple[float, float, float]:
    """Return ``theta``, ``z_H``, and ``Omega`` for one charge ratio."""

    resolved = _validate_xi(xi)
    theta = math.atan(resolved)
    z_h = 1.0 if resolved == 0.0 else theta / resolved
    return theta, z_h, math.sqrt(2.0) * resolved


def exact_factor_fields(
    xi: Real,
    u: Sequence[Real],
) -> Tuple[
    NDArray[np.float64],
    NDArray[np.float64],
    NDArray[np.float64],
    NDArray[np.float64],
]:
    """Return exact ``a, b, p, v`` factors without singular endpoint division."""

    resolved = _validate_xi(xi)
    values = np.asarray(u, dtype=float)
    if values.ndim != 1 or not np.all(np.isfinite(values)):
        raise ValueError("u must be a one-dimensional finite sequence")
    if np.any(values < 0.0) or np.any(values > 1.0):
        raise ValueError("u values must lie in [0, 1]")
    theta, _, omega = charge_geometry(resolved)
    if resolved == 0.0:
        return (
            np.zeros_like(values),
            np.ones_like(values),
            np.zeros_like(values),
            np.zeros_like(values),
        )

    x = theta * values
    sinc = np.sinc(x / math.pi)
    theta_over_sin = theta / math.sin(theta)
    q = np.log(np.cos(x)) / 3.0 - np.log(sinc)
    a = np.empty_like(values)
    nonzero = values != 0.0
    a[nonzero] = q[nonzero] / values[nonzero] ** 4
    a[~nonzero] = -(theta**4) / 45.0
    b = theta_over_sin**4 * sinc**4
    phi = -math.sqrt(8.0 / 3.0) * np.log(np.cos(x))
    p = np.empty_like(values)
    p[nonzero] = phi[nonzero] / values[nonzero] ** 2
    p[~nonzero] = math.sqrt(2.0 / 3.0) * theta**2
    v = math.sqrt(2.0) * resolved * theta_over_sin**2 * sinc**2
    v[-1:] = omega if values.size and values[-1] == 1.0 else v[-1:]
    return tuple(np.asarray(item, dtype=float) for item in (a, b, p, v))


def solve_emd_profile(
    xi: Real,
    degree: int,
    *,
    seed: Optional[EMDProfile] = None,
    config: Optional[EMDSolverConfig] = None,
) -> EMDProfile:
    """Solve one charge point without using a charged exact initial guess."""

    resolved_xi = _validate_xi(xi)
    _validate_integer("degree", degree, minimum=12)
    resolved_degree = int(degree)
    resolved_config = EMDSolverConfig() if config is None else config
    _, z_h, omega = charge_geometry(resolved_xi)
    grid = chebyshev_lobatto_grid(resolved_degree, 0.0, 1.0)
    u = grid.nodes
    d1 = grid.first_derivative
    d2 = grid.second_derivative
    size = grid.size

    if seed is None:
        if resolved_xi != 0.0:
            raise ValueError(
                "a charged EMD solve requires a deterministic lower-charge seed"
            )
        initial_fields = (
            np.zeros_like(u),
            np.ones_like(u),
            np.zeros_like(u),
            np.zeros_like(u),
        )
    else:
        if seed.xi > resolved_xi:
            raise ValueError("charge continuation seed must not decrease xi")
        interpolated = tuple(
            np.asarray(interpolator(u), dtype=float)
            for interpolator in seed.interpolators()
        )
        # Continue the prescribed boundary source explicitly.  The constant
        # shift keeps the previous interior response shape while satisfying
        # the new horizon gauge row; it is not the charged exact solution.
        shifted_gauge = interpolated[3] + (omega - seed.omega)
        initial_fields = interpolated[:3] + (shifted_gauge,)
    initial = np.concatenate(initial_fields)

    def residual(vector: NDArray[np.float64]) -> NDArray[np.float64]:
        a, b, p, v = np.asarray(vector, dtype=float).reshape(4, size)
        equations = _scaled_factor_equations(
            z_h,
            u,
            a,
            d1 @ a,
            d2 @ a,
            b,
            d1 @ b,
            d2 @ b,
            p,
            d1 @ p,
            d2 @ p,
            v,
            d1 @ v,
            d2 @ v,
        )
        warp_equation, blackening_equation, scalar_equation, maxwell_equation = (
            item.copy() for item in equations
        )
        blackening_equation[0] = float((d1 @ b)[0]) / (1.0 + abs(b[0]))
        blackening_equation[-1] = (b[-1] - 1.0) / (1.0 + abs(b[-1]))
        scalar_equation[0] = float((d1 @ p)[0]) / (1.0 + abs(p[0]))
        maxwell_equation[-1] = (v[-1] - omega) / max(1.0, abs(omega))
        return np.concatenate(
            (
                warp_equation,
                blackening_equation,
                scalar_equation,
                maxwell_equation,
            )
        )

    root_result = root(
        residual,
        initial,
        method="hybr",
        options={
            "xtol": resolved_config.root_tolerance,
            "maxfev": resolved_config.maximum_evaluations_factor * len(initial),
        },
    )
    root_vector = np.asarray(root_result.x, dtype=float)
    root_residual = float(np.max(np.abs(residual(root_vector))))
    polish_applied = bool(
        not root_result.success or root_residual > DEFAULT_COLLOCATION_TOLERANCE
    )
    if polish_applied:
        polish_result = least_squares(
            residual,
            root_vector,
            method="trf",
            ftol=resolved_config.polish_tolerance,
            xtol=resolved_config.polish_tolerance,
            gtol=resolved_config.polish_tolerance,
            max_nfev=resolved_config.polish_maximum_evaluations,
        )
        final_vector = np.asarray(polish_result.x, dtype=float)
        polish_success = bool(polish_result.success)
        polish_message = str(polish_result.message)
        polish_evaluations = int(polish_result.nfev)
    else:
        final_vector = root_vector
        polish_success = False
        polish_message = "not applied"
        polish_evaluations = 0
    final_residual = float(np.max(np.abs(residual(final_vector))))
    a, b, p, v = final_vector.reshape(4, size)
    return EMDProfile(
        xi=resolved_xi,
        degree=resolved_degree,
        z_h=z_h,
        omega=omega,
        u=np.asarray(u, dtype=float),
        warp_factor=np.asarray(a, dtype=float),
        blackening_factor=np.asarray(b, dtype=float),
        scalar_factor=np.asarray(p, dtype=float),
        gauge_factor=np.asarray(v, dtype=float),
        nonlinear=EMDNonlinearDiagnostics(
            root_success=bool(root_result.success),
            root_message=str(root_result.message),
            root_function_evaluations=int(root_result.nfev),
            root_scaled_residual=root_residual,
            polish_applied=polish_applied,
            polish_success=polish_success,
            polish_message=polish_message,
            polish_function_evaluations=polish_evaluations,
            final_scaled_residual=final_residual,
        ),
    )


def solve_emd_continuation(
    *,
    charge_path: Sequence[Real] = DEFAULT_CONTINUATION_XI,
    reported_xi: Sequence[Real] = DEFAULT_REPORTED_XI,
    degrees: Tuple[int, int, int] = DEFAULT_DEGREES,
    config: Optional[EMDSolverConfig] = None,
) -> EMDContinuation:
    """Solve the frozen charge path at three aligned spectral degrees."""

    path = tuple(_validate_xi(value) for value in charge_path)
    reported = tuple(_validate_xi(value) for value in reported_xi)
    if not path or path[0] != 0.0 or any(
        right <= left for left, right in zip(path, path[1:])
    ):
        raise ValueError("charge_path must start at zero and strictly increase")
    if not reported or any(value not in path for value in reported):
        raise ValueError("every reported xi must occur in charge_path")
    resolved_degrees = tuple(int(value) for value in degrees)
    if (
        len(resolved_degrees) != 3
        or tuple(sorted(set(resolved_degrees))) != resolved_degrees
    ):
        raise ValueError("degrees must be three strictly increasing integers")
    for degree in resolved_degrees:
        _validate_integer("degree", degree, minimum=12)

    by_degree: Dict[int, Dict[float, EMDProfile]] = {
        degree: {} for degree in resolved_degrees
    }
    coarse_history: List[EMDProfile] = []
    for xi in path:
        if not coarse_history:
            coarse_seed = None
        elif len(coarse_history) == 1:
            coarse_seed = coarse_history[-1]
        else:
            coarse_seed = _secant_charge_seed(
                coarse_history[-2], coarse_history[-1], xi
            )
        current = solve_emd_profile(
            xi,
            resolved_degrees[0],
            seed=coarse_seed,
            config=config,
        )
        by_degree[resolved_degrees[0]][xi] = current
        coarse_history.append(current)
        for degree in resolved_degrees[1:]:
            current = solve_emd_profile(
                xi,
                degree,
                seed=current,
                config=config,
            )
            by_degree[degree][xi] = current
    return EMDContinuation(
        charge_path=path,
        reported_xi=reported,
        degrees=(resolved_degrees[0], resolved_degrees[1], resolved_degrees[2]),
        profiles={degree: dict(items) for degree, items in by_degree.items()},
    )


def equation_diagnostics(
    profile: EMDProfile,
    *,
    oversampling_factor: int = 2,
) -> EMDEquationDiagnostics:
    """Evaluate physical equations and exact fields on an independent grid."""

    _validate_integer("oversampling_factor", oversampling_factor, minimum=2)
    grid = chebyshev_lobatto_grid(
        oversampling_factor * profile.degree, 0.0, 1.0
    )
    u = grid.nodes
    evaluated: List[
        Tuple[NDArray[np.float64], NDArray[np.float64], NDArray[np.float64]]
    ] = []
    for interpolator in profile.interpolators():
        values = np.asarray(interpolator(u), dtype=float)
        first = np.asarray(interpolator.derivative(u, der=1), dtype=float)
        second = np.asarray(interpolator.derivative(u, der=2), dtype=float)
        evaluated.append((values, first, second))
    a, au, auu = evaluated[0]
    b, bu, buu = evaluated[1]
    p, pu, puu = evaluated[2]
    v, vu, vuu = evaluated[3]
    equations = _scaled_factor_equations(
        profile.z_h,
        u,
        a,
        au,
        auu,
        b,
        bu,
        buu,
        p,
        pu,
        puu,
        v,
        vu,
        vuu,
    )
    warp_equation, blackening_equation, scalar_equation, maxwell_equation = (
        float(np.max(np.abs(item))) for item in equations
    )
    constraint = _scaled_einstein_constraint(
        profile.z_h, u, a, au, b, bu, p, pu, v, vu
    )
    flux = _maxwell_flux(profile.z_h, u, a, p, v, vu)
    if profile.xi == 0.0:
        flux_drift = float(np.max(np.abs(flux)))
    else:
        flux_drift = float(
            np.max(np.abs(flux - np.mean(flux)))
            / max(1.0, float(np.max(np.abs(flux))))
        )
    exact_a, exact_b, exact_p, exact_v = exact_factor_fields(profile.xi, u)
    q = u**4 * a
    exact_q = u**4 * exact_a
    blackening = 1.0 - u**4 * b
    exact_blackening = 1.0 - u**4 * exact_b
    scalar = u**2 * p
    exact_scalar = u**2 * exact_p
    gauge = -profile.omega + u**2 * v
    exact_gauge = -profile.omega + u**2 * exact_v
    boundary_terms = (
        abs(float(bu[0])),
        abs(float(pu[0])),
        abs(float(vu[0])),
        abs(float(b[-1] - 1.0)),
        abs(float(gauge[0] + profile.omega)),
        abs(float(gauge[-1])),
        abs(float(20.0 * a[0] + (2.0 / 3.0) * p[0] ** 2)),
        abs(float(equations[2][-1])),
    )
    return EMDEquationDiagnostics(
        warp_equation=warp_equation,
        blackening_equation=blackening_equation,
        scalar_equation=scalar_equation,
        maxwell_equation=maxwell_equation,
        einstein_constraint=float(np.max(np.abs(constraint))),
        boundary_and_source=max(boundary_terms),
        horizon_scalar_equation=abs(float(equations[2][-1])),
        maxwell_flux_drift=flux_drift,
        exact_warp_error=_maximum_scaled_array_difference(q, exact_q),
        exact_blackening_error=_maximum_scaled_array_difference(
            blackening, exact_blackening
        ),
        exact_scalar_error=_maximum_scaled_array_difference(scalar, exact_scalar),
        exact_gauge_error=_maximum_scaled_array_difference(gauge, exact_gauge),
    )


def profile_thermodynamics(profile: EMDProfile) -> EMDThermodynamics:
    """Extract source-normalized thermodynamics from one spectral profile."""

    a_interp, b_interp, p_interp, v_interp = profile.interpolators()
    del p_interp
    b_h = float(b_interp(1.0))
    b_u_h = float(b_interp.derivative(1.0, der=1))
    f_u_h = -(4.0 * b_h + b_u_h)
    temperature = abs(f_u_h / profile.z_h) / (4.0 * math.pi)
    entropy = math.exp(3.0 * float(a_interp(1.0))) / (
        2.0 * math.pi * profile.z_h**3
    )
    b_uv = float(b_interp(0.0))
    mu_bh = b_uv / profile.z_h**4
    v_uv = float(v_interp(0.0))
    v_u_uv = float(v_interp.derivative(0.0, der=1))
    flux_uv = -(
        math.exp(float(a_interp(0.0)) * 0.0)
        * float(gauge_coupling(0.0))
        * (2.0 * v_uv + 0.0 * v_u_uv)
        / profile.z_h**2
    )
    values = (
        mu_bh,
        temperature,
        entropy,
        flux_uv,
    )
    if not all(math.isfinite(value) for value in values):
        raise RuntimeError("EMD thermodynamics must be finite")
    if mu_bh <= 0.0 or temperature <= 0.0 or entropy <= 0.0:
        raise RuntimeError("EMD mass, temperature, and entropy must be positive")
    return EMDThermodynamics(
        xi=profile.xi,
        degree=profile.degree,
        mu_bh=mu_bh,
        energy_density=3.0 * mu_bh / (8.0 * math.pi**2),
        entropy_density=entropy,
        charge_density=abs(flux_uv) / (8.0 * math.pi**2),
        temperature=temperature,
        chemical_potential=profile.omega,
        maxwell_flux=flux_uv,
    )


def exact_thermodynamics(xi: Real, degree: int = 0) -> EMDThermodynamics:
    """Return source Eqs. (3)--(5) after ``L = r_H = 1``."""

    resolved = _validate_xi(xi)
    mu_bh = (1.0 + resolved**2) ** 2
    flux = -2.0 * math.sqrt(2.0) * resolved * (1.0 + resolved**2)
    return EMDThermodynamics(
        xi=resolved,
        degree=int(degree),
        mu_bh=mu_bh,
        energy_density=3.0 * mu_bh / (8.0 * math.pi**2),
        entropy_density=(1.0 + resolved**2) / (2.0 * math.pi),
        charge_density=abs(flux) / (8.0 * math.pi**2),
        temperature=1.0 / math.pi,
        chemical_potential=math.sqrt(2.0) * resolved,
        maxwell_flux=flux,
    )


def verify_gubser_rocha_emd(
    *,
    repeat_for_determinism: bool = True,
) -> VerificationRecord:
    """Run the frozen EMD contract and return all inspectable evidence."""

    first = _verify_once()
    second_state: Optional[Mapping[str, Any]] = None
    determinism_error: Optional[float] = None
    if repeat_for_determinism:
        second = _verify_once()
        second_state = second["determinism_state"]
        determinism_error = _maximum_nested_numeric_difference(
            first["determinism_state"], second_state
        )

    summary = first["summary"]
    checks = (
        AcceptanceCheck(
            "source-algebra",
            "canonical conversion, source functions, coordinate map, and exact identities",
            summary["source_algebra_error"] <= 1.0e-12,
            summary["source_algebra_error"],
            "maximum absolute or scaled error <= 1e-12",
        ),
        AcceptanceCheck(
            "nonlinear-solver",
            "every continuation and reported final solve reaches an accepted final state",
            bool(summary["solver_success"]),
            0.0 if summary["solver_success"] else 1.0,
            "all final residual states accepted and <= 1e-9",
        ),
        AcceptanceCheck(
            "collocation-residual",
            "maximum final scaled coupled collocation residual",
            summary["maximum_collocation_residual"]
            <= DEFAULT_COLLOCATION_TOLERANCE,
            summary["maximum_collocation_residual"],
            f"<= {DEFAULT_COLLOCATION_TOLERANCE:.1e}",
        ),
        AcceptanceCheck(
            "independent-equations",
            "maximum four-equation residual on the twice-denser grid",
            summary["maximum_equation_residual"] <= DEFAULT_EQUATION_TOLERANCE,
            summary["maximum_equation_residual"],
            f"<= {DEFAULT_EQUATION_TOLERANCE:.1e}",
        ),
        AcceptanceCheck(
            "einstein-constraint",
            "maximum independent Einstein-constraint residual",
            summary["maximum_constraint_residual"]
            <= DEFAULT_CONSTRAINT_TOLERANCE,
            summary["maximum_constraint_residual"],
            f"<= {DEFAULT_CONSTRAINT_TOLERANCE:.1e}",
        ),
        AcceptanceCheck(
            "boundary-and-source",
            "maximum endpoint, BF no-log source, and horizon regularity residual",
            summary["maximum_boundary_residual"] <= DEFAULT_BOUNDARY_TOLERANCE,
            summary["maximum_boundary_residual"],
            f"<= {DEFAULT_BOUNDARY_TOLERANCE:.1e}",
        ),
        AcceptanceCheck(
            "maxwell-flux",
            "maximum normalized radial Maxwell-flux drift",
            summary["maximum_flux_drift"] <= DEFAULT_FLUX_TOLERANCE,
            summary["maximum_flux_drift"],
            f"<= {DEFAULT_FLUX_TOLERANCE:.1e}",
        ),
        AcceptanceCheck(
            "exact-fields",
            "maximum scaled spectral-versus-source exact-field difference",
            summary["maximum_exact_field_error"] <= DEFAULT_FIELD_TOLERANCE,
            summary["maximum_exact_field_error"],
            f"<= {DEFAULT_FIELD_TOLERANCE:.1e}",
        ),
        AcceptanceCheck(
            "spectral-refinement",
            "N=60 to 80 thermodynamic refinement and amended ordering rule",
            (
                summary["maximum_final_refinement"]
                <= DEFAULT_REFINEMENT_TOLERANCE
                and summary["refinement_ordering_failures"] == 0
            ),
            summary["maximum_final_refinement"],
            (
                f"final <= {DEFAULT_REFINEMENT_TOLERANCE:.1e}; zero ordering "
                f"failures above {DEFAULT_REFINEMENT_ORDER_FLOOR:.1e}"
            ),
        ),
        AcceptanceCheck(
            "source-thermodynamics",
            "maximum source Eq. (3), exact T, and exact Omega relative error",
            summary["maximum_thermodynamic_error"]
            <= DEFAULT_THERMODYNAMIC_TOLERANCE,
            summary["maximum_thermodynamic_error"],
            f"<= {DEFAULT_THERMODYNAMIC_TOLERANCE:.1e}",
        ),
        AcceptanceCheck(
            "equation-of-state",
            "maximum source Eq. (4) and both Eq. (5) derivative errors",
            summary["maximum_eos_error"] <= DEFAULT_EOS_TOLERANCE,
            summary["maximum_eos_error"],
            f"<= {DEFAULT_EOS_TOLERANCE:.1e}",
        ),
        AcceptanceCheck(
            "low-temperature-relation",
            "finite-xi identity and low-temperature fit intercept and slope",
            (
                summary["maximum_low_temperature_identity_error"]
                <= DEFAULT_LOW_TEMPERATURE_IDENTITY_TOLERANCE
                and summary["low_temperature_fit_error"]
                <= DEFAULT_LOW_TEMPERATURE_FIT_TOLERANCE
            ),
            max(
                summary["maximum_low_temperature_identity_error"],
                summary["low_temperature_fit_error"],
            ),
            (
                f"identity <= {DEFAULT_LOW_TEMPERATURE_IDENTITY_TOLERANCE:.1e}; "
                f"fit <= {DEFAULT_LOW_TEMPERATURE_FIT_TOLERANCE:.1e}"
            ),
        ),
        AcceptanceCheck(
            "neutral-limit-and-determinism",
            "neutral AdS--Schwarzschild limit and duplicate physical observables",
            (
                summary["neutral_limit_error"] <= DEFAULT_NEUTRAL_TOLERANCE
                and determinism_error is not None
                and determinism_error <= DEFAULT_DETERMINISM_TOLERANCE
            ),
            (
                None
                if determinism_error is None
                else max(summary["neutral_limit_error"], determinism_error)
            ),
            (
                f"neutral <= {DEFAULT_NEUTRAL_TOLERANCE:.1e}; determinism <= "
                f"{DEFAULT_DETERMINISM_TOLERANCE:.1e}"
            ),
        ),
    )
    results = {
        "cases": first["cases"],
        "field_overlay": first["field_overlay"],
        "continuation_solves": first["continuation_solves"],
        "refinement": first["refinement"],
        "low_temperature": first["low_temperature"],
        "summary": summary,
        "determinism": {
            "repeat_enabled": repeat_for_determinism,
            "maximum_scaled_difference": determinism_error,
            "comparison_state_present": second_state is not None,
        },
    }
    record = VerificationRecord(
        definition=GUBSER_ROCHA_DEFINITION,
        configuration={
            "bulk_dimension": 5,
            "ensemble": "fixed boundary chemical potential for each source case",
            "units": "L = r_H = 1",
            "reported_xi": list(DEFAULT_REPORTED_XI),
            "continuation_xi": list(DEFAULT_CONTINUATION_XI),
            "degrees": list(DEFAULT_DEGREES),
            "polish_maximum_evaluations": DEFAULT_POLISH_MAXIMUM_EVALUATIONS,
            "refinement_order_floor": DEFAULT_REFINEMENT_ORDER_FLOOR,
            "instability_threshold_xi": 1.0,
        },
        numerical_method={
            "route": "coupled UV-factorized Chebyshev collocation",
            "coordinate": "u = z/z_H in [0, 1] with exact endpoints",
            "unknowns": ["a(u)", "b(u)", "p(u)", "v(u)"],
            "factorization": [
                "A = -log(z) + u^4 a",
                "f = 1 - u^4 b",
                "phi = u^2 p",
                "Phi = -Omega + u^2 v",
            ],
            "nonlinear_solver": (
                "scipy.optimize.root(method='hybr', xtol=1e-11), then at most "
                "thirty-two scipy.optimize.least_squares(method='trf') evaluations "
                "only after a failed or insufficient root state"
            ),
            "initialization": (
                "neutral analytic solution, theta-secant charge continuation, "
                "and lower-to-higher degree interpolation; charged exact fields "
                "are never solver seeds"
            ),
            "independent_checks": (
                "twice-denser barycentric equations, Einstein constraint, "
                "Maxwell flux, source exact fields, and source thermodynamics"
            ),
        },
        results=results,
        acceptance_checks=checks,
        software_versions=runtime_versions(),
        scope=(
            "Owner-reviewed reproduction of the public homogeneous equal-charge "
            "Gubser--Rocha top-down-derived classical EMD background and "
            "source Eqs. (2)--(6). Source Figure 1 and the charged-fermion "
            "Dirac system are not reproduced. This is not stability evidence, "
            "a Fermi-liquid validation, QCD, a private phenomenological EMD "
            "model, or a new prediction."
        ),
        extra={
            "primary_source": {
                "id": SOURCE_ID,
                "doi": "10.1103/PhysRevD.81.046001",
                "pdf_sha256": SOURCE_PDF_SHA256,
                "source_archive_sha256": SOURCE_ARCHIVE_SHA256,
                "equations_in_scope": ["(1)", "(2)", "(3)", "(4)", "(5)", "(6)"],
                "equation_7_specific_heats_in_scope": False,
                "figure_1_in_scope": False,
                "model_origin": (
                    "top-down consistent truncation of five-dimensional "
                    "maximal gauged supergravity with a type IIB lift"
                ),
            },
            "contract_review": {
                "review_state": "approved",
                "reviewed_by": "Xin-Yi Liu",
                "reviewed_on": "2026-08-19",
                "authorization": (
                    "owner-approved prospective numerical-contract amendments "
                    "and bounded clean preflight rerun only"
                ),
                "amendments": [
                    "TRF polish maximum evaluations increased from 12 to 32",
                    "refinement ordering floor increased from 1e-10 to 5e-10",
                ],
            },
            "result_review_state": "approved",
            "result_reviewed_by": "Xin-Yi Liu",
            "result_reviewed_on": "2026-08-19",
            "generated_by_ai": True,
        },
    )
    json.dumps(record.to_dict(), allow_nan=False, sort_keys=True)
    return record


def save_gubser_rocha_artifacts(
    record: VerificationRecord,
    output_directory: Path,
) -> Mapping[str, Path]:
    """Save the strict JSON record, seven-case CSV, and verification plot."""

    directory = Path(output_directory)
    directory.mkdir(parents=True, exist_ok=True)
    paths = {
        "json": directory / "gubser-rocha-emd-result.json",
        "csv": directory / "gubser-rocha-emd-cases.csv",
        "plot": directory / "gubser-rocha-emd-verification.png",
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
    rows = [
        "xi,temperature,Omega,mu_bh,hat_epsilon,hat_s,hat_rho,"
        "max_equation_residual,max_exact_field_error"
    ]
    for case in payload["results"]["cases"]:
        thermo = case["thermodynamics"]
        diagnostics = case["diagnostics"]
        rows.append(
            f"{case['xi']:.17g},{thermo['temperature']:.17g},"
            f"{thermo['Omega']:.17g},{thermo['mu_bh']:.17g},"
            f"{thermo['hat_epsilon']:.17g},{thermo['hat_s']:.17g},"
            f"{thermo['hat_rho']:.17g},"
            f"{diagnostics['maximum_equation_residual']:.17g},"
            f"{diagnostics['maximum_exact_field_error']:.17g}"
        )
    paths["csv"].write_text("\n".join(rows) + "\n", encoding="utf-8")
    _save_verification_plot(payload, paths["plot"])
    return paths


def _verify_once() -> Dict[str, Any]:
    continuation = solve_emd_continuation()
    fine = continuation.degrees[-1]
    cases: List[Dict[str, Any]] = []
    diagnostics_by_xi: Dict[float, EMDEquationDiagnostics] = {}
    thermodynamics_by_degree: Dict[int, Dict[float, EMDThermodynamics]] = {
        degree: {} for degree in continuation.degrees
    }
    for degree in continuation.degrees:
        for xi in continuation.reported_xi:
            thermodynamics_by_degree[degree][xi] = profile_thermodynamics(
                continuation.profiles[degree][xi]
            )

    maximum_thermodynamic_error = 0.0
    maximum_eos_error = 0.0
    for xi in continuation.reported_xi:
        profile = continuation.profiles[fine][xi]
        diagnostics = equation_diagnostics(profile)
        diagnostics_by_xi[xi] = diagnostics
        thermo = thermodynamics_by_degree[fine][xi]
        exact = exact_thermodynamics(xi, fine)
        thermo_errors = {
            name: _relative_error(getattr(thermo, name), getattr(exact, name))
            for name in (
                "mu_bh",
                "energy_density",
                "entropy_density",
                "charge_density",
                "temperature",
                "chemical_potential",
            )
        }
        maximum_thermodynamic_error = max(
            maximum_thermodynamic_error, max(thermo_errors.values())
        )
        eos = _equation_of_state_evidence(thermo)
        maximum_eos_error = max(maximum_eos_error, eos["maximum_relative_error"])
        cases.append(
            {
                "xi": xi,
                "degree": fine,
                "stability_interpretation": (
                    "threshold point"
                    if xi == 1.0
                    else (
                        "analytic verification point only; stability not claimed"
                        if xi > 1.0
                        else "below the cited unequal-charge instability threshold"
                    )
                ),
                "thermodynamics": thermo.to_dict(),
                "source_exact_thermodynamics": exact.to_dict(),
                "thermodynamic_relative_errors": thermo_errors,
                "equation_of_state": eos,
                "diagnostics": diagnostics.to_dict(),
                "nonlinear": profile.nonlinear.to_dict(),
            }
        )

    refinement = _refinement_evidence(continuation, thermodynamics_by_degree)
    low_temperature = _low_temperature_evidence(thermodynamics_by_degree[fine])
    continuation_solves = []
    maximum_collocation = 0.0
    solver_success = True
    for xi in continuation.charge_path:
        for degree in continuation.degrees:
            profile = continuation.profiles[degree][xi]
            maximum_collocation = max(
                maximum_collocation, profile.nonlinear.final_scaled_residual
            )
            solver_success = solver_success and profile.nonlinear.success
            continuation_solves.append(
                {
                    "xi": xi,
                    "degree": degree,
                    "reported_case": xi in continuation.reported_xi,
                    "nonlinear": profile.nonlinear.to_dict(),
                }
            )

    neutral = diagnostics_by_xi[0.0]
    neutral_thermo = thermodynamics_by_degree[fine][0.0]
    neutral_exact = exact_thermodynamics(0.0, fine)
    neutral_limit_error = max(
        neutral.maximum_exact_field_error,
        max(
            _relative_error(getattr(neutral_thermo, name), getattr(neutral_exact, name))
            for name in (
                "mu_bh",
                "energy_density",
                "entropy_density",
                "charge_density",
                "temperature",
                "chemical_potential",
            )
        ),
    )
    summary = {
        "source_algebra_error": _source_algebra_error(),
        "solver_success": solver_success,
        "maximum_collocation_residual": maximum_collocation,
        "maximum_equation_residual": max(
            item.maximum_equation_residual for item in diagnostics_by_xi.values()
        ),
        "maximum_constraint_residual": max(
            item.einstein_constraint for item in diagnostics_by_xi.values()
        ),
        "maximum_boundary_residual": max(
            item.boundary_and_source for item in diagnostics_by_xi.values()
        ),
        "maximum_flux_drift": max(
            item.maxwell_flux_drift for item in diagnostics_by_xi.values()
        ),
        "maximum_exact_field_error": max(
            item.maximum_exact_field_error for item in diagnostics_by_xi.values()
        ),
        "maximum_final_refinement": refinement["maximum_final_change"],
        "refinement_ordering_failures": refinement["ordering_failures"],
        "maximum_thermodynamic_error": maximum_thermodynamic_error,
        "maximum_eos_error": maximum_eos_error,
        "maximum_low_temperature_identity_error": low_temperature[
            "maximum_identity_error"
        ],
        "low_temperature_fit_error": low_temperature["maximum_fit_error"],
        "neutral_limit_error": neutral_limit_error,
    }
    determinism_state = {
        "cases": [
            {
                "xi": case["xi"],
                "thermodynamics": case["thermodynamics"],
                "equation_of_state": case["equation_of_state"],
            }
            for case in cases
        ],
        "low_temperature": low_temperature,
    }
    field_overlay = _field_overlay(continuation.profiles[fine][2.0])
    return {
        "cases": cases,
        "field_overlay": field_overlay,
        "continuation_solves": continuation_solves,
        "refinement": refinement,
        "low_temperature": low_temperature,
        "summary": summary,
        "determinism_state": determinism_state,
    }


def _refinement_evidence(
    continuation: EMDContinuation,
    thermodynamics: Mapping[int, Mapping[float, EMDThermodynamics]],
) -> Dict[str, Any]:
    coarse, middle, fine = continuation.degrees
    observables = (
        "mu_bh",
        "energy_density",
        "entropy_density",
        "charge_density",
        "temperature",
        "chemical_potential",
    )
    rows = []
    earlier_changes: List[float] = []
    final_changes: List[float] = []
    ordering_failures = 0
    for xi in continuation.reported_xi:
        row = {"xi": xi, "observables": {}}
        for name in observables:
            values = [getattr(thermodynamics[degree][xi], name) for degree in (coarse, middle, fine)]
            earlier = _scaled_relative_change(values[1], values[0])
            final = _scaled_relative_change(values[2], values[1])
            ordered = not (
                earlier > DEFAULT_REFINEMENT_ORDER_FLOOR and final >= earlier
            )
            if not ordered:
                ordering_failures += 1
            earlier_changes.append(earlier)
            final_changes.append(final)
            row["observables"][name] = {
                "coarse_to_middle": earlier,
                "middle_to_fine": final,
                "ordered_above_floor": ordered,
            }
        rows.append(row)
    return {
        "degrees": list(continuation.degrees),
        "ordering_floor": DEFAULT_REFINEMENT_ORDER_FLOOR,
        "coarse_to_middle_maximum": max(earlier_changes),
        "maximum_final_change": max(final_changes),
        "ordering_failures": ordering_failures,
        "cases": rows,
    }


def _equation_of_state_evidence(thermo: EMDThermodynamics) -> Dict[str, float]:
    s = thermo.entropy_density
    rho = thermo.charge_density
    combination = s**2 + 2.0 * math.pi**2 * rho**2
    coefficient = 3.0 / (2.0 ** (5.0 / 3.0) * math.pi ** (2.0 / 3.0))
    epsilon = coefficient * combination ** (2.0 / 3.0)
    temperature = (4.0 * coefficient / 3.0) * s * combination ** (-1.0 / 3.0)
    omega = (
        (8.0 * coefficient * math.pi**2 / 3.0)
        * rho
        * combination ** (-1.0 / 3.0)
    )
    errors = {
        "equation_relative_error": _relative_error(
            thermo.energy_density, epsilon
        ),
        "temperature_derivative_relative_error": _relative_error(
            thermo.temperature, temperature
        ),
        "chemical_potential_derivative_relative_error": _relative_error(
            thermo.chemical_potential, omega
        ),
    }
    return {
        "equation_energy_density": epsilon,
        "derivative_temperature": temperature,
        "derivative_Omega": omega,
        **errors,
        "maximum_relative_error": max(errors.values()),
    }


def _low_temperature_evidence(
    thermodynamics: Mapping[float, EMDThermodynamics],
) -> Dict[str, Any]:
    rows = []
    x_values = []
    y_values = []
    for xi in (4.0, 8.0, 16.0):
        thermo = thermodynamics[xi]
        inverse_xi_squared = 1.0 / xi**2
        ratio = (
            4.0
            * thermo.entropy_density
            / (thermo.chemical_potential**2 * thermo.temperature)
        )
        exact = 1.0 + inverse_xi_squared
        rows.append(
            {
                "xi": xi,
                "inverse_xi_squared": inverse_xi_squared,
                "ratio": ratio,
                "exact_finite_xi": exact,
                "absolute_error": abs(ratio - exact),
            }
        )
        x_values.append(inverse_xi_squared)
        y_values.append(ratio)
    design = np.column_stack((np.ones(3), np.asarray(x_values)))
    intercept, slope = np.linalg.lstsq(
        design, np.asarray(y_values), rcond=None
    )[0]
    return {
        "cases": rows,
        "fit": {
            "intercept": float(intercept),
            "slope": float(slope),
            "intercept_absolute_error": abs(float(intercept) - 1.0),
            "slope_absolute_error": abs(float(slope) - 1.0),
        },
        "maximum_identity_error": max(row["absolute_error"] for row in rows),
        "maximum_fit_error": max(
            abs(float(intercept) - 1.0), abs(float(slope) - 1.0)
        ),
    }


def _source_algebra_error() -> float:
    errors = [
        abs(float(scalar_potential(0.0)) + 12.0),
        abs(float(scalar_potential_prime(0.0))),
        abs(float(scalar_potential_second(0.0)) + 4.0),
        abs(float(gauge_coupling(0.0)) - 1.0),
        abs((2.0 * math.sqrt(6.0)) ** 2 / 24.0 - 1.0),
    ]
    for xi in (0.5, 1.0, 4.0, 16.0):
        theta, z_h, omega = charge_geometry(xi)
        errors.extend(
            (
                abs(math.tan(theta) - xi) / max(1.0, xi),
                abs(z_h * xi - theta),
                abs(omega - math.sqrt(2.0) * xi),
                abs(math.sin(theta) - xi / math.sqrt(1.0 + xi**2)),
                abs(math.cos(theta) - 1.0 / math.sqrt(1.0 + xi**2)),
            )
        )
    return max(errors)


def _field_overlay(profile: EMDProfile) -> Dict[str, Any]:
    u = np.linspace(0.0, 1.0, 161)
    numerical_factors = tuple(
        np.asarray(interpolator(u), dtype=float)
        for interpolator in profile.interpolators()
    )
    exact_factors = exact_factor_fields(profile.xi, u)

    def physical_fields(
        factors: Tuple[NDArray[np.float64], ...]
    ) -> Dict[str, List[float]]:
        a, b, p, v = factors
        return {
            "source_subtracted_A": (u**4 * a).tolist(),
            "f": (1.0 - u**4 * b).tolist(),
            "phi": (u**2 * p).tolist(),
            "Phi": (-profile.omega + u**2 * v).tolist(),
        }

    return {
        "xi": profile.xi,
        "u": u.tolist(),
        "warp_quantity": "A + log(z) = u^4 a",
        "numerical": physical_fields(numerical_factors),
        "source_exact": physical_fields(exact_factors),
    }


def _save_verification_plot(payload: Mapping[str, Any], path: Path) -> None:
    try:
        import matplotlib

        matplotlib.use("Agg")
        from matplotlib import pyplot as plt
    except ImportError as exc:
        raise RuntimeError(
            "Matplotlib is required for --output-dir; install holoforge[plot]"
        ) from exc
    cases = payload["results"]["cases"]
    figure, axes = plt.subplots(2, 3, figsize=(13.2, 7.2), constrained_layout=True)
    overlay = payload["results"]["field_overlay"]
    u = overlay["u"]
    field_specs = (
        ("source_subtracted_A", r"$A+\log z$"),
        ("f", r"$f$"),
        ("phi", r"$\phi$"),
        ("Phi", r"$\Phi$"),
    )
    for axis, (key, label) in zip(axes.flat[:4], field_specs):
        axis.plot(
            u,
            overlay["numerical"][key],
            color="#1565c0",
            linewidth=2.0,
            label="spectral",
        )
        axis.plot(
            u,
            overlay["source_exact"][key],
            color="black",
            linestyle="--",
            linewidth=1.3,
            label="source exact",
        )
        axis.set(xlabel=r"$u=z/z_H$", ylabel=label)
    axes.flat[0].set_title(rf"Field overlays at $\xi={overlay['xi']:g}$")
    axes.flat[0].legend(fontsize=8)

    axes.flat[4].semilogy(
        [case["xi"] for case in cases],
        [case["diagnostics"]["maximum_exact_field_error"] for case in cases],
        marker="o",
        color="#1565c0",
        label="spectral vs exact fields",
    )
    axes.flat[4].axvline(1.0, color="#b71c1c", linestyle="--", label=r"instability threshold $\xi=1$")
    axes.flat[4].axhline(DEFAULT_FIELD_TOLERANCE, color="0.4", linestyle=":", label="field gate")
    axes.flat[4].set(xlabel=r"$\xi=Q/r_H$", ylabel="maximum scaled field error", title="Exact background check")
    axes.flat[4].legend(fontsize=8)

    low = payload["results"]["low_temperature"]
    x_values = np.asarray(
        [item["inverse_xi_squared"] for item in low["cases"]], dtype=float
    )
    y_values = np.asarray([item["ratio"] for item in low["cases"]], dtype=float)
    order = np.argsort(x_values)
    axes.flat[5].scatter(x_values, y_values, color="#1565c0", label="spectral cases")
    fit = low["fit"]
    axes.flat[5].plot(
        x_values[order],
        fit["intercept"] + fit["slope"] * x_values[order],
        color="#c62828",
        label="declared linear fit",
    )
    axes.flat[5].plot(
        x_values[order],
        1.0 + x_values[order],
        color="black",
        linestyle="--",
        label=r"source finite-$\xi$ identity",
    )
    axes.flat[5].set(
        xlabel=r"$1/\xi^2$",
        ylabel=r"$4\hat s/(\Omega^2T)$",
        title="Source Eq. (6) extrapolation",
    )
    axes.flat[5].legend(fontsize=8)
    figure.savefig(path, dpi=180)
    plt.close(figure)


def _relative_error(left: float, right: float) -> float:
    if left == right:
        return 0.0
    return abs(left - right) / max(abs(right), 1.0e-300)


def _scaled_relative_change(left: float, right: float) -> float:
    return abs(left - right) / max(1.0, abs(left), abs(right))


def _maximum_nested_numeric_difference(left: Any, right: Any) -> float:
    if isinstance(left, Mapping) and isinstance(right, Mapping):
        if set(left) != set(right):
            return math.inf
        return max(
            (
                _maximum_nested_numeric_difference(left[key], right[key])
                for key in left
            ),
            default=0.0,
        )
    if isinstance(left, list) and isinstance(right, list):
        if len(left) != len(right):
            return math.inf
        return max(
            (
                _maximum_nested_numeric_difference(a, b)
                for a, b in zip(left, right)
            ),
            default=0.0,
        )
    if isinstance(left, (int, float)) and isinstance(right, (int, float)):
        return abs(float(left) - float(right)) / max(
            1.0, abs(float(left)), abs(float(right))
        )
    return 0.0 if left == right else math.inf


def _secant_charge_seed(
    earlier: EMDProfile,
    previous: EMDProfile,
    target_xi: float,
) -> EMDProfile:
    if earlier.degree != previous.degree:
        raise ValueError("secant charge seeds require one spectral degree")
    earlier_theta = math.atan(earlier.xi)
    previous_theta = math.atan(previous.xi)
    target_theta = math.atan(target_xi)
    factor = (target_theta - previous_theta) / (
        previous_theta - earlier_theta
    )
    _, z_h, omega = charge_geometry(target_xi)
    predicted = tuple(
        previous_values + factor * (previous_values - earlier_values)
        for earlier_values, previous_values in zip(
            (
                earlier.warp_factor,
                earlier.blackening_factor,
                earlier.scalar_factor,
                earlier.gauge_factor,
            ),
            (
                previous.warp_factor,
                previous.blackening_factor,
                previous.scalar_factor,
                previous.gauge_factor,
            ),
        )
    )
    predicted_gauge = predicted[3] + (omega - float(predicted[3][-1]))
    return EMDProfile(
        xi=target_xi,
        degree=previous.degree,
        z_h=z_h,
        omega=omega,
        u=previous.u,
        warp_factor=np.asarray(predicted[0], dtype=float),
        blackening_factor=np.asarray(predicted[1], dtype=float),
        scalar_factor=np.asarray(predicted[2], dtype=float),
        gauge_factor=np.asarray(predicted_gauge, dtype=float),
        nonlinear=previous.nonlinear,
    )


def _scaled_factor_equations(
    z_h: float,
    u: NDArray[np.float64],
    a: NDArray[np.float64],
    au: NDArray[np.float64],
    auu: NDArray[np.float64],
    b: NDArray[np.float64],
    bu: NDArray[np.float64],
    buu: NDArray[np.float64],
    p: NDArray[np.float64],
    pu: NDArray[np.float64],
    puu: NDArray[np.float64],
    v: NDArray[np.float64],
    vu: NDArray[np.float64],
    vuu: NDArray[np.float64],
) -> Tuple[NDArray[np.float64], ...]:
    """Return finite, term-scaled equations for the four factored fields."""

    u2 = u**2
    u3 = u**3
    u4 = u**4
    q = u4 * a
    phi = u2 * p
    f = 1.0 - u4 * b
    a1 = 4.0 * a + u * au
    b1 = 4.0 * b + u * bu
    p1 = 2.0 * p + u * pu
    v1 = 2.0 * v + u * vu
    z_value = np.asarray(gauge_coupling(phi), dtype=float)
    z_phi = _MAXWELL_EXPONENT * z_value

    warp_terms = (
        20.0 * a,
        10.0 * u * au,
        u2 * auu,
        -u4 * a1**2,
        p1**2 / 6.0,
    )
    blackening_terms = (
        -5.0 * u * bu,
        -u2 * buu,
        -3.0 * u4 * a1 * b1,
        -(z_h**2) * u2 * np.exp(-2.0 * q) * z_value * v1**2,
    )
    maxwell_terms = (
        3.0 * vu,
        u * vuu,
        u3 * a1 * v1,
        _MAXWELL_EXPONENT * u * p1 * v1,
    )
    potential_ratio = np.empty_like(u)
    nonzero = u != 0.0
    potential_prime = np.asarray(scalar_potential_prime(phi), dtype=float)
    potential_ratio[nonzero] = potential_prime[nonzero] / u2[nonzero]
    potential_ratio[~nonzero] = -4.0 * p[~nonzero]
    scalar_terms = (
        f * (-4.0 * p + u * pu + u2 * puu + 3.0 * u4 * a1 * p1),
        -u4 * b1 * p1,
        -np.exp(2.0 * q) * potential_ratio,
        0.5 * (z_h**2) * u4 * np.exp(-2.0 * q) * z_phi * v1**2,
    )
    return tuple(
        _scaled_sum(terms)
        for terms in (warp_terms, blackening_terms, scalar_terms, maxwell_terms)
    )


def _scaled_einstein_constraint(
    z_h: float,
    u: NDArray[np.float64],
    a: NDArray[np.float64],
    au: NDArray[np.float64],
    b: NDArray[np.float64],
    bu: NDArray[np.float64],
    p: NDArray[np.float64],
    pu: NDArray[np.float64],
    v: NDArray[np.float64],
    vu: NDArray[np.float64],
) -> NDArray[np.float64]:
    """Return the independently evaluated, finite Einstein constraint."""

    u4 = u**4
    q = u4 * a
    phi = u**2 * p
    f = 1.0 - u4 * b
    a1 = 4.0 * a + u * au
    b1 = 4.0 * b + u * bu
    p1 = 2.0 * p + u * pu
    v1 = 2.0 * v + u * vu
    terms = (
        6.0 * (u4 * b1 - u**8 * a1 * b1),
        f * 24.0 * (1.0 - 2.0 * u4 * a1 + u**8 * a1**2),
        -f * u4 * p1**2,
        2.0 * np.exp(2.0 * q) * np.asarray(scalar_potential(phi), dtype=float),
        (z_h**2)
        * u**6
        * np.exp(-2.0 * q)
        * np.asarray(gauge_coupling(phi), dtype=float)
        * v1**2,
    )
    return _scaled_sum(terms)


def _maxwell_flux(
    z_h: float,
    u: NDArray[np.float64],
    a: NDArray[np.float64],
    p: NDArray[np.float64],
    v: NDArray[np.float64],
    vu: NDArray[np.float64],
) -> NDArray[np.float64]:
    q = u**4 * a
    phi = u**2 * p
    v1 = 2.0 * v + u * vu
    return np.asarray(
        -np.exp(q) * gauge_coupling(phi) * v1 / z_h**2,
        dtype=float,
    )


def _maximum_scaled_array_difference(
    left: NDArray[np.float64],
    right: NDArray[np.float64],
) -> float:
    denominator = np.maximum(1.0, np.maximum(np.abs(left), np.abs(right)))
    return float(np.max(np.abs(left - right) / denominator))


def _scaled_sum(terms: Sequence[NDArray[np.float64]]) -> NDArray[np.float64]:
    numerator = sum(terms)
    denominator = 1.0 + sum(np.abs(term) for term in terms)
    return np.asarray(numerator / denominator, dtype=float)


def _validate_xi(value: Real) -> float:
    if isinstance(value, bool) or not isinstance(value, Real):
        raise ValueError("xi must be a finite nonnegative real number")
    resolved = float(value)
    if not math.isfinite(resolved) or resolved < 0.0:
        raise ValueError("xi must be a finite nonnegative real number")
    return resolved


def _validate_positive(name: str, value: Real) -> None:
    if isinstance(value, bool) or not isinstance(value, Real):
        raise ValueError(f"{name} must be a positive finite real number")
    resolved = float(value)
    if not math.isfinite(resolved) or resolved <= 0.0:
        raise ValueError(f"{name} must be a positive finite real number")


def _validate_integer(name: str, value: Integral, *, minimum: int) -> None:
    if isinstance(value, bool) or not isinstance(value, Integral):
        raise ValueError(f"{name} must be an integer")
    if int(value) < minimum:
        raise ValueError(f"{name} must be at least {minimum}")


__all__ = [
    "DEFAULT_CONTINUATION_XI",
    "DEFAULT_DEGREES",
    "DEFAULT_POLISH_MAXIMUM_EVALUATIONS",
    "DEFAULT_REFINEMENT_ORDER_FLOOR",
    "DEFAULT_REPORTED_XI",
    "EMDContinuation",
    "EMDEquationDiagnostics",
    "EMDProfile",
    "EMDSolverConfig",
    "EMDThermodynamics",
    "GUBSER_ROCHA_DEFINITION",
    "SOURCE_ARCHIVE_SHA256",
    "SOURCE_PDF_SHA256",
    "charge_geometry",
    "equation_diagnostics",
    "exact_factor_fields",
    "exact_thermodynamics",
    "gauge_coupling",
    "profile_thermodynamics",
    "save_gubser_rocha_artifacts",
    "scalar_potential",
    "scalar_potential_prime",
    "scalar_potential_second",
    "solve_emd_continuation",
    "solve_emd_profile",
    "verify_gubser_rocha_emd",
]
