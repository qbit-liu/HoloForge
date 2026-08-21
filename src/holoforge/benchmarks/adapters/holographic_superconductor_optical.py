"""Command adapter for the HHH optical-conductivity extension."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping, Sequence

from holoforge.benchmarks.holographic_superconductor_optical import (
    save_optical_diagnostic_plot,
    verify_holographic_superconductor_optical,
)
from holoforge.core.registry import (
    BenchmarkAdapter,
    BenchmarkExecution,
    BenchmarkExecutionError,
    ModelCardReference,
)


SUPERCONDUCTOR_OPTICAL_MODEL_CARD = ModelCardReference(
    identifier="condensed-matter.holographic-superconductor.hhh-optical",
    schema_version="0.1",
    repository_path=(
        "domains/condensed_matter/holographic_superconductor_optical/"
        "model-card.json"
    ),
    sha256="17c770cbf86104eb590ab735eef055582d474d54afc8e9ca61b6eaaaddca9367",
)


def _configure_superconductor_optical(parser: Any) -> None:
    parser.add_argument(
        "--plot",
        type=Path,
        default=None,
        metavar="PATH",
        help=(
            "Save an original near-critical London/pole diagnostic to PATH. "
            "This is not a source Figure 2 reproduction and requires the "
            "plot extra."
        ),
    )


def _execute_superconductor_optical(args: Any) -> BenchmarkExecution:
    try:
        result = verify_holographic_superconductor_optical()
        artifacts = {}
        if args.plot is not None:
            artifacts["near_critical_diagnostic"] = (
                save_optical_diagnostic_plot(result, args.plot)
            )
    except (OSError, RuntimeError, ValueError) as exc:
        raise BenchmarkExecutionError(str(exc)) from exc
    return BenchmarkExecution(
        payload=result.to_dict(),
        passed=result.passed,
        artifacts=artifacts,
    )


def _render_superconductor_optical(
    execution: BenchmarkExecution,
) -> Sequence[str]:
    payload = execution.payload
    near = payload["results"]["near_critical_pole"]
    figure = payload["results"]["figure_2_provenance"]
    maximum_primary_residual = max(
        response["equation_residual"]
        for point in near["points"]
        for response in point["responses"]
    )
    maximum_audit_residual = max(
        response["resolution_audit"]["equation_residual"]
        for point in near["points"]
        for response in point["responses"]
    )
    lines = [
        "HHH optical-conductivity benchmark (Delta = 2 probe limit)",
        (
            f"static London C_2 = {near['slope']:.8f}; "
            "source value = "
            f"{near['literature_coefficient']:.1f}; relative error = "
            f"{near['literature_relative_error']:.6e}"
        ),
        (
            "independent finite-frequency C_2 = "
            f"{near['finite_frequency_slope']:.8f}; maximum static/pole "
            "difference = "
            f"{near['maximum_static_pole_relative_difference']:.6e}"
        ),
        (
            f"maximum near-critical residual: primary = "
            f"{maximum_primary_residual:.6e}, audit = "
            f"{maximum_audit_residual:.6e}"
        ),
        (
            "source Figure 2 status = "
            f"{figure['status']} ({figure['acceptance_role']})"
        ),
    ]
    for check in payload["acceptance_checks"]:
        status = "PASS" if check["passed"] else "FAIL"
        value = "" if "value" not in check else f"; value = {check['value']:.6e}"
        lines.append(f"{status}: {check['description']}{value}")
    plot_path = execution.artifacts.get("near_critical_diagnostic")
    if plot_path is not None:
        lines.append(f"Diagnostic plot: {plot_path}")
    overall = "PASS" if execution.passed else "FAIL"
    lines.extend(
        (
            f"{overall}: all declared acceptance gates",
            (
                "Review state: owner-approved by Xin-Yi Liu on 2026-08-21; "
                "passing remains bounded by the recorded scope."
            ),
            payload["scope"],
        )
    )
    return lines


def _superconductor_optical_state(
    result: Mapping[str, Any],
) -> Mapping[str, Any]:
    configuration = result["configuration"]
    provenance = result["source_provenance"]
    return {
        "model_identifier": SUPERCONDUCTOR_OPTICAL_MODEL_CARD.identifier,
        "ensemble": (
            "probe-limit condensed branch with fixed-density presentation"
        ),
        "fixed_variables": {
            "background": "planar AdS4-Schwarzschild black brane",
            "quantization": configuration["quantization"],
            "spatial_momentum": 0.0,
        },
        "approximation": (
            "probe limit without metric backreaction; positive-frequency "
            "linear response and static London limit"
        ),
        "phase_branch": "Delta=2 condensed branch near T_c",
        "parameters": {
            "temperatures_over_tc": configuration["temperature_targets"][
                "near_critical"
            ],
            "frequencies_over_temperature": configuration[
                "near_critical_frequencies"
            ],
            "spectral_degrees": configuration[
                "near_critical_spectral_degrees"
            ],
        },
        "declared_controls": [],
        "boundary_source_conditions": {
            "scalar": "vanishing psi_- source in Delta=2 quantization",
            "optical": "unit A_x source with ingoing horizon response",
            "static": "regular zero-frequency London response",
        },
        "conventions": {
            "coordinate": "u = r_h/r",
            "frequency": "omega/T = 4 pi Omega/3",
            "conductivity": "sigma = -i A_1/(Omega A_0)",
            "superfluid_density": (
                "n_s/T_c = -(4 pi/3)(T/T_c) A_x'(0)/A_x(0)"
            ),
        },
        "source_record_versions": {
            "model_card_schema": (
                SUPERCONDUCTOR_OPTICAL_MODEL_CARD.schema_version
            ),
            "model_card_sha256": SUPERCONDUCTOR_OPTICAL_MODEL_CARD.sha256,
            "primary_source_pdf_sha256": provenance["pdf_sha256"],
            "primary_source_archive_sha256": provenance["archive_sha256"],
            "figure_2_status": result["results"]["figure_2_provenance"][
                "status"
            ],
        },
    }


SUPERCONDUCTOR_OPTICAL_ADAPTER = BenchmarkAdapter(
    identifier="holographic-superconductor-optical",
    description=(
        "Verify the Delta=2 HHH optical response and near-critical "
        "superfluid-density coefficient."
    ),
    configure_parser=_configure_superconductor_optical,
    execute=_execute_superconductor_optical,
    render_human=_render_superconductor_optical,
    scientific_state=_superconductor_optical_state,
    model_cards=(SUPERCONDUCTOR_OPTICAL_MODEL_CARD,),
)


__all__ = [
    "SUPERCONDUCTOR_OPTICAL_ADAPTER",
    "SUPERCONDUCTOR_OPTICAL_MODEL_CARD",
]
