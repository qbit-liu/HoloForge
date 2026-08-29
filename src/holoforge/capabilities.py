"""Public composition root for built-in benchmark capability receipts."""

from __future__ import annotations

from importlib import resources
import json
from typing import Any, Dict

from holoforge.benchmarks.registry import BUILTIN_BENCHMARKS
from holoforge.core.capabilities import (
    CapabilityReceipt,
    CapabilityReceiptError,
    CapabilityRegistry,
)


def _load_builtin_capabilities() -> CapabilityRegistry:
    directory = resources.files("holoforge.data.capabilities")
    receipts = []
    for resource in sorted(directory.iterdir(), key=lambda item: item.name):
        if resource.name.endswith(".json"):
            try:
                payload: Dict[str, Any] = json.loads(
                    resource.read_text(encoding="utf-8")
                )
            except (OSError, ValueError, TypeError) as exc:
                raise CapabilityReceiptError(
                    f"cannot load capability receipt {resource.name}: {exc}"
                ) from exc
            receipts.append(CapabilityReceipt(payload))
    registry = CapabilityRegistry(receipts)
    if registry.identifiers != BUILTIN_BENCHMARKS.identifiers:
        missing = sorted(set(BUILTIN_BENCHMARKS.identifiers) - set(registry.identifiers))
        extra = sorted(set(registry.identifiers) - set(BUILTIN_BENCHMARKS.identifiers))
        raise CapabilityReceiptError(
            "built-in capability receipts do not match the benchmark registry; "
            f"missing={missing}, extra={extra}"
        )
    for adapter in BUILTIN_BENCHMARKS:
        receipt = registry.get(adapter.identifier).to_dict()
        declared = {
            (item["identifier"], item["repository_path"])
            for item in receipt["evidence"]["model_cards"]
        }
        expected = {
            (item.identifier, item.repository_path) for item in adapter.model_cards
        }
        if declared != expected:
            raise CapabilityReceiptError(
                f"model-card evidence mismatch for {adapter.identifier}"
            )
    return registry


BUILTIN_CAPABILITIES = _load_builtin_capabilities()


def inspect_benchmark_capabilities(
    benchmark_id: str, *required_capabilities: str
) -> Dict[str, Any]:
    """Return one solver-free built-in receipt and exact-ID classifications."""

    return BUILTIN_CAPABILITIES.get(benchmark_id).to_dict(required_capabilities)


__all__ = ["BUILTIN_CAPABILITIES", "inspect_benchmark_capabilities"]
