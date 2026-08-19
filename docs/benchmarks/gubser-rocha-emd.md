# Gubser--Rocha top-down-derived EMD control benchmark

## Scope and current status

This Forge/Verify control benchmark targets the homogeneous equal-charge charged
dilatonic black brane in S. S. Gubser and F. D. Rocha, “Peculiar properties of
a charged dilatonic black hole in AdS_5,” *Phys. Rev. D* 81, 046001 (2010),
[arXiv:0911.2898v2](https://arxiv.org/abs/0911.2898).

The five-dimensional action is a consistent truncation of maximal gauged
supergravity and the solution has a type IIB lift. This is therefore a
top-down-derived classical EMD reference used to test HoloForge's coupled
spectral infrastructure. It is not one of HoloForge's representative bottom-up
examples and must not be counted as such in project summaries.

The owner approved the source, conventions, cases, spectral route, acceptance
gates, bounded implementation, corrected origin classification, and final
bosonic reproduction on 2026-08-19. The result is owner-approved
`reproduced`. It verifies only the selected classical source solution and
Eqs. (2)--(6). It does not validate a Fermi liquid, QCD, any material, or the
owner's phenomenological EMD research model.

The source has one figure, a charged-fermion normal-mode plot. The present
program contains no Dirac field or fermion boundary-value problem and therefore
does not reproduce source Figure 1. Reproducing the bosonic background does not
validate that omitted sector. The optional HoloForge plot is a new diagnostic
visualization of the background fields, errors, and Eq. (6), not a source-
figure reproduction.

The larger unequal-charge STU theory has the cited instability threshold
`xi = 1`. Cases with `xi > 1` remain useful exact verification points but must
not be presented as stable phase selections.

## Action and conventions

With five bulk dimensions, signature `(-,+,+,+,+)`, and `L = 1`, use

```text
S = 1/(2 kappa_5^2) integral sqrt(-g)
    [R - 1/2 (partial phi)^2 - 1/4 Z(phi) F^2 - V(phi)],

phi = 2 sqrt(6) alpha,
Z(phi) = exp(sqrt(2/3) phi),
V(phi) = -[8 exp(phi/sqrt(6)) + 4 exp(-2 phi/sqrt(6))].
```

Thus `V(0) = -12`, `V'(0) = 0`, and `m^2 = V''(0) = -4`. The scalar saturates
the AdS5 BF bound. Its `z^2` coefficient is a response; the logarithmic scalar
source is zero.

The source calls its black-hole mass parameter `mu`. HoloForge calls it
`mu_bh` and reserves `Omega` for the chemical potential.

## Conformal-gauge problem

Set `L = r_H = 1`, define

```text
xi = Q/r_H,
theta = arctan(xi),
z_H = theta/xi, with z_H = 1 at xi = 0,
u = z/z_H in [0,1].
```

The metric and gauge field are

```text
ds^2 = exp(2A) [-f dt^2 + d x_vec^2 + dz^2/f],
A_t = Phi(z) dt.
```

The coupled equations are

```text
A'' - A'^2 + phi'^2/6 = 0,
f'' + 3 A' f' - exp(-2A) Z Phi'^2 = 0,
Phi'' + [A' + (Z_phi/Z) phi'] Phi' = 0,
f phi'' + (3 A' f + f') phi'
  - exp(2A) V_phi + exp(-2A) Z_phi Phi'^2/2 = 0.
```

The independent Einstein constraint is

```text
6 A' f' + f(24 A'^2 - phi'^2)
  + 2 exp(2A) V + exp(-2A) Z Phi'^2 = 0.
```

The primary unknowns factor the exact endpoint powers:

```text
A = -log(z) + u^4 a(u),
f = 1 - u^4 b(u),
phi = u^2 p(u),
Phi = -Omega + u^2 v(u).
```

The UV rows enforce `b'(0) = p'(0) = 0`; these are the regularity and no-log
conditions. The horizon rows enforce `b(1) = 1` and `v(1) = Omega`, while the
undivided scalar equation remains at `u = 1` and supplies horizon regularity.

## Numerical route

The primary route is the shared Chebyshev--Gauss--Lobatto primitive with exact
endpoints and degrees `N = 40, 60, 80`. The frozen continuation path is

```text
0, 0.25, 0.5, 0.75, 1, 1.5, 2, 3, 4, 6, 8, 12, 16.
```

At each charge, solve `40 -> 60 -> 80`. The first charged seed is the neutral
solution with only the prescribed gauge source shifted. Later coarse solves use
a deterministic secant predictor in `theta = arctan(xi)`; higher degrees use
the converged lower-degree numerical field. Charged exact profiles are never
solver seeds.

Each solve first uses
`scipy.optimize.root(method="hybr", xtol=1e-11)`. A failed or insufficient
root state receives at most thirty-two evaluations of the amended TRF residual
polish. The record retains both library states and the final scaled residual.
There is no shooting fallback, random restart, best-of-seed selection, UV or
horizon cutoff, or private-code dependency.

## Source checks and thermodynamics

The independent reference is the source closed-form family. On a grid twice as
dense, the verifier checks all four equations, the Einstein constraint, the
conserved Maxwell flux `J = -exp(A) Z Phi'`, and the exact fields.

After the fixed scale choice, the exact thermodynamics are

```text
mu_bh = (1 + xi^2)^2,
hat epsilon = 3 mu_bh/(8 pi^2),
hat s = (1 + xi^2)/(2 pi),
hat rho = sqrt(2) xi (1 + xi^2)/(4 pi^2),
T = 1/pi,
Omega = sqrt(2) xi.
```

The numerical fields independently extract the boundary `f` coefficient,
horizon area and derivative, boundary gauge source, and Maxwell flux. Source
Eq. (4) and both Eq. (5) derivatives are then checked. At `xi = 4, 8, 16`, the
declared fit tests

```text
4 hat s/(Omega^2 T) = 1 + 1/xi^2.
```

## Acceptance and hard stops

The thirteen frozen gates cover source algebra, all nonlinear states,
collocation residuals, independently oversampled equations, the Einstein
constraint, endpoint and BF-source conditions, Maxwell flux, exact fields,
three-level refinement, source thermodynamics, the equation of state,
low-temperature extrapolation, the neutral limit, determinism, and external
interface/regression checks. The precise thresholds are retained in
[`gubser-rocha-emd-contract.md`](gubser-rocha-emd-contract.md).

Any missed gate is reported. It is not repaired by weakening a threshold after
the result is known. A new coordinate map, solver, restart rule, regularization,
branch choice, or private input also requires a new owner decision.

## Owner-approved numerical-contract amendment

The initial preflight and its two failed gates remain preserved. After an
owner-authorized diagnostic round, the owner prospectively approved only these
changes on 2026-08-19:

- increase the TRF polish cap from `12` to `32` evaluations; and
- increase the refinement ordering floor from `1e-10` to `5e-10`.

All five affected coarse polishes reached SciPy success within `13`--`18`
evaluations and changed thermodynamics by at most `7.90e-14`. A non-reporting
`N = 100` diagnostic at `xi = 16` reduced all three disputed changes to roughly
`5e-11`. The amended floor covers the frozen `N = 80` exact-thermodynamic error
envelope while remaining 4000 times below the unchanged `2e-6` magnitude
tolerance. The root-first route, all tolerances, degrees, continuation, seeds,
equations, cases, and scientific boundaries remain unchanged.

This amendment is prospective. It does not retroactively pass the initial run,
accept a new result, or authorize any Git or public action.

## Commands

After installation:

```bash
holoforge verify gubser-rocha-emd
holoforge verify gubser-rocha-emd --json
holoforge verify gubser-rocha-emd --output-dir OUTPUT_DIR
python3 -m unittest tests.test_gubser_rocha_emd -v
```

The optional output directory receives a strict JSON record, a seven-case CSV,
and a HoloForge-generated verification plot. Existing files are never silently
overwritten. The plot is not source Figure 1 and contains no fermion result.

## Initial local preflight evidence

The 2026-08-19 local implementation reaches all charges and degrees. The
equation, constraint, boundary, flux, exact-field, thermodynamic, equation-of-
state, low-temperature, neutral, and determinism checks pass with substantial
margin. The final `N = 60 -> 80` thermodynamic change is roughly `1.1e-9`, well
below its `2e-6` magnitude tolerance.

Five coarse `N = 40` roots require the frozen twelve-evaluation TRF polish.
Their final residuals are approximately `1e-11`, but SciPy stops at the
evaluation limit and reports `success = false`. The residual gate passes while
the separately declared solver-status gate therefore fails. Accepting a small
residual in place of library success requires a new owner decision.

However, three `xi = 16` changes fluctuate between approximately `1.5e-10`
and `1.8e-10` rather than decrease monotonically. They are the extracted
`mu_bh`, its derived energy density, and the charge density. The frozen
refinement-ordering floor is `1e-10`, so this sub-gate currently fails. No
threshold revision is authorized by this guide.

## Amended clean preflight evidence

The complete owner-authorized clean rerun passes all thirteen gates without a
further threshold change. Four coarse states apply TRF polish and all report
SciPy success within `14`--`19` evaluations, below the amended cap of `32`.
The maximum collocation residual is `7.79e-10` against `1e-9`.

The maximum `N = 60 -> 80` thermodynamic change is `6.69e-10` against the
unchanged `2e-6` magnitude tolerance, with zero ordering failures above the
amended `5e-10` floor. The maximum independently oversampled equation residual
is `1.34e-8`, the maximum exact-field difference is `4.92e-10`, and the maximum
source-thermodynamic relative error is `1.17e-9`; each remains within its
declared gate.

The owner accepted this passing implementation evidence on 2026-08-19. The
model card and numerical result are `reproduced` and `approved`; the
instability, fermion, Figure 1, and non-inference boundaries above remain
unchanged.

## Release-candidate portability amendment

The first PR #23 run preserved an additional numerical-platform result. On
Ubuntu 24.04 with Python 3.11, NumPy 2.4.6, and SciPy 1.17.1, the installed
verifier measured a maximum final scaled collocation residual of
`1.960378e-9`; the matching macOS dependency versions measured
`9.579273e-10`. The original `1e-9` final ceiling therefore failed on Linux.
Every independent equation, constraint, boundary/source, flux, exact-field,
refinement, thermodynamic, equation-of-state, low-temperature, and neutral
gate passed in the Ubuntu wheel run.

The owner approved a prospective `3e-9` final collocation ceiling on
2026-08-19. The root-first route is unchanged: any failed root or root residual
above the separate, unchanged `1e-9` trigger still receives the declared TRF
polish, capped at 32 evaluations, and the maintained library must report
success. No independent tolerance or scientific claim changed. This amendment
addresses the observed cross-platform double-precision residual floor; it does
not turn the original failed CI run into a pass.
