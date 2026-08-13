"""Command adapter for the linear-axion DC-conductivity benchmark."""

from __future__ import annotations

from typing import Any, Mapping, Sequence

from holoforge.benchmarks.linear_axion_dc import verify_linear_axion_dc
from holoforge.core.registry import (
    BenchmarkAdapter,
    BenchmarkExecution,
    BenchmarkExecutionError,
    ModelCardReference,
)


LINEAR_AXION_MODEL_CARD = ModelCardReference(
    identifier="transport.linear-axion-dc.andrade-withers",
    schema_version="0.1",
    repository_path="domains/transport/linear_axion_dc/model-card.json",
    sha256="d17a1d3d12ad71ff93354b9b61146a84be06030bbb4a8016f1371ba8cc472984",
)


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


__all__ = ["LINEAR_AXION_ADAPTER", "LINEAR_AXION_MODEL_CARD"]
