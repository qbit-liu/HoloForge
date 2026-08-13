"""Deterministic composition root for HoloForge's built-in benchmarks."""

from holoforge.benchmarks.adapters.hard_wall_vector import (
    HARD_WALL_ADAPTER,
    HARD_WALL_MODEL_CARD,
)
from holoforge.benchmarks.adapters.holographic_superconductor import (
    SUPERCONDUCTOR_ADAPTER,
    SUPERCONDUCTOR_MODEL_CARD,
)
from holoforge.benchmarks.adapters.linear_axion_dc import (
    LINEAR_AXION_ADAPTER,
    LINEAR_AXION_MODEL_CARD,
)
from holoforge.benchmarks.adapters.soft_wall_vector import (
    SOFT_WALL_ADAPTER,
    SOFT_WALL_MODEL_CARD,
)
from holoforge.core.registry import BenchmarkRegistry


BUILTIN_BENCHMARKS = BenchmarkRegistry(
    (
        SOFT_WALL_ADAPTER,
        HARD_WALL_ADAPTER,
        SUPERCONDUCTOR_ADAPTER,
        LINEAR_AXION_ADAPTER,
    )
)


__all__ = [
    "BUILTIN_BENCHMARKS",
    "HARD_WALL_ADAPTER",
    "HARD_WALL_MODEL_CARD",
    "LINEAR_AXION_ADAPTER",
    "LINEAR_AXION_MODEL_CARD",
    "SOFT_WALL_ADAPTER",
    "SOFT_WALL_MODEL_CARD",
    "SUPERCONDUCTOR_ADAPTER",
    "SUPERCONDUCTOR_MODEL_CARD",
]
