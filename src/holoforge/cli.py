"""Command-line interface for HoloForge verification tasks."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import sys
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple

from holoforge import __version__
from holoforge.benchmarks.hard_wall_vector import (
    DEFAULT_NUM_MODES as HARD_WALL_DEFAULT_NUM_MODES,
    DEFAULT_RATIO_TOLERANCE,
    HardWallConfig,
    HardWallSpectrumResult,
    solve_hard_wall_spectrum,
)
from holoforge.benchmarks.holographic_superconductor import (
    CondensateConfig,
    OnsetConfig,
    SuperconductorVerificationResult,
    save_condensate_plot,
    verify_superconductor,
)
from holoforge.benchmarks.soft_wall_vector import (
    DEFAULT_GRID_POINTS,
    DEFAULT_NUM_MODES,
    DEFAULT_TOLERANCE,
    SoftWallConfig,
    SpectrumResult,
    solve_spectrum,
)
from holoforge.comparisons.vector_spectrum import (
    VectorSpectrumComparisonResult,
    build_vector_spectrum_comparison,
    render_vector_spectrum_table,
    save_vector_spectrum_artifacts,
)
from holoforge.core.evidence import (
    BundleAuditResult,
    CompatibilityAuditResult,
    EvidenceBundleError,
    audit_evidence_bundle,
    audit_same_state_family,
    write_evidence_bundle,
)


_SOFT_WALL_MODEL_CARD = {
    "id": "qcd.soft-wall-vector.kkss",
    "schema_version": "0.1",
    "repository_path": "domains/qcd/soft_wall_vector/model-card.json",
    "sha256": "6cb2a0f2824d279b68e20da5c8304d5ef68676649815ee6bd0816ec0f385d2fd",
}
_HARD_WALL_MODEL_CARD = {
    "id": "qcd.hard-wall-vector.ekss",
    "schema_version": "0.1",
    "repository_path": "domains/qcd/hard_wall_vector/model-card.json",
    "sha256": "96aeff5ed6d970dbb90d5c0dd458e579ee449a871edc494e43899a1003c13c61",
}
_SUPERCONDUCTOR_MODEL_CARD = {
    "id": "condensed-matter.holographic-superconductor.hhh",
    "schema_version": "0.1",
    "repository_path": (
        "domains/condensed_matter/holographic_superconductor/model-card.json"
    ),
    "sha256": "d1c2bffe27fd76714f84d33c062caad7b3f5bc388546f58e50736009c7e6e908",
}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="holoforge",
        description="Verification-first bottom-up gauge/gravity tools.",
    )
    parser.add_argument("--version", action="version", version=__version__)
    commands = parser.add_subparsers(dest="command", required=True)

    verify = commands.add_parser(
        "verify", help="Run a benchmark with an explicit acceptance gate."
    )
    benchmarks = verify.add_subparsers(dest="benchmark", required=True)

    soft_wall = benchmarks.add_parser(
        "soft-wall-vector",
        help="Reproduce the exact quadratic soft-wall vector spectrum.",
    )
    soft_wall.add_argument(
        "--kappa",
        type=float,
        default=1.0,
        help="Positive soft-wall scale in GeV (default: 1.0).",
    )

    soft_wall.add_argument(
        "--modes",
        type=int,
        default=DEFAULT_NUM_MODES,
        help=f"Number of lowest modes (default: {DEFAULT_NUM_MODES}).",
    )
    soft_wall.add_argument(
        "--grid-points",
        type=int,
        default=DEFAULT_GRID_POINTS,
        help=(
            "Number of interior finite-difference points "
            f"(default: {DEFAULT_GRID_POINTS})."
        ),
    )
    soft_wall.add_argument(
        "--z-max",
        type=float,
        default=None,
        help="IR boundary in GeV^-1 (default: 10/kappa).",
    )
    soft_wall.add_argument(
        "--tolerance",
        type=float,
        default=DEFAULT_TOLERANCE,
        help=f"Maximum accepted relative error (default: {DEFAULT_TOLERANCE:g}).",
    )
    soft_wall.add_argument(
        "--json", action="store_true", help="Emit a machine-readable result."
    )
    _add_bundle_argument(soft_wall)

    hard_wall = benchmarks.add_parser(
        "hard-wall-vector",
        help="Reproduce the hard-wall vector spectrum and Bessel-zero ratios.",
    )
    hard_wall.add_argument(
        "--z-m",
        type=float,
        default=1.0,
        help="Positive hard-wall position in GeV^-1 (default: 1.0).",
    )
    hard_wall.add_argument(
        "--epsilon-fraction",
        type=float,
        default=1.0e-4,
        help="UV cutoff as a fraction of z_m (default: 1e-4).",
    )
    hard_wall.add_argument(
        "--modes",
        type=int,
        default=HARD_WALL_DEFAULT_NUM_MODES,
        help=(
            "Number of lowest modes "
            f"(default: {HARD_WALL_DEFAULT_NUM_MODES})."
        ),
    )
    hard_wall.add_argument(
        "--method",
        choices=("shooting", "collocation"),
        default="shooting",
        help="Numerical formulation (default: shooting).",
    )
    hard_wall.add_argument(
        "--tolerance",
        type=float,
        default=DEFAULT_RATIO_TOLERANCE,
        help=(
            "Maximum accepted relative ratio error "
            f"(default: {DEFAULT_RATIO_TOLERANCE:g})."
        ),
    )
    hard_wall.add_argument(
        "--json", action="store_true", help="Emit a machine-readable result."
    )
    _add_bundle_argument(hard_wall)

    superconductor = benchmarks.add_parser(
        "holographic-superconductor",
        help=(
            "Reproduce the Delta=2 instability and condensate curve of "
            "arXiv:0803.3295."
        ),
    )
    superconductor.add_argument(
        "--radial-cutoff",
        type=float,
        default=1.0e-5,
        help="UV and horizon cutoff in u=r_h/r (default: 1e-5).",
    )

    superconductor.add_argument(
        "--branch-points",
        type=int,
        default=32,
        help="Number of nonlinear continuation points (default: 32).",
    )
    superconductor.add_argument(
        "--plot",
        type=Path,
        default=None,
        metavar="PATH",
        help=(
            "Save the regenerated dimension-two condensate curve to PATH. "
            "Requires the plot extra."
        ),
    )
    superconductor.add_argument(
        "--json", action="store_true", help="Emit a machine-readable result."
    )
    _add_bundle_argument(superconductor)

    compare = commands.add_parser(
        "compare", help="Compare established constructions on one observable."
    )
    comparisons = compare.add_subparsers(dest="comparison", required=True)
    vector_comparison = comparisons.add_parser(
        "vector-spectrum",
        help="Compare soft-wall and hard-wall radial vector-meson ratios.",
    )
    vector_comparison.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        metavar="PATH",
        help="Save JSON, Markdown, and a plot under PATH.",
    )
    vector_comparison.add_argument(
        "--no-plot",
        action="store_true",
        help="When saving artifacts, omit the optional Matplotlib plot.",
    )
    vector_comparison.add_argument(
        "--json", action="store_true", help="Emit a machine-readable result."
    )
    _add_bundle_argument(vector_comparison)

    audit = commands.add_parser(
        "audit", help="Audit evidence-bundle integrity or compatibility."
    )
    audit_kinds = audit.add_subparsers(dest="audit_kind", required=True)
    bundle_audit = audit_kinds.add_parser(
        "bundle", help="Verify one portable evidence bundle."
    )
    bundle_audit.add_argument("path", type=Path, metavar="PATH")
    bundle_audit.add_argument(
        "--json", action="store_true", help="Emit a machine-readable report."
    )
    compatibility_audit = audit_kinds.add_parser(
        "compatibility", help="Compare declared scientific-state metadata."
    )
    compatibility_audit.add_argument("bundle_a", type=Path, metavar="BUNDLE_A")
    compatibility_audit.add_argument("bundle_b", type=Path, metavar="BUNDLE_B")
    compatibility_audit.add_argument(
        "--relation",
        choices=("same-state-family",),
        default="same-state-family",
        help="Compatibility relation (default: same-state-family).",
    )
    compatibility_audit.add_argument(
        "--json", action="store_true", help="Emit a machine-readable report."
    )

    return parser


def main(argv: Optional[List[str]] = None) -> int:
    """Run the CLI and return a process exit code."""

    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "audit" and args.audit_kind == "bundle":
        report = audit_evidence_bundle(args.path)
        if args.json:
            print(json.dumps(report.to_dict(), indent=2, sort_keys=True))
        else:
            _print_bundle_audit(report)
        return 0 if report.passed else 1

    if args.command == "audit" and args.audit_kind == "compatibility":
        report = audit_same_state_family(args.bundle_a, args.bundle_b)
        if args.json:
            print(json.dumps(report.to_dict(), indent=2, sort_keys=True))
        else:
            _print_compatibility_audit(report)
        return 0 if report.passed else 1

    if args.command == "verify" and args.benchmark == "soft-wall-vector":
        if not math.isfinite(args.tolerance) or args.tolerance < 0.0:
            print("error: tolerance must be finite and non-negative", file=sys.stderr)
            return 2
        try:
            config = SoftWallConfig(
                kappa_gev=args.kappa,
                grid_points=args.grid_points,
                z_max_gev_inverse=args.z_max,
            )
            result = solve_spectrum(config=config, num_modes=args.modes)
        except ValueError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 2

        payload = result.to_dict(args.tolerance)
        try:
            bundle_path = _write_requested_bundle(
                args.bundle_dir,
                "verify soft-wall-vector",
                payload,
            )
        except (EvidenceBundleError, OSError) as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 2
        if args.json:
            output_payload = dict(payload)
            if bundle_path is not None:
                output_payload["evidence_bundle"] = str(bundle_path)
            print(json.dumps(output_payload, indent=2, sort_keys=True))
        else:
            _print_human_result(result, args.tolerance)
            _print_bundle_path(bundle_path)
        return 0 if result.max_relative_error <= args.tolerance else 1

    if args.command == "verify" and args.benchmark == "hard-wall-vector":
        if not math.isfinite(args.tolerance) or args.tolerance < 0.0:
            print("error: tolerance must be finite and non-negative", file=sys.stderr)
            return 2
        try:
            config = HardWallConfig(
                z_m_gev_inverse=args.z_m,
                epsilon_fraction=args.epsilon_fraction,
            )
            hard_wall_result = solve_hard_wall_spectrum(
                config=config,
                num_modes=args.modes,
                method=args.method,
            )
        except (RuntimeError, ValueError) as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 2

        payload = hard_wall_result.to_dict(args.tolerance)
        try:
            bundle_path = _write_requested_bundle(
                args.bundle_dir,
                "verify hard-wall-vector",
                payload,
            )
        except (EvidenceBundleError, OSError) as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 2
        if args.json:
            output_payload = dict(payload)
            if bundle_path is not None:
                output_payload["evidence_bundle"] = str(bundle_path)
            print(json.dumps(output_payload, indent=2, sort_keys=True))
        else:
            _print_hard_wall_result(hard_wall_result, args.tolerance)
            _print_bundle_path(bundle_path)
        return (
            0
            if hard_wall_result.max_ratio_relative_error <= args.tolerance
            else 1
        )

    if args.command == "verify" and args.benchmark == "holographic-superconductor":
        try:
            onset_config = OnsetConfig(radial_cutoff=args.radial_cutoff)
            condensate_config = CondensateConfig(
                radial_cutoff=args.radial_cutoff,
                branch_points=args.branch_points,
            )
            superconductor_result = verify_superconductor(
                onset_config=onset_config,
                condensate_config=condensate_config,
            )
            plot_path = None
            if args.plot is not None:
                plot_path = save_condensate_plot(
                    superconductor_result, args.plot
                )
        except (RuntimeError, ValueError) as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 2

        payload = superconductor_result.to_dict()
        bundle_artifacts = None
        if plot_path is not None:
            bundle_artifacts = {"condensate_plot": plot_path}
        try:
            bundle_path = _write_requested_bundle(
                args.bundle_dir,
                "verify holographic-superconductor",
                payload,
                artifacts=bundle_artifacts,
            )
        except (EvidenceBundleError, OSError) as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 2
        if args.json:
            output_payload = dict(payload)
            if plot_path is not None:
                output_payload["artifacts"] = {
                    "condensate_plot": str(plot_path)
                }
            if bundle_path is not None:
                output_payload["evidence_bundle"] = str(bundle_path)
            print(json.dumps(output_payload, indent=2, sort_keys=True))
        else:
            _print_superconductor_result(superconductor_result, plot_path)
            _print_bundle_path(bundle_path)
        return 0 if superconductor_result.passed else 1

    if args.command == "compare" and args.comparison == "vector-spectrum":
        try:
            comparison_result = build_vector_spectrum_comparison()
            artifacts = None
            if args.output_dir is not None:
                artifacts = save_vector_spectrum_artifacts(
                    comparison_result,
                    args.output_dir,
                    include_plot=not args.no_plot,
                )
        except (RuntimeError, ValueError) as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 2

        payload = comparison_result.to_dict()
        bundle_artifacts = None
        if artifacts is not None:
            bundle_artifacts = {
                name: Path(path) for name, path in artifacts.items()
            }
        try:
            bundle_path = _write_requested_bundle(
                args.bundle_dir,
                "compare vector-spectrum",
                payload,
                artifacts=bundle_artifacts,
            )
        except (EvidenceBundleError, OSError) as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 2
        if args.json:
            output_payload = dict(payload)
            if artifacts is not None:
                output_payload["artifacts"] = artifacts
            if bundle_path is not None:
                output_payload["evidence_bundle"] = str(bundle_path)
            print(json.dumps(output_payload, indent=2, sort_keys=True))
        else:
            _print_vector_spectrum_comparison(comparison_result, artifacts)
            _print_bundle_path(bundle_path)
        return 0 if comparison_result.passed else 1

    parser.error("unsupported command")
    return 2


def _add_bundle_argument(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--bundle-dir",
        type=Path,
        default=None,
        metavar="PATH",
        help=(
            "Write a portable evidence bundle to a new or empty directory. "
            "Existing command behavior is unchanged when omitted."
        ),
    )


def _write_requested_bundle(
    bundle_directory: Optional[Path],
    command_identity: str,
    result_record: Mapping[str, Any],
    artifacts: Optional[Mapping[str, Path]] = None,
) -> Optional[Path]:
    if bundle_directory is None:
        return None
    state, model_cards = _bundle_profile(command_identity, result_record)
    return write_evidence_bundle(
        bundle_directory,
        command_identity=command_identity,
        result_record=result_record,
        scientific_state=state,
        model_card_references=model_cards,
        artifacts=artifacts,
    )


def _bundle_profile(
    command_identity: str, result: Mapping[str, Any]
) -> Tuple[Mapping[str, Any], Sequence[Mapping[str, str]]]:
    """Return explicit public compatibility metadata for current commands."""

    if command_identity == "verify soft-wall-vector":
        configuration = result["configuration"]
        return (
            {
                "model_identifier": _SOFT_WALL_MODEL_CARD["id"],
                "ensemble": "zero-density vacuum spectral problem",
                "fixed_variables": {
                    "background": "fixed AdS_5 with a quadratic dilaton",
                    "sector": "transverse vector",
                },
                "approximation": (
                    "bottom-up fixed-background quadratic soft-wall model"
                ),
                "phase_branch": "normalizable transverse-vector tower",
                "parameters": {
                    "kappa_gev": configuration["kappa_gev"],
                },
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
                    "model_card_schema": _SOFT_WALL_MODEL_CARD["schema_version"],
                    "model_card_sha256": _SOFT_WALL_MODEL_CARD["sha256"],
                },
            },
            (_SOFT_WALL_MODEL_CARD,),
        )

    if command_identity == "verify hard-wall-vector":
        configuration = result["configuration"]
        return (
            {
                "model_identifier": _HARD_WALL_MODEL_CARD["id"],
                "ensemble": "zero-density vacuum spectral problem",
                "fixed_variables": {
                    "background": "fixed AdS_5 slice with an IR wall",
                    "sector": "transverse vector",
                },
                "approximation": "bottom-up fixed-background hard-wall model",
                "phase_branch": "normalizable transverse-vector tower",
                "parameters": {
                    "z_m_gev_inverse": configuration["z_m_gev_inverse"],
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
                    "model_card_schema": _HARD_WALL_MODEL_CARD["schema_version"],
                    "model_card_sha256": _HARD_WALL_MODEL_CARD["sha256"],
                },
            },
            (_HARD_WALL_MODEL_CARD,),
        )

    if command_identity == "verify holographic-superconductor":
        configuration = result["configuration"]
        return (
            {
                "model_identifier": _SUPERCONDUCTOR_MODEL_CARD["id"],
                "ensemble": (
                    "grand-canonical onset with fixed-density curve presentation"
                ),
                "fixed_variables": {
                    "background": "planar AdS-Schwarzschild black brane",
                    "quantization": configuration["quantization"],
                },
                "approximation": "probe limit without metric backreaction",
                "phase_branch": "normal onset plus Delta=2 condensed branch",
                "parameters": {
                    "mass_squared_ads_units": configuration[
                        "mass_squared_ads_units"
                    ],
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
                    "model_card_schema": _SUPERCONDUCTOR_MODEL_CARD[
                        "schema_version"
                    ],
                    "model_card_sha256": _SUPERCONDUCTOR_MODEL_CARD["sha256"],
                },
            },
            (_SUPERCONDUCTOR_MODEL_CARD,),
        )

    if command_identity == "compare vector-spectrum":
        reference = result["reference"]
        return (
            {
                "model_identifier": (
                    "comparison.soft-wall-hard-wall-vector-ratios"
                ),
                "ensemble": "controlled zero-density spectrum comparison",
                "fixed_variables": {
                    "observable": "radial vector-mode mass ratios",
                    "anchor_index": reference["anchor_index"],
                },
                "approximation": (
                    "controlled comparison of two bottom-up constructions"
                ),
                "phase_branch": "candidate radial vector-spectrum assignments",
                "parameters": {
                    "reference_dataset": reference["dataset_id"],
                },
                "declared_controls": [],
                "boundary_source_conditions": {
                    "comparison": (
                        "each construction retains its documented boundary "
                        "conditions"
                    )
                },
                "conventions": {
                    "normalization": "m_n/m_0",
                    "reference_anchor": "lowest included state",
                    "metrics": "descriptive and not acceptance gates",
                },
                "source_record_versions": {
                    "comparison_schema": str(result["schema_version"]),
                    "reference_dataset_schema": "0.3",
                    "soft_wall_model_card_sha256": _SOFT_WALL_MODEL_CARD[
                        "sha256"
                    ],
                    "hard_wall_model_card_sha256": _HARD_WALL_MODEL_CARD[
                        "sha256"
                    ],
                },
            },
            (_SOFT_WALL_MODEL_CARD, _HARD_WALL_MODEL_CARD),
        )

    raise EvidenceBundleError(f"no evidence-bundle profile for {command_identity}")


def _print_bundle_path(bundle_path: Optional[Path]) -> None:
    if bundle_path is not None:
        print(f"Evidence bundle: {bundle_path}")


def _print_bundle_audit(report: BundleAuditResult) -> None:
    for check in report.checks:
        status = "PASS" if check["passed"] else "FAIL"
        print(f"{status}: {check['id']} - {check['detail']}")
    overall = "PASS" if report.passed else "FAIL"
    print(f"{overall}: portable evidence-bundle audit")
    print("Scope: integrity and declared provenance, not scientific validation.")


def _print_compatibility_audit(report: CompatibilityAuditResult) -> None:
    if report.mismatches:
        for mismatch in report.mismatches:
            print(f"FAIL: {mismatch['field']} - {mismatch['reason']}")
    else:
        print("PASS: all required same-state-family metadata matches")
    for change in report.control_changes:
        print(
            f"CONTROL: {change['field']} changed from "
            f"{change['left']} to {change['right']}"
        )
    overall = "PASS" if report.passed else "FAIL"
    print(f"{overall}: same-state-family compatibility preflight")
    print("Scope: declared compatibility, not physical correctness or novelty.")


def _print_human_result(result: SpectrumResult, tolerance: float) -> None:
    print("Quadratic soft-wall vector benchmark")
    print(
        f"kappa = {result.config.kappa_gev:g} GeV, "
        f"grid points = {result.config.grid_points}, "
        f"z_max = {result.config.resolved_z_max_gev_inverse:g} GeV^-1"
    )
    print(" n    numerical m^2    analytic m^2    relative error")
    for n, numerical, analytic, error in zip(
        result.mode_numbers,
        result.numerical_mass_squared_gev2,
        result.analytic_mass_squared_gev2,
        result.relative_errors,
    ):
        print(f"{n:2d}    {numerical:13.8f}    {analytic:12.8f}    {error:14.6e}")
    status = "PASS" if result.max_relative_error <= tolerance else "FAIL"
    print(
        f"{status}: max relative error = {result.max_relative_error:.6e}; "
        f"tolerance = {tolerance:.6e}"
    )
    print(
        "Scope: numerical reproduction of the model equation, not empirical "
        "validation."
    )


def _print_hard_wall_result(
    result: HardWallSpectrumResult, tolerance: float
) -> None:
    print("Hard-wall vector benchmark")
    print(
        f"method = {result.method}, z_m = {result.config.z_m_gev_inverse:g} "
        f"GeV^-1, epsilon/z_m = {result.config.epsilon_fraction:g}"
    )
    print(" n    numerical m*z_m    analytic m*z_m    numerical ratio    error")
    for index, numerical, analytic, ratio, error in zip(
        range(len(result.dimensionless_masses)),
        result.dimensionless_masses,
        result.analytic_dimensionless_masses,
        result.mass_ratios,
        result.ratio_relative_errors,
    ):
        print(
            f"{index:2d}    {numerical:15.9f}    {analytic:14.9f}    "
            f"{ratio:15.9f}    {error:10.3e}"
        )
    status = "PASS" if result.max_ratio_relative_error <= tolerance else "FAIL"
    print(
        f"{status}: max ratio relative error = "
        f"{result.max_ratio_relative_error:.6e}; tolerance = {tolerance:.6e}"
    )
    print(
        "Scope: numerical reproduction of the published model equation, not "
        "precision validation."
    )


def _print_superconductor_result(
    result: SuperconductorVerificationResult,
    plot_path: Optional[Path],
) -> None:
    onset = result.onset
    branch = result.branch
    low_point = branch.lowest_temperature_point
    print("Probe-limit holographic-superconductor benchmark (Delta = 2)")
    print("UV sources: chemical potential nonzero; scalar source psi_- = 0")
    print(
        f"mu_c/r_h = {onset.critical_mu_over_horizon:.10f}, "
        f"T_c/mu = {onset.tc_over_mu:.10f}, "
        f"T_c/sqrt(rho) = {onset.tc_over_sqrt_rho:.10f}"
    )
    print(
        f"nonlinear points = {len(branch.points)}, "
        f"near-critical coefficient = {branch.near_critical_amplitude:.6f}"
    )
    print(
        "lowest computed T/T_c = "
        f"{low_point.temperature_over_tc:.6f}, "
        "sqrt(<O_2>)/T_c = "
        f"{low_point.sqrt_condensate_over_tc:.6f}"
    )
    for check in result.acceptance_checks:
        status = "PASS" if check.passed else "FAIL"
        value = "" if check.value is None else f"; value = {check.value:.6e}"
        print(f"{status}: {check.description}{value}")
    if plot_path is not None:
        print(f"Plot: {plot_path}")
    overall = "PASS" if result.passed else "FAIL"
    print(f"{overall}: all declared acceptance gates")
    print(
        "Scope: numerical reproduction of the probe-limit model; not empirical "
        "material validation or a backreacted low-temperature solution."
    )


def _print_vector_spectrum_comparison(
    result: VectorSpectrumComparisonResult,
    artifacts: Optional[Dict[str, str]],
) -> None:
    print(render_vector_spectrum_table(result), end="")
    print("PASS: all numerical reproduction gates" if result.passed else "FAIL")
    print(
        "Reference review status: "
        f"{result.reference.dataset['provenance']['review_status']}"
    )
    if artifacts is not None:
        for name, path in sorted(artifacts.items()):
            print(f"Artifact ({name}): {path}")
