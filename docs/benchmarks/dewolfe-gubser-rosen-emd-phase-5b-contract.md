# DeWolfe--Gubser--Rosen EMD Phase 5B current contract

## Status and scientific boundary

This is the active Forge/Verify contract for the reduced Phase 5B classical
example based on DeWolfe, Gubser, and Rosen,
[arXiv:1012.1864v2](https://arxiv.org/abs/1012.1864). Xin-Yi Liu approved the
reduced numerical result, model card, and evidence boundary on 2026-08-23.
The implementation was merged to `main` through pull request 32.

The accepted result covers representative finite-density backgrounds, an
independent simultaneous-Maxwell formulation, fixed-state spectral
refinement, and the paper's reported critical-coordinate neighborhood. It
does not establish a global phase diagram or reproduce the absolute ordinate
or topology of source Figure 5.

## Frozen calculation

The public interface is

```text
dewolfe-gubser-rosen-emd-finite-density
holoforge verify dewolfe-gubser-rosen-emd-finite-density
```

The primary route analytically reduces Maxwell's equation to the conserved
flux `q=-f_EMD exp(A) Phi'`. The independent route collocates the geometry,
scalar, and UV-factorized electric potential together. The canonical source
dictionary is `rho_canonical_BH=q/2`.

The direct critical locator starts at `(phi_H,eta)=(4.800667,0.401127)` at
`N=80`, uses five-point constant-temperature steps
`(0.25,0.125,0.0625)` and the independent validation step `0.03125`, then
refines the fixed located state through `N=(80,120,150)`. The three `N=80`
controls are `(4.84,0)`, `(4.84,0.40)`, and `(7.0,0.50)`.

The known conditioned reconstructed-Maxwell row has a `1e-6` ceiling. The
independent physical equations remain at `1e-5`, boundaries and explicit
Gauss drift at `1e-7`, and Noether drift at `1e-6`. The primary and explicit
reported observables must agree within `5e-6`; critical diagnostics and final
refinement changes must not exceed `2e-3`; duplicate full runs must agree
within `1e-10`.

## Accepted result and seven gates

The current verifier reports

```text
(T_c, mu_c) = (142.973974 MeV, 781.693762 MeV)
```

All seven active gates must pass: charged-point equations and boundaries,
source critical coordinates, critical derivatives, spectral refinement,
independent explicit-Maxwell agreement, Figure 5 scope separation, and
determinism. The exact current numerical record, not a rounded value in this
document, controls regression acceptance.

## Scope remaining closed

The source artwork uses `mu_BH` horizontally and an unresolved
`rho_source_figure5` vertically. No reviewed public dictionary maps that
ordinate to `rho_canonical_BH`; absolute comparison and full Figure 5 topology
therefore remain blocked. The historical C3h dense topology campaign remains
a failed optional extension and is neither repaired nor waived. Free energy,
coexistence, critical exponents, DOP853 cross-validation, global branch
completeness, Phase 5C, and empirical-QCD claims require separate review.

All earlier amendments, conditioning studies, maps, hard stops, and owner
decisions remain available in the [Phase 5B development history](history/dewolfe-gubser-rosen-emd-phase-5b-development-history.md).
