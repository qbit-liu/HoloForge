"""Command-line interface for HoloForge verification tasks."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import sys
from typing import List, Optional

from holoforge import __version__
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
        help=f"Number of interior finite-difference points (default: {DEFAULT_GRID_POINTS}).",
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

    return parser


def main(argv: Optional[List[str]] = None) -> int:
    """Run the CLI and return a process exit code."""

    parser = build_parser()
    args = parser.parse_args(argv)

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

        if args.json:
            print(json.dumps(result.to_dict(args.tolerance), indent=2, sort_keys=True))
        else:
            _print_human_result(result, args.tolerance)
        return 0 if result.max_relative_error <= args.tolerance else 1

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

        if args.json:
            payload = superconductor_result.to_dict()
            if plot_path is not None:
                payload["artifacts"] = {"condensate_plot": str(plot_path)}
            print(json.dumps(payload, indent=2, sort_keys=True))
        else:
            _print_superconductor_result(superconductor_result, plot_path)
        return 0 if superconductor_result.passed else 1

    parser.error("unsupported command")
    return 2


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
    print("Scope: numerical reproduction of the model equation, not empirical validation.")


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
