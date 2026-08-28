"""Minimal probe-limit holographic-superconductor benchmark.

This module reproduces the dimension-two condensate of Hartnoll, Herzog, and
Horowitz, Phys. Rev. Lett. 101, 031601 (2008), arXiv:0803.3295v1.  It uses the
dimensionless coordinate ``u = r_h / r`` with the AdS radius and horizon radius
set to one.  The AdS boundary is at ``u = 0`` and the horizon at ``u = 1``.

Two complementary numerical calculations are deliberately retained:

* a linear shooting calculation locates the normal-phase instability; and
* a nonlinear boundary-value continuation constructs the condensed branch.

Both use SciPy solvers rather than project-specific ODE or root algorithms.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
import math
from numbers import Real
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

import numpy as np
from numpy.typing import NDArray
from scipy.integrate import solve_bvp, solve_ivp
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


LITERATURE_TC_OVER_SQRT_RHO = 0.118
DEFAULT_LITERATURE_TOLERANCE = 1.0e-3
DEFAULT_SOURCE_TOLERANCE = 1.0e-8
DEFAULT_CUTOFF_TOLERANCE = 1.0e-6
DEFAULT_NEAR_CRITICAL_RELATIVE_TOLERANCE = 5.0e-2
DEFAULT_LOW_TEMPERATURE_RANGE = (8.2, 8.7)


SUPERCONDUCTOR_DEFINITION = BenchmarkDefinition(
    identifier="holographic-superconductor",
    support_level="reproduced",
    background=BackgroundSpec(
        identifier="planar-ads4-schwarzschild-probe-limit",
        dimension=4,
        coordinate="u = r_h/r in [0, 1]",
        description=(
            "Planar AdS_4-Schwarzschild black brane with f(u) = 1 - u^3, "
            "L = r_h = 1, and a non-backreacting Abelian-Higgs sector."
        ),
    ),
    equations=(
        EquationSpec(
            identifier="charged-scalar",
            kind="linear onset and nonlinear background equation",
            dependent_fields=("psi", "phi"),
            expression=(
                "psi'' + (f'/f - 2/u) psi' + "
                "[phi^2/f^2 + 2/(u^2 f)] psi = 0"
            ),
            source_reference="Hartnoll et al., arXiv:0803.3295v1, Eq. (6)",
        ),
        EquationSpec(
            identifier="electric-potential",
            kind="nonlinear background equation",
            dependent_fields=("phi", "psi"),
            expression="phi'' - 2 psi^2 phi/(u^2 f) = 0",
            source_reference="Hartnoll et al., arXiv:0803.3295v1, Eq. (7)",
        ),
    ),
    boundary_conditions=(
        BoundaryConditionSpec(
            field="phi",
            location="u = 0 (UV boundary)",
            role="nonzero gauge-field source",
            expression="phi = mu - rho u + ... with mu != 0",
            interpretation=(
                "The chemical potential is the boundary source. It is fixed in "
                "the grand-canonical onset calculation and remains nonzero in "
                "the fixed-density presentation of the condensate curve."
            ),
        ),
        BoundaryConditionSpec(
            field="psi",
            location="u = 0 (UV boundary)",
            role="vanishing scalar source in Delta = 2 quantization",
            expression="psi = psi_- u + psi_+ u^2 + ... with psi_- = 0",
            interpretation=(
                "Only the scalar source is set to zero; psi_+ determines the "
                "spontaneous dimension-two condensate."
            ),
        ),
        BoundaryConditionSpec(
            field="phi",
            location="u = 1 (horizon)",
            role="horizon regularity",
            expression="phi(1) = 0",
            interpretation="The one-form phi dt has finite norm at the horizon.",
        ),
        BoundaryConditionSpec(
            field="psi",
            location="u = 1 (horizon)",
            role="horizon regularity",
            expression="psi'(1) = 2 psi(1)/3",
            interpretation="Regular branch of the scalar equation for m^2 L^2 = -2.",
        ),
    ),
    solvers=(
        SolverSpec(
            problem_type="linear onset shooting problem",
            library_function="scipy.integrate.solve_ivp + scipy.optimize.root_scalar",
            method="DOP853 integration with Brent root bracketing",
            description="The UV scalar-source coefficient is the shooting residual.",
        ),
        SolverSpec(
            problem_type="coupled nonlinear boundary-value problem",
            library_function="scipy.integrate.solve_bvp",
            method="fourth-order collocation with adaptive mesh refinement",
            description="Continuation is controlled by the horizon scalar value.",
        ),
    ),
    observables=(
        ObservableSpec(
            identifier="critical-temperature",
            symbol="T_c/sqrt(rho)",
            extraction="Normal-phase instability eigenvalue and scaling symmetry.",
            normalization="T = 3 r_h/(4 pi), with rho read from phi = mu - rho u.",
        ),
        ObservableSpec(
            identifier="dimension-two-condensate",
            symbol="sqrt(<O_2>)/T_c",
            extraction=(
                "<O_2> = sqrt(2) psi_+ from the vanishing-scalar-source "
                "UV expansion."
            ),
            normalization="Fixed-density presentation used in Figure 1 (right).",
        ),
    ),
)


@dataclass(frozen=True)
class OnsetConfig:
    """Numerical controls for the linear instability calculation."""

    radial_cutoff: float = 1.0e-5
    relative_tolerance: float = 1.0e-10
    absolute_tolerance: float = 1.0e-12
    root_bracket: Tuple[float, float] = (3.0, 5.0)
    root_tolerance: float = 1.0e-11

    def __post_init__(self) -> None:
        _validate_cutoff(self.radial_cutoff)
        _validate_positive("relative_tolerance", self.relative_tolerance)
        _validate_positive("absolute_tolerance", self.absolute_tolerance)
        _validate_positive("root_tolerance", self.root_tolerance)
        if len(self.root_bracket) != 2:
            raise ValueError("root_bracket must contain exactly two values")
        lower, upper = self.root_bracket
        if not _is_finite_real(lower) or not _is_finite_real(upper):
            raise ValueError("root_bracket values must be finite")
        if float(lower) <= 0.0 or float(lower) >= float(upper):
            raise ValueError("root_bracket must satisfy 0 < lower < upper")


@dataclass(frozen=True)
class OnsetResult:
    """Critical normal-phase eigenvalue and derived temperature ratios."""

    config: OnsetConfig
    critical_mu_over_horizon: float
    tc_over_mu: float
    tc_over_sqrt_rho: float
    scalar_source_residual: float
    root_iterations: int
    function_calls: int

    def to_dict(self) -> Dict[str, Any]:
        return {
            "critical_mu_over_horizon": self.critical_mu_over_horizon,
            "tc_over_mu": self.tc_over_mu,
            "tc_over_sqrt_rho": self.tc_over_sqrt_rho,
            "scalar_source_residual": self.scalar_source_residual,
            "root_iterations": self.root_iterations,
            "function_calls": self.function_calls,
        }


@dataclass(frozen=True)
class CondensateConfig:
    """Controls for nonlinear continuation along the condensed branch."""

    radial_cutoff: float = 1.0e-5
    mesh_points: int = 500
    branch_points: int = 32
    minimum_horizon_scalar: float = 2.0e-2
    maximum_horizon_scalar: float = 20.0
    tolerance: float = 1.0e-7
    max_nodes: int = 30_000

    def __post_init__(self) -> None:
        _validate_cutoff(self.radial_cutoff)
        _validate_integer("mesh_points", self.mesh_points, minimum=20)
        _validate_integer("branch_points", self.branch_points, minimum=4)
        _validate_integer("max_nodes", self.max_nodes, minimum=self.mesh_points)
        _validate_positive("minimum_horizon_scalar", self.minimum_horizon_scalar)
        _validate_positive("maximum_horizon_scalar", self.maximum_horizon_scalar)
        if self.minimum_horizon_scalar >= self.maximum_horizon_scalar:
            raise ValueError(
                "minimum_horizon_scalar must be smaller than maximum_horizon_scalar"
            )
        _validate_positive("tolerance", self.tolerance)


@dataclass(frozen=True)
class CondensatePoint:
    """One nonlinear solution, expressed in invariant observables."""

    horizon_scalar: float
    chemical_potential: float
    charge_density: float
    temperature_over_tc: float
    sqrt_condensate_over_tc: float
    scalar_source_residual: float
    bvp_max_rms_residual: float
    mesh_nodes: int

    def to_dict(self) -> Dict[str, Any]:
        return {
            "horizon_scalar": self.horizon_scalar,
            "chemical_potential": self.chemical_potential,
            "charge_density": self.charge_density,
            "temperature_over_tc": self.temperature_over_tc,
            "sqrt_condensate_over_tc": self.sqrt_condensate_over_tc,
            "scalar_source_residual": self.scalar_source_residual,
            "bvp_max_rms_residual": self.bvp_max_rms_residual,
            "mesh_nodes": self.mesh_nodes,
        }


@dataclass(frozen=True)
class CondensateBranchResult:
    """Nonlinear dimension-two condensate branch."""

    config: CondensateConfig
    points: Tuple[CondensatePoint, ...]

    @property
    def maximum_scalar_source_residual(self) -> float:
        return max(abs(point.scalar_source_residual) for point in self.points)

    @property
    def maximum_bvp_residual(self) -> float:
        return max(point.bvp_max_rms_residual for point in self.points)

    @property
    def near_critical_amplitude(self) -> float:
        """Estimate the coefficient in Eq. (12) of arXiv:0803.3295v1."""

        estimates: List[float] = []
        for point in sorted(self.points, key=lambda item: -item.temperature_over_tc):
            reduced_temperature = 1.0 - point.temperature_over_tc
            if reduced_temperature <= 0.0:
                continue
            estimates.append(
                point.sqrt_condensate_over_tc**2
                / math.sqrt(reduced_temperature)
            )
            if len(estimates) == 5:
                break
        if not estimates:
            raise RuntimeError("condensate branch has no subcritical points")
        return float(np.median(estimates))

    @property
    def lowest_temperature_point(self) -> CondensatePoint:
        return min(self.points, key=lambda item: item.temperature_over_tc)

    @property
    def is_monotonic(self) -> bool:
        ordered = sorted(self.points, key=lambda item: item.temperature_over_tc)
        condensates = np.asarray(
            [point.sqrt_condensate_over_tc for point in ordered], dtype=float
        )
        return bool(np.all(np.diff(condensates) <= 1.0e-8))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "points": [point.to_dict() for point in self.points],
            "near_critical_amplitude": self.near_critical_amplitude,
            "maximum_scalar_source_residual": (
                self.maximum_scalar_source_residual
            ),
            "maximum_bvp_residual": self.maximum_bvp_residual,
            "lowest_temperature_over_tc": (
                self.lowest_temperature_point.temperature_over_tc
            ),
            "low_temperature_sqrt_condensate_over_tc": (
                self.lowest_temperature_point.sqrt_condensate_over_tc
            ),
            "monotonic": self.is_monotonic,
        }


@dataclass(frozen=True)
class SuperconductorVerificationResult:
    """Complete v0.2 verification evidence for the benchmark."""

    onset: OnsetResult
    refined_onset: OnsetResult
    branch: CondensateBranchResult
    literature_tolerance: float = DEFAULT_LITERATURE_TOLERANCE
    source_tolerance: float = DEFAULT_SOURCE_TOLERANCE
    cutoff_tolerance: float = DEFAULT_CUTOFF_TOLERANCE

    @property
    def cutoff_difference(self) -> float:
        return abs(
            self.onset.critical_mu_over_horizon
            - self.refined_onset.critical_mu_over_horizon
        )

    @property
    def acceptance_checks(self) -> Tuple[AcceptanceCheck, ...]:
        low_point = self.branch.lowest_temperature_point
        low_minimum, low_maximum = DEFAULT_LOW_TEMPERATURE_RANGE
        near_critical_relative_error = abs(
            self.branch.near_critical_amplitude - 144.0
        ) / 144.0
        return (
            AcceptanceCheck(
                identifier="linear-scalar-source",
                description="The Delta = 2 scalar source vanishes at onset.",
                value=abs(self.onset.scalar_source_residual),
                criterion=f"value <= {self.source_tolerance:.16g}",
                passed=(
                    abs(self.onset.scalar_source_residual)
                    <= self.source_tolerance
                ),
            ),
            AcceptanceCheck(
                identifier="onset-cutoff-convergence",
                description="Halving both radial cutoffs leaves mu_c stable.",
                value=self.cutoff_difference,
                criterion=f"value <= {self.cutoff_tolerance:.16g}",
                passed=self.cutoff_difference <= self.cutoff_tolerance,
            ),
            AcceptanceCheck(
                identifier="published-critical-temperature",
                description=(
                    "T_c/sqrt(rho) agrees with the rounded value 0.118 in "
                    "arXiv:0803.3295v1."
                ),
                value=abs(
                    self.onset.tc_over_sqrt_rho
                    - LITERATURE_TC_OVER_SQRT_RHO
                ),
                criterion=f"absolute difference <= {self.literature_tolerance:.16g}",
                passed=(
                    abs(
                        self.onset.tc_over_sqrt_rho
                        - LITERATURE_TC_OVER_SQRT_RHO
                    )
                    <= self.literature_tolerance
                ),
            ),
            AcceptanceCheck(
                identifier="nonlinear-scalar-source",
                description="The scalar source vanishes along the nonlinear branch.",
                value=self.branch.maximum_scalar_source_residual,
                criterion=f"value <= {self.source_tolerance:.16g}",
                passed=(
                    self.branch.maximum_scalar_source_residual
                    <= self.source_tolerance
                ),
            ),
            AcceptanceCheck(
                identifier="nonlinear-collocation-residual",
                description=(
                    "The adaptive boundary-value mesh satisfies its declared "
                    "collocation tolerance."
                ),
                value=self.branch.maximum_bvp_residual,
                criterion=(
                    "value <= "
                    f"{1.1 * self.branch.config.tolerance:.16g}"
                ),
                passed=(
                    self.branch.maximum_bvp_residual
                    <= 1.1 * self.branch.config.tolerance
                ),
            ),
            AcceptanceCheck(
                identifier="near-critical-condensate",
                description=(
                    "The near-critical coefficient reproduces <O_2> approximately "
                    "144 T_c^2 sqrt(1 - T/T_c)."
                ),
                value=near_critical_relative_error,
                criterion=(
                    "relative difference from 144 <= "
                    f"{DEFAULT_NEAR_CRITICAL_RELATIVE_TOLERANCE:.16g}"
                ),
                passed=(
                    near_critical_relative_error
                    <= DEFAULT_NEAR_CRITICAL_RELATIVE_TOLERANCE
                ),
            ),
            AcceptanceCheck(
                identifier="low-temperature-condensate",
                description=(
                    "The dimension-two curve reaches the Figure 1 right-panel "
                    "low-temperature plateau."
                ),
                value=low_point.sqrt_condensate_over_tc,
                criterion=(
                    f"{low_minimum} <= value <= {low_maximum} and T/T_c <= 0.06"
                ),
                passed=(
                    low_minimum
                    <= low_point.sqrt_condensate_over_tc
                    <= low_maximum
                    and low_point.temperature_over_tc <= 0.06
                ),
            ),
            AcceptanceCheck(
                identifier="monotonic-condensate-branch",
                description="The condensate decreases monotonically toward T_c.",
                passed=self.branch.is_monotonic,
                criterion="monotonic in T/T_c",
            ),
        )

    @property
    def passed(self) -> bool:
        return bool(self.acceptance_checks) and all(
            check.passed for check in self.acceptance_checks
        )

    def to_dict(self) -> Dict[str, Any]:
        record = VerificationRecord(
            definition=SUPERCONDUCTOR_DEFINITION,
            configuration={
                "mass_squared_ads_units": -2.0,
                "scalar_charge": 1.0,
                "quantization": "Delta = 2 with psi_- = 0",
                "onset_ensemble": (
                    "grand canonical: nonzero boundary chemical potential"
                ),
                "curve_presentation": (
                    "fixed charge density using scale-invariant ratios"
                ),
                "onset": {
                    "radial_cutoff": self.onset.config.radial_cutoff,
                    "relative_tolerance": self.onset.config.relative_tolerance,
                    "absolute_tolerance": self.onset.config.absolute_tolerance,
                    "root_bracket": list(self.onset.config.root_bracket),
                    "root_tolerance": self.onset.config.root_tolerance,
                },
                "condensate_branch": {
                    "radial_cutoff": self.branch.config.radial_cutoff,
                    "mesh_points": self.branch.config.mesh_points,
                    "branch_points": self.branch.config.branch_points,
                    "minimum_horizon_scalar": (
                        self.branch.config.minimum_horizon_scalar
                    ),
                    "maximum_horizon_scalar": (
                        self.branch.config.maximum_horizon_scalar
                    ),
                    "tolerance": self.branch.config.tolerance,
                    "max_nodes": self.branch.config.max_nodes,
                },
            },
            numerical_method={
                "linear_onset": SUPERCONDUCTOR_DEFINITION.solvers[0].to_dict(),
                "nonlinear_branch": SUPERCONDUCTOR_DEFINITION.solvers[1].to_dict(),
                "continuation_parameter": "psi at the horizon",
                "curve_axis_x": "T/T_c",
                "curve_axis_y": "sqrt(<O_2>)/T_c",
            },
            results={
                "onset": self.onset.to_dict(),
                "cutoff_refined_onset": self.refined_onset.to_dict(),
                "onset_cutoff_difference": self.cutoff_difference,
                "condensate_branch": self.branch.to_dict(),
            },
            acceptance_checks=self.acceptance_checks,
            software_versions=runtime_versions(),
            scope=(
                "Numerical reproduction of the probe-limit model and its "
                "dimension-two condensate curve; not an empirical validation "
                "of a material, and not a backreacted low-temperature solution."
            ),
        )
        return record.to_dict()


def solve_onset(config: Optional[OnsetConfig] = None) -> OnsetResult:
    """Locate the dimension-two normal-phase instability."""

    if config is None:
        config = OnsetConfig()

    result = root_scalar(
        lambda chemical_potential: _linear_source_coefficient(
            chemical_potential, config
        ),
        bracket=config.root_bracket,
        method="brentq",
        xtol=config.root_tolerance,
        rtol=config.root_tolerance,
    )
    if not result.converged:
        raise RuntimeError("linear onset root solve did not converge")

    critical_mu = float(result.root)
    source_residual = _linear_source_coefficient(critical_mu, config)
    tc_over_mu = 3.0 / (4.0 * math.pi * critical_mu)
    tc_over_sqrt_rho = 3.0 / (4.0 * math.pi * math.sqrt(critical_mu))
    return OnsetResult(
        config=config,
        critical_mu_over_horizon=critical_mu,
        tc_over_mu=tc_over_mu,
        tc_over_sqrt_rho=tc_over_sqrt_rho,
        scalar_source_residual=source_residual,
        root_iterations=int(result.iterations),
        function_calls=int(result.function_calls),
    )


def solve_condensate_branch(
    critical_tc_over_sqrt_rho: float,
    config: Optional[CondensateConfig] = None,
) -> CondensateBranchResult:
    """Construct the nonlinear dimension-two branch by continuation."""

    _validate_positive(
        "critical_tc_over_sqrt_rho", critical_tc_over_sqrt_rho
    )
    if config is None:
        config = CondensateConfig()

    horizon_values = np.geomspace(
        config.minimum_horizon_scalar,
        config.maximum_horizon_scalar,
        config.branch_points,
    )
    prior_solution = None
    points: List[CondensatePoint] = []

    for horizon_scalar in horizon_values:
        coordinate, guess = _branch_initial_guess(
            float(horizon_scalar), config, prior_solution
        )
        solution = solve_bvp(
            _nonlinear_equations,
            lambda left, right, value=float(horizon_scalar): (
                _nonlinear_boundary_residuals(left, right, value, config)
            ),
            coordinate,
            guess,
            tol=config.tolerance,
            max_nodes=config.max_nodes,
            verbose=0,
        )
        if not solution.success:
            raise RuntimeError(
                "nonlinear branch solve failed at horizon scalar "
                f"{float(horizon_scalar):.8g}: {solution.message}"
            )
        prior_solution = solution
        points.append(
            _extract_condensate_point(
                solution,
                float(horizon_scalar),
                critical_tc_over_sqrt_rho,
                config,
            )
        )

    return CondensateBranchResult(config=config, points=tuple(points))


def verify_superconductor(
    onset_config: Optional[OnsetConfig] = None,
    condensate_config: Optional[CondensateConfig] = None,
) -> SuperconductorVerificationResult:
    """Run the complete linear and nonlinear verification path."""

    if onset_config is None:
        onset_config = OnsetConfig()
    onset = solve_onset(onset_config)
    refined_onset = solve_onset(
        replace(onset_config, radial_cutoff=onset_config.radial_cutoff / 2.0)
    )
    branch = solve_condensate_branch(
        onset.tc_over_sqrt_rho, config=condensate_config
    )
    return SuperconductorVerificationResult(
        onset=onset,
        refined_onset=refined_onset,
        branch=branch,
    )


def save_condensate_plot(
    result: SuperconductorVerificationResult,
    output_path: Path,
) -> Path:
    """Save an original reproduction of Figure 1's right-panel observable."""

    try:
        from matplotlib.backends.backend_agg import FigureCanvasAgg
        from matplotlib.figure import Figure
    except ImportError as exc:
        raise RuntimeError(
            "plotting requires Matplotlib; install HoloForge with the plot extra"
        ) from exc

    destination = Path(output_path).expanduser()
    destination.parent.mkdir(parents=True, exist_ok=True)

    ordered = sorted(
        result.branch.points, key=lambda point: point.temperature_over_tc
    )
    temperatures = [point.temperature_over_tc for point in ordered]
    condensates = [point.sqrt_condensate_over_tc for point in ordered]
    temperatures.append(1.0)
    condensates.append(0.0)

    figure = Figure(figsize=(6.0, 4.5), constrained_layout=True)
    FigureCanvasAgg(figure)
    axes = figure.add_subplot(1, 1, 1)
    axes.plot(
        temperatures,
        condensates,
        color="#195b9a",
        linewidth=2.0,
        marker="o",
        markersize=3.0,
        label="HoloForge nonlinear solution",
    )
    axes.set_xlim(0.0, 1.02)
    axes.set_ylim(0.0, 9.0)
    axes.set_xlabel(r"$T/T_c$")
    axes.set_ylabel(r"$\sqrt{\langle O_2\rangle}/T_c$")
    axes.set_title(r"Dimension-two holographic condensate ($\Delta=2$)")
    axes.grid(True, alpha=0.25)
    axes.legend(frameon=False, loc="lower left")
    axes.text(
        0.99,
        0.02,
        "Reproduction target: arXiv:0803.3295, Fig. 1 (right)",
        transform=axes.transAxes,
        ha="right",
        va="bottom",
        fontsize=8,
        color="#444444",
    )
    figure.savefig(
        destination,
        dpi=180,
        metadata={"Creator": "HoloForge"},
    )
    return destination.resolve()


def _linear_source_coefficient(
    chemical_potential: float, config: OnsetConfig
) -> float:
    cutoff = config.radial_cutoff
    start = 1.0 - cutoff
    stop = cutoff

    second_order = -(8.0 + chemical_potential**2) / 36.0
    scalar_start = (
        1.0 - (2.0 / 3.0) * cutoff + second_order * cutoff**2
    )
    derivative_start = 2.0 / 3.0 - 2.0 * second_order * cutoff

    def equations(coordinate: float, fields: NDArray[np.float64]) -> List[float]:
        scalar, derivative = fields
        blackening = 1.0 - coordinate**3
        blackening_prime = -3.0 * coordinate**2
        potential = (
            chemical_potential**2
            * (1.0 - coordinate) ** 2
            / blackening**2
            + 2.0 / (coordinate**2 * blackening)
        )
        first_derivative = blackening_prime / blackening - 2.0 / coordinate
        return [derivative, -first_derivative * derivative - potential * scalar]

    solution = solve_ivp(
        equations,
        (start, stop),
        (scalar_start, derivative_start),
        method="DOP853",
        rtol=config.relative_tolerance,
        atol=config.absolute_tolerance,
    )
    if not solution.success:
        raise RuntimeError(f"linear onset integration failed: {solution.message}")
    scalar, derivative = solution.y[:, -1]
    return float(2.0 * scalar / stop - derivative)


def _nonlinear_equations(
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


def _nonlinear_boundary_residuals(
    left: NDArray[np.float64],
    right: NDArray[np.float64],
    horizon_scalar: float,
    config: CondensateConfig,
) -> NDArray[np.float64]:
    cutoff = config.radial_cutoff
    scalar_source = 2.0 * left[0] / cutoff - left[1]
    horizon_gauge = right[2] + cutoff * right[3]
    horizon_scalar_regularity = right[1] - (2.0 / 3.0) * right[0]
    horizon_normalization = right[0] - horizon_scalar
    return np.asarray(
        (
            scalar_source,
            horizon_gauge,
            horizon_scalar_regularity,
            horizon_normalization,
        ),
        dtype=float,
    )


def _branch_initial_guess(
    horizon_scalar: float,
    config: CondensateConfig,
    prior_solution: Any,
) -> Tuple[NDArray[np.float64], NDArray[np.float64]]:
    coordinate = np.linspace(
        config.radial_cutoff,
        1.0 - config.radial_cutoff,
        config.mesh_points,
    )
    if prior_solution is not None:
        fields = np.asarray(prior_solution.sol(coordinate), dtype=float)
        scale = horizon_scalar / fields[0, -1]
        fields[0:2] *= scale
        return coordinate, fields

    scalar = (
        horizon_scalar
        * coordinate**2
        * (7.0 / 3.0 - 4.0 * coordinate / 3.0)
    )
    scalar_prime = horizon_scalar * (
        2.0 * coordinate * (7.0 / 3.0 - 4.0 * coordinate / 3.0)
        - 4.0 * coordinate**2 / 3.0
    )
    potential = 4.1 * (1.0 - coordinate)
    potential_prime = np.full_like(coordinate, -4.1)
    return coordinate, np.vstack(
        (scalar, scalar_prime, potential, potential_prime)
    )


def _extract_condensate_point(
    solution: Any,
    horizon_scalar: float,
    critical_tc_over_sqrt_rho: float,
    config: CondensateConfig,
) -> CondensatePoint:
    cutoff = config.radial_cutoff
    scalar, scalar_prime, potential, potential_prime = solution.sol(cutoff)

    scalar_source = 2.0 * scalar / cutoff - scalar_prime
    scalar_response = (scalar_prime - scalar / cutoff) / cutoff
    chemical_potential = potential - cutoff * potential_prime
    charge_density = -potential_prime
    if charge_density <= 0.0 or scalar_response <= 0.0:
        raise RuntimeError("nonlinear solution has nonphysical UV coefficients")

    temperature_over_sqrt_rho = 3.0 / (
        4.0 * math.pi * math.sqrt(charge_density)
    )
    temperature_over_tc = (
        temperature_over_sqrt_rho / critical_tc_over_sqrt_rho
    )
    condensate = math.sqrt(math.sqrt(2.0) * scalar_response)
    sqrt_condensate_over_tc = condensate / (
        critical_tc_over_sqrt_rho * math.sqrt(charge_density)
    )
    return CondensatePoint(
        horizon_scalar=horizon_scalar,
        chemical_potential=float(chemical_potential),
        charge_density=float(charge_density),
        temperature_over_tc=float(temperature_over_tc),
        sqrt_condensate_over_tc=float(sqrt_condensate_over_tc),
        scalar_source_residual=float(scalar_source),
        bvp_max_rms_residual=float(np.max(solution.rms_residuals)),
        mesh_nodes=int(solution.x.size),
    )


def _validate_cutoff(value: object) -> None:
    _validate_positive("radial_cutoff", value)
    if float(value) > 1.0e-2:
        raise ValueError("radial_cutoff must be at most 0.01")


def _validate_positive(name: str, value: object) -> None:
    if not _is_finite_real(value) or float(value) <= 0.0:
        raise ValueError(f"{name} must be a finite positive number")


def _validate_integer(name: str, value: object, minimum: int) -> None:
    if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
        raise ValueError(f"{name} must be an integer at least {minimum}")


def _is_finite_real(value: object) -> bool:
    return (
        isinstance(value, Real)
        and not isinstance(value, bool)
        and math.isfinite(float(value))
    )
