# Gubser--Nellore Einstein--Dilaton Benchmark Contract

**Status:** Decisions C1--C5 and revised Decisions R1--R10 were approved by the
owner on 2026-08-16. After the classified continuation stops documented below,
the approved coupled-equation production route passed all fourteen frozen
gates. Xin-Yi Liu accepted the implementation, derived anchors, reproduced
claim, model card, and evidence boundary on 2026-08-17 and authorized one
scoped local commit. Push, pull request, merge, tag, release, EMD, and iHQCD
remain unauthorized.

## Recommendation

Add one five-dimensional, zero-density Einstein--dilaton benchmark based on
Gubser and Nellore, with Chebyshev--Gauss--Lobatto collocation as the primary
numerical route and the paper's horizon-seeded ODE integration as an
independent check. Reproduce the paper's pure-cosh calibration curve and the
red black-hole curve of its QCD-like example.

This benchmark should precede an Einstein--Maxwell--dilaton example. Under the
approved roadmap, it replaces the need to add improved holographic QCD merely
to obtain a first dynamical gravity--scalar benchmark. It does not establish
that improved holographic QCD and the Gubser--Nellore model are physically
equivalent.

## Primary public source

Steven S. Gubser and Abhinav Nellore, "Mimicking the QCD equation of state
with a dual black hole," *Physical Review D* **78**, 086007 (2008),
[arXiv:0804.0434](https://arxiv.org/abs/0804.0434),
[DOI:10.1103/PhysRevD.78.086007](https://doi.org/10.1103/PhysRevD.78.086007).

The public arXiv PDF and TeX/EPS source archive retrieved during contract
preparation had SHA-256 digests:

```text
PDF:    ba8f25d69881fdb0a659651258a792377b83104de12bc1e30ee09532a9434809
source: 49057620542ad6839890f8328897615f0a5272e365ea06c806073d0147803360
```

The contract uses source Eqs. (1)--(4), (24)--(29), (34), (36)--(45),
(51)--(52), and (60)--(64), together with Figures 2 and 3. The source TeX and
vector figures were inspected directly. No source archive, source figure, or
copyrighted prose will be committed.

## Support and review state

- The action, background equations, endpoint expansions, thermodynamic
  formulas, two potentials, and displayed source curves are
  `established-source`, AI-transcribed, and owner-approved.
- The vector-figure anchor extraction below is an owner-approved derived source
  record. It is not raw numerical data supplied by the authors.
- The HoloForge coupled-equation calculation is `reproduced` and
  owner-approved because every frozen gate passes.
- Agreement with lattice QCD, phenomenological validity, novelty, top-down
  origin, and relevance to unpublished research are not claimed.

## Action and conventions

Use five bulk dimensions, metric signature `(-,+,+,+,+)`, dimensionless scalar
`phi`, and source normalization

```text
S = 1/(2 kappa_5^2) integral d^5x sqrt(-g) [
      R - (1/2) (partial phi)^2 - V(phi)
    ].
```

In scalar-coordinate gauge, `r = phi`, use

```text
ds^2 = exp(2 A(phi)) [-h(phi) dt^2 + d x_vec^2]
     + exp(2 B(phi)) dphi^2/h(phi).
```

The conformal boundary is at `phi -> 0+`; the regular horizon is at
`phi = phi_H > 0`; `h(phi_H) = 0` is a simple zero; and `A` and `B` are finite
at the horizon. Primes below mean `d/dphi`. The equations are

```text
A'' - A' B' + 1/6 = 0,
h'' + (4 A' - B') h' = 0,
6 A' h' + h (24 A'^2 - 1) + 2 exp(2 B) V = 0,
4 A' - B' + h'/h - exp(2 B) V'/h = 0.
```

Set `L = 1` and `Lambda L = 1`. Near the UV maximum,

```text
V(phi) = -12/L^2 + (1/2) m^2 phi^2 + O(phi^3),
Delta (Delta - 4) = m^2 L^2,
A(phi) = log(phi)/(Delta - 4) + o(1).
```

`kappa_5` is retained in the entropy formula but cancels from the speed of
sound. The benchmark is at zero chemical potential and has no Maxwell field.

## Master field and endpoint data

Define the generating function

```text
G(phi) = A'(phi).
```

The source master equation is

```text
G'/(G + V/(3 V'))
  = d/dphi log[
      G'/G + 1/(6 G) - 4 G - G'/(G + V/(3 V'))
    ].
```

The first two horizon-series coefficients are fixed by the source:

```text
G(phi) = -V(phi_H)/(3 V'(phi_H))
       + (1/6) [V(phi_H) V''(phi_H)/V'(phi_H)^2 - 1]
         (phi - phi_H)
       + O((phi - phi_H)^2).
```

The spectral residual may use an algebraically cross-multiplied form only if a
symbolic unit test demonstrates equivalence to the displayed equation away
from its named denominators. Both the raw and regularized residuals must be
reported on an independent grid so cross multiplication cannot silently admit
a spurious root.

## Approved-contract preflight and technical stop

The owner approved Decisions C1--C5 on 2026-08-16. Before adding production
files, a local scratch preflight tested the frozen spectral formulation at
`phi_H = 1` for both presets. It produced a technical stop, not a physics
result.

The leading source asymptotic behavior is

```text
G(phi) = 1/((Delta - 4) phi) + subleading terms.
```

On `[1e-5, 1 - 1e-5]`, the frozen global Chebyshev grid cannot represent this
raw pole at the approved degrees. Applying the approved differentiation matrix
to the exact leading analytic function gave a scaled derivative error at the
horizon of approximately `9.59e4` at `N = 80`; even `N = 320` remained at
approximately `5.44e4`. At `N = 80`, the minimum node spacing is approximately
`3.85e-4`, compared with the `1e-5` UV cutoff. The raw-`G` nonlinear solve
consequently failed and ran away. Increasing the solver effort would not
resolve the representation defect.

A scratch-only feasibility test used the regular UV field

```text
Y(phi) = phi G(phi),
G       = Y/phi,
G'      = Y'/phi - Y/phi^2,
G''     = Y''/phi - 2 Y'/phi^2 + 2 Y/phi^3.
```

This changes only the numerical unknown, not the physical master equation.
With deterministic degree continuation `24 -> 40 -> 60 -> 80`, SciPy's frozen
`hybr` solver converged for both presets. At `N = 80`, representative scaled
collocation residuals were below `9e-13`; a 2-times-or-denser independent
evaluation of the algebraically regularized equation was below `4.0e-9` for
the cosh preset and `6.4e-9` for the QCD-like preset. The UV and horizon values
also matched their analytic targets at about `1e-9` or better.

The direct raw equation remains ill-conditioned near the UV because its large
singular terms cancel. In a high-precision evaluation of the Chebyshev
interpolant, its scaled residual on the declared diagnostic interval
`u >= 0.05` was approximately `9.2e-9` for the cosh preset and `2.3e-7` for the
QCD-like preset at `N = 80`; it grows rapidly toward the UV cutoff. This is
consistent with the regularized equation but misses frozen Gate 4's full-domain
`1e-8` raw threshold. No thermodynamic integral, source anchor, reconstructed
metric equation, or figure curve was accepted from this scratch test.

These observations trigger the existing hard stops for an unapproved
regularization and for a non-diagnostic residual gate. Production ED files
must not be created until the revised decisions at the end of this document
are approved.

## Thermodynamic observables

For a solved `G(phi)` and the source UV convention, compute

```text
A_H = log(phi_H)/(Delta - 4)
    + integral_0^phi_H [G(phi) - 1/((Delta - 4) phi)] dphi,

s = (2 pi/kappa_5^2) phi_H^(3/(Delta - 4))
    * exp{3 integral_0^phi_H
          [G(phi) - 1/((Delta - 4) phi)] dphi},

T = phi_H^(1/(Delta - 4))/(pi L) * V(phi_H)/V(0)
    * exp{integral_0^phi_H
          [G(phi) - 1/((Delta - 4) phi) + 1/(6 G(phi))] dphi},

c_s^2 = d log(T)/d log(s).
```

Integrals must use the spectral representation and a maintained quadrature
routine. The explicit UV singular terms must be cancelled analytically before
numerical evaluation. No finite difference across unsorted or multivalued
thermodynamic branches is permitted.

## Frozen source presets

### Preset `cosh-calibration`

```text
V(phi) = -12/L^2 cosh(phi/sqrt(6)),
gamma = 1/sqrt(6),
m^2 L^2 = -2,
Delta = 2 + sqrt(2).
```

Reproduce the solid curve in source Figure 2 as `c_s^2` versus `T L`. The
dashed line is the conformal UV value `c_s^2 = 1/3` and is an analytic
annotation, not a numerical target. The low-temperature limit of the solid
curve is

```text
c_s,IR^2 = 1/3 - gamma^2/2 = 1/4.
```

### Preset `qcd-like`

```text
V(phi) = -12/L^2 cosh(gamma phi) + b phi^2,
gamma = 0.606,
b = 2.06/L^2,
Delta = 2 + sqrt(4 + 2 b L^2 - 12 gamma^2) approximately 3.93,
c_s,IR^2 = 1/3 - gamma^2/2 approximately 0.15.
```

Reproduce only the red black-hole curve in source Figure 3. The blue pure-glue
curve is partly based on private communication cited by the paper, and the
purple `2+1` lattice points are a different dataset. Neither is reference data
for this benchmark.

The source does not define the horizontal registration of its Figure 3 black-
hole curve in enough detail to treat `T_c` as a prediction. The vector source
places the curve minimum at

```text
(T/T_c)_minimum = 0.9619,
c_s,minimum^2 = 0.04525.
```

For figure reproduction only, HoloForge will define

```text
T_c,plot = T_minimum / 0.9618971489.
```

This single, preregistered horizontal registration reproduces the published
plot coordinate. It is not a calculated critical temperature and must be
named `T_c_plot`, never `T_c` without qualification, in machine output.

## Derived vector-figure anchors

The anchors below were extracted from the public Mathematica-generated EPS
paths in the arXiv source archive. Axis tick positions define affine coordinate
maps; interpolation is linear between adjacent vector-path vertices. The EPS
integer coordinate grid and line width imply conservative ordinate
uncertainties of `5e-4` for Figure 2 and `1.5e-3` for Figure 3. These anchors,
their extraction formula, and the source-archive digest must be stored in the
future reference-data record.

Figure 2:

| `T L` | source `c_s^2` |
|---:|---:|
| 0.001 | 0.250406 |
| 0.050 | 0.283180 |
| 0.100 | 0.300728 |
| 0.200 | 0.315099 |
| 0.400 | 0.324212 |
| 0.600 | 0.327419 |
| 0.800 | 0.329051 |
| 1.000 | 0.329995 |
| 1.200 | 0.330616 |

Figure 3 red black-hole curve:

| `T/T_c_plot` | source `c_s^2` |
|---:|---:|
| 0.100 | 0.148926 |
| 0.250 | 0.143892 |
| 0.500 | 0.127101 |
| 0.750 | 0.094438 |
| 0.900 | 0.058930 |
| 1.000 | 0.057147 |
| 1.250 | 0.217849 |
| 1.500 | 0.271178 |
| 2.000 | 0.303988 |
| 3.000 | 0.319753 |
| 4.000 | 0.324540 |
| 5.000 | 0.326687 |

## Primary spectral route

Map `u = phi/phi_H` and solve the master equation by
Chebyshev--Gauss--Lobatto collocation on

```text
u in [epsilon_UV, 1 - epsilon_H].
```

The primary profile is:

```text
degrees N = [40, 60, 80],
(epsilon_UV, epsilon_H) = (1e-5, 1e-5),
nonlinear solver = scipy.optimize.root(method="hybr", xtol=1e-11),
maximum evaluations = 200 * (N + 1).
```

Replace two collocation rows with the horizon-series value and derivative at
`u = 1 - epsilon_H`. Evaluate the master equation at every remaining row.
Initialize the first horizon solution from the displayed horizon series and
use deterministic continuation in `log(phi_H)` for neighboring horizons. A
different nonlinear method, a private program, or a shooting fit is not a
silent rescue path.

The figure profile begins at `phi_H = 1` and advances in both directions in
steps `Delta log(phi_H) = 0.05`, stopping after both source-plot abscissa ranges
are bracketed by at least 5 percent or at the hard bounds
`1e-3 <= phi_H <= 20`. Failure to bracket a range is a stop, not permission to
extend or retune the scan.

The cutoff-refinement profile holds `N = 80` and uses

```text
(epsilon_UV, epsilon_H) =
  (1e-4, 1e-4), (3e-5, 3e-5), (1e-5, 1e-5).
```

If coupled UV and horizon refinement obscures the error source, implementation
must stop and request approval for a separately frozen two-dimensional cutoff
study.

## Independent source-like route

At the five preregistered horizons nearest

```text
phi_H = [0.25, 0.5, 1.0, 2.0, 4.0],
```

integrate the same master equation from `phi_H (1 - epsilon_H)` toward the UV
with the source horizon series and

```text
scipy.integrate.solve_ivp(
    method="DOP853", rtol=1e-10, atol=1e-12
).
```

This check contains no shooting parameter: it does not adjust horizon data to
match the spectral result. It is independent in discretization and evolution
direction, not independent in physical equations.

## Acceptance gates

All thresholds are preregistered proposals. They may be revised only through
owner review before implementation or after a classified stop; they must not
be weakened after seeing a desired curve.

1. **Potential and UV algebra:** `V(0)`, `m^2 L^2`, `Delta`, and the two IR
   speed-of-sound expressions agree with their analytic values to `1e-12`.
2. **Horizon data:** value and derivative residuals of the two displayed
   series coefficients are at most `1e-9` at every accepted horizon.
3. **Nonlinear convergence:** SciPy reports success and the scaled collocation
   residual infinity norm is at most `1e-9`.
4. **Independent master residual:** on a 2-times oversampled grid, the raw and
   regularized residual infinity norms are each at most `1e-8`; points within
   one cutoff of a named denominator zero are reported and excluded, not
   silently dropped.
5. **Reconstructed equations:** Eqs. (25a)--(25c) have scaled oversampled
   residual norms at most `1e-7`; the redundant scalar constraint (25d) is
   independently at most `1e-7`.
6. **Boundary and UV behavior:** the horizon conditions and the leading UV
   behavior of `G` and `A` each have scaled residual at most `1e-7`.
7. **Spectral refinement:** for every verification horizon, the maximum
   relative change in `T`, `s`, and `c_s^2` from `N = 60` to `N = 80` is at
   most `2e-4` and is smaller than the `N = 40` to `N = 60` change.
8. **Cutoff refinement:** the maximum relative change in those observables
   between the final two cutoff pairs is at most `5e-4` and improves over the
   first refinement.
9. **Independent integration:** spectral and DOP853 values of `T`, `s`, and
   `c_s^2` agree within relative error `5e-4` at the five named horizons.
10. **Thermodynamic derivative:** barycentric differentiation in `phi_H` and
    a shape-preserving local derivative agree on `c_s^2` within `1e-3` away
    from branch endpoints. Both derivative records are retained.
11. **Figure 2 reproduction:** the maximum absolute `c_s^2` discrepancy at
    the nine frozen anchors is at most `1.5e-3`.
12. **Figure 3 reproduction:** after the single declared `T_c_plot`
    registration, the maximum absolute `c_s^2` discrepancy at the twelve red
    anchors is at most `5e-3`.
13. **Branch integrity:** `T(phi_H)` and `s(phi_H)` ordering is explicit; no
    interpolation crosses a turning point or joins thermodynamically distinct
    branches without a recorded segment label.
14. **Determinism and interface:** two verifier runs agree in all reported
    observables to `1e-12`, using
    `|a-b|/max(1,|a|,|b|)`; JSON, human output, registry behavior, and installed
    wheel behavior pass their tests.
15. **Regression protection:** all pre-existing tests and all four existing
    benchmark default verifiers remain green and byte-stable where golden JSON
    is already asserted.

## Planned public interface and artifacts

The proposed default command is

```text
holoforge verify gubser-nellore-ed
```

It runs a bounded anchor profile for both presets. The extended reproduction
is explicit:

```text
holoforge verify gubser-nellore-ed --profile figure --output-dir OUTPUT_DIR
```

The machine record must include source ID and digest, preset and potential,
all horizon values, spectral degrees and cutoffs, nonlinear-solver status,
raw and regularized residuals, reconstructed-equation residuals, refinement
tables, independent-route comparisons, branch labels, figure anchors,
digitization uncertainty, `T_c_plot` registration, support state, review state,
and limitations.

The implementation proposal is limited to:

```text
src/holoforge/benchmarks/gubser_nellore_ed.py
src/holoforge/benchmarks/adapters/gubser_nellore_ed.py
domains/qcd/gubser_nellore_ed/README.md
domains/qcd/gubser_nellore_ed/model-card.json
domains/qcd/gubser_nellore_ed/reference-data/...
docs/benchmarks/gubser-nellore-ed.md
tests/test_gubser_nellore_ed.py
```

Narrow registry, CLI, schema, README, architecture, and changelog edits are
allowed only as needed to expose that benchmark. The shared Chebyshev module
may be extended only with equation-independent, separately tested primitives.

## Scientific limits

A passing benchmark supports only a numerical reproduction of the selected
classical, two-derivative, single-scalar bottom-up model.

It does not include or establish:

- nonzero chemical potential, a Maxwell field, baryon response, or an EMD
  equation of state;
- chiral symmetry breaking, confinement, asymptotic freedom, hadron physics,
  or the low-temperature QCD phase;
- a top-down string embedding, finite-coupling corrections, or quantum gravity
  corrections;
- empirical validation of QCD, a universal dilaton potential, or a prediction
  of the physical critical temperature;
- the paper's private-communication lattice input or any unpublished HoloForge
  research artifact.

## Hard stops

Stop and return to owner review before accepting a curve if:

- any transcribed source equation, sign, dimension, or endpoint convention is
  ambiguous or contradicted by the primary source;
- the nonlinear solve needs a solver, initial-data adjustment, domain map, or
  regularization not frozen here;
- a denominator zero, spurious spectral root, or conditioning problem makes a
  residual gate non-diagnostic;
- the deterministic horizon scan fails to cover a frozen figure range;
- a thermodynamic turning point makes branch assignment ambiguous;
- any gate misses, even when the plotted curve looks plausible;
- source-figure provenance, coordinate registration, or digitization
  uncertainty cannot be represented in the public reference-data schema;
- implementation would require private code, a private path, unpublished data,
  or a confidential identifier; or
- a change to an existing benchmark's equations, default method, tolerance,
  output schema, or established claim becomes necessary.

No unapproved shooting fallback, tolerance weakening, point deletion, or
post-hoc parameter fit is allowed.

## Owner decisions

### Decision C1 -- source and physical conventions

**Recommendation: approve.**

- **Reason:** the contract preserves the source action, scalar-coordinate
  gauge, endpoint behavior, master equation, and zero-density interpretation.
- **Opens:** these equations and conventions as the ED benchmark target.
- **Remains closed:** EMD, iHQCD, top-down, and QCD-validation claims.
- **Uncertainty:** the master equation is singular in its raw form at the
  horizon, so regularization equivalence is a hard numerical gate.

### Decision C2 -- presets, figures, and data boundary

**Recommendation: approve.**

- **Reason:** the two presets give one clean calibration and one classical
  QCD-like example, while the EPS anchors provide a quick, auditable check.
- **Opens:** reproducing Figure 2 and the Figure 3 red curve with the declared
  plot-only horizontal registration.
- **Remains closed:** the private-communication pure-glue curve, the `2+1`
  points, and interpretation of `T_c_plot` as a prediction.
- **Uncertainty:** the figure curves are vector-derived anchors rather than
  author-supplied numerical tables.

### Decision C3 -- spectral primary and independent route

**Recommendation: approve.**

- **Reason:** Chebyshev collocation matches the project's preferred method and
  is genuinely primary; DOP853 follows the source's horizon-seeded route only
  as an independent discretization check.
- **Opens:** the frozen degrees, cutoffs, continuation, and five ODE checks.
- **Remains closed:** production shooting, private Mathematica reuse, a custom
  nonlinear solver, and a full coupled-EOM rescue implementation.
- **Uncertainty:** nonlinear global collocation of the master equation has not
  yet been demonstrated in HoloForge; failure triggers review.

### Decision C4 -- acceptance gates and public outputs

**Recommendation: approve.**

- **Reason:** the fifteen gates separate algebra, equation residuals,
  endpoints, convergence, independent numerics, thermodynamics, figures,
  branches, interfaces, and regressions.
- **Opens:** the named JSON evidence, reference data, documentation, tests, and
  source-curve reproduction after implementation authorization.
- **Remains closed:** retrospective threshold changes and unsupported claims.
- **Uncertainty:** the preregistered tolerances have not been tuned against an
  implementation; a miss may reveal either a defect or an overaggressive gate.

### Decision C5 -- sequencing and authorization

**Recommendation: approve bounded local ED implementation after reviewing the
compiled packet.**

- **Reason:** Phase 0 now supplies a tested shared spectral primitive, while
  this contract keeps the first dynamical gravity--scalar model narrow.
- **Opens:** local implementation of only the files and commands named above.
- **Remains closed:** EMD implementation, iHQCD, model-card approval, commit,
  push, pull request, merge, tag, release, and any public transfer from the
  private Explore repository.
- **Uncertainty:** any hard stop returns the model to owner review before the
  roadmap advances.

## Revised owner decisions after the technical stop

Decisions C1--C5 remain the approved scientific contract except where an
approved revised decision below explicitly supersedes the frozen numerical
formulation. The source, presets, targets, thermodynamic definitions, figure
anchors, DOP853 comparison, reconstructed-equation checks, and closed scope do
not change.

### Decision R1 -- regular UV spectral unknown

**Recommendation: approve `Y(phi) = phi G(phi)` as the primary collocation
unknown.**

- **Reason:** `Y` is finite at the UV endpoint, while exact analytic
  reconstruction preserves the same source master equation and physical
  generating function `G`.
- **Opens:** the displayed `Y`, `G`, `G'`, and `G''` relations in the local ED
  implementation and their symbolic-equivalence tests.
- **Remains closed:** a different physical equation, fitted endpoint data,
  multidomain mapping, rational basis, or shooting fallback.
- **Uncertainty:** feasibility has been checked only at `phi_H = 1`; every
  production horizon must still pass all applicable gates.

### Decision R2 -- deterministic degree seed

**Recommendation: approve `N = 24` only as a deterministic nonlinear seed,
followed by `24 -> 40 -> 60 -> 80` degree continuation.**

- **Reason:** both presets reached the same regular solution under this fixed
  sequence; direct high-degree initialization was less reliable.
- **Opens:** interpolation of the converged lower-degree `Y` profile as the
  next initial iterate.
- **Remains closed:** treating `N = 24` as acceptance evidence, adaptive degree
  tuning, arbitrary restarts, or parameter fitting.
- **Uncertainty:** continuation in `phi_H` and in degree may interact; any
  resulting branch ambiguity remains a stop.

### Decision R3 -- split residual diagnostics

**Recommendation: retain the full-domain, 2-times-oversampled regularized
residual threshold of `1e-8`, and revise the raw-equation diagnostic to a
scaled threshold of `1e-6` on `0.05 <= u <= 1 - epsilon_H`.**

The raw residual must be evaluated directly from the interpolated `Y` profile,
not as the regularized residual divided by a prefactor. The full raw-residual
profile from `epsilon_UV` onward must be stored so the UV conditioning region
is visible. Named denominators and their minima remain mandatory output;
denominator zeros retain the original stop/exclusion rule. The symbolic
equivalence identity, full-domain regularized residual, reconstructed Einstein
equations, UV asymptotics, spectral refinement, cutoff refinement, and DOP853
checks remain unchanged.

- **Reason:** this keeps a direct check of the unmodified master equation in a
  numerically diagnostic interior region without pretending that singular UV
  cancellations are accurate in double precision.
- **Opens:** a declared conditioning window and the revised Gate 4 threshold;
  the interval and threshold are frozen before any figure scan.
- **Remains closed:** deleting failed points, reporting only a best region,
  inferring the raw check from the regularized equation, or weakening any
  independent EOM/ODE gate.
- **Uncertainty:** the `phi_H = 1` QCD-like preflight has only a factor of about
  four margin below `1e-6`; another horizon may still trigger a valid stop.

### Decision R4 -- resume boundary

**Recommendation: approve resuming the same bounded local ED implementation
under R1--R3.**

- **Reason:** the revision addresses the classified numerical failure while
  preserving the approved scientific target and independent verification.
- **Opens:** only the production files and validation already authorized by
  C5, with R1--R3 recorded in their tests and model documentation.
- **Remains closed:** EMD, iHQCD, support-state approval, commit, push, pull
  request, merge, tag, release, and private-to-public transfer.
- **Uncertainty:** no thermodynamic or figure-reproduction gate has yet run;
  the next miss returns to owner review rather than triggering another rescue.

### R1--R4 approval and resumed-implementation finding

The owner approved R1--R4 on 2026-08-16. The resumed implementation derived
the next, equation-determined coefficient in the regular horizon series. The
source states that this series can be continued to arbitrary order; the added
coefficient introduces no fitted datum. It removes the cutoff-level
`O(epsilon_H)` derivative truncation that otherwise made the oversampled
near-horizon residual non-diagnostic.

At `phi_H = 1`, both presets then passed the revised primary diagnostics. The
`N = 80` scaled regularized residuals were below `3e-9`, the declared-window
raw residuals were below `2e-7`, and the independent DOP853 master profiles
agreed with the spectral profiles at approximately `1e-10` (cosh) and `1e-12`
(QCD-like). Reconstructed Eqs. (25a--d) pass `1e-7` when the reconstruction
quadrature is resolved. These are implementation preflights, not accepted
thermodynamic or figure results.

The QCD-like continuation toward larger `phi_H` reaches a new stop near
`phi_H = 3.67`: the frozen `N = 24` seed fails, and the mandated same-horizon
`24 -> 40` handoff can leave `N = 40` unconverged. Higher degrees can still
find small-residual profiles under alternative seeds, which identifies this as
a low-degree initialization problem rather than evidence that the ED branch
does not exist. Using a previous-horizon same-degree seed, dropping `N = 24`,
or importing a private initialization strategy would be an unapproved rescue.
The source-figure scan therefore remains stopped pending comparison with the
owner's existing spectral implementation or a separately approved deterministic
continuation revision.

## Clean-room coupled-equation feasibility finding

The continuation stop was numerical, not physical. A scratch-only derivation
used conformal radial gauge

```text
ds^2 = exp(2 A_E(z))/z^2 [ -f(z) dt^2 + d x_vec^2 + dz^2/f(z) ]
```

and the same canonical scalar action and source potentials. With
`p = 4 - Delta` and `x = z^p`, the coupled equations become

```text
f_xx + [3 A_E,x + (1 - 4/p)/x] f_x = 0,

A_E,xx + [(1 + 1/p)/x] A_E,x
       - A_E,x^2 + phi_x^2/6 = 0,

phi_xx + [3 A_E,x + f_x/f + (1 - 4/p)/x] phi_x
       - exp(2 A_E) V'(phi)/(p^2 x^2 f) = 0.
```

Map `u = x/x_H` and factor the source UV behavior as

```text
phi(u) = x_H u P(u),       P(0) = 1,
A_E(u) = x_H^2 u^2 C(u),
f(0) = 1,                 f(1) = 0.
```

The `C` equation is imposed at both endpoints. The scalar equation is replaced
by `P(0) = 1` only at the UV endpoint and is retained at `u = 1`, where it
imposes horizon regularity. Thus the method includes the exact boundary and
horizon rather than introducing UV and horizon cutoffs. The transformed
equations and factorizations must receive symbolic or analytic regression
tests before production use.

The scratch implementation used only maintained NumPy/SciPy primitives and
Chebyshev--Lobatto collocation. No external implementation code, stored
solution, or private result was copied. Its bounded findings were:

- The QCD-like branch continued from `x_H = 0.2` through `x_H = 1.25`, covering
  approximately `0.204 <= phi_H <= 21.03`; the former stop near
  `phi_H = 3.67` disappeared under previous-horizon same-degree continuation.
- At `phi_H = 1.13705534112`, the coupled and scalar-coordinate master routes
  agreed in `T` and `s` within `2.1e-11` relative error.
- At the five preregistered QCD-like horizons nearest
  `[0.25, 0.5, 1, 2, 4]`, coupled thermodynamics and the source-like DOP853
  route agreed within `5.2e-12` for `T` and `1.7e-11` for `s`.
- At the worst sampled high-degree QCD-like point, a deterministic
  least-squares polish reduced the scaled collocation residual from about
  `1.3e-7` to `4.6e-10`; the independently oversampled coupled-equation
  residual was below `3.0e-8`.
- Across the tested QCD-like branch, the largest sampled thermodynamic change
  among the high-degree profiles was below `5.4e-10`. Strict ordering of
  successive changes was not meaningful once differences reached the
  floating-point floor.
- A fine QCD-like scratch scan reproduced all twelve Figure 3 anchors with
  maximum absolute discrepancy `2.43e-3`, below the frozen `5e-3` threshold;
  its two local derivative constructions differed by at most `5.88e-4`, below
  the frozen `1e-3` threshold.
- The pure-cosh scan covered `0.00089 < T L < 16.3`. It reproduced all nine
  Figure 2 anchors with maximum absolute discrepancy `7.31e-5`, below the
  frozen `1.5e-3` threshold. Its `N = 40` to `N = 60` anchor change was below
  `1.4e-9`, and the two derivative constructions differed by at most
  `4.91e-7`.
- At the five preregistered pure-cosh horizons, the coupled and master routes
  agreed within `3.8e-13` for `T` and `3.7e-12` for `s`; the master and DOP853
  routes agreed within `3.2e-10` for `T` and `9.6e-10` for `s`.

These are feasibility measurements used to classify and revise the stopped
numerical contract. They are not accepted benchmark results, and the displayed
curve agreement is not permission to weaken a gate after implementation.

## Proposed revised owner decisions after the continuation stop

If approved, R5--R8 supersede only the primary numerical formulation,
continuation rule, and master-specific/cutoff-specific gates. The action,
potentials, thermodynamics, figure anchors, DOP853 route, figure tolerances,
scientific limits, interface boundary, and disclosure boundary remain as
approved under C1--C5 and R1--R4.

### Decision R5 -- full coupled equations as the primary spectral route

**Recommendation: approve the displayed UV-factorized coupled formulation.**

- **Reason:** it solves the physical Einstein--scalar boundary-value problem
  directly, includes both exact endpoints, crosses the classified
  master-field continuation stop, and agrees with two independent
  scalar-coordinate routes.
- **Opens:** production fields `f`, `C`, and `P`; the `x = z^p` map; the
  displayed factorizations; and exact-endpoint collocation.
- **Remains closed:** a Maxwell field, finite density, EMD, a shooting fit,
  copied external code, multidomain rescue, fitted boundary data, and any
  change to the source potential or thermodynamic normalization.
- **Uncertainty:** the QCD-like infrared profiles require higher spectral
  degree than the pure-cosh calibration, and dense differentiation matrices
  approach their double-precision conditioning floor.

### Decision R6 -- deterministic continuation and nonlinear solve

**Recommendation: approve previous-horizon same-degree continuation and a
frozen two-stage maintained-library nonlinear solve.**

At the initial horizon, use degree continuation `24 -> 40 -> 60 -> 80`.
Thereafter, seed each degree from the preceding horizon at the same degree;
interpolation from the current lower degree is allowed only to initialize a
new verification degree. The primary curve uses `N = 80`. Pure-cosh
verification uses `N = [40, 60, 80]`; QCD-like infrared verification uses
`N = [80, 120, 150]` at the frozen verification horizons, figure-anchor
neighbors, thermodynamic extrema, and branch endpoints.

Use `scipy.optimize.root(method="hybr", xtol=1e-11)` to locate the solution.
If it reports failure or its scaled residual exceeds `1e-9`, apply the frozen
polish

```text
scipy.optimize.least_squares(
    method="trf", ftol=1e-14, xtol=1e-14, gtol=1e-14, max_nfev=12
)
```

from that iterate. Report both solver states and function-evaluation counts.
The polish is part of the preregistered route, not a discretionary fallback.

- **Reason:** same-degree continuation preserves the physical branch without
  making an unresolved low-order profile a mandatory gate; least-squares
  polishing resolves high-degree residual stagnation without changing the
  equations or data.
- **Opens:** only the stated seed hierarchy and nonlinear polish.
- **Remains closed:** arbitrary restarts, parameter fitting, point deletion,
  tolerance changes, private initialization data, and choosing a solver after
  inspecting curve agreement.
- **Uncertainty:** the final production scan may expose a new conditioning or
  branch stop; any such stop returns to owner review.

### Decision R7 -- coupled-equation acceptance gates

**Recommendation: replace master-specific Gates 2--6 and cutoff Gate 8 with
the following direct coupled-equation gates; retain all other applicable
gates.**

1. The final nonlinear solver reports success and its scaled collocation
   residual infinity norm is at most `1e-9`.
2. On an independently evaluated grid at least twice as dense, the scaled
   residual infinity norm of each of the three displayed physical equations
   is at most `1e-7` at every verification horizon.
3. The exact `f(0)`, `f(1)`, and `P(0)` boundary residuals and the leading
   `phi/x -> 1`, `A_E/x^2 -> finite` UV behavior are each at most `1e-7`.
4. The horizon scalar equation is retained and passes the same `1e-7`
   independent residual threshold; no separately fitted horizon datum is
   allowed.
5. Both successive thermodynamic refinement changes must be at most `2e-4`.
   The decrease ordering is additionally required whenever the earlier change
   exceeds `1e-8`; below that numerical floor the ordering is reported but is
   not a binary gate.
6. Because the coupled domain contains the exact endpoints, the old cutoff
   refinement gate is inapplicable and is removed rather than weakened.
7. The five named DOP853 comparisons, thermodynamic-derivative gate, figure
   tolerances, branch-integrity gate, determinism/interface checks, and all
   regression checks retain their previously approved thresholds.

- **Reason:** these checks test the uncross-multiplied physical equations and
  exact endpoints directly. They remove diagnostics that exist only because
  the superseded master formulation omitted singular endpoints.
- **Opens:** acceptance evidence matched to the coupled boundary-value problem.
- **Remains closed:** accepting a visually correct curve with a failed direct
  equation, endpoint, refinement, independent-route, or branch gate.
- **Uncertainty:** the independently oversampled residual, rather than the
  collocation residual alone, remains the decisive guard against dense-matrix
  roundoff and interpolation error.

### Decision R8 -- resume boundary

**Recommendation: approve replacing the partial local ED implementation under
R5--R7 and running the complete retained/revised gate set.**

- **Reason:** the clean-room feasibility evidence resolves the specific
  continuation and conditioning stops without changing the scientific target.
- **Opens:** local implementation and validation only for the already approved
  Gubser--Nellore ED artifact list.
- **Remains closed:** accepting the model card, commit, push, pull request,
  merge, tag, release, EMD, iHQCD, or any public transfer of private material.
- **Uncertainty:** production evidence may still fail a retained gate, in
  which case the benchmark remains unaccepted and returns to owner review.

## R5--R8 approval and production continuation stop

The owner approved R5--R8 on 2026-08-16. The partial master-collocation module
was replaced locally by an independently structured Python implementation of
the displayed UV-factorized coupled equations. The pure-cosh production branch
passes its applicable first-run diagnostics: maximum Figure 2 anchor error
`7.31e-5`, maximum independently oversampled physical-equation residual
`2.83e-9`, maximum collocation residual `3.58e-10`, maximum DOP853 comparison
error `9.74e-10`, maximum derivative disagreement `5.67e-6`, and final
thermodynamic refinement change `2.57e-10`. These values are unaccepted
implementation evidence because the aggregate two-preset benchmark stopped
and the mandatory duplicate determinism run was not executed.

The QCD-like `N = 150` route exposes a new stop under R6. A direct jump from
`x_H = 0.20` to `0.21` fails, while deterministic same-degree substeps of
`Delta x_H = 1e-3` cross that first location and remain converged through
`x_H = 0.442`. At `x_H = 0.443` (`phi_H = 0.4927309663` on the failed
iterate), `scipy.optimize.root(method="hybr")` reports no progress after 917
function evaluations with scaled residual `4.14e-4`. The frozen 12-evaluation
TRF polish also reports failure and ends at scaled residual `4.30e-4`, far
above the unchanged `1e-9` gate. Continuing from this invalid profile corrupts
all downstream QCD-like residual, refinement, DOP853, and figure checks, so
none of those downstream values are scientific or numerical results.

This is a deterministic high-degree initialization stop, not evidence that the
coupled ED branch is absent. The primary `N = 80` and middle `N = 120` routes
are not the failing rows, and the earlier clean-room feasibility scan already
showed that current-horizon degree continuation reaches the valid high-degree
branch. R6 nevertheless froze preceding-horizon same-degree seeding, so that
alternative cannot be adopted silently after this production failure.

## Proposed revision after the R6 production stop

### Decision R9 -- deterministic high-degree seed hierarchy

**Recommendation: keep same-degree continuation for the primary `N = 80`
curve, but initialize each new verification degree at a target horizon from
the converged current-horizon lower degree.**

At every reported QCD-like target horizon, solve in the frozen order
`N = 80 -> 120 -> 150`. Seed `N = 80` only from the preceding `N = 80`
horizon; seed `N = 120` from the current `N = 80` solution and `N = 150` from
the current `N = 120` solution. Retain the same equations, target horizons,
`hybr` solve, frozen TRF polish, residual thresholds, independent oversampling,
thermodynamic refinement comparisons, and DOP853 checks. The lower-degree seed
selects an iterate; it does not supply acceptance evidence for the higher
degree, which must independently pass every high-degree gate.

- **Reason:** this is the deterministic degree-continuation route already
  demonstrated in the clean-room feasibility study and avoids propagating a
  precision-sensitive high-degree iterate across parameter space.
- **Opens:** only the stated current-horizon lower-degree initialization for
  the QCD-like verification degrees.
- **Remains closed:** multiple discretionary restarts, best-of-seed selection,
  threshold changes, fitted data, a different nonlinear solver, copied code,
  EMD, iHQCD, model acceptance, Git actions, and publication.
- **Uncertainty:** the production rerun must still pass every unchanged direct
  equation, refinement, independent-route, branch, figure, and determinism
  gate; feasibility agreement is not acceptance.

### Decision R10 -- second resume boundary

**Recommendation: after approving R9, resume only the local coupled ED
implementation and complete verification.**

- **Reason:** R9 changes only the classified failing initialization rule and
  is prospectively explicit before another production run.
- **Opens:** the same bounded artifact list and full retained/revised gate set.
- **Remains closed:** model-card acceptance, commit, push, pull request, merge,
  tag, release, EMD, iHQCD, and any private-material transfer.
- **Uncertainty:** any new gate miss remains a mandatory owner return.

### R9--R10 owner disposition

Xin-Yi Liu approved R9--R10 through Option A on 2026-08-16. The implementation
may now replace only the classified QCD-like high-degree seed hierarchy and
rerun the complete unchanged verification contract. This approval does not
accept an ED result or model card and does not authorize a commit, push, pull
request, merge, release, EMD, or iHQCD work.

## R9 production implementation note

The R9 hierarchy reaches every frozen QCD-like verification horizon at
`N = 80, 120, 150`. A diagnostic primary scan with `Delta x_H = 0.01` passed
the equation, endpoint, refinement, DOP853, and branch gates but was too coarse
for the already frozen thermodynamic-derivative and Figure 3 interpolation
gates. Refining only the dense primary `N = 80` sampling to
`Delta x_H = 0.002` reduced the barycentric-versus-PCHIP disagreement from
`9.91e-3` to `4.41e-4` and the Figure 3 anchor error from `5.75e-3` to
`1.42e-3`. No equation, potential, endpoint, nonlinear method, source anchor,
registration, or acceptance threshold changed.

The production implementation therefore separates the roles already declared
by R6: the dense displayed curves use the primary `N = 80` branch, while
aligned three-degree branches supply high-degree residual, refinement, and
DOP853 evidence at verification horizons. The anchor profile uses 260 dense
pure-cosh points, 526 dense QCD-like points, 100 pure-cosh verification
horizons, and 106 QCD-like verification horizons. Every dense primary profile
still contributes nonlinear-status and collocation evidence; the independent
`2N` physical-equation gate is evaluated on the declared highest-degree
verification profiles.

The first corrected QCD-like stress run passed its individual numerical gates:
maximum collocation residual `8.40e-10`, maximum independently oversampled
physical-equation residual `9.39e-8`, maximum final refinement change
`1.64e-8`, maximum DOP853 comparison error `3.03e-11`, maximum derivative
disagreement `4.41e-4`, and maximum Figure 3 anchor error `1.42e-3`. These are
implementation measurements, not an accepted reproduced result. The mandatory
duplicate complete run, interface suite, artifact inspection, and owner review
remain required.

The subsequent extended `figure` profile completed two full deterministic
runs and passed all fourteen aggregate gates. The recorded maxima are
`9.37e-10` for the scaled collocation residual, `9.41e-8` for the independently
oversampled physical equations, `9.33e-9` for the final thermodynamic
refinement change, `1.14e-9` for the DOP853 comparison, `4.41e-4` for the
thermodynamic derivative disagreement, `7.31e-5` for Figure 2, `1.42e-3` for
Figure 3, and zero for the duplicate-run physical-observable difference. The
generated JSON, CSV, and visually inspected plot were initially retained as
`unreviewed`; the automated pass alone did not accept the model card or broaden
the evidence.

## Final owner disposition

Xin-Yi Liu selected Option A on 2026-08-17 and approved the implementation,
derived anchors, reproduced claim, model card, and evidence boundary. The
review state changes to `approved` without changing the support level beyond
`reproduced`, erasing AI provenance, or interpreting the result as empirical
QCD validation. The same decision authorizes one scoped local commit containing
the spectral foundation and this ED benchmark. It does not authorize a push,
pull request, merge, tag, release, EMD, or iHQCD stage.

## Current handoff

- **Completed:** spectral foundation; source contract and anchors; all
  classified stops; clean-room coupled implementation; full verification;
  owner acceptance of the ED implementation, model card, derived anchors,
  reproduced claim, and evidence boundary.
- **Current:** final staged audit and the authorized scoped local commit.
- **Proposed next:** stop after the local commit. Any push, pull request, merge,
  release, EMD, or iHQCD work requires a separate owner gate.

No owner approval is currently pending inside this closed benchmark gate.
