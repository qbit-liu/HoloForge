"""Optical conductivity in the probe-limit HHH superconductor.

This Phase 4 Forge/Verify extension targets the dimension-two theory in
Hartnoll, Herzog, and Horowitz, Phys. Rev. Lett. 101, 031601 (2008),
arXiv:0803.3295v1.  It retains the released nonlinear background equations and
adds a zero-momentum Maxwell response.  A source-free UV series transferred to
a Chebyshev--Gauss--Lobatto bulk element is the primary response method;
Riccati-form DOP853 integration is the independent route.

The module deliberately keeps the low-temperature probe-limit limitation
visible.  The public Figure 2 curve is retained as a provenance-linked
non-reproduction, not as an acceptance target.  Passing a model calculation
would not turn the probe approximation into a controlled zero-temperature
ground state or validate a real material.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import math
from pathlib import Path
from typing import Any, Callable, Dict, Optional, Sequence, Tuple

import numpy as np
from numpy.typing import NDArray
from scipy.integrate import solve_bvp, solve_ivp
from scipy.linalg import solve
from scipy.optimize import root_scalar

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
from holoforge.numerics.interpolation import (
    deterministic_barycentric_interpolator,
)


SOURCE_ID = "arXiv:0803.3295v1"
SOURCE_PDF_SHA256 = (
    "7a9d6ecaf7ee6faf701374ef843bbd8f52eb371697ea0f31414990e0c57cd775"
)
SOURCE_ARCHIVE_SHA256 = (
    "3f0a017843f290e338f6db51d2a791f4bb8daea3d79613d1e09dbd59fad9be36"
)
SOURCE_FIGURE_EPS_SHA256 = (
    "f44e59d520cfd29eb95da61a9b9a0460eccd485a26676535cfed78ae6c857652"
)
SOURCE_RESCALED_FIGURE_EPS_SHA256 = (
    "581233f0dec393aab39ed1be073c55a1a243ae4e4d23fed43277db5da0f6076e"
)

FIGURE_TEMPERATURE_OVER_TC = 0.0026
FIGURE_ANCHORS: Tuple[Tuple[float, float], ...] = (
    (25.0, 0.000094),
    (30.0, 0.001595),
    (35.0, 0.023397),
    (40.0, 0.257286),
    (45.0, 0.920190),
    (50.0, 1.156583),
    (60.0, 1.115810),
    (70.0, 1.066470),
    (80.0, 1.039451),
)
FIGURE_SOURCE_ABSOLUTE_TOLERANCE = 2.0e-2
FIGURE_2_STATUS = "not_reproduced"
FIGURE_2_CROSS_PANEL_SCALE = 45.2420
LITERATURE_SUPERFLUID_COEFFICIENT = 24.0
NEAR_CRITICAL_RELATIVE_TOLERANCE = 0.15
NEAR_CRITICAL_SLOPE_STABILITY_TOLERANCE = 0.10
POLE_INTERCEPT_STABILITY_TOLERANCE = 0.02
NORMAL_CONDUCTIVITY_TOLERANCE = 1.0e-8
RESPONSE_ROUTE_TOLERANCE = 5.0e-4
RESPONSE_RESOLUTION_TOLERANCE = 5.0e-4
PASSIVITY_MINIMUM = -1.0e-8
LOW_TEMPERATURE_CONDENSATE_RANGE = (8.2, 8.7)
SPECTRAL_DEGREES = (96, 128, 160)
SPECTRAL_AUDIT_DEGREES = (192, 256, 320, 384, 512)
SPECTRAL_CONFIRMATION_DEGREE = 640
HISTORICAL_NEAR_CRITICAL_TEMPERATURES = (0.900, 0.940, 0.970, 0.985)
NEAR_CRITICAL_TEMPERATURES = (0.990, 0.995, 0.9975, 0.999)
NEAR_CRITICAL_FREQUENCIES = (0.200, 0.100, 0.050, 0.025)
NEAR_CRITICAL_SPECTRAL_DEGREES = (128, 160, 192)
STATIC_LONDON_HORIZON_CUTOFF = 1.0e-7
STATIC_LONDON_UV_FIT_MAXIMUM = 5.0e-4
STATIC_LONDON_UV_REFINEMENT_MAXIMUM = 2.5e-4
STATIC_LONDON_RELATIVE_TOLERANCE = 1.0e-11
STATIC_LONDON_ABSOLUTE_TOLERANCE = 1.0e-13
HORIZON_CUTOFFS = (2.0e-6, 1.0e-6, 5.0e-7)
ASYMPTOTIC_UV_FIT_MAXIMA = (5.0e-5, 2.5e-5)
ENDPOINT_SPLIT_COORDINATE = 1.0e-5
ENDPOINT_SPLIT_DEGREE_PAIRS = ((24, 384), (32, 512), (40, 640))
ENDPOINT_SPLIT_EQUATION_TOLERANCE = 1.0e-7
ENDPOINT_SPLIT_UV_TOLERANCE = 1.0e-10
ENDPOINT_SPLIT_HORIZON_TOLERANCE = 1.0e-9
ENDPOINT_SPLIT_INTERFACE_TOLERANCE = 1.0e-10
ENDPOINT_SPLIT_CONDITIONING_BUDGET = 1.0e-4
UV_TRANSFER_SERIES_ORDERS = (4, 3)
UV_TRANSFER_BULK_DEGREES = (384, 512, 640)
UV_TRANSFER_EQUATION_TOLERANCE = 1.0e-7
UV_TRANSFER_ROW_TOLERANCE = 1.0e-10
UV_TRANSFER_HORIZON_TOLERANCE = 1.0e-9
UV_TRANSFER_CONDITIONING_BUDGET = 1.0e-4
UV_TRANSFER_TRUNCATION_TOLERANCE = 1.0e-6
UV_TRANSFER_CONTROL_DEGREES = (192, 256, 320)
UV_TRANSFER_CONTROL_EQUATION_TOLERANCE = 1.0e-6
UV_TRANSFER_CONTROL_BOUNDARY_TOLERANCE = 1.0e-9
UV_TRANSFER_TARGET_DEGREES = (384, 512, 640)
UV_TRANSFER_TARGET_EQUATION_TOLERANCE = 1.0e-5
UV_TRANSFER_TARGET_BOUNDARY_TOLERANCE = 1.0e-9

BACKGROUND_TEMPERATURE_TOLERANCE = 2.0e-6
BACKGROUND_SOURCE_TOLERANCE = 1.0e-8
BACKGROUND_BVP_TOLERANCE = 1.1e-7
BACKGROUND_OVERLAP_TOLERANCE = 1.0e-6
BACKGROUND_EQUATION_TOLERANCE = 1.0e-7
RESIDUAL_UV_MAXIMUM_COORDINATE = 0.1
RESIDUAL_HORIZON_MINIMUM_COORDINATE = 0.9


OPTICAL_DEFINITION = BenchmarkDefinition(
    identifier="holographic-superconductor-optical",
    support_level="reproduced",
    background=BackgroundSpec(
        identifier="planar-ads4-schwarzschild-probe-limit",
        dimension=4,
        coordinate="u = r_h/r in [0, 1]",
        description=(
            "The released dimension-two HHH probe-limit background, with "
            "normal, near-critical, and conditioned low-temperature states."
        ),
    ),
    equations=(
        EquationSpec(
            identifier="optical-maxwell-response",
            kind="linear retarded response equation",
            dependent_fields=("A_x", "psi"),
            expression=(
                "A_x'' + (F'/F) A_x' + "
                "[Omega^2/F^2 - 2 psi^2/(u^2 F)] A_x = 0"
            ),
            source_reference="Hartnoll et al., arXiv:0803.3295v1, Eq. (13)",
        ),
        EquationSpec(
            identifier="static-london-response",
            kind="zero-frequency linear response equation",
            dependent_fields=("A_x", "psi"),
            expression="(F A_x')' - 2 psi^2 A_x/u^2 = 0",
            source_reference="Hartnoll et al., arXiv:0810.1563, Sec. IV",
        ),
    ),
    boundary_conditions=(
        BoundaryConditionSpec(
            field="A_x",
            location="u = 1 (horizon)",
            role="retarded ingoing response",
            expression="A_x = (1-u)^(-i Omega/3) a(u), with a regular",
            interpretation=(
                "The sign follows delta A_x proportional to exp(-i omega t)."
            ),
        ),
        BoundaryConditionSpec(
            field="A_x",
            location="u = 1 (horizon), Omega = 0",
            role="regular static London response",
            expression="A_x'(1) + (2 psi_h^2/3) A_x(1) = 0",
            interpretation="The zero-frequency solution is horizon regular.",
        ),
        BoundaryConditionSpec(
            field="A_x",
            location="u = 0 (UV boundary)",
            role="unit applied gauge-field source",
            expression="A_x = A_0 + A_1 u + ... with A_0 = 1",
            interpretation=(
                "The boundary current response is A_1 and "
                "sigma = -i A_1/(Omega A_0)."
            ),
        ),
    ),
    solvers=(
        SolverSpec(
            problem_type="linear optical boundary-value problem",
            library_function="scipy.linalg.solve",
            method="analytic UV series transfer plus Chebyshev bulk collocation",
            description=(
                "The primary route removes the source-free UV singular "
                "structure before the spectral bulk solve."
            ),
        ),
        SolverSpec(
            problem_type="static London initial-value problem",
            library_function="scipy.integrate.solve_ivp",
            method="Riccati logarithmic derivative with DOP853",
            description=(
                "The primary superfluid-density route uses two frozen UV "
                "intercept windows."
            ),
        ),
        SolverSpec(
            problem_type="linear optical initial-value problem",
            library_function="scipy.integrate.solve_ivp",
            method="Riccati logarithmic derivative with DOP853",
            description=(
                "An amplitude-independent route with a quadratic UV-intercept fit."
            ),
        ),
    ),
    observables=(
        ObservableSpec(
            identifier="complex-optical-conductivity",
            symbol="sigma(omega)",
            extraction="sigma = -i A_1/(Omega A_0) from the UV response.",
            normalization="omega/T = 4 pi Omega/3 and A_0 = 1.",
        ),
        ObservableSpec(
            identifier="superfluid-density-coefficient",
            symbol="C_2",
            extraction=(
                "Fit static n_s/T_c to C_2 delta + C_4 delta^2; use the "
                "finite-frequency pole intercept as an independent route."
            ),
            normalization=(
                "delta = 1 - T/T_c and n_s/T_c = "
                "-(4 pi/3)(T/T_c) A_x'(0)/A_x(0)."
            ),
        ),
    ),
)


ScalarProfile = Callable[[NDArray[np.float64]], NDArray[np.float64]]


@dataclass(frozen=True)
class ConditionedBackgroundConfig:
    """Frozen controls for the approved fixed-density continuation."""

    radial_cutoff: float = 1.0e-5
    mesh_points: int = 500
    tolerance: float = 1.0e-7
    max_nodes: int = 250_000
    overlap_horizon_scalar: float = 22.22
    max_seed_ratio: float = 1.05

    def __post_init__(self) -> None:
        _validate_positive("radial_cutoff", self.radial_cutoff)
        if float(self.radial_cutoff) > 1.0e-2:
            raise ValueError("radial_cutoff must be at most 0.01")
        _validate_integer("mesh_points", self.mesh_points, minimum=20)
        _validate_positive("tolerance", self.tolerance)
        _validate_integer("max_nodes", self.max_nodes, minimum=self.mesh_points)
        _validate_positive(
            "overlap_horizon_scalar", self.overlap_horizon_scalar
        )
        if not _is_finite_real(self.max_seed_ratio) or not (
            1.0 < float(self.max_seed_ratio) <= 1.05
        ):
            raise ValueError("max_seed_ratio must satisfy 1 < value <= 1.05")


@dataclass(frozen=True)
class BackgroundState:
    """One nonlinear HHH background with invariant diagnostics."""

    coordinate_system: str
    radius: float
    critical_tc_over_sqrt_rho: float
    radial_cutoff: float
    temperature_over_tc: float
    chemical_potential: float
    charge_density: float
    scalar_source: float
    scalar_response: float
    horizon_scalar: float
    horizon_electric_field: float
    bvp_max_rms_residual: float
    mesh_nodes: int
    solution: Any = field(repr=False, compare=False)

    def scalar_profile(
        self, coordinate: NDArray[np.float64]
    ) -> NDArray[np.float64]:
        """Evaluate ``psi(u)`` with the frozen UV/IR endpoint expansions."""

        values = np.asarray(coordinate, dtype=float)
        if not np.all(np.isfinite(values)) or np.any(values < 0.0) or np.any(
            values > 1.0
        ):
            raise ValueError("background coordinates must lie in [0, 1]")
        flattened = values.reshape(-1)
        result = np.empty_like(flattened)
        cutoff = self.radial_cutoff
        uv = flattened < cutoff
        horizon = flattened > 1.0 - cutoff
        interior = ~(uv | horizon)
        result[uv] = (
            self.scalar_source * flattened[uv]
            + self.scalar_response * flattened[uv] ** 2
        )
        distance = 1.0 - flattened[horizon]
        result[horizon] = self.horizon_scalar * (1.0 - 2.0 * distance / 3.0)
        if np.any(interior):
            if self.coordinate_system == "u":
                evaluation_coordinate = flattened[interior]
            elif self.coordinate_system == "z":
                evaluation_coordinate = self.radius * flattened[interior]
            else:
                raise RuntimeError("unknown background coordinate system")
            result[interior] = np.asarray(
                self.solution.sol(evaluation_coordinate)[0], dtype=float
            )
        return result.reshape(values.shape)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "coordinate_system": self.coordinate_system,
            "radius": self.radius,
            "temperature_over_tc": self.temperature_over_tc,
            "chemical_potential": self.chemical_potential,
            "charge_density": self.charge_density,
            "scalar_source": self.scalar_source,
            "scalar_response": self.scalar_response,
            "horizon_scalar": self.horizon_scalar,
            "horizon_electric_field": self.horizon_electric_field,
            "bvp_max_rms_residual": self.bvp_max_rms_residual,
            "mesh_nodes": self.mesh_nodes,
        }


@dataclass(frozen=True)
class BackgroundOverlap:
    """Equivalence evidence at the last accepted original-``u`` state."""

    original: BackgroundState
    conditioned: BackgroundState
    mapped_equation_residual: float
    mapped_boundary_residual: float
    temperature_relative_error: float
    uv_relative_error: float
    horizon_relative_error: float

    @property
    def passed(self) -> bool:
        return bool(
            self.mapped_equation_residual <= BACKGROUND_EQUATION_TOLERANCE
            and self.mapped_boundary_residual <= BACKGROUND_EQUATION_TOLERANCE
            and self.temperature_relative_error <= BACKGROUND_OVERLAP_TOLERANCE
            and self.uv_relative_error <= BACKGROUND_OVERLAP_TOLERANCE
            and self.horizon_relative_error <= BACKGROUND_OVERLAP_TOLERANCE
            and abs(self.original.scalar_source)
            <= BACKGROUND_SOURCE_TOLERANCE
            and abs(self.conditioned.scalar_source)
            <= BACKGROUND_SOURCE_TOLERANCE
            and self.original.bvp_max_rms_residual
            <= BACKGROUND_BVP_TOLERANCE
            and self.conditioned.bvp_max_rms_residual
            <= BACKGROUND_BVP_TOLERANCE
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "passed": self.passed,
            "original": self.original.to_dict(),
            "conditioned": self.conditioned.to_dict(),
            "mapped_equation_residual": self.mapped_equation_residual,
            "mapped_boundary_residual": self.mapped_boundary_residual,
            "temperature_relative_error": self.temperature_relative_error,
            "uv_relative_error": self.uv_relative_error,
            "horizon_relative_error": self.horizon_relative_error,
        }


@dataclass(frozen=True)
class BackgroundContinuationStep:
    """One deterministic fixed-density continuation step."""

    radius: float
    temperature_over_tc: float
    mesh_nodes: int
    bvp_max_rms_residual: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "radius": self.radius,
            "temperature_over_tc": self.temperature_over_tc,
            "mesh_nodes": self.mesh_nodes,
            "bvp_max_rms_residual": self.bvp_max_rms_residual,
        }


@dataclass(frozen=True)
class ConditionedBackgroundResult:
    """Approved overlap evidence and a reached low-temperature target."""

    config: ConditionedBackgroundConfig
    target_temperature_over_tc: float
    overlap: BackgroundOverlap
    steps: Tuple[BackgroundContinuationStep, ...]
    target: BackgroundState

    @property
    def passed(self) -> bool:
        return bool(
            self.overlap.passed
            and abs(
                self.target.temperature_over_tc
                - self.target_temperature_over_tc
            )
            <= BACKGROUND_TEMPERATURE_TOLERANCE
            and abs(self.target.scalar_source) <= BACKGROUND_SOURCE_TOLERANCE
            and self.target.bvp_max_rms_residual
            <= BACKGROUND_BVP_TOLERANCE
            and self.target.charge_density > 0.0
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "passed": self.passed,
            "target_temperature_over_tc": self.target_temperature_over_tc,
            "overlap": self.overlap.to_dict(),
            "steps": [step.to_dict() for step in self.steps],
            "target": self.target.to_dict(),
        }


def solve_conditioned_background(
    target_temperature_over_tc: float = FIGURE_TEMPERATURE_OVER_TC,
    *,
    critical_tc_over_sqrt_rho: Optional[float] = None,
    config: Optional[ConditionedBackgroundConfig] = None,
) -> ConditionedBackgroundResult:
    """Run the approved R1--R3 overlap and fixed-density continuation."""

    _validate_positive(
        "target_temperature_over_tc", target_temperature_over_tc
    )
    if config is None:
        config = ConditionedBackgroundConfig()
    if critical_tc_over_sqrt_rho is None:
        from holoforge.benchmarks.holographic_superconductor import solve_onset

        critical_tc_over_sqrt_rho = solve_onset().tc_over_sqrt_rho
    _validate_positive(
        "critical_tc_over_sqrt_rho", critical_tc_over_sqrt_rho
    )
    critical_ratio = float(critical_tc_over_sqrt_rho)
    original = _solve_original_overlap_state(critical_ratio, config)
    conditioned = _condition_original_state(original, config)
    overlap = _overlap_diagnostics(original, conditioned)
    if not overlap.passed:
        raise RuntimeError("conditioned background failed the frozen overlap gate")

    target_radius = 3.0 / (
        4.0
        * math.pi
        * critical_ratio
        * float(target_temperature_over_tc)
    )
    if target_radius < conditioned.radius:
        raise ValueError(
            "conditioned target must not precede the approved overlap state"
        )

    state = conditioned
    steps = []
    while state.radius < target_radius * (1.0 - 1.0e-14):
        next_radius = min(
            target_radius, state.radius * float(config.max_seed_ratio)
        )
        state = _solve_conditioned_radius(state, next_radius, config)
        steps.append(
            BackgroundContinuationStep(
                radius=state.radius,
                temperature_over_tc=state.temperature_over_tc,
                mesh_nodes=state.mesh_nodes,
                bvp_max_rms_residual=state.bvp_max_rms_residual,
            )
        )
    result = ConditionedBackgroundResult(
        config=config,
        target_temperature_over_tc=float(target_temperature_over_tc),
        overlap=overlap,
        steps=tuple(steps),
        target=state,
    )
    if not result.passed:
        raise RuntimeError("conditioned background missed a frozen target gate")
    return result


def _refine_conditioned_background_cutoff(
    state: BackgroundState,
    *,
    radial_cutoff: float = 5.0e-6,
    tolerance: float = 1.0e-7,
    max_nodes: int = 250_000,
) -> BackgroundState:
    """Repeat an accepted conditioned state at a smaller endpoint cutoff."""

    if state.coordinate_system != "z":
        raise ValueError("cutoff refinement requires a conditioned z state")
    _validate_positive("radial_cutoff", radial_cutoff)
    _validate_positive("tolerance", tolerance)
    _validate_integer("max_nodes", max_nodes, minimum=20)
    if float(radial_cutoff) >= state.radial_cutoff:
        raise ValueError("refined radial_cutoff must be smaller than the primary")
    radius = state.radius
    left = radius * float(radial_cutoff)
    right = radius * (1.0 - float(radial_cutoff))
    prior_nodes = np.asarray(state.solution.x, dtype=float)
    coordinate = np.unique(
        np.concatenate(
            (
                (left,),
                prior_nodes[(prior_nodes > left) & (prior_nodes < right)],
                (right,),
            )
        )
    )
    guess = np.asarray(state.solution.sol(coordinate), dtype=float)
    solution = solve_bvp(
        lambda values, fields: _conditioned_background_equations(
            values, fields, radius
        ),
        lambda left_values, right_values: _conditioned_background_boundaries(
            left_values,
            right_values,
            radius,
            float(radial_cutoff),
        ),
        coordinate,
        guess,
        tol=float(tolerance),
        max_nodes=int(max_nodes),
        verbose=0,
    )
    if not solution.success:
        raise RuntimeError(
            "conditioned cutoff refinement failed: " + solution.message
        )
    config = ConditionedBackgroundConfig(
        radial_cutoff=float(radial_cutoff),
        tolerance=float(tolerance),
        max_nodes=int(max_nodes),
    )
    refined = _state_from_conditioned_solution(
        solution,
        radius,
        state.critical_tc_over_sqrt_rho,
        config,
    )
    if (
        abs(refined.temperature_over_tc - state.temperature_over_tc)
        > BACKGROUND_TEMPERATURE_TOLERANCE
        or abs(refined.scalar_source) > BACKGROUND_SOURCE_TOLERANCE
        or refined.bvp_max_rms_residual > BACKGROUND_BVP_TOLERANCE
        or refined.charge_density <= 0.0
    ):
        raise RuntimeError("conditioned cutoff refinement missed a frozen gate")
    return refined


def solve_original_background_at_temperature(
    target_temperature_over_tc: float,
    *,
    critical_tc_over_sqrt_rho: Optional[float] = None,
    config: Optional[ConditionedBackgroundConfig] = None,
) -> BackgroundState:
    """Target a moderate-temperature state on the accepted original branch."""

    _validate_positive(
        "target_temperature_over_tc", target_temperature_over_tc
    )
    target_temperature = float(target_temperature_over_tc)
    if target_temperature >= 1.0:
        raise ValueError("condensed target temperature must be below one")
    if config is None:
        config = ConditionedBackgroundConfig()
    if critical_tc_over_sqrt_rho is None:
        from holoforge.benchmarks.holographic_superconductor import solve_onset

        critical_tc_over_sqrt_rho = solve_onset().tc_over_sqrt_rho
    _validate_positive(
        "critical_tc_over_sqrt_rho", critical_tc_over_sqrt_rho
    )
    critical_ratio = float(critical_tc_over_sqrt_rho)

    cached_solutions: Dict[float, Any] = {}
    cached_states: Dict[float, BackgroundState] = {}

    def solve_horizon(horizon_scalar: float, prior: Any) -> BackgroundState:
        key = float(horizon_scalar)
        if key in cached_states:
            return cached_states[key]
        coordinate, guess = _original_initial_guess(key, config, prior)
        solution = solve_bvp(
            _original_background_equations,
            lambda left, right: _original_background_boundaries(
                left, right, key, config.radial_cutoff
            ),
            coordinate,
            guess,
            tol=config.tolerance,
            max_nodes=config.max_nodes,
            verbose=0,
        )
        if not solution.success:
            raise RuntimeError(
                "moderate-temperature background failed at horizon scalar "
                f"{key:.8g}: {solution.message}"
            )
        state = _state_from_original_solution(
            solution, critical_ratio, config
        )
        cached_solutions[key] = solution
        cached_states[key] = state
        return state

    lower_horizon = None
    upper_horizon = None
    prior_solution = None
    prior_horizon = None
    prior_state = None
    for horizon_scalar in np.geomspace(
        0.02, config.overlap_horizon_scalar, 96
    ):
        state = solve_horizon(float(horizon_scalar), prior_solution)
        if state.temperature_over_tc <= target_temperature:
            if prior_horizon is None or prior_state is None:
                raise RuntimeError(
                    "moderate-temperature scan began below the requested target"
                )
            lower_horizon = prior_horizon
            upper_horizon = float(horizon_scalar)
            break
        prior_horizon = float(horizon_scalar)
        prior_state = state
        prior_solution = state.solution
    if lower_horizon is None or upper_horizon is None:
        raise RuntimeError("could not bracket the requested background temperature")

    def temperature_residual(log_horizon: float) -> float:
        horizon_scalar = math.exp(float(log_horizon))
        if horizon_scalar not in cached_states:
            nearest = min(
                cached_solutions,
                key=lambda value: abs(math.log(value) - log_horizon),
            )
            solve_horizon(horizon_scalar, cached_solutions[nearest])
        return (
            cached_states[horizon_scalar].temperature_over_tc
            - target_temperature
        )

    root = root_scalar(
        temperature_residual,
        bracket=(math.log(lower_horizon), math.log(upper_horizon)),
        method="brentq",
        xtol=1.0e-11,
        rtol=1.0e-11,
    )
    if not root.converged:
        raise RuntimeError("moderate-temperature root solve did not converge")
    horizon_scalar = math.exp(float(root.root))
    if horizon_scalar not in cached_states:
        nearest = min(
            cached_solutions,
            key=lambda value: abs(math.log(value) - float(root.root)),
        )
        solve_horizon(horizon_scalar, cached_solutions[nearest])
    state = cached_states[horizon_scalar]
    if (
        abs(state.temperature_over_tc - target_temperature)
        > BACKGROUND_TEMPERATURE_TOLERANCE
        or abs(state.scalar_source) > BACKGROUND_SOURCE_TOLERANCE
        or state.bvp_max_rms_residual > BACKGROUND_BVP_TOLERANCE
    ):
        raise RuntimeError("moderate-temperature background missed a frozen gate")
    return state


def _solve_original_overlap_state(
    critical_ratio: float, config: ConditionedBackgroundConfig
) -> BackgroundState:
    horizon_values = list(np.geomspace(0.02, 20.0, 32))
    horizon_values.extend((20.5, 21.0, 21.5, 22.0, 22.1, 22.15, 22.2))
    if config.overlap_horizon_scalar > 22.2:
        horizon_values.append(float(config.overlap_horizon_scalar))
    else:
        horizon_values = [
            value
            for value in horizon_values
            if value < float(config.overlap_horizon_scalar)
        ]
        horizon_values.append(float(config.overlap_horizon_scalar))

    prior = None
    for horizon_scalar in horizon_values:
        coordinate, guess = _original_initial_guess(
            horizon_scalar, config, prior
        )
        solution = solve_bvp(
            _original_background_equations,
            lambda left, right, value=horizon_scalar: (
                _original_background_boundaries(
                    left, right, value, config.radial_cutoff
                )
            ),
            coordinate,
            guess,
            tol=config.tolerance,
            max_nodes=config.max_nodes,
            verbose=0,
        )
        if not solution.success:
            raise RuntimeError(
                "original-u overlap continuation failed at horizon scalar "
                f"{horizon_scalar:.8g}: {solution.message}"
            )
        prior = solution
    if prior is None:
        raise RuntimeError("original-u overlap continuation produced no state")
    return _state_from_original_solution(prior, critical_ratio, config)


def _condition_original_state(
    original: BackgroundState, config: ConditionedBackgroundConfig
) -> BackgroundState:
    radius = original.radius
    original_coordinate = np.asarray(original.solution.x, dtype=float)
    original_coordinate = np.sort(
        np.concatenate(
            (
                original_coordinate,
                0.5 * (original_coordinate[:-1] + original_coordinate[1:]),
            )
        )
    )
    coordinate = radius * original_coordinate
    original_fields = np.asarray(
        original.solution.sol(original_coordinate), dtype=float
    )
    guess = np.vstack(
        (
            original_fields[0],
            original_fields[1] / radius,
            original_fields[2] / radius,
            original_fields[3] / radius**2,
        )
    )
    solution = solve_bvp(
        lambda values, fields: _conditioned_background_equations(
            values, fields, radius
        ),
        lambda left, right: _conditioned_background_boundaries(
            left, right, radius, config.radial_cutoff
        ),
        coordinate,
        guess,
        # The overlap gate is a stricter equivalence diagnostic than ordinary
        # branch continuation.  Tighten the same maintained solver rather
        # than altering the frozen residual ceiling after seeing the result.
        tol=min(config.tolerance, 1.0e-8),
        max_nodes=config.max_nodes,
        verbose=0,
    )
    if not solution.success:
        raise RuntimeError(
            f"conditioned overlap solve failed: {solution.message}"
        )
    return _state_from_conditioned_solution(
        solution, radius, original.critical_tc_over_sqrt_rho, config
    )


def _solve_conditioned_radius(
    prior: BackgroundState,
    target_radius: float,
    config: ConditionedBackgroundConfig,
) -> BackgroundState:
    ratio = float(target_radius) / prior.radius
    if ratio <= 1.0 or ratio > float(config.max_seed_ratio) * (1.0 + 1.0e-13):
        raise ValueError("conditioned continuation step exceeds max_seed_ratio")
    normalized = np.asarray(prior.solution.x, dtype=float) / prior.radius
    coordinate = float(target_radius) * normalized
    prior_fields = np.asarray(prior.solution.sol(prior.solution.x), dtype=float)
    guess = np.vstack(
        (
            prior_fields[0],
            prior_fields[1] / ratio,
            prior_fields[2] * ratio,
            prior_fields[3],
        )
    )
    solution = solve_bvp(
        lambda values, fields: _conditioned_background_equations(
            values, fields, float(target_radius)
        ),
        lambda left, right: _conditioned_background_boundaries(
            left, right, float(target_radius), config.radial_cutoff
        ),
        coordinate,
        guess,
        tol=config.tolerance,
        max_nodes=config.max_nodes,
        verbose=0,
    )
    if not solution.success:
        raise RuntimeError(
            "conditioned continuation failed at R="
            f"{float(target_radius):.10g}: {solution.message}"
        )
    return _state_from_conditioned_solution(
        solution,
        float(target_radius),
        prior.critical_tc_over_sqrt_rho,
        config,
    )


def _original_initial_guess(
    horizon_scalar: float,
    config: ConditionedBackgroundConfig,
    prior_solution: Any,
) -> Tuple[NDArray[np.float64], NDArray[np.float64]]:
    coordinate = np.linspace(
        config.radial_cutoff,
        1.0 - config.radial_cutoff,
        config.mesh_points,
    )
    if prior_solution is not None:
        fields = np.asarray(prior_solution.sol(coordinate), dtype=float)
        fields[0:2] *= float(horizon_scalar) / fields[0, -1]
        return coordinate, fields
    scalar = float(horizon_scalar) * coordinate**2 * (
        7.0 / 3.0 - 4.0 * coordinate / 3.0
    )
    scalar_prime = float(horizon_scalar) * (
        2.0 * coordinate * (7.0 / 3.0 - 4.0 * coordinate / 3.0)
        - 4.0 * coordinate**2 / 3.0
    )
    potential = 4.1 * (1.0 - coordinate)
    potential_prime = np.full_like(coordinate, -4.1)
    return coordinate, np.vstack(
        (scalar, scalar_prime, potential, potential_prime)
    )


def _original_background_equations(
    coordinate: NDArray[np.float64], fields: NDArray[np.float64]
) -> NDArray[np.float64]:
    scalar, scalar_prime, potential, potential_prime = fields
    blackening = 1.0 - coordinate**3
    blackening_prime = -3.0 * coordinate**2
    return np.vstack(
        (
            scalar_prime,
            -(blackening_prime / blackening - 2.0 / coordinate)
            * scalar_prime
            - (
                potential**2 / blackening**2
                + 2.0 / (coordinate**2 * blackening)
            )
            * scalar,
            potential_prime,
            2.0
            * scalar**2
            * potential
            / (coordinate**2 * blackening),
        )
    )


def _original_background_boundaries(
    left: NDArray[np.float64],
    right: NDArray[np.float64],
    horizon_scalar: float,
    cutoff: float,
) -> NDArray[np.float64]:
    return np.asarray(
        (
            2.0 * left[0] / cutoff - left[1],
            right[2] + cutoff * right[3],
            right[1] - 2.0 * right[0] / 3.0,
            right[0] - float(horizon_scalar),
        ),
        dtype=float,
    )


def _conditioned_background_equations(
    coordinate: NDArray[np.float64],
    fields: NDArray[np.float64],
    radius: float,
) -> NDArray[np.float64]:
    scalar, scalar_prime, potential, potential_prime = fields
    blackening = 1.0 - (coordinate / radius) ** 3
    blackening_prime = -3.0 * coordinate**2 / radius**3
    return np.vstack(
        (
            scalar_prime,
            -(blackening_prime / blackening - 2.0 / coordinate)
            * scalar_prime
            - (
                potential**2 / blackening**2
                + 2.0 / (coordinate**2 * blackening)
            )
            * scalar,
            potential_prime,
            2.0
            * scalar**2
            * potential
            / (coordinate**2 * blackening),
        )
    )


def _conditioned_background_boundaries(
    left: NDArray[np.float64],
    right: NDArray[np.float64],
    radius: float,
    cutoff: float,
) -> NDArray[np.float64]:
    left_coordinate = radius * cutoff
    horizon_distance = radius * cutoff
    return np.asarray(
        (
            2.0 * left[0] / left_coordinate - left[1],
            left[3] + 1.0,
            right[2] + horizon_distance * right[3],
            right[1] - 2.0 * right[0] / (3.0 * radius),
        ),
        dtype=float,
    )


def _state_from_original_solution(
    solution: Any,
    critical_ratio: float,
    config: ConditionedBackgroundConfig,
) -> BackgroundState:
    cutoff = config.radial_cutoff
    left = np.asarray(solution.sol(cutoff), dtype=float)
    right = np.asarray(solution.sol(1.0 - cutoff), dtype=float)
    scalar_source, scalar_response = _scalar_uv_coefficients(
        left[0], left[1], cutoff
    )
    charge_density = -left[3]
    if charge_density <= 0.0:
        raise RuntimeError("original-u background has nonpositive charge density")
    radius = math.sqrt(charge_density)
    return BackgroundState(
        coordinate_system="u",
        radius=radius,
        critical_tc_over_sqrt_rho=critical_ratio,
        radial_cutoff=cutoff,
        temperature_over_tc=_temperature_over_tc(radius, critical_ratio),
        chemical_potential=float(left[2] - cutoff * left[3]),
        charge_density=float(charge_density),
        scalar_source=float(scalar_source),
        scalar_response=float(scalar_response),
        horizon_scalar=float(right[0] / (1.0 - 2.0 * cutoff / 3.0)),
        horizon_electric_field=float(right[3]),
        bvp_max_rms_residual=float(np.max(solution.rms_residuals)),
        mesh_nodes=int(solution.x.size),
        solution=solution,
    )


def _state_from_conditioned_solution(
    solution: Any,
    radius: float,
    critical_ratio: float,
    config: ConditionedBackgroundConfig,
) -> BackgroundState:
    cutoff = config.radial_cutoff
    left_coordinate = radius * cutoff
    right_coordinate = radius * (1.0 - cutoff)
    left = np.asarray(solution.sol(left_coordinate), dtype=float)
    right = np.asarray(solution.sol(right_coordinate), dtype=float)
    scalar_u_derivative = radius * left[1]
    scalar_source, scalar_response = _scalar_uv_coefficients(
        left[0], scalar_u_derivative, cutoff
    )
    charge_density = -radius**2 * left[3]
    if charge_density <= 0.0:
        raise RuntimeError("conditioned background has nonpositive charge density")
    return BackgroundState(
        coordinate_system="z",
        radius=float(radius),
        critical_tc_over_sqrt_rho=critical_ratio,
        radial_cutoff=cutoff,
        temperature_over_tc=_temperature_over_tc(radius, critical_ratio),
        chemical_potential=float(radius * (left[2] - left_coordinate * left[3])),
        charge_density=float(charge_density),
        scalar_source=float(scalar_source),
        scalar_response=float(scalar_response),
        horizon_scalar=float(right[0] / (1.0 - 2.0 * cutoff / 3.0)),
        horizon_electric_field=float(radius**2 * right[3]),
        bvp_max_rms_residual=float(np.max(solution.rms_residuals)),
        mesh_nodes=int(solution.x.size),
        solution=solution,
    )


def _scalar_uv_coefficients(
    scalar: float, scalar_derivative: float, cutoff: float
) -> Tuple[float, float]:
    source = 2.0 * scalar / cutoff - scalar_derivative
    response = (scalar_derivative - scalar / cutoff) / cutoff
    return float(source), float(response)


def _temperature_over_tc(radius: float, critical_ratio: float) -> float:
    return 3.0 / (4.0 * math.pi * float(radius) * float(critical_ratio))


def _overlap_diagnostics(
    original: BackgroundState, conditioned: BackgroundState
) -> BackgroundOverlap:
    mapped_equation, mapped_boundary = _mapped_original_residual(conditioned)
    original_uv = np.asarray(
        (
            original.chemical_potential,
            original.charge_density,
            original.scalar_response,
        ),
        dtype=float,
    )
    conditioned_uv = np.asarray(
        (
            conditioned.chemical_potential,
            conditioned.charge_density,
            conditioned.scalar_response,
        ),
        dtype=float,
    )
    original_horizon = np.asarray(
        (original.horizon_scalar, original.horizon_electric_field), dtype=float
    )
    conditioned_horizon = np.asarray(
        (conditioned.horizon_scalar, conditioned.horizon_electric_field),
        dtype=float,
    )
    return BackgroundOverlap(
        original=original,
        conditioned=conditioned,
        mapped_equation_residual=mapped_equation,
        mapped_boundary_residual=mapped_boundary,
        temperature_relative_error=_relative_error(
            conditioned.temperature_over_tc, original.temperature_over_tc
        ),
        uv_relative_error=_array_relative_error(conditioned_uv, original_uv),
        horizon_relative_error=_array_relative_error(
            conditioned_horizon, original_horizon
        ),
    )


def _mapped_original_residual(state: BackgroundState) -> Tuple[float, float]:
    if state.coordinate_system != "z":
        raise ValueError("mapped residual requires a conditioned z solution")
    cutoff = state.radial_cutoff
    coordinate = np.linspace(cutoff, 1.0 - cutoff, 2001)
    z_coordinate = state.radius * coordinate
    fields = np.asarray(state.solution.sol(z_coordinate), dtype=float)
    first = np.asarray(state.solution.sol(z_coordinate, 1), dtype=float)
    scalar = fields[0]
    scalar_u = state.radius * first[0]
    scalar_uu = state.radius**2 * first[1]
    potential = state.radius * fields[2]
    potential_uu = state.radius**3 * first[3]
    blackening = 1.0 - coordinate**3
    blackening_prime = -3.0 * coordinate**2
    scalar_first_term = (
        blackening_prime / blackening - 2.0 / coordinate
    ) * scalar_u
    scalar_potential_term = (
        potential**2 / blackening**2
        + 2.0 / (coordinate**2 * blackening)
    ) * scalar
    scalar_residual = scalar_uu + scalar_first_term + scalar_potential_term
    scalar_scale = (
        np.abs(scalar_uu)
        + np.abs(scalar_first_term)
        + np.abs(scalar_potential_term)
        + 1.0
    )
    gauge_term = 2.0 * scalar**2 * potential / (
        coordinate**2 * blackening
    )
    gauge_residual = potential_uu - gauge_term
    gauge_scale = np.abs(potential_uu) + np.abs(gauge_term) + 1.0
    equation_residual = float(
        max(
            np.max(np.abs(scalar_residual) / scalar_scale),
            np.max(np.abs(gauge_residual) / gauge_scale),
        )
    )
    left = fields[:, 0]
    right = fields[:, -1]
    left_u = np.asarray(
        (
            left[0],
            state.radius * first[0, 0],
            state.radius * left[2],
            state.radius**2 * first[2, 0],
        ),
        dtype=float,
    )
    right_u = np.asarray(
        (
            right[0],
            state.radius * first[0, -1],
            state.radius * right[2],
            state.radius**2 * first[2, -1],
        ),
        dtype=float,
    )
    boundary_values = np.asarray(
        (
            2.0 * left_u[0] / cutoff - left_u[1],
            right_u[2] + cutoff * right_u[3],
            right_u[1] - 2.0 * right_u[0] / 3.0,
            -left_u[3] / state.radius**2 - 1.0,
        ),
        dtype=float,
    )
    boundary_scales = np.asarray(
        (
            abs(2.0 * left_u[0] / cutoff) + abs(left_u[1]) + 1.0,
            abs(right_u[2]) + abs(cutoff * right_u[3]) + 1.0,
            abs(right_u[1]) + abs(2.0 * right_u[0] / 3.0) + 1.0,
            abs(left_u[3] / state.radius**2) + 2.0,
        ),
        dtype=float,
    )
    boundary_residual = float(
        np.max(np.abs(boundary_values) / boundary_scales)
    )
    return equation_residual, boundary_residual


def _relative_error(value: float, reference: float) -> float:
    return float(abs(value - reference) / max(abs(reference), 1.0e-12))


def _array_relative_error(
    values: NDArray[np.float64], reference: NDArray[np.float64]
) -> float:
    return float(
        np.max(np.abs(values - reference) / np.maximum(np.abs(reference), 1.0e-12))
    )


def dimensionless_frequency(omega_over_temperature: float) -> float:
    """Return ``Omega = omega/r_h`` from the source Figure 2 axis."""

    _validate_positive("omega_over_temperature", omega_over_temperature)
    return 3.0 * float(omega_over_temperature) / (4.0 * math.pi)


def omega_over_temperature(dimensionless_omega: float) -> float:
    """Return ``omega/T`` for ``T = 3 r_h/(4 pi)``."""

    _validate_positive("dimensionless_omega", dimensionless_omega)
    return 4.0 * math.pi * float(dimensionless_omega) / 3.0


def ingoing_exponent(dimensionless_omega: float) -> complex:
    """Return the retarded exponent for the ``exp(-i omega t)`` convention."""

    _validate_positive("dimensionless_omega", dimensionless_omega)
    return -1j * float(dimensionless_omega) / 3.0


def horizon_frobenius_coefficient(
    dimensionless_omega: float, horizon_scalar: float
) -> complex:
    """Return the first regular coefficient in ``A_x=s^p(1+c1 s+...)``."""

    _validate_positive("dimensionless_omega", dimensionless_omega)
    _validate_nonnegative("horizon_scalar", horizon_scalar)
    exponent = ingoing_exponent(dimensionless_omega)
    return complex(
        (
            exponent
            + 2.0 * exponent**2
            + 2.0 * float(horizon_scalar) ** 2 / 3.0
        )
        / (1.0 + 2.0 * exponent)
    )


def frobenius_identity_error(
    dimensionless_omega: float, horizon_scalar: float
) -> float:
    """Return the algebraic residual of the frozen first-order horizon row."""

    exponent = ingoing_exponent(dimensionless_omega)
    coefficient = horizon_frobenius_coefficient(
        dimensionless_omega, horizon_scalar
    )
    residual = (
        (1.0 + 2.0 * exponent) * coefficient
        - exponent
        - 2.0 * exponent**2
        - 2.0 * float(horizon_scalar) ** 2 / 3.0
    )
    return float(abs(residual))


def uv_current_coefficient(
    regular_source: complex,
    regular_derivative: complex,
    dimensionless_omega: float,
) -> complex:
    """Return ``A_1=a'(0)-p a(0)`` for the factored ingoing field."""

    _validate_positive("dimensionless_omega", dimensionless_omega)
    source = complex(regular_source)
    derivative = complex(regular_derivative)
    if not _is_finite_complex(source) or not _is_finite_complex(derivative):
        raise ValueError("regular UV data must be finite complex numbers")
    return derivative - ingoing_exponent(dimensionless_omega) * source


def conductivity_from_uv(
    source: complex, current: complex, dimensionless_omega: float
) -> complex:
    """Apply source Eq. (16) with the frozen time and current conventions."""

    _validate_positive("dimensionless_omega", dimensionless_omega)
    source_value = complex(source)
    current_value = complex(current)
    if not _is_finite_complex(source_value) or not _is_finite_complex(
        current_value
    ):
        raise ValueError("UV source and current must be finite complex numbers")
    if abs(source_value) == 0.0:
        raise ValueError("UV gauge-field source must be nonzero")
    return complex(-1j * current_value / (dimensionless_omega * source_value))


def coordinate_transform_identity_error(u: float, dimensionless_omega: float) -> float:
    """Check the transformed response coefficients against the ``r`` equation."""

    if not _is_finite_real(u) or not 0.0 < float(u) < 1.0:
        raise ValueError("u must be a finite value strictly between zero and one")
    _validate_positive("dimensionless_omega", dimensionless_omega)
    coordinate = float(u)
    omega = float(dimensionless_omega)
    blackening = 1.0 - coordinate**3
    blackening_prime = -3.0 * coordinate**2

    radius = 1.0 / coordinate
    radial_blackening = radius**2 - 1.0 / radius
    radial_blackening_prime = 2.0 * radius + 1.0 / radius**2
    first_from_radial = (
        2.0 / coordinate
        - radial_blackening_prime / radial_blackening / coordinate**2
    )
    first_transformed = blackening_prime / blackening
    frequency_from_radial = omega**2 / (
        radial_blackening**2 * coordinate**4
    )
    frequency_transformed = omega**2 / blackening**2
    return float(
        max(
            abs(first_from_radial - first_transformed),
            abs(frequency_from_radial - frequency_transformed),
        )
    )


@dataclass(frozen=True)
class EquationResidualLocalization:
    """Location metadata for the unchanged independent-grid residual."""

    maximum: float
    maximum_coordinate: float
    maximum_region: str
    uv_maximum: float
    bulk_maximum: float
    horizon_maximum: float
    check_degree: int
    excluded_nodes_per_endpoint: int
    uv_maximum_coordinate: float = RESIDUAL_UV_MAXIMUM_COORDINATE
    horizon_minimum_coordinate: float = RESIDUAL_HORIZON_MINIMUM_COORDINATE

    def to_dict(self) -> Dict[str, Any]:
        return {
            "maximum": self.maximum,
            "maximum_coordinate": self.maximum_coordinate,
            "maximum_region": self.maximum_region,
            "regional_maxima": {
                "uv": self.uv_maximum,
                "bulk": self.bulk_maximum,
                "horizon": self.horizon_maximum,
            },
            "check_degree": self.check_degree,
            "excluded_nodes_per_endpoint": self.excluded_nodes_per_endpoint,
            "region_boundaries": {
                "uv_maximum_coordinate": self.uv_maximum_coordinate,
                "horizon_minimum_coordinate": self.horizon_minimum_coordinate,
            },
        }


@dataclass(frozen=True)
class SpectralResponse:
    """One exact-endpoint spectral response and its numerical diagnostics."""

    degree: int
    omega_over_temperature: float
    dimensionless_omega: float
    source: complex
    current: complex
    conductivity: complex
    condition_number: float
    equation_residual: float
    residual_localization: EquationResidualLocalization
    uv_boundary_residual: float
    horizon_boundary_residual: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "degree": self.degree,
            "omega_over_temperature": self.omega_over_temperature,
            "dimensionless_omega": self.dimensionless_omega,
            "source": _complex_record(self.source),
            "current": _complex_record(self.current),
            "conductivity": _complex_record(self.conductivity),
            "condition_number": self.condition_number,
            "equation_residual": self.equation_residual,
            "residual_localization": self.residual_localization.to_dict(),
            "uv_boundary_residual": self.uv_boundary_residual,
            "horizon_boundary_residual": self.horizon_boundary_residual,
        }


@dataclass(frozen=True)
class ElementEquationResidual:
    """Independent-grid residual evidence for one spectral element."""

    maximum: float
    maximum_coordinate: float
    check_degree: int
    excluded_nodes_per_endpoint: int

    def to_dict(self) -> Dict[str, Any]:
        return {
            "maximum": self.maximum,
            "maximum_coordinate": self.maximum_coordinate,
            "check_degree": self.check_degree,
            "excluded_nodes_per_endpoint": self.excluded_nodes_per_endpoint,
        }


@dataclass(frozen=True)
class EndpointSplitSpectralResponse:
    """Two-element exact-endpoint response and its frozen W1 diagnostics."""

    uv_degree: int
    bulk_degree: int
    split_coordinate: float
    omega_over_temperature: float
    dimensionless_omega: float
    source: complex
    current: complex
    conductivity: complex
    condition_number: float
    conditioning_roundoff_budget: float
    equation_residual: float
    uv_element_residual: ElementEquationResidual
    bulk_element_residual: ElementEquationResidual
    uv_boundary_residual: float
    horizon_boundary_residual: float
    interface_field_residual: float
    interface_derivative_residual: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "degree_pair": [self.uv_degree, self.bulk_degree],
            "split_coordinate": self.split_coordinate,
            "omega_over_temperature": self.omega_over_temperature,
            "dimensionless_omega": self.dimensionless_omega,
            "source": _complex_record(self.source),
            "current": _complex_record(self.current),
            "conductivity": _complex_record(self.conductivity),
            "condition_number": self.condition_number,
            "conditioning_roundoff_budget": self.conditioning_roundoff_budget,
            "equation_residual": self.equation_residual,
            "element_residuals": {
                "uv": self.uv_element_residual.to_dict(),
                "bulk": self.bulk_element_residual.to_dict(),
            },
            "uv_boundary_residual": self.uv_boundary_residual,
            "horizon_boundary_residual": self.horizon_boundary_residual,
            "interface_field_residual": self.interface_field_residual,
            "interface_derivative_residual": self.interface_derivative_residual,
        }


@dataclass(frozen=True)
class UVSeriesTransferCoefficients:
    """Linear UV transfer data in the source and current coefficients."""

    series_order: int
    coordinate: float
    field_source: complex
    field_current: complex
    derivative_source: complex
    derivative_current: complex

    def to_dict(self) -> Dict[str, Any]:
        return {
            "series_order": self.series_order,
            "coordinate": self.coordinate,
            "field_source": _complex_record(self.field_source),
            "field_current": _complex_record(self.field_current),
            "derivative_source": _complex_record(self.derivative_source),
            "derivative_current": _complex_record(self.derivative_current),
        }


@dataclass(frozen=True)
class SeriesTransferredSpectralResponse:
    """Bulk spectral response with an analytic source-free UV transfer."""

    degree: int
    series_order: int
    transfer_coordinate: float
    omega_over_temperature: float
    dimensionless_omega: float
    source: complex
    current: complex
    conductivity: complex
    condition_number: float
    conditioning_roundoff_budget: float
    equation_residual: float
    bulk_element_residual: ElementEquationResidual
    transfer_field_residual: float
    transfer_derivative_residual: float
    horizon_boundary_residual: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "degree": self.degree,
            "series_order": self.series_order,
            "transfer_coordinate": self.transfer_coordinate,
            "omega_over_temperature": self.omega_over_temperature,
            "dimensionless_omega": self.dimensionless_omega,
            "source": _complex_record(self.source),
            "current": _complex_record(self.current),
            "conductivity": _complex_record(self.conductivity),
            "condition_number": self.condition_number,
            "conditioning_roundoff_budget": self.conditioning_roundoff_budget,
            "equation_residual": self.equation_residual,
            "bulk_element_residual": self.bulk_element_residual.to_dict(),
            "transfer_field_residual": self.transfer_field_residual,
            "transfer_derivative_residual": self.transfer_derivative_residual,
            "horizon_boundary_residual": self.horizon_boundary_residual,
        }


@dataclass(frozen=True)
class DOP853Response:
    """One independent ingoing response and UV least-squares extraction."""

    omega_over_temperature: float
    dimensionless_omega: float
    horizon_cutoff: float
    uv_fit_maximum: float
    relative_tolerance: float
    absolute_tolerance: float
    source: complex
    current: complex
    conductivity: complex
    function_evaluations: int

    def to_dict(self) -> Dict[str, Any]:
        return {
            "omega_over_temperature": self.omega_over_temperature,
            "dimensionless_omega": self.dimensionless_omega,
            "horizon_cutoff": self.horizon_cutoff,
            "uv_fit_maximum": self.uv_fit_maximum,
            "relative_tolerance": self.relative_tolerance,
            "absolute_tolerance": self.absolute_tolerance,
            "source": _complex_record(self.source),
            "current": _complex_record(self.current),
            "conductivity": _complex_record(self.conductivity),
            "function_evaluations": self.function_evaluations,
        }


@dataclass(frozen=True)
class RiccatiDOP853Response:
    """One logarithmic-derivative response and UV intercept extraction."""

    omega_over_temperature: float
    dimensionless_omega: float
    horizon_cutoff: float
    uv_fit_maximum: float
    relative_tolerance: float
    absolute_tolerance: float
    uv_log_derivative: complex
    conductivity: complex
    function_evaluations: int

    def to_dict(self) -> Dict[str, Any]:
        return {
            "omega_over_temperature": self.omega_over_temperature,
            "dimensionless_omega": self.dimensionless_omega,
            "horizon_cutoff": self.horizon_cutoff,
            "uv_fit_maximum": self.uv_fit_maximum,
            "relative_tolerance": self.relative_tolerance,
            "absolute_tolerance": self.absolute_tolerance,
            "uv_log_derivative": _complex_record(self.uv_log_derivative),
            "conductivity": _complex_record(self.conductivity),
            "function_evaluations": self.function_evaluations,
        }


@dataclass(frozen=True)
class StaticLondonResponse:
    """Zero-frequency London response from the logarithmic derivative."""

    temperature_over_tc: float
    horizon_cutoff: float
    uv_fit_maximum: float
    uv_refinement_maximum: float
    relative_tolerance: float
    absolute_tolerance: float
    uv_log_derivative: float
    refined_uv_log_derivative: float
    superfluid_density_over_tc: float
    uv_refinement_change: float
    function_evaluations: int

    def to_dict(self) -> Dict[str, Any]:
        return {
            "temperature_over_tc": self.temperature_over_tc,
            "horizon_cutoff": self.horizon_cutoff,
            "uv_fit_maximum": self.uv_fit_maximum,
            "uv_refinement_maximum": self.uv_refinement_maximum,
            "relative_tolerance": self.relative_tolerance,
            "absolute_tolerance": self.absolute_tolerance,
            "uv_log_derivative": self.uv_log_derivative,
            "refined_uv_log_derivative": (
                self.refined_uv_log_derivative
            ),
            "superfluid_density_over_tc": (
                self.superfluid_density_over_tc
            ),
            "uv_refinement_change": self.uv_refinement_change,
            "function_evaluations": self.function_evaluations,
        }


@dataclass(frozen=True)
class SpectralResolutionAudit:
    """One additional spectral degree in the near-critical ladder."""

    degree: int
    conductivity: complex
    equation_residual: float
    transfer_field_residual: float
    transfer_derivative_residual: float
    horizon_boundary_residual: float
    conditioning_roundoff_budget: float
    change_from_primary: float
    equation_tolerance: float
    boundary_tolerance: float

    @property
    def numerical_gate_ratio(self) -> float:
        return max(
            self.equation_residual / self.equation_tolerance,
            self.transfer_field_residual / self.boundary_tolerance,
            self.transfer_derivative_residual / self.boundary_tolerance,
            self.horizon_boundary_residual / self.boundary_tolerance,
            self.conditioning_roundoff_budget
            / UV_TRANSFER_CONDITIONING_BUDGET,
            self.change_from_primary / RESPONSE_RESOLUTION_TOLERANCE,
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "degree": self.degree,
            "conductivity": _complex_record(self.conductivity),
            "equation_residual": self.equation_residual,
            "transfer_field_residual": self.transfer_field_residual,
            "transfer_derivative_residual": (
                self.transfer_derivative_residual
            ),
            "horizon_boundary_residual": self.horizon_boundary_residual,
            "conditioning_roundoff_budget": (
                self.conditioning_roundoff_budget
            ),
            "change_from_primary": self.change_from_primary,
            "equation_tolerance": self.equation_tolerance,
            "boundary_tolerance": self.boundary_tolerance,
            "numerical_gate_ratio": self.numerical_gate_ratio,
        }


@dataclass(frozen=True)
class OpticalResponseEvidence:
    """Finite, route-comparison evidence for one positive frequency."""

    omega_over_temperature: float
    spectral_degree: int
    series_order: int
    spectral_conductivity: complex
    independent_conductivity: complex
    equation_residual: float
    equation_tolerance: float
    transfer_field_residual: float
    transfer_derivative_residual: float
    horizon_boundary_residual: float
    boundary_tolerance: float
    conditioning_roundoff_budget: float
    resolution_change: float
    series_truncation_change: float
    route_relative_difference: float
    background_cutoff_change: Optional[float] = None
    source_real_conductivity: Optional[float] = None
    resolution_audit: Optional[SpectralResolutionAudit] = None

    @property
    def source_absolute_error(self) -> Optional[float]:
        if self.source_real_conductivity is None:
            return None
        return abs(
            self.spectral_conductivity.real
            - float(self.source_real_conductivity)
        )

    @property
    def numerical_gate_ratio(self) -> float:
        ratios = [
            self.equation_residual / self.equation_tolerance,
            self.transfer_field_residual / self.boundary_tolerance,
            self.transfer_derivative_residual / self.boundary_tolerance,
            self.horizon_boundary_residual / self.boundary_tolerance,
            self.conditioning_roundoff_budget
            / UV_TRANSFER_CONDITIONING_BUDGET,
            self.resolution_change / RESPONSE_RESOLUTION_TOLERANCE,
            self.series_truncation_change
            / UV_TRANSFER_TRUNCATION_TOLERANCE,
        ]
        if self.resolution_audit is not None:
            ratios.append(self.resolution_audit.numerical_gate_ratio)
        return max(ratios)

    def to_dict(self) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "omega_over_temperature": self.omega_over_temperature,
            "spectral_degree": self.spectral_degree,
            "series_order": self.series_order,
            "spectral_conductivity": _complex_record(
                self.spectral_conductivity
            ),
            "independent_conductivity": _complex_record(
                self.independent_conductivity
            ),
            "equation_residual": self.equation_residual,
            "equation_tolerance": self.equation_tolerance,
            "transfer_field_residual": self.transfer_field_residual,
            "transfer_derivative_residual": (
                self.transfer_derivative_residual
            ),
            "horizon_boundary_residual": self.horizon_boundary_residual,
            "boundary_tolerance": self.boundary_tolerance,
            "conditioning_roundoff_budget": (
                self.conditioning_roundoff_budget
            ),
            "resolution_change": self.resolution_change,
            "series_truncation_change": self.series_truncation_change,
            "route_relative_difference": self.route_relative_difference,
            "numerical_gate_ratio": self.numerical_gate_ratio,
        }
        if self.background_cutoff_change is not None:
            payload["background_cutoff_change"] = (
                self.background_cutoff_change
            )
        if self.source_real_conductivity is not None:
            payload["source_real_conductivity"] = float(
                self.source_real_conductivity
            )
            payload["source_absolute_error"] = self.source_absolute_error
        if self.resolution_audit is not None:
            payload["resolution_audit"] = self.resolution_audit.to_dict()
        return payload


@dataclass(frozen=True)
class PoleTemperatureEvidence:
    """Low-frequency pole extraction at one near-critical temperature."""

    temperature_over_tc: float
    background: BackgroundState
    responses: Tuple[OpticalResponseEvidence, ...]
    pole_intercept: float
    pole_intercept_without_largest_frequency: float
    intercept_stability: float
    static_london: StaticLondonResponse
    static_pole_relative_difference: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "temperature_over_tc": self.temperature_over_tc,
            "background": self.background.to_dict(),
            "responses": [item.to_dict() for item in self.responses],
            "pole_intercept": self.pole_intercept,
            "pole_intercept_without_largest_frequency": (
                self.pole_intercept_without_largest_frequency
            ),
            "intercept_stability": self.intercept_stability,
            "static_london": self.static_london.to_dict(),
            "static_pole_relative_difference": (
                self.static_pole_relative_difference
            ),
        }


@dataclass(frozen=True)
class NearCriticalPoleEvidence:
    """Asymptotic London fit and independent finite-frequency evidence."""

    points: Tuple[PoleTemperatureEvidence, ...]
    slope: float
    nonlinear_coefficient: float
    slope_without_lowest_temperature: float
    finite_frequency_slope: float
    finite_frequency_nonlinear_coefficient: float
    literature_coefficient: float
    literature_relative_error: float
    slope_stability: float
    maximum_intercept_stability: float
    maximum_route_relative_difference: float
    maximum_static_pole_relative_difference: float
    maximum_static_uv_refinement_change: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "fit_model": (
                "n_s/T_c = C_2 delta + C_4 delta^2, "
                "delta = 1 - T/T_c"
            ),
            "primary_quantity": "zero-frequency static London response",
            "independent_quantity": "finite-frequency pole intercept",
            "points": [item.to_dict() for item in self.points],
            "slope": self.slope,
            "nonlinear_coefficient": self.nonlinear_coefficient,
            "slope_without_lowest_temperature": (
                self.slope_without_lowest_temperature
            ),
            "finite_frequency_slope": self.finite_frequency_slope,
            "finite_frequency_nonlinear_coefficient": (
                self.finite_frequency_nonlinear_coefficient
            ),
            "literature_coefficient": self.literature_coefficient,
            "literature_relative_error": self.literature_relative_error,
            "slope_stability": self.slope_stability,
            "maximum_intercept_stability": (
                self.maximum_intercept_stability
            ),
            "maximum_route_relative_difference": (
                self.maximum_route_relative_difference
            ),
            "maximum_static_pole_relative_difference": (
                self.maximum_static_pole_relative_difference
            ),
            "maximum_static_uv_refinement_change": (
                self.maximum_static_uv_refinement_change
            ),
        }


@dataclass(frozen=True)
class HistoricalNearCriticalFailureEvidence:
    """Preserved result from the superseded finite-window contract."""

    temperatures_over_tc: Tuple[float, ...] = (
        HISTORICAL_NEAR_CRITICAL_TEMPERATURES
    )
    through_origin_coefficient: float = 19.314452328382107
    literature_relative_error: float = 0.195231153
    spectral_degree: int = 320
    maximum_equation_residual: float = 1.4533022707e-6
    equation_tolerance: float = 1.0e-6
    status: str = "superseded-contract-failure"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status,
            "acceptance_role": "historical-evidence-only",
            "temperatures_over_tc": list(self.temperatures_over_tc),
            "fit_model": "n_s/T_c = C_2 (1 - T/T_c)",
            "through_origin_coefficient": self.through_origin_coefficient,
            "literature_relative_error": self.literature_relative_error,
            "spectral_degree": self.spectral_degree,
            "maximum_equation_residual": self.maximum_equation_residual,
            "equation_tolerance": self.equation_tolerance,
        }


@dataclass(frozen=True)
class Figure2ProvenanceEvidence:
    """Public-source Figure 2 evidence that is explicitly non-accepting."""

    responses: Tuple[OpticalResponseEvidence, ...]
    figure_target_condensate_over_temperature: float
    cross_panel_condensate_scale: float = FIGURE_2_CROSS_PANEL_SCALE
    status: str = FIGURE_2_STATUS

    @property
    def source_gate_passed(self) -> bool:
        return bool(
            self.responses
            and all(
                item.source_absolute_error is not None
                and item.source_absolute_error
                <= FIGURE_SOURCE_ABSOLUTE_TOLERANCE
                for item in self.responses
            )
        )

    @property
    def first_failed_frequency(self) -> Optional[float]:
        for item in self.responses:
            error = item.source_absolute_error
            if (
                error is not None
                and error > FIGURE_SOURCE_ABSOLUTE_TOLERANCE
            ):
                return item.omega_over_temperature
        return None

    @property
    def maximum_source_absolute_error(self) -> float:
        errors = [
            item.source_absolute_error
            for item in self.responses
            if item.source_absolute_error is not None
        ]
        return float(max(errors)) if errors else 0.0

    @property
    def cross_panel_mismatch_factor(self) -> float:
        return (
            self.figure_target_condensate_over_temperature
            / self.cross_panel_condensate_scale
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status,
            "acceptance_role": "provenance-only",
            "source_gate_passed": self.source_gate_passed,
            "source_absolute_tolerance": (
                FIGURE_SOURCE_ABSOLUTE_TOLERANCE
            ),
            "first_failed_frequency": self.first_failed_frequency,
            "maximum_source_absolute_error": (
                self.maximum_source_absolute_error
            ),
            "figure_target_sqrt_condensate_over_temperature": (
                self.figure_target_condensate_over_temperature
            ),
            "cross_panel_condensate_scale": (
                self.cross_panel_condensate_scale
            ),
            "cross_panel_mismatch_factor": (
                self.cross_panel_mismatch_factor
            ),
            "responses": [item.to_dict() for item in self.responses],
        }


@dataclass(frozen=True)
class OpticalVerificationResult:
    """Bounded Phase 4 evidence under the owner-approved amended gates."""

    protected_verification: Any
    conditioned_background: ConditionedBackgroundResult
    refined_conditioned_background: BackgroundState
    normal_responses: Tuple[OpticalResponseEvidence, ...]
    near_critical: NearCriticalPoleEvidence
    historical_near_critical_failure: HistoricalNearCriticalFailureEvidence
    figure_2_provenance: Figure2ProvenanceEvidence
    convention_identity_error: float
    background_gate_ratio: float
    low_temperature_condensate_scale: float

    @property
    def reported_responses(self) -> Tuple[OpticalResponseEvidence, ...]:
        near = tuple(
            response
            for point in self.near_critical.points
            for response in point.responses
        )
        return (
            self.normal_responses
            + near
            + self.figure_2_provenance.responses
        )

    @property
    def acceptance_checks(self) -> Tuple[AcceptanceCheck, ...]:
        responses = self.reported_responses
        maximum_numerical_ratio = max(
            item.numerical_gate_ratio for item in responses
        )
        maximum_route_difference = max(
            item.route_relative_difference for item in responses
        )
        normal_error = max(
            abs(item.spectral_conductivity - 1.0)
            for item in self.normal_responses
        )
        minimum_real_conductivity = min(
            item.spectral_conductivity.real for item in responses
        )
        minimum_pole_intercept = min(
            point.pole_intercept for point in self.near_critical.points
        )
        low_minimum, low_maximum = LOW_TEMPERATURE_CONDENSATE_RANGE
        return (
            AcceptanceCheck(
                identifier="protected-hhh-benchmark",
                description=(
                    "The released HHH condensate verifier passes unchanged."
                ),
                passed=bool(self.protected_verification.passed),
                criterion="all protected acceptance checks pass",
            ),
            AcceptanceCheck(
                identifier="optical-convention-identities",
                description=(
                    "The coordinate and ingoing Frobenius identities close."
                ),
                value=self.convention_identity_error,
                criterion="value <= 1e-12",
                passed=self.convention_identity_error <= 1.0e-12,
            ),
            AcceptanceCheck(
                identifier="optical-backgrounds",
                description=(
                    "Conditioned and near-critical backgrounds satisfy their "
                    "frozen residual, source, and temperature gates."
                ),
                value=self.background_gate_ratio,
                criterion="maximum normalized gate ratio <= 1",
                passed=(
                    self.conditioned_background.passed
                    and self.background_gate_ratio <= 1.0
                ),
            ),
            AcceptanceCheck(
                identifier="optical-response-numerics",
                description=(
                    "Spectral residual, boundary, conditioning, truncation, "
                    "and resolution gates pass."
                ),
                value=maximum_numerical_ratio,
                criterion="maximum normalized gate ratio <= 1",
                passed=maximum_numerical_ratio <= 1.0,
            ),
            AcceptanceCheck(
                identifier="independent-response-route",
                description=(
                    "Spectral and Riccati/DOP853 complex conductivities agree."
                ),
                value=maximum_route_difference,
                criterion=(
                    f"maximum relative difference <= {RESPONSE_ROUTE_TOLERANCE}"
                ),
                passed=(
                    maximum_route_difference <= RESPONSE_ROUTE_TOLERANCE
                ),
            ),
            AcceptanceCheck(
                identifier="exact-normal-conductivity",
                description="The normal-state conductivity is exactly one.",
                value=normal_error,
                criterion=(
                    f"maximum complex error <= {NORMAL_CONDUCTIVITY_TOLERANCE}"
                ),
                passed=normal_error <= NORMAL_CONDUCTIVITY_TOLERANCE,
            ),
            AcceptanceCheck(
                identifier="near-critical-literature-coefficient",
                description=(
                    "The asymptotic static-London coefficient agrees with "
                    "the source C_2 = 24."
                ),
                value=self.near_critical.literature_relative_error,
                criterion=(
                    "relative difference <= "
                    f"{NEAR_CRITICAL_RELATIVE_TOLERANCE}"
                ),
                passed=(
                    self.near_critical.literature_relative_error
                    <= NEAR_CRITICAL_RELATIVE_TOLERANCE
                ),
            ),
            AcceptanceCheck(
                identifier="near-critical-fit-stability",
                description=(
                    "The frozen temperature and frequency omissions leave "
                    "the asymptotic and pole fits stable."
                ),
                value=max(
                    self.near_critical.slope_stability,
                    self.near_critical.maximum_intercept_stability,
                ),
                criterion=(
                    f"slope <= {NEAR_CRITICAL_SLOPE_STABILITY_TOLERANCE} "
                    "and pole intercept <= "
                    f"{POLE_INTERCEPT_STABILITY_TOLERANCE}"
                ),
                passed=(
                    self.near_critical.slope_stability
                    <= NEAR_CRITICAL_SLOPE_STABILITY_TOLERANCE
                    and self.near_critical.maximum_intercept_stability
                    <= POLE_INTERCEPT_STABILITY_TOLERANCE
                ),
            ),
            AcceptanceCheck(
                identifier="static-london-numerics",
                description=(
                    "The zero-frequency London UV extraction is stable "
                    "under its frozen fit-window refinement."
                ),
                value=(
                    self.near_critical.maximum_static_uv_refinement_change
                ),
                criterion=(
                    "maximum relative change <= "
                    f"{RESPONSE_RESOLUTION_TOLERANCE}"
                ),
                passed=(
                    self.near_critical.maximum_static_uv_refinement_change
                    <= RESPONSE_RESOLUTION_TOLERANCE
                ),
            ),
            AcceptanceCheck(
                identifier="static-finite-frequency-agreement",
                description=(
                    "Static London densities and finite-frequency pole "
                    "intercepts agree point by point."
                ),
                value=(
                    self.near_critical.maximum_static_pole_relative_difference
                ),
                criterion=(
                    "maximum relative difference <= "
                    f"{RESPONSE_ROUTE_TOLERANCE}"
                ),
                passed=(
                    self.near_critical.maximum_static_pole_relative_difference
                    <= RESPONSE_ROUTE_TOLERANCE
                ),
            ),
            AcceptanceCheck(
                identifier="low-temperature-condensate-scale",
                description=(
                    "The inherited Figure 1 condensate scale remains on its "
                    "released low-temperature plateau."
                ),
                value=self.low_temperature_condensate_scale,
                criterion=f"{low_minimum} <= value <= {low_maximum}",
                passed=(
                    low_minimum
                    <= self.low_temperature_condensate_scale
                    <= low_maximum
                ),
            ),
            AcceptanceCheck(
                identifier="causality-passivity-sanity",
                description=(
                    "The pole sign is positive and Re sigma is nonnegative "
                    "within the frozen numerical allowance."
                ),
                value=minimum_real_conductivity,
                criterion=(
                    f"pole intercept > 0 and Re sigma >= {PASSIVITY_MINIMUM}"
                ),
                passed=(
                    minimum_pole_intercept > 0.0
                    and minimum_real_conductivity >= PASSIVITY_MINIMUM
                ),
            ),
        )

    @property
    def passed(self) -> bool:
        return all(check.passed for check in self.acceptance_checks)

    def to_dict(self) -> Dict[str, Any]:
        protected_payload = self.protected_verification.to_dict()
        record = VerificationRecord(
            definition=OPTICAL_DEFINITION,
            configuration={
                "source": SOURCE_ID,
                "quantization": "Delta = 2 with psi_- = 0",
                "temperature_targets": {
                    "low_temperature": FIGURE_TEMPERATURE_OVER_TC,
                    "near_critical": list(NEAR_CRITICAL_TEMPERATURES),
                },
                "normal_frequencies": [
                    item[0] for item in FIGURE_ANCHORS
                ],
                "near_critical_frequencies": list(
                    NEAR_CRITICAL_FREQUENCIES
                ),
                "near_critical_spectral_degrees": list(
                    NEAR_CRITICAL_SPECTRAL_DEGREES
                ),
                "static_london": {
                    "horizon_cutoff": STATIC_LONDON_HORIZON_CUTOFF,
                    "uv_fit_maximum": STATIC_LONDON_UV_FIT_MAXIMUM,
                    "uv_refinement_maximum": (
                        STATIC_LONDON_UV_REFINEMENT_MAXIMUM
                    ),
                    "relative_tolerance": (
                        STATIC_LONDON_RELATIVE_TOLERANCE
                    ),
                    "absolute_tolerance": (
                        STATIC_LONDON_ABSOLUTE_TOLERANCE
                    ),
                },
                "response_tolerances": {
                    "route_relative": RESPONSE_ROUTE_TOLERANCE,
                    "resolution_relative": RESPONSE_RESOLUTION_TOLERANCE,
                    "series_truncation_relative": (
                        UV_TRANSFER_TRUNCATION_TOLERANCE
                    ),
                    "conditioning_roundoff": (
                        UV_TRANSFER_CONDITIONING_BUDGET
                    ),
                },
            },
            numerical_method={
                "finite_frequency_primary": (
                    OPTICAL_DEFINITION.solvers[0].to_dict()
                ),
                "superfluid_density_primary": (
                    OPTICAL_DEFINITION.solvers[1].to_dict()
                ),
                "finite_frequency_independent": (
                    OPTICAL_DEFINITION.solvers[2].to_dict()
                ),
                "pole_fit": (
                    "linear fit of (omega/T) Im sigma against "
                    "(omega/T)^2; primary static-London values and "
                    "independent pole intercepts are fit to "
                    "C_2 delta + C_4 delta^2"
                ),
            },
            results={
                "protected_hhh": {
                    "passed": protected_payload["passed"],
                    "acceptance_checks": protected_payload[
                        "acceptance_checks"
                    ],
                },
                "conditioned_background": (
                    self.conditioned_background.to_dict()
                ),
                "cutoff_refined_conditioned_background": (
                    self.refined_conditioned_background.to_dict()
                ),
                "normal_responses": [
                    item.to_dict() for item in self.normal_responses
                ],
                "near_critical_pole": self.near_critical.to_dict(),
                "historical_near_critical_failure": (
                    self.historical_near_critical_failure.to_dict()
                ),
                "low_temperature_condensate_scale": (
                    self.low_temperature_condensate_scale
                ),
                "figure_2_provenance": (
                    self.figure_2_provenance.to_dict()
                ),
            },
            acceptance_checks=self.acceptance_checks,
            software_versions=runtime_versions(),
            scope=(
                "Probe-limit dimension-two HHH exact normal response, "
                "near-critical pole test, and independently checked model "
                "conductivity. Figure 2 is not reproduced; this is not "
                "empirical validation or a controlled zero-temperature result."
            ),
            extra={
                "source_provenance": {
                    "pdf_sha256": SOURCE_PDF_SHA256,
                    "archive_sha256": SOURCE_ARCHIVE_SHA256,
                    "figure_2_right_eps_sha256": SOURCE_FIGURE_EPS_SHA256,
                    "figure_2_rescaled_eps_sha256": (
                        SOURCE_RESCALED_FIGURE_EPS_SHA256
                    ),
                },
                "material_ai_involvement": True,
                "contract_review": {
                    "review_state": "approved",
                    "reviewed_by": "Xin-Yi Liu",
                    "reviewed_on": "2026-08-21",
                },
                "result_review_state": "approved",
                "result_reviewed_by": "Xin-Yi Liu",
                "result_reviewed_on": "2026-08-21",
            },
        )
        return record.to_dict()


def zero_scalar_profile(coordinate: NDArray[np.float64]) -> NDArray[np.float64]:
    """Return the normal-state scalar profile."""

    values = np.asarray(coordinate, dtype=float)
    return np.zeros_like(values)


def leading_uv_scalar_field_correction(
    scalar_response: float, uv_fit_maximum: float
) -> float:
    """Return the source-free ``psi_+^2 u^4 / 6`` field correction.

    This prospective scale justifies the Phase 4 V1 extraction windows.  It is
    a field-series diagnostic, not a bound on all omitted UV terms.
    """

    if not _is_finite_real(scalar_response):
        raise ValueError("scalar_response must be a finite real number")
    _validate_positive("uv_fit_maximum", uv_fit_maximum)
    return float(
        float(scalar_response) ** 2 * float(uv_fit_maximum) ** 4 / 6.0
    )


def uv_series_transfer_coefficients(
    dimensionless_omega: float,
    scalar_response: float,
    coordinate: float = ENDPOINT_SPLIT_COORDINATE,
    *,
    series_order: int = 4,
) -> UVSeriesTransferCoefficients:
    """Return the source/current transfer coefficients through order four."""

    _validate_positive("dimensionless_omega", dimensionless_omega)
    if not _is_finite_real(scalar_response):
        raise ValueError("scalar_response must be a finite real number")
    _validate_positive("coordinate", coordinate)
    if float(coordinate) >= 1.0:
        raise ValueError("coordinate must be smaller than one")
    if series_order not in UV_TRANSFER_SERIES_ORDERS:
        raise ValueError("series_order must be one of (4, 3)")

    frequency = float(dimensionless_omega)
    response = float(scalar_response)
    radial = float(coordinate)
    field_source = 1.0 - 0.5 * frequency**2 * radial**2
    field_current = radial - frequency**2 * radial**3 / 6.0
    derivative_source = -frequency**2 * radial
    derivative_current = 1.0 - 0.5 * frequency**2 * radial**2
    if series_order == 4:
        fourth_source = response**2 / 6.0 + frequency**4 / 24.0
        fourth_current = 0.25
        field_source += fourth_source * radial**4
        field_current += fourth_current * radial**4
        derivative_source += 4.0 * fourth_source * radial**3
        derivative_current += 4.0 * fourth_current * radial**3

    exponent = ingoing_exponent(frequency)
    inverse_phase = np.exp(-exponent * math.log1p(-radial))
    regular_field_source = inverse_phase * field_source
    regular_field_current = inverse_phase * field_current
    regular_derivative_source = inverse_phase * (
        derivative_source
        + exponent * field_source / (1.0 - radial)
    )
    regular_derivative_current = inverse_phase * (
        derivative_current
        + exponent * field_current / (1.0 - radial)
    )
    return UVSeriesTransferCoefficients(
        series_order=int(series_order),
        coordinate=radial,
        field_source=complex(regular_field_source),
        field_current=complex(regular_field_current),
        derivative_source=complex(regular_derivative_source),
        derivative_current=complex(regular_derivative_current),
    )


def solve_spectral_response(
    omega_over_temperature_value: float,
    scalar_profile: ScalarProfile = zero_scalar_profile,
    *,
    horizon_scalar: float = 0.0,
    degree: int = 160,
    compute_condition_number: bool = True,
) -> SpectralResponse:
    """Solve one optical response with exact-endpoint Chebyshev collocation."""

    frequency = dimensionless_frequency(omega_over_temperature_value)
    _validate_nonnegative("horizon_scalar", horizon_scalar)
    grid = chebyshev_lobatto_grid(degree, 0.0, 1.0)
    coordinate = grid.nodes
    first = grid.first_derivative
    second = grid.second_derivative
    scalar = np.asarray(scalar_profile(coordinate), dtype=float)
    if scalar.shape != coordinate.shape or not np.all(np.isfinite(scalar)):
        raise ValueError("scalar_profile must return one finite value per node")

    exponent = ingoing_exponent(frequency)
    operator = np.zeros((grid.size, grid.size), dtype=complex)
    interior = slice(1, -1)
    interior_coordinate = coordinate[interior]
    interior_blackening = 1.0 - interior_coordinate**3
    interior_blackening_prime = -3.0 * interior_coordinate**2
    one_minus = 1.0 - interior_coordinate
    first_coefficient = (
        interior_blackening_prime / interior_blackening
        - 2.0 * exponent / one_minus
    )
    potential = (
        exponent * (exponent - 1.0) / one_minus**2
        - exponent
        * interior_blackening_prime
        / (one_minus * interior_blackening)
        + frequency**2 / interior_blackening**2
        - 2.0
        * scalar[interior] ** 2
        / (interior_coordinate**2 * interior_blackening)
    )
    operator[interior, :] = (
        second[interior, :]
        + first_coefficient[:, np.newaxis] * first[interior, :]
    )
    diagonal_indices = np.arange(1, grid.size - 1)
    operator[diagonal_indices, diagonal_indices] += potential

    operator[0, 0] = 1.0
    horizon_coefficient = horizon_frobenius_coefficient(
        frequency, horizon_scalar
    )
    operator[-1, :] = first[-1, :]
    operator[-1, -1] += horizon_coefficient
    right_hand_side = np.zeros(grid.size, dtype=complex)
    right_hand_side[0] = 1.0

    regular = solve(operator, right_hand_side, assume_a="gen", check_finite=True)
    if abs(regular[0]) == 0.0 or not _is_finite_complex(regular[0]):
        raise RuntimeError("spectral response returned an invalid UV amplitude")
    # The response equation is homogeneous; impose the contract's a(0)=1
    # normalization exactly rather than treating the linear-solve row roundoff
    # as a physical source residual.
    regular = regular / regular[0]
    regular_derivative = first @ regular
    source = complex(regular[0])
    current = uv_current_coefficient(source, regular_derivative[0], frequency)
    conductivity = conductivity_from_uv(source, current, frequency)
    uv_residual = abs(source - 1.0)
    horizon_residual = abs(
        regular_derivative[-1] + horizon_coefficient * regular[-1]
    )
    residual_localization = _independent_equation_residual_localization(
        coordinate,
        regular,
        scalar_profile,
        frequency,
        degree,
    )
    condition_number = (
        float(np.linalg.cond(operator)) if compute_condition_number else math.nan
    )
    return SpectralResponse(
        degree=int(degree),
        omega_over_temperature=float(omega_over_temperature_value),
        dimensionless_omega=frequency,
        source=source,
        current=current,
        conductivity=conductivity,
        condition_number=condition_number,
        equation_residual=residual_localization.maximum,
        residual_localization=residual_localization,
        uv_boundary_residual=float(uv_residual),
        horizon_boundary_residual=float(horizon_residual),
    )


def solve_endpoint_split_spectral_response(
    omega_over_temperature_value: float,
    scalar_profile: ScalarProfile = zero_scalar_profile,
    *,
    horizon_scalar: float = 0.0,
    uv_degree: int = 32,
    bulk_degree: int = 512,
    split_coordinate: float = ENDPOINT_SPLIT_COORDINATE,
    compute_condition_number: bool = True,
) -> EndpointSplitSpectralResponse:
    """Solve the response on two Chebyshev elements joined at ``u_*``.

    The regular ingoing field and its first derivative are continuous at the
    fixed background endpoint-expansion transition.  Infinity-norm row
    equilibration conditions the dense solve without changing its equations.
    """

    frequency = dimensionless_frequency(omega_over_temperature_value)
    _validate_nonnegative("horizon_scalar", horizon_scalar)
    _validate_integer("uv_degree", uv_degree, minimum=8)
    _validate_integer("bulk_degree", bulk_degree, minimum=8)
    _validate_positive("split_coordinate", split_coordinate)
    split = float(split_coordinate)
    if split >= 1.0:
        raise ValueError("split_coordinate must be smaller than one")

    uv_grid = chebyshev_lobatto_grid(uv_degree, 0.0, split)
    bulk_grid = chebyshev_lobatto_grid(bulk_degree, split, 1.0)
    uv_size = uv_grid.size
    bulk_offset = uv_size
    total_size = uv_size + bulk_grid.size
    operator = np.zeros((total_size, total_size), dtype=complex)

    exponent = ingoing_exponent(frequency)

    def add_interior_rows(grid: Any, offset: int) -> None:
        coordinate = grid.nodes
        scalar = np.asarray(scalar_profile(coordinate), dtype=float)
        if scalar.shape != coordinate.shape or not np.all(np.isfinite(scalar)):
            raise ValueError("scalar_profile must return one finite value per node")
        interior_indices = np.arange(1, grid.size - 1)
        interior_coordinate = coordinate[interior_indices]
        blackening = 1.0 - interior_coordinate**3
        blackening_prime = -3.0 * interior_coordinate**2
        one_minus = 1.0 - interior_coordinate
        first_coefficient = (
            blackening_prime / blackening - 2.0 * exponent / one_minus
        )
        potential = (
            exponent * (exponent - 1.0) / one_minus**2
            - exponent * blackening_prime / (one_minus * blackening)
            + frequency**2 / blackening**2
            - 2.0
            * scalar[interior_indices] ** 2
            / (interior_coordinate**2 * blackening)
        )
        rows = offset + interior_indices
        columns = slice(offset, offset + grid.size)
        operator[rows, columns] = (
            grid.second_derivative[interior_indices, :]
            + first_coefficient[:, np.newaxis]
            * grid.first_derivative[interior_indices, :]
        )
        operator[rows, offset + interior_indices] += potential

    add_interior_rows(uv_grid, 0)
    add_interior_rows(bulk_grid, bulk_offset)

    operator[0, 0] = 1.0
    interface_field_row = uv_size - 1
    operator[interface_field_row, uv_size - 1] = 1.0
    operator[interface_field_row, bulk_offset] = -1.0
    interface_derivative_row = bulk_offset
    operator[interface_derivative_row, :uv_size] = (
        uv_grid.first_derivative[-1, :]
    )
    operator[interface_derivative_row, bulk_offset:] = (
        -bulk_grid.first_derivative[0, :]
    )
    horizon_coefficient = horizon_frobenius_coefficient(
        frequency, horizon_scalar
    )
    operator[-1, bulk_offset:] = bulk_grid.first_derivative[-1, :]
    operator[-1, -1] += horizon_coefficient

    right_hand_side = np.zeros(total_size, dtype=complex)
    right_hand_side[0] = 1.0
    row_norms = np.max(np.abs(operator), axis=1)
    if np.any(~np.isfinite(row_norms)) or np.any(row_norms == 0.0):
        raise RuntimeError("endpoint-split operator has an invalid equation row")
    equilibrated_operator = operator / row_norms[:, np.newaxis]
    equilibrated_right_hand_side = right_hand_side / row_norms
    regular = solve(
        equilibrated_operator,
        equilibrated_right_hand_side,
        assume_a="gen",
        check_finite=True,
    )
    if abs(regular[0]) == 0.0 or not _is_finite_complex(regular[0]):
        raise RuntimeError("endpoint-split response returned an invalid UV amplitude")
    regular = regular / regular[0]
    uv_regular = np.asarray(regular[:uv_size], dtype=complex)
    bulk_regular = np.asarray(regular[bulk_offset:], dtype=complex)
    uv_derivative = uv_grid.first_derivative @ uv_regular
    bulk_derivative = bulk_grid.first_derivative @ bulk_regular
    source = complex(uv_regular[0])
    current = uv_current_coefficient(source, uv_derivative[0], frequency)
    conductivity = conductivity_from_uv(source, current, frequency)

    interface_field_scale = (
        1.0 + abs(uv_regular[-1]) + abs(bulk_regular[0])
    )
    interface_derivative_scale = (
        1.0 + abs(uv_derivative[-1]) + abs(bulk_derivative[0])
    )
    interface_field_residual = (
        abs(uv_regular[-1] - bulk_regular[0]) / interface_field_scale
    )
    interface_derivative_residual = (
        abs(uv_derivative[-1] - bulk_derivative[0])
        / interface_derivative_scale
    )
    uv_residual = _independent_element_equation_residual(
        uv_grid.nodes,
        uv_regular,
        scalar_profile,
        frequency,
        uv_degree,
        0.0,
        split,
    )
    bulk_residual = _independent_element_equation_residual(
        bulk_grid.nodes,
        bulk_regular,
        scalar_profile,
        frequency,
        bulk_degree,
        split,
        1.0,
    )
    condition_number = (
        float(np.linalg.cond(equilibrated_operator))
        if compute_condition_number
        else math.nan
    )
    conditioning_budget = float(condition_number * np.finfo(float).eps)
    return EndpointSplitSpectralResponse(
        uv_degree=int(uv_degree),
        bulk_degree=int(bulk_degree),
        split_coordinate=split,
        omega_over_temperature=float(omega_over_temperature_value),
        dimensionless_omega=frequency,
        source=source,
        current=current,
        conductivity=conductivity,
        condition_number=condition_number,
        conditioning_roundoff_budget=conditioning_budget,
        equation_residual=max(uv_residual.maximum, bulk_residual.maximum),
        uv_element_residual=uv_residual,
        bulk_element_residual=bulk_residual,
        uv_boundary_residual=float(abs(source - 1.0)),
        horizon_boundary_residual=float(
            abs(bulk_derivative[-1] + horizon_coefficient * bulk_regular[-1])
        ),
        interface_field_residual=float(interface_field_residual),
        interface_derivative_residual=float(interface_derivative_residual),
    )


def solve_series_transferred_spectral_response(
    omega_over_temperature_value: float,
    scalar_profile: ScalarProfile = zero_scalar_profile,
    *,
    scalar_response: float = 0.0,
    horizon_scalar: float = 0.0,
    degree: int = 512,
    transfer_coordinate: float = ENDPOINT_SPLIT_COORDINATE,
    series_order: int = 4,
    compute_condition_number: bool = True,
) -> SeriesTransferredSpectralResponse:
    """Solve one bulk element with an analytic source-free UV transfer."""

    frequency = dimensionless_frequency(omega_over_temperature_value)
    if not _is_finite_real(scalar_response):
        raise ValueError("scalar_response must be a finite real number")
    _validate_nonnegative("horizon_scalar", horizon_scalar)
    _validate_integer("degree", degree, minimum=8)
    transfer = uv_series_transfer_coefficients(
        frequency,
        float(scalar_response),
        transfer_coordinate,
        series_order=series_order,
    )
    coordinate = transfer.coordinate
    grid = chebyshev_lobatto_grid(degree, coordinate, 1.0)
    scalar = np.asarray(scalar_profile(grid.nodes), dtype=float)
    if scalar.shape != grid.nodes.shape or not np.all(np.isfinite(scalar)):
        raise ValueError("scalar_profile must return one finite value per node")

    exponent = ingoing_exponent(frequency)
    current_index = grid.size
    total_size = grid.size + 1
    operator = np.zeros((total_size, total_size), dtype=complex)
    interior_indices = np.arange(1, grid.size - 1)
    interior_coordinate = grid.nodes[interior_indices]
    blackening = 1.0 - interior_coordinate**3
    blackening_prime = -3.0 * interior_coordinate**2
    one_minus = 1.0 - interior_coordinate
    first_coefficient = (
        blackening_prime / blackening - 2.0 * exponent / one_minus
    )
    potential = (
        exponent * (exponent - 1.0) / one_minus**2
        - exponent * blackening_prime / (one_minus * blackening)
        + frequency**2 / blackening**2
        - 2.0
        * scalar[interior_indices] ** 2
        / (interior_coordinate**2 * blackening)
    )
    operator[interior_indices, : grid.size] = (
        grid.second_derivative[interior_indices, :]
        + first_coefficient[:, np.newaxis]
        * grid.first_derivative[interior_indices, :]
    )
    operator[interior_indices, interior_indices] += potential

    operator[0, 0] = 1.0
    operator[0, current_index] = -transfer.field_current
    horizon_coefficient = horizon_frobenius_coefficient(
        frequency, horizon_scalar
    )
    horizon_row = grid.size - 1
    operator[horizon_row, : grid.size] = grid.first_derivative[-1, :]
    operator[horizon_row, horizon_row] += horizon_coefficient
    derivative_row = total_size - 1
    operator[derivative_row, : grid.size] = grid.first_derivative[0, :]
    operator[derivative_row, current_index] = (
        -transfer.derivative_current
    )

    right_hand_side = np.zeros(total_size, dtype=complex)
    right_hand_side[0] = transfer.field_source
    right_hand_side[derivative_row] = transfer.derivative_source
    row_norms = np.max(np.abs(operator), axis=1)
    if np.any(~np.isfinite(row_norms)) or np.any(row_norms == 0.0):
        raise RuntimeError("series-transferred operator has an invalid equation row")
    equilibrated_operator = operator / row_norms[:, np.newaxis]
    equilibrated_right_hand_side = right_hand_side / row_norms
    solution = solve(
        equilibrated_operator,
        equilibrated_right_hand_side,
        assume_a="gen",
        check_finite=True,
    )
    regular = np.asarray(solution[: grid.size], dtype=complex)
    current = complex(solution[current_index])
    if not np.all(np.isfinite(regular)) or not _is_finite_complex(current):
        raise RuntimeError("series-transferred response returned non-finite data")
    source = complex(1.0)
    conductivity = conductivity_from_uv(source, current, frequency)
    regular_derivative = grid.first_derivative @ regular
    expected_field = transfer.field_source + transfer.field_current * current
    expected_derivative = (
        transfer.derivative_source + transfer.derivative_current * current
    )
    transfer_field_residual = abs(regular[0] - expected_field) / (
        1.0 + abs(regular[0]) + abs(expected_field)
    )
    transfer_derivative_residual = (
        abs(regular_derivative[0] - expected_derivative)
        / (1.0 + abs(regular_derivative[0]) + abs(expected_derivative))
    )
    horizon_residual = abs(
        regular_derivative[-1] + horizon_coefficient * regular[-1]
    )
    equation_residual = _independent_element_equation_residual(
        grid.nodes,
        regular,
        scalar_profile,
        frequency,
        degree,
        coordinate,
        1.0,
    )
    condition_number = (
        float(np.linalg.cond(equilibrated_operator))
        if compute_condition_number
        else math.nan
    )
    conditioning_budget = float(condition_number * np.finfo(float).eps)
    return SeriesTransferredSpectralResponse(
        degree=int(degree),
        series_order=int(series_order),
        transfer_coordinate=coordinate,
        omega_over_temperature=float(omega_over_temperature_value),
        dimensionless_omega=frequency,
        source=source,
        current=current,
        conductivity=conductivity,
        condition_number=condition_number,
        conditioning_roundoff_budget=conditioning_budget,
        equation_residual=equation_residual.maximum,
        bulk_element_residual=equation_residual,
        transfer_field_residual=float(transfer_field_residual),
        transfer_derivative_residual=float(transfer_derivative_residual),
        horizon_boundary_residual=float(horizon_residual),
    )


def solve_dop853_response(
    omega_over_temperature_value: float,
    scalar_profile: ScalarProfile = zero_scalar_profile,
    *,
    horizon_scalar: float = 0.0,
    horizon_cutoff: float = 1.0e-6,
    uv_fit_maximum: float = 5.0e-3,
    relative_tolerance: float = 1.0e-10,
    absolute_tolerance: float = 1.0e-12,
) -> DOP853Response:
    """Integrate the unfactored response and fit ``A_0+A_1 u+A_2 u^2``."""

    frequency = dimensionless_frequency(omega_over_temperature_value)
    _validate_nonnegative("horizon_scalar", horizon_scalar)
    _validate_positive("horizon_cutoff", horizon_cutoff)
    _validate_positive("uv_fit_maximum", uv_fit_maximum)
    _validate_positive("relative_tolerance", relative_tolerance)
    _validate_positive("absolute_tolerance", absolute_tolerance)
    if float(horizon_cutoff) >= 1.0e-3:
        raise ValueError("horizon_cutoff must be smaller than 0.001")
    uv_minimum = 1.0e-6
    if not uv_minimum < float(uv_fit_maximum) <= 5.0e-3:
        raise ValueError("uv_fit_maximum must lie in (1e-6, 5e-3]")

    exponent = ingoing_exponent(frequency)
    coefficient = horizon_frobenius_coefficient(
        frequency, horizon_scalar
    )
    distance = float(horizon_cutoff)
    phase = np.exp(exponent * math.log(distance))
    field = phase * (1.0 + coefficient * distance)
    field_derivative = -phase / distance * (
        exponent * (1.0 + coefficient * distance)
        + coefficient * distance
    )

    def equations(
        coordinate: float, values: NDArray[np.complex128]
    ) -> NDArray[np.complex128]:
        blackening = 1.0 - coordinate**3
        blackening_prime = -3.0 * coordinate**2
        scalar_values = np.asarray(
            scalar_profile(np.asarray((coordinate,), dtype=float)), dtype=float
        )
        if scalar_values.shape != (1,) or not np.all(np.isfinite(scalar_values)):
            raise ValueError("scalar_profile must return one finite value per node")
        potential = (
            frequency**2 / blackening**2
            - 2.0 * scalar_values[0] ** 2 / (coordinate**2 * blackening)
        )
        return np.asarray(
            (
                values[1],
                -blackening_prime / blackening * values[1]
                - potential * values[0],
            ),
            dtype=complex,
        )

    integration = solve_ivp(
        equations,
        (1.0 - distance, uv_minimum),
        np.asarray((field, field_derivative), dtype=complex),
        method="DOP853",
        rtol=float(relative_tolerance),
        atol=float(absolute_tolerance),
        dense_output=True,
    )
    if not integration.success or integration.sol is None:
        raise RuntimeError(f"DOP853 response failed: {integration.message}")
    fit_coordinate = np.linspace(uv_minimum, float(uv_fit_maximum), 80)
    fit_field = np.asarray(integration.sol(fit_coordinate)[0], dtype=complex)
    design = np.column_stack(
        (
            np.ones_like(fit_coordinate),
            fit_coordinate,
            fit_coordinate**2,
        )
    )
    coefficients, _, _, _ = np.linalg.lstsq(design, fit_field, rcond=None)
    source = complex(coefficients[0])
    current = complex(coefficients[1])
    conductivity = conductivity_from_uv(source, current, frequency)
    return DOP853Response(
        omega_over_temperature=float(omega_over_temperature_value),
        dimensionless_omega=frequency,
        horizon_cutoff=distance,
        uv_fit_maximum=float(uv_fit_maximum),
        relative_tolerance=float(relative_tolerance),
        absolute_tolerance=float(absolute_tolerance),
        source=source,
        current=current,
        conductivity=conductivity,
        function_evaluations=int(integration.nfev),
    )


def horizon_log_derivative(
    dimensionless_omega: float,
    horizon_scalar: float,
    horizon_cutoff: float,
) -> complex:
    """Return ``A_x'/A_x`` from the frozen first-order ingoing series."""

    _validate_positive("dimensionless_omega", dimensionless_omega)
    _validate_nonnegative("horizon_scalar", horizon_scalar)
    _validate_positive("horizon_cutoff", horizon_cutoff)
    distance = float(horizon_cutoff)
    exponent = ingoing_exponent(dimensionless_omega)
    coefficient = horizon_frobenius_coefficient(
        dimensionless_omega, horizon_scalar
    )
    denominator = 1.0 + coefficient * distance
    if abs(denominator) == 0.0:
        raise ValueError("ingoing horizon series has a zero first-order factor")
    return complex(-exponent / distance - coefficient / denominator)


def solve_riccati_dop853_response(
    omega_over_temperature_value: float,
    scalar_profile: ScalarProfile = zero_scalar_profile,
    *,
    horizon_scalar: float = 0.0,
    horizon_cutoff: float = 1.0e-6,
    uv_fit_maximum: float = 5.0e-3,
    relative_tolerance: float = 1.0e-10,
    absolute_tolerance: float = 1.0e-12,
) -> RiccatiDOP853Response:
    """Integrate ``Y=A_x'/A_x`` and fit its UV intercept ``A_1/A_0``."""

    frequency = dimensionless_frequency(omega_over_temperature_value)
    _validate_nonnegative("horizon_scalar", horizon_scalar)
    _validate_positive("horizon_cutoff", horizon_cutoff)
    _validate_positive("uv_fit_maximum", uv_fit_maximum)
    _validate_positive("relative_tolerance", relative_tolerance)
    _validate_positive("absolute_tolerance", absolute_tolerance)
    if float(horizon_cutoff) >= 1.0e-3:
        raise ValueError("horizon_cutoff must be smaller than 0.001")
    uv_minimum = 1.0e-6
    if not uv_minimum < float(uv_fit_maximum) <= 5.0e-3:
        raise ValueError("uv_fit_maximum must lie in (1e-6, 5e-3]")

    distance = float(horizon_cutoff)
    initial_log_derivative = horizon_log_derivative(
        frequency, horizon_scalar, distance
    )

    def equations(
        coordinate: float, values: NDArray[np.complex128]
    ) -> NDArray[np.complex128]:
        blackening = 1.0 - coordinate**3
        blackening_prime = -3.0 * coordinate**2
        scalar_values = np.asarray(
            scalar_profile(np.asarray((coordinate,), dtype=float)), dtype=float
        )
        if scalar_values.shape != (1,) or not np.all(np.isfinite(scalar_values)):
            raise ValueError("scalar_profile must return one finite value per node")
        potential = (
            frequency**2 / blackening**2
            - 2.0 * scalar_values[0] ** 2 / (coordinate**2 * blackening)
        )
        derivative = (
            -values[0] ** 2
            - blackening_prime / blackening * values[0]
            - potential
        )
        return np.asarray((derivative,), dtype=complex)

    integration = solve_ivp(
        equations,
        (1.0 - distance, uv_minimum),
        np.asarray((initial_log_derivative,), dtype=complex),
        method="DOP853",
        rtol=float(relative_tolerance),
        atol=float(absolute_tolerance),
        dense_output=True,
    )
    if not integration.success or integration.sol is None:
        raise RuntimeError(
            f"Riccati DOP853 response failed: {integration.message}"
        )
    fit_coordinate = np.linspace(uv_minimum, float(uv_fit_maximum), 80)
    fit_log_derivative = np.asarray(
        integration.sol(fit_coordinate)[0], dtype=complex
    )
    if not np.all(np.isfinite(fit_log_derivative)):
        raise RuntimeError("Riccati DOP853 response returned non-finite UV data")
    design = np.column_stack(
        (
            np.ones_like(fit_coordinate),
            fit_coordinate,
            fit_coordinate**2,
        )
    )
    coefficients, _, _, _ = np.linalg.lstsq(
        design, fit_log_derivative, rcond=None
    )
    uv_log_derivative = complex(coefficients[0])
    conductivity = conductivity_from_uv(1.0, uv_log_derivative, frequency)
    return RiccatiDOP853Response(
        omega_over_temperature=float(omega_over_temperature_value),
        dimensionless_omega=frequency,
        horizon_cutoff=distance,
        uv_fit_maximum=float(uv_fit_maximum),
        relative_tolerance=float(relative_tolerance),
        absolute_tolerance=float(absolute_tolerance),
        uv_log_derivative=uv_log_derivative,
        conductivity=conductivity,
        function_evaluations=int(integration.nfev),
    )


def solve_static_london_response(
    background: BackgroundState,
    *,
    horizon_cutoff: float = STATIC_LONDON_HORIZON_CUTOFF,
    uv_fit_maximum: float = STATIC_LONDON_UV_FIT_MAXIMUM,
    uv_refinement_maximum: float = STATIC_LONDON_UV_REFINEMENT_MAXIMUM,
    relative_tolerance: float = STATIC_LONDON_RELATIVE_TOLERANCE,
    absolute_tolerance: float = STATIC_LONDON_ABSOLUTE_TOLERANCE,
) -> StaticLondonResponse:
    """Solve the zero-frequency London equation through ``Y=A_x'/A_x``.

    The regular horizon series fixes ``Y(1-s)`` and the two frozen UV fit
    windows independently extract ``A_x'(0)/A_x(0)`` from the same dense
    DOP853 solution.
    """

    _validate_positive("horizon_cutoff", horizon_cutoff)
    _validate_positive("uv_fit_maximum", uv_fit_maximum)
    _validate_positive("uv_refinement_maximum", uv_refinement_maximum)
    _validate_positive("relative_tolerance", relative_tolerance)
    _validate_positive("absolute_tolerance", absolute_tolerance)
    if float(horizon_cutoff) >= 1.0e-3:
        raise ValueError("horizon_cutoff must be smaller than 0.001")
    uv_minimum = 1.0e-7
    if not (
        uv_minimum
        < float(uv_refinement_maximum)
        < float(uv_fit_maximum)
        <= 5.0e-3
    ):
        raise ValueError(
            "UV windows must satisfy 1e-7 < refinement < primary <= 5e-3"
        )

    distance = float(horizon_cutoff)
    horizon_coefficient = 2.0 * background.horizon_scalar**2 / 3.0
    initial_log_derivative = -horizon_coefficient / (
        1.0 + horizon_coefficient * distance
    )

    def equations(
        coordinate: float, values: NDArray[np.float64]
    ) -> NDArray[np.float64]:
        blackening = 1.0 - coordinate**3
        blackening_prime = -3.0 * coordinate**2
        scalar_values = np.asarray(
            background.scalar_profile(
                np.asarray((coordinate,), dtype=float)
            ),
            dtype=float,
        )
        if scalar_values.shape != (1,) or not np.all(np.isfinite(scalar_values)):
            raise ValueError("scalar_profile must return one finite value per node")
        derivative = (
            -values[0] ** 2
            - blackening_prime / blackening * values[0]
            + 2.0
            * scalar_values[0] ** 2
            / (coordinate**2 * blackening)
        )
        return np.asarray((derivative,), dtype=float)

    integration = solve_ivp(
        equations,
        (1.0 - distance, uv_minimum),
        np.asarray((initial_log_derivative,), dtype=float),
        method="DOP853",
        rtol=float(relative_tolerance),
        atol=float(absolute_tolerance),
        dense_output=True,
    )
    if not integration.success or integration.sol is None:
        raise RuntimeError(
            f"static London DOP853 response failed: {integration.message}"
        )

    def uv_intercept(fit_maximum: float) -> float:
        fit_coordinate = np.linspace(uv_minimum, fit_maximum, 80)
        fit_log_derivative = np.asarray(
            integration.sol(fit_coordinate)[0], dtype=float
        )
        if not np.all(np.isfinite(fit_log_derivative)):
            raise RuntimeError("static London response returned non-finite UV data")
        design = np.column_stack(
            (
                np.ones_like(fit_coordinate),
                fit_coordinate,
                fit_coordinate**2,
            )
        )
        coefficients, _, _, _ = np.linalg.lstsq(
            design, fit_log_derivative, rcond=None
        )
        return float(coefficients[0])

    uv_log_derivative = uv_intercept(float(uv_fit_maximum))
    refined_uv_log_derivative = uv_intercept(
        float(uv_refinement_maximum)
    )
    conversion = (
        4.0 * math.pi * background.temperature_over_tc / 3.0
    )
    superfluid_density = -conversion * uv_log_derivative
    refined_superfluid_density = -conversion * refined_uv_log_derivative
    if not math.isfinite(superfluid_density) or superfluid_density <= 0.0:
        raise RuntimeError("static London response is not finite and positive")
    return StaticLondonResponse(
        temperature_over_tc=background.temperature_over_tc,
        horizon_cutoff=distance,
        uv_fit_maximum=float(uv_fit_maximum),
        uv_refinement_maximum=float(uv_refinement_maximum),
        relative_tolerance=float(relative_tolerance),
        absolute_tolerance=float(absolute_tolerance),
        uv_log_derivative=uv_log_derivative,
        refined_uv_log_derivative=refined_uv_log_derivative,
        superfluid_density_over_tc=float(superfluid_density),
        uv_refinement_change=float(
            abs(refined_superfluid_density - superfluid_density)
            / max(abs(superfluid_density), 1.0e-12)
        ),
        function_evaluations=int(integration.nfev),
    )


def _independent_element_equation_residual(
    nodes: NDArray[np.float64],
    regular: NDArray[np.complex128],
    scalar_profile: ScalarProfile,
    frequency: float,
    degree: int,
    lower_bound: float,
    upper_bound: float,
) -> ElementEquationResidual:
    width = float(upper_bound - lower_bound)
    check_grid = chebyshev_lobatto_grid(
        2 * int(degree), lower_bound, upper_bound
    )
    coordinate = check_grid.nodes
    local_nodes = (np.asarray(nodes, dtype=float) - lower_bound) / width
    local_coordinate = (coordinate - lower_bound) / width
    interpolator = deterministic_barycentric_interpolator(
        local_nodes, regular
    )
    regular_check = np.asarray(interpolator(local_coordinate), dtype=complex)
    regular_first = np.asarray(
        interpolator.derivative(local_coordinate, der=1), dtype=complex
    )
    regular_second = np.asarray(
        interpolator.derivative(local_coordinate, der=2), dtype=complex
    )
    scalar = np.asarray(scalar_profile(coordinate), dtype=float)
    if scalar.shape != coordinate.shape or not np.all(np.isfinite(scalar)):
        raise ValueError("scalar_profile must return finite independent-grid values")

    selected = np.arange(3, check_grid.size - 3)
    selected_coordinate = coordinate[selected]
    one_minus = 1.0 - selected_coordinate
    exponent = ingoing_exponent(frequency)
    phase = np.exp(exponent * np.log(one_minus))
    field = phase * regular_check[selected]
    field_first = phase * (
        regular_first[selected]
        - width * exponent * regular_check[selected] / one_minus
    )
    field_second = phase * (
        regular_second[selected]
        - 2.0
        * width
        * exponent
        * regular_first[selected]
        / one_minus
        + width**2
        * exponent
        * (exponent - 1.0)
        * regular_check[selected]
        / one_minus**2
    )
    blackening = 1.0 - selected_coordinate**3
    blackening_prime = -3.0 * selected_coordinate**2
    response_potential = (
        frequency**2 / blackening**2
        - 2.0 * scalar[selected] ** 2 / (selected_coordinate**2 * blackening)
    )
    residual = (
        field_second
        + width * blackening_prime / blackening * field_first
        + width**2 * response_potential * field
    )
    scale = (
        np.abs(field_second)
        + np.abs(width * blackening_prime / blackening * field_first)
        + width**2 * np.abs(response_potential) * np.abs(field)
        + width**2
    )
    normalized = np.abs(residual) / scale
    maximum_index = int(np.argmax(normalized))
    return ElementEquationResidual(
        maximum=float(normalized[maximum_index]),
        maximum_coordinate=float(selected_coordinate[maximum_index]),
        check_degree=2 * int(degree),
        excluded_nodes_per_endpoint=3,
    )


def _independent_equation_residual_localization(
    nodes: NDArray[np.float64],
    regular: NDArray[np.complex128],
    scalar_profile: ScalarProfile,
    frequency: float,
    degree: int,
) -> EquationResidualLocalization:
    check_grid = chebyshev_lobatto_grid(2 * int(degree), 0.0, 1.0)
    coordinate = check_grid.nodes
    interpolator = deterministic_barycentric_interpolator(nodes, regular)
    regular_check = np.asarray(interpolator(coordinate), dtype=complex)
    regular_first = np.asarray(
        interpolator.derivative(coordinate, der=1), dtype=complex
    )
    regular_second = np.asarray(
        interpolator.derivative(coordinate, der=2), dtype=complex
    )
    scalar = np.asarray(scalar_profile(coordinate), dtype=float)
    if scalar.shape != coordinate.shape or not np.all(np.isfinite(scalar)):
        raise ValueError("scalar_profile must return finite independent-grid values")

    selected = np.arange(3, check_grid.size - 3)
    selected_coordinate = coordinate[selected]
    one_minus = 1.0 - selected_coordinate
    exponent = ingoing_exponent(frequency)
    phase = np.exp(exponent * np.log(one_minus))
    field = phase * regular_check[selected]
    field_first = phase * (
        regular_first[selected]
        - exponent * regular_check[selected] / one_minus
    )
    field_second = phase * (
        regular_second[selected]
        - 2.0 * exponent * regular_first[selected] / one_minus
        + exponent
        * (exponent - 1.0)
        * regular_check[selected]
        / one_minus**2
    )
    blackening = 1.0 - selected_coordinate**3
    blackening_prime = -3.0 * selected_coordinate**2
    response_potential = (
        frequency**2 / blackening**2
        - 2.0 * scalar[selected] ** 2 / (selected_coordinate**2 * blackening)
    )
    residual = (
        field_second
        + blackening_prime / blackening * field_first
        + response_potential * field
    )
    scale = (
        np.abs(field_second)
        + np.abs(blackening_prime / blackening * field_first)
        + np.abs(response_potential) * np.abs(field)
        + 1.0
    )
    normalized = np.abs(residual) / scale
    maximum_index = int(np.argmax(normalized))
    maximum_coordinate = float(selected_coordinate[maximum_index])
    uv_mask = selected_coordinate <= RESIDUAL_UV_MAXIMUM_COORDINATE
    horizon_mask = (
        selected_coordinate >= RESIDUAL_HORIZON_MINIMUM_COORDINATE
    )
    bulk_mask = ~(uv_mask | horizon_mask)
    if maximum_coordinate <= RESIDUAL_UV_MAXIMUM_COORDINATE:
        maximum_region = "uv"
    elif maximum_coordinate >= RESIDUAL_HORIZON_MINIMUM_COORDINATE:
        maximum_region = "horizon"
    else:
        maximum_region = "bulk"
    return EquationResidualLocalization(
        maximum=float(normalized[maximum_index]),
        maximum_coordinate=maximum_coordinate,
        maximum_region=maximum_region,
        uv_maximum=float(np.max(normalized[uv_mask])),
        bulk_maximum=float(np.max(normalized[bulk_mask])),
        horizon_maximum=float(np.max(normalized[horizon_mask])),
        check_degree=2 * int(degree),
        excluded_nodes_per_endpoint=3,
    )


def _response_evidence(
    omega_over_temperature_value: float,
    scalar_profile: ScalarProfile,
    *,
    scalar_response: float,
    horizon_scalar: float,
    primary_degree: int,
    refinement_degree: int,
    equation_tolerance: float,
    boundary_tolerance: float,
    independent_uv_fit_maximum: float,
    source_real_conductivity: Optional[float] = None,
    cutoff_refined_background: Optional[BackgroundState] = None,
    audit_degree: Optional[int] = None,
) -> OpticalResponseEvidence:
    """Build one frozen spectral/refinement/independent evidence row."""

    primary = solve_series_transferred_spectral_response(
        omega_over_temperature_value,
        scalar_profile,
        scalar_response=scalar_response,
        horizon_scalar=horizon_scalar,
        degree=primary_degree,
        series_order=4,
    )
    resolution = solve_series_transferred_spectral_response(
        omega_over_temperature_value,
        scalar_profile,
        scalar_response=scalar_response,
        horizon_scalar=horizon_scalar,
        degree=refinement_degree,
        series_order=4,
        compute_condition_number=False,
    )
    truncated = solve_series_transferred_spectral_response(
        omega_over_temperature_value,
        scalar_profile,
        scalar_response=scalar_response,
        horizon_scalar=horizon_scalar,
        degree=primary_degree,
        series_order=3,
        compute_condition_number=False,
    )
    audit: Optional[SeriesTransferredSpectralResponse] = None
    if audit_degree is not None:
        audit = solve_series_transferred_spectral_response(
            omega_over_temperature_value,
            scalar_profile,
            scalar_response=scalar_response,
            horizon_scalar=horizon_scalar,
            degree=audit_degree,
            series_order=4,
        )
    independent = solve_riccati_dop853_response(
        omega_over_temperature_value,
        scalar_profile,
        horizon_scalar=horizon_scalar,
        uv_fit_maximum=independent_uv_fit_maximum,
    )
    response_scale = 1.0 + abs(primary.conductivity)
    route_scale = 1.0 + abs(independent.conductivity)
    background_cutoff_change: Optional[float] = None
    if cutoff_refined_background is not None:
        cutoff_response = solve_series_transferred_spectral_response(
            omega_over_temperature_value,
            cutoff_refined_background.scalar_profile,
            scalar_response=cutoff_refined_background.scalar_response,
            horizon_scalar=cutoff_refined_background.horizon_scalar,
            degree=primary_degree,
            series_order=4,
            compute_condition_number=False,
        )
        background_cutoff_change = float(
            abs(cutoff_response.conductivity - primary.conductivity)
            / response_scale
        )
    resolution_audit = None
    if audit is not None:
        resolution_audit = SpectralResolutionAudit(
            degree=audit.degree,
            conductivity=audit.conductivity,
            equation_residual=audit.equation_residual,
            transfer_field_residual=audit.transfer_field_residual,
            transfer_derivative_residual=(
                audit.transfer_derivative_residual
            ),
            horizon_boundary_residual=audit.horizon_boundary_residual,
            conditioning_roundoff_budget=(
                audit.conditioning_roundoff_budget
            ),
            change_from_primary=float(
                abs(audit.conductivity - primary.conductivity)
                / response_scale
            ),
            equation_tolerance=float(equation_tolerance),
            boundary_tolerance=float(boundary_tolerance),
        )
    return OpticalResponseEvidence(
        omega_over_temperature=float(omega_over_temperature_value),
        spectral_degree=primary.degree,
        series_order=primary.series_order,
        spectral_conductivity=primary.conductivity,
        independent_conductivity=independent.conductivity,
        equation_residual=primary.equation_residual,
        equation_tolerance=float(equation_tolerance),
        transfer_field_residual=primary.transfer_field_residual,
        transfer_derivative_residual=primary.transfer_derivative_residual,
        horizon_boundary_residual=primary.horizon_boundary_residual,
        boundary_tolerance=float(boundary_tolerance),
        conditioning_roundoff_budget=primary.conditioning_roundoff_budget,
        resolution_change=float(
            abs(primary.conductivity - resolution.conductivity)
            / response_scale
        ),
        series_truncation_change=float(
            abs(primary.conductivity - truncated.conductivity)
            / response_scale
        ),
        route_relative_difference=float(
            abs(primary.conductivity - independent.conductivity)
            / route_scale
        ),
        background_cutoff_change=background_cutoff_change,
        source_real_conductivity=source_real_conductivity,
        resolution_audit=resolution_audit,
    )


def _pole_intercept(
    responses: Sequence[OpticalResponseEvidence],
    temperature_over_tc: float,
) -> float:
    """Extrapolate ``n_s/T_c`` linearly in frequency squared."""

    frequencies = np.asarray(
        [item.omega_over_temperature for item in responses], dtype=float
    )
    pole_samples = float(temperature_over_tc) * frequencies * np.asarray(
        [item.spectral_conductivity.imag for item in responses], dtype=float
    )
    design = np.column_stack((frequencies**2, np.ones_like(frequencies)))
    coefficients, _, _, _ = np.linalg.lstsq(
        design, pole_samples, rcond=None
    )
    return float(coefficients[1])


def _near_critical_coefficients(
    temperatures: Sequence[float], values: Sequence[float]
) -> Tuple[float, float]:
    """Fit ``C_2 delta + C_4 delta^2`` with the critical intercept fixed."""

    distances = 1.0 - np.asarray(temperatures, dtype=float)
    resolved_values = np.asarray(values, dtype=float)
    design = np.column_stack((distances, distances**2))
    coefficients, _, _, _ = np.linalg.lstsq(
        design, resolved_values, rcond=None
    )
    return float(coefficients[0]), float(coefficients[1])


def _background_state_gate_ratio(
    state: BackgroundState, target_temperature_over_tc: float
) -> float:
    positivity_ratio = 0.0 if state.charge_density > 0.0 else 2.0
    return max(
        abs(state.temperature_over_tc - target_temperature_over_tc)
        / BACKGROUND_TEMPERATURE_TOLERANCE,
        abs(state.scalar_source) / BACKGROUND_SOURCE_TOLERANCE,
        state.bvp_max_rms_residual / BACKGROUND_BVP_TOLERANCE,
        positivity_ratio,
    )


def _conditioned_background_gate_ratio(
    result: ConditionedBackgroundResult,
) -> float:
    overlap = result.overlap
    return max(
        _background_state_gate_ratio(
            result.target, result.target_temperature_over_tc
        ),
        overlap.mapped_equation_residual / BACKGROUND_EQUATION_TOLERANCE,
        overlap.mapped_boundary_residual / BACKGROUND_EQUATION_TOLERANCE,
        overlap.temperature_relative_error / BACKGROUND_OVERLAP_TOLERANCE,
        overlap.uv_relative_error / BACKGROUND_OVERLAP_TOLERANCE,
        overlap.horizon_relative_error / BACKGROUND_OVERLAP_TOLERANCE,
    )


def verify_holographic_superconductor_optical() -> OpticalVerificationResult:
    """Run the bounded amended optical verification without promotion."""

    from holoforge.benchmarks.holographic_superconductor import (
        verify_superconductor,
    )

    protected = verify_superconductor()
    critical_ratio = protected.onset.tc_over_sqrt_rho
    conditioned = solve_conditioned_background(
        critical_tc_over_sqrt_rho=critical_ratio
    )
    cutoff_refined = _refine_conditioned_background_cutoff(
        conditioned.target,
        radial_cutoff=5.0e-6,
        tolerance=conditioned.config.tolerance,
        max_nodes=conditioned.config.max_nodes,
    )

    normal_responses = tuple(
        _response_evidence(
            frequency,
            zero_scalar_profile,
            scalar_response=0.0,
            horizon_scalar=0.0,
            primary_degree=UV_TRANSFER_CONTROL_DEGREES[-1],
            refinement_degree=UV_TRANSFER_CONTROL_DEGREES[-2],
            equation_tolerance=UV_TRANSFER_CONTROL_EQUATION_TOLERANCE,
            boundary_tolerance=UV_TRANSFER_CONTROL_BOUNDARY_TOLERANCE,
            independent_uv_fit_maximum=5.0e-3,
        )
        for frequency, _ in FIGURE_ANCHORS
    )

    pole_points = []
    near_background_ratios = []
    for temperature in NEAR_CRITICAL_TEMPERATURES:
        background = solve_original_background_at_temperature(
            temperature, critical_tc_over_sqrt_rho=critical_ratio
        )
        near_background_ratios.append(
            _background_state_gate_ratio(background, temperature)
        )
        responses = tuple(
            _response_evidence(
                frequency,
                background.scalar_profile,
                scalar_response=background.scalar_response,
                horizon_scalar=background.horizon_scalar,
                primary_degree=NEAR_CRITICAL_SPECTRAL_DEGREES[1],
                refinement_degree=NEAR_CRITICAL_SPECTRAL_DEGREES[0],
                equation_tolerance=UV_TRANSFER_CONTROL_EQUATION_TOLERANCE,
                boundary_tolerance=UV_TRANSFER_CONTROL_BOUNDARY_TOLERANCE,
                independent_uv_fit_maximum=5.0e-3,
                audit_degree=NEAR_CRITICAL_SPECTRAL_DEGREES[2],
            )
            for frequency in NEAR_CRITICAL_FREQUENCIES
        )
        intercept = _pole_intercept(responses, temperature)
        reduced_intercept = _pole_intercept(responses[1:], temperature)
        static_london = solve_static_london_response(background)
        pole_points.append(
            PoleTemperatureEvidence(
                temperature_over_tc=float(temperature),
                background=background,
                responses=responses,
                pole_intercept=intercept,
                pole_intercept_without_largest_frequency=reduced_intercept,
                intercept_stability=(
                    abs(reduced_intercept - intercept) / abs(intercept)
                ),
                static_london=static_london,
                static_pole_relative_difference=(
                    abs(
                        static_london.superfluid_density_over_tc
                        - intercept
                    )
                    / abs(static_london.superfluid_density_over_tc)
                ),
            )
        )
    pole_points_tuple = tuple(pole_points)
    temperatures = [item.temperature_over_tc for item in pole_points_tuple]
    intercepts = [item.pole_intercept for item in pole_points_tuple]
    static_densities = [
        item.static_london.superfluid_density_over_tc
        for item in pole_points_tuple
    ]
    slope, nonlinear_coefficient = _near_critical_coefficients(
        temperatures, static_densities
    )
    reduced_slope, _ = _near_critical_coefficients(
        temperatures[1:], static_densities[1:]
    )
    finite_slope, finite_nonlinear_coefficient = (
        _near_critical_coefficients(temperatures, intercepts)
    )
    near_critical = NearCriticalPoleEvidence(
        points=pole_points_tuple,
        slope=slope,
        nonlinear_coefficient=nonlinear_coefficient,
        slope_without_lowest_temperature=reduced_slope,
        finite_frequency_slope=finite_slope,
        finite_frequency_nonlinear_coefficient=(
            finite_nonlinear_coefficient
        ),
        literature_coefficient=LITERATURE_SUPERFLUID_COEFFICIENT,
        literature_relative_error=(
            abs(slope - LITERATURE_SUPERFLUID_COEFFICIENT)
            / LITERATURE_SUPERFLUID_COEFFICIENT
        ),
        slope_stability=abs(reduced_slope - slope) / abs(slope),
        maximum_intercept_stability=max(
            item.intercept_stability for item in pole_points_tuple
        ),
        maximum_route_relative_difference=max(
            response.route_relative_difference
            for item in pole_points_tuple
            for response in item.responses
        ),
        maximum_static_pole_relative_difference=max(
            item.static_pole_relative_difference
            for item in pole_points_tuple
        ),
        maximum_static_uv_refinement_change=max(
            item.static_london.uv_refinement_change
            for item in pole_points_tuple
        ),
    )

    target = conditioned.target
    low_temperature_scale = float(
        math.sqrt(math.sqrt(2.0) * target.scalar_response)
        / (target.radius * critical_ratio)
    )
    figure_responses = tuple(
        _response_evidence(
            frequency,
            target.scalar_profile,
            scalar_response=target.scalar_response,
            horizon_scalar=target.horizon_scalar,
            primary_degree=UV_TRANSFER_TARGET_DEGREES[-1],
            refinement_degree=UV_TRANSFER_TARGET_DEGREES[-2],
            equation_tolerance=UV_TRANSFER_TARGET_EQUATION_TOLERANCE,
            boundary_tolerance=UV_TRANSFER_TARGET_BOUNDARY_TOLERANCE,
            independent_uv_fit_maximum=ASYMPTOTIC_UV_FIT_MAXIMA[0],
            source_real_conductivity=source_value,
            cutoff_refined_background=cutoff_refined,
        )
        for frequency, source_value in FIGURE_ANCHORS
    )
    figure_evidence = Figure2ProvenanceEvidence(
        responses=figure_responses,
        figure_target_condensate_over_temperature=(
            low_temperature_scale / target.temperature_over_tc
        ),
    )

    convention_error = max(
        coordinate_transform_identity_error(0.37, 2.4),
        frobenius_identity_error(dimensionless_frequency(40.0), 3.2),
    )
    background_gate_ratio = max(
        _conditioned_background_gate_ratio(conditioned),
        _background_state_gate_ratio(
            cutoff_refined, FIGURE_TEMPERATURE_OVER_TC
        ),
        max(
            float(item.background_cutoff_change)
            / RESPONSE_RESOLUTION_TOLERANCE
            for item in figure_responses
            if item.background_cutoff_change is not None
        ),
        *near_background_ratios,
    )
    return OpticalVerificationResult(
        protected_verification=protected,
        conditioned_background=conditioned,
        refined_conditioned_background=cutoff_refined,
        normal_responses=normal_responses,
        near_critical=near_critical,
        historical_near_critical_failure=(
            HistoricalNearCriticalFailureEvidence()
        ),
        figure_2_provenance=figure_evidence,
        convention_identity_error=convention_error,
        background_gate_ratio=background_gate_ratio,
        low_temperature_condensate_scale=low_temperature_scale,
    )


def save_optical_diagnostic_plot(
    result: OpticalVerificationResult, output_path: Path
) -> Path:
    """Save the original near-critical London/pole diagnostic.

    This plot displays HoloForge-computed quantities only. It is not a source
    Figure 2 reproduction and contains no source artwork or digitized curve.
    """

    try:
        from matplotlib.backends.backend_agg import FigureCanvasAgg
        from matplotlib.figure import Figure
    except ImportError as exc:
        raise RuntimeError(
            "plotting requires Matplotlib; install HoloForge with the plot extra"
        ) from exc

    destination = Path(output_path).expanduser()
    destination.parent.mkdir(parents=True, exist_ok=True)
    points = result.near_critical.points
    distances = np.asarray(
        [1.0 - point.temperature_over_tc for point in points], dtype=float
    )
    static_values = np.asarray(
        [
            point.static_london.superfluid_density_over_tc
            for point in points
        ],
        dtype=float,
    )
    pole_values = np.asarray(
        [point.pole_intercept for point in points], dtype=float
    )
    fit_distance = np.linspace(0.0, 1.05 * float(max(distances)), 200)
    fit_values = (
        result.near_critical.slope * fit_distance
        + result.near_critical.nonlinear_coefficient * fit_distance**2
    )

    figure = Figure(figsize=(6.2, 4.7), constrained_layout=True)
    FigureCanvasAgg(figure)
    axes = figure.add_subplot(1, 1, 1)
    axes.plot(
        fit_distance,
        fit_values,
        color="#195b9a",
        linewidth=2.0,
        label=r"$C_2\delta+C_4\delta^2$ fit",
    )
    axes.scatter(
        distances,
        static_values,
        color="#00796b",
        marker="o",
        s=38,
        label="static London response",
        zorder=3,
    )
    axes.scatter(
        distances,
        pole_values,
        facecolors="none",
        edgecolors="#c62828",
        marker="s",
        s=48,
        label="finite-frequency pole",
        zorder=4,
    )
    axes.set_xlabel(r"$\delta=1-T/T_c$")
    axes.set_ylabel(r"$n_s/T_c$")
    axes.set_title(r"HHH near-critical superfluid density ($\Delta=2$)")
    axes.grid(True, alpha=0.25)
    axes.legend(frameon=False, loc="upper left")
    axes.text(
        0.99,
        0.02,
        "HoloForge model diagnostic; not a source Figure 2 reproduction",
        transform=axes.transAxes,
        ha="right",
        va="bottom",
        fontsize=8,
        color="#444444",
    )
    figure.savefig(destination, dpi=180, metadata={"Software": "HoloForge"})
    return destination


def _complex_record(value: complex) -> Dict[str, float]:
    resolved = complex(value)
    return {
        "real": float(resolved.real),
        "imag": float(resolved.imag),
        "magnitude": float(abs(resolved)),
    }


def _validate_positive(name: str, value: object) -> None:
    if not _is_finite_real(value) or float(value) <= 0.0:
        raise ValueError(f"{name} must be a finite positive number")


def _validate_nonnegative(name: str, value: object) -> None:
    if not _is_finite_real(value) or float(value) < 0.0:
        raise ValueError(f"{name} must be a finite nonnegative number")


def _validate_integer(name: str, value: object, minimum: int) -> None:
    if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
        raise ValueError(f"{name} must be an integer at least {minimum}")


def _is_finite_real(value: object) -> bool:
    return (
        not isinstance(value, bool)
        and isinstance(value, (int, float, np.integer, np.floating))
        and math.isfinite(float(value))
    )


def _is_finite_complex(value: complex) -> bool:
    resolved = complex(value)
    return math.isfinite(resolved.real) and math.isfinite(resolved.imag)


__all__ = [
    "ASYMPTOTIC_UV_FIT_MAXIMA",
    "BACKGROUND_BVP_TOLERANCE",
    "BACKGROUND_EQUATION_TOLERANCE",
    "BACKGROUND_OVERLAP_TOLERANCE",
    "BACKGROUND_SOURCE_TOLERANCE",
    "BACKGROUND_TEMPERATURE_TOLERANCE",
    "BackgroundContinuationStep",
    "BackgroundOverlap",
    "BackgroundState",
    "ConditionedBackgroundConfig",
    "ConditionedBackgroundResult",
    "DOP853Response",
    "ENDPOINT_SPLIT_CONDITIONING_BUDGET",
    "ENDPOINT_SPLIT_COORDINATE",
    "ENDPOINT_SPLIT_DEGREE_PAIRS",
    "ENDPOINT_SPLIT_EQUATION_TOLERANCE",
    "ENDPOINT_SPLIT_HORIZON_TOLERANCE",
    "ENDPOINT_SPLIT_INTERFACE_TOLERANCE",
    "ENDPOINT_SPLIT_UV_TOLERANCE",
    "ElementEquationResidual",
    "EndpointSplitSpectralResponse",
    "EquationResidualLocalization",
    "FIGURE_ANCHORS",
    "FIGURE_2_CROSS_PANEL_SCALE",
    "FIGURE_2_STATUS",
    "FIGURE_SOURCE_ABSOLUTE_TOLERANCE",
    "FIGURE_TEMPERATURE_OVER_TC",
    "Figure2ProvenanceEvidence",
    "HISTORICAL_NEAR_CRITICAL_TEMPERATURES",
    "HORIZON_CUTOFFS",
    "HistoricalNearCriticalFailureEvidence",
    "LITERATURE_SUPERFLUID_COEFFICIENT",
    "LOW_TEMPERATURE_CONDENSATE_RANGE",
    "NEAR_CRITICAL_FREQUENCIES",
    "NEAR_CRITICAL_RELATIVE_TOLERANCE",
    "NEAR_CRITICAL_SPECTRAL_DEGREES",
    "NEAR_CRITICAL_SLOPE_STABILITY_TOLERANCE",
    "NEAR_CRITICAL_TEMPERATURES",
    "NORMAL_CONDUCTIVITY_TOLERANCE",
    "NearCriticalPoleEvidence",
    "OPTICAL_DEFINITION",
    "OpticalResponseEvidence",
    "OpticalVerificationResult",
    "PASSIVITY_MINIMUM",
    "POLE_INTERCEPT_STABILITY_TOLERANCE",
    "PoleTemperatureEvidence",
    "RESPONSE_RESOLUTION_TOLERANCE",
    "RESPONSE_ROUTE_TOLERANCE",
    "RESIDUAL_HORIZON_MINIMUM_COORDINATE",
    "RESIDUAL_UV_MAXIMUM_COORDINATE",
    "SOURCE_ARCHIVE_SHA256",
    "SOURCE_FIGURE_EPS_SHA256",
    "SOURCE_PDF_SHA256",
    "SOURCE_RESCALED_FIGURE_EPS_SHA256",
    "SPECTRAL_DEGREES",
    "SPECTRAL_AUDIT_DEGREES",
    "SPECTRAL_CONFIRMATION_DEGREE",
    "RiccatiDOP853Response",
    "STATIC_LONDON_ABSOLUTE_TOLERANCE",
    "STATIC_LONDON_HORIZON_CUTOFF",
    "STATIC_LONDON_RELATIVE_TOLERANCE",
    "STATIC_LONDON_UV_FIT_MAXIMUM",
    "STATIC_LONDON_UV_REFINEMENT_MAXIMUM",
    "SeriesTransferredSpectralResponse",
    "SpectralResolutionAudit",
    "SpectralResponse",
    "StaticLondonResponse",
    "UVSeriesTransferCoefficients",
    "UV_TRANSFER_BULK_DEGREES",
    "UV_TRANSFER_CONTROL_BOUNDARY_TOLERANCE",
    "UV_TRANSFER_CONTROL_DEGREES",
    "UV_TRANSFER_CONTROL_EQUATION_TOLERANCE",
    "UV_TRANSFER_CONDITIONING_BUDGET",
    "UV_TRANSFER_EQUATION_TOLERANCE",
    "UV_TRANSFER_HORIZON_TOLERANCE",
    "UV_TRANSFER_ROW_TOLERANCE",
    "UV_TRANSFER_SERIES_ORDERS",
    "UV_TRANSFER_TARGET_BOUNDARY_TOLERANCE",
    "UV_TRANSFER_TARGET_DEGREES",
    "UV_TRANSFER_TARGET_EQUATION_TOLERANCE",
    "UV_TRANSFER_TRUNCATION_TOLERANCE",
    "conductivity_from_uv",
    "coordinate_transform_identity_error",
    "dimensionless_frequency",
    "frobenius_identity_error",
    "horizon_frobenius_coefficient",
    "horizon_log_derivative",
    "leading_uv_scalar_field_correction",
    "omega_over_temperature",
    "solve_conditioned_background",
    "solve_dop853_response",
    "solve_endpoint_split_spectral_response",
    "solve_original_background_at_temperature",
    "solve_spectral_response",
    "solve_riccati_dop853_response",
    "save_optical_diagnostic_plot",
    "solve_static_london_response",
    "solve_series_transferred_spectral_response",
    "uv_current_coefficient",
    "uv_series_transfer_coefficients",
    "verify_holographic_superconductor_optical",
    "zero_scalar_profile",
]
