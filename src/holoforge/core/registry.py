"""Validated contracts for deterministic in-repository benchmark dispatch."""

from __future__ import annotations

from dataclasses import dataclass, field
import json
from pathlib import Path, PurePosixPath
import re
from types import MappingProxyType
from typing import Any, Callable, Dict, Iterator, Mapping, Sequence, Tuple


_IDENTIFIER = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_SUPPORT_LEVELS = {
    "established-source",
    "reproduced",
    "model-extension",
    "hypothesis",
}


class BenchmarkRegistryError(ValueError):
    """Raised when a benchmark adapter or registry is malformed."""


class BenchmarkExecutionError(ValueError):
    """Raised for a controlled benchmark input or execution failure."""


@dataclass(frozen=True)
class ModelCardReference:
    """Immutable reference to one reviewed public model card."""

    identifier: str
    schema_version: str
    repository_path: str
    sha256: str

    def to_dict(self) -> Dict[str, str]:
        """Return the evidence-bundle representation."""

        return {
            "id": self.identifier,
            "schema_version": self.schema_version,
            "repository_path": self.repository_path,
            "sha256": self.sha256,
        }


@dataclass(frozen=True)
class BenchmarkExecution:
    """Generic command outcome without a shared numerical-solver contract."""

    payload: Mapping[str, Any]
    passed: bool
    artifacts: Mapping[str, Path] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.payload, Mapping):
            raise BenchmarkRegistryError("benchmark payload must be a mapping")
        if not isinstance(self.passed, bool):
            raise BenchmarkRegistryError("benchmark passed flag must be boolean")
        payload_passed = self.payload.get("passed")
        if not isinstance(payload_passed, bool):
            raise BenchmarkRegistryError(
                "benchmark payload must contain a boolean passed field"
            )
        checks = self.payload.get("acceptance_checks")
        if not isinstance(checks, (list, tuple)) or not checks:
            raise BenchmarkRegistryError(
                "benchmark payload requires at least one acceptance check"
            )
        if not all(
            isinstance(check, Mapping)
            and isinstance(check.get("passed"), bool)
            for check in checks
        ):
            raise BenchmarkRegistryError(
                "benchmark acceptance checks require boolean passed fields"
            )
        derived_passed = all(check["passed"] for check in checks)
        if payload_passed != derived_passed or self.passed != derived_passed:
            raise BenchmarkRegistryError(
                "benchmark execution, payload, and acceptance checks disagree"
            )
        support_level = self.payload.get("support_level")
        if support_level not in _SUPPORT_LEVELS:
            raise BenchmarkRegistryError(
                "benchmark payload requires an explicit recognized support level"
            )
        try:
            json.dumps(self.payload, allow_nan=False, sort_keys=True)
        except (TypeError, ValueError) as exc:
            raise BenchmarkRegistryError(
                "benchmark payload must contain strict finite JSON values"
            ) from exc
        if not isinstance(self.artifacts, Mapping):
            raise BenchmarkRegistryError("benchmark artifacts must be a mapping")
        for role, path in self.artifacts.items():
            if not isinstance(role, str) or not role:
                raise BenchmarkRegistryError("artifact roles must be nonempty strings")
            if not isinstance(path, Path):
                raise BenchmarkRegistryError("artifact values must be pathlib Paths")


@dataclass(frozen=True)
class BenchmarkAdapter:
    """Command and evidence hooks for one in-repository benchmark."""

    identifier: str
    description: str
    configure_parser: Callable[[Any], None]
    execute: Callable[[Any], BenchmarkExecution]
    render_human: Callable[[BenchmarkExecution], Sequence[str]]
    scientific_state: Callable[[Mapping[str, Any]], Mapping[str, Any]]
    model_cards: Tuple[ModelCardReference, ...]


class BenchmarkRegistry:
    """Immutable, identifier-sorted collection of validated adapters."""

    def __init__(self, adapters: Sequence[BenchmarkAdapter]) -> None:
        entries = tuple(adapters)
        if any(not isinstance(adapter, BenchmarkAdapter) for adapter in entries):
            raise BenchmarkRegistryError(
                "registry entries must be BenchmarkAdapter objects"
            )
        ordered = tuple(sorted(entries, key=lambda item: item.identifier))
        identifiers = [adapter.identifier for adapter in ordered]
        if len(identifiers) != len(set(identifiers)):
            duplicates = sorted(
                identifier
                for identifier in set(identifiers)
                if identifiers.count(identifier) > 1
            )
            raise BenchmarkRegistryError(
                f"duplicate benchmark identifier: {', '.join(duplicates)}"
            )
        for adapter in ordered:
            _validate_adapter(adapter)
        self._adapters = ordered
        self._by_identifier = MappingProxyType(
            {adapter.identifier: adapter for adapter in self._adapters}
        )

    def __iter__(self) -> Iterator[BenchmarkAdapter]:
        return iter(self._adapters)

    def __len__(self) -> int:
        return len(self._adapters)

    @property
    def identifiers(self) -> Tuple[str, ...]:
        """Return stable benchmark identifiers in help-display order."""

        return tuple(adapter.identifier for adapter in self._adapters)

    def get(self, identifier: str) -> BenchmarkAdapter:
        """Resolve one validated adapter or fail with a controlled message."""

        try:
            return self._by_identifier[identifier]
        except KeyError as exc:
            raise BenchmarkRegistryError(
                f"unknown benchmark identifier: {identifier}"
            ) from exc


def _validate_adapter(adapter: BenchmarkAdapter) -> None:
    if not isinstance(adapter, BenchmarkAdapter):
        raise BenchmarkRegistryError(
            "registry entries must be BenchmarkAdapter objects"
        )
    if not _IDENTIFIER.fullmatch(adapter.identifier):
        raise BenchmarkRegistryError(
            f"invalid benchmark identifier: {adapter.identifier!r}"
        )
    if not isinstance(adapter.description, str) or not adapter.description.strip():
        raise BenchmarkRegistryError(
            f"benchmark {adapter.identifier!r} has no public description"
        )
    callbacks = {
        "configure_parser": adapter.configure_parser,
        "execute": adapter.execute,
        "render_human": adapter.render_human,
        "scientific_state": adapter.scientific_state,
    }
    for name, callback in callbacks.items():
        if not callable(callback):
            raise BenchmarkRegistryError(
                f"benchmark {adapter.identifier!r} callback {name} is not callable"
            )
    if not isinstance(adapter.model_cards, tuple) or not adapter.model_cards:
        raise BenchmarkRegistryError(
            f"benchmark {adapter.identifier!r} must declare model cards as a tuple"
        )
    for reference in adapter.model_cards:
        _validate_model_card_reference(adapter.identifier, reference)


def _validate_model_card_reference(
    benchmark_identifier: str, reference: ModelCardReference
) -> None:
    if not isinstance(reference, ModelCardReference):
        raise BenchmarkRegistryError(
            f"benchmark {benchmark_identifier!r} has a malformed model-card reference"
        )
    if (
        not reference.identifier.strip()
        or not reference.schema_version.strip()
        or reference.identifier != reference.identifier.strip()
        or reference.schema_version != reference.schema_version.strip()
    ):
        raise BenchmarkRegistryError(
            f"benchmark {benchmark_identifier!r} has incomplete model-card metadata"
        )
    path = PurePosixPath(reference.repository_path)
    if (
        not reference.repository_path
        or "\\" in reference.repository_path
        or path.is_absolute()
        or any(part in {"", ".", ".."} for part in path.parts)
    ):
        raise BenchmarkRegistryError(
            f"benchmark {benchmark_identifier!r} has an unsafe model-card path"
        )
    if not _SHA256.fullmatch(reference.sha256):
        raise BenchmarkRegistryError(
            f"benchmark {benchmark_identifier!r} has an invalid model-card digest"
        )
