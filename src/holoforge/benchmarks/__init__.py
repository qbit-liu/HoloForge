"""Literature-anchored numerical benchmarks."""

from holoforge.benchmarks.dewolfe_gubser_rosen_emd import (
    verify_dewolfe_gubser_rosen_emd,
)
from holoforge.benchmarks.dewolfe_gubser_rosen_emd_critical_point import (
    verify_dewolfe_gubser_rosen_emd_finite_density,
)
from holoforge.benchmarks.gubser_nellore_ed import (
    verify_gubser_nellore_ed,
)
from holoforge.benchmarks.gubser_rocha_emd import verify_gubser_rocha_emd
from holoforge.benchmarks.hard_wall_vector import (
    HardWallConfig,
    HardWallRefinementResult,
    HardWallSpectrumResult,
    analytic_dimensionless_masses,
    hard_wall_cutoff_refinement,
    solve_hard_wall_spectrum,
)
from holoforge.benchmarks.hard_wall_chiral import (
    verify_hard_wall_chiral,
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
from holoforge.benchmarks.holographic_superconductor_optical import (
    OpticalVerificationResult,
    save_optical_diagnostic_plot,
    verify_holographic_superconductor_optical,
)
from holoforge.benchmarks.linear_axion_dc import (
    LinearAxionCaseResult,
    LinearAxionFrequencyResult,
    LinearAxionPreflightConfig,
    LinearAxionRefinementEvidence,
    LinearAxionVerificationResult,
    solve_linear_axion_case,
    solve_linear_axion_frequency,
    verify_linear_axion_dc,
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
    "LinearAxionCaseResult",
    "LinearAxionFrequencyResult",
    "LinearAxionPreflightConfig",
    "LinearAxionRefinementEvidence",
    "LinearAxionVerificationResult",
    "OnsetConfig",
    "OnsetResult",
    "OpticalVerificationResult",
    "SoftWallConfig",
    "SpectrumResult",
    "SuperconductorVerificationResult",
    "analytic_mass_squared",
    "analytic_dimensionless_masses",
    "hard_wall_cutoff_refinement",
    "save_condensate_plot",
    "save_optical_diagnostic_plot",
    "schrodinger_potential",
    "solve_condensate_branch",
    "solve_hard_wall_spectrum",
    "solve_linear_axion_case",
    "solve_linear_axion_frequency",
    "solve_onset",
    "solve_spectrum",
    "verify_superconductor",
    "verify_holographic_superconductor_optical",
    "verify_linear_axion_dc",
    "verify_gubser_nellore_ed",
    "verify_dewolfe_gubser_rosen_emd",
    "verify_dewolfe_gubser_rosen_emd_finite_density",
    "verify_gubser_rocha_emd",
    "verify_hard_wall_chiral",
]
