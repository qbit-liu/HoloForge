# HHH optical-conductivity current contract

## Status and scientific boundary

This is the active Forge/Verify contract for Phase 4 of the classical
benchmark sequence. Xin-Yi Liu approved the corrected result and bounded
public promotion on 2026-08-21. Phase 4 was merged, verified in the
authoritative CI matrix, and released in Version 0.5.5.

The accepted calculation reproduces the exact normal conductivity and the
near-critical dimension-two superfluid-density coefficient of Hartnoll,
Herzog, and Horowitz, [arXiv:0803.3295v1](https://arxiv.org/abs/0803.3295).
It also preserves the separately verified source Figure 1 right-panel
condensate result. The source Figure 2 rightmost curve is **not reproduced**;
it is provenance-only and cannot enter an acceptance gate.

## Frozen implementation

The benchmark identifier and command are

```text
holographic-superconductor-optical
holoforge verify holographic-superconductor-optical
```

The model uses the protected probe-limit dimension-two HHH background with
`m^2 L^2=-2`, `q=1`, `psi_-=0`, `u=r_h/r`, and the retarded convention
`exp(-i omega t)`. The primary response is a source-free UV-series transfer
to a Chebyshev--Gauss--Lobatto bulk solve. Riccati DOP853 is the independent
finite-frequency route; a static London solve supplies the zero-frequency
cross-check.

The current near-critical window is

```text
T/T_c = (0.990, 0.995, 0.9975, 0.999)
N     = (128, 160, 192)
```

The independent equation-residual ceiling is `1e-6`. The accepted equations,
boundary conditions, defaults, solver degrees, tolerances, twelve acceptance
gates, CLI schema, and model-card bytes are frozen by the implementation,
tests, and evidence record.

## Accepted result

The static and finite-frequency fits give

```text
C_2 static = 23.96884334975214
C_2 pole   = 23.968833072939002
source     = 24
```

The protected low-temperature condensate scale remains
`sqrt(<O_2>)/T_c=8.443622405101506`. All twelve declared gates must pass,
including exact-normal response, independent-route agreement, spectral
refinement, protected-background regression, and strict non-inference from
Figure 2.

## Scope remaining closed

No Figure 2 reproduction, source-caption repair, zero-temperature ground
state, backreaction, sum rule, free energy, quasinormal-mode spectrum,
finite-momentum response, nonlinear transport, material interpretation, or
empirical validation is claimed.

The complete sequence of amendments, failed superseded routes, portability
diagnostics, decisions, commits, CI runs, and release closure is preserved in
the [Phase 4 development history](history/holographic-superconductor-optical-development-history.md).
That history is evidence, not a second active contract.
