"""Literature-anchored numerical benchmarks."""

from holoforge.benchmarks.holographic_superconductor import (
    CondensateBranchResult,
    CondensateConfig,
    OnsetConfig,
    OnsetResult,
    SuperconductorVerificationResult,
    save_condensate_plot,
    solve_condensate_branch,
    solve_onset,
    verify_superconductor,
)
from holoforge.benchmarks.soft_wall_vector import (
    SoftWallConfig,
    SpectrumResult,
    analytic_mass_squared,
    schrodinger_potential,
    solve_spectrum,
)

__all__ = [
    "CondensateBranchResult",
    "CondensateConfig",
    "OnsetConfig",
    "OnsetResult",
    "SoftWallConfig",
    "SpectrumResult",
    "SuperconductorVerificationResult",
    "analytic_mass_squared",
    "save_condensate_plot",
    "schrodinger_potential",
    "solve_condensate_branch",
    "solve_onset",
    "solve_spectrum",
    "verify_superconductor",
]
