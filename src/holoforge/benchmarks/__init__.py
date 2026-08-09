"""Literature-anchored numerical benchmarks."""

from holoforge.benchmarks.hard_wall_vector import (
    HardWallConfig,
    HardWallRefinementResult,
    HardWallSpectrumResult,
    analytic_dimensionless_masses,
    hard_wall_cutoff_refinement,
    solve_hard_wall_spectrum,
)
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
from holoforge.benchmarks.registry import BUILTIN_BENCHMARKS

__all__ = [
    "CondensateBranchResult",
    "CondensateConfig",
    "BUILTIN_BENCHMARKS",
    "HardWallConfig",
    "HardWallRefinementResult",
    "HardWallSpectrumResult",
    "OnsetConfig",
    "OnsetResult",
    "SoftWallConfig",
    "SpectrumResult",
    "SuperconductorVerificationResult",
    "analytic_mass_squared",
    "analytic_dimensionless_masses",
    "hard_wall_cutoff_refinement",
    "save_condensate_plot",
    "schrodinger_potential",
    "solve_condensate_branch",
    "solve_hard_wall_spectrum",
    "solve_onset",
    "solve_spectrum",
    "verify_superconductor",
]
