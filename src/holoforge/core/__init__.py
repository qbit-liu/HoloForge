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
from holoforge.core.provenance import runtime_versions

__all__ = [
    "AcceptanceCheck",
    "BackgroundSpec",
    "BenchmarkDefinition",
    "BoundaryConditionSpec",
    "EquationSpec",
    "ObservableSpec",
    "SolverSpec",
    "VerificationRecord",
    "runtime_versions",
]
