"""Reduced finite-density DeWolfe--Gubser--Rosen EMD benchmark.

This module is intentionally separate from the accepted Phase 5A neutral
benchmark.  Its primary route solves the fully backreacted charged equations
in conformal radial gauge with the Maxwell flux eliminated analytically.  A
passing calculation verifies representative charged backgrounds, independent
conserved quantities, and the source model's reported critical-coordinate
neighborhood.  The optional dense-map topology campaign is preserved
separately and does not gate this classical example.  No passing result is
empirical evidence for a QCD critical point.
"""

from __future__ import annotations

from dataclasses import dataclass
import csv
import json
import math
from numbers import Integral, Real
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple

import numpy as np
from numpy.typing import NDArray
from scipy.integrate import solve_ivp
from scipy.interpolate import BarycentricInterpolator
from scipy.optimize import brentq, least_squares, root
from scipy.special import roots_jacobi

from holoforge.benchmarks.dewolfe_gubser_rosen_emd import (
    DGR_POTENTIAL,
    LAMBDA_MU_MEV,
    LAMBDA_RHO_MEV3,
    LAMBDA_S_MEV3,
    LAMBDA_T_MEV,
    SOURCE_ARCHIVE_SHA256,
    SOURCE_ID,
    SOURCE_PDF_SHA256,
    gauge_coupling,
    gauge_log_derivative,
)
from holoforge.benchmarks.gubser_nellore_ed import (
    CoupledProfile,
    solve_coupled_profile,
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
from holoforge.numerics import chebyshev_lobatto_grid
from holoforge.numerics.interpolation import (
    deterministic_barycentric_interpolator as _barycentric_interpolator,
)
from holoforge.reference_data import load_reference_dataset


DEFAULT_COLLOCATION_TOLERANCE = 1.0e-6
DEFAULT_EQUATION_TOLERANCE = 1.0e-5
DEFAULT_CONSTRAINT_TOLERANCE = 1.0e-5
DEFAULT_BOUNDARY_TOLERANCE = 1.0e-7
DEFAULT_GAUSS_TOLERANCE = 1.0e-7
DEFAULT_NOETHER_TOLERANCE = 1.0e-6
DEFAULT_TARGET_TOLERANCE = 1.0e-7
DEFAULT_PRIMARY_MAXWELL_TOLERANCE = 1.0e-6
DEFAULT_ROUTE_TOLERANCE = 5.0e-6
DEFAULT_FIELD_ROUTE_TOLERANCE = 2.0e-5
DEFAULT_CRITICAL_TOLERANCE = 2.0e-3
DEFAULT_REFINEMENT_TOLERANCE = 2.0e-3
DEFAULT_REFINEMENT_ORDER_FLOOR = 1.0e-8
DEFAULT_DETERMINISM_TOLERANCE = 1.0e-10

DEFAULT_DEGREES = (80, 120, 150)
DEFAULT_CRITICAL_INITIAL = (4.800667, 0.401127)
DEFAULT_CRITICAL_PHI_STEPS = (0.25, 0.125, 0.0625)
DEFAULT_CRITICAL_VALIDATION_STEP = 0.03125
DEFAULT_CRITICAL_ETA_BRACKET = (0.35, 0.45)
DEFAULT_CRITICAL_JACOBIAN_STEPS = (
    (0.25, 1.0 / 60.0),
    (0.125, 0.0125),
    (0.0625, 0.00625),
)
DEFAULT_CONTROL_STATES = (
    ("neutral", 4.84, 0.00),
    ("charged", 4.84, 0.40),
    ("high-charge", 7.00, 0.50),
)
FIGURE_5_RESOURCES = (
    "data/reference/dewolfe-gubser-rosen-figure-5-above-tc.json",
    "data/reference/dewolfe-gubser-rosen-figure-5-at-tc.json",
    "data/reference/dewolfe-gubser-rosen-figure-5-below-tc.json",
)

CRITICAL_PHI_H_INTERVAL = (4.2, 5.5)
CRITICAL_ETA_INTERVAL = (0.30, 0.50)
SOURCE_PHI_H_INTERVAL = (1.0, 15.0)
SOURCE_ETA_INTERVAL = (0.0, 0.9)
LOG_X_H_SOLVER_INTERVAL = (-2.0, 1.0)


DEWOLFE_GUBSER_ROSEN_FINITE_DENSITY_DEFINITION = BenchmarkDefinition(
    identifier="dewolfe-gubser-rosen-emd-critical-point",
    support_level="reproduced",
    background=BackgroundSpec(
        identifier="five-dimensional-dgr-finite-density-black-brane",
        dimension=5,
        coordinate="u = x/x_H in [0,1], x = z^(4-Delta_phi)",
        description=(
            "Phenomenological bottom-up DGR EMD model on representative "
            "neutral and charged homogeneous black-brane backgrounds."
        ),
    ),
    equations=(
        EquationSpec(
            identifier="charged-warp-equation",
            kind="coupled nonlinear boundary-value equation",
            dependent_fields=("A", "phi"),
            expression="A'' - A'^2 + phi'^2/6 = 0",
            source_reference=(
                "DeWolfe, Gubser, Rosen, arXiv:1012.1864v2, Eqs. (27)-(29)"
            ),
        ),
        EquationSpec(
            identifier="charged-blackening-equation",
            kind="coupled nonlinear boundary-value equation",
            dependent_fields=("h", "A", "phi", "Phi"),
            expression=(
                "h'' + 3 A' h' - exp(-2A) f_EMD(phi) Phi'^2 = 0"
            ),
            source_reference=(
                "DeWolfe, Gubser, Rosen, arXiv:1012.1864v2, Eqs. (27)-(29)"
            ),
        ),
        EquationSpec(
            identifier="charged-scalar-equation",
            kind="coupled nonlinear boundary-value equation",
            dependent_fields=("phi", "A", "h", "Phi"),
            expression=(
                "h phi'' + (3 A' h + h') phi' - exp(2A) V_phi "
                "+ exp(-2A) f_EMD,phi Phi'^2/2 = 0"
            ),
            source_reference=(
                "DeWolfe, Gubser, Rosen, arXiv:1012.1864v2, Eqs. (27)-(29)"
            ),
        ),
        EquationSpec(
            identifier="maxwell-equation",
            kind="coupled Maxwell boundary-value equation",
            dependent_fields=("Phi", "A", "phi"),
            expression="d/dz[exp(A) f_EMD(phi) Phi'] = 0",
            source_reference=(
                "DeWolfe, Gubser, Rosen, arXiv:1012.1864v2, Eqs. (38)-(45)"
            ),
        ),
        EquationSpec(
            identifier="einstein-constraint",
            kind="independent radial constraint",
            dependent_fields=("A", "h", "phi", "Phi"),
            expression=(
                "6 A' h' + h(24 A'^2 - phi'^2) + 2 exp(2A) V "
                "+ exp(-2A) f_EMD Phi'^2 = 0"
            ),
            source_reference=(
                "DeWolfe, Gubser, Rosen, arXiv:1012.1864v2, Eqs. (27)-(29)"
            ),
        ),
    ),
    boundary_conditions=(
        BoundaryConditionSpec(
            field="h",
            location="u = 0 and u = 1",
            role="boundary normalization and regular horizon",
            expression="h(0)=1, h(1)=0",
            interpretation="unit boundary time and a nonextremal horizon",
        ),
        BoundaryConditionSpec(
            field="A and phi",
            location="u = 0",
            role="asymptotically AdS source normalization",
            expression="A=-log(z)+O(z^(2 nu)), phi=z^nu+...",
            interpretation="unit scalar-source coefficient in the DGR gauge",
        ),
        BoundaryConditionSpec(
            field="Phi",
            location="u = 0 and u = 1",
            role="grand-canonical source and regular gauge",
            expression="Phi(0)=mu, Phi(1)=0",
            interpretation=(
                "boundary chemical potential with a horizon-regular potential"
            ),
        ),
        BoundaryConditionSpec(
            field="h and phi",
            location="u = 1",
            role="charged horizon regularity",
            expression="source EMD horizon equations",
            interpretation="regular nonextremal charged black brane",
        ),
    ),
    solvers=(
        SolverSpec(
            problem_type="charged nonlinear boundary-value problem",
            library_function="scipy.optimize.root and least_squares",
            method="UV-factorized Chebyshev collocation with analytic flux",
            description=(
                "Primary geometry/scalar solve with Maxwell flux eliminated "
                "analytically and the Einstein equation checked independently."
            ),
        ),
        SolverSpec(
            problem_type="independent charged formulation",
            library_function="scipy.optimize.root and least_squares",
            method="simultaneous explicit-Maxwell Chebyshev collocation",
            description=(
                "Geometry, scalar, and electric potential are solved together "
                "without replacing the primary route."
            ),
        ),
    ),
    observables=(
        ObservableSpec(
            identifier="temperature",
            symbol="T",
            extraction="regular horizon derivative of h",
            normalization="T_BH dimensionless and T_MeV = 252 T_BH",
        ),
        ObservableSpec(
            identifier="chemical-potential",
            symbol="mu",
            extraction="boundary value of the regular electric potential",
            normalization="mu_BH dimensionless and mu_MeV = 972 mu_BH",
        ),
        ObservableSpec(
            identifier="entropy-density",
            symbol="s",
            extraction="2 pi exp(3 A_H) at kappa_5=1",
            normalization="s_BH dimensionless",
        ),
        ObservableSpec(
            identifier="canonical-charge-density",
            symbol="rho",
            extraction="q/2 from the source UV Maxwell dictionary",
            normalization="rho_canonical_BH; distinct from rho_source_figure5",
        ),
    ),
)


@dataclass(frozen=True)
class ChargedSolverConfig:
    """Frozen maintained-library controls for one charged collocation solve."""

    root_tolerance: float = 1.0e-11
    maximum_evaluations_factor: int = 500
    polish_tolerance: float = 1.0e-13
    polish_maximum_evaluations: int = 32
    oversampling_factor: int = 2
    neutral_initial_degree: int = 24
    maximum_eta_step: float = 0.05

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
        _validate_integer(
            "oversampling_factor", self.oversampling_factor, minimum=2
        )
        _validate_integer(
            "neutral_initial_degree", self.neutral_initial_degree, minimum=12
        )
        _validate_positive("maximum_eta_step", self.maximum_eta_step)


@dataclass(frozen=True)
class ChargedNonlinearDiagnostics:
    """Maintained-library status and scaled residuals for one solve."""

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
        return (
            self.root_success and not self.polish_applied
        ) or (self.polish_applied and self.polish_success)

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
                "success": self.polish_success,
                "message": self.polish_message,
                "function_evaluations": self.polish_function_evaluations,
            },
            "final_success": self.success,
            "final_scaled_residual": self.final_scaled_residual,
        }


@dataclass(frozen=True)
class ChargedProfile:
    """One source-normalized charged conformal-gauge background."""

    degree: int
    target_phi_h: float
    target_eta: float
    x_h: float
    q: float
    u: NDArray[np.float64]
    blackening: NDArray[np.float64]
    warp_factor: NDArray[np.float64]
    scalar_factor: NDArray[np.float64]
    nonlinear: ChargedNonlinearDiagnostics

    @property
    def phi_h(self) -> float:
        return float(self.x_h * self.scalar_factor[-1])

    @property
    def z_h(self) -> float:
        return math.exp(math.log(self.x_h) / DGR_POTENTIAL.uv_power)

    @property
    def a_h(self) -> float:
        return float(self.x_h**2 * self.warp_factor[-1])

    @property
    def A_h(self) -> float:
        return -math.log(self.z_h) + self.a_h

    @property
    def eta(self) -> float:
        denominator = math.exp(3.0 * self.A_h) * math.sqrt(
            -2.0
            * float(DGR_POTENTIAL.potential(self.phi_h))
            * float(gauge_coupling(self.phi_h))
        )
        return self.q / denominator if denominator > 0.0 else math.nan

    def interpolators(
        self,
    ) -> Tuple[
        BarycentricInterpolator,
        BarycentricInterpolator,
        BarycentricInterpolator,
    ]:
        return (
            _barycentric_interpolator(self.u, self.blackening),
            _barycentric_interpolator(self.u, self.warp_factor),
            _barycentric_interpolator(self.u, self.scalar_factor),
        )


@dataclass(frozen=True)
class ExplicitMaxwellProfile:
    """Secondary charged solution with ``Phi`` collocated explicitly.

    The regular electric coefficient ``e`` is the spectral unknown in

    ``Phi(u) = mu - u**(2/nu) e(u)``.

    This factorization retains the full second-order Maxwell equation while
    avoiding loss of precision from the high UV power ``2/nu``.  The primary
    flux-reduced route is used only to construct a deterministic initial
    guess; every returned field is part of the simultaneous nonlinear solve.
    """

    degree: int
    target_phi_h: float
    target_eta: float
    x_h: float
    q: float
    chemical_potential: float
    u: NDArray[np.float64]
    blackening: NDArray[np.float64]
    warp_factor: NDArray[np.float64]
    scalar_factor: NDArray[np.float64]
    electric_coefficient: NDArray[np.float64]
    nonlinear: ChargedNonlinearDiagnostics

    @property
    def phi_h(self) -> float:
        return float(self.x_h * self.scalar_factor[-1])

    @property
    def z_h(self) -> float:
        return math.exp(math.log(self.x_h) / DGR_POTENTIAL.uv_power)

    @property
    def a_h(self) -> float:
        return float(self.x_h**2 * self.warp_factor[-1])

    @property
    def A_h(self) -> float:
        return -math.log(self.z_h) + self.a_h

    @property
    def eta(self) -> float:
        denominator = math.exp(3.0 * self.A_h) * math.sqrt(
            -2.0
            * float(DGR_POTENTIAL.potential(self.phi_h))
            * float(gauge_coupling(self.phi_h))
        )
        return self.q / denominator if denominator > 0.0 else math.nan

    @property
    def electric_potential(self) -> NDArray[np.float64]:
        radial_power = np.power(self.u, 2.0 / DGR_POTENTIAL.uv_power)
        return np.asarray(
            self.chemical_potential
            - radial_power * self.electric_coefficient,
            dtype=float,
        )

    def interpolators(
        self,
    ) -> Tuple[
        BarycentricInterpolator,
        BarycentricInterpolator,
        BarycentricInterpolator,
        BarycentricInterpolator,
    ]:
        return (
            _barycentric_interpolator(self.u, self.blackening),
            _barycentric_interpolator(self.u, self.warp_factor),
            _barycentric_interpolator(self.u, self.scalar_factor),
            _barycentric_interpolator(self.u, self.electric_coefficient),
        )

    def as_flux_profile(self) -> ChargedProfile:
        """Expose the shared geometry and flux for existing extractors."""

        return ChargedProfile(
            degree=self.degree,
            target_phi_h=self.target_phi_h,
            target_eta=self.target_eta,
            x_h=self.x_h,
            q=self.q,
            u=self.u,
            blackening=self.blackening,
            warp_factor=self.warp_factor,
            scalar_factor=self.scalar_factor,
            nonlinear=self.nonlinear,
        )


@dataclass(frozen=True)
class ChargedPoint:
    """Thermodynamics and the canonical charge dictionary for one profile.

    ``density`` is the source-derived physical density ``q/2``.  The
    separately digitized Figure 5 ordinate is intentionally not a numerical
    field on this object because no public dictionary maps it to the canonical
    density.
    """

    degree: int
    x_h: float
    phi_h: float
    eta: float
    q: float
    temperature: float
    chemical_potential: float
    entropy: float
    density: float
    temperature_mev: float
    chemical_potential_mev: float
    entropy_mev3: float
    density_mev3: float
    maxwell_integral: float

    @property
    def inverse_f_h_squared_density_diagnostic(self) -> float:
        """Return the unverified inverse-``f_H`` diagnostic.

        This quantity is retained solely to make the density-normalization
        investigation reproducible.  It is not a physical density and cannot
        steer a solve or satisfy an acceptance gate.
        """

        f_h = float(gauge_coupling(self.phi_h))
        return self.density / f_h**2

    def to_dict(self) -> Dict[str, Any]:
        return {
            "degree": self.degree,
            "x_h": self.x_h,
            "phi_h": self.phi_h,
            "eta": self.eta,
            "q": self.q,
            "temperature_BH": self.temperature,
            "mu_BH": self.chemical_potential,
            "entropy_BH": self.entropy,
            "rho_canonical_BH": self.density,
            "temperature_MeV": self.temperature_mev,
            "mu_MeV": self.chemical_potential_mev,
            "entropy_MeV3": self.entropy_mev3,
            "rho_canonical_MeV3": self.density_mev3,
            "maxwell_integral": self.maxwell_integral,
            "review_state": "approved",
            "reviewed_by": "Xin-Yi Liu",
            "reviewed_on": "2026-08-23",
            "density_normalization_state": (
                "canonical-resolved-source-ordinate-blocked"
            ),
            "figure_5_axes": {
                "abscissa": "mu_BH",
                "ordinate": "rho_source_figure5",
            },
            "figure_5_verification": {
                "canonical_topology": {
                    "coordinates": ["rho_canonical_BH", "mu_BH"],
                    "status": "not-evaluated-by-point-solver",
                },
                "absolute_ordinate_comparison": {
                    "source_ordinate": "rho_source_figure5",
                    "status": "blocked",
                    "reason": (
                        "no verified public map to rho_canonical_BH"
                    ),
                },
            },
            "rho_inverse_f_h_squared_diagnostic_BH": (
                self.inverse_f_h_squared_density_diagnostic
            ),
            "rho_inverse_f_h_squared_diagnostic_state": (
                "unverified-non-inferential"
            ),
            "rho_inverse_f_h_squared_diagnostic_affects_acceptance": False,
        }


@dataclass(frozen=True)
class ChargedEquationDiagnostics:
    """Oversampled equations, reconstructed Maxwell field, and endpoints.

    The primary nonlinear solve eliminates the Maxwell field in favor of its
    conserved flux.  These diagnostics reconstruct ``Phi`` independently and
    differentiate that reconstruction before evaluating Gauss conservation.
    """

    warp_equation: float
    blackening_equation: float
    scalar_equation: float
    maxwell_equation: float
    gauss_flux_relative_drift: float
    electric_potential_horizon: float
    maximum_electric_potential_z_derivative: float
    reconstructed_chemical_potential: float
    chemical_potential_reconstruction_relative_error: float
    uv_minus_phi2: float
    uv_minus_phi2_q_over_2_relative_error: float
    constraint: float
    horizon_constraint: float
    horizon_scalar_equation: float
    blackening_uv: float
    blackening_horizon: float
    scalar_uv: float
    warp_uv: float
    minimum_blackening_interior: float
    horizon_blackening_derivative: float
    phi_h_target_relative_error: float
    eta_algebraic_consistency_error: float

    @property
    def maximum_evaluated_equation_residual(self) -> float:
        """Maximum over the four independently evaluated equations."""

        return max(
            self.warp_equation,
            self.blackening_equation,
            self.scalar_equation,
            self.maxwell_equation,
        )

    @property
    def maximum_boundary_residual(self) -> float:
        return max(
            self.horizon_constraint,
            self.horizon_scalar_equation,
            self.blackening_uv,
            self.blackening_horizon,
            self.scalar_uv,
            self.warp_uv,
            self.electric_potential_horizon,
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "warp_equation": self.warp_equation,
            "blackening_equation": self.blackening_equation,
            "scalar_equation": self.scalar_equation,
            "maxwell_equation": self.maxwell_equation,
            "gauss_flux_relative_drift": self.gauss_flux_relative_drift,
            "electric_potential_horizon": self.electric_potential_horizon,
            "maximum_electric_potential_z_derivative": (
                self.maximum_electric_potential_z_derivative
            ),
            "reconstructed_chemical_potential": (
                self.reconstructed_chemical_potential
            ),
            "chemical_potential_reconstruction_relative_error": (
                self.chemical_potential_reconstruction_relative_error
            ),
            "uv_minus_phi2": self.uv_minus_phi2,
            "uv_minus_phi2_q_over_2_relative_error": (
                self.uv_minus_phi2_q_over_2_relative_error
            ),
            "constraint": self.constraint,
            "horizon_constraint": self.horizon_constraint,
            "horizon_scalar_equation": self.horizon_scalar_equation,
            "blackening_uv": self.blackening_uv,
            "blackening_horizon": self.blackening_horizon,
            "scalar_uv": self.scalar_uv,
            "warp_uv": self.warp_uv,
            "minimum_blackening_interior": self.minimum_blackening_interior,
            "horizon_blackening_derivative": self.horizon_blackening_derivative,
            "phi_h_target_relative_error": self.phi_h_target_relative_error,
            "eta_algebraic_consistency_error": (
                self.eta_algebraic_consistency_error
            ),
            "maximum_evaluated_equation_residual": (
                self.maximum_evaluated_equation_residual
            ),
            "maximum_boundary_residual": self.maximum_boundary_residual,
        }


def solve_charged_profile(
    phi_h: Real,
    eta: Real,
    degree: int,
    *,
    seed: Optional[ChargedProfile] = None,
    config: Optional[ChargedSolverConfig] = None,
) -> ChargedProfile:
    """Solve one charged profile at physical ``(phi_H, eta)``.

    With no charged seed, a neutral Phase 5A profile is used only as an
    initial guess and charge is turned on in deterministic bounded steps.  The
    residual solved here is always the separate fully backreacted charged
    system.
    """

    resolved_phi_h = _validate_interval(
        "phi_h", phi_h, SOURCE_PHI_H_INTERVAL
    )
    resolved_eta = _validate_interval("eta", eta, SOURCE_ETA_INTERVAL)
    _validate_integer("degree", degree, minimum=12)
    resolved_degree = int(degree)
    resolved_config = ChargedSolverConfig() if config is None else config

    if seed is not None:
        return _solve_charged_once(
            resolved_phi_h,
            resolved_eta,
            resolved_degree,
            seed=seed,
            neutral_seed=None,
            config=resolved_config,
        )

    neutral_seed = _neutral_initial_profile(
        resolved_phi_h, resolved_degree, resolved_config
    )
    current = _solve_charged_once(
        resolved_phi_h,
        0.0,
        resolved_degree,
        seed=None,
        neutral_seed=neutral_seed,
        config=resolved_config,
    )
    if resolved_eta == 0.0:
        return current
    steps = max(1, int(math.ceil(resolved_eta / resolved_config.maximum_eta_step)))
    for value in np.linspace(0.0, resolved_eta, steps + 1, dtype=float)[1:]:
        current = _solve_charged_once(
            resolved_phi_h,
            float(value),
            resolved_degree,
            seed=current,
            neutral_seed=None,
            config=resolved_config,
        )
    return current


def solve_explicit_maxwell_profile(
    reference: ChargedProfile,
    *,
    degree: Optional[int] = None,
    config: Optional[ChargedSolverConfig] = None,
) -> ExplicitMaxwellProfile:
    """Simultaneously solve the geometry, scalar, and Maxwell potential.

    This secondary verification route does not replace the flux-reduced
    primary solver.  ``reference`` supplies only the deterministic initial
    guess and the frozen physical targets ``(phi_H, eta)``.  The nonlinear
    unknown vector is ``(h, c, p, e, log(x_H), mu)`` and the returned solution
    collocates all four second-order field equations together.
    """

    if not isinstance(reference, ChargedProfile):
        raise ValueError("reference must be a ChargedProfile")
    resolved_degree = reference.degree if degree is None else degree
    _validate_integer("degree", resolved_degree, minimum=12)
    resolved_config = ChargedSolverConfig() if config is None else config
    return _solve_explicit_maxwell_once(
        reference,
        int(resolved_degree),
        resolved_config,
    )


def explicit_maxwell_point_from_profile(
    profile: ExplicitMaxwellProfile,
    *,
    quadrature_order: int = 512,
) -> ChargedPoint:
    """Extract thermodynamics using the explicitly solved UV potential."""

    flux_point = charged_point_from_profile(
        profile.as_flux_profile(), quadrature_order=quadrature_order
    )
    maxwell_integral = (
        profile.chemical_potential / profile.q
        if profile.q > 0.0
        else flux_point.maxwell_integral
    )
    return ChargedPoint(
        degree=profile.degree,
        x_h=profile.x_h,
        phi_h=profile.phi_h,
        eta=profile.eta,
        q=profile.q,
        temperature=flux_point.temperature,
        chemical_potential=profile.chemical_potential,
        entropy=flux_point.entropy,
        density=0.5 * profile.q,
        temperature_mev=flux_point.temperature_mev,
        chemical_potential_mev=(
            LAMBDA_MU_MEV * profile.chemical_potential
        ),
        entropy_mev3=flux_point.entropy_mev3,
        density_mev3=LAMBDA_RHO_MEV3 * 0.5 * profile.q,
        maxwell_integral=maxwell_integral,
    )


def explicit_noether_diagnostics(
    profile: ExplicitMaxwellProfile,
) -> Dict[str, float]:
    """Evaluate the signed conserved Noether charge in the stable bulk.

    With ``v=(z/z_H)^2`` and the inward conformal orientation, the frozen
    charge is

    ``Q_N = exp(3 A) h_z + q Phi = -2 kappa_5^2 T s``.

    Here ``kappa_5=1``.  The radial drift is normalized to the signed horizon
    value and evaluated on the fixed interior interval ``0.1 <= v <= 0.98``.
    The excluded asymptotic layer is not needed to test conservation and
    would amplify roundoff when differentiating ``h=1+O(v^2)`` by ``1/v``.
    The horizon is checked separately against the thermodynamic identity.
    """

    if not isinstance(profile, ExplicitMaxwellProfile):
        raise ValueError("profile must be an ExplicitMaxwellProfile")

    v = np.geomspace(0.1, 0.98, 80)
    nu = DGR_POTENTIAL.uv_power
    u = np.power(v, 0.5 * nu)
    h_interpolator, c_interpolator, _, e_interpolator = (
        profile.interpolators()
    )
    h_u = np.asarray(h_interpolator.derivative(u, der=1), dtype=float)
    c = np.asarray(c_interpolator(u), dtype=float)
    efield = np.asarray(e_interpolator(u), dtype=float)
    z = profile.z_h * np.sqrt(v)
    x = profile.x_h * u
    a = x**2 * c
    warp = -np.log(z) + a
    h_z = nu * u * h_u / z
    electric_potential = profile.chemical_potential - v * efield
    noether = (
        np.exp(3.0 * warp) * h_z + profile.q * electric_potential
    )

    horizon_h_u = float(h_interpolator.derivative(1.0, der=1))
    horizon_noether = (
        math.exp(3.0 * profile.A_h)
        * nu
        * horizon_h_u
        / profile.z_h
    )
    point = explicit_maxwell_point_from_profile(profile)
    thermodynamic_horizon = -2.0 * point.temperature * point.entropy
    drift_scale = max(abs(horizon_noether), 1.0e-300)
    identity_scale = max(
        abs(horizon_noether), abs(thermodynamic_horizon), 1.0e-300
    )
    return {
        "noether_charge_relative_drift": float(
            np.max(np.abs(noether - horizon_noether)) / drift_scale
        ),
        "noether_horizon_identity_relative_error": float(
            abs(horizon_noether - thermodynamic_horizon) / identity_scale
        ),
        "noether_charge_horizon": float(horizon_noether),
        "noether_thermodynamic_horizon": float(thermodynamic_horizon),
        "noether_interior_v_minimum": 0.1,
        "noether_interior_v_maximum": 0.98,
    }


def explicit_maxwell_diagnostics(
    profile: ExplicitMaxwellProfile,
    reference: ChargedProfile,
    *,
    oversampling_factor: int = 2,
) -> Dict[str, float]:
    """Compare the explicit-``Phi`` route with the flux-reduced route."""

    _validate_integer("oversampling_factor", oversampling_factor, minimum=2)
    if (
        profile.target_phi_h != reference.target_phi_h
        or profile.target_eta != reference.target_eta
    ):
        raise ValueError("profile and reference must share physical targets")

    grid = chebyshev_lobatto_grid(
        int(oversampling_factor) * max(profile.degree, reference.degree),
        0.0,
        1.0,
    )
    u = grid.nodes
    explicit_interpolators = profile.interpolators()
    reference_interpolators = reference.interpolators()
    h = np.asarray(explicit_interpolators[0](u), dtype=float)
    c = np.asarray(explicit_interpolators[1](u), dtype=float)
    pfield = np.asarray(explicit_interpolators[2](u), dtype=float)
    efield = np.asarray(explicit_interpolators[3](u), dtype=float)
    hu = np.asarray(explicit_interpolators[0].derivative(u, der=1), dtype=float)
    huu = np.asarray(
        explicit_interpolators[0].derivative(u, der=2), dtype=float
    )
    eu = np.asarray(explicit_interpolators[3].derivative(u, der=1), dtype=float)
    euu = np.asarray(
        explicit_interpolators[3].derivative(u, der=2), dtype=float
    )
    cu = np.asarray(explicit_interpolators[1].derivative(u, der=1), dtype=float)
    cuu = np.asarray(
        explicit_interpolators[1].derivative(u, der=2), dtype=float
    )
    pu = np.asarray(explicit_interpolators[2].derivative(u, der=1), dtype=float)
    puu = np.asarray(
        explicit_interpolators[2].derivative(u, der=2), dtype=float
    )
    warp, blackening, scalar, maxwell, constraint = (
        _explicit_maxwell_physical_equations(
        profile.x_h,
        u,
        h,
        hu,
        huu,
        c,
        cu,
        cuu,
        pfield,
        pu,
        puu,
        efield,
        eu,
        euu,
        )
    )

    nu = DGR_POTENTIAL.uv_power
    x = profile.x_h * u
    a = x**2 * c
    phi = x * pfield
    kfield = 2.0 * efield + nu * u * eu
    flux = (
        np.asarray(gauge_coupling(phi), dtype=float)
        * np.exp(a)
        * kfield
        / profile.z_h**2
    )
    flux_scale = max(abs(profile.q), 1.0)
    gauss_drift = float(np.max(np.abs(flux - profile.q)) / flux_scale)

    explicit_point = explicit_maxwell_point_from_profile(profile)
    reference_point = charged_point_from_profile(reference)
    reference_electric = _electric_coefficient_seed(reference, u)
    reference_mu = float(reference_electric[-1])

    def relative_error(left: float, right: float) -> float:
        scale = max(abs(left), abs(right))
        if scale < 1.0e-14:
            return abs(left - right)
        return abs(left - right) / scale

    field_errors = []
    for explicit_values, interpolator in zip(
        (h, c, pfield), reference_interpolators
    ):
        reference_values = np.asarray(interpolator(u), dtype=float)
        field_errors.append(
            float(
                np.max(np.abs(explicit_values - reference_values))
                / (1.0 + float(np.max(np.abs(reference_values))))
            )
        )
    electric_error = float(
        np.max(np.abs(efield - reference_electric))
        / (1.0 + float(np.max(np.abs(reference_electric))))
    )
    radial_power = np.power(u, 2.0 / nu)
    explicit_potential = profile.chemical_potential - radial_power * efield
    reference_potential = reference_mu - radial_power * reference_electric
    electric_potential_error = float(
        np.max(np.abs(explicit_potential - reference_potential))
        / (1.0 + float(np.max(np.abs(reference_potential))))
    )
    horizon_potential = abs(
        profile.chemical_potential - profile.electric_coefficient[-1]
    )
    eta_error = relative_error(profile.eta, profile.target_eta)
    warp_equation = float(np.max(np.abs(warp[1:])))
    blackening_equation = float(np.max(np.abs(blackening[1:-1])))
    scalar_equation = float(np.max(np.abs(scalar[1:])))
    maxwell_equation = float(np.max(np.abs(maxwell[1:-1])))
    maximum_equation = max(
        warp_equation,
        blackening_equation,
        scalar_equation,
        maxwell_equation,
    )
    horizon_scalar = float(abs(scalar[-1]))
    horizon_constraint = float(abs(constraint[-1]))
    boundary_residuals = (
        abs(h[0] - 1.0),
        abs(h[-1]),
        abs(c[0] - _analytic_warp_uv()),
        abs(pfield[0] - 1.0),
        horizon_potential,
        horizon_scalar,
        horizon_constraint,
        relative_error(profile.phi_h, profile.target_phi_h),
        eta_error,
    )
    noether = explicit_noether_diagnostics(profile)
    return {
        "maximum_background_field_difference": max(field_errors),
        "electric_coefficient_difference": electric_error,
        "electric_potential_difference": electric_potential_error,
        "x_h_relative_difference": relative_error(
            profile.x_h, reference.x_h
        ),
        "q_relative_difference": relative_error(profile.q, reference.q),
        "temperature_relative_difference": relative_error(
            explicit_point.temperature, reference_point.temperature
        ),
        "chemical_potential_relative_difference": relative_error(
            explicit_point.chemical_potential,
            reference_point.chemical_potential,
        ),
        "entropy_relative_difference": relative_error(
            explicit_point.entropy, reference_point.entropy
        ),
        "density_relative_difference": relative_error(
            explicit_point.density, reference_point.density
        ),
        "reference_mu_reconstruction_relative_error": relative_error(
            reference_mu, reference_point.chemical_potential
        ),
        "warp_equation": warp_equation,
        "blackening_equation": blackening_equation,
        "scalar_equation": scalar_equation,
        "maximum_maxwell_equation_residual": maxwell_equation,
        "maximum_evaluated_equation_residual": maximum_equation,
        "constraint": float(np.max(np.abs(constraint[1:]))),
        "horizon_constraint": horizon_constraint,
        "horizon_scalar_equation": horizon_scalar,
        "blackening_uv": float(abs(h[0] - 1.0)),
        "blackening_horizon": float(abs(h[-1])),
        "scalar_uv": float(abs(pfield[0] - 1.0)),
        "warp_uv": float(abs(c[0] - _analytic_warp_uv())),
        "gauss_flux_relative_drift": gauss_drift,
        "electric_potential_horizon": float(horizon_potential),
        "eta_relative_error": float(eta_error),
        "phi_h_target_relative_error": relative_error(
            profile.phi_h, profile.target_phi_h
        ),
        "maximum_boundary_residual": float(max(boundary_residuals)),
        "minimum_blackening_interior": float(np.min(h[:-1])),
        "horizon_blackening_derivative": float(hu[-1]),
        **noether,
    }


def charged_point_from_profile(
    profile: ChargedProfile,
    *,
    quadrature_order: int = 512,
) -> ChargedPoint:
    """Extract ``(T, mu, s, rho_canonical)`` with the DGR dictionary."""

    _validate_integer("quadrature_order", quadrature_order, minimum=32)
    h_interpolator, c_interpolator, p_interpolator = profile.interpolators()
    h_u_h = float(h_interpolator.derivative(1.0, der=1))
    regularity_u = np.linspace(0.0, 1.0, 4 * profile.degree + 1, dtype=float)
    regularity_h = np.asarray(h_interpolator(regularity_u), dtype=float)
    if not np.all(np.isfinite(regularity_h)):
        raise RuntimeError("charged blackening profile must remain finite")
    if np.any(regularity_h[:-1] <= 0.0):
        raise RuntimeError(
            "charged blackening profile must remain positive before the horizon"
        )
    if not math.isfinite(h_u_h) or h_u_h >= -1.0e-10:
        raise RuntimeError(
            "charged horizon must be simple with inward derivative h_u(1) < 0"
        )
    temperature = -DGR_POTENTIAL.uv_power * h_u_h / profile.z_h / (
        4.0 * math.pi
    )
    entropy = 2.0 * math.pi * math.exp(3.0 * profile.A_h)

    nodes, weights = np.polynomial.legendre.leggauss(int(quadrature_order))
    u = 0.5 * (nodes + 1.0)
    weights = 0.5 * weights
    c = np.asarray(c_interpolator(u), dtype=float)
    pfield = np.asarray(p_interpolator(u), dtype=float)
    x = profile.x_h * u
    phi = x * pfield
    a = x**2 * c
    power = 2.0 / DGR_POTENTIAL.uv_power - 1.0
    integrand = (
        profile.z_h**2
        / DGR_POTENTIAL.uv_power
        * u**power
        * np.exp(-a)
        / gauge_coupling(phi)
    )
    maxwell_integral = float(np.dot(weights, integrand))
    chemical_potential = profile.q * maxwell_integral
    density = 0.5 * profile.q
    values = (temperature, entropy, maxwell_integral, chemical_potential, density)
    if not all(math.isfinite(value) and value >= 0.0 for value in values):
        raise RuntimeError("charged thermodynamics must be finite and nonnegative")
    if temperature <= 0.0 or entropy <= 0.0 or maxwell_integral <= 0.0:
        raise RuntimeError(
            "charged temperature, entropy, and integral must be positive"
        )
    return ChargedPoint(
        degree=profile.degree,
        x_h=profile.x_h,
        phi_h=profile.phi_h,
        eta=profile.eta,
        q=profile.q,
        temperature=temperature,
        chemical_potential=chemical_potential,
        entropy=entropy,
        density=density,
        temperature_mev=LAMBDA_T_MEV * temperature,
        chemical_potential_mev=LAMBDA_MU_MEV * chemical_potential,
        entropy_mev3=LAMBDA_S_MEV3 * entropy,
        density_mev3=LAMBDA_RHO_MEV3 * density,
        maxwell_integral=maxwell_integral,
    )


def charged_equation_diagnostics(
    profile: ChargedProfile,
    *,
    oversampling_factor: int = 2,
) -> ChargedEquationDiagnostics:
    """Evaluate charged equations and constraint on an independent dense grid."""

    _validate_integer("oversampling_factor", oversampling_factor, minimum=2)
    grid = chebyshev_lobatto_grid(
        int(oversampling_factor) * profile.degree, 0.0, 1.0
    )
    u = grid.nodes
    evaluated = []
    for interpolator in profile.interpolators():
        values = np.asarray(interpolator(u), dtype=float)
        first = np.asarray(interpolator.derivative(u, der=1), dtype=float)
        second = np.asarray(interpolator.derivative(u, der=2), dtype=float)
        evaluated.append((values, first, second))
    h, hu, huu = evaluated[0]
    c, cu, cuu = evaluated[1]
    pfield, pu, puu = evaluated[2]
    warp, blackening, scalar, constraint = _charged_equations(
        profile.x_h,
        profile.target_eta,
        u,
        h,
        hu,
        huu,
        c,
        cu,
        cuu,
        pfield,
        pu,
        puu,
        scaled=False,
    )
    expected_warp_uv = _analytic_warp_uv()
    target_phi_error = abs(profile.phi_h - profile.target_phi_h) / max(
        abs(profile.target_phi_h), 1.0e-300
    )
    eta_algebraic_error = abs(profile.eta - profile.target_eta) / max(
        abs(profile.target_eta), 1.0e-300
    )
    maxwell = _reconstructed_maxwell_diagnostics(profile)
    return ChargedEquationDiagnostics(
        warp_equation=float(np.max(np.abs(warp[1:]))),
        blackening_equation=float(np.max(np.abs(blackening[1:-1]))),
        scalar_equation=float(np.max(np.abs(scalar[1:]))),
        maxwell_equation=maxwell["maxwell_equation"],
        gauss_flux_relative_drift=maxwell["gauss_flux_relative_drift"],
        electric_potential_horizon=maxwell["electric_potential_horizon"],
        maximum_electric_potential_z_derivative=maxwell[
            "maximum_electric_potential_z_derivative"
        ],
        reconstructed_chemical_potential=maxwell[
            "reconstructed_chemical_potential"
        ],
        chemical_potential_reconstruction_relative_error=maxwell[
            "chemical_potential_reconstruction_relative_error"
        ],
        uv_minus_phi2=maxwell["uv_minus_phi2"],
        uv_minus_phi2_q_over_2_relative_error=maxwell[
            "uv_minus_phi2_q_over_2_relative_error"
        ],
        constraint=float(np.max(np.abs(constraint[1:]))),
        horizon_constraint=float(abs(constraint[-1])),
        horizon_scalar_equation=float(abs(scalar[-1])),
        blackening_uv=float(abs(h[0] - 1.0)),
        blackening_horizon=float(abs(h[-1])),
        scalar_uv=float(abs(pfield[0] - 1.0)),
        warp_uv=float(abs(c[0] - expected_warp_uv)),
        minimum_blackening_interior=float(np.min(h[:-1])),
        horizon_blackening_derivative=float(hu[-1]),
        phi_h_target_relative_error=float(target_phi_error),
        eta_algebraic_consistency_error=float(eta_algebraic_error),
    )


def _reconstructed_maxwell_diagnostics(
    profile: ChargedProfile,
) -> Dict[str, float]:
    """Reconstruct ``Phi`` and check Maxwell flux without changing the solve.

    In source-normalized conformal coordinates,

    ``Phi_u = -(q z_H^2/nu) u^(2/nu-1) exp(-a)/f(phi)``.

    ``Phi`` is integrated from its regular horizon value and then
    differentiated locally in ``v=(z/z_H)^2``.  The latter derivative, rather
    than the first-integral right-hand side, is used to evaluate Gauss flux.
    """

    if profile.q == 0.0:
        return {
            "maxwell_equation": 0.0,
            "gauss_flux_relative_drift": 0.0,
            "electric_potential_horizon": 0.0,
            "maximum_electric_potential_z_derivative": 0.0,
            "reconstructed_chemical_potential": 0.0,
            "chemical_potential_reconstruction_relative_error": 0.0,
            "uv_minus_phi2": 0.0,
            "uv_minus_phi2_q_over_2_relative_error": 0.0,
        }

    _, c_interpolator, p_interpolator = profile.interpolators()
    nu = DGR_POTENTIAL.uv_power
    power = 2.0 / nu - 1.0
    z_h_squared = profile.z_h**2

    def rhs(u: float, _state: NDArray[np.float64]) -> Tuple[float]:
        if u <= 0.0:
            return (0.0,)
        x = profile.x_h * u
        c = float(c_interpolator(u))
        pfield = float(p_interpolator(u))
        a = x**2 * c
        phi = x * pfield
        return (
            -profile.q
            * z_h_squared
            / nu
            * u**power
            * math.exp(-a)
            / float(gauge_coupling(phi)),
        )

    answer = solve_ivp(
        rhs,
        (1.0, 0.0),
        (0.0,),
        method="DOP853",
        rtol=2.0e-12,
        atol=2.0e-14,
        dense_output=True,
    )
    if not answer.success or answer.sol is None:
        raise RuntimeError(
            f"independent Maxwell reconstruction failed: {answer.message}"
        )

    reconstructed_mu = float(answer.y[0, -1])
    reference_mu = charged_point_from_profile(profile).chemical_potential
    mu_relative_error = abs(reconstructed_mu - reference_mu) / max(
        abs(reconstructed_mu), abs(reference_mu), 1.0e-300
    )

    v_samples = np.geomspace(1.0e-4, 0.98, 80)
    flux_values = []
    z_derivatives = []
    for v in v_samples:
        half_width = min(2.0e-4, 0.08 * v, 0.08 * (1.0 - v))
        local_coordinate = np.linspace(-1.0, 1.0, 11)
        v_local = v + half_width * local_coordinate
        u_local = np.power(v_local, 0.5 * nu)
        phi_local = np.asarray(answer.sol(u_local)[0], dtype=float)
        coefficients = np.polynomial.polynomial.polyfit(
            local_coordinate, phi_local, 6
        )
        dphi_dv = float(coefficients[1] / half_width)

        u = float(v ** (0.5 * nu))
        x = profile.x_h * u
        c = float(c_interpolator(u))
        pfield = float(p_interpolator(u))
        a = x**2 * c
        phi = x * pfield
        flux_values.append(
            2.0
            * float(gauge_coupling(phi))
            * math.exp(a)
            * dphi_dv
            / z_h_squared
        )
        z_derivatives.append(2.0 * math.sqrt(v) * dphi_dv / profile.z_h)

    flux = np.asarray(flux_values, dtype=float)
    normalized_flux = flux / (-profile.q)
    maxwell_equation = float(np.max(np.abs(normalized_flux - 1.0)))
    gauss_drift = float(
        (np.max(flux) - np.min(flux))
        / max(abs(float(np.mean(flux))), 1.0e-300)
    )

    # Extract -(Phi-mu)/z^2 without subtracting nearly equal UV values.  The
    # weighted integral's intercept is fitted freely; q/2 is only compared
    # after the fit and is not supplied as a density normalization.
    jacobi_nodes, jacobi_weights = roots_jacobi(192, 0.0, power)
    s = 0.5 * (jacobi_nodes + 1.0)
    weighted_scale = 2.0 ** (-(power + 1.0))

    def uv_ratio(x: float) -> float:
        local_x = x * s
        local_u = local_x / profile.x_h
        c = np.asarray(c_interpolator(local_u), dtype=float)
        pfield = np.asarray(p_interpolator(local_u), dtype=float)
        a = local_x**2 * c
        phi = local_x * pfield
        regular = np.exp(-a) / np.asarray(gauge_coupling(phi), dtype=float)
        integral = weighted_scale * float(np.dot(jacobi_weights, regular))
        return profile.q / nu * integral

    u_values = np.geomspace(5.0e-7, 5.0e-3, 40)
    x_values = profile.x_h * u_values
    ratios = np.asarray([uv_ratio(float(x)) for x in x_values], dtype=float)
    coefficients = np.polynomial.polynomial.polyfit(
        x_values / x_values[-1], ratios, 6
    )
    uv_minus_phi2 = float(coefficients[0])
    q_over_two = 0.5 * profile.q
    uv_relative_error = abs(uv_minus_phi2 - q_over_two) / max(
        abs(uv_minus_phi2), abs(q_over_two), 1.0e-300
    )

    return {
        "maxwell_equation": maxwell_equation,
        "gauss_flux_relative_drift": gauss_drift,
        "electric_potential_horizon": abs(float(answer.sol(1.0)[0])),
        "maximum_electric_potential_z_derivative": float(
            np.max(np.asarray(z_derivatives, dtype=float))
        ),
        "reconstructed_chemical_potential": reconstructed_mu,
        "chemical_potential_reconstruction_relative_error": float(
            mu_relative_error
        ),
        "uv_minus_phi2": uv_minus_phi2,
        "uv_minus_phi2_q_over_2_relative_error": float(uv_relative_error),
    }


def _solve_explicit_maxwell_once(
    reference: ChargedProfile,
    degree: int,
    config: ChargedSolverConfig,
) -> ExplicitMaxwellProfile:
    grid = chebyshev_lobatto_grid(degree, 0.0, 1.0)
    u = grid.nodes
    d1 = grid.first_derivative
    d2 = grid.second_derivative
    size = grid.size
    reference_interpolators = reference.interpolators()
    h = np.asarray(reference_interpolators[0](u), dtype=float)
    c = np.asarray(reference_interpolators[1](u), dtype=float)
    pfield = np.asarray(reference_interpolators[2](u), dtype=float)
    efield = _electric_coefficient_seed(reference, u)
    log_x_h = math.log(reference.x_h)
    chemical_potential = float(efield[-1])
    initial = np.concatenate(
        (
            h,
            c,
            pfield,
            efield,
            np.asarray([log_x_h, chemical_potential]),
        )
    )

    def residual(vector: NDArray[np.float64]) -> NDArray[np.float64]:
        values = np.asarray(vector, dtype=float)
        fields = values[:-2].reshape(4, size)
        raw_log_x_h = float(values[-2])
        mu = float(values[-1])
        if not math.isfinite(raw_log_x_h) or not math.isfinite(mu):
            return np.full(4 * size + 2, 1.0e6, dtype=float)
        bounded_log_x_h = float(
            np.clip(raw_log_x_h, *LOG_X_H_SOLVER_INTERVAL)
        )
        resolved_x_h = math.exp(bounded_log_x_h)
        log_x_h_boundary_violation = raw_log_x_h - bounded_log_x_h
        h_values, c_values, p_values, e_values = fields
        warp, blackening, scalar, maxwell = (
            _scaled_explicit_maxwell_collocation_equations(
                resolved_x_h,
                u,
                h_values,
                d1 @ h_values,
                d2 @ h_values,
                c_values,
                d1 @ c_values,
                d2 @ c_values,
                p_values,
                d1 @ p_values,
                d2 @ p_values,
                e_values,
                d1 @ e_values,
                d2 @ e_values,
            )
        )
        warp = warp.copy()
        blackening = blackening.copy()
        scalar = scalar.copy()
        maxwell = maxwell.copy()
        blackening[0] = h_values[0] - 1.0
        blackening[-1] = h_values[-1]
        warp[0] = c_values[0] - _analytic_warp_uv()
        scalar[0] = p_values[0] - 1.0

        nu = DGR_POTENTIAL.uv_power
        e_u = d1 @ e_values
        kfield = 2.0 * e_values + nu * u * e_u
        uv_terms = (
            (2.0 + nu) * e_u[0],
            2.0
            * float(gauge_log_derivative(0.0))
            * resolved_x_h
            * p_values[0]
            * e_values[0],
        )
        maxwell[0] = sum(uv_terms) / (
            1.0 + sum(abs(term) for term in uv_terms)
        )
        q_target = _charge_from_horizon(
            resolved_x_h,
            reference.target_eta,
            c_values[-1],
            p_values[-1],
        )
        z_h = math.exp(math.log(resolved_x_h) / nu)
        phi_h = resolved_x_h * p_values[-1]
        a_h = resolved_x_h**2 * c_values[-1]
        k_target = (
            q_target
            * z_h**2
            * math.exp(-a_h)
            / float(gauge_coupling(phi_h))
        )
        maxwell[-1] = (kfield[-1] - k_target) / (
            1.0 + abs(kfield[-1]) + abs(k_target)
        )
        target = (
            (resolved_x_h * p_values[-1] - reference.target_phi_h)
            / (1.0 + abs(reference.target_phi_h))
            + log_x_h_boundary_violation
        )
        electric_horizon = (mu - e_values[-1]) / (
            1.0 + abs(mu) + abs(e_values[-1])
        )
        return np.concatenate(
            (
                blackening,
                warp,
                scalar,
                maxwell,
                np.asarray([target, electric_horizon]),
            )
        )

    root_result = root(
        residual,
        initial,
        method="hybr",
        options={
            "xtol": config.root_tolerance,
            "maxfev": config.maximum_evaluations_factor * len(initial),
        },
    )
    root_vector = np.asarray(root_result.x, dtype=float)
    root_residual = float(np.max(np.abs(residual(root_vector))))
    polish_applied = bool(
        not root_result.success
        or root_residual > DEFAULT_COLLOCATION_TOLERANCE
    )
    if polish_applied:
        polish_result = least_squares(
            residual,
            root_vector,
            method="trf",
            ftol=config.polish_tolerance,
            xtol=config.polish_tolerance,
            gtol=config.polish_tolerance,
            max_nfev=config.polish_maximum_evaluations,
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
    h_final, c_final, p_final, e_final = final_vector[:-2].reshape(4, size)
    final_log_x_h = float(final_vector[-2])
    mu_final = float(final_vector[-1])
    if not (
        math.isfinite(final_log_x_h)
        and LOG_X_H_SOLVER_INTERVAL[0]
        < final_log_x_h
        < LOG_X_H_SOLVER_INTERVAL[1]
    ):
        raise RuntimeError(
            "explicit-Maxwell solve contacted the log(x_h) solver boundary"
        )
    x_h_final = math.exp(final_log_x_h)
    nu = DGR_POTENTIAL.uv_power
    z_h_final = math.exp(final_log_x_h / nu)
    phi_h_final = x_h_final * p_final[-1]
    a_h_final = x_h_final**2 * c_final[-1]
    e_u_final = d1 @ e_final
    k_h_final = 2.0 * e_final[-1] + nu * e_u_final[-1]
    if reference.target_eta == 0.0:
        # The gauge-fixed neutral Maxwell solution is exactly Phi=e=q=0.
        # Some SciPy versions leave signed roundoff of order 1e-40 in the
        # otherwise null electric sector; canonicalize that mathematical zero
        # before enforcing the physical nonnegativity check.
        q_final = 0.0
        mu_final = 0.0
        e_final = np.zeros_like(e_final)
    else:
        q_final = (
            float(gauge_coupling(phi_h_final))
            * math.exp(a_h_final)
            * k_h_final
            / z_h_final**2
        )
    nonlinear = ChargedNonlinearDiagnostics(
        root_success=bool(root_result.success),
        root_message=str(root_result.message),
        root_function_evaluations=int(root_result.nfev),
        root_scaled_residual=root_residual,
        polish_applied=polish_applied,
        polish_success=polish_success,
        polish_message=polish_message,
        polish_function_evaluations=polish_evaluations,
        final_scaled_residual=final_residual,
    )
    if not nonlinear.success or final_residual > DEFAULT_COLLOCATION_TOLERANCE:
        raise RuntimeError(
            "explicit-Maxwell nonlinear solve failed the local convergence "
            f"gate: success={nonlinear.success}, residual={final_residual:.3e}"
        )
    h_u_final = d1 @ h_final
    if np.any(~np.isfinite(h_final)) or np.any(h_final[:-1] <= 0.0):
        raise RuntimeError(
            "explicit-Maxwell blackening must remain finite and positive"
        )
    if not math.isfinite(float(h_u_final[-1])) or h_u_final[-1] >= -1.0e-10:
        raise RuntimeError(
            "explicit-Maxwell horizon must be simple with h_u(1) < 0"
        )
    if not all(math.isfinite(value) for value in (q_final, mu_final)):
        raise RuntimeError("explicit-Maxwell charge and potential must be finite")
    if q_final < 0.0 or mu_final < 0.0:
        raise RuntimeError(
            "explicit-Maxwell charge and chemical potential must be nonnegative"
        )
    return ExplicitMaxwellProfile(
        degree=degree,
        target_phi_h=reference.target_phi_h,
        target_eta=reference.target_eta,
        x_h=x_h_final,
        q=float(q_final),
        chemical_potential=mu_final,
        u=np.asarray(u, dtype=float),
        blackening=np.asarray(h_final, dtype=float),
        warp_factor=np.asarray(c_final, dtype=float),
        scalar_factor=np.asarray(p_final, dtype=float),
        electric_coefficient=np.asarray(e_final, dtype=float),
        nonlinear=nonlinear,
    )


def _electric_coefficient_seed(
    reference: ChargedProfile,
    u: NDArray[np.float64],
) -> NDArray[np.float64]:
    """Return a regular quadrature seed for ``Phi=mu-u**(2/nu)e``."""

    resolved_u = np.asarray(u, dtype=float)
    if reference.q == 0.0:
        return np.zeros_like(resolved_u)
    _, c_interpolator, p_interpolator = reference.interpolators()
    nu = DGR_POTENTIAL.uv_power
    power = 2.0 / nu - 1.0
    nodes, weights = roots_jacobi(128, 0.0, power)
    s = 0.5 * (nodes + 1.0)
    scale = 2.0 ** (-(power + 1.0))
    result = []
    for value in resolved_u:
        local_u = value * s
        x = reference.x_h * local_u
        c = np.asarray(c_interpolator(local_u), dtype=float)
        pfield = np.asarray(p_interpolator(local_u), dtype=float)
        a = x**2 * c
        phi = x * pfield
        regular = np.exp(-a) / np.asarray(gauge_coupling(phi), dtype=float)
        integral = scale * float(np.dot(weights, regular))
        result.append(reference.q * reference.z_h**2 / nu * integral)
    return np.asarray(result, dtype=float)


def _factorized_maxwell_equation(
    x_h: float,
    u: NDArray[np.float64],
    c: NDArray[np.float64],
    cu: NDArray[np.float64],
    pfield: NDArray[np.float64],
    pu: NDArray[np.float64],
    efield: NDArray[np.float64],
    eu: NDArray[np.float64],
    euu: NDArray[np.float64],
    *,
    scaled: bool,
) -> NDArray[np.float64]:
    """Return the second-order Maxwell EOM after removing its UV power."""

    nu = DGR_POTENTIAL.uv_power
    x = x_h * u
    phi = x * pfield
    au = x_h**2 * (2.0 * u * c + u**2 * cu)
    phiu = x_h * (pfield + u * pu)
    alpha = -1.0 + nu * u * au
    beta = nu * u * phiu
    kfield = 2.0 * efield + nu * u * eu
    kfield_u = (2.0 + nu) * eu + nu * u * euu
    terms = (
        nu * u * kfield_u,
        (
            alpha
            + 1.0
            + np.asarray(gauge_log_derivative(phi), dtype=float) * beta
        )
        * kfield,
    )
    return (_scaled_sum if scaled else _unscaled_sum)(terms)


def _explicit_maxwell_physical_equations(
    x_h: float,
    u: NDArray[np.float64],
    h: NDArray[np.float64],
    hu: NDArray[np.float64],
    huu: NDArray[np.float64],
    c: NDArray[np.float64],
    cu: NDArray[np.float64],
    cuu: NDArray[np.float64],
    pfield: NDArray[np.float64],
    pu: NDArray[np.float64],
    puu: NDArray[np.float64],
    efield: NDArray[np.float64],
    eu: NDArray[np.float64],
    euu: NDArray[np.float64],
) -> Tuple[
    NDArray[np.float64],
    NDArray[np.float64],
    NDArray[np.float64],
    NDArray[np.float64],
    NDArray[np.float64],
]:
    """Evaluate all four EOMs and the Einstein constraint from ``Phi``."""

    nu = DGR_POTENTIAL.uv_power
    x = x_h * u
    a = x**2 * c
    au = x_h**2 * (2.0 * u * c + u**2 * cu)
    auu = x_h**2 * (2.0 * c + 4.0 * u * cu + u**2 * cuu)
    phi = x * pfield
    phiu = x_h * (pfield + u * pu)
    phiuu = x_h * (2.0 * pu + u * puu)
    alpha = -1.0 + nu * u * au
    alpha_u = nu * (au + u * auu)
    d_alpha = nu * u * alpha_u
    beta = nu * u * phiu
    beta_u = nu * (phiu + u * phiuu)
    d_beta = nu * u * beta_u
    gamma = nu * u * hu
    gamma_u = nu * (hu + u * huu)
    d_gamma = nu * u * gamma_u
    potential = np.asarray(DGR_POTENTIAL.potential(phi), dtype=float)
    potential_prime = np.asarray(
        DGR_POTENTIAL.first_derivative(phi), dtype=float
    )
    coupling = np.asarray(gauge_coupling(phi), dtype=float)
    coupling_log_prime = np.asarray(gauge_log_derivative(phi), dtype=float)
    radial_power = np.power(u, 2.0 / nu)
    kfield = 2.0 * efield + nu * u * eu
    charge_term = (
        coupling
        * math.exp(2.0 * math.log(x_h) / nu)
        * radial_power**3
        * np.exp(-2.0 * a)
        * kfield**2
    )
    warp = _unscaled_sum((d_alpha, -alpha, -(alpha**2), beta**2 / 6.0))
    blackening = _unscaled_sum(
        (d_gamma, -gamma, 3.0 * alpha * gamma, -charge_term)
    )
    scalar = _unscaled_sum(
        (
            h * (d_beta - beta),
            (3.0 * alpha * h + gamma) * beta,
            -np.exp(2.0 * a) * potential_prime,
            0.5 * charge_term * coupling_log_prime,
        )
    )
    maxwell = _factorized_maxwell_equation(
        x_h,
        u,
        c,
        cu,
        pfield,
        pu,
        efield,
        eu,
        euu,
        scaled=False,
    )
    constraint = _unscaled_sum(
        (
            6.0 * alpha * gamma,
            h * (24.0 * alpha**2 - beta**2),
            2.0 * np.exp(2.0 * a) * potential,
            charge_term,
        )
    )
    return warp, blackening, scalar, maxwell, constraint


def _scaled_explicit_maxwell_collocation_equations(
    x_h: float,
    u: NDArray[np.float64],
    h: NDArray[np.float64],
    hu: NDArray[np.float64],
    huu: NDArray[np.float64],
    c: NDArray[np.float64],
    cu: NDArray[np.float64],
    cuu: NDArray[np.float64],
    pfield: NDArray[np.float64],
    pu: NDArray[np.float64],
    puu: NDArray[np.float64],
    efield: NDArray[np.float64],
    eu: NDArray[np.float64],
    euu: NDArray[np.float64],
) -> Tuple[
    NDArray[np.float64],
    NDArray[np.float64],
    NDArray[np.float64],
    NDArray[np.float64],
]:
    """Return four simultaneous UV-factorized collocation equations."""

    nu = DGR_POTENTIAL.uv_power
    x = x_h * u
    a = x**2 * c
    phi = x * pfield
    a_x_scaled = 2.0 * u * c + u**2 * cu
    scalar_x = pfield + u * pu
    coupling = np.asarray(gauge_coupling(phi), dtype=float)
    coupling_log_prime = np.asarray(gauge_log_derivative(phi), dtype=float)
    potential_prime = np.asarray(
        DGR_POTENTIAL.first_derivative(phi), dtype=float
    )
    radial_power = np.power(u, 2.0 / nu)
    kfield = 2.0 * efield + nu * u * eu
    charge_term = (
        coupling
        * math.exp(2.0 * math.log(x_h) / nu)
        * radial_power**3
        * np.exp(-2.0 * a)
        * kfield**2
    )
    charge_blackening = np.divide(
        -charge_term,
        nu**2 * u,
        out=np.zeros_like(u),
        where=u != 0.0,
    )
    charge_scalar = np.divide(
        0.5 * charge_term * coupling_log_prime,
        nu**2 * x_h * u,
        out=np.zeros_like(u),
        where=u != 0.0,
    )
    blackening_terms = (
        u * huu,
        (3.0 * x_h**2 * u * a_x_scaled + 1.0 - 4.0 / nu) * hu,
        charge_blackening,
    )
    warp_terms = (
        2.0 * c + 4.0 * u * cu + u**2 * cuu,
        (1.0 + 1.0 / nu) * (2.0 * c + u * cu),
        -x_h**2 * a_x_scaled**2,
        scalar_x**2 / 6.0,
    )
    scalar_terms = (
        u * h * (2.0 * pu + u * puu),
        (
            3.0 * x_h**2 * u * h * a_x_scaled
            + (1.0 - 4.0 / nu) * h
            + u * hu
        )
        * scalar_x,
        np.divide(
            -np.exp(2.0 * a) * potential_prime,
            nu**2 * x_h * u,
            out=np.zeros_like(u),
            where=u != 0.0,
        ),
        charge_scalar,
    )
    maxwell = _factorized_maxwell_equation(
        x_h,
        u,
        c,
        cu,
        pfield,
        pu,
        efield,
        eu,
        euu,
        scaled=True,
    )
    return (
        _scaled_sum(warp_terms),
        _scaled_sum(blackening_terms),
        _scaled_sum(scalar_terms),
        maxwell,
    )


def _solve_charged_once(
    phi_h: float,
    eta: float,
    degree: int,
    *,
    seed: Optional[ChargedProfile],
    neutral_seed: Optional[CoupledProfile],
    config: ChargedSolverConfig,
) -> ChargedProfile:
    grid = chebyshev_lobatto_grid(degree, 0.0, 1.0)
    u = grid.nodes
    d1 = grid.first_derivative
    d2 = grid.second_derivative
    size = grid.size
    if seed is not None:
        h = np.asarray(seed.interpolators()[0](u), dtype=float)
        c = np.asarray(seed.interpolators()[1](u), dtype=float)
        pfield = np.asarray(seed.interpolators()[2](u), dtype=float)
        log_x_h = math.log(seed.x_h)
    elif neutral_seed is not None:
        h = _interpolate_profile_field(
            neutral_seed.u, neutral_seed.blackening, u
        )
        c = _interpolate_profile_field(
            neutral_seed.u, neutral_seed.warp_factor, u
        )
        pfield = _interpolate_profile_field(
            neutral_seed.u, neutral_seed.scalar_factor, u
        )
        log_x_h = math.log(neutral_seed.x_h)
    else:
        raise ValueError("one deterministic seed is required")
    initial = np.concatenate((h, c, pfield, np.asarray([log_x_h])))

    def residual(vector: NDArray[np.float64]) -> NDArray[np.float64]:
        values = np.asarray(vector, dtype=float)
        fields = values[:-1].reshape(3, size)
        raw_log_x_h = float(values[-1])
        if not math.isfinite(raw_log_x_h):
            return np.full(3 * size + 1, 1.0e6, dtype=float)
        bounded_log_x_h = float(
            np.clip(raw_log_x_h, *LOG_X_H_SOLVER_INTERVAL)
        )
        resolved_x_h = math.exp(bounded_log_x_h)
        log_x_h_boundary_violation = raw_log_x_h - bounded_log_x_h
        h_values, c_values, p_values = fields
        warp, blackening, scalar = _scaled_charged_collocation_equations(
            resolved_x_h,
            eta,
            u,
            h_values,
            d1 @ h_values,
            d2 @ h_values,
            c_values,
            d1 @ c_values,
            d2 @ c_values,
            p_values,
            d1 @ p_values,
            d2 @ p_values,
        )
        warp = warp.copy()
        blackening = blackening.copy()
        scalar = scalar.copy()
        blackening[0] = h_values[0] - 1.0
        blackening[-1] = h_values[-1]
        warp[0] = c_values[0] - _analytic_warp_uv()
        scalar[0] = p_values[0] - 1.0
        target = (
            (resolved_x_h * p_values[-1] - phi_h) / (1.0 + abs(phi_h))
            + log_x_h_boundary_violation
        )
        return np.concatenate((blackening, warp, scalar, np.asarray([target])))

    root_result = root(
        residual,
        initial,
        method="hybr",
        options={
            "xtol": config.root_tolerance,
            "maxfev": config.maximum_evaluations_factor * len(initial),
        },
    )
    root_vector = np.asarray(root_result.x, dtype=float)
    root_residual = float(np.max(np.abs(residual(root_vector))))
    polish_applied = bool(
        not root_result.success
        or root_residual > DEFAULT_COLLOCATION_TOLERANCE
    )
    if polish_applied:
        polish_result = least_squares(
            residual,
            root_vector,
            method="trf",
            ftol=config.polish_tolerance,
            xtol=config.polish_tolerance,
            gtol=config.polish_tolerance,
            max_nfev=config.polish_maximum_evaluations,
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
    h_final, c_final, p_final = final_vector[:-1].reshape(3, size)
    final_log_x_h = float(final_vector[-1])
    if not (
        math.isfinite(final_log_x_h)
        and LOG_X_H_SOLVER_INTERVAL[0]
        < final_log_x_h
        < LOG_X_H_SOLVER_INTERVAL[1]
    ):
        raise RuntimeError(
            "charged solve contacted the explicit log(x_h) solver boundary"
        )
    x_h_final = math.exp(final_log_x_h)
    q_final = _charge_from_horizon(x_h_final, eta, c_final[-1], p_final[-1])
    nonlinear = ChargedNonlinearDiagnostics(
        root_success=bool(root_result.success),
        root_message=str(root_result.message),
        root_function_evaluations=int(root_result.nfev),
        root_scaled_residual=root_residual,
        polish_applied=polish_applied,
        polish_success=polish_success,
        polish_message=polish_message,
        polish_function_evaluations=polish_evaluations,
        final_scaled_residual=final_residual,
    )
    if not nonlinear.success or final_residual > DEFAULT_COLLOCATION_TOLERANCE:
        raise RuntimeError(
            "charged nonlinear solve failed the frozen local convergence gate: "
            f"success={nonlinear.success}, residual={final_residual:.3e}"
        )
    h_u_final = d1 @ h_final
    if np.any(~np.isfinite(h_final)) or np.any(h_final[:-1] <= 0.0):
        raise RuntimeError(
            "charged blackening profile must remain finite and positive "
            "before the horizon"
        )
    if not math.isfinite(float(h_u_final[-1])) or h_u_final[-1] >= -1.0e-10:
        raise RuntimeError(
            "charged horizon must be simple with inward derivative h_u(1) < 0"
        )
    return ChargedProfile(
        degree=degree,
        target_phi_h=phi_h,
        target_eta=eta,
        x_h=x_h_final,
        q=q_final,
        u=np.asarray(u, dtype=float),
        blackening=np.asarray(h_final, dtype=float),
        warp_factor=np.asarray(c_final, dtype=float),
        scalar_factor=np.asarray(p_final, dtype=float),
        nonlinear=nonlinear,
    )


def _charged_equations(
    x_h: float,
    eta: float,
    u: NDArray[np.float64],
    h: NDArray[np.float64],
    hu: NDArray[np.float64],
    huu: NDArray[np.float64],
    c: NDArray[np.float64],
    cu: NDArray[np.float64],
    cuu: NDArray[np.float64],
    pfield: NDArray[np.float64],
    pu: NDArray[np.float64],
    puu: NDArray[np.float64],
    *,
    scaled: bool,
) -> Tuple[
    NDArray[np.float64],
    NDArray[np.float64],
    NDArray[np.float64],
    NDArray[np.float64],
]:
    """Return compact physical equations, optionally elementwise-scaled."""

    nu = DGR_POTENTIAL.uv_power
    x = x_h * u
    a = x**2 * c
    au = x_h**2 * (2.0 * u * c + u**2 * cu)
    auu = x_h**2 * (2.0 * c + 4.0 * u * cu + u**2 * cuu)
    phi = x * pfield
    phiu = x_h * (pfield + u * pu)
    phiuu = x_h * (2.0 * pu + u * puu)

    alpha = -1.0 + nu * u * au
    alpha_u = nu * (au + u * auu)
    d_alpha = nu * u * alpha_u
    beta = nu * u * phiu
    beta_u = nu * (phiu + u * phiuu)
    d_beta = nu * u * beta_u
    gamma = nu * u * hu
    gamma_u = nu * (hu + u * huu)
    d_gamma = nu * u * gamma_u

    potential = np.asarray(DGR_POTENTIAL.potential(phi), dtype=float)
    potential_prime = np.asarray(
        DGR_POTENTIAL.first_derivative(phi), dtype=float
    )
    coupling = np.asarray(gauge_coupling(phi), dtype=float)
    coupling_log_prime = np.asarray(gauge_log_derivative(phi), dtype=float)
    phi_h = float(x_h * pfield[-1])
    potential_h = float(DGR_POTENTIAL.potential(phi_h))
    coupling_h = float(gauge_coupling(phi_h))
    radial_power = np.power(u, 6.0 / nu)
    charge_term = (
        eta**2
        * (-2.0 * potential_h * coupling_h)
        * radial_power
        * np.exp(6.0 * a[-1] - 4.0 * a)
        / coupling
    )

    warp_terms = (d_alpha, -alpha, -(alpha**2), beta**2 / 6.0)
    blackening_terms = (d_gamma, -gamma, 3.0 * alpha * gamma, -charge_term)
    scalar_terms = (
        h * (d_beta - beta),
        (3.0 * alpha * h + gamma) * beta,
        -np.exp(2.0 * a) * potential_prime,
        0.5 * charge_term * coupling_log_prime,
    )
    constraint_terms = (
        6.0 * alpha * gamma,
        h * (24.0 * alpha**2 - beta**2),
        2.0 * np.exp(2.0 * a) * potential,
        charge_term,
    )
    aggregate = _scaled_sum if scaled else _unscaled_sum
    return (
        aggregate(warp_terms),
        aggregate(blackening_terms),
        aggregate(scalar_terms),
        aggregate(constraint_terms),
    )


def _scaled_charged_collocation_equations(
    x_h: float,
    eta: float,
    u: NDArray[np.float64],
    h: NDArray[np.float64],
    hu: NDArray[np.float64],
    huu: NDArray[np.float64],
    c: NDArray[np.float64],
    cu: NDArray[np.float64],
    cuu: NDArray[np.float64],
    pfield: NDArray[np.float64],
    pu: NDArray[np.float64],
    puu: NDArray[np.float64],
) -> Tuple[NDArray[np.float64], NDArray[np.float64], NDArray[np.float64]]:
    """Return UV-factorized charged residuals used by the nonlinear solve.

    These equations are the compact ``D = z d/dz`` equations divided by
    their known analytic UV powers.  This avoids subtracting order-one terms
    to recover an order-``u**2`` warp residual near the boundary.  The
    oversampled diagnostics deliberately evaluate the compact physical form
    in :func:`_scaled_charged_equations` instead.
    """

    nu = DGR_POTENTIAL.uv_power
    x = x_h * u
    a = x**2 * c
    phi = x * pfield
    a_x_scaled = 2.0 * u * c + u**2 * cu
    scalar_x = pfield + u * pu
    potential_prime = np.asarray(
        DGR_POTENTIAL.first_derivative(phi), dtype=float
    )
    coupling = np.asarray(gauge_coupling(phi), dtype=float)
    coupling_log_prime = np.asarray(gauge_log_derivative(phi), dtype=float)
    phi_h = float(x_h * pfield[-1])
    potential_h = float(DGR_POTENTIAL.potential(phi_h))
    coupling_h = float(gauge_coupling(phi_h))
    charge_term = (
        eta**2
        * (-2.0 * potential_h * coupling_h)
        * np.power(u, 6.0 / nu)
        * np.exp(6.0 * a[-1] - 4.0 * a)
        / coupling
    )
    charge_blackening = np.divide(
        -charge_term,
        nu**2 * u,
        out=np.zeros_like(u),
        where=u != 0.0,
    )
    charge_scalar = np.divide(
        0.5 * charge_term * coupling_log_prime,
        nu**2 * x_h * u,
        out=np.zeros_like(u),
        where=u != 0.0,
    )
    blackening_terms = (
        u * huu,
        (3.0 * x_h**2 * u * a_x_scaled + 1.0 - 4.0 / nu) * hu,
        charge_blackening,
    )
    warp_terms = (
        2.0 * c + 4.0 * u * cu + u**2 * cuu,
        (1.0 + 1.0 / nu) * (2.0 * c + u * cu),
        -x_h**2 * a_x_scaled**2,
        scalar_x**2 / 6.0,
    )
    scalar_terms = (
        u * h * (2.0 * pu + u * puu),
        (
            3.0 * x_h**2 * u * h * a_x_scaled
            + (1.0 - 4.0 / nu) * h
            + u * hu
        )
        * scalar_x,
        np.divide(
            -np.exp(2.0 * a) * potential_prime,
            nu**2 * x_h * u,
            out=np.zeros_like(u),
            where=u != 0.0,
        ),
        charge_scalar,
    )
    return (
        _scaled_sum(warp_terms),
        _scaled_sum(blackening_terms),
        _scaled_sum(scalar_terms),
    )


def _scaled_sum(
    terms: Tuple[NDArray[np.float64], ...],
) -> NDArray[np.float64]:
    numerator = sum(terms)
    denominator = 1.0 + sum(np.abs(term) for term in terms)
    return np.asarray(numerator / denominator, dtype=float)


def _unscaled_sum(
    terms: Tuple[NDArray[np.float64], ...],
) -> NDArray[np.float64]:
    return np.asarray(sum(terms), dtype=float)


def _charge_from_horizon(
    x_h: float,
    eta: float,
    c_h: float,
    p_h: float,
) -> float:
    if eta == 0.0:
        return 0.0
    z_h = math.exp(math.log(x_h) / DGR_POTENTIAL.uv_power)
    phi_h = x_h * p_h
    a_h = x_h**2 * c_h
    A_h = -math.log(z_h) + a_h
    horizon_factor = -2.0 * float(DGR_POTENTIAL.potential(phi_h)) * float(
        gauge_coupling(phi_h)
    )
    if not math.isfinite(horizon_factor) or horizon_factor <= 0.0:
        raise RuntimeError("charged horizon normalization must be positive")
    return eta * math.exp(3.0 * A_h) * math.sqrt(horizon_factor)


def _neutral_initial_profile(
    phi_h: float,
    degree: int,
    config: ChargedSolverConfig,
) -> CoupledProfile:
    # This local fit is only a deterministic initial guess over the approved
    # critical patch.  The combined charged solve enforces the exact phi_H.
    x_guess = float(np.clip(0.9700 + 0.0152 * (phi_h - 4.84), 0.82, 1.05))
    degrees = [
        item
        for item in (24, 40, 60, 80, 120, 150)
        if item >= config.neutral_initial_degree and item <= degree
    ]
    if degree not in degrees:
        degrees.append(degree)
    degrees = sorted(set(degrees))
    seed: Optional[CoupledProfile] = None
    for item in degrees:
        seed = solve_coupled_profile(
            DGR_POTENTIAL,
            x_guess,
            item,
            seed=seed,
        )
    if seed is None:
        raise RuntimeError("neutral seed continuation did not run")
    return seed


def _interpolate_profile_field(
    source_nodes: NDArray[np.float64],
    source_values: NDArray[np.float64],
    target_nodes: NDArray[np.float64],
) -> NDArray[np.float64]:
    return np.asarray(
        _barycentric_interpolator(source_nodes, source_values)(target_nodes),
        dtype=float,
    )


def _analytic_warp_uv() -> float:
    nu = DGR_POTENTIAL.uv_power
    return -nu / (12.0 * (2.0 * nu + 1.0))


class _DirectCriticalEvaluator:
    """Deterministic constant-temperature derivative evaluator at ``N=80``."""

    def __init__(self) -> None:
        self.seed = solve_charged_profile(
            DEFAULT_CRITICAL_INITIAL[0],
            DEFAULT_CRITICAL_INITIAL[1],
            DEFAULT_DEGREES[0],
        )
        self.cache: Dict[Tuple[float, float], Tuple[ChargedProfile, ChargedPoint]] = {}
        self.solve_count = 0

    @staticmethod
    def key(phi_h: float, eta: float) -> Tuple[float, float]:
        return round(float(phi_h), 13), round(float(eta), 13)

    def evaluate(
        self, phi_h: float, eta: float
    ) -> Tuple[ChargedProfile, ChargedPoint]:
        key = self.key(phi_h, eta)
        if key not in self.cache:
            profile = solve_charged_profile(
                float(phi_h),
                float(eta),
                DEFAULT_DEGREES[0],
                seed=self.seed,
            )
            self.cache[key] = profile, charged_point_from_profile(profile)
            self.solve_count += 1
        return self.cache[key]

    def isotherm_point(
        self,
        phi_h: float,
        temperature: float,
    ) -> Tuple[ChargedProfile, ChargedPoint, float]:
        def residual(eta: float) -> float:
            return self.evaluate(phi_h, eta)[1].temperature - temperature

        lower, upper = DEFAULT_CRITICAL_ETA_BRACKET
        low_value = residual(lower)
        high_value = residual(upper)
        if low_value * high_value > 0.0:
            raise RuntimeError("constant-temperature eta crossing is absent")
        eta = brentq(
            residual,
            lower,
            upper,
            xtol=1.0e-10,
            rtol=1.0e-12,
        )
        profile, point = self.evaluate(phi_h, eta)
        return profile, point, eta

    def physical_conditions(
        self,
        candidate: Sequence[float],
        step: float,
        *,
        details: bool = False,
    ) -> Any:
        phi_h, eta = map(float, candidate)
        center_profile, center = self.evaluate(phi_h, eta)
        points: List[Tuple[ChargedProfile, ChargedPoint]] = []
        etas: List[float] = []
        offsets = (-2, -1, 0, 1, 2)
        for offset in offsets:
            if offset == 0:
                profile, point, row_eta = center_profile, center, eta
            else:
                profile, point, row_eta = self.isotherm_point(
                    phi_h + offset * step,
                    center.temperature,
                )
            points.append((profile, point))
            etas.append(float(row_eta))

        mu = np.asarray([item[1].chemical_potential for item in points])
        rho = np.asarray([item[1].density for item in points])
        first_weights = np.asarray([1.0, -8.0, 0.0, 8.0, -1.0]) / 12.0
        second_weights = np.asarray([-1.0, 16.0, -30.0, 16.0, -1.0]) / 12.0
        mu_first = float(first_weights @ mu / step)
        rho_first = float(first_weights @ rho / step)
        mu_second = float(second_weights @ mu / step**2)
        rho_second = float(second_weights @ rho / step**2)
        if abs(rho_first) <= 1.0e-12:
            raise RuntimeError("constant-temperature density coordinate is singular")
        slope = mu_first / rho_first
        curvature = (
            mu_second * rho_first - mu_first * rho_second
        ) / rho_first**3
        rho_scale = max(1.0, abs(center.density))
        mu_scale = max(1.0, abs(center.chemical_potential))
        normalized = np.asarray(
            [
                slope * rho_scale / mu_scale,
                curvature * rho_scale**2 / mu_scale,
            ]
        )
        if not details:
            return normalized
        return {
            "phi_H": phi_h,
            "eta": eta,
            "T_BH": center.temperature,
            "mu_BH": center.chemical_potential,
            "rho_canonical_BH": center.density,
            "dmu_drho_T": slope,
            "d2mu_drho2_T": curvature,
            "normalized_conditions": normalized.tolist(),
            "stencil": [
                {
                    "phi_H": phi_h + offset * step,
                    "eta": etas[index],
                    "mu_BH": float(mu[index]),
                    "rho_canonical_BH": float(rho[index]),
                }
                for index, offset in enumerate(offsets)
            ],
        }


def _independent_critical_jacobian(
    evaluator: _DirectCriticalEvaluator,
    point: Sequence[float],
    phi_step: float,
    eta_step: float,
) -> Dict[str, float]:
    values: Dict[Tuple[int, int], NDArray[np.float64]] = {}
    for i_phi in (-1, 0, 1):
        for i_eta in (-1, 0, 1):
            item = evaluator.evaluate(
                point[0] + i_phi * phi_step,
                point[1] + i_eta * eta_step,
            )[1]
            values[i_phi, i_eta] = np.asarray(
                [item.temperature, item.chemical_potential, item.density]
            )

    def d1(field: int, axis: int) -> float:
        if axis == 0:
            return float(
                (values[1, 0][field] - values[-1, 0][field])
                / (2.0 * phi_step)
            )
        return float(
            (values[0, 1][field] - values[0, -1][field])
            / (2.0 * eta_step)
        )

    def d2(field: int, axis: int) -> float:
        if axis == 0:
            return float(
                (
                    values[1, 0][field]
                    - 2.0 * values[0, 0][field]
                    + values[-1, 0][field]
                )
                / phi_step**2
            )
        return float(
            (
                values[0, 1][field]
                - 2.0 * values[0, 0][field]
                + values[0, -1][field]
            )
            / eta_step**2
        )

    def mixed(field: int) -> float:
        return float(
            (
                values[1, 1][field]
                - values[1, -1][field]
                - values[-1, 1][field]
                + values[-1, -1][field]
            )
            / (4.0 * phi_step * eta_step)
        )

    t_phi, t_eta = d1(0, 0), d1(0, 1)
    m_phi, m_eta = d1(1, 0), d1(1, 1)
    r_phi, r_eta = d1(2, 0), d1(2, 1)
    t_pp, t_ee, t_pe = d2(0, 0), d2(0, 1), mixed(0)
    m_pp, m_ee, m_pe = d2(1, 0), d2(1, 1), mixed(1)
    jacobian = t_phi * m_eta - t_eta * m_phi
    jacobian_phi = (
        t_pp * m_eta + t_phi * m_pe - t_pe * m_phi - t_eta * m_pp
    )
    jacobian_eta = (
        t_pe * m_eta + t_phi * m_ee - t_ee * m_phi - t_eta * m_pe
    )
    tangent = t_eta * jacobian_phi - t_phi * jacobian_eta
    t_norm = math.hypot(t_phi, t_eta)
    m_norm = math.hypot(m_phi, m_eta)
    jacobian_norm = math.hypot(jacobian_phi, jacobian_eta)
    return {
        "delta_phi_H": phi_step,
        "delta_eta": eta_step,
        "T_mu_jacobian": jacobian,
        "normalized_T_mu_jacobian": jacobian / (t_norm * m_norm),
        "isotherm_tangent_derivative": tangent,
        "normalized_isotherm_tangent_derivative": (
            tangent / (t_norm * jacobian_norm)
        ),
        "T_rho_jacobian": t_phi * r_eta - t_eta * r_phi,
    }


def _locate_direct_critical() -> Tuple[Dict[str, Any], _DirectCriticalEvaluator]:
    evaluator = _DirectCriticalEvaluator()
    roots: List[Dict[str, Any]] = []
    guess = np.asarray(DEFAULT_CRITICAL_INITIAL, dtype=float)
    for step in DEFAULT_CRITICAL_PHI_STEPS:
        answer = root(
            lambda value: evaluator.physical_conditions(value, step),
            guess,
            method="hybr",
            options={
                "xtol": 1.0e-8,
                "maxfev": 32,
                "diag": np.asarray([1.0, 10.0]),
            },
        )
        details = evaluator.physical_conditions(answer.x, step, details=True)
        roots.append(
            {
                "phi_step": step,
                "solver_success": bool(answer.success),
                "solver_message": str(answer.message),
                "function_evaluations": int(answer.nfev),
                **details,
            }
        )
        if not answer.success:
            raise RuntimeError(f"direct critical root failed at step {step}")
        guess = np.asarray(answer.x, dtype=float)

    final = roots[-1]
    final_coordinate = (float(final["phi_H"]), float(final["eta"]))
    validation = evaluator.physical_conditions(
        final_coordinate,
        DEFAULT_CRITICAL_VALIDATION_STEP,
        details=True,
    )
    jacobians = [
        _independent_critical_jacobian(
            evaluator,
            final_coordinate,
            phi_step,
            eta_step,
        )
        for phi_step, eta_step in DEFAULT_CRITICAL_JACOBIAN_STEPS
    ]
    changes = [
        {
            name: _scaled_relative_change(previous[name], current[name])
            for name in (
                "phi_H",
                "eta",
                "T_BH",
                "mu_BH",
                "rho_canonical_BH",
            )
        }
        for previous, current in zip(roots, roots[1:])
    ]
    derivative_values = [
        abs(float(value)) for value in validation["normalized_conditions"]
    ] + [
        abs(float(item[name]))
        for item in jacobians
        for name in (
            "normalized_T_mu_jacobian",
            "normalized_isotherm_tangent_derivative",
        )
    ]
    maximum_step_change = max(
        value for change in changes for value in change.values()
    )
    source_coordinates = {
        "T_MeV": float(final["T_BH"]) * LAMBDA_T_MEV,
        "mu_MeV": float(final["mu_BH"]) * LAMBDA_MU_MEV,
    }
    source_errors = {
        "T_MeV_absolute_error": abs(source_coordinates["T_MeV"] - 143.0),
        "mu_MeV_absolute_error": abs(source_coordinates["mu_MeV"] - 783.0),
        "phi_H_absolute_error": abs(float(final["phi_H"]) - 4.84),
        "eta_absolute_error": abs(float(final["eta"]) - 0.40),
    }
    return (
        {
            "method": "direct constant-T five-point physical derivatives",
            "degree": DEFAULT_DEGREES[0],
            "step_roots": roots,
            "scaled_step_changes": changes,
            "maximum_step_change": maximum_step_change,
            "fine_step_cross_validation": validation,
            "independent_parameter_map_diagnostics": jacobians,
            "maximum_normalized_critical_diagnostic": max(derivative_values),
            "final_source_coordinates": source_coordinates,
            "source_coordinate_errors": source_errors,
            "fresh_profile_solves": evaluator.solve_count,
        },
        evaluator,
    )


def _point_gate_evidence(profile: ChargedProfile) -> Dict[str, Any]:
    point = charged_point_from_profile(profile)
    diagnostics = charged_equation_diagnostics(profile)
    explicit = solve_explicit_maxwell_profile(profile)
    explicit_point = explicit_maxwell_point_from_profile(explicit)
    explicit_diagnostics = explicit_maxwell_diagnostics(explicit, profile)
    noether = explicit_noether_diagnostics(explicit)

    limits = {
        "nonlinear_scaled": DEFAULT_COLLOCATION_TOLERANCE,
        "equation_unscaled": DEFAULT_EQUATION_TOLERANCE,
        "constraint_unscaled": DEFAULT_CONSTRAINT_TOLERANCE,
        "boundary_unscaled": DEFAULT_BOUNDARY_TOLERANCE,
        "primary_reconstructed_maxwell_unscaled": (
            DEFAULT_PRIMARY_MAXWELL_TOLERANCE
        ),
        "explicit_gauss_flux_relative_drift": DEFAULT_GAUSS_TOLERANCE,
        "explicit_noether_charge_relative_drift": DEFAULT_NOETHER_TOLERANCE,
        "explicit_noether_horizon_identity_relative_error": 1.0e-12,
        "target_relative_error": DEFAULT_TARGET_TOLERANCE,
        "chemical_potential_reconstruction_relative_error": 1.0e-9,
        "route_observable_relative_difference": DEFAULT_ROUTE_TOLERANCE,
        "route_field_relative_difference": DEFAULT_FIELD_ROUTE_TOLERANCE,
        "electric_potential_horizon": 1.0e-12,
    }
    metrics = {
        "nonlinear_scaled": profile.nonlinear.final_scaled_residual,
        "maximum_equation_unscaled": (
            diagnostics.maximum_evaluated_equation_residual
        ),
        "constraint_unscaled": diagnostics.constraint,
        "boundary_unscaled": diagnostics.maximum_boundary_residual,
        "primary_reconstructed_maxwell_unscaled": diagnostics.maxwell_equation,
        "primary_reconstructed_gauss_flux_relative_drift_monitor": (
            diagnostics.gauss_flux_relative_drift
        ),
        "phi_h_target_relative_error": diagnostics.phi_h_target_relative_error,
        "eta_target_relative_error": (
            diagnostics.eta_algebraic_consistency_error
        ),
        "chemical_potential_reconstruction_relative_error": (
            diagnostics.chemical_potential_reconstruction_relative_error
        ),
        "uv_density_dictionary_relative_error": (
            diagnostics.uv_minus_phi2_q_over_2_relative_error
        ),
        "electric_potential_horizon": diagnostics.electric_potential_horizon,
        "minimum_blackening_interior": diagnostics.minimum_blackening_interior,
        "horizon_blackening_derivative": (
            diagnostics.horizon_blackening_derivative
        ),
        "explicit_nonlinear_scaled": explicit.nonlinear.final_scaled_residual,
        "explicit_maximum_equation_unscaled": explicit_diagnostics[
            "maximum_evaluated_equation_residual"
        ],
        "explicit_constraint_unscaled": explicit_diagnostics["constraint"],
        "explicit_boundary_unscaled": explicit_diagnostics[
            "maximum_boundary_residual"
        ],
        "explicit_gauss_flux_relative_drift": explicit_diagnostics[
            "gauss_flux_relative_drift"
        ],
        "explicit_noether_charge_relative_drift": noether[
            "noether_charge_relative_drift"
        ],
        "explicit_noether_horizon_identity_relative_error": noether[
            "noether_horizon_identity_relative_error"
        ],
        "route_background_field_relative_difference": explicit_diagnostics[
            "maximum_background_field_difference"
        ],
        "route_electric_coefficient_relative_difference": explicit_diagnostics[
            "electric_coefficient_difference"
        ],
        "route_electric_potential_relative_difference": explicit_diagnostics[
            "electric_potential_difference"
        ],
        "route_temperature_relative_difference": explicit_diagnostics[
            "temperature_relative_difference"
        ],
        "route_chemical_potential_relative_difference": explicit_diagnostics[
            "chemical_potential_relative_difference"
        ],
        "route_entropy_relative_difference": explicit_diagnostics[
            "entropy_relative_difference"
        ],
        "route_density_relative_difference": explicit_diagnostics[
            "density_relative_difference"
        ],
    }
    failures: List[str] = []

    def require(metric: str, limit: float, label: Optional[str] = None) -> None:
        if not math.isfinite(float(metrics[metric])) or float(metrics[metric]) > limit:
            failures.append(metric if label is None else label)

    require("nonlinear_scaled", limits["nonlinear_scaled"])
    require("maximum_equation_unscaled", limits["equation_unscaled"])
    require("constraint_unscaled", limits["constraint_unscaled"])
    require("boundary_unscaled", limits["boundary_unscaled"])
    require(
        "primary_reconstructed_maxwell_unscaled",
        limits["primary_reconstructed_maxwell_unscaled"],
    )
    require("phi_h_target_relative_error", limits["target_relative_error"])
    require("eta_target_relative_error", limits["target_relative_error"])
    require(
        "chemical_potential_reconstruction_relative_error",
        limits["chemical_potential_reconstruction_relative_error"],
    )
    require("uv_density_dictionary_relative_error", limits["target_relative_error"])
    require("electric_potential_horizon", limits["electric_potential_horizon"])
    require("explicit_nonlinear_scaled", limits["nonlinear_scaled"])
    require(
        "explicit_maximum_equation_unscaled", limits["equation_unscaled"]
    )
    require("explicit_constraint_unscaled", limits["constraint_unscaled"])
    require("explicit_boundary_unscaled", limits["boundary_unscaled"])
    require(
        "explicit_gauss_flux_relative_drift",
        limits["explicit_gauss_flux_relative_drift"],
    )
    require(
        "explicit_noether_charge_relative_drift",
        limits["explicit_noether_charge_relative_drift"],
    )
    require(
        "explicit_noether_horizon_identity_relative_error",
        limits["explicit_noether_horizon_identity_relative_error"],
    )
    for metric in (
        "route_background_field_relative_difference",
        "route_electric_coefficient_relative_difference",
        "route_electric_potential_relative_difference",
    ):
        require(metric, limits["route_field_relative_difference"])
    for metric in (
        "route_temperature_relative_difference",
        "route_chemical_potential_relative_difference",
        "route_entropy_relative_difference",
        "route_density_relative_difference",
    ):
        require(metric, limits["route_observable_relative_difference"])
    if metrics["minimum_blackening_interior"] <= 0.0:
        failures.append("minimum_blackening_interior")
    if metrics["horizon_blackening_derivative"] >= 0.0:
        failures.append("horizon_blackening_derivative")

    return {
        "status": "pass" if not failures else "fail",
        "passed": not failures,
        "failures": failures,
        "limits": limits,
        "metrics": metrics,
        "primary": {
            "point": point.to_dict(),
            "nonlinear": profile.nonlinear.to_dict(),
            "diagnostics": diagnostics.to_dict(),
        },
        "explicit": {
            "point": explicit_point.to_dict(),
            "nonlinear": explicit.nonlinear.to_dict(),
            "diagnostics": explicit_diagnostics,
            "noether": noether,
            "role": (
                "independent simultaneous geometry-scalar-Maxwell acceptance route"
            ),
        },
        "primary_reconstructed_gauss_affects_acceptance": False,
        "density_dictionary": "rho_canonical_BH = q/2",
    }


def _run_reduced_verifier_once() -> Dict[str, Any]:
    critical, evaluator = _locate_direct_critical()
    final = critical["step_roots"][-1]
    critical_phi_h = float(final["phi_H"])
    critical_eta = float(final["eta"])
    degree_80_profile, _ = evaluator.evaluate(critical_phi_h, critical_eta)

    refinement: List[Dict[str, Any]] = []
    current_profile = degree_80_profile
    for degree in DEFAULT_DEGREES:
        if degree != DEFAULT_DEGREES[0]:
            current_profile = solve_charged_profile(
                critical_phi_h,
                critical_eta,
                degree,
                seed=current_profile,
            )
        evidence = _point_gate_evidence(current_profile)
        refinement.append(
            {
                "label": "located-critical-state",
                "degree": degree,
                **evidence,
            }
        )

    controls = []
    for label, phi_h, eta in DEFAULT_CONTROL_STATES:
        profile = solve_charged_profile(phi_h, eta, DEFAULT_DEGREES[0])
        controls.append(
            {
                "label": label,
                "degree": DEFAULT_DEGREES[0],
                **_point_gate_evidence(profile),
            }
        )

    observable_keys = (
        "temperature_BH",
        "mu_BH",
        "entropy_BH",
        "rho_canonical_BH",
    )
    refinement_changes: List[Dict[str, Any]] = []
    for coarse, fine in zip(refinement, refinement[1:]):
        coarse_point = coarse["primary"]["point"]
        fine_point = fine["primary"]["point"]
        changes = {
            key: _scaled_relative_change(coarse_point[key], fine_point[key])
            for key in observable_keys
        }
        refinement_changes.append(
            {
                "coarse_degree": coarse["degree"],
                "fine_degree": fine["degree"],
                "changes": changes,
                "maximum_change": max(changes.values()),
            }
        )
    ordering_failures = []
    for key in observable_keys:
        coarse_change = refinement_changes[0]["changes"][key]
        fine_change = refinement_changes[1]["changes"][key]
        if (
            coarse_change > DEFAULT_REFINEMENT_ORDER_FLOOR
            and fine_change > coarse_change
        ):
            ordering_failures.append(key)

    figure_5_records = []
    for resource in FIGURE_5_RESOURCES:
        dataset = load_reference_dataset(resource)
        figure_5_records.append(
            {
                "id": dataset["id"],
                "entry_count": len(dataset["entries"]),
                "review_status": dataset["provenance"]["review_status"],
                "reviewed_by": dataset["provenance"].get("reviewed_by"),
                "reviewed_on": dataset["provenance"].get("reviewed_on"),
                "absolute_ordinate_comparison": "blocked",
                "role": "source-provenance and horizontal-window diagnostic only",
            }
        )

    all_states = refinement + controls
    all_point_gates_pass = all(item["passed"] for item in all_states)
    maximum_route_difference = max(
        item["metrics"][key]
        for item in all_states
        for key in (
            "route_temperature_relative_difference",
            "route_chemical_potential_relative_difference",
            "route_entropy_relative_difference",
            "route_density_relative_difference",
        )
    )
    source_errors = critical["source_coordinate_errors"]
    source_coordinate_gate = bool(
        source_errors["T_MeV_absolute_error"] <= 5.0
        and source_errors["mu_MeV_absolute_error"] <= 10.0
        and source_errors["phi_H_absolute_error"] <= 0.20
        and source_errors["eta_absolute_error"] <= 0.04
    )
    critical_gate = bool(
        critical["maximum_normalized_critical_diagnostic"]
        <= DEFAULT_CRITICAL_TOLERANCE
        and critical["maximum_step_change"] <= DEFAULT_CRITICAL_TOLERANCE
    )
    refinement_gate = bool(
        refinement_changes[-1]["maximum_change"]
        <= DEFAULT_REFINEMENT_TOLERANCE
        and not ordering_failures
    )
    determinism_state = {
        "critical": {
            "phi_H": critical_phi_h,
            "eta": critical_eta,
            "T_BH": float(final["T_BH"]),
            "mu_BH": float(final["mu_BH"]),
            "rho_canonical_BH": float(final["rho_canonical_BH"]),
        },
        "refinement": [
            {
                "degree": item["degree"],
                "primary": {
                    key: item["primary"]["point"][key] for key in observable_keys
                },
                "explicit": {
                    key: item["explicit"]["point"][key] for key in observable_keys
                },
            }
            for item in refinement
        ],
        "controls": [
            {
                "label": item["label"],
                "primary": {
                    key: item["primary"]["point"][key] for key in observable_keys
                },
                "explicit": {
                    key: item["explicit"]["point"][key] for key in observable_keys
                },
            }
            for item in controls
        ],
    }
    return {
        "critical": critical,
        "critical_source_coordinate_gate": source_coordinate_gate,
        "critical_derivative_gate": critical_gate,
        "refinement": {
            "states": refinement,
            "changes": refinement_changes,
            "ordering_floor": DEFAULT_REFINEMENT_ORDER_FLOOR,
            "ordering_failures": ordering_failures,
            "passed": refinement_gate,
        },
        "controls": controls,
        "figure_5_reference_records": figure_5_records,
        "figure_5_absolute_ordinate_comparison": {
            "status": "blocked",
            "reason": "no verified public map to rho_canonical_BH",
            "affects_acceptance": False,
        },
        "summary": {
            "all_point_gates_pass": all_point_gates_pass,
            "critical_source_coordinate_gate": source_coordinate_gate,
            "critical_derivative_gate": critical_gate,
            "spectral_refinement_gate": refinement_gate,
            "maximum_final_refinement": refinement_changes[-1][
                "maximum_change"
            ],
            "refinement_ordering_failures": len(ordering_failures),
            "maximum_route_observable_difference": maximum_route_difference,
            "reported_state_count": len(all_states),
        },
        "determinism_state": determinism_state,
    }


def verify_dewolfe_gubser_rosen_emd_finite_density(
    *,
    repeat_for_determinism: bool = True,
) -> VerificationRecord:
    """Run the reduced finite-density classical benchmark contract."""

    first = _run_reduced_verifier_once()
    determinism_error: Optional[float] = None
    if repeat_for_determinism:
        second = _run_reduced_verifier_once()
        determinism_error = _maximum_nested_numeric_difference(
            first["determinism_state"], second["determinism_state"]
        )
    summary = first["summary"]
    source_errors = first["critical"]["source_coordinate_errors"]
    source_error_ratio = max(
        source_errors["T_MeV_absolute_error"] / 5.0,
        source_errors["mu_MeV_absolute_error"] / 10.0,
        source_errors["phi_H_absolute_error"] / 0.20,
        source_errors["eta_absolute_error"] / 0.04,
    )
    checks = (
        AcceptanceCheck(
            "charged-point-gates",
            (
                "all representative and refinement states pass equations, "
                "boundaries, conserved charges, and target gates"
            ),
            bool(summary["all_point_gates_pass"]),
            0.0 if summary["all_point_gates_pass"] else 1.0,
            "all six reported states pass the frozen point contract",
        ),
        AcceptanceCheck(
            "critical-source-coordinates",
            (
                "direct N=80 critical candidate reproduces the source T, mu, "
                "phi_H, and eta neighborhood"
            ),
            bool(summary["critical_source_coordinate_gate"]),
            source_error_ratio,
            "maximum normalized source-coordinate error <= 1",
        ),
        AcceptanceCheck(
            "critical-derivatives",
            (
                "constant-temperature critical conditions and independent "
                "parameter-map diagnostics"
            ),
            bool(summary["critical_derivative_gate"]),
            max(
                first["critical"]["maximum_normalized_critical_diagnostic"],
                first["critical"]["maximum_step_change"],
            ),
            f"<= {DEFAULT_CRITICAL_TOLERANCE:.1e}",
        ),
        AcceptanceCheck(
            "spectral-refinement",
            "fixed located state converges from N=80 through N=120 to N=150",
            bool(summary["spectral_refinement_gate"]),
            summary["maximum_final_refinement"],
            (
                f"N=120 to 150 <= {DEFAULT_REFINEMENT_TOLERANCE:.1e}; "
                f"zero ordering failures above {DEFAULT_REFINEMENT_ORDER_FLOOR:.1e}"
            ),
        ),
        AcceptanceCheck(
            "independent-explicit-maxwell-route",
            (
                "simultaneous explicit-Maxwell observables agree with the "
                "flux-reduced route"
            ),
            summary["maximum_route_observable_difference"]
            <= DEFAULT_ROUTE_TOLERANCE,
            summary["maximum_route_observable_difference"],
            f"<= {DEFAULT_ROUTE_TOLERANCE:.1e}",
        ),
        AcceptanceCheck(
            "figure-5-scope-separation",
            (
                "all three approved Figure 5 records remain provenance-only "
                "while the absolute ordinate dictionary is blocked"
            ),
            bool(
                len(first["figure_5_reference_records"]) == 3
                and all(
                    item["entry_count"] == 12
                    and item["review_status"] == "approved"
                    for item in first["figure_5_reference_records"]
                )
                and not first["figure_5_absolute_ordinate_comparison"][
                    "affects_acceptance"
                ]
            ),
            0.0,
            "three approved 12-anchor records; no absolute-density gate",
        ),
        AcceptanceCheck(
            "determinism",
            (
                "duplicate complete reduced verifiers reproduce every reported "
                "physical observable"
            ),
            determinism_error is not None
            and determinism_error <= DEFAULT_DETERMINISM_TOLERANCE,
            determinism_error,
            f"<= {DEFAULT_DETERMINISM_TOLERANCE:.1e}",
        ),
    )
    results = {
        "critical": first["critical"],
        "refinement": first["refinement"],
        "controls": first["controls"],
        "figure_5_reference_records": first["figure_5_reference_records"],
        "figure_5_absolute_ordinate_comparison": first[
            "figure_5_absolute_ordinate_comparison"
        ],
        "summary": summary,
        "determinism": {
            "repeat_enabled": repeat_for_determinism,
            "maximum_scaled_difference": determinism_error,
        },
    }
    record = VerificationRecord(
        definition=DEWOLFE_GUBSER_ROSEN_FINITE_DENSITY_DEFINITION,
        configuration={
            "bulk_dimension": 5,
            "ensemble": "grand canonical at each selected boundary chemical potential",
            "units": "L = kappa_5 = 1 with the published DGR source scales",
            "degrees": list(DEFAULT_DEGREES),
            "critical_initial": list(DEFAULT_CRITICAL_INITIAL),
            "critical_phi_steps": list(DEFAULT_CRITICAL_PHI_STEPS),
            "critical_validation_step": DEFAULT_CRITICAL_VALIDATION_STEP,
            "control_states": [
                {"label": label, "phi_H": phi_h, "eta": eta}
                for label, phi_h, eta in DEFAULT_CONTROL_STATES
            ],
            "canonical_density": "rho_canonical_BH = q/2",
            "source_figure_5_ordinate": "rho_source_figure5 (mapping blocked)",
        },
        numerical_method={
            "primary_route": (
                "UV-factorized Chebyshev collocation with analytic "
                "Maxwell-flux elimination"
            ),
            "verification_route": (
                "simultaneous UV-factorized Chebyshev solve of geometry, scalar, "
                "and Phi"
            ),
            "critical_locator": (
                "direct constant-temperature five-point derivatives with "
                "scipy.optimize.root(method='hybr')"
            ),
            "nonlinear_solver": (
                "scipy.optimize.root(method='hybr', xtol=1e-11), followed only "
                "when triggered by bounded scipy.optimize.least_squares(method='trf')"
            ),
            "independent_checks": (
                "oversampled physical equations, Einstein constraint, Gauss flux, "
                "Noether charge, source-coordinate comparison, and N refinement"
            ),
        },
        results=results,
        acceptance_checks=checks,
        software_versions=runtime_versions(),
        scope=(
            "Owner-approved reduced Forge/Verify reproduction of representative "
            "finite-density DeWolfe--Gubser--Rosen phenomenological bottom-up EMD "
            "backgrounds and the source model's reported critical-coordinate "
            "neighborhood. The Figure 5 absolute density ordinate, accepted "
            "near-critical topology, global phase diagram, coexistence line, "
            "critical exponents, and empirical-QCD validation are not reproduced."
        ),
        extra={
            "primary_source": {
                "id": SOURCE_ID,
                "pdf_sha256": SOURCE_PDF_SHA256,
                "source_archive_sha256": SOURCE_ARCHIVE_SHA256,
                "equations_in_scope": ["(1)-(5)", "(27)-(29)", "(38)-(45)"],
                "figure_5_absolute_ordinate_in_scope": False,
            },
            "contract_review": {
                "review_state": "approved",
                "reviewed_by": "Xin-Yi Liu",
                "reviewed_on": "2026-08-23",
                "authorization": (
                    "owner-selected classical-example Option A after C3i scope review"
                ),
            },
            "result_review_state": "approved",
            "result_reviewed_by": "Xin-Yi Liu",
            "result_reviewed_on": "2026-08-23",
            "generated_by_ai": True,
            "preserved_optional_extension": {
                "c3h_status": "failed-primary-temperature-overlap-gate",
                "topology": "not evaluated after the C3h hard stop",
                "affects_reduced_core_acceptance": False,
            },
        },
    )
    json.dumps(record.to_dict(), allow_nan=False, sort_keys=True)
    return record


def save_dewolfe_gubser_rosen_emd_finite_density_artifacts(
    record: VerificationRecord,
    output_directory: Path,
) -> Mapping[str, Path]:
    """Save strict JSON, selected-state CSV, and a computed verification plot."""

    directory = Path(output_directory)
    directory.mkdir(parents=True, exist_ok=True)
    paths = {
        "json": directory / "dewolfe-gubser-rosen-emd-finite-density-result.json",
        "csv": directory / "dewolfe-gubser-rosen-emd-finite-density-states.csv",
        "plot": directory / "dewolfe-gubser-rosen-emd-finite-density-verification.png",
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
    rows = []
    for group in ("refinement", "controls"):
        states = (
            payload["results"]["refinement"]["states"]
            if group == "refinement"
            else payload["results"]["controls"]
        )
        for state in states:
            for route in ("primary", "explicit"):
                point = state[route]["point"]
                rows.append(
                    {
                        "group": group,
                        "label": state["label"],
                        "degree": state["degree"],
                        "route": route,
                        "phi_H": point["phi_h"],
                        "eta": point["eta"],
                        "temperature_BH": point["temperature_BH"],
                        "mu_BH": point["mu_BH"],
                        "entropy_BH": point["entropy_BH"],
                        "rho_canonical_BH": point["rho_canonical_BH"],
                        "passed": state["passed"],
                    }
                )
    with paths["csv"].open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    _save_reduced_verification_plot(payload, paths["plot"])
    return paths


def _save_reduced_verification_plot(
    payload: Mapping[str, Any], path: Path
) -> None:
    try:
        import matplotlib

        matplotlib.use("Agg")
        from matplotlib import pyplot as plt
    except ImportError as exc:
        raise RuntimeError(
            "Matplotlib is required for --output-dir; install holoforge[plot]"
        ) from exc

    critical = payload["results"]["critical"]
    computed = critical["final_source_coordinates"]
    refinement = payload["results"]["refinement"]["changes"]
    labels = ("T", "mu", "s", "rho")
    keys = (
        "temperature_BH",
        "mu_BH",
        "entropy_BH",
        "rho_canonical_BH",
    )
    figure, axes = plt.subplots(1, 2, figsize=(10.5, 4.3), constrained_layout=True)
    axes[0].scatter([783.0], [143.0], marker="x", s=90, linewidths=2.0, label="source")
    axes[0].scatter(
        [computed["mu_MeV"]],
        [computed["T_MeV"]],
        marker="o",
        s=55,
        label="HoloForge N=80",
    )
    axes[0].set(
        xlabel=r"$\mu_c$ [MeV]",
        ylabel=r"$T_c$ [MeV]",
        title="Reported critical-coordinate neighborhood",
    )
    axes[0].ticklabel_format(
        axis="both",
        style="plain",
        useOffset=False,
    )
    axes[0].legend(frameon=False)
    width = 0.34
    positions = np.arange(len(labels), dtype=float)
    axes[1].bar(
        positions - width / 2.0,
        [refinement[0]["changes"][key] for key in keys],
        width,
        label="80 to 120",
    )
    axes[1].bar(
        positions + width / 2.0,
        [refinement[1]["changes"][key] for key in keys],
        width,
        label="120 to 150",
    )
    axes[1].axhline(
        DEFAULT_REFINEMENT_TOLERANCE,
        color="black",
        linestyle="--",
        linewidth=1.0,
        label="gate",
    )
    axes[1].set_yscale("log")
    axes[1].set_xticks(positions, labels)
    axes[1].set(
        ylabel="scaled change",
        title="Fixed located-state spectral refinement",
    )
    axes[1].legend(frameon=False)
    figure.suptitle("DGR finite-density classical benchmark")
    figure.savefig(path, dpi=180)
    plt.close(figure)


def _scaled_relative_change(left: float, right: float) -> float:
    return abs(float(left) - float(right)) / max(
        1.0, abs(float(left)), abs(float(right))
    )


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
    if (
        isinstance(left, Sequence)
        and isinstance(right, Sequence)
        and not isinstance(left, (str, bytes))
    ):
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
        return _scaled_relative_change(float(left), float(right))
    return 0.0 if left == right else math.inf


def _validate_positive(name: str, value: Real) -> float:
    if isinstance(value, bool) or not isinstance(value, Real):
        raise ValueError(f"{name} must be a positive finite real number")
    resolved = float(value)
    if not math.isfinite(resolved) or resolved <= 0.0:
        raise ValueError(f"{name} must be a positive finite real number")
    return resolved


def _validate_integer(name: str, value: int, *, minimum: int) -> int:
    if isinstance(value, bool) or not isinstance(value, Integral):
        raise ValueError(f"{name} must be an integer")
    resolved = int(value)
    if resolved < minimum:
        raise ValueError(f"{name} must be at least {minimum}")
    return resolved


def _validate_interval(
    name: str,
    value: Real,
    interval: Tuple[float, float],
) -> float:
    if isinstance(value, bool) or not isinstance(value, Real):
        raise ValueError(f"{name} must be a finite real number")
    resolved = float(value)
    if not math.isfinite(resolved) or not interval[0] <= resolved <= interval[1]:
        raise ValueError(
            f"{name} must lie in the approved [{interval[0]}, {interval[1]}] interval"
        )
    return resolved


__all__ = [
    "CRITICAL_ETA_INTERVAL",
    "CRITICAL_PHI_H_INTERVAL",
    "DEWOLFE_GUBSER_ROSEN_FINITE_DENSITY_DEFINITION",
    "ChargedEquationDiagnostics",
    "ChargedNonlinearDiagnostics",
    "ChargedPoint",
    "ChargedProfile",
    "ChargedSolverConfig",
    "ExplicitMaxwellProfile",
    "charged_equation_diagnostics",
    "charged_point_from_profile",
    "explicit_maxwell_diagnostics",
    "explicit_noether_diagnostics",
    "explicit_maxwell_point_from_profile",
    "save_dewolfe_gubser_rosen_emd_finite_density_artifacts",
    "solve_charged_profile",
    "solve_explicit_maxwell_profile",
    "verify_dewolfe_gubser_rosen_emd_finite_density",
]
