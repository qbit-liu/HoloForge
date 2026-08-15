"""Command adapter for the probe-limit superconductor benchmark."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping, Sequence

from holoforge.benchmarks.holographic_superconductor import (
    CondensateConfig,
    OnsetConfig,
    save_condensate_plot,
    verify_superconductor,
)
from holoforge.core.registry import (
    BenchmarkAdapter,
    BenchmarkExecution,
    BenchmarkExecutionError,
    ModelCardReference,
)


SUPERCONDUCTOR_MODEL_CARD = ModelCardReference(
    identifier="condensed-matter.holographic-superconductor.hhh",
    schema_version="0.1",
    repository_path=(
        "domains/condensed_matter/holographic_superconductor/model-card.json"
    ),
    sha256="d1c2bffe27fd76714f84d33c062caad7b3f5bc388546f58e50736009c7e6e908",
)


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


__all__ = ["SUPERCONDUCTOR_ADAPTER", "SUPERCONDUCTOR_MODEL_CARD"]
