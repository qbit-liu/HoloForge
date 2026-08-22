# DeWolfe--Gubser--Rosen EMD Phase 5 contract

## Status and authorization boundary

This document began as the prospective owner-review contract for **Phase 5A**
of the classical benchmark sequence and now records its implementation,
accepted result, and integration decisions. It is public-source
**Forge/Verify** work based
on the phenomenological bottom-up Einstein--Maxwell--dilaton (EMD) model of
DeWolfe, Gubser, and Rosen (DGR).

- **Completed:** Phases 0--4 are released; Phase 4 closed in Version 0.5.5.
- **Completed:** the owner approved Decisions C1--C6 on 2026-08-22 with the
  amended Phase 5B boundary recorded below; the bounded local implementation
  and all fourteen preflight gates are complete.
- **Completed:** the owner selected Option A and approved R1--R3 on 2026-08-22,
  accepting the bounded numerical result, model card, review artifacts, and
  scoped Git integration.
- **Current:** integration and release validation. Phase 5B remains closed.
- **Proposed next:** close Phase 5A after green remote CI and release, then
  return before freezing any Phase 5B contract.

The passing DGR numerical result and model card are owner-approved as
`reproduced` on 2026-08-22. This opens only the scoped Phase 5A Git integration
and release workflow. It does not authorize private-research transfer, Phase
5B, Phase 5C, or any empirical-QCD claim.

## Recommendation

Add one separate `dewolfe-gubser-rosen-emd` benchmark in three owner-gated
stages:

1. **Phase 5A -- zero-density calibration:** reproduce both DGR black-hole
   curves in source Figure 3, namely `s/T^3` and `chi_2/T^2` at `mu = 0`.
   Use a neutral Chebyshev background scan and the source linear-response
   susceptibility integral. This contract covers only Phase 5A.
2. **Phase 5B -- finite-density phase structure:** only after Phase 5A closes,
   freeze a separate two-parameter charged-background contract for source
   Figure 5 and the reported model critical point. Figure 4 may inform grid
   coverage and branch-topology diagnostics, but reproducing its full panel is
   not required.
3. **Phase 5C -- critical scaling:** only after Phase 5B closes, freeze selected
   critical-exponent fits with preregistered fit windows and uncertainty
   analysis.

Figure 5 is mandatory in Phase 5B because its single-valued,
multi-valued, and infinite-slope isotherms provide the quickest physical check
of the finite-density branch structure. It must not be pulled into Phase 5A:
doing so would mix a one-parameter neutral calibration with a two-parameter
charged scan before the neutral solver and dictionary are verified.

## Primary public source and provenance

Oliver DeWolfe, Steven S. Gubser, and Christopher Rosen, "A holographic
critical point," *Physical Review D* **83**, 086005 (2011),
[arXiv:1012.1864v2](https://arxiv.org/abs/1012.1864),
[doi:10.1103/PhysRevD.83.086005](https://doi.org/10.1103/PhysRevD.83.086005).

The official public arXiv artifacts inspected for this contract have SHA-256
digests

```text
PDF:                    ed6f00b759dbf3347521b6321d2c69c8c2e629f45ff7ab3dd6a9e6a6afc7040c
source archive:         3f921d2212cb5f7956c1da7cbb0904c02ff32e302d514ab2e80b4bfc64b6778e
Figure 3 source PDF:    bf1dfec799335ca3b8db124a188a4c7d17e1a3f73ddf31f2606f58fa7492f65b
Figure 4 source PDF:    6ba10f000cd9d34ca92acb23afb4ac08fd90b1241cdbd37234c4f5eba479b0d2
Figure 5 source PDFs:   c6a56d588ee5491c2e06359d3d718b8fd21a24ebcf4f888b796a0a6db87d0719
                        5282e9a4174fd124a18a6aa53861182277b7c46024e8b6e301c39839942ed8a3
                        5519dfc2f0abfa1f721f28432a7b748e73c15d532104e21c14d32b5395814064
```

Phase 5A uses source Eqs. (1)--(5), (27)--(29), (31)--(41), (44)--(45), and
(49)--(64), together with Figure 3 and the accompanying numerical-strategy
text. The public TeX and Mathematica-generated vector PDF were inspected
directly. The source PDF, archive, figure artwork, and third-party lattice
points are audit inputs only and must not be committed or redistributed.

## Support, review, and data boundary

| Item | Support level | Review state |
| --- | --- | --- |
| Source action, potentials, equations, dictionary, and scale choices | `established-source` | owner-approved contract, 2026-08-22 |
| Conformal-gauge transformation and factorization below | direct derivation from the source equations | owner-approved contract; AI-assisted |
| Derived Figure 3 black-hole curve anchors | derived public-source record | owner-approved contract; AI-extracted |
| HoloForge Figure 3 calculation | `reproduced` | owner-approved, 2026-08-22 |
| Critical point or exponents | source claims only; not a Phase 5A result | closed |

The Figure 3 lattice symbols come from a separate cited lattice source. They
may be described for provenance, but they are not HoloForge reference data and
must not appear in a committed reproduction plot unless a later license and
provenance review explicitly opens them. Phase 5A compares only the two blue
black-hole paths derived from the DGR public vector figure.

## Phase boundary and model identity

DGR is a phenomenological bottom-up EMD model. The authors state that the
chosen functions are not known to arise from a precise string construction and
that the dual should only be regarded as a QCD-like large-`N` gauge theory.
This differs from the already released Gubser--Rocha Phase 2 benchmark, which
is a top-down-derived exact control retained to test coupled EMD numerics.

The DGR model is also distinct from the owner's unpublished phenomenological
EMD programs. Phase 5 must be implemented from the public source and the
maintained public HoloForge numerical primitives. The temporary Mathematica
programs are neither needed nor authorized for copying or public transfer.

## Action, ansatz, and source functions

Use five bulk dimensions, mostly-plus signature, and the source normalization

```text
S = 1/(2 kappa_5^2) integral d^5x sqrt(-g) [
      R - 1/2 (partial phi)^2 - 1/4 f_EMD(phi) F_ab F^ab - V(phi)
    ].
```

The source radial ansatz is

```text
ds^2 = exp(2 A(r)) [-h(r) dt^2 + d x_vec^2]
     + exp(2 B(r)) dr^2/h(r),
phi = phi(r),
A_a dx^a = Phi(r) dt.
```

Freeze the DGR functions exactly as

```text
V(phi) = [-12 cosh(gamma phi) + b phi^2]/L^2,
gamma = 0.606,
b = 2.057,

f_EMD(phi) = sech[(6/5)(phi - 2)] / sech(12/5).
```

The subscript on `f_EMD` prevents collision with a blackening function named
`f` in conformal gauge. The ultraviolet mass and dimensions are

```text
m_phi^2 L^2 = -12 gamma^2 + 2 b = -0.292832,
Delta_phi = 2 + sqrt(4 + m_phi^2 L^2) = 3.925400737508948,
nu = 4 - Delta_phi = 0.0745992624910521.
```

The other admissible root is not used. `L = kappa_5 = 1` is the source's
dimensionless black-hole convention before the declared phenomenological
rescalings.

## Source equations and conserved quantities

In the general radial gauge, primes mean `d/dr`. The source equations are

```text
A'' - A' B' + phi'^2/6 = 0,

h'' + (4 A' - B') h' - exp(-2 A) f_EMD Phi'^2 = 0,

Phi'' + (2 A' - B') Phi'
     + (d log f_EMD/dphi) phi' Phi' = 0,

phi'' + (4 A' - B' + h'/h) phi'
      - exp(2 B)/h dV_eff/dphi = 0,

V_eff = V - 1/2 exp(-2 A - 2 B) f_EMD Phi'^2.
```

The independent zero-energy constraint is

```text
h (24 A'^2 - phi'^2) + 6 A' h'
+ 2 exp(2 B) V + exp(-2 A) f_EMD Phi'^2 = 0.
```

The two source charges are

```text
Q_G = f_EMD exp(2 A - B) Phi',
Q_N = exp(2 A - B) [exp(2 A) h' - f_EMD Phi Phi'].
```

Both must be radially constant when applicable. In Phase 5A, `Phi = 0`,
`Q_G = 0`, `mu = rho = 0`, and the neutral background is independent of
`f_EMD`. The gauge kinetic function enters only the linear-response
susceptibility integral.

## Primary conformal-gauge boundary-value problem

Use

```text
ds^2 = exp(2 A(z)) [-h(z) dt^2 + d x_vec^2 + dz^2/h(z)].
```

At `mu = 0`, the primary spectral equations are

```text
A'' - A'^2 + phi'^2/6 = 0,
h'' + 3 A' h' = 0,
h phi'' + (3 A' h + h') phi' - exp(2 A) V_phi = 0.
```

The independent Einstein constraint is

```text
6 A' h' + h (24 A'^2 - phi'^2) + 2 exp(2 A) V = 0.
```

The conformal boundary is `z = 0`; the regular horizon is `z = z_H`.
Normalize the boundary metric by `h(0) = 1`, require the simple horizon
`h(z_H) = 0`, retain the undivided scalar equation at the horizon, and require
finite `A + log(z/L)` and `phi` there. No fitted horizon condition or endpoint
cutoff is permitted.

Because `nu` is small, use the already verified Phase 1 analytic
factorization

```text
x = (z/L)^nu,
u = x/x_H in [0, 1],
A(z) = -log(z/L) + x^2 C(u),
phi(z) = x P(u),
h(z) = H(u),

H(0) = 1,
H(1) = 0,
P(0) = 1.
```

The unit leading coefficient of `phi` fixes the common UV deformation scale.
The horizon value is the derived quantity `phi_0 = x_H P(1)`. Source Figure 3
uses 20 `phi_0` values uniformly spaced in `log(phi_0)` from `1.5` to `7.5`.
The implementation must locate those physical horizon targets by a
deterministic bracketed inversion of the continued `x_H -> phi_0` map; it must
not identify `x_H` with `phi_0`.

## Thermodynamics and zero-density susceptibility

For the source-normalized conformal solution,

```text
T_BH = abs(h'(z_H))/(4 pi),
s_BH = 2 pi exp(3 A(z_H))/kappa_5^2.
```

Define the positive linear-response integral

```text
I = integral_0^z_H dz exp[-A(z)] / f_EMD(phi(z)).
```

The Maxwell equation implies `Phi'` is proportional to
`exp(-A)/f_EMD`. With the source normalization of charge density,

```text
chi_2,BH = 1/(2 kappa_5^2 I),
chi_hat_2,BH = chi_2,BH/T_BH^2.
```

This is the conformal-gauge form of source Eqs. (53)--(57). It must be checked
against an explicit infinitesimal Maxwell solution on selected fixed neutral
backgrounds; it must not be treated as a fitted formula.

The DGR Figure 3 presentation uses the source calibration constants

```text
lambda_s = (121 MeV)^3,
lambda_T = 252 MeV,
lambda_mu = 972 MeV,
lambda_rho = (77 MeV)^3,

lambda_T lambda_s = lambda_mu lambda_rho
  (defining relation before the displayed values are rounded).
```

They are `established-source` inputs, not quantities predicted or refitted by
Phase 5A. The printed integers differ in the two scale products by a relative
`0.0060468632`; this is recorded as source rounding, not silently forced to
zero. Plot

```text
T_MeV = lambda_T T_BH,
(s/T^3)_plot = (lambda_s/lambda_T^3) (s_BH/T_BH^3),
(chi_2/T^2)_plot
  = [lambda_s/(lambda_T lambda_mu^2)] chi_hat_2,BH.
```

The equality of the two scale products and direct substitution into the
source rescaling equations must be tested. No independent claim about
`T_c`, `lambda_s`, `lambda_T`, `lambda_mu`, or `lambda_rho` follows from
matching Figure 3.

## Frozen Figure 3 target and derived anchors

The source Figure 3 file is a Mathematica-generated vector PDF. The anchors
below were derived from the center lines of its two blue paths. Axis ticks
define affine maps and linear interpolation is used only between adjacent
vector-path vertices. The extraction record and source digest must be stored
with future reference data. The lattice markers are excluded.

With `(x_pdf, y_pdf)` denoting the converted vector coordinates, the audited
tick maps are

```text
left panel:
  T = 200 + 100 (x_pdf - 78.143)/(144.828 - 78.143),
  s/T^3 = 5 (278.847 - y_pdf)/(278.847 - 220.359),

right panel:
  T = 150 + 50 (x_pdf - 531.110)/(595.268 - 531.110),
  chi_2/T^2 = 0.1 (278.893 - y_pdf)/(278.893 - 219.415).
```

Figure 3 left, black-hole `s/T^3` path:

| `T` (MeV) | source path `s/T^3` |
| ---: | ---: |
| 170 | 1.899407 |
| 180 | 4.961648 |
| 190 | 7.883849 |
| 200 | 9.909476 |
| 225 | 12.972585 |
| 250 | 14.642470 |
| 300 | 16.505148 |
| 400 | 18.087696 |
| 550 | 19.098777 |
| 650 | 19.418822 |
| 700 | 19.574478 |

Figure 3 right, black-hole `chi_2/T^2` path:

| `T` (MeV) | source path `chi_2/T^2` |
| ---: | ---: |
| 150 | 0.002001 |
| 170 | 0.022026 |
| 180 | 0.081693 |
| 190 | 0.151201 |
| 200 | 0.203321 |
| 225 | 0.281409 |
| 250 | 0.318216 |
| 300 | 0.346912 |
| 350 | 0.351970 |
| 400 | 0.349351 |
| 450 | 0.344815 |

The prospective comparison ceilings are absolute errors `0.15` for `s/T^3`
and `5e-3` for `chi_2/T^2`. These are deliberately wider than vector
coordinate precision and narrower than the plot line widths at review scale;
they test the published curves without pretending that the paper supplied raw
author data. Any anchor extraction correction requires owner review before a
result is classified.

## Frozen primary and independent numerical routes

The primary route reuses the maintained Phase 0 Chebyshev--Gauss--Lobatto grid
and the accepted Phase 1 neutral coupled-BVP functions where their interfaces
are genuinely model-independent. It must add a separate DGR definition and
must not change Phase 1 potentials, defaults, outputs, schemas, or results.

```text
reported horizon targets:
  phi_0 = exp(linspace(log(1.5), log(7.5), 20))

spectral degrees:
  N = (80, 120, 150), with N = 150 reported

nonlinear solve:
  scipy.optimize.root(method="hybr", xtol=1e-11)
  followed only when triggered by the already documented bounded
  scipy.optimize.least_squares(method="trf") residual polish

quadrature:
  maintained Gauss--Legendre or Clenshaw--Curtis quadrature on the
  analytic spectral representation, with an explicit refinement record
```

Continue deterministically in `log(x_H)` from the lowest accepted horizon.
The initial seed may use the analytic UV factorization and the neighboring
accepted Phase 1 public solution only if the exact public source parameters and
seed provenance are recorded. No private program, random restart,
best-of-seed selection, shooting fallback, or post-result grid edit is allowed.

At the five physical horizons nearest

```text
phi_0 = (1.5, 2.0, 3.0, 5.0, 7.5),
```

use the source scalar-coordinate horizon series and
`scipy.integrate.solve_ivp(method="DOP853", rtol=1e-10, atol=1e-12)` as an
independent background route. Evaluate the susceptibility both from an
independently refined integral and from the explicit linear Maxwell equation.
This changes the discretization and evolution direction; it does not provide
independent physical equations.

## Proposed acceptance gates

All ceilings are prospective. A missed or unrealistic gate causes a recorded
stop; it is not permission to weaken the threshold after seeing a desired
curve.

1. **Source algebra:** `V(0)`, `V'(0)`, `m_phi^2 L^2`, `Delta_phi`, `nu`,
   `f_EMD(0)`, the symbolic scale-product relation, the published-value
   rounding mismatch, and conformal-gauge transformations agree with the
   displayed analytic values to `1e-12`.
2. **Nonlinear solve:** every final reported and continuation solve reports
   maintained-library success with scaled collocation residual at most `1e-8`.
   Any bounded residual polish and its trigger are recorded.
3. **Independent physical equations:** the three uncross-multiplied neutral
   equations on a barycentrically evaluated grid of at least `2N` have
   individual scaled infinity norms at most `1e-6`.
4. **Einstein constraint:** its separately evaluated scaled infinity norm is
   at most `1e-6` at every reported horizon.
5. **Boundary and regularity:** `H(0)=1`, `H(1)=0`, `P(0)=1`, UV warp
   behavior, and the undivided horizon scalar equation have scaled residual at
   most `1e-8`.
6. **Target and branch integrity:** the 20 physical `phi_0` targets are met
   within relative error `1e-9`; the `x_H -> phi_0` map remains one-to-one on
   the declared branch, and no interpolation crosses a turning point.
7. **Spectral refinement:** from `N=120` to `N=150`, the maximum relative
   change in `T_BH`, `s_BH`, `I`, and `chi_hat_2,BH` is at most `2e-4` and
   improves over `N=80` to `N=120` whenever the earlier change exceeds a
   `1e-8` numerical floor.
8. **Quadrature refinement:** doubling the integration order changes `I` and
   `chi_hat_2,BH` by at most `2e-5`; the change improves over the preceding
   refinement above a `1e-10` floor.
9. **Maxwell identity:** the integral formula and explicit infinitesimal
   Maxwell solve agree in `chi_hat_2,BH` within relative error `1e-6` at the
   five named horizons; normalized Maxwell-flux drift is at most `1e-8`.
10. **Independent background route:** Chebyshev and DOP853 `T_BH`, `s_BH`,
    `I`, and `chi_hat_2,BH` agree within relative error `5e-4` at the five
    named horizons.
11. **Figure 3 entropy:** the maximum absolute `s/T^3` discrepancy at the 11
    frozen black-hole anchors is at most `0.15`.
12. **Figure 3 susceptibility:** the maximum absolute `chi_2/T^2` discrepancy
    at the 11 frozen black-hole anchors is at most `5e-3`.
13. **Determinism and interfaces:** two complete verifier runs agree in every
    reported physical observable to `1e-12`, scaled by
    `max(1, abs(a), abs(b))`; strict JSON, human CLI, evidence bundle,
    overwrite protection, and installed-wheel behavior pass.
14. **Regression and privacy:** all pre-existing tests and default verifiers
    pass unchanged; the public-content and release-policy scans find no private
    path, unpublished identifier, secret, source artwork, or temporary
    Mathematica dependency.

The `1e-6` independent differential-equation and constraint ceilings are
conditioned physics diagnostics, not relaxed figure-fit tolerances. They match
the accuracy scale previously judged appropriate for independently evaluated
spectral second derivatives. Boundary, flux, refinement, independent-route,
and source-curve gates prevent a visually plausible but invalid solution from
passing.

## Implemented reproduction interface and artifacts

The owner-approved reproduction implements:

```text
holoforge verify dewolfe-gubser-rosen-emd
holoforge verify dewolfe-gubser-rosen-emd --json
holoforge verify dewolfe-gubser-rosen-emd --output-dir OUTPUT_DIR
```

The evidence record includes the source identifiers and digests,
all conventions and scales, potential and gauge function, spectral degrees,
physical horizon targets, nonlinear diagnostics, independent equation and
constraint residuals, quadrature and degree refinement, DOP853 and Maxwell
comparisons, both anchor tables, branch labels, limitations, support/review
state, runtime versions, and deterministic artifact hashes.

The generated plot may show only HoloForge curves and the derived DGR
black-hole anchors. It must label both panels as a model reproduction, not as
new lattice agreement. Figure 5, finite-density data, critical-point values,
and exponent fits are forbidden from Phase 5A artifacts.

The implementation is one separate module and adapter, one model card and
guide, focused scientific/interface tests, and bounded generated JSON/CSV/plot
artifacts. It reuses only generic accepted Phase 1 functions, and all released
benchmark tests pass unchanged.

## Evidence boundary

Every gate passes. If the owner approves the record, Phase 5A may support only
this statement:

> HoloForge independently reproduces the two DGR black-hole curves in source
> Figure 3 at zero chemical potential with a Chebyshev neutral-background
> calculation and independent numerical checks.

It would not support empirical validation of QCD or lattice data, a prediction
of a QCD critical point, finite-density phase structure, source Figures 4 or 5,
critical exponents, model uniqueness, error bars for the DGR calibration,
fluctuation physics, finite-`N` physics, a top-down embedding, stability, or
relevance to unpublished research.

The paper itself reports no systematic model study or theoretical error bars
for its critical-point location and calls the result a proof of principle.
That limitation applies even more strongly before Phases 5B and 5C are run.

## Hostile critic

**"Figure 3 is a fit to lattice data, so reproducing it validates QCD."** No.
The potential, gauge kinetic function, and scale constants were selected to
approximate particular zero-density lattice curves. Phase 5A verifies the DGR
model calculation and the HoloForge implementation, not nature or the lattice
analysis.

**"The susceptibility requires a charged black-hole scan."** Not at
`mu = 0`. Because the Maxwell equation is linear and its backreaction begins
quadratically, the source susceptibility follows from a linear Maxwell field
on the neutral background. The explicit Maxwell check guards this reduction.

**"The entropy panel merely repeats Phase 1."** It is a protected reuse check,
but not redundant: DGR freezes `b = 2.057`, a different source calibration,
the MeV scale dictionary, the same 20 horizon values used for the
susceptibility, and a joint two-panel source target. Phase 1 must remain
unchanged.

**"The scale constants can hide a wrong solution."** They are frozen source
inputs, not fitted after calculation. Equation, constraint, refinement,
independent-route, Maxwell, and two separate curve gates are required before a
match can pass.

**"Why not reproduce Figure 5 now?"** Figure 5 requires a two-parameter
charged scan, branch multiplicity, susceptibility-sign classification, and
critical-point localization. Mixing it into Phase 5A would remove the clean
neutral calibration gate. It is mandatory for the separately frozen Phase 5B.

## Hard stops

Stop and return to owner review before interpreting a result if:

- any equation, sign, normalization, scale relation, or ensemble remains
  ambiguous;
- the UV factorization admits a second branch or a hidden source;
- the `x_H -> phi_0` map is not one-to-one on the target range;
- a source curve or axis map cannot be independently reconstructed;
- the numerical route needs a new field, map, domain decomposition, solver,
  restart strategy, private program, or threshold;
- any acceptance gate misses or becomes non-diagnostic;
- a Phase 1 default or accepted result changes;
- third-party lattice data or source artwork would need to be redistributed;
- finite-density, critical-point, exponent, unpublished, or private material
  enters the proposed diff; or
- public-content, package, interface, portability, or regression checks fail.

No tolerance weakening, point deletion, curve rescaling, solver substitution,
or expansion into Phase 5B is a silent rescue path.

## Owner decisions requested

### C1 -- source, model, and conventions

**Recommendation: approve.** Freeze DGR arXiv:1012.1864v2, the displayed EMD
action, `V`, `f_EMD`, canonical scalar, conformal gauge, and scale dictionary.

- **Opens:** only the public DGR model and its zero-density dictionary.
- **Remains closed:** private EMD programs, top-down claims, QCD validation,
  and alternative potentials or gauge functions.
- **Uncertainty:** the owner should check the source normalization and
  phenomenological scale interpretation before code begins.

### C2 -- Phase split and Figure 3 data boundary

**Recommendation: approve with the owner's amendment.** Make both DGR
black-hole curves in Figure 3 the complete Phase 5A target; reserve Figure 5
and the critical point for Phase 5B and selected critical exponents for Phase
5C. Figure 4 may be used as a diagnostic but is not a reproduction target.

- **Opens:** the two derived Figure 3 black-hole anchor tables.
- **Remains closed:** lattice markers, source artwork, Figure 4 reproduction,
  Figure 5, critical coordinates, exponents, and finite-density conclusions.
- **Uncertainty:** the anchors are vector-derived, not author-supplied raw
  numerical data.

### C3 -- equations, endpoints, and numerical route

**Recommendation: approve.** Use the exact-endpoint neutral Chebyshev BVP at
`N = (80, 120, 150)`, physical `phi_0` targeting, independent DOP853
backgrounds, and an explicit Maxwell linear-response check.

- **Opens:** the declared one-parameter local spectral preflight only.
- **Remains closed:** shooting fallback, private code, random restarts,
  two-parameter charged backgrounds, and silent Phase 1 changes.
- **Uncertainty:** the small UV exponent `nu` and high-`phi_0` endpoint may
  expose conditioning or branch problems and therefore remain hard stops.

### C4 -- numerical gates and tolerances

**Recommendation: approve.** Freeze all 14 gates, including `1e-6`
independent equation and constraint ceilings, three-degree and quadrature
refinement, and separate source-curve tolerances.

- **Opens:** auditable classification of a future preflight.
- **Remains closed:** post-result tolerance changes or acceptance from visual
  agreement alone.
- **Uncertainty:** prospective thresholds have not yet been measured on a DGR
  implementation; a miss returns with evidence.

### C5 -- evidence claim, artifacts, and privacy

**Recommendation: approve.** Permit only the named future public module,
adapter, model card, guide, tests, records, and HoloForge-generated Figure 3
comparison after all gates pass.

- **Opens:** a future bounded `reproduced` recommendation after a second owner
  review.
- **Remains closed:** empirical QCD claims, lattice redistribution, source
  artwork, private material, finite-density artifacts, and every Git/release
  action.
- **Uncertainty:** common-code reuse must not alter any released benchmark.

### C6 -- bounded implementation authorization

**Recommendation: approve only after C1--C5 are accepted.** Authorize the
Phase 5A local implementation and complete preflight, followed by a mandatory
owner-review return.

- **Opens:** only the planned local files and validation commands.
- **Remains closed:** result or model-card acceptance, commit, push, pull
  request, merge, tag, release, branch deletion, Phase 5B, and Phase 5C.
- **Uncertainty:** any new scientific or numerical issue stops the run rather
  than silently expanding the contract.

## Owner response paths

- **A -- approve all recommendations:** approve C1--C6 and authorize only the
  bounded Phase 5A local implementation and preflight.
- **B -- approve selected items:** name the approved decisions; all others
  remain closed.
- **C -- request revision or evidence:** identify the source, equation,
  convention, phase split, gate, tolerance, or limitation to revise.
- **D -- status walkthrough only:** discuss the contract without opening
  implementation.
- **E -- custom response:** state a different bounded instruction.

**Recommended path: A.** It advances the already selected bottom-up DGR model
to a clean zero-density spectral preflight while preserving a mandatory owner
return before result acceptance or any Git/public action.

## Owner disposition -- 2026-08-22

Xin-Yi Liu selected Option E to amend C2: Phase 5B must reproduce Figure 5,
whereas Figure 4 is optional and should be used only if it is necessary for
constructing or validating the charged branch scan. The owner then explicitly
approved Option A under that amendment. C1--C6 are therefore approved with
this bounded interpretation.

This disposition opens only the local Phase 5A implementation and complete
preflight. It does not accept a future result or model card and does not open
commit, push, pull request, merge, tag, release, branch deletion, Phase 5B, or
Phase 5C. The implementation must return to owner review whether the gates pass
or fail.

## Phase 5A implementation preflight -- 2026-08-22

The bounded implementation is complete in the isolated worktree and the
registered command passes all fourteen prospective gates. No threshold,
target, source scale, or phase boundary was changed after seeing the result.
The high-degree solver issue encountered during development was resolved by
applying the frozen `N=80 -> 120 -> 150` continuation independently at each
physical `phi_0` target; horizon-only continuation is not accepted as a
high-degree solution.

| Evidence | Maximum observed | Frozen ceiling | Status |
| --- | ---: | ---: | --- |
| Scaled collocation residual | `9.313322e-10` | `1e-8` | pass |
| Oversampled equation residual | `5.847086e-10` | `1e-6` | pass |
| Einstein constraint | `1.505612e-12` | `1e-6` | pass |
| Endpoint and horizon regularity | `1.532446e-12` | `1e-8` | pass |
| Physical horizon target error | `2.635049e-12` | `1e-9` | pass |
| Final spectral observable change | `5.551312e-11` | `2e-4` | pass |
| Final quadrature change | `8.036525e-13` | `2e-5` | pass |
| Explicit Maxwell/flux check | `1.625296e-9` | `1e-8` flux | pass |
| Chebyshev--DOP853 comparison | `1.163957e-6` | `5e-4` | pass |
| Figure 3 entropy anchor error | `0.08398744` | `0.15` | pass |
| Figure 3 susceptibility anchor error | `0.002607142` | `0.005` | pass |
| Duplicate complete-run difference | `0` | `1e-12` | pass |

The two-panel HoloForge plot was inspected at full size. The spectral curves
track the derived public DGR Figure 3 black-hole path anchors in both panels;
no lattice markers or source artwork are redistributed. The strict result
record now reports `support_level = reproduced` and
`result_review_state = approved`.

### Result-review decisions requested

**R1 -- scientific result. Recommendation: approve.** Accept the bounded claim
that HoloForge independently reproduces the two DGR Figure 3 black-hole curves
at zero chemical potential. This does not validate QCD or the lattice data and
does not open finite density.

**R2 -- model card, guide, reference anchors, tests, and generated Figure 3.
Recommendation: approve.** Promote only these Phase 5A public artifacts from
reference/unreviewed to reproduced/approved, retaining material AI provenance
and all limitations.

**R3 -- scoped Git integration. Recommendation: approve after R1 and R2.**
Permit one logical commit of the reviewed Phase 5A change, then the separately
authorized push/PR/merge/release workflow. Phase 5B and Phase 5C remain closed.

Owner response paths at this mandatory return are:

- **A:** approve R1--R3;
- **B:** approve selected items and name them;
- **C:** request revision or more evidence;
- **D:** status walkthrough only; or
- **E:** give a different bounded instruction.

The recommended path is **A**, because every prospective gate passes with
margin, the reproduced source curves are now directly visible, and the next
phase remains explicitly closed.

## R1--R3 owner disposition -- 2026-08-22

Xin-Yi Liu selected **Option A** and approved R1--R3. The bounded claim that
HoloForge reproduces the two selected DGR Figure 3 black-hole curves at zero
chemical potential is accepted at support level `reproduced`. The model card,
guide, derived public anchors, tests, strict record, CSV, HoloForge-generated
plot, and material AI provenance are approved.

This decision also authorizes the scoped commit, push, pull request, green-CI
merge, and release workflow for Phase 5A. It does not open finite-density Phase
5B or critical-scaling Phase 5C. Figure 5 and the reported model critical point
remain mandatory targets of a future separately reviewed Phase 5B contract;
Figure 4 remains optional diagnostic evidence only.
