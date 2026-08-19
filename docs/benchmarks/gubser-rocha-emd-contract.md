# Gubser--Rocha EMD benchmark contract and amendment record

## Status and authorization boundary

This document began as the **pre-implementation owner-review contract** for
Phase 2 of the classical benchmark sequence and now also preserves the
owner-approved numerical-contract amendment and origin-classification
correction, followed by the owner-approved result and release decision. It is
public-source Forge/Verify work. The benchmark is a
top-down-derived control for numerical infrastructure, not a representative
bottom-up example. On 2026-08-19 the owner accepted the bounded bosonic
reproduction, approved its model-card state, and authorized scoped Git and
Version 0.5.3 release actions. This approval does not open the charged-fermion
sector or source Figure 1.

- **Completed:** Phase 0 and Phase 1 are merged; the initial failed Phase 2
  preflight, bounded diagnostics, prospective amendments, corrected clean run,
  origin clarification, and result review are preserved.
- **Current:** synchronize the approved `reproduced` state and prepare the
  scoped Version 0.5.3 public release.
- **Proposed next:** merge the reviewed implementation and publish the release,
  subject to repository checks and authenticated GitHub access.

The intended implementation identifier is `gubser-rocha-emd`. The target is
the homogeneous five-dimensional charged dilatonic black brane of Gubser and
Rocha. The five-dimensional theory is a consistent truncation of maximal
gauged supergravity and the solution has a type IIB lift. It is therefore a
top-down-derived classical EMD reference, retained because its exact background
and thermodynamics provide a strong control for the coupled spectral solver.
It is not the phenomenological finite-density EMD model used in the owner's
unpublished research, and no private Mathematica program is required or
authorized for this contract.

## Primary public source

Steven S. Gubser and Fabio D. Rocha, "Peculiar properties of a charged
dilatonic black hole in AdS_5," *Physical Review D* **81**, 046001 (2010),
[arXiv:0911.2898v2](https://arxiv.org/abs/0911.2898v2),
[doi:10.1103/PhysRevD.81.046001](https://doi.org/10.1103/PhysRevD.81.046001).

The proposed benchmark uses only source Eqs. (1)--(6): the five-dimensional
action, analytic equal-charge background, thermodynamic densities,
microcanonical equation of state, thermodynamic derivatives, and the
low-temperature linear-entropy relation. The public v2 artifacts inspected for
this contract have SHA-256 digests

```text
PDF:            7a6fadd4c420caaa443fb6b47c770436638bfb95ecf55b1bb1232c80421f7e97
source archive: 4b024dab3abe6d2b4f3f58830e246771a1e6934690c9b7b582ae9e4e496cbe66
```

No source archive, source PDF, or source figure will be committed. The paper's
only figure concerns a fermion normal mode and is outside this background
benchmark.

This figure boundary is structural, not merely a plotting choice. The current
program solves only the bosonic fields `A`, `f`, `phi`, and `Phi`; it contains
no charged Dirac field, fermion boundary conditions, or normal-mode search.
Consequently it cannot reproduce source Figure 1 without a separately reviewed
extension covering source Eqs. (8)--(20). Agreement with Eqs. (1)--(6) does not
validate that omitted sector.

## Claim and review state before implementation (historical)

| Item | Support level | Review state |
| --- | --- | --- |
| Source action, analytic background, and Eqs. (3)--(6) | `established-source` | `unreviewed` in HoloForge |
| Canonical-scalar conversion and conformal-gauge equations below | direct derivation from source Eq. (1) | AI-assisted, awaiting owner review |
| Future Chebyshev agreement with the analytic family | not yet supported | closed until every gate passes and the owner reviews the result |
| Fermi-liquid interpretation or thermodynamic stability | not a benchmark result | closed |

Human review may change the review state but must not erase AI provenance or
raise the support level beyond the evidence.

## Physical conventions

Use five bulk dimensions, signature `(-,+,+,+,+)`, and the source normalization

```text
S = 1/(2 kappa_5^2) integral d^5x sqrt(-g)
    [R - 1/2 (partial phi)^2 - 1/4 Z(phi) F^2 - V(phi)],

phi = 2 sqrt(6) alpha,
Z(phi) = exp(sqrt(2/3) phi),
V(phi) = -[8 exp(phi/sqrt(6)) + 4 exp(-2 phi/sqrt(6))]/L^2.
```

Thus `V(0) = -12/L^2`, `V'(0) = 0`, and the canonical scalar saturates the
AdS5 Breitenlohner--Freedman bound, `m^2 L^2 = V''(0)L^2 = -4`. The source
solution has no logarithmic scalar source; its `z^2` coefficient is a response.

The source uses `mu` for a black-hole mass parameter and `Omega` for the
chemical potential. HoloForge must call the former `mu_bh`; it must never call
both quantities `mu` in one record.

## Source analytic family

In the source radial coordinate `r`, with `A_t = Phi(r) dt`,

```text
ds^2 = exp(2A) [-h dt^2 + d x_vec^2] + exp(2B) dr^2/h,

A = log(r/L) + (1/3) log(1 + Q^2/r^2),
B = -log(r/L) - (2/3) log(1 + Q^2/r^2),
h = 1 - mu_bh L^2/(r^2 + Q^2)^2,
Phi = Q sqrt(2 mu_bh)/(r^2 + Q^2)
      - Q sqrt(2 mu_bh)/(r_H^2 + Q^2),
alpha = (1/6) log(1 + Q^2/r^2),
mu_bh L^2 = (r_H^2 + Q^2)^2.
```

The gauge is regular at the horizon, `Phi(r_H) = 0`. With the source sign,
`Omega = -Phi(infinity)/L = sqrt(2)Q/L^2`.

The benchmark sets `L = r_H = 1` and labels the dimensionless family by

```text
xi = Q/r_H >= 0,
theta = arctan(xi),
z_H = theta/xi, with z_H = 1 at xi = 0.
```

This fixes only a conformal scale. Every reported physical comparison uses
dimensionless ratios or the source's hatted densities.

## Conformal gauge and equations to be solved

Define

```text
z = (L^2/Q) arctan(Q/r),
ds^2 = exp(2A(z)) [-f(z) dt^2 + d x_vec^2 + dz^2/f(z)],
A_t = Phi(z) dt,
u = z/z_H in [0,1].
```

Primes in this section mean `d/dz`. The proposed primary solver enforces

```text
A'' - (A')^2 + (phi')^2/6 = 0,

f'' + 3 A' f' - exp(-2A) Z (Phi')^2 = 0,

Phi'' + [A' + (Z_phi/Z) phi'] Phi' = 0,

f phi'' + (3 A' f + f') phi'
  - exp(2A) V_phi
  + (1/2) exp(-2A) Z_phi (Phi')^2 = 0.
```

The following Einstein constraint is not used to replace one of those four
equations; it is an independent acceptance diagnostic:

```text
6 A' f' + f [24 (A')^2 - (phi')^2]
  + 2 exp(2A) V + exp(-2A) Z (Phi')^2 = 0.
```

The Maxwell flux

```text
J = -exp(A) Z Phi'
```

is radially constant. Its orientation-dependent sign is retained, while the
source positive density is extracted as `hat_rho = abs(J)/(8 pi^2)` in the
`L = r_H = 1` convention.

## Exact conformal-gauge reference

For `theta = arctan(xi)` and `L = r_H = 1`, the exact source solution becomes

```text
A = -log(z) + log[theta u cos(theta u)^(1/3)/sin(theta u)],
f = 1 - [sin(theta u)/sin(theta)]^4,
phi = -sqrt(8/3) log[cos(theta u)],
Phi = sqrt(2) xi {sin(theta u)^2/sin(theta)^2 - 1}.
```

All expressions use their continuous `xi -> 0` limits. At `xi = 0`, they
reduce to the neutral AdS5--Schwarzschild solution

```text
A = -log(z),  f = 1-u^4,  phi = 0,  Phi = 0.
```

These closed forms are acceptance references, not charged initial guesses.

## Boundary conditions and UV factorization

The spectral unknowns must be analytic functions on the exact endpoint domain
and use

```text
A(z) = -log(z/L) + u^4 a(u),
f(u) = 1 - u^4 b(u),
phi(u) = u^2 p(u),
Phi(u) = -L Omega + u^2 v(u).
```

This factorization fixes the boundary metric and time normalization, removes
the scalar logarithmic source, and fixes the grand-canonical gauge source.
The exact horizon conditions are

```text
b(1) = 1,  v(1) = L Omega,
```

so `f(1) = 0` and `Phi(1) = 0`. The undivided scalar equation is retained at
the horizon and must supply the regularity relation. No UV or horizon cutoff,
fitted horizon datum, or post-hoc boundary adjustment is allowed.

Each case is a fixed-source Dirichlet problem. The source paper presents the
equation of state microcanonically; the benchmark reports both the fixed
boundary source and the corresponding hatted densities without conflating the
two ensembles.

## Frozen source cases and deterministic spectral route

The reported cases are

```text
xi = 0, 0.5, 1, 2, 4, 8, 16.
```

The primary route uses the shared Chebyshev--Gauss--Lobatto grid and
polynomial degrees `N = 40, 60, 80`. The degree-80 branch is the reported
solution; all three aligned degrees supply convergence evidence.

Start from the analytic neutral solution only. Continue deterministically
through

```text
xi = 0, 0.25, 0.5, 0.75, 1, 1.5, 2, 3, 4, 6, 8, 12, 16.
```

Intermediate cases are initialization points, not reportable evidence. At
each `xi`, solve degree `40 -> 60 -> 80`, interpolating only the converged
current-case lower degree to seed the next degree. Use

```text
scipy.optimize.root(method="hybr", xtol=1e-11)
```

and, only if it reports failure or its scaled residual exceeds `1e-9`, the
owner-approved thirty-two-evaluation TRF residual polish. Record both states
and all evaluation counts. No random restart, best-of-seed selection, shooting
fallback, or copied private implementation is authorized.

## Thermodynamic targets from source Eqs. (3)--(6)

For `L = r_H = 1`, the exact source quantities are

```text
mu_bh = (1 + xi^2)^2,
hat_epsilon = 3 mu_bh/(8 pi^2),
hat_s = (1 + xi^2)/(2 pi),
hat_rho = sqrt(2) xi (1 + xi^2)/(4 pi^2),
T = 1/pi,
Omega = sqrt(2) xi.
```

The numerical extraction rules are

```text
T = abs(f'(z_H))/(4 pi),
Omega = -Phi(0),
hat_s = exp(3 A(z_H))/(2 pi),
mu_bh = -lim[z->0] (f-1)/z^4,
hat_epsilon = 3 mu_bh/(8 pi^2),
hat_rho = abs(J)/(8 pi^2).
```

These extraction formulas are applied only after the benchmark scale choice
`L = r_H = 1`; the contract does not assert a general-`L` dimensional
continuation of them.

The microcanonical equation of state is

```text
hat_epsilon = 3/[2^(5/3) pi^(2/3)]
              * (hat_s^2 + 2 pi^2 hat_rho^2)^(2/3).
```

The horizon `T` and boundary `Omega` must agree with derivatives of this
equation of state at fixed `hat_rho` and fixed `hat_s`, respectively.

To reproduce the source low-temperature statement without pretending that a
finite point is the extremal limit, use `xi = 4, 8, 16` and test

```text
4 hat_s/(Omega^2 T) = 1 + 1/xi^2.
```

A preregistered linear fit against `1/xi^2` must have intercept and slope equal
to one within their proposed gates. The intercept is the source relation
`hat_s ~ Omega^2 T/4`. This is a property of the homogeneous equal-charge
solution, not evidence for a stable Fermi liquid.

## Proposed public outputs

After contract approval, and only after implementation passes its gates, the
bounded artifact list is:

- `src/holoforge/benchmarks/gubser_rocha_emd.py` and one registry adapter;
- one model card under `domains/` and one concise benchmark guide;
- analytic, equation, convergence, thermodynamic, CLI, schema, bundle, and
  expected-failure tests;
- a JSON verification record and CSV containing only the seven frozen cases;
- one HoloForge-generated plot comparing spectral and exact fields and showing
  the Eq. (6) low-temperature extrapolation.

The plot is a HoloForge-generated verification visualization, not a
reproduction of source Figure 1. No fermion wavefunction or source figure is in
scope.

## Current acceptance gates

The original thresholds were preregistered before implementation. Two
prospective amendments below were authorized only after the initial failed
preflight and bounded diagnostics were preserved. A third prospective
portability amendment was authorized after the release-candidate CI evidence
was preserved. No other gate changed.

1. **Source algebra:** canonical conversion, `V(0)`, `V'(0)`, `m^2L^2`,
   `Z(0)`, coordinate transformation, and exact solution identities agree
   symbolically or numerically within `1e-12`.
2. **Nonlinear solve:** every final reported and continuation solve reports
   success with scaled collocation residual at most `3e-9`. The root-first
   route still invokes TRF polishing whenever the root fails or its scaled
   residual exceeds the unchanged `1e-9` polish trigger.
3. **Independent equations:** the four uncross-multiplied physical equations
   evaluated barycentrically on a grid at least twice as dense have individual
   scaled infinity norms at most `1e-7`, including both exact endpoints.
4. **Einstein constraint:** the independently evaluated constraint has scaled
   infinity norm at most `1e-7` for every reported case.
5. **Boundary and source conditions:** all factored UV limits, the absence of a
   scalar logarithmic source, `f(0)=1`, `f(1)=0`, `Phi(1)=0`, and horizon scalar
   regularity have scaled residual at most `1e-8`.
6. **Maxwell flux:** the maximum radial drift of `J`, normalized by
   `max(1,abs(J))`, is at most `1e-8`.
7. **Exact fields:** at all seven reported cases, the maximum scaled difference
   between spectral and source-exact `A`, `f`, `phi`, and `Phi` on the
   independent grid is at most `2e-7`.
8. **Spectral refinement:** the maximum relative change in every thermodynamic
   observable from `N=60` to `N=80` is at most `2e-6` and improves over
   `N=40` to `N=60` whenever the earlier change exceeds a `5e-10` numerical
   floor.
9. **Source thermodynamics:** every quantity in source Eq. (3) and the exact
   `T` and `Omega` values agree within `2e-7` relative error.
10. **Equation of state:** source Eq. (4) and both Eq. (5) derivatives agree
    within `2e-7` relative error.
11. **Low-temperature relation:** at `xi = 4, 8, 16`, the finite-`xi` identity
    above agrees within `2e-6`; the fit intercept and slope each agree with one
    within `2e-5`.
12. **Neutral limit and determinism:** `xi=0` reproduces AdS--Schwarzschild
    within `1e-10`; two complete runs agree in physical observables within
    `1e-12`, scaled by the maximum of one and both magnitudes.
13. **Interfaces and regressions:** strict JSON, human CLI, evidence bundle,
    model-card schema, artifact overwrite protection, installed-wheel smoke
    test, the full public suite, and every existing default verifier pass.

If a threshold is numerically unrealistic, the implementation stops and
returns with measured evidence before any threshold revision. A missed gate is
not hidden by exact visual agreement.

## Owner-approved diagnostic amendment, 2026-08-19

The initial `N = 40, 60, 80` preflight remains preserved as a failed result.
It stopped at the nonlinear-library-status gate and three refinement-ordering
comparisons at `xi = 16`. The owner then authorized exactly two diagnostics:

1. rerun only the five affected `N = 40` TRF polishes with a larger evaluation
   allowance; and
2. add one non-reporting `N = 100` solve at `xi = 16`.

All five TRF calls reported SciPy success after `13`--`18` evaluations. Relative
to the twelve-evaluation states, their largest field change was `4.17e-13` and
their largest thermodynamic change was `7.90e-14`. The `N = 100` root reported
success with scaled residual `3.49e-10`. The disputed `mu_bh`, energy-density,
and charge-density changes decreased to `5.22e-11`, `5.22e-11`, and `5.50e-11`,
respectively.

The owner selected Option A at the diagnostic gate and prospectively approved:

- a TRF polish cap of `32`, retaining the root-first route, tolerances,
  library-success rule, residual rule, continuation, and seeds;
- a refinement ordering floor of `5e-10`, retaining the `2e-6` final-change
  tolerance and all three spectral degrees; and
- one complete clean rerun followed by a new result owner gate.

The rounded refinement floor covers the frozen `N = 80` maximum exact-
thermodynamic error `4.80e-10` while remaining 4000 times below the unchanged
final-change tolerance. This is a documented prospective amendment, not a
retroactive pass. Result acceptance, model-card promotion, commit, push, merge,
release, private-code transfer, and every broader physical interpretation stay
closed.

## Owner-approved origin and figure clarification, 2026-08-19

Before accepting the passing amended result, the owner identified that the
source background is top-down-derived rather than bottom-up and that the result
packet did not use HoloForge's standard LaTeX style. The owner approved the
following bounded correction without changing the solver or numerical result:

- retain the implementation and passing preflight as a top-down-derived
  numerical control;
- remove wording that counts it among representative bottom-up examples;
- state that the current bosonic program reproduces source Eqs. (2)--(6), not
  the paper's charged-fermion Figure 1;
- rebuild the result packet from `docs/templates/review-packet-template.tex`;
  and
- require future classical bottom-up benchmark contracts to reproduce at least
  one central source figure or table when feasible, or record an owner-reviewed
  reason and an alternative quantitative literature check.

This clarification does not authorize the fermion extension, result
acceptance, support promotion, commit, push, pull request, merge, tag, or
release.

## Owner-approved result and release decision, 2026-08-19

After reviewing the corrected standard seven-page result packet, the owner
selected Option A and approved all five result decisions:

1. classify the benchmark as a top-down-derived numerical control rather than
   a representative bottom-up example;
2. accept the explicit boundary that the program reproduces the bosonic
   background and source Eqs. (2)--(6), not source Figure 1;
3. accept all thirteen numerical gates as a HoloForge reproduction of the
   bounded bosonic claim, not empirical validation;
4. promote the numerical claim and model-card provenance to owner-approved
   `reproduced`; and
5. authorize a scoped local commit, push, pull request, merge, and a release if
   required by repository policy.

The owner additionally authorized push, merge, and release. Version 0.5.3 is
the appropriate backward-compatible patch because the public branch already
contains unreleased spectral-foundation and Einstein--dilaton work and this
benchmark adds another opt-in verifier without changing existing commands,
schemas, defaults, or scientific meanings.

The charged-fermion extension, source Figure 1, stability claims, empirical
interpretation, private-code transfer, and unpublished research remain closed.

## Owner-approved release-candidate portability amendment, 2026-08-19

PR #23 then exercised the installed verifier on Ubuntu 24.04. The Python 3.11
wheel job used NumPy 2.4.6 and SciPy 1.17.1 and measured a maximum final scaled
collocation residual of `1.960378e-9`, so the frozen `1e-9` final-acceptance
ceiling stopped the release. The same dependency versions on macOS measured
`9.579273e-10`. The Python 3.9, 3.11, and 3.14 Ubuntu test jobs all stopped at
the same nonlinear-state and collocation gates, while all three wheel-
relocation portability jobs passed.

The Ubuntu wheel run retained passing independent evidence: the maximum
twice-oversampled four-equation residual was `1.237393e-8`, the Einstein
constraint residual was `6.881107e-12`, the boundary/source residual was
`1.175903e-10`, the normalized Maxwell-flux drift was `1.342367e-11`, and the
exact-field difference was `6.275377e-10`. The refinement, source
thermodynamics, equation of state, low-temperature, and neutral/determinism
gates also passed. Additional TRF iterations did not materially lower the
high-degree double-precision residual floor in the matching macOS environment.

After this failed CI evidence was reported, the owner selected Option A and
prospectively approved only the following portability amendment:

- increase the **final scaled collocation acceptance ceiling** from `1e-9` to
  `3e-9`; and
- retain the `1e-9` TRF-polish trigger, the 32-evaluation cap, solver route,
  equations, continuation, spectral degrees, independent gates, physical
  claim, and all non-inference boundaries unchanged.

The `3e-9` ceiling covers the measured Ubuntu state without converting an
unpolished root into an accepted route: roots above `1e-9` still receive TRF
polishing and must report maintained-library success. This is a documented
prospective amendment, not a retroactive claim that the original CI run
passed. Merge, tag, and release remain conditional on a clean amended run.

## Evidence boundary and important limitations

With all gates passing and the result owner-approved, HoloForge may claim only
that its coupled Chebyshev implementation reproduces the selected analytic
background and Eqs. (3)--(6) inside the cited top-down-derived classical EMD
model. This control result must not be listed as a representative bottom-up
example.

It must not claim:

- empirical validation of a Fermi liquid, QCD, or any material;
- stability of the low-temperature equal-charge branch;
- reproduction of the fermion normal mode, source Figure 1, the ten-dimensional
  lift, the `AdS_3` mechanism, unequal-charge STU dynamics, or Section 6 scaling
  solutions;
- reproduction of source Eq. (7) or either specific heat;
- equivalence to the owner's phenomenological EMD research model;
- a new physical prediction, a fitted parameter, or a top-down result beyond
  what the source establishes.

The source itself shows that the symmetric branch becomes unstable to an
unequal-charge mode on the low-temperature side. With the present variables,
the source threshold is `xi = 1`; therefore the `xi > 1` cases are retained
only as analytic verification points. Passing them must never be described as
stability or physical phase selection.

## Hard stops

Return to owner review before implementation continues if:

- the BF-bound logarithmic source cannot be separated unambiguously;
- the exact-endpoint horizon equation becomes non-diagnostic;
- continuation selects more than one smooth branch;
- any new coordinate map, domain decomposition, regularization, solver,
  restart policy, shooting fallback, or threshold change appears necessary;
- source conventions, charge normalization, ensemble, or thermodynamic
  extraction remain ambiguous;
- any acceptance gate misses;
- implementation would require a private path, notebook, code fragment,
  unpublished datum, or confidential identifier; or
- an existing benchmark default or protected compatibility contract would
  change.

## Hostile critic before implementation

**"The exact solution makes the benchmark trivial."** The analytic family
does make the target unusually checkable, but the proposed primary task is a
fully coupled nonlinear EMD boundary-value solve. Exact fields, flux, the
constraint, and thermodynamics prevent a solver from passing merely because a
plot looks right.

**"The low-temperature points are thermodynamically unstable."** Correct in
the larger unequal-charge STU theory. They are retained only to verify the
source's homogeneous equal-charge solution and Eq. (6); the contract forbids
calling them stable equilibrium states or Fermi-liquid evidence.

**"Feeding source boundary data predetermines the answer."** The benchmark is
a verification target, not a parameter fit. Fixed boundary sources identify
the exact member of the analytic family; the interior fields, conserved flux,
constraint, and extracted densities must still be recovered independently by
the nonlinear spectral solve.

**"A shooting comparison is missing."** The closed-form source solution is a
stronger independent reference for this first EMD benchmark. Shooting is not
needed to establish the declared claim and remains closed unless a later owner
decision adds a distinct purpose.

## Owner decisions requested (historical pre-implementation gate)

The following C1--C5 menu is retained as the original contract record. It is
superseded by the later result and release decision recorded above.

### C1 -- source and physical conventions

**Recommendation: approve.** Use source Eqs. (1)--(6), the canonical scalar
`phi = 2 sqrt(6) alpha`, the source gauge sign, and the distinct names
`mu_bh` and `Omega`.

- **Reason:** these conventions reproduce the public v2 source without a
  normalization collision.
- **Opens:** only the five-dimensional homogeneous EMD background and its
  thermodynamics.
- **Remains closed:** fermions, unequal charges, the ten-dimensional lift,
  Section 6 models, QCD, and private EMD work.
- **Uncertainty:** the owner should check the canonical conversion and charge
  sign before code begins.

### C2 -- conformal gauge, boundary data, and source cases

**Recommendation: approve.** Use the exact-endpoint conformal interval, the
four UV factorizations, `L = r_H = 1`, and the seven frozen `xi` cases.

- **Reason:** this shares the Phase 0 spectral primitive, exposes the BF-bound
  source condition, and includes neutral, moderate-charge, and controlled
  low-temperature checks.
- **Opens:** the stated fixed-source BVP only.
- **Remains closed:** cutoffs, fitted horizon data, alternate maps, and
  interpreting `xi > 1` as stable phases.
- **Uncertainty:** the smooth no-log factorization is the main endpoint risk.

### C3 -- numerical route

**Recommendation: approve.** Use deterministic `N = 40, 60, 80` Chebyshev
continuation with the frozen maintained-library nonlinear solve and no shooting
fallback.

- **Reason:** the source exact family already supplies the strongest
  independent reference, while the selected route matches the user's spectral
  research practice.
- **Opens:** local coupled spectral implementation and declared diagnostics.
- **Remains closed:** random restarts, best-of-seed selection, custom numerical
  primitives, private Mathematica copying, and post-result solver changes.
- **Uncertainty:** `xi = 16` may expose conditioning from the nearby extremal
  singular limit; that is a stop, not permission to redesign silently.

### C4 -- targets, gates, and evidence boundary

**Recommendation: approve.** Reproduce source Eqs. (2)--(6), use the thirteen
preregistered gates, and state the instability limitation next to every
low-temperature result.

- **Reason:** exact fields plus equation, constraint, flux, refinement, EOS,
  and interface gates provide fast and difficult-to-fake validity checks.
- **Opens:** only a future `reproduced` claim after all gates and owner review.
- **Remains closed:** source Figure 1, fermion physics, stability, empirical
  validation, and broader model claims.
- **Uncertainty:** proposed numerical thresholds have not yet been measured by
  an implementation and may trigger a documented return.

### C5 -- implementation authorization

**Recommendation: approve only after C1--C4 are accepted.** Authorize a bounded
local implementation and preflight run, followed by a new owner gate.

- **Reason:** the contract is specific enough to make implementation auditable.
- **Opens:** the proposed local files and validation commands only.
- **Remains closed:** accepting a result or model card, commit, push, pull
  request, merge, tag, release, iHQCD, and transfer of private material.
- **Uncertainty:** any new source, endpoint, conditioning, or branch problem
  returns before production evidence is interpreted.

## Owner response paths (historical pre-implementation gate)

- **A -- approve all recommendations:** approve C1--C5 and authorize only the
  bounded local implementation and preflight described above.
- **B -- approve selected items:** name the approved decisions; all others stay
  closed.
- **C -- request revision or more evidence:** identify the equation,
  convention, case, gate, or limitation to revise before implementation.
- **D -- status walkthrough only:** discuss the packet; make no implementation
  change.
- **E -- custom response:** state a different bounded instruction.

**Recommended path: A.** It advances Phase 2 to a local spectral preflight
while preserving a mandatory stop before result acceptance or any Git/public
action.
