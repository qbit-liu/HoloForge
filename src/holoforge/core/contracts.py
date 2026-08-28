"""Small, explicit contracts shared by heterogeneous benchmarks.

HoloForge benchmarks need common scientific metadata and result semantics, but
they do not necessarily share one numerical problem type.  An eigenvalue
problem and a nonlinear boundary-value problem therefore use the same
descriptors and acceptance records without being forced through one artificial
solver signature.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import json
import math
from typing import Any, Dict, Mapping, Optional, Sequence, Tuple


@dataclass(frozen=True)
class BackgroundSpec:
    """Literature-anchored background on which a benchmark is posed."""

    identifier: str
    dimension: int
    coordinate: str
    description: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.identifier,
            "dimension": self.dimension,
            "coordinate": self.coordinate,
            "description": self.description,
        }


@dataclass(frozen=True)
class EquationSpec:
    """Equation metadata, including its role and source provenance."""

    identifier: str
    kind: str
    dependent_fields: Tuple[str, ...]
    expression: str
    source_reference: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.identifier,
            "kind": self.kind,
            "dependent_fields": list(self.dependent_fields),
            "expression": self.expression,
            "source_reference": self.source_reference,
        }


@dataclass(frozen=True)
class BoundaryConditionSpec:
    """Boundary condition with its physical role stated explicitly."""

    field: str
    location: str
    role: str
    expression: str
    interpretation: str

    def to_dict(self) -> Dict[str, str]:
        return {
            "field": self.field,
            "location": self.location,
            "role": self.role,
            "expression": self.expression,
            "interpretation": self.interpretation,
        }


@dataclass(frozen=True)
class SolverSpec:
    """Numerical method selected for one equation class."""

    problem_type: str
    library_function: str
    method: str
    description: str

    def to_dict(self) -> Dict[str, str]:
        return {
            "problem_type": self.problem_type,
            "library_function": self.library_function,
            "method": self.method,
            "description": self.description,
        }


@dataclass(frozen=True)
class ObservableSpec:
    """Observable and the rule used to extract it from a solution."""

    identifier: str
    symbol: str
    extraction: str
    normalization: str

    def to_dict(self) -> Dict[str, str]:
        return {
            "id": self.identifier,
            "symbol": self.symbol,
            "extraction": self.extraction,
            "normalization": self.normalization,
        }


@dataclass(frozen=True)
class BenchmarkDefinition:
    """Static scientific contract for an executable benchmark."""

    identifier: str
    support_level: str
    background: BackgroundSpec
    equations: Tuple[EquationSpec, ...]
    boundary_conditions: Tuple[BoundaryConditionSpec, ...]
    solvers: Tuple[SolverSpec, ...]
    observables: Tuple[ObservableSpec, ...]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "benchmark": self.identifier,
            "support_level": self.support_level,
            "background": self.background.to_dict(),
            "equations": [item.to_dict() for item in self.equations],
            "boundary_conditions": [
                item.to_dict() for item in self.boundary_conditions
            ],
            "solvers": [item.to_dict() for item in self.solvers],
            "observables": [item.to_dict() for item in self.observables],
        }


@dataclass(frozen=True)
class AcceptanceCheck:
    """One inspectable pass/fail gate in a verification result."""

    identifier: str
    description: str
    passed: bool
    value: Optional[float] = None
    criterion: Optional[str] = None

    def __post_init__(self) -> None:
        if not isinstance(self.identifier, str) or not self.identifier.strip():
            raise ValueError("acceptance-check identifier must be non-empty")
        if not isinstance(self.description, str) or not self.description.strip():
            raise ValueError("acceptance-check description must be non-empty")
        if not isinstance(self.passed, bool):
            raise ValueError("acceptance-check passed state must be boolean")
        if self.value is not None:
            try:
                finite_value = math.isfinite(float(self.value))
            except (TypeError, ValueError) as exc:
                raise ValueError("acceptance-check value must be numeric") from exc
            if not finite_value:
                raise ValueError("acceptance-check value must be finite")
        if self.criterion is not None and (
            not isinstance(self.criterion, str) or not self.criterion.strip()
        ):
            raise ValueError("acceptance-check criterion must be non-empty")

    def to_dict(self) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "id": self.identifier,
            "description": self.description,
            "passed": bool(self.passed),
        }
        if self.value is not None:
            payload["value"] = float(self.value)
        if self.criterion is not None:
            payload["criterion"] = self.criterion
        return payload


@dataclass(frozen=True)
class VerificationRecord:
    """Common machine-readable envelope for benchmark evidence."""

    definition: BenchmarkDefinition
    configuration: Mapping[str, Any]
    numerical_method: Mapping[str, Any]
    results: Any
    acceptance_checks: Sequence[AcceptanceCheck]
    software_versions: Mapping[str, str]
    scope: str
    extra: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.definition, BenchmarkDefinition):
            raise ValueError("verification definition must be a BenchmarkDefinition")
        if not isinstance(self.configuration, Mapping):
            raise ValueError("verification configuration must be a mapping")
        if not isinstance(self.numerical_method, Mapping):
            raise ValueError("verification numerical_method must be a mapping")
        if not self.acceptance_checks:
            raise ValueError("verification record requires at least one acceptance check")
        if not all(
            isinstance(check, AcceptanceCheck) for check in self.acceptance_checks
        ):
            raise ValueError("verification acceptance checks must be AcceptanceCheck objects")
        if not isinstance(self.software_versions, Mapping) or not self.software_versions:
            raise ValueError("verification software_versions must be a non-empty mapping")
        if not all(
            isinstance(key, str)
            and key.strip()
            and isinstance(value, str)
            and value.strip()
            for key, value in self.software_versions.items()
        ):
            raise ValueError("verification software_versions must contain strings")
        if not isinstance(self.scope, str) or not self.scope.strip():
            raise ValueError("verification scope must be non-empty")
        if not isinstance(self.extra, Mapping):
            raise ValueError("verification extra metadata must be a mapping")
        reserved = set(self.definition.to_dict()) | {
            "configuration",
            "numerical_method",
            "results",
            "acceptance_checks",
            "software_versions",
            "passed",
            "scope",
        }
        collisions = sorted(reserved.intersection(self.extra))
        if collisions:
            raise ValueError(
                "verification extra metadata cannot replace reserved fields: "
                + ", ".join(collisions)
            )

    @property
    def passed(self) -> bool:
        return bool(self.acceptance_checks) and all(
            check.passed for check in self.acceptance_checks
        )

    def to_dict(self) -> Dict[str, Any]:
        payload = self.definition.to_dict()
        payload.update(
            {
                "configuration": dict(self.configuration),
                "numerical_method": dict(self.numerical_method),
                "results": self.results,
                "acceptance_checks": [
                    check.to_dict() for check in self.acceptance_checks
                ],
                "software_versions": dict(self.software_versions),
                "passed": self.passed,
                "scope": self.scope,
            }
        )
        payload.update(dict(self.extra))
        try:
            json.dumps(payload, allow_nan=False, sort_keys=True)
        except (TypeError, ValueError) as exc:
            raise ValueError(
                "verification record must contain strict finite JSON values"
            ) from exc
        return payload
