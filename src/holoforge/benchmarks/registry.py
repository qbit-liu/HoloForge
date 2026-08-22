"""Deterministic composition root for HoloForge's built-in benchmarks."""

from holoforge.benchmarks.adapters.dewolfe_gubser_rosen_emd import (
    DEWOLFE_GUBSER_ROSEN_ADAPTER,
    DEWOLFE_GUBSER_ROSEN_MODEL_CARD,
)
from holoforge.benchmarks.adapters.hard_wall_vector import (
    HARD_WALL_ADAPTER,
    HARD_WALL_MODEL_CARD,
)
from holoforge.benchmarks.adapters.hard_wall_chiral import (
    HARD_WALL_CHIRAL_ADAPTER,
    HARD_WALL_CHIRAL_MODEL_CARD,
)
from holoforge.benchmarks.adapters.gubser_nellore_ed import (
    GUBSER_NELLORE_ADAPTER,
    GUBSER_NELLORE_MODEL_CARD,
)
from holoforge.benchmarks.adapters.gubser_rocha_emd import (
    GUBSER_ROCHA_ADAPTER,
    GUBSER_ROCHA_MODEL_CARD,
)
from holoforge.benchmarks.adapters.holographic_superconductor import (
    SUPERCONDUCTOR_ADAPTER,
    SUPERCONDUCTOR_MODEL_CARD,
)
from holoforge.benchmarks.adapters.holographic_superconductor_optical import (
    SUPERCONDUCTOR_OPTICAL_ADAPTER,
    SUPERCONDUCTOR_OPTICAL_MODEL_CARD,
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
        DEWOLFE_GUBSER_ROSEN_ADAPTER,
        SOFT_WALL_ADAPTER,
        HARD_WALL_CHIRAL_ADAPTER,
        HARD_WALL_ADAPTER,
        GUBSER_NELLORE_ADAPTER,
        GUBSER_ROCHA_ADAPTER,
        SUPERCONDUCTOR_ADAPTER,
        SUPERCONDUCTOR_OPTICAL_ADAPTER,
        LINEAR_AXION_ADAPTER,
    )
)


__all__ = [
    "BUILTIN_BENCHMARKS",
    "DEWOLFE_GUBSER_ROSEN_ADAPTER",
    "DEWOLFE_GUBSER_ROSEN_MODEL_CARD",
    "GUBSER_NELLORE_ADAPTER",
    "GUBSER_NELLORE_MODEL_CARD",
    "GUBSER_ROCHA_ADAPTER",
    "GUBSER_ROCHA_MODEL_CARD",
    "HARD_WALL_ADAPTER",
    "HARD_WALL_MODEL_CARD",
    "HARD_WALL_CHIRAL_ADAPTER",
    "HARD_WALL_CHIRAL_MODEL_CARD",
    "LINEAR_AXION_ADAPTER",
    "LINEAR_AXION_MODEL_CARD",
    "SOFT_WALL_ADAPTER",
    "SOFT_WALL_MODEL_CARD",
    "SUPERCONDUCTOR_ADAPTER",
    "SUPERCONDUCTOR_MODEL_CARD",
    "SUPERCONDUCTOR_OPTICAL_ADAPTER",
    "SUPERCONDUCTOR_OPTICAL_MODEL_CARD",
]
