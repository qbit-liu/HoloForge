# HoloForge Version 0.2 Specification

**Status:** complete and approved by Xin-Yi Liu on 2026-08-02.

## Objective

Version 0.2 tests whether HoloForge can express and verify two genuinely
different bottom-up problems through common scientific contracts without
hiding their distinct numerical structures.

The existing soft-wall eigenvalue problem is retained. The second benchmark is
the minimal probe-limit holographic superconductor of Hartnoll, Herzog, and
Horowitz, using the dimension-two quantization.

## Included

- Shared descriptors for backgrounds, equations, boundary conditions,
  solvers, observables, acceptance gates, and verification records.
- Migration of the v0.1 soft-wall result into the common verification envelope
  without changing its equation, solver, defaults, or tolerance.
- A linear shooting calculation of the superconducting instability.
- A nonlinear boundary-value continuation of the dimension-two condensate.
- An original numerical reproduction of Figure 1's right-panel observable in
  arXiv:0803.3295v1.
- Human-readable and JSON command output, explicit provenance, convergence
  tests, and an optional Matplotlib plot artifact.

## Scientific conventions

The coordinate is `u = r_h/r`, with the AdS boundary at `u = 0`, the horizon
at `u = 1`, and `L = r_h = 1` during the dimensionless solve. The blackening
factor is `f(u) = 1 - u^3`.

The gauge field has UV expansion

```text
phi(u) = mu - rho u + ...,
```

where `mu` is a nonzero gauge-field source. The scalar has expansion

```text
psi(u) = psi_- u + psi_+ u^2 + ... .
```

Version 0.2 fixes `psi_- = 0`: the scalar source vanishes, while the chemical
potential does not. This defines spontaneous condensation in the `Delta = 2`
quantization. The onset is reported in the grand-canonical language through
`T_c/mu`; the Figure 1 curve is presented at fixed charge density through
scale-invariant ratios. These are distinct ensemble descriptions, not distinct
bulk solution families.

## Numerical methods

The onset calculation integrates the linear scalar equation in the normal
phase with `scipy.integrate.solve_ivp` and locates the
vanishing-scalar-source solution with `scipy.optimize.root_scalar`.

The nonlinear condensate branch solves the coupled scalar and Maxwell
equations with `scipy.integrate.solve_bvp`. Continuation uses the horizon scalar
value as its control parameter. HoloForge does not implement a custom ODE
integrator, root finder, or collocation method.

## Acceptance criteria

At the documented defaults:

1. the scalar-source residual is below `1e-8` at onset and along the nonlinear
   branch;
2. the nonlinear collocation residual satisfies the configured boundary-value
   tolerance;
3. halving the onset cutoff changes `mu_c/r_h` by less than `1e-6`;
4. `T_c/sqrt(rho)` differs from the source's rounded value `0.118` by at most
   `0.001`;
5. the near-critical condensate coefficient agrees within 5% with
   `<O_2> = 144 T_c^2 sqrt(1 - T/T_c)`;
6. the nonlinear curve reaches `T/T_c <= 0.06` with
   `8.2 <= sqrt(<O_2>)/T_c <= 8.7` and is monotonic;
7. a representative nonlinear observable remains stable under radial-cutoff
   refinement;
8. both benchmark records contain conventions, boundary roles, solvers,
   observables, runtime versions, and individual pass/fail gates.

## Explicitly not included

- Metric backreaction or a zero-temperature backreacted ground state.
- Optical conductivity, quasinormal modes, or free-energy comparison.
- The alternative `Delta = 1` quantization and Figure 1's left panel.
- A claim that the model describes a particular material.
- A claim that the boundary global U(1) is literally electromagnetism without
  an additional weak gauging prescription.

## Definition of done

Version 0.2 is complete when both benchmarks pass from a clean installation,
the generated condensate plot is visually inspected, all model cards satisfy
their schemas, the package build succeeds, and Xin-Yi Liu approves the
scientific conventions and numerical evidence.
