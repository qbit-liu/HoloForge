"""Fail-closed contracts for solver-free benchmark capability inspection."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
import re
from types import MappingProxyType
from typing import Any, Dict, Iterable, Mapping, Optional, Sequence, Tuple


_IDENTIFIER = re.compile(r"^[a-z0-9]+(?:[.-][a-z0-9]+)*$")


class CapabilityReceiptError(ValueError):
    """Raised when a capability receipt is incomplete or contradictory."""


@dataclass(frozen=True)
class CapabilityInspection:
    """Classification of one exact capability identifier."""

    capability_id: str
    status: str
    description: Optional[str] = None
    declaration_kind: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "capability_id": self.capability_id,
            "status": self.status,
        }
        if self.declaration_kind is not None:
            payload["declaration_kind"] = self.declaration_kind
        if self.description is not None:
            payload["description"] = self.description
        return payload


class CapabilityReceipt:
    """Validated immutable view of one machine-readable benchmark receipt."""

    def __init__(self, payload: Mapping[str, Any]) -> None:
        normalized = _validate_receipt(payload)
        self._payload = MappingProxyType(normalized)
        self._qualified = _index_declarations(
            normalized["outputs"],
            normalized["validated_transformations"],
        )
        self._known_gaps = MappingProxyType(
            {item["id"]: item for item in normalized["known_gaps"]}
        )

    @property
    def benchmark_id(self) -> str:
        return str(self._payload["benchmark_id"])

    @property
    def capability_ids(self) -> Tuple[str, ...]:
        return tuple(sorted(self._qualified))

    @property
    def known_gap_ids(self) -> Tuple[str, ...]:
        return tuple(sorted(self._known_gaps))

    def inspect(self, capability_id: str) -> CapabilityInspection:
        _require_identifier(capability_id, "requested capability identifier")
        declaration = self._qualified.get(capability_id)
        if declaration is not None:
            return CapabilityInspection(
                capability_id=capability_id,
                status="qualified",
                description=declaration["description"],
                declaration_kind=declaration["declaration_kind"],
            )
        gap = self._known_gaps.get(capability_id)
        if gap is not None:
            return CapabilityInspection(
                capability_id=capability_id,
                status="known-gap",
                description=gap["description"],
                declaration_kind="known-gap",
            )
        return CapabilityInspection(
            capability_id=capability_id,
            status="not-declared",
        )

    def to_dict(
        self, required_capabilities: Sequence[str] = ()
    ) -> Dict[str, Any]:
        payload = deepcopy(dict(self._payload))
        payload["inspection"] = {
            "solver_executed": False,
            "scientific_judgment": "not-performed",
            "requirements": [
                self.inspect(identifier).to_dict()
                for identifier in required_capabilities
            ],
        }
        return payload


class CapabilityRegistry:
    """Immutable benchmark-keyed collection of capability receipts."""

    def __init__(self, receipts: Iterable[CapabilityReceipt]) -> None:
        indexed: Dict[str, CapabilityReceipt] = {}
        for receipt in receipts:
            if not isinstance(receipt, CapabilityReceipt):
                raise CapabilityReceiptError(
                    "capability registry entries must be CapabilityReceipt objects"
                )
            if receipt.benchmark_id in indexed:
                raise CapabilityReceiptError(
                    "duplicate benchmark capability receipt: "
                    f"{receipt.benchmark_id}"
                )
            indexed[receipt.benchmark_id] = receipt
        if not indexed:
            raise CapabilityReceiptError(
                "capability registry must contain at least one receipt"
            )
        self._receipts = MappingProxyType(indexed)

    @property
    def identifiers(self) -> Tuple[str, ...]:
        return tuple(sorted(self._receipts))

    def get(self, benchmark_id: str) -> CapabilityReceipt:
        try:
            return self._receipts[benchmark_id]
        except KeyError as exc:
            available = ", ".join(self.identifiers)
            raise CapabilityReceiptError(
                f"unknown benchmark capability receipt {benchmark_id!r}; "
                f"available: {available}"
            ) from exc

    def __iter__(self):
        for identifier in self.identifiers:
            yield self._receipts[identifier]


def _validate_receipt(payload: Mapping[str, Any]) -> Dict[str, Any]:
    if not isinstance(payload, Mapping):
        raise CapabilityReceiptError("capability receipt must be a mapping")
    allowed = {
        "schema_version",
        "benchmark_id",
        "summary",
        "mode",
        "support_level",
        "coverage",
        "outputs",
        "validated_transformations",
        "known_gaps",
        "evidence",
        "provenance",
    }
    _require_exact_keys(payload, allowed, allowed, "capability receipt")
    if payload["schema_version"] != "0.6":
        raise CapabilityReceiptError("capability schema_version must be '0.6'")
    _require_identifier(payload["benchmark_id"], "benchmark_id")
    _require_text(payload["summary"], "summary")
    if payload["mode"] != "forge-verify":
        raise CapabilityReceiptError("capability receipt mode must be forge-verify")
    if payload["support_level"] != "reproduced":
        raise CapabilityReceiptError(
            "capability receipt support_level must be reproduced"
        )

    coverage = _require_mapping(payload["coverage"], "coverage")
    _require_exact_keys(
        coverage,
        {"branches", "ensembles", "parameters"},
        {"branches", "ensembles", "parameters"},
        "coverage",
    )
    _require_text_list(coverage["branches"], "coverage.branches")
    _require_text_list(coverage["ensembles"], "coverage.ensembles")
    parameters = _require_sequence(coverage["parameters"], "coverage.parameters")
    if not parameters:
        raise CapabilityReceiptError("coverage.parameters must not be empty")
    for index, parameter in enumerate(parameters):
        item = _require_mapping(parameter, f"coverage.parameters[{index}]")
        _require_exact_keys(
            item,
            {"id", "description", "coverage_kind"},
            {"id", "description", "coverage_kind"},
            f"coverage.parameters[{index}]",
        )
        _require_identifier(item["id"], f"coverage.parameters[{index}].id")
        _require_text(item["description"], f"coverage.parameters[{index}].description")
        if item["coverage_kind"] not in {
            "fixed",
            "bounded",
            "finite-set",
            "configurable",
        }:
            raise CapabilityReceiptError("invalid parameter coverage_kind")

    outputs = _validate_declarations(payload["outputs"], "outputs", output=True)
    transformations = _validate_declarations(
        payload["validated_transformations"],
        "validated_transformations",
        output=False,
    )
    gaps = _validate_gaps(payload["known_gaps"])
    all_ids = [item["id"] for item in outputs + transformations + gaps]
    if len(all_ids) != len(set(all_ids)):
        raise CapabilityReceiptError(
            "capability and known-gap identifiers must be unique within a receipt"
        )

    evidence = _require_mapping(payload["evidence"], "evidence")
    _require_exact_keys(
        evidence,
        {"model_cards", "documentation"},
        {"model_cards", "documentation"},
        "evidence",
    )
    model_cards = _require_sequence(evidence["model_cards"], "evidence.model_cards")
    if not model_cards:
        raise CapabilityReceiptError("evidence.model_cards must not be empty")
    for index, reference in enumerate(model_cards):
        item = _require_mapping(reference, f"evidence.model_cards[{index}]")
        _require_exact_keys(
            item,
            {"identifier", "repository_path"},
            {"identifier", "repository_path"},
            f"evidence.model_cards[{index}]",
        )
        _require_identifier(item["identifier"], "model-card identifier")
        _require_relative_path(item["repository_path"], "model-card repository_path")
    documentation = _require_text_list(
        evidence["documentation"], "evidence.documentation"
    )
    for path in documentation:
        _require_relative_path(path, "documentation path")

    provenance = _require_mapping(payload["provenance"], "provenance")
    required_provenance = {"generated_by_ai", "review_status"}
    allowed_provenance = required_provenance | {"reviewed_by", "reviewed_on"}
    _require_exact_keys(
        provenance,
        required_provenance,
        allowed_provenance,
        "provenance",
    )
    if provenance["generated_by_ai"] is not True:
        raise CapabilityReceiptError("generated_by_ai must be true")
    if provenance["review_status"] not in {"unreviewed", "approved"}:
        raise CapabilityReceiptError("invalid provenance.review_status")
    if provenance["review_status"] == "approved":
        _require_text(provenance.get("reviewed_by"), "provenance.reviewed_by")
        _require_text(provenance.get("reviewed_on"), "provenance.reviewed_on")
    elif "reviewed_by" in provenance or "reviewed_on" in provenance:
        raise CapabilityReceiptError(
            "unreviewed receipts cannot name a reviewer or review date"
        )

    return deepcopy(dict(payload))


def _validate_declarations(value: Any, field: str, *, output: bool):
    declarations = _require_sequence(value, field)
    if not declarations:
        raise CapabilityReceiptError(f"{field} must not be empty")
    normalized = []
    for index, declaration in enumerate(declarations):
        item = _require_mapping(declaration, f"{field}[{index}]")
        required = {"id", "description", "evidence"}
        allowed = set(required)
        if output:
            required |= {"artifact_role"}
            allowed |= {"artifact_role"}
        _require_exact_keys(item, required, allowed, f"{field}[{index}]")
        _require_identifier(item["id"], f"{field}[{index}].id")
        _require_text(item["description"], f"{field}[{index}].description")
        _require_text_list(item["evidence"], f"{field}[{index}].evidence")
        if output and item["artifact_role"] not in {
            "result",
            "evidence",
            "diagnostic",
        }:
            raise CapabilityReceiptError("invalid output artifact_role")
        normalized.append(dict(item))
    return normalized


def _validate_gaps(value: Any):
    gaps = _require_sequence(value, "known_gaps")
    if not gaps:
        raise CapabilityReceiptError("known_gaps must not be empty")
    normalized = []
    for index, gap in enumerate(gaps):
        item = _require_mapping(gap, f"known_gaps[{index}]")
        _require_exact_keys(
            item,
            {"id", "description"},
            {"id", "description"},
            f"known_gaps[{index}]",
        )
        _require_identifier(item["id"], f"known_gaps[{index}].id")
        _require_text(item["description"], f"known_gaps[{index}].description")
        normalized.append(dict(item))
    return normalized


def _index_declarations(outputs, transformations):
    indexed = {}
    for declaration in outputs:
        item = dict(declaration)
        item["declaration_kind"] = "output"
        indexed[item["id"]] = item
    for declaration in transformations:
        item = dict(declaration)
        item["declaration_kind"] = "validated-transformation"
        indexed[item["id"]] = item
    return MappingProxyType(indexed)


def _require_exact_keys(value, required, allowed, field):
    missing = set(required) - set(value)
    extra = set(value) - set(allowed)
    if missing:
        raise CapabilityReceiptError(
            f"{field} is missing required keys: {', '.join(sorted(missing))}"
        )
    if extra:
        raise CapabilityReceiptError(
            f"{field} contains unknown keys: {', '.join(sorted(extra))}"
        )


def _require_mapping(value: Any, field: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise CapabilityReceiptError(f"{field} must be a mapping")
    return value


def _require_sequence(value: Any, field: str):
    if not isinstance(value, list):
        raise CapabilityReceiptError(f"{field} must be a JSON array")
    return value


def _require_text(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise CapabilityReceiptError(f"{field} must be non-empty text")
    return value


def _require_text_list(value: Any, field: str):
    items = _require_sequence(value, field)
    if not items:
        raise CapabilityReceiptError(f"{field} must not be empty")
    for index, item in enumerate(items):
        _require_text(item, f"{field}[{index}]")
    if len(items) != len(set(items)):
        raise CapabilityReceiptError(f"{field} entries must be unique")
    return items


def _require_identifier(value: Any, field: str) -> str:
    text = _require_text(value, field)
    if not _IDENTIFIER.fullmatch(text):
        raise CapabilityReceiptError(f"{field} is not a canonical identifier")
    return text


def _require_relative_path(value: Any, field: str) -> str:
    text = _require_text(value, field)
    parts = text.replace("\\", "/").split("/")
    if text.startswith("/") or ".." in parts or "." in parts:
        raise CapabilityReceiptError(f"{field} must be a repository-relative path")
    return text


__all__ = [
    "CapabilityInspection",
    "CapabilityReceipt",
    "CapabilityReceiptError",
    "CapabilityRegistry",
]
