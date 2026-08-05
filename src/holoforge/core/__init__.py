"""Shared scientific and verification contracts."""

from holoforge.core.contracts import (
    AcceptanceCheck,
    BackgroundSpec,
    BenchmarkDefinition,
    BoundaryConditionSpec,
    EquationSpec,
    ObservableSpec,
    SolverSpec,
    VerificationRecord,
)
from holoforge.core.comparison import NormalizedSpectrum, normalize_spectrum
from holoforge.core.provenance import runtime_versions

__all__ = [
    "AcceptanceCheck",
    "BackgroundSpec",
    "BenchmarkDefinition",
    "BoundaryConditionSpec",
    "EquationSpec",
    "ObservableSpec",
    "NormalizedSpectrum",
    "SolverSpec",
    "VerificationRecord",
    "normalize_spectrum",
    "runtime_versions",
]
