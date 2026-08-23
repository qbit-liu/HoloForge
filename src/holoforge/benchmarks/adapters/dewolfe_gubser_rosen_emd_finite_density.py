"""Command adapter for the reduced finite-density DGR EMD benchmark."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping, Sequence

from holoforge.benchmarks.dewolfe_gubser_rosen_emd_critical_point import (
    save_dewolfe_gubser_rosen_emd_finite_density_artifacts,
    verify_dewolfe_gubser_rosen_emd_finite_density,
)
from holoforge.core.registry import (
    BenchmarkAdapter,
    BenchmarkExecution,
    BenchmarkExecutionError,
    ModelCardReference,
)


DEWOLFE_GUBSER_ROSEN_FINITE_DENSITY_MODEL_CARD = ModelCardReference(
    identifier="qcd.dewolfe-gubser-rosen-emd-critical-point",
    schema_version="0.1",
    repository_path=(
        "domains/qcd/dewolfe_gubser_rosen_emd_critical_point/model-card.json"
    ),
    sha256="110b6dae17de004034a2237710a81f0ee5d64e558d98501fe0be6dcd08099cb8",
)


def _configure_dewolfe_gubser_rosen_finite_density(parser: Any) -> None:
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        metavar="PATH",
        help="Save the strict JSON record, selected-state CSV, and verification plot.",
    )


def _execute_dewolfe_gubser_rosen_finite_density(
    args: Any,
) -> BenchmarkExecution:
    try:
        result = verify_dewolfe_gubser_rosen_emd_finite_density()
        artifacts = {}
        if args.output_dir is not None:
            artifacts = save_dewolfe_gubser_rosen_emd_finite_density_artifacts(
                result, args.output_dir
            )
    except (OSError, RuntimeError, ValueError) as exc:
        raise BenchmarkExecutionError(str(exc)) from exc
    return BenchmarkExecution(
        payload=result.to_dict(),
        passed=result.passed,
        artifacts=artifacts,
    )


def _render_dewolfe_gubser_rosen_finite_density(
    execution: BenchmarkExecution,
) -> Sequence[str]:
    payload = execution.payload
    critical = payload["results"]["critical"]
    source = critical["final_source_coordinates"]
    summary = payload["results"]["summary"]
    lines = [
        "DeWolfe--Gubser--Rosen finite-density EMD classical benchmark",
        "Scale: L = kappa_5 = 1; canonical density rho = q/2",
        (
            "Direct critical neighborhood: "
            f"T_c = {source['T_MeV']:.6f} MeV, "
            f"mu_c = {source['mu_MeV']:.6f} MeV"
        ),
        (
            "N=120 to 150 maximum scaled change: "
            f"{summary['maximum_final_refinement']:.6e}"
        ),
        (
            "Maximum primary/explicit observable difference: "
            f"{summary['maximum_route_observable_difference']:.6e}"
        ),
        (
            "Figure 5 absolute density ordinate: BLOCKED; retained as "
            "source provenance only"
        ),
    ]
    for check in payload["acceptance_checks"]:
        status = "PASS" if check["passed"] else "FAIL"
        value = "" if "value" not in check else f"; value = {check['value']:.6e}"
        lines.append(f"{status}: {check['description']}{value}")
    failed = [
        check["id"] for check in payload["acceptance_checks"] if not check["passed"]
    ]
    if failed:
        lines.append("HARD STOP: failed gates: " + ", ".join(failed) + ".")
    for role, path in execution.artifacts.items():
        lines.append(f"Artifact ({role}): {path}")
    overall = "PASS" if execution.passed else "FAIL"
    lines.extend((f"{overall}: all declared acceptance gates", payload["scope"]))
    return lines


def _dewolfe_gubser_rosen_finite_density_state(
    result: Mapping[str, Any],
) -> Mapping[str, Any]:
    configuration = result["configuration"]
    return {
        "model_identifier": (
            DEWOLFE_GUBSER_ROSEN_FINITE_DENSITY_MODEL_CARD.identifier
        ),
        "ensemble": configuration["ensemble"],
        "fixed_variables": {
            "bulk_dimension": configuration["bulk_dimension"],
            "units": configuration["units"],
            "degrees": configuration["degrees"],
            "canonical_density": configuration["canonical_density"],
        },
        "approximation": (
            "classical two-derivative homogeneous phenomenological bottom-up "
            "Einstein--Maxwell--dilaton background"
        ),
        "phase_branch": (
            "selected neutral and charged black-brane states plus one direct "
            "critical-coordinate neighborhood; global topology not asserted"
        ),
        "parameters": {
            "critical_initial": configuration["critical_initial"],
            "critical_phi_steps": configuration["critical_phi_steps"],
            "critical_validation_step": configuration[
                "critical_validation_step"
            ],
            "control_states": configuration["control_states"],
        },
        "declared_controls": [
            "critical_initial",
            "critical_phi_steps",
            "critical_validation_step",
            "control_states",
        ],
        "boundary_source_conditions": {
            "metric": "asymptotically AdS boundary metric with h(0)=1",
            "scalar": "unit DGR scalar-source normalization",
            "gauge": "Phi(0)=mu and regular horizon gauge Phi(1)=0",
            "horizon": "h(1)=0 with charged scalar and constraint regularity",
        },
        "conventions": {
            "radial_coordinate": "u = x/x_H in [0,1]",
            "density": configuration["canonical_density"],
            "figure_5_ordinate": configuration["source_figure_5_ordinate"],
        },
        "source_record_versions": {
            "model_card_schema": (
                DEWOLFE_GUBSER_ROSEN_FINITE_DENSITY_MODEL_CARD.schema_version
            ),
            "model_card_sha256": (
                DEWOLFE_GUBSER_ROSEN_FINITE_DENSITY_MODEL_CARD.sha256
            ),
            "primary_source_pdf_sha256": result["primary_source"]["pdf_sha256"],
            "primary_source_archive_sha256": result["primary_source"][
                "source_archive_sha256"
            ],
        },
    }


DEWOLFE_GUBSER_ROSEN_FINITE_DENSITY_ADAPTER = BenchmarkAdapter(
    identifier="dewolfe-gubser-rosen-emd-finite-density",
    description=(
        "Verify representative finite-density DGR EMD backgrounds and the "
        "reported critical-coordinate neighborhood without asserting Figure 5 "
        "absolute density or global topology."
    ),
    configure_parser=_configure_dewolfe_gubser_rosen_finite_density,
    execute=_execute_dewolfe_gubser_rosen_finite_density,
    render_human=_render_dewolfe_gubser_rosen_finite_density,
    scientific_state=_dewolfe_gubser_rosen_finite_density_state,
    model_cards=(DEWOLFE_GUBSER_ROSEN_FINITE_DENSITY_MODEL_CARD,),
)


__all__ = [
    "DEWOLFE_GUBSER_ROSEN_FINITE_DENSITY_ADAPTER",
    "DEWOLFE_GUBSER_ROSEN_FINITE_DENSITY_MODEL_CARD",
]
