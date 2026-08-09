"""Linear-axion DC-conductivity verification benchmark.

The implementation proceeds through the source paper's decoupled
finite-frequency master fields.  It reconstructs the original fluctuation
equations, extracts the boundary current, audits the radial flux, and only then
compares the zero-frequency extrapolation with the analytic DC result.

The equations follow Andrade and Withers, JHEP 05 (2014) 101,
arXiv:1311.5157v2, specialized to four bulk dimensions and ``r0 = 1``.
SciPy performs the complex initial-value integrations, while NumPy supplies
the least-squares UV fits and the two-by-two source solve.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
import math
from numbers import Integral, Real
from typing import Any, Dict, List, Optional, Sequence, Tuple

import numpy as np
from numpy.typing import NDArray
from scipy.integrate import solve_ivp

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


DEFAULT_SOURCE_TOLERANCE = 1.0e-8
DEFAULT_CONDITION_LIMIT = 1.0e10
DEFAULT_EQUATION_TOLERANCE = 1.0e-6
DEFAULT_FLUX_TOLERANCE = 1.0e-6
DEFAULT_DC_RELATIVE_TOLERANCE = 5.0e-3
DEFAULT_IMAGINARY_INTERCEPT_TOLERANCE = 5.0e-3
DEFAULT_FREQUENCY_STABILITY_TOLERANCE = 3.0e-3
DEFAULT_HORIZON_REFINEMENT_TOLERANCE = 2.0e-3
DEFAULT_UV_REFINEMENT_TOLERANCE = 2.0e-3
DEFAULT_INTEGRATOR_REFINEMENT_TOLERANCE = 1.0e-3
DEFAULT_RADIAL_DC_TOLERANCE = 5.0e-3
DEFAULT_FREQUENCIES = (0.08, 0.05, 0.03, 0.02)
DEFAULT_RADIAL_AUDIT_LOCATIONS = (1.5, 5.0, 20.0)
DEFAULT_PARAMETER_CASES = (
    ("P1", 0.5, 1.0),
    ("P2", 1.0, 1.0),
    ("P3", 1.0, math.sqrt(2.0)),
)


LINEAR_AXION_DEFINITION = BenchmarkDefinition(
    identifier="linear-axion-dc",
    support_level="reproduced",
    background=BackgroundSpec(
        identifier="ads4-linear-axion-black-brane",
        dimension=4,
        coordinate="r in [r0, infinity), with r0 = 1 in the solve",
        description=(
            "Homogeneous charged AdS_4 black brane with two spatially "
            "linear massless-scalar sources."
        ),
    ),
    equations=(
        EquationSpec(
            identifier="master-fields",
            kind="two decoupled complex initial-value equations",
            dependent_fields=("Phi_plus", "Phi_minus"),
            expression=(
                "r^2 (f Phi_pm')' + [r^2 omega^2/f - mu^2/r^2 "
                "+ c_pm mu/r] Phi_pm = 0"
            ),
            source_reference=(
                "Andrade and Withers, arXiv:1311.5157v2, Eqs. (3.24)-(3.26)"
            ),
        ),
        EquationSpec(
            identifier="reconstructed-gauge-field",
            kind="coupled fluctuation check",
            dependent_fields=("a_x", "phi"),
            expression=(
                "(f a_x')' + omega^2 a_x/f = mu^2 a_x/r^4 "
                "+ i mu phi/r^4"
            ),
            source_reference=(
                "Andrade and Withers, arXiv:1311.5157v2, Eq. (3.8), d = 3"
            ),
        ),
        EquationSpec(
            identifier="reconstructed-scalar-combination",
            kind="coupled fluctuation check",
            dependent_fields=("a_x", "phi"),
            expression=(
                "r^2 (r^-2 f phi')' + omega^2 phi/f = "
                "-i alpha^2 mu a_x/r^2 + alpha^2 phi/r^2"
            ),
            source_reference=(
                "Andrade and Withers, arXiv:1311.5157v2, Eq. (3.9), d = 3"
            ),
        ),
    ),
    boundary_conditions=(
        BoundaryConditionSpec(
            field="Phi_plus, Phi_minus",
            location="r = r0 (future horizon)",
            role="retarded ingoing branch",
            expression="Phi_pm proportional to (r-r0)^[-i omega/f'(r0)]",
            interpretation=(
                "A Frobenius expansion initializes each independent master "
                "solution at a finite numerical horizon cutoff."
            ),
        ),
        BoundaryConditionSpec(
            field="a_x",
            location="r -> infinity",
            role="unit electric gauge-field source",
            expression="a_x = 1 + J_x/r + ...",
            interpretation=(
                "The constant gauge perturbation is fixed to one and the "
                "1/r coefficient is the current response."
            ),
        ),
        BoundaryConditionSpec(
            field="chi and H_tx",
            location="r -> infinity",
            role="zero scalar and metric fluctuation sources",
            expression="phi_growing = -(omega chi_0 - i alpha^2 H_tx^(0)) = 0",
            interpretation=(
                "The invariant obstruction vanishes, after which one residual "
                "boundary diffeomorphism sets both individual sources to zero."
            ),
        ),
    ),
    solvers=(
        SolverSpec(
            problem_type="complex master-field initial-value problem",
            library_function="scipy.integrate.solve_ivp",
            method="DOP853 with ingoing Frobenius initial data",
            description=(
                "Two independent solutions are combined by a NumPy source-map "
                "solve after overdetermined UV least-squares fits."
            ),
        ),
    ),
    observables=(
        ObservableSpec(
            identifier="complex-conductivity",
            symbol="sigma(omega)",
            extraction="J_x/[i omega a_x^(0)] from the fitted UV expansion.",
            normalization="Dimensionless in four bulk dimensions.",
        ),
        ObservableSpec(
            identifier="dc-conductivity",
            symbol="sigma_DC",
            extraction=(
                "Zero-frequency intercept of Re sigma versus omega^2, checked "
                "against radial-flux intercepts."
            ),
            normalization="Exact source-model target 1 + mu^2/alpha^2.",
        ),
    ),
)


@dataclass(frozen=True)
class LinearAxionPreflightConfig:
    """Physical inputs and numerical controls for one UV preflight."""

    chemical_potential: float = 1.0
    axion_gradient: float = 1.0
    frequency: float = 0.05
    horizon_cutoff: float = 1.0e-6
    uv_endpoint: float = 60.0
    radial_points: int = 800
    uv_fit_fraction: float = 0.2
    relative_tolerance: float = 1.0e-9
    absolute_tolerance: float = 1.0e-11

    def __post_init__(self) -> None:
        _require_positive(self.chemical_potential, "chemical_potential")
        _require_positive(self.axion_gradient, "axion_gradient")
        _require_positive(self.frequency, "frequency")
        _require_positive(self.horizon_cutoff, "horizon_cutoff")
        if self.horizon_cutoff > 1.0e-3:
            raise ValueError("horizon_cutoff must be at most 1e-3")
        _require_positive(self.uv_endpoint, "uv_endpoint")
        if self.uv_endpoint <= 2.0:
            raise ValueError("uv_endpoint must be greater than 2")
        _require_integer_at_least(self.radial_points, 30, "radial_points")
        _require_fraction(self.uv_fit_fraction, "uv_fit_fraction")
        if self.uv_fit_fraction * self.radial_points < 6:
            raise ValueError("uv_fit_fraction must retain at least six samples")
        _require_positive(self.relative_tolerance, "relative_tolerance")
        _require_positive(self.absolute_tolerance, "absolute_tolerance")
        if self.horizon_slope <= 0.0:
            raise ValueError(
                "chemical_potential and axion_gradient must give positive temperature"
            )

    @property
    def mass_parameter(self) -> float:
        """Return ``m0`` with the horizon scale fixed to one."""

        mu = float(self.chemical_potential)
        alpha = float(self.axion_gradient)
        return 1.0 + 0.25 * mu**2 - 0.5 * alpha**2

    @property
    def horizon_slope(self) -> float:
        """Return ``f'(1) = 4 pi T``."""

        mu = float(self.chemical_potential)
        alpha = float(self.axion_gradient)
        return 3.0 - 0.5 * alpha**2 - 0.25 * mu**2


@dataclass(frozen=True)
class BackgroundPreflight:
    """Analytic background checks required before fluctuation integration."""

    horizon_residual: float
    temperature_relative_error: float
    maxwell_flux_relative_variation: float
    temperature: float
    mass_parameter: float

    @property
    def passed(self) -> bool:
        return (
            self.horizon_residual <= 1.0e-12
            and self.temperature_relative_error <= 1.0e-10
            and self.maxwell_flux_relative_variation <= 1.0e-10
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "horizon_residual": self.horizon_residual,
            "temperature_relative_error": self.temperature_relative_error,
            "maxwell_flux_relative_variation": (
                self.maxwell_flux_relative_variation
            ),
            "temperature": self.temperature,
            "mass_parameter": self.mass_parameter,
            "passed": self.passed,
        }


@dataclass(frozen=True)
class SourceMapPreflightResult:
    """Numerical evidence for the two-master UV source construction."""

    config: LinearAxionPreflightConfig
    background: BackgroundPreflight
    master_constants: Tuple[float, float]
    amplitudes: Tuple[complex, complex]
    source_matrix: NDArray[np.complex128]
    condition_number: float
    gauge_source: complex
    phi_growing_coefficient: complex
    gauge_source_residual: float
    scalar_source_residual: float
    metric_source_residual: float
    master_uv_fit_residuals: Tuple[float, float]
    reconstructed_uv_fit_residuals: Tuple[float, float]
    frobenius_exponent_errors: Tuple[float, float]

    @property
    def passed(self) -> bool:
        return (
            self.background.passed
            and self.condition_number < DEFAULT_CONDITION_LIMIT
            and self.gauge_source_residual <= DEFAULT_SOURCE_TOLERANCE
            and self.scalar_source_residual <= DEFAULT_SOURCE_TOLERANCE
            and self.metric_source_residual <= DEFAULT_SOURCE_TOLERANCE
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "configuration": {
                "r0": 1.0,
                "chemical_potential": self.config.chemical_potential,
                "axion_gradient": self.config.axion_gradient,
                "frequency": self.config.frequency,
                "horizon_cutoff": self.config.horizon_cutoff,
                "uv_endpoint": self.config.uv_endpoint,
                "radial_points": self.config.radial_points,
                "uv_fit_fraction": self.config.uv_fit_fraction,
                "relative_tolerance": self.config.relative_tolerance,
                "absolute_tolerance": self.config.absolute_tolerance,
            },
            "background": self.background.to_dict(),
            "master_constants": list(self.master_constants),
            "amplitudes": [_complex_record(value) for value in self.amplitudes],
            "source_matrix": [
                [_complex_record(value) for value in row]
                for row in self.source_matrix
            ],
            "condition_number": self.condition_number,
            "gauge_source": _complex_record(self.gauge_source),
            "phi_growing_coefficient": _complex_record(
                self.phi_growing_coefficient
            ),
            "source_residuals": {
                "unit_gauge": self.gauge_source_residual,
                "gauge_invariant_scalar": self.scalar_source_residual,
                "metric_after_scalar_gauge_fixing": self.metric_source_residual,
            },
            "master_uv_fit_residuals": list(self.master_uv_fit_residuals),
            "reconstructed_uv_fit_residuals": list(
                self.reconstructed_uv_fit_residuals
            ),
            "frobenius_exponent_errors": list(
                self.frobenius_exponent_errors
            ),
            "source_map_interpretation": (
                "The growing phi coefficient is minus the gauge-invariant "
                "combination omega*chi_source - i*alpha^2*metric_source. "
                "When it vanishes, one residual boundary diffeomorphism sets "
                "both individual sources to zero."
            ),
            "passed": self.passed,
            "scope": (
                "Background and UV source-map preflight only; no conductivity "
                "observable or physical validation is claimed."
            ),
        }


@dataclass(frozen=True)
class LinearAxionFrequencyResult:
    """One finite-frequency solution and its independent residual checks."""

    preflight: SourceMapPreflightResult
    current_response: complex
    conductivity: complex
    equation_residual: float
    flux_balance_residual: float
    radial_dc_proxies: Tuple[complex, complex, complex]

    @property
    def config(self) -> LinearAxionPreflightConfig:
        return self.preflight.config

    def to_dict(self) -> Dict[str, Any]:
        return {
            "frequency": self.config.frequency,
            "conductivity": _complex_record(self.conductivity),
            "current_response": _complex_record(self.current_response),
            "equation_residual": self.equation_residual,
            "flux_balance_residual": self.flux_balance_residual,
            "radial_dc_proxies": [
                {
                    "radius": radius,
                    "value": _complex_record(value),
                }
                for radius, value in zip(
                    DEFAULT_RADIAL_AUDIT_LOCATIONS, self.radial_dc_proxies
                )
            ],
            "source_map": self.preflight.to_dict(),
        }


@dataclass(frozen=True)
class LinearAxionCaseResult:
    """Frozen frequency sequence and zero-frequency fits for one case."""

    identifier: str
    chemical_potential: float
    axion_gradient: float
    frequency_results: Tuple[LinearAxionFrequencyResult, ...]
    exact_dc_conductivity: float
    real_dc_intercept: float
    imaginary_dc_intercept: float
    stable_real_dc_intercept: float
    radial_dc_intercepts: Tuple[float, float, float]

    @property
    def dc_relative_error(self) -> float:
        return abs(self.real_dc_intercept - self.exact_dc_conductivity) / abs(
            self.exact_dc_conductivity
        )

    @property
    def frequency_fit_change(self) -> float:
        return abs(
            self.real_dc_intercept - self.stable_real_dc_intercept
        ) / abs(self.real_dc_intercept)

    @property
    def radial_dc_relative_spread(self) -> float:
        values = np.asarray(self.radial_dc_intercepts, dtype=float)
        return float(np.ptp(values) / max(abs(float(np.mean(values))), 1.0e-300))

    @property
    def maximum_equation_residual(self) -> float:
        return max(result.equation_residual for result in self.frequency_results)

    @property
    def maximum_flux_balance_residual(self) -> float:
        return max(
            result.flux_balance_residual for result in self.frequency_results
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "case": self.identifier,
            "chemical_potential": self.chemical_potential,
            "axion_gradient": self.axion_gradient,
            "temperature": self.frequency_results[0].preflight.background.temperature,
            "entropy_density": 4.0 * math.pi,
            "exact_dc_conductivity": self.exact_dc_conductivity,
            "frequency_results": [
                result.to_dict() for result in self.frequency_results
            ],
            "fits": {
                "real_basis": "intercept + slope*omega^2",
                "real_dc_intercept": self.real_dc_intercept,
                "real_dc_intercept_without_largest_frequency": (
                    self.stable_real_dc_intercept
                ),
                "imaginary_basis": "intercept + b1*omega + b3*omega^3",
                "imaginary_dc_intercept": self.imaginary_dc_intercept,
                "radial_dc_intercepts": [
                    {"radius": radius, "intercept": value}
                    for radius, value in zip(
                        DEFAULT_RADIAL_AUDIT_LOCATIONS,
                        self.radial_dc_intercepts,
                    )
                ],
            },
            "diagnostics": {
                "dc_relative_error": self.dc_relative_error,
                "frequency_fit_change": self.frequency_fit_change,
                "radial_dc_relative_spread": self.radial_dc_relative_spread,
                "maximum_equation_residual": self.maximum_equation_residual,
                "maximum_flux_balance_residual": (
                    self.maximum_flux_balance_residual
                ),
            },
        }


@dataclass(frozen=True)
class LinearAxionRefinementEvidence:
    """DC-intercept changes under the three frozen numerical refinements."""

    case_identifier: str
    horizon_cutoff_relative_change: float
    uv_endpoint_relative_change: float
    integrator_tolerance_relative_change: float
    maximum_frobenius_refinement_ratio: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "case": self.case_identifier,
            "horizon_cutoff_relative_change": (
                self.horizon_cutoff_relative_change
            ),
            "uv_endpoint_relative_change": self.uv_endpoint_relative_change,
            "integrator_tolerance_relative_change": (
                self.integrator_tolerance_relative_change
            ),
            "maximum_frobenius_refinement_ratio": (
                self.maximum_frobenius_refinement_ratio
            ),
        }


@dataclass(frozen=True)
class LinearAxionVerificationResult:
    """Complete numerical evidence for the frozen Version 0.5 benchmark."""

    cases: Tuple[LinearAxionCaseResult, ...]
    refinements: Tuple[LinearAxionRefinementEvidence, ...]

    @property
    def acceptance_checks(self) -> Tuple[AcceptanceCheck, ...]:
        preflights = [
            frequency.preflight
            for case in self.cases
            for frequency in case.frequency_results
        ]
        max_horizon_residual = max(
            result.background.horizon_residual for result in preflights
        )
        max_temperature_error = max(
            result.background.temperature_relative_error for result in preflights
        )
        max_maxwell_variation = max(
            result.background.maxwell_flux_relative_variation
            for result in preflights
        )
        max_frobenius_ratio = max(
            result.maximum_frobenius_refinement_ratio
            for result in self.refinements
        )
        max_source_residual = max(
            max(result.scalar_source_residual, result.metric_source_residual)
            for result in preflights
        )
        max_condition_number = max(result.condition_number for result in preflights)
        max_equation_residual = max(
            case.maximum_equation_residual for case in self.cases
        )
        max_flux_residual = max(
            case.maximum_flux_balance_residual for case in self.cases
        )
        max_radial_spread = max(
            case.radial_dc_relative_spread for case in self.cases
        )
        max_dc_error = max(case.dc_relative_error for case in self.cases)
        max_imaginary_intercept = max(
            abs(case.imaginary_dc_intercept) for case in self.cases
        )
        max_frequency_change = max(
            case.frequency_fit_change for case in self.cases
        )
        max_horizon_change = max(
            result.horizon_cutoff_relative_change for result in self.refinements
        )
        max_uv_change = max(
            result.uv_endpoint_relative_change for result in self.refinements
        )
        max_tolerance_change = max(
            result.integrator_tolerance_relative_change
            for result in self.refinements
        )
        return (
            AcceptanceCheck(
                identifier="background-horizon",
                description="The exact background has a horizon at r0 = 1.",
                value=max_horizon_residual,
                criterion="value <= 1e-12",
                passed=max_horizon_residual <= 1.0e-12,
            ),
            AcceptanceCheck(
                identifier="temperature-identity",
                description="Analytic differentiation reproduces 4 pi T.",
                value=max_temperature_error,
                criterion="relative error <= 1e-10",
                passed=max_temperature_error <= 1.0e-10,
            ),
            AcceptanceCheck(
                identifier="maxwell-flux",
                description="The background Maxwell radial flux is constant.",
                value=max_maxwell_variation,
                criterion="relative variation <= 1e-10",
                passed=max_maxwell_variation <= 1.0e-10,
            ),
            AcceptanceCheck(
                identifier="ingoing-branch-refinement",
                description=(
                    "The initialized Frobenius-exponent error improves when "
                    "the horizon cutoff is halved."
                ),
                value=max_frobenius_ratio,
                criterion="fine/coarse error ratio < 0.51",
                passed=max_frobenius_ratio < 0.51,
            ),
            AcceptanceCheck(
                identifier="uv-source-residual",
                description="Scalar and metric fluctuation sources vanish.",
                value=max_source_residual,
                criterion=f"value <= {DEFAULT_SOURCE_TOLERANCE:.16g}",
                passed=max_source_residual <= DEFAULT_SOURCE_TOLERANCE,
            ),
            AcceptanceCheck(
                identifier="uv-source-condition-number",
                description="The two-master source solve is well conditioned.",
                value=max_condition_number,
                criterion=f"value < {DEFAULT_CONDITION_LIMIT:.16g}",
                passed=max_condition_number < DEFAULT_CONDITION_LIMIT,
            ),
            AcceptanceCheck(
                identifier="equation-reconstruction",
                description="Reconstructed fields satisfy source Eqs. (3.8)-(3.9).",
                value=max_equation_residual,
                criterion=f"value <= {DEFAULT_EQUATION_TOLERANCE:.16g}",
                passed=max_equation_residual <= DEFAULT_EQUATION_TOLERANCE,
            ),
            AcceptanceCheck(
                identifier="finite-frequency-flux-balance",
                description="The source-paper radial flux identity is satisfied.",
                value=max_flux_residual,
                criterion=f"value <= {DEFAULT_FLUX_TOLERANCE:.16g}",
                passed=max_flux_residual <= DEFAULT_FLUX_TOLERANCE,
            ),
            AcceptanceCheck(
                identifier="radial-dc-agreement",
                description="DC flux intercepts agree at the frozen radii.",
                value=max_radial_spread,
                criterion=f"relative spread <= {DEFAULT_RADIAL_DC_TOLERANCE:.16g}",
                passed=max_radial_spread <= DEFAULT_RADIAL_DC_TOLERANCE,
            ),
            AcceptanceCheck(
                identifier="exact-dc-conductivity",
                description="Boundary-response DC values reproduce 1 + mu^2/alpha^2.",
                value=max_dc_error,
                criterion=f"relative error <= {DEFAULT_DC_RELATIVE_TOLERANCE:.16g}",
                passed=max_dc_error <= DEFAULT_DC_RELATIVE_TOLERANCE,
            ),
            AcceptanceCheck(
                identifier="imaginary-dc-intercept",
                description="The odd-frequency imaginary response has zero intercept.",
                value=max_imaginary_intercept,
                criterion=(
                    f"absolute value <= {DEFAULT_IMAGINARY_INTERCEPT_TOLERANCE:.16g}"
                ),
                passed=(
                    max_imaginary_intercept
                    <= DEFAULT_IMAGINARY_INTERCEPT_TOLERANCE
                ),
            ),
            AcceptanceCheck(
                identifier="frequency-fit-stability",
                description="Dropping the largest frequency leaves the DC fit stable.",
                value=max_frequency_change,
                criterion=(
                    f"relative change <= {DEFAULT_FREQUENCY_STABILITY_TOLERANCE:.16g}"
                ),
                passed=max_frequency_change <= DEFAULT_FREQUENCY_STABILITY_TOLERANCE,
            ),
            AcceptanceCheck(
                identifier="horizon-cutoff-refinement",
                description="Halving the horizon cutoff leaves the DC result stable.",
                value=max_horizon_change,
                criterion=(
                    f"relative change <= {DEFAULT_HORIZON_REFINEMENT_TOLERANCE:.16g}"
                ),
                passed=max_horizon_change <= DEFAULT_HORIZON_REFINEMENT_TOLERANCE,
            ),
            AcceptanceCheck(
                identifier="uv-endpoint-refinement",
                description="Increasing r_max to 80 leaves the DC result stable.",
                value=max_uv_change,
                criterion=f"relative change <= {DEFAULT_UV_REFINEMENT_TOLERANCE:.16g}",
                passed=max_uv_change <= DEFAULT_UV_REFINEMENT_TOLERANCE,
            ),
            AcceptanceCheck(
                identifier="integrator-tolerance-refinement",
                description="Ten-times tighter integrator tolerances leave DC stable.",
                value=max_tolerance_change,
                criterion=(
                    "relative change <= "
                    f"{DEFAULT_INTEGRATOR_REFINEMENT_TOLERANCE:.16g}"
                ),
                passed=(
                    max_tolerance_change
                    <= DEFAULT_INTEGRATOR_REFINEMENT_TOLERANCE
                ),
            ),
        )

    @property
    def passed(self) -> bool:
        return all(check.passed for check in self.acceptance_checks)

    def to_dict(self) -> Dict[str, Any]:
        record = VerificationRecord(
            definition=LINEAR_AXION_DEFINITION,
            configuration={
                "r0": 1.0,
                "parameter_cases": [
                    {
                        "case": case.identifier,
                        "chemical_potential": case.chemical_potential,
                        "axion_gradient": case.axion_gradient,
                    }
                    for case in self.cases
                ],
                "frequencies": list(DEFAULT_FREQUENCIES),
                "radial_audit_locations": list(DEFAULT_RADIAL_AUDIT_LOCATIONS),
                "ensemble": (
                    "grand canonical with fixed chemical-potential and "
                    "linear-scalar sources"
                ),
            },
            numerical_method={
                "master_solver": LINEAR_AXION_DEFINITION.solvers[0].to_dict(),
                "uv_fit_basis": ["1", "1/r", "1/r^2"],
                "uv_fit_window": "final 20 percent of 800 radial samples",
                "real_dc_fit": "intercept + slope*omega^2",
                "imaginary_dc_fit": "intercept + b1*omega + b3*omega^3",
                "equation_check": "analytic reconstruction on a staggered grid",
                "radial_flux_check": "analytic derivative of reconstructed fields",
            },
            results={
                "cases": [case.to_dict() for case in self.cases],
                "refinements": [
                    refinement.to_dict() for refinement in self.refinements
                ],
            },
            acceptance_checks=self.acceptance_checks,
            software_versions=runtime_versions(),
            scope=(
                "Numerical reproduction of the selected bottom-up model's "
                "four-dimensional DC conductivity; not empirical validation "
                "of a material or a microscopic theory of momentum relaxation."
            ),
            extra={
                "primary_source": {
                    "arxiv": "1311.5157v2",
                    "doi": "10.1007/JHEP05(2014)101",
                    "equation_locators": [
                        "Eqs. (2.1)-(2.9)",
                        "Eqs. (3.2)-(3.21)",
                        "Eqs. (3.24)-(3.26)",
                        "Appendix A",
                    ],
                },
                "limitations": [
                    "The calculation is a classical bottom-up effective model.",
                    "The neutral, translation-invariant, and extremal limits are excluded.",
                    "The frequency sequence is a bounded DC extrapolation, not a full optical spectrum.",
                ],
            },
        )
        return record.to_dict()


@dataclass(frozen=True)
class _MasterIntegration:
    output_fields: NDArray[np.complex128]
    check_fields: NDArray[np.complex128]
    audit_fields: NDArray[np.complex128]
    frobenius_exponent_error: float


@dataclass(frozen=True)
class _ReconstructedFields:
    gauge: NDArray[np.complex128]
    gauge_prime: NDArray[np.complex128]
    gauge_second: NDArray[np.complex128]
    phi: NDArray[np.complex128]
    phi_prime: NDArray[np.complex128]
    phi_second: NDArray[np.complex128]


@dataclass(frozen=True)
class _SolvedFrequency:
    preflight: SourceMapPreflightResult
    output_radii: NDArray[np.float64]
    output_fields: _ReconstructedFields
    check_radii: NDArray[np.float64]
    check_fields: _ReconstructedFields
    audit_fields: _ReconstructedFields


def blackening_function(
    radius: NDArray[np.float64] | float,
    config: LinearAxionPreflightConfig,
) -> NDArray[np.float64] | float:
    """Evaluate the exact four-dimensional linear-axion blackening factor."""

    r = np.asarray(radius, dtype=float)
    mu = float(config.chemical_potential)
    alpha = float(config.axion_gradient)
    values = r**2 - 0.5 * alpha**2 - config.mass_parameter / r + 0.25 * mu**2 / r**2
    if np.ndim(radius) == 0:
        return float(values)
    return values


def run_background_preflight(
    config: LinearAxionPreflightConfig,
) -> BackgroundPreflight:
    """Check the horizon, temperature identity, and Maxwell radial flux."""

    mu = float(config.chemical_potential)
    analytic_slope = float(config.horizon_slope)
    differentiated_slope = 2.0 + config.mass_parameter - 0.5 * mu**2
    temperature = analytic_slope / (4.0 * math.pi)
    temperature_error = abs(differentiated_slope - analytic_slope) / abs(
        analytic_slope
    )

    radii = np.geomspace(1.0 + config.horizon_cutoff, config.uv_endpoint, 80)
    radial_flux = radii**2 * (mu / radii**2)
    flux_variation = float(
        np.ptp(radial_flux) / max(abs(float(np.mean(radial_flux))), 1.0e-300)
    )
    return BackgroundPreflight(
        horizon_residual=abs(float(blackening_function(1.0, config))),
        temperature_relative_error=float(temperature_error),
        maxwell_flux_relative_variation=flux_variation,
        temperature=float(temperature),
        mass_parameter=float(config.mass_parameter),
    )


def master_constants(config: LinearAxionPreflightConfig) -> Tuple[float, float]:
    """Return the two constants in source Eqs. (3.25) and (3.26)."""

    mu = float(config.chemical_potential)
    alpha = float(config.axion_gradient)
    discriminant = math.sqrt(9.0 * config.mass_parameter**2 + 4.0 * mu**2 * alpha**2)
    return (
        (3.0 * config.mass_parameter + discriminant) / (2.0 * mu),
        (3.0 * config.mass_parameter - discriminant) / (2.0 * mu),
    )


def run_source_map_preflight(
    config: LinearAxionPreflightConfig | None = None,
) -> SourceMapPreflightResult:
    """Integrate both ingoing master fields and impose the two UV sources.

    The two independent amplitude equations are the unit gauge source and the
    vanishing gauge-invariant scalar/metric source.  The latter is the
    no-growing-``phi`` condition; the separate scalar and metric statements in
    the contract are its two gauge-dependent consequences, not two extra
    amplitude equations.
    """

    if config is None:
        config = LinearAxionPreflightConfig()
    return _solve_frequency(config).preflight


def solve_linear_axion_frequency(
    config: Optional[LinearAxionPreflightConfig] = None,
) -> LinearAxionFrequencyResult:
    """Solve one finite-frequency response and evaluate gates 5--7."""

    if config is None:
        config = LinearAxionPreflightConfig()
    solved = _solve_frequency(config)
    gauge_coefficients, _ = _fit_inverse_radius(
        solved.output_fields.gauge, solved.output_radii, config
    )
    gauge_source = complex(gauge_coefficients[0])
    current_response = complex(gauge_coefficients[1])
    conductivity = current_response / (
        1j * float(config.frequency) * gauge_source
    )
    equation_residual = _equation_reconstruction_residual(
        solved.check_radii, solved.check_fields, config
    )
    flux_balance_residual = _flux_balance_residual(
        solved.check_radii, solved.check_fields, config
    )
    radial_proxies = _radial_dc_proxies(
        np.asarray(DEFAULT_RADIAL_AUDIT_LOCATIONS, dtype=float),
        solved.audit_fields,
        config,
    )
    return LinearAxionFrequencyResult(
        preflight=solved.preflight,
        current_response=current_response,
        conductivity=complex(conductivity),
        equation_residual=equation_residual,
        flux_balance_residual=flux_balance_residual,
        radial_dc_proxies=(
            complex(radial_proxies[0]),
            complex(radial_proxies[1]),
            complex(radial_proxies[2]),
        ),
    )


def solve_linear_axion_case(
    identifier: str,
    chemical_potential: float,
    axion_gradient: float,
    base_config: Optional[LinearAxionPreflightConfig] = None,
) -> LinearAxionCaseResult:
    """Solve the frozen four-frequency sequence for one parameter case."""

    if not isinstance(identifier, str) or not identifier.strip():
        raise ValueError("identifier must be a nonempty string")
    if base_config is None:
        base_config = LinearAxionPreflightConfig(
            chemical_potential=chemical_potential,
            axion_gradient=axion_gradient,
        )
    else:
        base_config = replace(
            base_config,
            chemical_potential=chemical_potential,
            axion_gradient=axion_gradient,
        )
    frequency_results = tuple(
        solve_linear_axion_frequency(
            replace(base_config, frequency=float(frequency))
        )
        for frequency in DEFAULT_FREQUENCIES
    )
    frequencies = np.asarray(DEFAULT_FREQUENCIES, dtype=float)
    conductivities = np.asarray(
        [result.conductivity for result in frequency_results],
        dtype=np.complex128,
    )
    real_intercept = _fit_intercept(
        frequencies,
        conductivities.real,
        powers=(0, 2),
    )
    stable_real_intercept = _fit_intercept(
        frequencies[1:],
        conductivities.real[1:],
        powers=(0, 2),
    )
    imaginary_intercept = _fit_intercept(
        frequencies,
        conductivities.imag,
        powers=(0, 1, 3),
    )
    radial_intercepts = tuple(
        _fit_intercept(
            frequencies,
            np.asarray(
                [result.radial_dc_proxies[index].real for result in frequency_results],
                dtype=float,
            ),
            powers=(0, 2),
        )
        for index in range(len(DEFAULT_RADIAL_AUDIT_LOCATIONS))
    )
    exact_dc = 1.0 + float(chemical_potential) ** 2 / float(axion_gradient) ** 2
    return LinearAxionCaseResult(
        identifier=identifier.strip(),
        chemical_potential=float(chemical_potential),
        axion_gradient=float(axion_gradient),
        frequency_results=frequency_results,
        exact_dc_conductivity=exact_dc,
        real_dc_intercept=real_intercept,
        imaginary_dc_intercept=imaginary_intercept,
        stable_real_dc_intercept=stable_real_intercept,
        radial_dc_intercepts=(
            float(radial_intercepts[0]),
            float(radial_intercepts[1]),
            float(radial_intercepts[2]),
        ),
    )


def verify_linear_axion_dc() -> LinearAxionVerificationResult:
    """Run all frozen cases, frequency fits, and numerical refinements."""

    cases: List[LinearAxionCaseResult] = []
    refinements: List[LinearAxionRefinementEvidence] = []
    default_config = LinearAxionPreflightConfig()
    for identifier, chemical_potential, axion_gradient in DEFAULT_PARAMETER_CASES:
        baseline = solve_linear_axion_case(
            identifier,
            chemical_potential,
            axion_gradient,
            default_config,
        )
        horizon_refined = solve_linear_axion_case(
            identifier,
            chemical_potential,
            axion_gradient,
            replace(
                default_config,
                horizon_cutoff=default_config.horizon_cutoff / 2.0,
            ),
        )
        uv_refined = solve_linear_axion_case(
            identifier,
            chemical_potential,
            axion_gradient,
            replace(default_config, uv_endpoint=80.0),
        )
        tolerance_refined = solve_linear_axion_case(
            identifier,
            chemical_potential,
            axion_gradient,
            replace(
                default_config,
                relative_tolerance=default_config.relative_tolerance / 10.0,
                absolute_tolerance=default_config.absolute_tolerance / 10.0,
            ),
        )
        frobenius_ratios = [
            fine_error / coarse_error
            for coarse_frequency, fine_frequency in zip(
                baseline.frequency_results,
                horizon_refined.frequency_results,
            )
            for coarse_error, fine_error in zip(
                coarse_frequency.preflight.frobenius_exponent_errors,
                fine_frequency.preflight.frobenius_exponent_errors,
            )
        ]
        cases.append(baseline)
        refinements.append(
            LinearAxionRefinementEvidence(
                case_identifier=identifier,
                horizon_cutoff_relative_change=_relative_change(
                    baseline.real_dc_intercept,
                    horizon_refined.real_dc_intercept,
                ),
                uv_endpoint_relative_change=_relative_change(
                    baseline.real_dc_intercept,
                    uv_refined.real_dc_intercept,
                ),
                integrator_tolerance_relative_change=_relative_change(
                    baseline.real_dc_intercept,
                    tolerance_refined.real_dc_intercept,
                ),
                maximum_frobenius_refinement_ratio=max(frobenius_ratios),
            )
        )
    return LinearAxionVerificationResult(
        cases=tuple(cases), refinements=tuple(refinements)
    )


def _solve_frequency(config: LinearAxionPreflightConfig) -> _SolvedFrequency:
    background = run_background_preflight(config)
    constants = master_constants(config)
    output_radii = np.linspace(
        1.0 + config.horizon_cutoff,
        config.uv_endpoint,
        config.radial_points,
    )
    check_start = 1.0 + max(100.0 * config.horizon_cutoff, 1.0e-4)
    check_stop = min(config.uv_endpoint - 0.5, 0.99 * config.uv_endpoint)
    check_radii = np.linspace(check_start, check_stop, 601)
    audit_radii = np.asarray(DEFAULT_RADIAL_AUDIT_LOCATIONS, dtype=float)
    integrations = tuple(
        _integrate_master_state(
            constant,
            config,
            output_radii,
            check_radii,
            audit_radii,
        )
        for constant in constants
    )

    master_leading = []
    master_fit_residuals = []
    for integration in integrations:
        coefficients, residual = _fit_inverse_radius(
            integration.output_fields[0], output_radii, config
        )
        master_leading.append(coefficients[0])
        master_fit_residuals.append(residual)

    constant_plus, constant_minus = constants
    leading_plus, leading_minus = master_leading
    source_matrix = np.asarray(
        (
            (-1j * leading_plus, -1j * leading_minus),
            (
                constant_plus * leading_plus,
                constant_minus * leading_minus,
            ),
        ),
        dtype=np.complex128,
    )
    condition_number = float(np.linalg.cond(source_matrix))
    if not math.isfinite(condition_number):
        raise RuntimeError("UV source matrix is singular")
    amplitudes = np.linalg.solve(
        source_matrix, np.asarray((1.0, 0.0), dtype=np.complex128)
    )

    output_fields = _reconstruct_fields(
        output_radii,
        integrations[0].output_fields,
        integrations[1].output_fields,
        constants,
        amplitudes,
        config,
    )
    check_fields = _reconstruct_fields(
        check_radii,
        integrations[0].check_fields,
        integrations[1].check_fields,
        constants,
        amplitudes,
        config,
    )
    audit_fields = _reconstruct_fields(
        audit_radii,
        integrations[0].audit_fields,
        integrations[1].audit_fields,
        constants,
        amplitudes,
        config,
    )
    gauge_coefficients, gauge_fit_residual = _fit_inverse_radius(
        output_fields.gauge, output_radii, config
    )
    phi_coefficients, phi_fit_residual = _fit_inverse_radius(
        output_fields.phi / output_radii, output_radii, config
    )
    gauge_source = complex(gauge_coefficients[0])
    phi_growing = complex(phi_coefficients[0])
    invariant_source = -phi_growing
    preflight = SourceMapPreflightResult(
        config=config,
        background=background,
        master_constants=constants,
        amplitudes=(complex(amplitudes[0]), complex(amplitudes[1])),
        source_matrix=source_matrix,
        condition_number=condition_number,
        gauge_source=gauge_source,
        phi_growing_coefficient=phi_growing,
        gauge_source_residual=abs(gauge_source - 1.0),
        scalar_source_residual=(
            abs(invariant_source) / float(config.frequency)
        ),
        metric_source_residual=(
            abs(invariant_source) / float(config.axion_gradient) ** 2
        ),
        master_uv_fit_residuals=(
            float(master_fit_residuals[0]),
            float(master_fit_residuals[1]),
        ),
        reconstructed_uv_fit_residuals=(
            float(gauge_fit_residual),
            float(phi_fit_residual),
        ),
        frobenius_exponent_errors=(
            integrations[0].frobenius_exponent_error,
            integrations[1].frobenius_exponent_error,
        ),
    )
    return _SolvedFrequency(
        preflight=preflight,
        output_radii=output_radii,
        output_fields=output_fields,
        check_radii=check_radii,
        check_fields=check_fields,
        audit_fields=audit_fields,
    )


def _integrate_master(
    constant: float,
    config: LinearAxionPreflightConfig,
    radii: NDArray[np.float64],
) -> Tuple[NDArray[np.complex128], float]:
    check_radii = np.asarray((2.0,), dtype=float)
    audit_radii = np.asarray(DEFAULT_RADIAL_AUDIT_LOCATIONS, dtype=float)
    result = _integrate_master_state(
        constant,
        config,
        radii,
        check_radii,
        audit_radii,
    )
    return result.output_fields[0], result.frobenius_exponent_error


def _integrate_master_state(
    constant: float,
    config: LinearAxionPreflightConfig,
    output_radii: NDArray[np.float64],
    check_radii: NDArray[np.float64],
    audit_radii: NDArray[np.float64],
) -> _MasterIntegration:
    initial_value, initial_derivative, exponent_error = _ingoing_initial_data(
        constant, config
    )

    def equation(
        radius: float, fields: NDArray[np.complex128]
    ) -> NDArray[np.complex128]:
        return _master_rhs(radius, fields, constant, config)

    solution = solve_ivp(
        equation,
        (float(output_radii[0]), float(output_radii[-1])),
        np.asarray((initial_value, initial_derivative), dtype=np.complex128),
        method="DOP853",
        dense_output=True,
        rtol=float(config.relative_tolerance),
        atol=float(config.absolute_tolerance),
    )
    if not solution.success:
        raise RuntimeError(f"master-field integration failed: {solution.message}")
    if solution.sol is None:
        raise RuntimeError("master-field integration returned no dense solution")
    return _MasterIntegration(
        output_fields=np.asarray(solution.sol(output_radii), dtype=np.complex128),
        check_fields=np.asarray(solution.sol(check_radii), dtype=np.complex128),
        audit_fields=np.asarray(solution.sol(audit_radii), dtype=np.complex128),
        frobenius_exponent_error=exponent_error,
    )


def _master_rhs(
    radius: float,
    fields: NDArray[np.complex128],
    constant: float,
    config: LinearAxionPreflightConfig,
) -> NDArray[np.complex128]:
    value, derivative = fields
    mu = float(config.chemical_potential)
    blackening = float(blackening_function(radius, config))
    blackening_prime = _blackening_prime(radius, config)
    potential = (
        config.frequency**2 / blackening**2
        - mu**2 / (blackening * radius**4)
        + constant * mu / (blackening * radius**3)
    )
    return np.asarray(
        (
            derivative,
            -(blackening_prime / blackening) * derivative - potential * value,
        ),
        dtype=np.complex128,
    )


def _reconstruct_fields(
    radii: NDArray[np.float64],
    plus_fields: NDArray[np.complex128],
    minus_fields: NDArray[np.complex128],
    constants: Tuple[float, float],
    amplitudes: NDArray[np.complex128],
    config: LinearAxionPreflightConfig,
) -> _ReconstructedFields:
    plus_value, plus_prime = plus_fields
    minus_value, minus_prime = minus_fields
    plus_second = _master_second_derivative(
        radii, plus_value, plus_prime, constants[0], config
    )
    minus_second = _master_second_derivative(
        radii, minus_value, minus_prime, constants[1], config
    )

    sum_value = amplitudes[0] * plus_value + amplitudes[1] * minus_value
    sum_prime = amplitudes[0] * plus_prime + amplitudes[1] * minus_prime
    sum_second = amplitudes[0] * plus_second + amplitudes[1] * minus_second
    weighted_value = (
        constants[0] * amplitudes[0] * plus_value
        + constants[1] * amplitudes[1] * minus_value
    )
    weighted_prime = (
        constants[0] * amplitudes[0] * plus_prime
        + constants[1] * amplitudes[1] * minus_prime
    )
    weighted_second = (
        constants[0] * amplitudes[0] * plus_second
        + constants[1] * amplitudes[1] * minus_second
    )
    return _ReconstructedFields(
        gauge=np.asarray(-1j * sum_value, dtype=np.complex128),
        gauge_prime=np.asarray(-1j * sum_prime, dtype=np.complex128),
        gauge_second=np.asarray(-1j * sum_second, dtype=np.complex128),
        phi=np.asarray(radii * weighted_value, dtype=np.complex128),
        phi_prime=np.asarray(
            weighted_value + radii * weighted_prime,
            dtype=np.complex128,
        ),
        phi_second=np.asarray(
            2.0 * weighted_prime + radii * weighted_second,
            dtype=np.complex128,
        ),
    )


def _master_second_derivative(
    radii: NDArray[np.float64],
    values: NDArray[np.complex128],
    derivatives: NDArray[np.complex128],
    constant: float,
    config: LinearAxionPreflightConfig,
) -> NDArray[np.complex128]:
    blackening = np.asarray(blackening_function(radii, config), dtype=float)
    blackening_prime = _blackening_prime(radii, config)
    mu = float(config.chemical_potential)
    potential = (
        config.frequency**2 / blackening**2
        - mu**2 / (blackening * radii**4)
        + constant * mu / (blackening * radii**3)
    )
    return np.asarray(
        -(blackening_prime / blackening) * derivatives - potential * values,
        dtype=np.complex128,
    )


def _equation_reconstruction_residual(
    radii: NDArray[np.float64],
    fields: _ReconstructedFields,
    config: LinearAxionPreflightConfig,
) -> float:
    blackening = np.asarray(blackening_function(radii, config), dtype=float)
    blackening_prime = _blackening_prime(radii, config)
    mu = float(config.chemical_potential)
    alpha = float(config.axion_gradient)
    omega = float(config.frequency)

    gauge_terms = (
        blackening * fields.gauge_second,
        blackening_prime * fields.gauge_prime,
        omega**2 * fields.gauge / blackening,
        -mu**2 * fields.gauge / radii**4,
        -1j * mu * fields.phi / radii**4,
    )
    phi_terms = (
        blackening * fields.phi_second,
        (blackening_prime - 2.0 * blackening / radii) * fields.phi_prime,
        omega**2 * fields.phi / blackening,
        1j * alpha**2 * mu * fields.gauge / radii**2,
        -alpha**2 * fields.phi / radii**2,
    )
    return max(
        _normalized_sum_residual(gauge_terms),
        _normalized_sum_residual(phi_terms),
    )


def _flux_balance_residual(
    radii: NDArray[np.float64],
    fields: _ReconstructedFields,
    config: LinearAxionPreflightConfig,
) -> float:
    lambda_one, _, _, pi_prime = _flux_quantities(radii, fields, config)
    blackening = np.asarray(blackening_function(radii, config), dtype=float)
    mu = float(config.chemical_potential)
    alpha = float(config.axion_gradient)
    radial_factor = 1.0 + mu**2 / (alpha**2 * radii**2)
    frequency_term = config.frequency**2 * radial_factor * lambda_one / blackening
    return _normalized_sum_residual((pi_prime, frequency_term))


def _radial_dc_proxies(
    radii: NDArray[np.float64],
    fields: _ReconstructedFields,
    config: LinearAxionPreflightConfig,
) -> NDArray[np.complex128]:
    lambda_one, _, pi, _ = _flux_quantities(radii, fields, config)
    return np.asarray(
        -pi / (1j * float(config.frequency) * lambda_one),
        dtype=np.complex128,
    )


def _flux_quantities(
    radii: NDArray[np.float64],
    fields: _ReconstructedFields,
    config: LinearAxionPreflightConfig,
) -> Tuple[
    NDArray[np.complex128],
    NDArray[np.complex128],
    NDArray[np.complex128],
    NDArray[np.complex128],
]:
    mu = float(config.chemical_potential)
    alpha = float(config.axion_gradient)
    blackening = np.asarray(blackening_function(radii, config), dtype=float)
    blackening_prime = _blackening_prime(radii, config)
    radial_factor = 1.0 + mu**2 / (alpha**2 * radii**2)
    radial_factor_prime = -2.0 * mu**2 / (alpha**2 * radii**3)
    radial_factor_second = 6.0 * mu**2 / (alpha**2 * radii**4)

    numerator_one = fields.gauge - 1j * mu * fields.phi / (alpha**2 * radii**2)
    numerator_one_prime = fields.gauge_prime - 1j * mu / alpha**2 * (
        fields.phi_prime / radii**2 - 2.0 * fields.phi / radii**3
    )
    numerator_one_second = fields.gauge_second - 1j * mu / alpha**2 * (
        fields.phi_second / radii**2
        - 4.0 * fields.phi_prime / radii**3
        + 6.0 * fields.phi / radii**4
    )
    lambda_one = numerator_one / radial_factor
    lambda_one_prime = (
        numerator_one_prime / radial_factor
        - numerator_one * radial_factor_prime / radial_factor**2
    )
    lambda_one_second = (
        numerator_one_second / radial_factor
        - 2.0
        * numerator_one_prime
        * radial_factor_prime
        / radial_factor**2
        - numerator_one * radial_factor_second / radial_factor**2
        + 2.0
        * numerator_one
        * radial_factor_prime**2
        / radial_factor**3
    )

    numerator_two = (
        mu**2 * fields.gauge + 1j * mu * fields.phi
    ) / (alpha**2 * radii**2)
    numerator_two_prime = (
        (mu**2 * fields.gauge_prime + 1j * mu * fields.phi_prime)
        / (alpha**2 * radii**2)
        - 2.0
        * (mu**2 * fields.gauge + 1j * mu * fields.phi)
        / (alpha**2 * radii**3)
    )
    lambda_two = numerator_two / radial_factor
    lambda_two_prime = (
        numerator_two_prime / radial_factor
        - numerator_two * radial_factor_prime / radial_factor**2
    )
    pi = (
        blackening * radial_factor * lambda_one_prime
        - 2.0 * blackening * lambda_two / radii
    )
    pi_prime = (
        blackening_prime * radial_factor * lambda_one_prime
        + blackening * radial_factor_prime * lambda_one_prime
        + blackening * radial_factor * lambda_one_second
        - 2.0 * blackening_prime * lambda_two / radii
        - 2.0 * blackening * lambda_two_prime / radii
        + 2.0 * blackening * lambda_two / radii**2
    )
    return (
        np.asarray(lambda_one, dtype=np.complex128),
        np.asarray(lambda_two, dtype=np.complex128),
        np.asarray(pi, dtype=np.complex128),
        np.asarray(pi_prime, dtype=np.complex128),
    )


def _normalized_sum_residual(
    terms: Sequence[NDArray[np.complex128]],
) -> float:
    residual = np.sum(np.asarray(terms, dtype=np.complex128), axis=0)
    scale = np.sum(np.abs(np.asarray(terms, dtype=np.complex128)), axis=0)
    return float(
        np.max(np.abs(residual)) / max(float(np.max(scale)), 1.0e-300)
    )


def _fit_intercept(
    frequencies: NDArray[np.float64],
    values: NDArray[np.float64],
    powers: Sequence[int],
) -> float:
    design = np.column_stack([frequencies**power for power in powers])
    coefficients, _, _, _ = np.linalg.lstsq(design, values, rcond=None)
    return float(coefficients[0])


def _relative_change(reference: float, comparison: float) -> float:
    return abs(float(reference) - float(comparison)) / max(
        abs(float(reference)), 1.0e-300
    )


def _blackening_prime(
    radius: NDArray[np.float64] | float,
    config: LinearAxionPreflightConfig,
) -> NDArray[np.float64] | float:
    values = np.asarray(radius, dtype=float)
    mu = float(config.chemical_potential)
    result = (
        2.0 * values
        + config.mass_parameter / values**2
        - 0.5 * mu**2 / values**3
    )
    if np.ndim(radius) == 0:
        return float(result)
    return np.asarray(result, dtype=float)


def _ingoing_initial_data(
    constant: float,
    config: LinearAxionPreflightConfig,
) -> Tuple[complex, complex, float]:
    epsilon = float(config.horizon_cutoff)
    mu = float(config.chemical_potential)
    alpha = float(config.axion_gradient)
    slope = float(config.horizon_slope)
    exponent = -1j * float(config.frequency) / slope
    second_derivative = alpha**2 + mu**2
    horizon_potential = -mu**2 + constant * mu
    first_correction = (
        -second_derivative * exponent / (2.0 * slope)
        - horizon_potential / (slope * (2.0 * exponent + 1.0))
    )
    logarithmic_derivative = (
        exponent + first_correction * (exponent + 1.0) * epsilon
    ) / (epsilon * (1.0 + first_correction * epsilon))
    exponent_error = abs(epsilon * logarithmic_derivative - exponent)
    return 1.0 + 0.0j, complex(logarithmic_derivative), float(exponent_error)


def _fit_inverse_radius(
    values: NDArray[np.complex128],
    radii: NDArray[np.float64],
    config: LinearAxionPreflightConfig,
) -> Tuple[NDArray[np.complex128], float]:
    count = max(6, int(math.ceil(config.uv_fit_fraction * radii.size)))
    fit_radii = radii[-count:]
    fit_values = values[-count:]
    design = np.column_stack(
        (
            np.ones_like(fit_radii),
            1.0 / fit_radii,
            1.0 / fit_radii**2,
        )
    )
    coefficients, _, _, _ = np.linalg.lstsq(design, fit_values, rcond=None)
    fitted = design @ coefficients
    residual = np.linalg.norm(fitted - fit_values) / max(
        float(np.linalg.norm(fit_values)), 1.0e-300
    )
    return np.asarray(coefficients, dtype=np.complex128), float(residual)


def _complex_record(value: complex) -> Dict[str, float]:
    return {"real": float(value.real), "imaginary": float(value.imag)}


def _require_positive(value: Real, name: str) -> None:
    if isinstance(value, bool) or not isinstance(value, Real):
        raise ValueError(f"{name} must be a finite positive number")
    if not math.isfinite(float(value)) or float(value) <= 0.0:
        raise ValueError(f"{name} must be a finite positive number")


def _require_fraction(value: Real, name: str) -> None:
    _require_positive(value, name)
    if float(value) >= 1.0:
        raise ValueError(f"{name} must be less than one")


def _require_integer_at_least(value: int, minimum: int, name: str) -> None:
    if isinstance(value, bool) or not isinstance(value, Integral):
        raise ValueError(f"{name} must be an integer")
    if int(value) < minimum:
        raise ValueError(f"{name} must be at least {minimum}")


__all__ = [
    "BackgroundPreflight",
    "DEFAULT_CONDITION_LIMIT",
    "DEFAULT_DC_RELATIVE_TOLERANCE",
    "DEFAULT_EQUATION_TOLERANCE",
    "DEFAULT_FREQUENCIES",
    "DEFAULT_FLUX_TOLERANCE",
    "DEFAULT_FREQUENCY_STABILITY_TOLERANCE",
    "DEFAULT_HORIZON_REFINEMENT_TOLERANCE",
    "DEFAULT_IMAGINARY_INTERCEPT_TOLERANCE",
    "DEFAULT_INTEGRATOR_REFINEMENT_TOLERANCE",
    "DEFAULT_PARAMETER_CASES",
    "DEFAULT_RADIAL_AUDIT_LOCATIONS",
    "DEFAULT_RADIAL_DC_TOLERANCE",
    "DEFAULT_SOURCE_TOLERANCE",
    "DEFAULT_UV_REFINEMENT_TOLERANCE",
    "LINEAR_AXION_DEFINITION",
    "LinearAxionCaseResult",
    "LinearAxionFrequencyResult",
    "LinearAxionPreflightConfig",
    "LinearAxionRefinementEvidence",
    "LinearAxionVerificationResult",
    "SourceMapPreflightResult",
    "blackening_function",
    "master_constants",
    "run_background_preflight",
    "run_source_map_preflight",
    "solve_linear_axion_case",
    "solve_linear_axion_frequency",
    "verify_linear_axion_dc",
]
