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
from holoforge.core.evidence import (
    BundleAuditResult,
    CompatibilityAuditResult,
    EvidenceBundleError,
    audit_evidence_bundle,
    audit_same_state_family,
    canonical_json_sha256,
    write_evidence_bundle,
)
from holoforge.core.provenance import runtime_versions
from holoforge.core.registry import (
    BenchmarkAdapter,
    BenchmarkExecution,
    BenchmarkExecutionError,
    BenchmarkRegistry,
    BenchmarkRegistryError,
    ModelCardReference,
)

__all__ = [
    "AcceptanceCheck",
    "BackgroundSpec",
    "BenchmarkAdapter",
    "BenchmarkDefinition",
    "BenchmarkExecution",
    "BenchmarkExecutionError",
    "BenchmarkRegistry",
    "BenchmarkRegistryError",
    "BoundaryConditionSpec",
    "BundleAuditResult",
    "CompatibilityAuditResult",
    "EquationSpec",
    "EvidenceBundleError",
    "ObservableSpec",
    "NormalizedSpectrum",
    "ModelCardReference",
    "SolverSpec",
    "VerificationRecord",
    "audit_evidence_bundle",
    "audit_same_state_family",
    "canonical_json_sha256",
    "normalize_spectrum",
    "runtime_versions",
    "write_evidence_bundle",
]
