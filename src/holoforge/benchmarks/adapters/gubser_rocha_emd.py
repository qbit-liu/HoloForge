"""Command adapter for the Gubser--Rocha charged EMD benchmark."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping, Sequence

from holoforge.benchmarks.gubser_rocha_emd import (
    save_gubser_rocha_artifacts,
    verify_gubser_rocha_emd,
)
from holoforge.core.registry import (
    BenchmarkAdapter,
    BenchmarkExecution,
    BenchmarkExecutionError,
    ModelCardReference,
)


GUBSER_ROCHA_MODEL_CARD = ModelCardReference(
    identifier="condensed-matter.gubser-rocha-emd",
    schema_version="0.1",
    repository_path="domains/condensed_matter/gubser_rocha_emd/model-card.json",
    sha256="2b8fe071b7bd11a304f81b5ea5dd66cfa06ed24b439dc74ce6a9804a8e606a63",
)


def _configure_gubser_rocha(parser: Any) -> None:
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        metavar="PATH",
        help="Save the strict JSON record, seven-case CSV, and verification plot.",
    )


def _execute_gubser_rocha(args: Any) -> BenchmarkExecution:
    try:
        result = verify_gubser_rocha_emd()
        artifacts = {}
        if args.output_dir is not None:
            artifacts = save_gubser_rocha_artifacts(result, args.output_dir)
    except (OSError, RuntimeError, ValueError) as exc:
        raise BenchmarkExecutionError(str(exc)) from exc
    return BenchmarkExecution(
        payload=result.to_dict(),
        passed=result.passed,
        artifacts=artifacts,
    )


def _render_gubser_rocha(execution: BenchmarkExecution) -> Sequence[str]:
    payload = execution.payload
    lines = [
        "Gubser--Rocha top-down-derived EMD control benchmark",
        "Scale: L = r_H = 1; fixed source Omega at each xi",
        "xi    max equation residual    max exact-field error    T              hat s",
    ]
    for case in payload["results"]["cases"]:
        diagnostics = case["diagnostics"]
        thermo = case["thermodynamics"]
        lines.append(
            f"{case['xi']:4.1f}  "
            f"{diagnostics['maximum_equation_residual']:21.6e}  "
            f"{diagnostics['maximum_exact_field_error']:21.6e}  "
            f"{thermo['temperature']:13.9f}  {thermo['hat_s']:13.9f}"
        )
    for check in payload["acceptance_checks"]:
        status = "PASS" if check["passed"] else "FAIL"
        value = "" if "value" not in check else f"; value = {check['value']:.6e}"
        lines.append(f"{status}: {check['description']}{value}")
    ordering_failures = payload["results"]["refinement"]["ordering_failures"]
    failed_gates = [
        check["id"] for check in payload["acceptance_checks"] if not check["passed"]
    ]
    if failed_gates:
        lines.append(
            "HARD STOP: failed gates: " + ", ".join(failed_gates) + "."
        )
    if ordering_failures:
        lines.append(
            f"Detail: {ordering_failures} amended refinement-ordering "
            "comparisons failed; no further threshold revision is authorized."
        )
    for role, path in execution.artifacts.items():
        lines.append(f"Artifact ({role}): {path}")
    overall = "PASS" if execution.passed else "FAIL"
    lines.extend((f"{overall}: all declared acceptance gates", payload["scope"]))
    return lines


def _gubser_rocha_state(result: Mapping[str, Any]) -> Mapping[str, Any]:
    configuration = result["configuration"]
    return {
        "model_identifier": GUBSER_ROCHA_MODEL_CARD.identifier,
        "ensemble": configuration["ensemble"],
        "fixed_variables": {
            "bulk_dimension": configuration["bulk_dimension"],
            "units": configuration["units"],
            "reported_xi": configuration["reported_xi"],
            "instability_threshold_xi": configuration["instability_threshold_xi"],
        },
        "approximation": (
            "top-down-derived classical two-derivative homogeneous equal-charge "
            "Einstein--Maxwell--dilaton background used as a numerical control"
        ),
        "phase_branch": (
            "homogeneous equal-charge analytic branch; xi > 1 is verification "
            "only and not asserted stable"
        ),
        "parameters": {
            "continuation_xi": configuration["continuation_xi"],
            "degrees": configuration["degrees"],
            "polish_maximum_evaluations": configuration[
                "polish_maximum_evaluations"
            ],
            "polish_trigger_tolerance": configuration[
                "polish_trigger_tolerance"
            ],
            "collocation_tolerance": configuration[
                "collocation_tolerance"
            ],
            "refinement_order_floor": configuration[
                "refinement_order_floor"
            ],
        },
        "declared_controls": [
            "polish_maximum_evaluations",
            "polish_trigger_tolerance",
            "collocation_tolerance",
            "refinement_order_floor",
        ],
        "boundary_source_conditions": {
            "metric": "asymptotically AdS boundary metric and f(0)=1",
            "scalar": "zero BF-bound logarithmic source",
            "gauge": "Phi(0)=-Omega and regular horizon gauge Phi(1)=0",
            "horizon": "f(1)=0 with retained scalar regularity equation",
        },
        "conventions": {
            "radial_coordinate": "u = z/z_H in [0,1]",
            "canonical_scalar": "phi = 2 sqrt(6) alpha",
            "black_hole_parameter": "mu_bh is distinct from Omega",
        },
        "source_record_versions": {
            "model_card_schema": GUBSER_ROCHA_MODEL_CARD.schema_version,
            "model_card_sha256": GUBSER_ROCHA_MODEL_CARD.sha256,
            "primary_source_pdf_sha256": result["primary_source"]["pdf_sha256"],
            "primary_source_archive_sha256": result["primary_source"][
                "source_archive_sha256"
            ],
        },
    }


GUBSER_ROCHA_ADAPTER = BenchmarkAdapter(
    identifier="gubser-rocha-emd",
    description=(
        "Verify the top-down-derived homogeneous charged Gubser--Rocha EMD "
        "background and source thermodynamics as a numerical control."
    ),
    configure_parser=_configure_gubser_rocha,
    execute=_execute_gubser_rocha,
    render_human=_render_gubser_rocha,
    scientific_state=_gubser_rocha_state,
    model_cards=(GUBSER_ROCHA_MODEL_CARD,),
)


__all__ = ["GUBSER_ROCHA_ADAPTER", "GUBSER_ROCHA_MODEL_CARD"]
