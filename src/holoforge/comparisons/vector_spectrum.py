"""Controlled soft-wall versus hard-wall vector-spectrum comparison."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any, Dict, Mapping, Tuple

import numpy as np
from numpy.typing import NDArray

from holoforge.benchmarks.hard_wall_vector import (
    DEFAULT_CROSS_SOLVER_TOLERANCE,
    DEFAULT_RATIO_TOLERANCE,
    HardWallRefinementResult,
    hard_wall_cutoff_refinement,
    solve_hard_wall_spectrum,
)
from holoforge.benchmarks.soft_wall_vector import (
    DEFAULT_TOLERANCE as SOFT_WALL_TOLERANCE,
    SoftWallConfig,
    solve_spectrum,
)
from holoforge.core import AcceptanceCheck, runtime_versions
from holoforge.reference_data import (
    ReferenceMassSpectrum,
    load_pdg_2024_rho_spectrum,
)


COMPARISON_ID = "soft-wall-hard-wall-vector-ratios"


@dataclass(frozen=True)
class SpectrumPrediction:
    """One construction evaluated on the reference dataset's mode labels."""

    identifier: str
    label: str
    construction: str
    calibration: str
    solver: str
    model_modes: NDArray[np.int64]
    ratios: NDArray[np.float64]
    analytic_ratios: NDArray[np.float64]
    numerical_absolute_errors: NDArray[np.float64]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.identifier,
            "label": self.label,
            "construction": self.construction,
            "calibration": self.calibration,
            "solver": self.solver,
            "entries": [
                {
                    "model_mode": int(mode),
                    "ratio": float(ratio),
                    "analytic_ratio": float(analytic),
                    "numerical_absolute_error": float(error),
                }
                for mode, ratio, analytic, error in zip(
                    self.model_modes,
                    self.ratios,
                    self.analytic_ratios,
                    self.numerical_absolute_errors,
                )
            ],
        }


@dataclass(frozen=True)
class DescriptiveModelComparison:
    """Covariance-aware residual summary that is not an acceptance gate."""

    model_id: str
    model_modes: NDArray[np.int64]
    residuals: NDArray[np.float64]
    compared_positions: NDArray[np.int64]
    chi_square: float
    degrees_of_freedom: int

    def to_dict(self) -> Dict[str, Any]:
        return {
            "model_id": self.model_id,
            "entries": [
                {
                    "model_mode": int(mode),
                    "residual": float(residual),
                    "included_in_chi_square": bool(index in self.compared_positions),
                }
                for index, (mode, residual) in enumerate(
                    zip(self.model_modes, self.residuals)
                )
            ],
            "chi_square": self.chi_square,
            "degrees_of_freedom": self.degrees_of_freedom,
            "chi_square_per_dof": self.chi_square / self.degrees_of_freedom,
            "covariance": "frozen reference-data ratio covariance",
            "is_acceptance_gate": False,
        }


@dataclass(frozen=True)
class VectorSpectrumComparisonResult:
    """Reference data, two predictions, and bounded numerical evidence."""

    reference: ReferenceMassSpectrum
    predictions: Tuple[SpectrumPrediction, ...]
    comparisons: Tuple[DescriptiveModelComparison, ...]
    hard_wall_cross_solver_max_relative_difference: float
    hard_wall_refinement: HardWallRefinementResult
    acceptance_checks: Tuple[AcceptanceCheck, ...]

    @property
    def passed(self) -> bool:
        return all(check.passed for check in self.acceptance_checks)

    def prediction(self, identifier: str) -> SpectrumPrediction:
        for item in self.predictions:
            if item.identifier == identifier:
                return item
        raise ValueError(f"unknown model prediction: {identifier}")

    def to_dict(self) -> Dict[str, Any]:
        excluded_entries = [
            {
                "id": entry["id"],
                "label": entry["label"],
                "reason": entry["notes"],
            }
            for entry in self.reference.dataset["entries"]
            if not entry["included"]
        ]
        return {
            "comparison": COMPARISON_ID,
            "support_level": "reproduced",
            "reference": self.reference.to_dict(),
            "model_predictions": [item.to_dict() for item in self.predictions],
            "descriptive_comparisons": [
                item.to_dict() for item in self.comparisons
            ],
            "excluded_entries": excluded_entries,
            "numerical_validation": {
                "hard_wall_cross_solver_max_relative_difference": (
                    self.hard_wall_cross_solver_max_relative_difference
                ),
                "hard_wall_cutoff_refinement": self.hard_wall_refinement.to_dict(),
            },
            "acceptance_checks": [
                check.to_dict() for check in self.acceptance_checks
            ],
            "software_versions": runtime_versions(),
            "passed": self.passed,
            "interpretation_limits": [
                (
                    "The PDG excited-state assignments are candidate "
                    "phenomenological labels."
                ),
                (
                    "Goodness-of-comparison values are descriptive and are not "
                    "model acceptance gates."
                ),
                "Agreement does not prove QCD duality or precision-model validity.",
                (
                    "The comparison does not rank either construction outside "
                    "this selected observable."
                ),
            ],
        }


def build_vector_spectrum_comparison() -> VectorSpectrumComparisonResult:
    """Compute the frozen v0.3 comparison with no fitted shape parameters."""

    reference = load_pdg_2024_rho_spectrum()
    if reference.normalized.anchor_index != 0:
        raise ValueError("the v0.3 comparison requires the ground state as anchor")
    highest_mode = int(np.max(reference.model_modes))
    num_modes = highest_mode + 1

    soft_result = solve_spectrum(SoftWallConfig(), num_modes=num_modes)
    soft_masses = np.sqrt(soft_result.numerical_mass_squared_gev2)
    soft_exact_masses = np.sqrt(soft_result.analytic_mass_squared_gev2)
    soft_all_ratios = soft_masses / soft_masses[0]
    soft_exact_all_ratios = soft_exact_masses / soft_exact_masses[0]
    soft_ratios = soft_all_ratios[reference.model_modes]
    soft_exact_ratios = soft_exact_all_ratios[reference.model_modes]
    soft_prediction = SpectrumPrediction(
        identifier="quadratic-soft-wall",
        label="Quadratic soft wall",
        construction="dilaton Phi(z) = kappa^2 z^2 on fixed AdS5",
        calibration="m_0 is normalized to the rho(770)^0 anchor",
        solver="scipy.linalg.eigvalsh_tridiagonal",
        model_modes=reference.model_modes.copy(),
        ratios=soft_ratios,
        analytic_ratios=soft_exact_ratios,
        numerical_absolute_errors=np.abs(soft_ratios - soft_exact_ratios),
    )

    hard_shooting = solve_hard_wall_spectrum(
        num_modes=num_modes, method="shooting"
    )
    hard_collocation = solve_hard_wall_spectrum(
        num_modes=num_modes, method="collocation"
    )
    hard_ratios = hard_shooting.mass_ratios[reference.model_modes]
    hard_exact_ratios = hard_shooting.analytic_mass_ratios[reference.model_modes]
    hard_prediction = SpectrumPrediction(
        identifier="hard-wall",
        label="Hard wall",
        construction="fixed AdS5 slice with a phenomenological IR wall",
        calibration="m_0 is normalized to the rho(770)^0 anchor",
        solver="adaptive shooting; independently checked by global collocation",
        model_modes=reference.model_modes.copy(),
        ratios=hard_ratios,
        analytic_ratios=hard_exact_ratios,
        numerical_absolute_errors=np.abs(hard_ratios - hard_exact_ratios),
    )

    cross_solver_differences = np.abs(
        hard_shooting.mass_ratios - hard_collocation.mass_ratios
    ) / hard_collocation.mass_ratios
    cross_solver_max = float(np.max(cross_solver_differences[1:]))
    refinement = hard_wall_cutoff_refinement(
        num_modes=num_modes, method="shooting"
    )

    predictions = (soft_prediction, hard_prediction)
    comparisons = tuple(
        _compare_prediction(prediction, reference) for prediction in predictions
    )
    checks = (
        AcceptanceCheck(
            identifier="soft-wall-existing-verifier",
            description="The unchanged soft-wall verifier remains within tolerance.",
            value=soft_result.max_relative_error,
            criterion=f"value <= {SOFT_WALL_TOLERANCE:.16g}",
            passed=soft_result.max_relative_error <= SOFT_WALL_TOLERANCE,
        ),
        AcceptanceCheck(
            identifier="hard-wall-analytic-ratios",
            description="Hard-wall shooting ratios reproduce Bessel-zero ratios.",
            value=hard_shooting.max_ratio_relative_error,
            criterion=f"value <= {DEFAULT_RATIO_TOLERANCE:.16g}",
            passed=(
                hard_shooting.max_ratio_relative_error
                <= DEFAULT_RATIO_TOLERANCE
            ),
        ),
        AcceptanceCheck(
            identifier="hard-wall-independent-solvers",
            description="Shooting and collocation agree on their common ratios.",
            value=cross_solver_max,
            criterion=f"value <= {DEFAULT_CROSS_SOLVER_TOLERANCE:.16g}",
            passed=cross_solver_max <= DEFAULT_CROSS_SOLVER_TOLERANCE,
        ),
        AcceptanceCheck(
            identifier="hard-wall-cutoff-refinement",
            description="All three decreasing UV cutoffs reduce the ratio error.",
            passed=refinement.improves_at_every_level,
        ),
    )
    return VectorSpectrumComparisonResult(
        reference=reference,
        predictions=predictions,
        comparisons=comparisons,
        hard_wall_cross_solver_max_relative_difference=cross_solver_max,
        hard_wall_refinement=refinement,
        acceptance_checks=checks,
    )


def render_vector_spectrum_table(result: VectorSpectrumComparisonResult) -> str:
    """Render a deterministic Markdown table from computed values."""

    reference = result.reference
    soft = result.prediction("quadratic-soft-wall")
    hard = result.prediction("hard-wall")
    lines = [
        "# Vector-spectrum comparison",
        "",
        "| Mode | PDG 2024 ratio | Assignment | Soft wall | Hard wall |",
        "| ---: | ---: | :--- | ---: | ---: |",
    ]
    for index, mode in enumerate(reference.model_modes):
        ratio = reference.normalized.ratios[index]
        sigma = reference.normalized.standard_deviations[index]
        if sigma == 0.0:
            reference_text = f"{ratio:.6f} (anchor)"
        else:
            reference_text = f"{ratio:.6f} +/- {sigma:.6f}"
        lines.append(
            f"| {int(mode)} | {reference_text} | "
            f"{reference.assignment_statuses[index]} | "
            f"{soft.ratios[index]:.6f} | {hard.ratios[index]:.6f} |"
        )

    metrics: Mapping[str, DescriptiveModelComparison] = {
        item.model_id: item for item in result.comparisons
    }
    lines.extend(
        [
            "",
            "The ground state fixes the common normalization and is excluded from "
            "the covariance inversion.",
            "",
            (
                "Descriptive covariance-aware chi-square values for the two "
                "candidate excited-state assignments: "
                f"soft wall = {metrics['quadratic-soft-wall'].chi_square:.6f}; "
                f"hard wall = {metrics['hard-wall'].chi_square:.6f}."
            ),
            "",
            (
                "These values are not acceptance gates and do not establish model "
                "superiority, QCD duality, or precision validity."
            ),
            "",
        ]
    )
    return "\n".join(lines)


def save_vector_spectrum_artifacts(
    result: VectorSpectrumComparisonResult,
    output_directory: Path,
    include_plot: bool = True,
) -> Dict[str, str]:
    """Save JSON, Markdown, and optionally a plot generated from the result."""

    directory = Path(output_directory)
    directory.mkdir(parents=True, exist_ok=True)
    json_path = directory / "vector-spectrum-comparison.json"
    table_path = directory / "vector-spectrum-comparison.md"
    json_path.write_text(
        json.dumps(result.to_dict(), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    table_path.write_text(render_vector_spectrum_table(result), encoding="utf-8")
    artifacts = {"json": str(json_path), "table": str(table_path)}

    if include_plot:
        plot_path = directory / "vector-spectrum-comparison.png"
        _save_vector_spectrum_plot(result, plot_path)
        artifacts["plot"] = str(plot_path)
    return artifacts


def _compare_prediction(
    prediction: SpectrumPrediction,
    reference: ReferenceMassSpectrum,
) -> DescriptiveModelComparison:
    residuals = prediction.ratios - reference.normalized.ratios
    compared_positions = np.asarray(
        [
            index
            for index, assignment in enumerate(reference.assignment_statuses)
            if assignment != "anchor"
        ],
        dtype=int,
    )
    covariance = reference.normalized.ratio_covariance[
        np.ix_(compared_positions, compared_positions)
    ]
    selected_residuals = residuals[compared_positions]
    chi_square = float(
        selected_residuals @ np.linalg.solve(covariance, selected_residuals)
    )
    return DescriptiveModelComparison(
        model_id=prediction.identifier,
        model_modes=prediction.model_modes.copy(),
        residuals=residuals,
        compared_positions=compared_positions,
        chi_square=chi_square,
        degrees_of_freedom=len(compared_positions),
    )


def _save_vector_spectrum_plot(
    result: VectorSpectrumComparisonResult, path: Path
) -> None:
    import matplotlib

    matplotlib.use("Agg")
    from matplotlib import pyplot as plt

    modes = result.reference.model_modes
    reference = result.reference.normalized
    soft = result.prediction("quadratic-soft-wall")
    hard = result.prediction("hard-wall")

    figure, axis = plt.subplots(figsize=(6.4, 4.2), constrained_layout=True)
    axis.errorbar(
        modes,
        reference.ratios,
        yerr=reference.standard_deviations,
        color="black",
        marker="o",
        linestyle="none",
        capsize=4,
        label="PDG 2024 candidate assignments",
    )
    axis.plot(modes, soft.ratios, marker="s", label="Quadratic soft wall")
    axis.plot(modes, hard.ratios, marker="^", label="Hard wall")
    axis.set_xlabel("Model radial mode n")
    axis.set_ylabel("Ground-state-normalized mass ratio")
    axis.set_xticks(modes)
    axis.grid(alpha=0.25)
    axis.legend(frameon=False)
    figure.savefig(path, dpi=180)
    plt.close(figure)
