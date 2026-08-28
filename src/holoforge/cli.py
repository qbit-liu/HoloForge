"""Command-line interface for HoloForge verification tasks."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple

from holoforge import __version__
from holoforge.benchmarks.registry import (
    BUILTIN_BENCHMARKS,
    HARD_WALL_MODEL_CARD,
    SOFT_WALL_MODEL_CARD,
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
from holoforge.core.registry import (
    BenchmarkExecutionError,
    BenchmarkRegistry,
    BenchmarkRegistryError,
)


def build_parser(
    benchmark_registry: BenchmarkRegistry = BUILTIN_BENCHMARKS,
) -> argparse.ArgumentParser:
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
    for adapter in benchmark_registry:
        benchmark = benchmarks.add_parser(
            adapter.identifier,
            help=adapter.description,
        )
        adapter.configure_parser(benchmark)
        benchmark.add_argument(
            "--json",
            action="store_true",
            help="Emit a machine-readable result.",
        )
        _add_bundle_argument(benchmark)

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


def main(
    argv: Optional[List[str]] = None,
    *,
    benchmark_registry: BenchmarkRegistry = BUILTIN_BENCHMARKS,
) -> int:
    """Run the CLI and return a process exit code."""

    parser = build_parser(benchmark_registry)
    args = parser.parse_args(argv)

    if args.command == "audit" and args.audit_kind == "bundle":
        report = audit_evidence_bundle(args.path)
        if args.json:
            if not _emit_json(report.to_dict()):
                return 2
        else:
            _print_bundle_audit(report)
        return 0 if report.passed else 1

    if args.command == "audit" and args.audit_kind == "compatibility":
        report = audit_same_state_family(args.bundle_a, args.bundle_b)
        if args.json:
            if not _emit_json(report.to_dict()):
                return 2
        else:
            _print_compatibility_audit(report)
        return 0 if report.passed else 1

    if args.command == "verify":
        adapter = benchmark_registry.get(args.benchmark)
        try:
            execution = adapter.execute(args)
        except (BenchmarkExecutionError, BenchmarkRegistryError) as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 2
        try:
            bundle_path = _write_requested_benchmark_bundle(
                args.bundle_dir,
                adapter.identifier,
                execution.payload,
                adapter.scientific_state(execution.payload),
                tuple(reference.to_dict() for reference in adapter.model_cards),
                artifacts=execution.artifacts,
            )
        except (EvidenceBundleError, OSError) as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 2
        if args.json:
            output_payload = dict(execution.payload)
            if execution.artifacts:
                output_payload["artifacts"] = {
                    name: str(path)
                    for name, path in execution.artifacts.items()
                }
            if bundle_path is not None:
                output_payload["evidence_bundle"] = str(bundle_path)
            if not _emit_json(output_payload):
                return 2
        else:
            for line in adapter.render_human(execution):
                print(line)
            _print_bundle_path(bundle_path)
        return 0 if execution.passed else 1

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
            if not _emit_json(output_payload):
                return 2
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


def _emit_json(payload: Mapping[str, Any]) -> bool:
    """Print strict JSON or report one controlled serialization failure."""

    try:
        rendered = json.dumps(
            payload,
            allow_nan=False,
            indent=2,
            sort_keys=True,
        )
    except (TypeError, ValueError) as exc:
        print(
            f"error: JSON output is not finite and serializable: {exc}",
            file=sys.stderr,
        )
        return False
    print(rendered)
    return True


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


def _write_requested_benchmark_bundle(
    bundle_directory: Optional[Path],
    benchmark_identifier: str,
    result_record: Mapping[str, Any],
    scientific_state: Mapping[str, Any],
    model_cards: Sequence[Mapping[str, str]],
    artifacts: Optional[Mapping[str, Path]] = None,
) -> Optional[Path]:
    if bundle_directory is None:
        return None
    return write_evidence_bundle(
        bundle_directory,
        command_identity=f"verify {benchmark_identifier}",
        result_record=result_record,
        scientific_state=scientific_state,
        model_card_references=model_cards,
        artifacts=artifacts,
    )


def _bundle_profile(
    command_identity: str, result: Mapping[str, Any]
) -> Tuple[Mapping[str, Any], Sequence[Mapping[str, str]]]:
    """Return explicit public compatibility metadata for current commands."""

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
                    "soft_wall_model_card_sha256": SOFT_WALL_MODEL_CARD.sha256,
                    "hard_wall_model_card_sha256": HARD_WALL_MODEL_CARD.sha256,
                },
            },
            (
                SOFT_WALL_MODEL_CARD.to_dict(),
                HARD_WALL_MODEL_CARD.to_dict(),
            ),
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
