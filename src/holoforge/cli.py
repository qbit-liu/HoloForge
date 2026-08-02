"""Command-line interface for HoloForge verification tasks."""

from __future__ import annotations

import argparse
import json
import math
import sys
from typing import List, Optional

from holoforge import __version__
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
