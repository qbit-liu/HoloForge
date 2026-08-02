"""Literature-anchored numerical benchmarks."""

from holoforge.benchmarks.soft_wall_vector import (
    SoftWallConfig,
    SpectrumResult,
    analytic_mass_squared,
    schrodinger_potential,
    solve_spectrum,
)

__all__ = [
    "SoftWallConfig",
    "SpectrumResult",
    "analytic_mass_squared",
    "schrodinger_potential",
    "solve_spectrum",
]
