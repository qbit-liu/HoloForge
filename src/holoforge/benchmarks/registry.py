"""Deterministic command adapters for HoloForge's built-in benchmarks."""

from __future__ import annotations

import math
from pathlib import Path
from typing import Any, Mapping, Sequence

from holoforge.benchmarks.hard_wall_vector import (
    DEFAULT_NUM_MODES as HARD_WALL_DEFAULT_NUM_MODES,
    DEFAULT_RATIO_TOLERANCE,
    HardWallConfig,
    solve_hard_wall_spectrum,
)
from holoforge.benchmarks.holographic_superconductor import (
    CondensateConfig,
    OnsetConfig,
    save_condensate_plot,
    verify_superconductor,
)
from holoforge.benchmarks.linear_axion_dc import verify_linear_axion_dc
from holoforge.benchmarks.soft_wall_vector import (
    DEFAULT_GRID_POINTS,
    DEFAULT_NUM_MODES,
    DEFAULT_TOLERANCE,
    SoftWallConfig,
    solve_spectrum,
)
from holoforge.core.registry import (
    BenchmarkAdapter,
    BenchmarkExecution,
    BenchmarkExecutionError,
    BenchmarkRegistry,
    ModelCardReference,
)


SOFT_WALL_MODEL_CARD = ModelCardReference(
    identifier="qcd.soft-wall-vector.kkss",
    schema_version="0.1",
    repository_path="domains/qcd/soft_wall_vector/model-card.json",
    sha256="6cb2a0f2824d279b68e20da5c8304d5ef68676649815ee6bd0816ec0f385d2fd",
)
HARD_WALL_MODEL_CARD = ModelCardReference(
    identifier="qcd.hard-wall-vector.ekss",
    schema_version="0.1",
    repository_path="domains/qcd/hard_wall_vector/model-card.json",
    sha256="96aeff5ed6d970dbb90d5c0dd458e579ee449a871edc494e43899a1003c13c61",
)
SUPERCONDUCTOR_MODEL_CARD = ModelCardReference(
    identifier="condensed-matter.holographic-superconductor.hhh",
    schema_version="0.1",
    repository_path=(
        "domains/condensed_matter/holographic_superconductor/model-card.json"
    ),
    sha256="d1c2bffe27fd76714f84d33c062caad7b3f5bc388546f58e50736009c7e6e908",
)
LINEAR_AXION_MODEL_CARD = ModelCardReference(
    identifier="transport.linear-axion-dc.andrade-withers",
    schema_version="0.1",
    repository_path="domains/transport/linear_axion_dc/model-card.json",
    sha256="d17a1d3d12ad71ff93354b9b61146a84be06030bbb4a8016f1371ba8cc472984",
)
def _configure_soft_wall(parser: Any) -> None:
    parser.add_argument(
        "--kappa",
        type=float,
        default=1.0,
        help="Positive soft-wall scale in GeV (default: 1.0).",
    )
    parser.add_argument(
        "--modes",
        type=int,
        default=DEFAULT_NUM_MODES,
        help=f"Number of lowest modes (default: {DEFAULT_NUM_MODES}).",
    )
    parser.add_argument(
        "--grid-points",
        type=int,
        default=DEFAULT_GRID_POINTS,
        help=(
            "Number of interior finite-difference points "
            f"(default: {DEFAULT_GRID_POINTS})."
        ),
    )
    parser.add_argument(
        "--z-max",
        type=float,
        default=None,
        help="IR boundary in GeV^-1 (default: 10/kappa).",
    )
    parser.add_argument(
        "--tolerance",
        type=float,
        default=DEFAULT_TOLERANCE,
        help=f"Maximum accepted relative error (default: {DEFAULT_TOLERANCE:g}).",
    )


def _execute_soft_wall(args: Any) -> BenchmarkExecution:
    if not math.isfinite(args.tolerance) or args.tolerance < 0.0:
        raise BenchmarkExecutionError(
            "tolerance must be finite and non-negative"
        )
    try:
        config = SoftWallConfig(
            kappa_gev=args.kappa,
            grid_points=args.grid_points,
            z_max_gev_inverse=args.z_max,
        )
        result = solve_spectrum(config=config, num_modes=args.modes)
    except ValueError as exc:
        raise BenchmarkExecutionError(str(exc)) from exc
    payload = result.to_dict(args.tolerance)
    return BenchmarkExecution(
        payload=payload,
        passed=result.max_relative_error <= args.tolerance,
    )


def _render_soft_wall(execution: BenchmarkExecution) -> Sequence[str]:
    payload = execution.payload
    configuration = payload["configuration"]
    lines = [
        "Quadratic soft-wall vector benchmark",
        (
            f"kappa = {configuration['kappa_gev']:g} GeV, "
            f"grid points = {configuration['grid_points']}, "
            f"z_max = {configuration['z_max_gev_inverse']:g} GeV^-1"
        ),
        " n    numerical m^2    analytic m^2    relative error",
    ]
    for record in payload["results"]:
        lines.append(
            f"{record['n']:2d}    "
            f"{record['numerical_mass_squared_gev2']:13.8f}    "
            f"{record['analytic_mass_squared_gev2']:12.8f}    "
            f"{record['relative_error']:14.6e}"
        )
    status = "PASS" if execution.passed else "FAIL"
    lines.extend(
        (
            (
                f"{status}: max relative error = "
                f"{payload['max_relative_error']:.6e}; "
                f"tolerance = {payload['tolerance']:.6e}"
            ),
            (
                "Scope: numerical reproduction of the model equation, not "
                "empirical validation."
            ),
        )
    )
    return lines


def _soft_wall_state(result: Mapping[str, Any]) -> Mapping[str, Any]:
    configuration = result["configuration"]
    return {
        "model_identifier": SOFT_WALL_MODEL_CARD.identifier,
        "ensemble": "zero-density vacuum spectral problem",
        "fixed_variables": {
            "background": "fixed AdS_5 with a quadratic dilaton",
            "sector": "transverse vector",
        },
        "approximation": "bottom-up fixed-background quadratic soft-wall model",
        "phase_branch": "normalizable transverse-vector tower",
        "parameters": {"kappa_gev": configuration["kappa_gev"]},
        "declared_controls": ["kappa_gev"],
        "boundary_source_conditions": {
            "uv": "normalizable mode; numerical Dirichlet condition",
            "ir": "normalizable mode; finite-domain Dirichlet condition",
        },
        "conventions": {
            "coordinate": "z",
            "units": "kappa in GeV, z in GeV^-1, m^2 in GeV^2",
            "observable": "ordered transverse-vector squared masses",
        },
        "source_record_versions": {
            "model_card_schema": SOFT_WALL_MODEL_CARD.schema_version,
            "model_card_sha256": SOFT_WALL_MODEL_CARD.sha256,
        },
    }


def _configure_hard_wall(parser: Any) -> None:
    parser.add_argument(
        "--z-m",
        type=float,
        default=1.0,
        help="Positive hard-wall position in GeV^-1 (default: 1.0).",
    )
    parser.add_argument(
        "--epsilon-fraction",
        type=float,
        default=1.0e-4,
        help="UV cutoff as a fraction of z_m (default: 1e-4).",
    )
    parser.add_argument(
        "--modes",
        type=int,
        default=HARD_WALL_DEFAULT_NUM_MODES,
        help=(
            "Number of lowest modes "
            f"(default: {HARD_WALL_DEFAULT_NUM_MODES})."
        ),
    )
    parser.add_argument(
        "--method",
        choices=("shooting", "collocation"),
        default="shooting",
        help="Numerical formulation (default: shooting).",
    )
    parser.add_argument(
        "--tolerance",
        type=float,
        default=DEFAULT_RATIO_TOLERANCE,
        help=(
            "Maximum accepted relative ratio error "
            f"(default: {DEFAULT_RATIO_TOLERANCE:g})."
        ),
    )


def _execute_hard_wall(args: Any) -> BenchmarkExecution:
    if not math.isfinite(args.tolerance) or args.tolerance < 0.0:
        raise BenchmarkExecutionError(
            "tolerance must be finite and non-negative"
        )
    try:
        config = HardWallConfig(
            z_m_gev_inverse=args.z_m,
            epsilon_fraction=args.epsilon_fraction,
        )
        result = solve_hard_wall_spectrum(
            config=config,
            num_modes=args.modes,
            method=args.method,
        )
    except (RuntimeError, ValueError) as exc:
        raise BenchmarkExecutionError(str(exc)) from exc
    payload = result.to_dict(args.tolerance)
    return BenchmarkExecution(
        payload=payload,
        passed=result.max_ratio_relative_error <= args.tolerance,
    )


def _render_hard_wall(execution: BenchmarkExecution) -> Sequence[str]:
    payload = execution.payload
    configuration = payload["configuration"]
    lines = [
        "Hard-wall vector benchmark",
        (
            f"method = {payload['numerical_method']['route']}, "
            f"z_m = {configuration['z_m_gev_inverse']:g} GeV^-1, "
            f"epsilon/z_m = {configuration['epsilon_fraction']:g}"
        ),
        " n    numerical m*z_m    analytic m*z_m    numerical ratio    error",
    ]
    for record in payload["results"]:
        lines.append(
            f"{record['n']:2d}    {record['numerical_m_z_m']:15.9f}    "
            f"{record['analytic_m_z_m']:14.9f}    "
            f"{record['numerical_ratio']:15.9f}    "
            f"{record['ratio_relative_error']:10.3e}"
        )
    status = "PASS" if execution.passed else "FAIL"
    lines.extend(
        (
            (
                f"{status}: max ratio relative error = "
                f"{payload['max_ratio_relative_error']:.6e}; "
                f"tolerance = {payload['tolerance']:.6e}"
            ),
            (
                "Scope: numerical reproduction of the published model equation, "
                "not precision validation."
            ),
        )
    )
    return lines


def _hard_wall_state(result: Mapping[str, Any]) -> Mapping[str, Any]:
    configuration = result["configuration"]
    return {
        "model_identifier": HARD_WALL_MODEL_CARD.identifier,
        "ensemble": "zero-density vacuum spectral problem",
        "fixed_variables": {
            "background": "fixed AdS_5 slice with an IR wall",
            "sector": "transverse vector",
        },
        "approximation": "bottom-up fixed-background hard-wall model",
        "phase_branch": "normalizable transverse-vector tower",
        "parameters": {
            "z_m_gev_inverse": configuration["z_m_gev_inverse"]
        },
        "declared_controls": ["z_m_gev_inverse"],
        "boundary_source_conditions": {
            "uv": "finite-cutoff Dirichlet condition",
            "ir": "Neumann condition at the IR wall",
        },
        "conventions": {
            "coordinate": "z",
            "units": "z_m in GeV^-1 and masses in GeV",
            "observable": "masses normalized to the lowest mode",
        },
        "source_record_versions": {
            "model_card_schema": HARD_WALL_MODEL_CARD.schema_version,
            "model_card_sha256": HARD_WALL_MODEL_CARD.sha256,
        },
    }


def _configure_superconductor(parser: Any) -> None:
    parser.add_argument(
        "--radial-cutoff",
        type=float,
        default=1.0e-5,
        help="UV and horizon cutoff in u=r_h/r (default: 1e-5).",
    )
    parser.add_argument(
        "--branch-points",
        type=int,
        default=32,
        help="Number of nonlinear continuation points (default: 32).",
    )
    parser.add_argument(
        "--plot",
        type=Path,
        default=None,
        metavar="PATH",
        help=(
            "Save the regenerated dimension-two condensate curve to PATH. "
            "Requires the plot extra."
        ),
    )


def _execute_superconductor(args: Any) -> BenchmarkExecution:
    try:
        onset_config = OnsetConfig(radial_cutoff=args.radial_cutoff)
        condensate_config = CondensateConfig(
            radial_cutoff=args.radial_cutoff,
            branch_points=args.branch_points,
        )
        result = verify_superconductor(
            onset_config=onset_config,
            condensate_config=condensate_config,
        )
        artifacts = {}
        if args.plot is not None:
            artifacts["condensate_plot"] = save_condensate_plot(result, args.plot)
    except (RuntimeError, ValueError) as exc:
        raise BenchmarkExecutionError(str(exc)) from exc
    return BenchmarkExecution(
        payload=result.to_dict(),
        passed=result.passed,
        artifacts=artifacts,
    )


def _render_superconductor(execution: BenchmarkExecution) -> Sequence[str]:
    payload = execution.payload
    result = payload["results"]
    onset = result["onset"]
    branch = result["condensate_branch"]
    lines = [
        "Probe-limit holographic-superconductor benchmark (Delta = 2)",
        "UV sources: chemical potential nonzero; scalar source psi_- = 0",
        (
            f"mu_c/r_h = {onset['critical_mu_over_horizon']:.10f}, "
            f"T_c/mu = {onset['tc_over_mu']:.10f}, "
            f"T_c/sqrt(rho) = {onset['tc_over_sqrt_rho']:.10f}"
        ),
        (
            f"nonlinear points = {len(branch['points'])}, "
            f"near-critical coefficient = {branch['near_critical_amplitude']:.6f}"
        ),
        (
            "lowest computed T/T_c = "
            f"{branch['lowest_temperature_over_tc']:.6f}, "
            "sqrt(<O_2>)/T_c = "
            f"{branch['low_temperature_sqrt_condensate_over_tc']:.6f}"
        ),
    ]
    for check in payload["acceptance_checks"]:
        status = "PASS" if check["passed"] else "FAIL"
        value = "" if "value" not in check else f"; value = {check['value']:.6e}"
        lines.append(f"{status}: {check['description']}{value}")
    plot_path = execution.artifacts.get("condensate_plot")
    if plot_path is not None:
        lines.append(f"Plot: {plot_path}")
    overall = "PASS" if execution.passed else "FAIL"
    lines.extend(
        (
            f"{overall}: all declared acceptance gates",
            (
                "Scope: numerical reproduction of the probe-limit model; not "
                "empirical material validation or a backreacted low-temperature "
                "solution."
            ),
        )
    )
    return lines


def _superconductor_state(result: Mapping[str, Any]) -> Mapping[str, Any]:
    configuration = result["configuration"]
    return {
        "model_identifier": SUPERCONDUCTOR_MODEL_CARD.identifier,
        "ensemble": "grand-canonical onset with fixed-density curve presentation",
        "fixed_variables": {
            "background": "planar AdS-Schwarzschild black brane",
            "quantization": configuration["quantization"],
        },
        "approximation": "probe limit without metric backreaction",
        "phase_branch": "normal onset plus Delta=2 condensed branch",
        "parameters": {
            "mass_squared_ads_units": configuration["mass_squared_ads_units"],
            "scalar_charge": configuration["scalar_charge"],
        },
        "declared_controls": [],
        "boundary_source_conditions": {
            "gauge": "nonzero boundary chemical-potential source",
            "scalar": "vanishing psi_- source in Delta=2 quantization",
        },
        "conventions": {
            "radial_coordinate": "u = r_h/r",
            "onset_observable": "T_c/sqrt(rho)",
            "curve_observable": "sqrt(<O_2>)/T_c",
        },
        "source_record_versions": {
            "model_card_schema": SUPERCONDUCTOR_MODEL_CARD.schema_version,
            "model_card_sha256": SUPERCONDUCTOR_MODEL_CARD.sha256,
        },
    }


def _configure_linear_axion(parser: Any) -> None:
    """Keep the scientific contract frozen at the registered defaults."""


def _execute_linear_axion(args: Any) -> BenchmarkExecution:
    del args
    try:
        result = verify_linear_axion_dc()
    except (RuntimeError, ValueError) as exc:
        raise BenchmarkExecutionError(str(exc)) from exc
    return BenchmarkExecution(payload=result.to_dict(), passed=result.passed)


def _render_linear_axion(execution: BenchmarkExecution) -> Sequence[str]:
    payload = execution.payload
    lines = [
        "Linear-axion DC-conductivity benchmark",
        (
            "Ensemble: fixed nonzero chemical-potential and linear-scalar "
            "background sources"
        ),
        "case    mu    alpha    numerical DC    exact DC    relative error",
    ]
    for case in payload["results"]["cases"]:
        diagnostics = case["diagnostics"]
        lines.append(
            f"{case['case']:>4s}  {case['chemical_potential']:5.2f}  "
            f"{case['axion_gradient']:7.4f}  "
            f"{case['fits']['real_dc_intercept']:14.9f}  "
            f"{case['exact_dc_conductivity']:10.6f}  "
            f"{diagnostics['dc_relative_error']:14.6e}"
        )
    for check in payload["acceptance_checks"]:
        status = "PASS" if check["passed"] else "FAIL"
        lines.append(
            f"{status}: {check['description']}; value = {check['value']:.6e}"
        )
    overall = "PASS" if execution.passed else "FAIL"
    lines.extend((f"{overall}: all declared acceptance gates", payload["scope"]))
    return lines


def _linear_axion_state(result: Mapping[str, Any]) -> Mapping[str, Any]:
    configuration = result["configuration"]
    return {
        "model_identifier": LINEAR_AXION_MODEL_CARD.identifier,
        "ensemble": configuration["ensemble"],
        "fixed_variables": {
            "bulk_dimension": 4,
            "horizon_scale": configuration["r0"],
            "parameter_cases": configuration["parameter_cases"],
        },
        "approximation": "classical bottom-up Einstein-Maxwell-axion model",
        "phase_branch": "charged nonextremal homogeneous black brane",
        "parameters": {
            "frequencies": configuration["frequencies"],
            "radial_audit_locations": configuration["radial_audit_locations"],
        },
        "declared_controls": [],
        "boundary_source_conditions": {
            "background_gauge": "nonzero chemical-potential source",
            "background_scalars": "nonzero linear scalar-gradient sources",
            "gauge_fluctuation": "unit electric source",
            "scalar_metric_fluctuations": (
                "zero gauge-invariant scalar/metric source"
            ),
        },
        "conventions": {
            "radial_coordinate": "r with horizon r0 = 1",
            "time_dependence": "exp(-i omega t)",
            "observable": "dimensionless electric DC conductivity",
        },
        "source_record_versions": {
            "model_card_schema": LINEAR_AXION_MODEL_CARD.schema_version,
            "model_card_sha256": LINEAR_AXION_MODEL_CARD.sha256,
        },
    }


SOFT_WALL_ADAPTER = BenchmarkAdapter(
    identifier="soft-wall-vector",
    description="Reproduce the exact quadratic soft-wall vector spectrum.",
    configure_parser=_configure_soft_wall,
    execute=_execute_soft_wall,
    render_human=_render_soft_wall,
    scientific_state=_soft_wall_state,
    model_cards=(SOFT_WALL_MODEL_CARD,),
)
HARD_WALL_ADAPTER = BenchmarkAdapter(
    identifier="hard-wall-vector",
    description="Reproduce the hard-wall vector spectrum and Bessel-zero ratios.",
    configure_parser=_configure_hard_wall,
    execute=_execute_hard_wall,
    render_human=_render_hard_wall,
    scientific_state=_hard_wall_state,
    model_cards=(HARD_WALL_MODEL_CARD,),
)
SUPERCONDUCTOR_ADAPTER = BenchmarkAdapter(
    identifier="holographic-superconductor",
    description=(
        "Reproduce the Delta=2 instability and condensate curve of "
        "arXiv:0803.3295."
    ),
    configure_parser=_configure_superconductor,
    execute=_execute_superconductor,
    render_human=_render_superconductor,
    scientific_state=_superconductor_state,
    model_cards=(SUPERCONDUCTOR_MODEL_CARD,),
)
LINEAR_AXION_ADAPTER = BenchmarkAdapter(
    identifier="linear-axion-dc",
    description=(
        "Reproduce the four-dimensional linear-axion DC conductivity."
    ),
    configure_parser=_configure_linear_axion,
    execute=_execute_linear_axion,
    render_human=_render_linear_axion,
    scientific_state=_linear_axion_state,
    model_cards=(LINEAR_AXION_MODEL_CARD,),
)
BUILTIN_BENCHMARKS = BenchmarkRegistry(
    (
        SOFT_WALL_ADAPTER,
        HARD_WALL_ADAPTER,
        SUPERCONDUCTOR_ADAPTER,
        LINEAR_AXION_ADAPTER,
    )
)


__all__ = [
    "BUILTIN_BENCHMARKS",
    "HARD_WALL_ADAPTER",
    "HARD_WALL_MODEL_CARD",
    "LINEAR_AXION_ADAPTER",
    "LINEAR_AXION_MODEL_CARD",
    "SOFT_WALL_ADAPTER",
    "SOFT_WALL_MODEL_CARD",
    "SUPERCONDUCTOR_ADAPTER",
    "SUPERCONDUCTOR_MODEL_CARD",
]
