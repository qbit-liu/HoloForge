"""Load versioned reference data distributed with the HoloForge wheel."""

from __future__ import annotations

from dataclasses import dataclass
from importlib import resources
import json
from typing import Any, Dict, Tuple

import numpy as np
from numpy.typing import NDArray

from holoforge.core import NormalizedSpectrum, normalize_spectrum


PDG_2024_RHO_RESOURCE = "data/reference/pdg-2024-rho-masses.json"


@dataclass(frozen=True)
class ReferenceMassSpectrum:
    """Selected mass entries and their covariance-aware normalized form."""

    dataset: Dict[str, Any]
    entry_ids: Tuple[str, ...]
    labels: Tuple[str, ...]
    model_modes: NDArray[np.int64]
    assignment_statuses: Tuple[str, ...]
    normalized: NormalizedSpectrum

    def to_dict(self) -> Dict[str, Any]:
        """Return data values, assignments, covariance, and source metadata."""

        transformation = self.normalized.to_dict(labels=self.labels)
        for entry, identifier, mode, assignment in zip(
            transformation["entries"],
            self.entry_ids,
            self.model_modes,
            self.assignment_statuses,
        ):
            entry.update(
                {
                    "id": identifier,
                    "model_mode": int(mode),
                    "assignment_status": assignment,
                }
            )
        return {
            "dataset_id": self.dataset["id"],
            "edition": dict(self.dataset["edition"]),
            "observable": dict(self.dataset["observable"]),
            "conventions": list(self.dataset["conventions"]),
            "review_status": self.dataset["provenance"]["review_status"],
            "normalization": self.dataset["transformations"][0]["expression"],
            **transformation,
        }


def load_reference_dataset(
    resource_name: str = PDG_2024_RHO_RESOURCE,
) -> Dict[str, Any]:
    """Load a canonical packaged JSON resource without a repository path."""

    if not isinstance(resource_name, str) or not resource_name:
        raise ValueError("resource_name must be a non-empty string")
    resource = resources.files("holoforge").joinpath(resource_name)
    try:
        with resource.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except FileNotFoundError as exc:
        raise ValueError(
            f"unknown packaged reference resource: {resource_name}"
        ) from exc
    if not isinstance(payload, dict):
        raise ValueError("reference resource must contain a JSON object")
    return payload


def load_pdg_2024_rho_spectrum() -> ReferenceMassSpectrum:
    """Load included PDG rho entries and propagate their listed errors."""

    dataset = load_reference_dataset()
    entries = [entry for entry in dataset["entries"] if entry["included"]]
    if len(entries) < 2:
        raise ValueError(
            "reference dataset must contain at least two included entries"
        )

    anchor_positions = [
        index
        for index, entry in enumerate(entries)
        if entry["assignment_status"] == "anchor"
    ]
    if len(anchor_positions) != 1:
        raise ValueError("reference dataset must contain exactly one included anchor")
    modes = np.asarray([entry["model_mode"] for entry in entries], dtype=int)
    if len(set(int(mode) for mode in modes)) != len(modes):
        raise ValueError("included model_mode values must be unique")

    masses = np.asarray([entry["value"] for entry in entries], dtype=float)
    standard_deviations = np.asarray(
        [_symmetric_standard_deviation(entry["uncertainty"]) for entry in entries],
        dtype=float,
    )
    normalized = normalize_spectrum(
        masses,
        np.diag(standard_deviations**2),
        anchor_index=anchor_positions[0],
    )
    return ReferenceMassSpectrum(
        dataset=dataset,
        entry_ids=tuple(entry["id"] for entry in entries),
        labels=tuple(entry["label"] for entry in entries),
        model_modes=modes,
        assignment_statuses=tuple(
            entry["assignment_status"] for entry in entries
        ),
        normalized=normalized,
    )


def _symmetric_standard_deviation(uncertainty: Dict[str, Any]) -> float:
    kind = uncertainty["kind"]
    if kind == "symmetric":
        return float(uncertainty["sigma"])
    if kind == "none":
        return 0.0
    raise ValueError(
        "comparison requires a documented symmetric uncertainty or an explicit "
        "symmetrization implementation"
    )
