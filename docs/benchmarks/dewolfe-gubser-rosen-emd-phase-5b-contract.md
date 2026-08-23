# DeWolfe--Gubser--Rosen EMD Phase 5B contract

## Status and authorization boundary

This is the approved-and-gated scientific contract for **Phase 5B** of the
classical benchmark sequence. It is public-source **Forge/Verify** work based
on the phenomenological bottom-up Einstein--Maxwell--dilaton (EMD) model of
DeWolfe, Gubser, and Rosen (DGR).

- **Completed:** Phases 0--4 and DGR Phase 5A are released; Phase 5A closed in
  Version 0.5.6.
- **Completed:** the separate CI-deduplication change was merged on
  2026-08-22 and its exact post-merge `main` run passed all seven jobs.
- **Completed:** the owner selected Option A and approved C1--C7 on
  2026-08-22.
- **Completed:** the required pre-implementation audit found and corrected one
  radial-orientation sign inconsistency in the displayed positive charge
  definition; the owner selected Option A and approved C3a on 2026-08-22.
- **Completed:** the bounded charged-point implementation converges
  deterministically through `N = 150`, satisfies the implemented three
  compact-equation, constraint, endpoint, refinement, and source-coordinate
  checks, and
  preserves `Phi' < 0` for positive charge.
- **Completed:** the owner approved R1--R4 and opened only the prospective C3b
  density-dictionary repair on 2026-08-22. A fresh source audit and an
  independent Maxwell/UV reconstruction found no HoloForge solver,
  boundary-condition, sign, flux, or coordinate-normalization error.
- **Completed:** the owner selected Option A and approved S1--S5 on
  2026-08-22. The implemented semantic repair preserves
  `rho_canonical_BH = q/2`, relabels the paper axis as
  `rho_source_figure5`, blocks absolute-ordinate agreement, and keeps the
  inverse-`f_H^2` quantity non-inferential.
- **Completed, provisional:** the exact frozen `9 x 9` then `13 x 13`,
  `N = 80` charged-background map completed all 250 states without an
  implemented numerical-gate failure. The independent Maxwell reconstruction
  was included in the final repeat.
- **Completed:** the simultaneous explicit-`Phi` formulation passes all four
  frozen controls and agrees with the flux-reduced primary route.
- **Completed, incomplete map:** the wider C3c survey stored 170 states that
  pass its implemented rows, then stopped at reconstructed Gauss drift
  `1.4251413e-7` against the frozen `1e-7` ceiling. The remaining 50 survey
  states and all 561 refinement states were not run.
- **Completed audit:** C3d shows the same reconstructed drift at `N=120`,
  while the explicit conserved-flux metric improves from `6.69e-10` to
  `1.35e-13`. It also found that C3c omitted the frozen Noether row.
- **Current implementation:** the owner approved C3e Option A on 2026-08-23,
  opening the map-wide authoritative explicit-flux Gauss diagnostic,
  restoration of the Noether gate, and a complete fresh map. No fresh map
  result has yet been accepted.
- **Closed:** result acceptance, commit, push, pull request, merge, tag,
  release, branch deletion, and Phase 5C.

No Phase 5B numerical result has been accepted. The selected charged point is
provisional implementation evidence only. C3a resolves the declared sign
ambiguity but does not authorize a density rescaling. A future passing
calculation would reproduce a result of the DGR model; it would not
empirically validate a QCD critical point.

## Recommendation and benchmark identity

Add a separate benchmark and command:

```text
dewolfe-gubser-rosen-emd-critical-point
```

Do not expand or change the released
`dewolfe-gubser-rosen-emd` Phase 5A benchmark. Phase 5B must reproduce:

1. the single-valued, infinite-slope, and multivalued isotherm topology in
   DGR source Figure 5; and
2. the reported model candidate critical point
   `(T_c, mu_c) approximately (143 MeV, 783 MeV)`.

Source Figure 4 may be used to diagnose parameter-space coverage, branch
multiplicity, and Jacobian signs. Reproducing its full panel is not required.
Critical exponents, first-order coexistence data, and near-critical fits
remain Phase 5C.

## Primary public source and provenance

Oliver DeWolfe, Steven S. Gubser, and Christopher Rosen, "A holographic
critical point," *Physical Review D* **83**, 086005 (2011),
[arXiv:1012.1864v2](https://arxiv.org/abs/1012.1864),
[doi:10.1103/PhysRevD.83.086005](https://doi.org/10.1103/PhysRevD.83.086005).

The official public arXiv artifacts inspected for this contract have SHA-256
digests

```text
paper PDF:                 ed6f00b759dbf3347521b6321d2c69c8c2e629f45ff7ab3dd6a9e6a6afc7040c
source archive:            3f921d2212cb5f7956c1da7cbb0904c02ff32e302d514ab2e80b4bfc64b6778e
Figure 5, above T_c:       c6a56d588ee5491c2e06359d3d718b8fd21a24ebcf4f888b796a0a6db87d0719
Figure 5, at T_c:          5282e9a4174fd124a18a6aa53861182277b7c46024e8b6e301c39839942ed8a3
Figure 5, below T_c:       5519dfc2f0abfa1f721f28432a7b748e73c15d532104e21c14d32b5395814064
```

The public TeX and all three vector Figure 5 panels were inspected directly.
The paper PDF, source archive, and source artwork are audit inputs only and
must not be committed or redistributed. The reference table below contains
only AI-assisted numerical anchors derived from the public vector paths.

## Support, review, and data boundary

| Item | Support level | Review state |
| --- | --- | --- |
| Source action, functions, equations, dictionary, and scale choices | `established-source` | C1--C7 approved by Xin-Yi Liu on 2026-08-22 |
| Charged conformal-gauge equations and flux reduction below | direct derivation from source equations | C1--C7 and C3a approved; AI-assisted |
| Derived Figure 5 path anchors | derived public-source record | C2 approved; AI-extracted |
| Selected charged point | provisional implementation evidence | unreviewed; local equations, independent Maxwell reconstruction, and density semantics pass |
| Bounded charged-background map | provisional implementation evidence | executed at the exact approved bounds; 81/81 survey and 169/169 refinement states pass the implemented point gates |
| Canonical topology result | provisional numerical analysis | qualitative below/above behavior appears, but the critical tangent is unresolved and every reported path touches both scan boundaries; Gate 6 hard stop |
| Absolute Figure 5 ordinate comparison | not executed | blocked by unresolved `rho_source_figure5` dictionary |
| Critical exponents or a physical-QCD critical point | not a Phase 5B result | closed |

DGR is a phenomenological bottom-up model. Its potential and gauge kinetic
function were calibrated to selected zero-density lattice behavior, but the
authors do not claim a precise string construction and do not provide a
systematic model uncertainty for the critical point. The temporary private
Mathematica programs are neither required nor authorized for copying or
public transfer.

## Model, ensemble, and source functions

Use the already reviewed five-dimensional, mostly-plus convention

```text
S = 1/(2 kappa_5^2) integral d^5x sqrt(-g) [
      R - 1/2 (partial phi)^2 - 1/4 f_EMD(phi) F_ab F^ab - V(phi)
    ],

V(phi) = [-12 cosh(gamma phi) + b phi^2]/L^2,
gamma = 0.606,
b = 2.057,

f_EMD(phi) = sech[(6/5)(phi - 2)] / sech(12/5).
```

Use `L = kappa_5 = 1` in the source-normalized black-hole calculation. The
grand-canonical variables are `(T, mu)`; `rho` and `s` are derived densities.
At the regular horizon choose `Phi(z_H) = 0`, so the boundary value of `Phi`
is the chemical potential. A negative susceptibility branch is retained as a
diagnostic unstable solution and is never called a stable phase.

Freeze the source scale dictionary

```text
lambda_T   = 252 MeV,
lambda_mu  = 972 MeV,
lambda_rho = (77 MeV)^3,
lambda_s   = (121 MeV)^3.
```

The reported critical coordinates therefore correspond approximately to

```text
T_c,BH  = 143/252 = 0.5674603174603174,
mu_c,BH = 783/972 = 0.8055555555555556.
```

The displayed integer scales have the already recorded rounding mismatch in
their scale-product relation. They are source inputs, not refitted values.

## Charged conformal-gauge boundary-value problem

Use

```text
ds^2 = exp(2 A(z)) [-h(z) dt^2 + d x_vec^2 + dz^2/h(z)],
A_a dx^a = Phi(z) dt.
```

Primes mean `d/dz`. The primary charged equations are

```text
A'' - A'^2 + phi'^2/6 = 0,

h'' + 3 A' h' - exp(-2 A) f_EMD Phi'^2 = 0,

Phi'' + A' Phi' + (f_EMD,phi/f_EMD) phi' Phi' = 0,

h phi'' + (3 A' h + h') phi'
  - exp(2 A) V_phi
  + 1/2 exp(-2 A) f_EMD,phi Phi'^2 = 0.
```

The independently evaluated Einstein constraint is

```text
6 A' h' + h (24 A'^2 - phi'^2)
  + 2 exp(2 A) V + exp(-2 A) f_EMD Phi'^2 = 0.
```

Because `z` increases inward from the conformal boundary to the horizon,
positive chemical potential and density require the orientation-fixed charge

```text
q = -f_EMD exp(A) Phi' > 0
```

to be radially constant. Eliminate `Phi` from the nonlinear collocation
fields:

```text
Phi' = -q exp(-A)/f_EMD,
mu_BH = q integral_0^z_H dz exp(-A)/f_EMD,
rho_canonical_BH = q/(2 kappa_5^2).
```

The electrical source tail is then recovered by quadrature instead of being
collocated as a high-power UV field. This is an analytic Maxwell reduction,
not a probe approximation: the `q^2` backreaction remains in the metric and
scalar equations.

At the boundary require `h(0)=1`, the Phase 5A unit scalar-source
normalization, and asymptotically AdS warp behavior. At the regular simple
horizon require

```text
h(z_H) = 0,
Phi(z_H) = 0,

6 A'_H h'_H + 2 exp(2 A_H) V_H
  + q^2 exp(-4 A_H)/f_EMD,H = 0,

h'_H phi'_H - exp(2 A_H) V_phi,H
  + 1/2 q^2 exp(-4 A_H) f_EMD,phi,H/f_EMD,H^2 = 0.
```

Retain the same analytic UV factorization as Phase 5A:

```text
x = (z/L)^nu,
u = x/x_H in [0, 1],
A = -log(z/L) + x^2 C(u),
phi = x P(u),
h = H(u),

H(0) = 1,
H(1) = 0,
P(0) = 1.
```

The implementation parameters are the physical horizon scalar `phi_H` and
the invariant charge ratio

```text
eta = q/[exp(3 A_H) sqrt(-2 V_H f_EMD,H)].
```

This equals the source `Phi_1/Phi_1,max` in its normalized horizon gauge. The
source reports the candidate critical neighborhood

```text
(phi_H, eta) approximately (4.84, 0.40).
```

Thermodynamics are extracted as

```text
T_BH = abs(h'_H)/(4 pi),
s_BH = 2 pi exp(3 A_H)/kappa_5^2.
```

In this inward conformal orientation the conserved quantities are

```text
Q_G^(z) = f_EMD exp(A) Phi' = -q,
Q_N^(z) = exp(3 A) h' - f_EMD exp(A) Phi Phi'
        = exp(3 A) h' + q Phi
        = -2 kappa_5^2 T s.
```

Their normalized radial drifts must be evaluated with these signed
definitions. The independent outward `B=0` route uses the source-positive
Gauss orientation; compare magnitudes and thermodynamics after the complete
UV dictionary.

## Figure 5 reference paths

Figure 5 contains three constant-temperature curves in the source's plotted
dimensionless coordinates. The paper labels the panels only as
`T > T_c`, `T = T_c`, and `T < T_c`; it does not publish exact temperatures
for the outer panels. Filled blue vector points were isolated, mapped using
the vector tick coordinates, sorted in `rho`, and linearly interpolated at
the frozen source-artwork anchors below. The affine vector maps place
`mu_BH` on the horizontal abscissa and the paper density on the vertical
ordinate. Because the public density dictionary does not reproduce that
ordinate, it is named `rho_source_figure5` and is not identified with
`rho_canonical_BH`.

| `rho_source_figure5` | `mu_BH`, above `T_c` | `mu_BH`, at `T_c` | `mu_BH`, below `T_c` |
| ---: | ---: | ---: | ---: |
| 5 | 0.763360248 | 0.798016580 | 0.804842255 |
| 6 | 0.769184501 | 0.802130292 | 0.808652241 |
| 7 | 0.772491083 | 0.804082027 | 0.810375950 |
| 8 | 0.774429108 | 0.804868047 | 0.810812705 |
| 9 | 0.775677302 | 0.805101632 | 0.810850854 |
| 10 | 0.776608413 | 0.805121624 | 0.810712157 |
| 11 | 0.777384213 | 0.805103109 | 0.810562202 |
| 12 | 0.778201412 | 0.805190607 | 0.810497383 |
| 13 | 0.779162673 | 0.805484660 | 0.810678207 |
| 14 | 0.780265316 | 0.806013227 | 0.811037943 |
| 16 | 0.783136041 | 0.807772507 | 0.812599677 |
| 18 | 0.786922967 | 0.810528785 | 0.815169234 |

The middle panel carries the source label `T_c`. The outer-panel temperature
windows remain frozen historical contract inputs, not new source claims:

```text
T_minus/T_c in [0.90, 0.999],
T_plus/T_c  in [1.001, 1.10].
```

Do not run the temperature fit while the absolute-ordinate comparison is
blocked. No axis rescaling, point deletion, per-point temperature, diagnostic
proxy fit, or manual tuning is allowed. The derived anchors remain an approved
source record but are not a canonical-density acceptance target.

## Frozen numerical routes and scan

The primary route reuses maintained Chebyshev--Gauss--Lobatto construction,
barycentric evaluation, and generic evidence interfaces. It must not change
Phase 5A equations, defaults, results, or schemas.

```text
critical search patch:
  phi_H in [4.2, 5.5]
  eta   in [0.30, 0.50]

map grids at field degree N = 80:
  deterministic 9 x 9 survey, then 13 x 13 refinement

reported critical and Figure 5 states:
  N = (80, 120, 150), with N = 150 reported

nonlinear solve:
  scipy.optimize.root(method="hybr", xtol=1e-11)
  then, only when triggered, at most 32 evaluations of
  scipy.optimize.least_squares(method="trf")
```

Continue deterministically in neighboring `(phi_H, eta)` states. A wider
coverage diagnostic may extend only within the source-declared
`phi_H in [1, 15]`, `eta in [0, 0.9]` domain; touching a contract boundary,
losing asymptotic AdS behavior, or needing a new seed family is a hard stop.
No shooting fallback, random restart, best-of-seed selection, source-point
deletion, or private program is allowed.

Use the two-dimensional physical map to inspect constant-temperature paths in
the canonical pair `(rho_canonical_BH, mu_BH)` without mapping them onto the
blocked source-artwork ordinate. Locate the critical point by the coalescence
conditions on the critical isotherm

```text
(partial mu/partial rho)_T = 0,
(partial^2 mu/partial rho^2)_T = 0,
```

and independently verify the corresponding degeneracy of
`partial(T,mu)/partial(phi_H,eta)`. Below `T_c`, require two distinct spinodal
turning points and a negative-susceptibility middle branch. Above `T_c`,
require a single-valued positive-susceptibility path.

At five selected states spanning the three Figure 5 curves, independently
integrate the source equations in `B=0` gauge with a fourth-order regular
horizon series and

```text
scipy.integrate.solve_ivp(
  method="DOP853", rtol=1e-10, atol=1e-12
)
```

Refine the horizon cutoff and compare `(T, mu, s, rho_canonical)` after the
complete UV dictionary. This changes gauge, discretization, and evolution direction; it
does not provide independent physical equations.

## Prospective acceptance gates

All ceilings are frozen before implementation. Their scale is based on the
binary64 Chebyshev second-derivative conditioning already measured at the
declared degrees, including `epsilon ||D2||_infinity approximately 3.75e-8`
at `N=150`, rather than on a future desired curve. A missed gate returns to
owner review; it is not permission to relax the gate.

1. **Source algebra:** action, `V`, `f_EMD`, UV mass/dimension, charged
   conformal equations, flux reduction, horizon equations, thermodynamic
   dictionary, source scales, and critical-coordinate conversion agree with
   displayed analytic values to `1e-12` where values are exact.
2. **Nonlinear solve:** every final state reports maintained-library success
   with scaled collocation residual at most `1e-6`; any bounded TRF polish and
   its trigger are recorded.
3. **Independent physical equations:** all four uncross-multiplied charged
   equations on a barycentrically evaluated grid of at least `2N` have
   individual scaled infinity norms at most `1e-5`.
4. **Constraint and endpoints:** the independently evaluated Einstein
   constraint is at most `1e-5`; boundary conditions and both undivided
   horizon regularity equations are at most `1e-7`.
5. **Conserved quantities:** normalized Gauss-flux drift is at most `1e-7`
   and normalized Noether-charge drift is at most `1e-6`.
6. **Parameter and branch integrity:** requested
   `(phi_H, eta, T, rho_canonical)`
   targets meet relative error `1e-7`; all reported paths are continuous,
   retain asymptotic AdS behavior, and do not touch a scan boundary.
7. **Spectral refinement:** from `N=120` to `N=150`, the maximum scaled change
   in `(T, mu, s, rho_canonical)` and every reported critical coordinate is at most
   `2e-3` and improves over `N=80` to `N=120` above a `1e-8` floor.
8. **Independent route:** the DOP853 calculation agrees with spectral
   `(T, mu, s, rho_canonical)` within relative error `5e-3` at all five selected states,
   and its final cutoff refinement changes them by at most `1e-3`.
9. **Critical source coordinates:** the HoloForge candidate satisfies
   `|T_c - 143 MeV| <= 5 MeV`, `|mu_c - 783 MeV| <= 10 MeV`,
   `|phi_H,c - 4.84| <= 0.20`, and `|eta_c - 0.40| <= 0.04`.
10. **Critical conditions:** the two spinodals coalesce at the reported
    critical state; normalized first- and second-derivative conditions and
    the independent parameter-map Jacobian diagnostic are each at most
    `2e-3` under both grid and step-size refinement.
11. **Figure 5 absolute-ordinate comparison -- blocked:** preserve all 36
    `rho_source_figure5` anchors and the historical `2e-3` maximum/
    `7.5e-4` RMS thresholds, but do not evaluate them against
    `rho_canonical_BH` while the source dictionary is unresolved. This gate
    cannot pass, fail, or affect canonical topology acceptance in the current
    phase.
12. **Canonical Figure 5 topology:** in `(rho_canonical_BH, mu_BH)`, the
    above-`T_c` curve is single-valued with
    positive susceptibility, the below-`T_c` curve has exactly two spinodals
    and a negative-susceptibility middle branch, and the critical curve has
    coalesced spinodals/infinite susceptibility. A visually similar path with
    the wrong topology fails.
13. **Determinism and interfaces:** two complete verifier runs agree in every
    reported physical observable to `1e-10`, scaled by
    `max(1, abs(a), abs(b))`; strict JSON, human CLI, evidence bundle,
    overwrite protection, and installed-wheel behavior pass.
14. **Regression, privacy, and runtime:** all released tests and verifiers
    pass unchanged; scans find no private path, unpublished identifier,
    secret, source artwork, or temporary Mathematica dependency. If one full
    verifier exceeds 45 minutes on the declared reference environment, stop
    before CI integration and return with a runtime profile.

The `1e-6` collocation and `1e-5` independently evaluated equation/constraint
ceilings are physics-conditioned spectral diagnostics. Endpoint equations,
flux conservation, degree refinement, canonical branch topology, and the
independent gauge/solver route prevent these ceilings from accepting a merely
plausible plot. The blocked source-ordinate anchors provide no such acceptance
evidence in the current phase.

## CI and artifact architecture

The expensive two-parameter verification must be designed without recreating
the duplicate-work problem removed immediately before Phase 5B:

- run one full high-degree verifier in one dedicated installed-wheel
  Python 3.11 job;
- keep bounded algebra, adapter, point-solution, and schema tests in normal
  discovery;
- use selected point portability checks in other Python/OS jobs, not a full
  two-dimensional scan in every job; and
- stop for owner review before CI if the 45-minute local runtime ceiling is
  exceeded. Never silently reduce the scientific grid to make CI green.

The future evidence bundle must record source identifiers and digests,
equations and conventions, scan bounds and temperatures, all solver versions
and diagnostics, critical conditions, both conserved charges, degree/cutoff
refinement, the independent-route comparison, all Figure 5 anchors,
limitations, AI provenance, deterministic hashes, and runtime profiles.

The future plot may show only HoloForge-generated curves and the derived
Figure 5 anchors. It must label the result as a DGR model reproduction; source
artwork and third-party lattice data are forbidden.

## Evidence boundary and hostile criticism

If every gate later passes and the owner accepts the result, Phase 5B may
support only:

> HoloForge independently reproduces the three branch topologies in DGR
> source Figure 5 and locates the reported candidate critical point of that
> specific bottom-up EMD model with spectral charged backgrounds and an
> independent numerical route.

It would not establish a QCD critical point, experimental relevance, lattice
agreement at finite density, model uniqueness, a top-down embedding,
renormalized free energies, a physical coexistence line, critical exponents,
finite-`N` fluctuations, or systematic theoretical error bars.

**"The S-shaped curve proves the first-order coexistence line."** No. It
establishes multivalued extrema and a locally unstable branch. The source did
not calculate the renormalized free energy and later used an equal-area
construction. Phase 5B therefore reports a candidate critical point and
spinodals, not an independently verified equal-free-energy coexistence line.

**"Fitting the outer temperatures makes Figure 5 agreement automatic."** No.
Each outer panel receives one bounded scalar temperature only; 12 fixed
anchors, the curve topology, critical coordinates, equations, refinement,
and independent-route checks remain simultaneous gates. The fit and objective
profile are preserved.

**"Figure 4 is required to locate the point."** Its broad scan is useful
diagnostically, but the paper supplies the critical neighborhood and Figure 5
contains the direct branch-topology target requested by the owner. Any wider
scan must stay inside the declared source domain and cannot become a hidden
Figure 4 reproduction claim.

**"The paper calls this a QCD critical point."** The paper explicitly treats
the construction as a proof of principle without systematic model error bars
and omits fluctuations. HoloForge verifies its calculation and must preserve
that limitation.

## Hard stops

Stop and return to owner review if:

- any equation, sign, charge normalization, ensemble, gauge transformation,
  scale, or Figure 5 coordinate map remains ambiguous;
- `eta` fails to reproduce the source horizon charge ratio;
- the critical root or either Figure 5 path touches a scan or temperature-fit
  boundary;
- a fold is crossed by unresolved interpolation rather than continued physical
  solutions;
- the numerical route needs a new field, domain decomposition, solver,
  restart strategy, private program, threshold, or omitted source point;
- any gate misses, the full verifier exceeds 45 minutes, or the independent
  route disagrees;
- Phase 5A behavior, a released schema, or a released result changes;
- source artwork, private material, or unpublished research would enter the
  diff; or
- a critical exponent, coexistence/free-energy claim, or empirical-QCD claim
  enters the proposed artifact.

No tolerance weakening, point deletion, temperature-window expansion, axis
rescaling, solver substitution, or expansion into Phase 5C is a silent rescue
path.

## Owner decisions requested

### C1 -- source, model, and separate benchmark

**Recommendation: approve.** Freeze DGR arXiv:1012.1864v2, the reviewed
action/functions/scales, and a new
`dewolfe-gubser-rosen-emd-critical-point` identifier.

- **Opens:** only the public DGR charged model under a separate interface.
- **Remains closed:** any change to Phase 5A, private EMD code, alternative
  potentials, top-down claims, and QCD validation.
- **Uncertainty:** the source calibration is phenomenological and has no
  systematic model-error analysis.

### C2 -- Figure 5 target and reference data

**Recommendation: approve.** Make all three Figure 5 topologies and the 36
derived anchors mandatory; fit only the two unreported outer-panel
temperatures inside the frozen windows. Keep Figure 4 optional.

- **Opens:** the derived vector-path anchor table and bounded temperature fit.
- **Remains closed:** source artwork, lattice data, full Figure 4 reproduction,
  point deletion, or post-result rescaling.
- **Uncertainty:** anchors are vector-derived rather than author-supplied raw
  data, and the outer temperatures are not published.

### C3 -- equations, ensemble, endpoints, and charge parameter

**Recommendation: approve as corrected by C3a below.** Freeze the charged
conformal BVP, exact endpoints, inward-orientation positive charge
`q = -f_EMD exp(A) Phi'`, flux-eliminated Maxwell field, grand-canonical
dictionary, and invariant `(phi_H, eta)` parameterization.

- **Opens:** the declared charged spectral equations only.
- **Remains closed:** probe approximation, shooting fallback, fitted endpoint
  conditions, and alternative charge normalizations.
- **Uncertainty:** the small UV exponent and charged horizon conditioning may
  expose a need for a new formulation, which is a hard stop.

### C4 -- scan, critical locator, and independent route

**Recommendation: approve.** Freeze the two-stage local patch, continued
constant-temperature paths, coalescing-spinodal locator, independent
parameter-map Jacobian, and five-state DOP853 comparison.

- **Opens:** only the bounded local map and source-domain diagnostic expansion.
- **Remains closed:** random/best-of seeds, unresolved fold interpolation,
  dense Phase 5C data, and silent global expansion.
- **Uncertainty:** the source's critical locator was grid/finite-difference
  based, so the proposed continuous locator is a stronger HoloForge method
  that still must reproduce the source result.

### C5 -- prospective gates, tolerances, and runtime

**Recommendation: approve.** Freeze all 14 gates, including conditioned
`1e-6`/`1e-5` differential-equation diagnostics, independent-route evidence,
critical/source tolerances, Figure 5 errors, and the 45-minute return gate.

- **Opens:** auditable classification of a future preflight.
- **Remains closed:** post-result tolerance changes or visual acceptance.
- **Uncertainty:** charged `N=150` conditioning and total runtime have not yet
  been measured on the implementation.

### C6 -- evidence claim, privacy, and CI architecture

**Recommendation: approve.** Permit only the future public module, adapter,
model card, guide, tests, records, HoloForge plot, and deduplicated CI shape
described here.

- **Opens:** a future bounded `reproduced` recommendation after result review.
- **Remains closed:** source artwork, private paths/programs, QCD validation,
  coexistence/free-energy claims, and repeated full scans across the CI matrix.
- **Uncertainty:** any new public artifact remains unreviewed until a second
  owner gate.

### C7 -- bounded implementation authorization

**Recommendation: approve only after C1--C6 are accepted.** Authorize the
local Phase 5B implementation and complete preflight, followed by a mandatory
owner-review return whether the gates pass or fail.

- **Opens:** only local implementation and validation on the isolated branch.
- **Remains closed:** result/model-card acceptance, commit, push, pull request,
  merge, tag, release, branch deletion, and Phase 5C.
- **Uncertainty:** any hard stop returns without silently enlarging scope.

## Owner response paths

- **A -- approve all recommendations:** approve C1--C7 and authorize only the
  bounded local Phase 5B implementation and preflight.
- **B -- approve selected items:** name the approved decisions; all others
  remain closed.
- **C -- request revision or evidence:** identify the source, equation,
  convention, scan, gate, tolerance, runtime, or limitation to revise.
- **D -- status walkthrough only:** discuss the contract without opening
  implementation.
- **E -- custom response:** state a different bounded instruction.

**Recommended path: A.** It implements the already agreed Phase 5B target
while preserving a mandatory return before result acceptance or any Git or
public action.

## Owner disposition -- 2026-08-22

Xin-Yi Liu selected **Option A** and approved C1--C7. This disposition opens
only the bounded local Phase 5B implementation and complete preflight on the
isolated branch, followed by a mandatory owner-review return whether the
frozen gates pass or fail.

It does not accept a future numerical result or model card and does not open
commit, push, pull request, merge, tag, release, branch deletion, or Phase 5C.
Every hard stop and unsupported-claim boundary above remains in force.

## Independent pre-implementation audit and C3a -- 2026-08-22

Before any charged code was written, an independent source/equation audit
confirmed the conformal equations, constraint, both horizon equations,
thermodynamic dictionary, `eta` mapping, critical conditions, Figure 5 anchor
interpretation, and evidence limitations. It found one clerical orientation
inconsistency in the originally displayed Gauss definition.

With `z = 0` at the boundary, `z = z_H` at the horizon, `Phi(0) = mu > 0`, and
`Phi(z_H) = 0`, positive density has `Phi' < 0`. C3a therefore proposes the
orientation-fixed definitions now displayed above:

```text
q = -f_EMD exp(A) Phi' > 0,
Phi' = -q exp(-A)/f_EMD,
Q_G^(z) = -q,
Q_N^(z) = exp(3 A) h' + q Phi = -2 kappa_5^2 T s.
```

The `q^2` background equations, constraint, horizon equations, `mu`, `rho`,
`eta`, scan, anchors, tolerances, and all other decisions are unchanged. This
is not a new physical model choice, but the contract explicitly requires an
owner return for any sign ambiguity.

### C3a -- radial orientation and signed conserved charges

**Recommendation: approve.** Accept the corrected positive-density charge,
Maxwell derivative, Gauss orientation, and Noether diagnostic above, then
resume the already approved bounded local implementation and preflight.

- **Opens:** only resumption of the previously approved local implementation.
- **Remains closed:** every result, Git, release, Phase 5C, free-energy, and
  empirical-QCD action already closed by C1--C7.
- **Uncertainty:** none remains in this convention after the source-coordinate
  transformation and UV density expansion were independently checked.

### C3a response paths

- **A -- approve the correction:** approve C3a and resume the bounded local
  Phase 5B implementation/preflight.
- **B -- approve with a stated modification:** give the exact convention to
  use; all implementation remains paused until it is unambiguous.
- **C -- request more derivation or evidence:** keep implementation paused.
- **D -- status walkthrough only:** discuss the sign transformation without
  resuming implementation.
- **E -- custom response:** state a different bounded instruction.

**Recommended path: A.** It corrects the inward radial orientation without
changing the approved physics target or any numerical gate.

### C3a owner disposition -- 2026-08-22

Xin-Yi Liu selected **Option A** and approved C3a. This disposition resumes
only the bounded local Phase 5B implementation and complete preflight already
authorized by C7, followed by the mandatory owner-review return whether the
frozen gates pass or fail.

It does not accept a future numerical result or model card and does not open
commit, push, pull request, merge, tag, release, branch deletion, Phase 5C,
free-energy/coexistence claims, or empirical-QCD claims. Every other hard stop
and unsupported-claim boundary remains in force.

## Charged-solver preflight and C3b owner gate -- 2026-08-22

The separately implemented, fully backreacted charged Chebyshev point solver
converges deterministically at `(phi_H, eta) = (4.84, 0.40)` through
`N = (80, 120, 150)`. At `N = 150` it gives

```text
T_BH  = 0.5669465710355773,
mu_BH = 0.8056545697761217,
T     = 142.8705359 MeV,
mu    = 783.0962418 MeV,
q     = 2.6736618002,
rho_canonical = q/2 = 1.3368309001.
```

The `N = 80` scaled collocation residual is `6.72e-10`, the independently
evaluated unscaled three-equation maximum is `4.32e-8`, and the unscaled
constraint maximum is `2.88e-9`. At `N = 150` these latter diagnostics improve
to `1.08e-8` and `3.98e-10`; duplicate selected-point solves are bitwise
identical, and an explicit interior evaluation confirms `Phi' < 0`.
These are provisional technical facts, not an accepted Phase 5B result.

The implementation then reached a mandatory source-dictionary hard stop. The
paper prints `rho_c = 9.9022`, and the approved Figure 5 anchors begin at
`rho = 5`, while the complete frozen critical tolerance box gives only
`0.921014896 <= rho_canonical <= 1.902892698`. The published Gauss law and the
independent UV Maxwell tail both imply `rho_canonical = q/2`; solver
refinement cannot repair the disjoint ranges.

At the rounded source horizon,

```text
rho_c / rho_canonical = 7.40722,
1 / f(phi_H)^2         = 7.40236,
rho_canonical / f(phi_H)^2 = 9.89570.
```

This strongly suggests an unstated Figure 5 post-processing convention, but
primary evidence does not authorize asserting or silently applying it. The
public arXiv v1 and v2 figures are unchanged, a primary follow-up repeats the
canonical UV density without such a factor, and the bounded primary-source
audit found no published erratum. The full map, critical locator, Figure 5
fit, DOP853 cross-check, result/model card, and all Git/public actions remain
paused.

### C3b recommendations

- **R1 -- approve the selected charged point as provisional technical
  evidence.** This accepts solver behavior, not a scientific result.
- **R2 -- accept the density mismatch as a contract hard stop.** Do not
  rescale either the canonical density or the source anchors silently.
- **R3 -- authorize only a prospective density-dictionary repair contract.**
  Separate `rho_canonical` from an explicitly unverified
  `rho_source_figure5`; either
  seek author/raw-code clarification or retain Figure 5 only as a topology and
  shape target under a declared unverified plotting dictionary. Return before
  resuming the map.
- **R4 -- preserve every wider closure.** Phase 5C, free energy/coexistence,
  private-code transfer, result/model-card acceptance, commit, push, pull
  request, merge, tag, release, and branch deletion remain closed.

### C3b response paths

- **A -- approve all recommendations:** accept R1--R4 and prepare only the C3b
  repair contract.
- **B -- approve selected items:** name the approved recommendations.
- **C -- request revision or evidence:** identify the derivation or check
  needed.
- **D -- status walkthrough only:** discuss the hard stop without opening C3b.
- **E -- custom response:** provide another bounded instruction.

**Recommended path: A.** It preserves the correct charged solver and canonical
thermodynamics while treating the unexplained Figure 5 normalization as an
explicit source ambiguity rather than hiding it in code.

### C3b owner disposition -- 2026-08-22

Xin-Yi Liu selected **Option A** and approved R1--R4. This accepts the selected
charged point only as provisional technical evidence, preserves the canonical
density and the Figure 5 mismatch as an explicit hard stop, and opens only the
prospective density-dictionary repair contract followed by a mandatory owner
return before any charged map is resumed.

It does not accept a Phase 5B numerical result or model card and does not open
the full map, Figure 5 scan, Phase 5C, free-energy/coexistence work, private-code
transfer, commit, push, pull request, merge, tag, release, or branch deletion.
Every wider scientific, Git, release, and disclosure boundary remains closed.

## C3b prospective density-dictionary repair -- 2026-08-22

### What succeeds at zero density and what changes at finite density

At `mu = rho = 0`, the regular Maxwell solution is identically `Phi = 0`.
The gauge kinetic function therefore drops out of the background equations,
all electric backreaction terms vanish, and the charge-density dictionary is
multiplied by zero. A neutral thermodynamic solution can consequently be
correct without testing any finite-density normalization.

Finite density is not only a different endpoint value for `Phi`. It introduces
a nonzero conserved canonical momentum and the backreaction terms

```text
exp(-2 A) f_EMD Phi'^2 = q^2 exp(-4 A)/f_EMD
```

in the blackening, scalar, constraint, and horizon equations. It also requires
the additional holographic dictionary that converts the horizon electric field
to the UV coefficient and then to the boundary density. The present charged
solver succeeds in both the backreacted background and the chemical-potential
quadrature. The conflict occurs only in the last comparison between the
canonical density and the ordinate printed in source Figure 5.

### Source re-derivation

In the source radial gauge, let

```text
a = phi_A^(1/nu),
Q_G = f_H Phi_1,
Phi = Phi_0^far + Phi_2^far exp(-2 alpha) + ... .
```

The source gives

```text
A_-1^far = 1/sqrt(h_0^far),
Q_G = -2 Phi_2^far/[L sqrt(h_0^far)],
tilde Phi_2 = Phi_2^far/[a^3 sqrt(h_0^far)],
rho = -tilde Phi_2/kappa^2.
```

Combining these equations cancels `h_0^far` exactly:

```text
rho = L Q_G/(2 kappa^2 a^3).
```

Since `q = Q_G/a^3` is the same conserved flux in the UV-normalized inward
conformal coordinate, the unique published dictionary is

```text
rho_canonical = L q/(2 kappa^2) = q/2
```

for the source choice `L = kappa = 1`. The independent source identity
`Q_G = (4 pi/L) rho/s` gives the same result. There is no remaining factor of
`h_0^far`, `phi_A`, `L`, `kappa`, or `f_H` that can be added consistently.

The direct same-author follow-up, arXiv:1108.2029, repeats
`rho = -Phi_(2)/kappa^2`. The later same-author review arXiv:1304.7794 writes
the UV expansion explicitly as

```text
Phi(r) = mu L - rho L^2 kappa^2/r^2 + ...
```

and republishes byte-identical copies of all three Figure 5 panels. No APS
erratum, author correction, public raw table, or public numerical program that
clarifies a different plotting convention was located. Absence of such a
record does not prove how the private plotting workflow was implemented.

### Independent HoloForge reconstruction

At `(phi_H, eta, N) = (4.84, 0.40, 150)`, reconstruct `Phi` from the solved
background and the Maxwell equation, with only `Phi(z_H) = 0` imposed. This
separate calculation gives

```text
mu_reconstructed       = 0.8056545697763529,
-Phi_2_reconstructed   = 1.3368309000815293,
q/2                    = 1.3368309000815297,
relative UV difference = 3.32e-16,
normalized Gauss drift = 1.78e-8.
```

The independently reconstructed source identity `Q_G = 4 pi rho/s` also gives
`rho = 1.3368309000815295`. Coordinate round trips, the unit scalar source,
`f(0) = 1`, horizon `eta`, and the Maxwell integral agree independently. This
rules out a HoloForge finite-density solve, boundary-condition, radial-sign,
Gauss-flux, `q <-> Phi_2`, or UV-rescaling defect at the selected point.

### Candidate-normalization disposition

| Candidate | Disposition |
|---|---|
| `rho = q/2` | **Retain as canonical.** Required independently by the source algebra, UV tail, thermodynamic identity, and reconstructed Maxwell field. |
| missing `h_0^far` or `phi_A` factor | **Reject.** The factors cancel or are already contained in the UV-normalized `q`. |
| different constant `L`, `kappa`, or U(1) scale | **Reject for this benchmark.** It changes the declared model dictionary; `L = kappa = 1` and `f(0) = 1` are explicit source choices. |
| baryon versus quark convention | **Reject.** It would give a factor of three and require the conjugate inverse change in `mu`, which already agrees. |
| rounded `lambda` scales | **Reject.** Their product mismatch changes density by only `1.00605`, not by about `7.4`. |
| `rho_candidate = q/(2 f_H^2)` | **Diagnostic hypothesis only.** It nearly matches the rounded critical density but contradicts `Q_G = f_H Phi_1` and is not a constant rescaling. |

At the selected point,

```text
f_H                           = 0.3675487085,
rho_canonical/f_H^2           = 9.8957034785,
source rho_c                  = 9.9022,
relative one-point difference = 6.56e-4.
```

Across five nearby points the factor `1/f_H^2` varies from `4.59` to `11.95`.
Using it would therefore change the curve shape and susceptibility rather than
merely relabel an axis. The close critical-point match is evidence for a
possible hybrid source post-processing relation `Q_G = Phi_1/f_H` in place of
the published `Q_G = f_H Phi_1`, but one rounded point cannot establish that
private implementation history. It must not be promoted to a physical density
or fitted from Figure 5.

### Prospective semantic and acceptance repair

If the owner later authorizes implementation, apply all of the following as
one prospective change:

1. Keep the solver output named `rho_canonical_BH` and defined only as `q/2`.
2. Relabel the digitized Figure 5 ordinate as `rho_source_figure5`, not
   `rho_canonical_BH`; this records what the public artwork displays without claiming its
   equality to the canonical density.
3. Preserve the extracted Figure 5 paths and hashes, but mark their use in a
   quantitative density gate as challenged until the dictionary is resolved.
4. Split Figure 5 verification into a source-independent topology gate
   (single-valued above, vertical critical tangent, multivalued below) and a
   separately blocked ordinate-agreement gate. A topology pass is not a
   canonical-density reproduction of the published figure.
5. Permit `q/(2 f_H^2)` only as an explicitly named, unverified diagnostic
   column. It cannot affect continuation, fitting, critical-point location,
   acceptance, or physical-unit output.
6. Require a fresh owner return after the bounded charged map reports both the
   canonical topology and the diagnostic comparison. Do not infer that a
   visually similar curve validates the hidden source dictionary.

This repair resolves the HoloForge-side question: the finite-density solver
and canonical density are internally consistent. It cannot reconstruct an
unpublished private plotting operation. The scientifically honest remaining
state is therefore a **source-ordinate ambiguity**, not a numerical-solver
failure.

### C3b-repair recommendations

- **S1 -- approve the canonical/source-axis separation.** Keep `q/2` as the
  only physical density and relabel Figure 5 anchors prospectively.
- **S2 -- approve the split verification target.** Reproduce Figure 5 topology
  in canonical variables, while keeping numerical ordinate agreement blocked.
- **S3 -- retain the inverse-`f_H^2` quantity only as a non-inferential
  diagnostic.** It may help identify the private plotting convention but may
  not enter any scientific gate.
- **S4 -- authorize the bounded charged map only after S1--S3 are implemented
  and tested.** The map must return to the owner before result/model-card or
  any Git/public action.
- **S5 -- preserve every wider closure.** Phase 5C, free energy/coexistence,
  author contact, private-code transfer, result acceptance, commit, push, pull
  request, merge, tag, release, and branch deletion remain closed.

### C3b-repair response paths

- **A -- approve all recommendations:** approve S1--S5, implement the narrow
  semantic repair and tests, then run only the bounded charged map and return.
- **B -- approve selected items:** name the approved recommendations.
- **C -- request revision or more evidence:** keep the map paused.
- **D -- status walkthrough only:** discuss the diagnosis without resuming.
- **E -- custom response:** provide another bounded instruction.

**Recommended path: A.** It preserves the source-derived physical density,
still lets HoloForge test the phase-structure topology that motivated Figure 5,
and prevents an unexplained plotting ordinate from being silently converted
into model physics.

### C3b-repair owner disposition -- 2026-08-22

Xin-Yi Liu selected **Option A** and approved S1--S5. This opens only the
narrow semantic repair above, its focused tests, and the previously frozen
`9 x 9` then `13 x 13` charged-background map at `N = 80` on
`phi_H in [4.2, 5.5]`, `eta in [0.30, 0.50]`. The map must report canonical
topology using `rho_canonical_BH`; any comparison involving
`rho_source_figure5` remains blocked, and `rho_canonical_BH/f_H^2` remains a
non-inferential diagnostic that cannot steer the solve or pass a gate.

This disposition does not accept a Phase 5B numerical result or model card.
It does not open the outer-temperature fit, source-anchor RMS comparison,
DOP853 five-state campaign, Phase 5C, free energy or coexistence work, author
contact, private-code transfer, commit, push, pull request, merge, tag,
release, or branch deletion. A mandatory owner return follows the bounded map
whether it succeeds or reaches a frozen hard stop.

## C3b-repair bounded-map return -- 2026-08-22

The owner-authorized map was run exactly twice on the frozen patch: the final
repeat added the independent Maxwell reconstruction without changing the
solver, bounds, continuation order, or density definition. The repeat
completed the `9 x 9` survey and `13 x 13` refinement at `N = 80`, yielding
81/81 and 169/169 stored states. Every state reports maintained-library
success and passes the implemented point gates. The 31.79-second local run is
provisional AI-generated evidence; no Phase 5B result or model card is thereby
accepted.

On the refinement grid, the physical ranges are

```text
T_BH                 in [0.4848479773, 0.6386016791]
mu_BH                in [0.5726419586, 1.1064858362]
q                    in [0.7914632875, 7.5089499548]
rho_canonical_BH=q/2 in [0.3957316438, 3.7544749774]
f_H                  in [0.1666217885, 0.7890832575].
```

The maximum final scaled nonlinear residual is `3.40e-9`; the maximum
independently evaluated physical-equation residual is `4.54e-7`, including a
maximum reconstructed Maxwell-equation residual of `3.83e-8`. The maximum
Einstein-constraint and boundary residuals are each `8.54e-9`, normalized
Gauss-flux drift is `5.89e-8`, chemical-potential reconstruction error is
`1.11e-12`, and the independent UV `-Phi_2=q/2` error is `1.71e-15`.

For the topology diagnostic, each fixed-`phi_H` row has monotone temperature
as `eta` varies. The analysis linearly interpolates in `eta` at fixed
temperature and then applies finite differences along the 13 `phi_H` rows.
The resulting provisional sign-change table is

| `T_BH` | sign changes of `d mu_BH / d rho_canonical_BH` | minimum slope | interpretation |
| --- | ---: | ---: | --- |
| `0.5600000000` | 2 | `-3.70e-3` | local S-shaped path with a negative-susceptibility middle segment |
| `143/252 = 0.5674603175` | 0 | `+1.19e-4` | near coalescence, but the critical tangent is not resolved as zero |
| `0.5750000000` | 0 | `+4.07e-3` | local single-valued positive-susceptibility path |

The parameter-map Jacobian changes sign on the patch; the smallest sampled
absolute value is `1.43e-4` at `(phi_H,eta)=(4.85,0.40)`. This proximity does
not replace the frozen critical-derivative and refinement gates.

As a separate interpolation diagnostic, a bicubic tensor spline on the
13-by-13 map gives

```text
(phi_H, eta, T_BH, mu_BH, rho_canonical_BH)
= (4.8005928, 0.4011273, 0.5673573, 0.8042108, 1.4171485).
```

At that spline-defined temperature minus `0.005`, at the candidate, and plus
`0.005`, the interpolated paths have two, one, and zero spinodal roots. The
formal one-root tangent is imposed by the spline critical search and is a
useful localization diagnostic; it does not override the direct
`143/252` minimum-slope result, establish a resolved critical tangent, or pass
the frozen critical-derivative and path-integrity gates.

All three extracted paths use the full 13-row range and contact both
`phi_H=4.2` and `phi_H=5.5`. Gate 6 requires reported paths to remain off all
scan boundaries, and the frozen route explicitly makes boundary contact a
hard stop. Therefore the qualitative below/above topology is provisional,
the critical tangent and full canonical topology gate do **not** pass, and no
critical-point result may be claimed. Expanding the map is outside the current
authorization.

The inverse-`f_H^2` diagnostic spans `[4.1468822732, 21.3072334271]`; it never
entered a solve, interpolation target, topology decision, or acceptance gate.
The absolute comparison to `rho_source_figure5` remains blocked and was not
evaluated. The complete per-state record remains local and unreviewed; no
tracked evidence bundle or public numerical result is created by this return.

## C3c explicit-Maxwell and coverage-extension owner disposition -- 2026-08-22

After the C3b-repair return, Xin-Yi Liu selected **Option A** and approved the
complete next bounded gate. The approval preserves the flux-reduced charged
solver as the primary route and opens two prospective verification actions in
this order.

First, add a secondary Chebyshev formulation in which `Phi` is an explicit
collocation unknown and the second-order Maxwell equation is solved together
with the warp, blackening, and scalar equations. This route must not replace,
tune, or seed-select the primary formulation. It uses `Phi(z_H)=0` and the
same horizon `eta` normalization so that the boundary chemical potential
emerges from the solve. The Einstein/Hamiltonian equation remains an
independent constraint, because the Bianchi identity makes it redundant with
the complete dynamical system rather than an additional freely collocatable
equation.

The frozen control states are

```text
neutral control:        (phi_H, eta, N) = (4.84, 0.00, 80)
critical neighborhood:  (phi_H, eta, N) = (4.84, 0.40, 80 and 120)
high-charge coverage:   (phi_H, eta, N) = (7.00, 0.50, 80)
```

At every explicit-`Phi` control state, the final scaled collocation residual
must be at most `1e-6`; each of the four independently evaluated physical
equations and the Einstein constraint must be at most `1e-5`; endpoint and
undivided horizon residuals must be at most `1e-7`; and normalized Gauss-flux
drift must be at most `1e-7`. Between the explicit and flux-reduced routes,
relative differences in `(T, mu, s, rho_canonical)` must be at most `5e-6`.
For each interpolated field, use
`max(abs(explicit-primary))/(1+max(abs(primary))) <= 2e-5`; compare the
explicit potential to the separately reconstructed primary potential with the
same norm. The `N=80 -> 120` critical-neighborhood observable change must
remain below the existing `2e-3` convergence ceiling. A singular endpoint,
new seed family, tolerance change, or route disagreement is a mandatory
return rather than permission to modify the primary solver.

Second, only if the formulation comparison passes, extend the canonical map
without changing the density dictionary:

```text
coverage patch:
  phi_H in [3.0, 7.0]
  eta   in [0.30, 0.50]

map grids at field degree N = 80:
  deterministic 17 x 13 survey, then 33 x 17 refinement
```

The continuation order, point gates, canonical variables, fixed-temperature
targets `T_BH = 0.56`, `143/252`, and `0.575`, and the separation between
direct finite-difference and smooth-interpolation diagnostics remain frozen.
Every stored state must pass the existing nonlinear, four-equation,
constraint, boundary, Gauss, Maxwell-reconstruction, chemical-potential, and
UV-tail gates. If a reported isotherm still touches any `phi_H` or `eta` scan
boundary, the coverage gate hard-stops again. No adaptive widening, random
restart, source-point deletion, hidden density transformation, or fit to
`rho_source_figure5` is authorized.

The approved review deliverable is a standard HoloForge PDF packet because
this gate compares two equation formulations, their boundary conditions and
residuals, and a multi-curve topology figure. The packet must be compiled
twice, rendered page by page, and visually checked. It remains a review aid,
not scientific acceptance.

This disposition does not authorize a Figure 5 absolute-ordinate claim,
critical-point acceptance, Phase 5C, free-energy or coexistence work, private
program transfer, commit, push, pull request, merge, tag, release, branch
deletion, or any change to the released Phase 5A benchmark. A mandatory owner
return follows success or the first frozen hard stop.

## C3c explicit-Maxwell and coverage-extension return -- 2026-08-22

The simultaneous explicit-`Phi` prerequisite passed without changing the
primary flux-reduced solver. To avoid the DGR field's exceptionally flat UV
tail, the secondary route collocates the regular coefficient `e(u)` in

```text
Phi(u) = mu - u^(2/nu) e(u),
K(u)   = 2 e(u) + nu u e'(u),
D Phi  = -u^(2/nu) K(u).
```

Its nonlinear vector is `(h,c,p,e,log(x_H),mu)`. The four dynamical equations
use the electric backreaction reconstructed directly from `e`; the
Einstein/Hamiltonian equation is evaluated independently. The square system
replaces endpoint rows with `h(0)=1`, `h(1)=0`, the analytic warp UV value,
unit scalar source, Maxwell UV regularity, the `eta`-fixed horizon electric
flux, `Phi(1)=0`, and the target `phi_H`. The primary solution supplies only a
deterministic starting vector.

The exact frozen controls give

| `(phi_H,eta,N)` | scaled solve | maximum four-EOM residual | constraint | boundary | Gauss drift |
| --- | ---: | ---: | ---: | ---: | ---: |
| `(4.84,0.00,80)` | `1.04e-11` | `1.95e-10` | `7.91e-11` | `5.81e-11` | `0` |
| `(4.84,0.40,80)` | `7.62e-12` | `2.69e-8` | `4.87e-10` | below `1e-7` | `7.04e-12` |
| `(4.84,0.40,120)` | `2.75e-11` | `3.87e-10` | `3.08e-11` | below `1e-7` | `2.31e-13` |
| `(7.00,0.50,80)` | `4.22e-11` | `2.56e-6` | `6.03e-8` | `6.03e-8` | `1.34e-9` |

At the central `N=80` point, the simultaneous and flux-reduced routes differ
by `1.54e-12` in the normalized background-field norm, `1.44e-12` in `q`,
and `2.20e-12` in `mu`. Their `N=80 -> 120` thermodynamic changes are all
below `5.7e-11`. At the high-charge control, the corresponding background,
`q`, and `mu` differences are `1.41e-11`, `2.95e-11`, and
`1.2501e-10`.
All eleven focused tests pass. This supports the analytic Maxwell reduction
as a valid primary formulation and the explicit-field route as a genuinely
simultaneous secondary check; it does not make the Einstein constraint a
fifth independent collocation equation.

The coverage map then began on the exact frozen `17 x 13` survey. It stored
171 of 221 survey states: 170 pass and one fails. The first failure occurred
at

```text
(phi_H,eta,N) = (6.25, 0.4833333333333333, 80).
```

At this state the scaled nonlinear residual is `5.66e-11`, the maximum
four-equation residual is `1.14e-6`, the constraint and boundary residual are
`2.32e-8`, the reconstructed-Maxwell residual is `7.95e-8`, the relative
chemical-potential reconstruction error is `6.76e-13`, and the UV
`-Phi_2=q/2` error is `7.82e-16`; all of these pass their frozen rows. The
normalized reconstructed Gauss-flux drift is instead `1.4251413e-7`, which
exceeds the unchanged `1e-7` ceiling by a factor `1.425`. The driver therefore
stopped after `22.07` seconds exactly as required.

The remaining 50 survey states and all 561 refinement states were not run.
No fixed-temperature path, boundary-contact test, smooth critical candidate,
or Figure 5 topology is evaluated from the incomplete map. This is a
near-threshold numerical-diagnostic hard stop, not evidence that the EMD
background equations failed and not permission to weaken the Gauss gate after
seeing the miss. The canonical density remains `q/2`; the source Figure 5
ordinate remains blocked and was not compared.

The standard PDF review packet records the simultaneous formulation, row
count, control-state comparison, incomplete-map evidence, hostile criticism,
and next owner decisions. All Phase 5C, source-density, free-energy,
coexistence, Git, public, and release actions remain closed.

## C3d stopped-state conditioning audit return -- 2026-08-22

The owner-authorized C3d audit replayed the exact deterministic `17 x 13`
survey continuation through its first stopped state,

```text
(phi_H, eta) = (6.25, 0.4833333333333333),
```

and recomputed that same state at `N = 120`. The primary solver, continuation
history, integration settings, `1e-7` Gauss ceiling, density dictionary, and
scientific claim were unchanged. The already-approved UV-factorized
explicit-`Phi` formulation was then evaluated on the same background as an
independent conserved-flux diagnostic.

| resolution and route | normalized Gauss drift | maximum four-EOM residual | constraint/boundary | result |
| --- | ---: | ---: | ---: | --- |
| `N=80`, reconstructed `Phi` | `1.4251412979e-7` | `1.14e-6` | `2.32e-8` | misses only Gauss |
| `N=80`, explicit `Phi` | `6.6899574769e-10` | `1.1547973102e-6` | `2.5442020046e-8` | passes |
| `N=120`, reconstructed `Phi` | `1.4274904166e-7` | below frozen ceiling | below frozen ceiling | misses only Gauss |
| `N=120`, explicit `Phi` | `1.3472556404e-13` | `5.2840221088e-10` | `4.1318060084e-11` | passes |

The reconstructed Maxwell-equation residuals are `7.9496e-8` and
`7.9898e-8` at `N=80` and `N=120`, respectively, so they also pass. From
`N=80` to `N=120`, every primary thermodynamic observable changes by less
than `3e-9`. Explicit-primary field, charge, and chemical-potential
differences are between `1e-11` and `1e-13` at the refined state.

The reconstructed drift is localized to the two lowest independent-grid
samples at both resolutions. There the local interpolant differentiates a
potential of magnitude approximately `1.195` across a variation of only
`8.03e-7`, a conditioning ratio of approximately `1.49e6`. Raising the
spectral resolution therefore leaves the reconstructed value on the same
`1.43e-7` floor, while the simultaneous conserved-flux metric improves by a
factor of approximately `4966`. This evidence localizes the stop to numerical
differentiation of the reconstructed potential near the UV boundary; it does
not indicate a background, thermodynamic, or Maxwell-equation failure.

The audit also found that the C3c map driver's implemented point-gate list did
not include the contract's Noether-charge drift and horizon-identity check.
The 170 stored states passed every gate that the driver evaluated, but they
cannot be called complete frozen-point passes. Their stored summaries do not
contain the full profiles needed to add the missing check retrospectively.
Any scientifically valid continuation must therefore implement

```text
Q_N^(z) = exp(3 A) h' + q Phi,
Q_N^(z) = -2 kappa_5^2 T s at the horizon,
```

retain the frozen `1e-6` normalized-drift ceiling, and rerun the entire
`17 x 13` survey and `33 x 17` refinement from the first state.

No diagnostic semantics were changed and no map state was resumed under C3d.
The smallest prospective repair is to retain the primary flux-reduced solver
and every numerical ceiling, make the already-validated explicit-`Phi`
conserved flux the authoritative Gauss acceptance metric at every map state,
and retain reconstructed-`Phi` drift as a recorded non-gating conditioning
monitor. This is stronger than relaxing the threshold, but it changes which
independent diagnostic carries the frozen Gauss gate and therefore requires a
new owner decision.

### C3e owner recommendations

- **T1 -- accept the conditioning classification.** Record the stopped state
  as a reconstructed-potential differentiation floor, not a failed EMD
  solution. **Recommendation: approve.**
- **T2 -- authorize the map-wide Gauss diagnostic repair.** At every rerun
  state, require explicit-`Phi` conserved-flux drift at or below `1e-7`, the
  already-frozen explicit equation/constraint/endpoint rows, and
  explicit-primary field and thermodynamic agreement. Preserve the old
  reconstructed drift as a non-gating conditioning monitor. Do not change the
  primary solver or any ceiling. **Recommendation: approve.**
- **T3 -- restore the missing Noether gate before rerunning.** Require
  normalized Noether drift at or below `1e-6` and the horizon identity, then
  rerun both maps from the first state with the existing continuation order,
  first-failure rule, and 45-minute ceiling. **Recommendation: approve.**
- **T4 -- continue through the already-frozen completion gates if the fresh
  map passes.** Proceed in order through boundary-free canonical topology,
  direct critical conditions and independent Jacobian, `N=80,120,150`
  critical/five-state refinement, the five-state fully coupled outward-`B=0`
  DOP853 comparison, and public verifier/package validation. Return at the
  first new scientific or numerical failure. **Recommendation: approve.**
- **T5 -- preserve the claim and disclosure boundary.** Keep the absolute
  `rho_source_figure5` ordinate blocked; do not rescale density or infer free
  energy, coexistence, Phase 5C, or empirical-QCD validation. Git integration
  and release remain later owner gates. **Recommendation: approve.**

### C3e owner response paths

- **A -- approve all recommendations:** open T1--T5 and continue Phase 5B
  through its already-frozen gates until completion or the first new return.
- **B -- approve selected items:** name the approved T-items.
- **C -- request revision or more evidence:** keep calculation paused.
- **D -- status walkthrough only:** discuss the audit without changing scope.
- **E -- custom response:** provide another bounded instruction.

**Recommended path: A.** It preserves every tolerance and scientific claim,
replaces a demonstrably ill-conditioned derivative with an independently
solved conserved flux, restores an omitted contract gate, and requires a
fresh auditable map rather than selectively rescuing one failed point.

## C3e owner disposition -- 2026-08-23

Xin-Yi Liu selected **Option A** and approved T1--T5. The implementation may
therefore make the UV-factorized explicit-`Phi` conserved flux the
authoritative Gauss acceptance diagnostic, preserve reconstructed-`Phi` drift
as a non-gating conditioning monitor, add the missing Noether drift and
horizon identity, and rerun the complete `17 x 13` survey and `33 x 17`
refinement from their first states. If those maps pass, work may continue
through the already-frozen topology, direct critical-point, resolution,
five-state DOP853, verifier, artifact, and package gates until completion or
the first new scientific or numerical stop.

The owner also noted that `1e-6` is a familiar practical residual scale in
their Mathematica calculations and may be appropriate if the charged problem
still cannot be resolved at `1e-7`. This is recorded as a **conditional
fallback**, not an immediate threshold change. The authoritative explicit
Gauss gate remains `1e-7` for the fresh run. A `1e-6` Gauss fallback may be
activated only if a new state:

1. passes the nonlinear, four-equation, constraint, endpoint, density,
   explicit-primary field, and thermodynamic agreement gates;
2. has its boundary conditions checked explicitly;
3. retains explicit Gauss drift above `1e-7` but at or below `1e-6` under a
   fixed `N=80 -> 120` refinement audit; and
4. shows a stable conditioning or discretization floor rather than a growing
   physical-equation disagreement.

If activated, both the original `1e-7` result and the owner-authorized `1e-6`
classification must be recorded; no other tolerance changes, point deletion,
or state-dependent threshold are authorized. Drift above `1e-6`, loss of
convergence, a boundary-condition failure, or worsening with resolution
remains a mandatory hard stop.

Before the fresh map starts, the direct Noether diagnostic is fixed on 80
logarithmically spaced interior samples in `v=(z/z_H)^2` over
`0.1 <= v <= 0.98`. It evaluates `exp(3 A) h_z + q Phi` from the independently
differentiated explicit-`Phi` profile and retains the `1e-6` normalized-drift
ceiling. The UV asymptotic layer is excluded because differentiating
`h=1+O(v^2)` there amplifies binary64 roundoff by `1/v`; the horizon is checked
separately against `Q_N=-2 kappa_5^2 T s` at `1e-12`. An integrated
blackening-flux reconstruction may be recorded as a conditioning monitor, but
cannot replace the direct differentiated-field gate because doing so would
make conservation nearly built into the diagnostic.

This disposition does not authorize the blocked source-density ordinate,
density rescaling, free energy, coexistence, Phase 5C, empirical-QCD claims,
commit, push, pull request, merge, tag, release, or branch deletion.

### C3f reconstructed-Maxwell conditioning amendment -- 2026-08-23

The first C3e smoke run retained the previously implemented `1e-7` ceiling
for the primary route's reconstructed-`Phi` Maxwell-equation residual. The
required high-charge endpoint `(phi_H,eta)=(7.0,0.5)` returned
`1.5455179747e-7` at `N=80`, while every explicit-`Phi` equation, constraint,
endpoint, authoritative Gauss, Noether, and route-agreement gate passed.

In response to the owner's instruction that a globally justified `1e-6`
residual tolerance may be used if the charged problem remains limited by an
overly strict numerical row, the endpoint was repeated without changing the
solver at `N=80,120,150`. The reconstructed-Maxwell residuals were

```text
N=80:   1.5455179747e-7
N=120:  1.2588895382e-7
N=150:  1.2322021237e-7
```

while the reconstructed Gauss monitor stayed on the same `O(2e-7)` floor,
the authoritative explicit Gauss drift improved from `1.3432404e-9` to
`O(1e-13)`, primary boundary residuals remained below `2.71e-8`, all explicit
equation and boundary rows passed, and explicit-primary thermodynamic
differences remained below `9.74e-10`. The physical observables were stable
under both refinements.

This evidence activates one prospective **global `1e-6` ceiling only for the
primary reconstructed-`Phi` Maxwell-equation residual**. Its measured value
remains recorded at every state. The explicit Maxwell-equation ceiling stays
`1e-5`, the authoritative explicit Gauss ceiling stays `1e-7`, the direct
Noether ceiling stays `1e-6`, and every other threshold is unchanged. No
state-specific rescue or point deletion is allowed; a reconstructed-Maxwell
residual above `1e-6`, worsening resolution behavior, boundary failure, or
explicit-route disagreement is a hard stop. This amendment opens the fresh
C3e map but no Git, release, source-ordinate, free-energy, coexistence, or
Phase 5C action.

## C3e fresh-map return and C3g owner gate -- 2026-08-23

The complete fresh C3e calculation reran the `17 x 13` survey and `33 x 17`
refinement from their first states with the explicit-`Phi` Gauss gate, direct
Noether diagnostic, and C3f conditioning amendment active globally. It stored
and passed all `221 + 561 = 782` requested states in `289.7547` seconds. No
state failed and no solver or driver checksum changed during the run.

The largest refinement-grid gate values were:

| diagnostic | maximum | ceiling or role |
| --- | ---: | --- |
| scaled nonlinear residual | `6.25008e-8` | `1e-6` |
| maximum primary physical equation | `2.45105e-6` | `1e-5` |
| reconstructed-`Phi` Maxwell equation | `2.08577e-7` | C3f global `1e-6` |
| primary constraint / boundary | `5.72241e-8` / `5.05850e-8` | `1e-5` / `1e-7` |
| explicit Gauss drift | `1.34324e-9` | authoritative `1e-7` |
| direct Noether drift / horizon identity | `2.54205e-7` / `4.13419e-16` | `1e-6` / `1e-12` |
| maximum explicit physical equation | `2.56349e-6` | `1e-5` |
| explicit boundary | `6.02903e-8` | `1e-7` |
| explicit-primary thermodynamic difference | `1.99434e-10` | `5e-6` |
| explicit-primary electric-potential difference | `5.65277e-11` | `2e-5` |

The survey's reconstructed-Maxwell maximum is `2.11417e-7`. Thus the scoped
`1e-6` ceiling retains a factor greater than `4.7` of map-wide headroom; it is
not needed by the explicit Gauss, explicit equation, boundary, Noether, or
cross-route acceptance rows. The reconstructed Gauss value remains a
non-gating conditioning monitor and reaches `3.04806e-7`.

### Direct topology returned by the completed map

Linear interpolation in `eta` on each fixed-`phi_H` row followed by direct
finite differences along the refinement rows gives:

| `T_BH` | slope-sign changes | minimum `d mu / d rho` | classification |
| ---: | ---: | ---: | --- |
| `0.5600000000` | 2 | `-3.77430e-3` | local S-shaped path |
| `143/252` | 0 | `+3.80239e-4` | positive-susceptibility path |
| `0.5750000000` | 0 | `+4.29017e-3` | positive-susceptibility path |

The two `T=0.56` spinodal estimates are

```text
(phi_H, eta, mu_BH, rho_canonical_BH)
=(4.5515094, 0.4239265, 0.8280733, 2.1028328)
=(5.0949420, 0.3994959, 0.8310605, 0.9265319)
```

The refinement spline diagnostic localizes

```text
(phi_H, eta, T_BH, mu_BH, rho_canonical_BH)
=(4.8006670, 0.4011271, 0.5673554, 0.8042172, 1.4169975).
```

This remains a localization diagnostic. It does not satisfy the later direct
critical-derivative, Jacobian-refinement, `N=80,120,150`, or DOP853 gates.

Every complete constant-temperature contour is an open curve joining
`eta=0.50` to `eta=0.30`. The three frozen direct paths contact those edges at
chemical potentials

```text
T=0.56:       1.0096813 and 0.7370913
T=143/252:    1.0283787 and 0.7212522
T=0.575:      1.0477598 and 0.7046173.
```

The implemented Gate 6 therefore correctly returned
`hard-stop-reported-path-contacted-scan-boundary`. This is the first new
mandatory return under C3e Option A. It is separate from the fully passing
782-state numerical map.

The completed tensor map has strictly negative direct temperature secants in
both parameter directions. Consequently, these isotherms cannot close inside
the current rectangle; blindly extending `eta` only relocates their endpoint
contacts. The targeted spinodals and smooth candidate are nevertheless at
least six refinement cells from the parent-map parameter boundaries. This
supports a local critical-neighborhood analysis but not a claim that every
global branch or lower-temperature Jacobian-zero locus is enclosed.

### Source-backed Figure 5 reporting windows

The approved reference records already determine finite chemical-potential
anchor hulls without using the unresolved density conversion:

| source panel | frozen `mu_BH` reporting window |
| --- | ---: |
| above `T_c` | `[0.763360248, 0.786922967]` |
| at `T_c` | `[0.798016580, 0.810528785]` |
| below `T_c` | `[0.804842255, 0.815169234]` |

All full-contour parameter-boundary contacts lie outside their corresponding
source window. These windows imply no bound on `rho_canonical_BH` and do not
resolve `rho_source_figure5`.

Changing only the boundary-contact rule is insufficient. The `T=0.56`
spinodal chemical potentials, `0.8280733` and `0.8310605`, lie outside the
below-`T_c` source window. The paper does not publish the outer-panel
temperature. A read-only diagnostic of the already completed map finds that
temperatures near `T_BH=0.5655` move the two folds to approximately
`0.8104547` and `0.8107552`, but this temperature was inspected after the
return and cannot enter acceptance without a prospective owner amendment.
The stored source values `0.810497383` and `0.810850854` are discrete-anchor
extrema, not independently extracted continuous-path spinodals. Their midpoint
`0.8106741185` may localize one representative below-panel temperature, but
their separation cannot validate the model fold shape under the much wider
historical `2e-3` horizontal comparison scale.

### C3g owner recommendations

- **U1 -- accept the pointwise numerical map and scoped conditioning
  classification.** Record 782/782 point gates as passing and retain the
  C3f `1e-6` ceiling only for the primary reconstructed-`Phi` Maxwell row.
  Keep every explicit gate unchanged. **Recommendation: approve.**
- **U2 -- localize the Figure 5 claim and freeze its horizontal windows.**
  Test only the connected near-critical component within the three
  source-backed `mu_BH` windows above. State explicitly that this is not a
  global-isotherm or absolute-density claim. **Recommendation: approve.**
- **U3 -- replace Gate 6 with a prospectively buffered window rule.** Clip
  the continuation of the component containing the independently located
  direct critical root to each frozen `mu_BH` window. The below continuation
  must uniquely contain both folds and the above continuation must remain the
  same branch; zero or multiple eligible components is a hard stop. Require
  exactly two simple transverse `mu_BH`-window crossings, no parameter-edge
  contact inside the clipped component, and at least four refinement-grid
  intervals between every crossing/fold/root and every parent-map edge. Freeze
  the resulting inner guard as `phi_H in [3.5,6.5]`,
  `eta in [0.35,0.45]`; repeat with its four sides moved inward and outward by
  one fine interval (`Delta phi_H=0.125`, `Delta eta=0.0125`). Component
  identity, fold count and sign pattern, and root ordering must agree on the
  `17 x 13` and `33 x 17` maps, under both guard perturbations, and between
  direct finite differences and the smooth diagnostic; reported feature
  positions may move by at most one refinement interval. Direct conditions
  remain authoritative. Preserve full-contour boundary contacts as reported,
  non-gating coverage diagnostics. **Recommendation: approve.**
- **U4 -- authorize one horizontal-only determination of the unpublished
  below-panel temperature.** First locate `T_c` from the already-frozen direct
  derivative and independent Jacobian conditions. Then, within
  `0.90 <= T_-/T_c <= 0.999`, use one fixed bracketed scalar root solve to
  match the midpoint of the model's two fold chemical potentials to the
  discrete-anchor proxy `0.8106741185`. Freeze `scipy.optimize.brentq` with
  `xtol=1e-10`; no root or more than one sign-changing root is a hard stop.
  Report `T_-` as a one-parameter calibration, not a prediction or the
  paper's unpublished temperature. Record both folds and their separation as
  non-fitted diagnostics; the historical `2e-3` scale may be reported only as
  a horizontal consistency screen and cannot validate fold shape. Do not fit
  `T_+` or any density. Repeat the calibration after each accepted critical
  resolution and report the final-resolution value. **Recommendation:
  approve.**
- **U5 -- continue only in the prospectively fixed order.** Run the direct
  critical/Jacobian and step-refinement gate first, then the calibrated local
  topology gate, `N=80,120,150` critical/five-state checks with the calibration
  repeated, and finally the fully coupled outward-`B=0` DOP853 comparison.
  Return at the first new failure or method change. A pass supports only
  “canonical near-critical topology consistent with Figure 5 over the
  source-backed `mu_BH` windows after one disclosed below-`T_c` calibration.”
  **Recommendation: approve.**
- **U6 -- preserve all scientific, disclosure, and Git closures.** Keep the
  absolute source-density ordinate, global branch completeness, free energy,
  coexistence, Phase 5C, empirical-QCD claims, commit, push, pull request,
  merge, tag, release, and branch deletion closed. **Recommendation: approve.**

### C3g owner response paths

- **A -- approve all recommendations:** open U1--U6 and continue Phase 5B
  through the newly frozen local topology gate and the previously approved
  later gates until completion or the first new mandatory return.
- **B -- approve selected items:** name the approved U-items.
- **C -- request revision or more evidence:** keep Phase 5B paused.
- **D -- status walkthrough only:** discuss the return without changing scope.
- **E -- custom response:** provide another bounded instruction.

**Recommended path: A.** It preserves the original hard stop in provenance,
uses only a source-backed horizontal domain, discloses the one fitted scalar,
adds stability and buffer tests against post-hoc windowing, and does not infer
the unresolved density dictionary or global phase structure.

## C3g owner disposition -- 2026-08-23

Xin-Yi Liu selected **Option A** and approved U1--U6. The complete 782-state
C3e point map and the globally scoped C3f conditioning classification are
therefore accepted as the numerical input to the next gate. The implementation
may replace the full-contour boundary-contact acceptance rule only for the
connected near-critical components inside the three frozen source-backed
`mu_BH` windows, subject to every component-selection, crossing, guard,
resolution, perturbation, and direct-versus-smooth requirement in U3.

The implementation must now proceed in the approved order:

1. locate the direct critical state and verify the independent parameter-map
   Jacobian and step refinement;
2. use that directly located `T_c` in the unique bracketed one-parameter
   below-temperature calibration defined in U4;
3. evaluate the buffered local topology gate on both stored map resolutions
   and guard perturbations;
4. repeat the accepted critical and calibrated representative states at
   `N=80,120,150` under the frozen convergence rules;
5. compare the five selected states with the fully coupled outward-`B=0`
   DOP853 route; and
6. only after all scientific gates pass, complete the verifier, artifacts,
   package, privacy, and final owner-acceptance evidence.

This approval does not identify the calibrated `T_-` with the source's
unpublished temperature and does not turn the discrete-anchor midpoint into a
continuous-path spinodal measurement. A later pass can support only
“canonical near-critical topology consistent with Figure 5 over the
source-backed `mu_BH` windows after one disclosed below-`T_c` calibration.”
The absolute source-density ordinate, global branch completeness, quantitative
fold-shape reproduction, free energy, coexistence, Phase 5C, empirical-QCD
claims, commit, push, pull request, merge, tag, release, and branch deletion
remain closed. Work returns at the first new scientific failure, numerical
failure, or method change not already frozen above.

## C3g direct-critical pass and local-topology return -- 2026-08-23

The owner-approved C3g calculation followed the frozen U5 ordering and first
located the critical state from direct constant-temperature derivatives. At
`N=80`, the three five-point derivative steps
`Delta phi_H=(0.25,0.125,0.0625)` converge to

```text
(phi_H,c, eta_c) = (4.8000914089, 0.4011509185)
(T_c, mu_c, rho_canonical,c)
                 = (0.5673570388, 0.8042116890, 1.4182254432)
(T_c, mu_c)      = (142.973974 MeV, 781.693762 MeV).
```

The largest scaled change from the middle to fine step is `5.33e-6`, after
changes as large as `8.78e-5` from the coarse to middle step. A separate
`Delta phi_H=0.03125` evaluation gives normalized first- and second-derivative
conditions below `7.31e-8`. Direct second-order parameter-map differences at

```text
(Delta phi_H, Delta eta)
=(0.25,1/60), (0.125,0.0125), (0.0625,0.00625)
```

give normalized `J(T,mu)` magnitudes
`(8.42e-4,2.10e-4,5.25e-5)` and normalized isotherm-tangent derivatives
`(1.09e-3,2.71e-4,6.76e-5)`. The independent `J(T,rho)` values remain near
`-1.25`, so canonical density is a nonsingular path coordinate. The complete
C3e primary plus simultaneous-explicit-`Phi` point gate also passes at the
final state. The direct critical subgate therefore passes without changing a
solver or tolerance.

The next calibrated local-topology gate returns two failures:

1. On the `17 x 13` direct row-linear/finite-difference map, the two folds
   coalesce numerically at
   `T_BH=0.5650031108447`, where their common chemical potential is still
   `0.8120646059`. This is `0.0013904874` above the frozen midpoint target.
   The coarse direct map consequently has no admissible `brentq` calibration
   root. The `33 x 17` direct map has one unique root at
   `T_-=0.5654799518161`, with folds `0.8105220546` and `0.8108261824`.
   Both smooth maps also have one root near `T_-=0.5654945`. Thus the U3/U4
   direct cross-resolution fold-count agreement fails.
2. At the frozen above temperature `T_BH=0.575`, the low edge of the source
   window crosses the path at `eta=0.35255` in both smooth maps and at
   `eta=0.35379` and `0.35277` on the direct survey and refinement maps. Each
   crossing is more than four fine intervals from the parent-map edge and is
   inside the nominal and outward guards. It is outside the prescribed inward
   guard `eta >= 0.3625`, however, leaving only one of the two required window
   crossings. The literal U3 inward-guard rule therefore fails.

These are feature-resolution and frozen-domain-selection failures. They do
not depend on the collocation residual tolerance; changing `1e-6`, `1e-5`, or
any explicit-equation ceiling cannot repair them. U5 therefore stops before
the `N=80,120,150` critical/five-state campaign, the fully coupled outward
`B=0` DOP853 route, verifier packaging, or any Git action.

### C3h owner recommendations

- **V1 -- accept the direct critical subgate.** Preserve the direct root,
  step-refinement evidence, independent Jacobian evidence, and passing full
  point gate as completed C3g evidence. **Recommendation: approve.**
- **V2 -- replace the under-resolved direct topology comparison.** Retain the
  `17 x 13` map as coverage and smooth-localization evidence, but do not ask
  its `Delta phi_H=0.25` direct finite differences to resolve folds separated
  by only about `0.22` in `phi_H`. Compare the existing `33 x 17` direct result
  prospectively against a fresh local tensor refinement with
  `Delta phi_H=0.0625`, `Delta eta=0.00625` on
  `[3.375,6.625] x [0.3125,0.4875]`, namely `53 x 29` states; all new states
  must pass the same C3e point gates. Direct finite differences remain
  authoritative and the smooth routes remain diagnostic. **Recommendation:
  approve.**
- **V3 -- repair the guard without weakening the source-window and parent
  buffer tests.** Replace only the inner guard's eta range by the symmetric
  interval `[0.325,0.475]`; its inward and outward eta ranges become
  `[0.3375,0.4625]` and `[0.3125,0.4875]`. Keep the phi guard and perturbations,
  exactly two transverse source-window crossings, the four-parent-cell
  buffer, component identity, fold count/sign, ordering, and one-fine-interval
  feature-stability rules unchanged. **Recommendation: approve.**
- **V4 -- preserve the calibrated claim and sequence.** Repeat the one-scalar
  `T_-` calibration on every accepted direct resolution. If the repaired
  local gate passes, continue to the already frozen `N=80,120,150`, DOP853,
  verifier, artifact, package, privacy, and final owner gates; return at the
  first new failure or method change. **Recommendation: approve.**
- **V5 -- preserve all closures.** Keep the source density, global topology,
  quantitative fold-shape reproduction, free energy, coexistence, Phase 5C,
  empirical-QCD claims, commit, push, pull request, merge, tag, release, and
  branch deletion closed. **Recommendation: approve.**

### C3h owner response paths

- **A -- approve all recommendations:** open V1--V5 and run the prospective
  local refinement and repaired topology gate, then continue in the frozen
  order only if it passes.
- **B -- approve selected items:** name the approved V-items.
- **C -- request revision or more evidence:** keep Phase 5B paused.
- **D -- status walkthrough only:** discuss the return without changing scope.
- **E -- custom response:** provide another bounded instruction.

**Recommended path: A.** It does not waive either failure. It replaces an
under-resolved finite-difference comparison with a finer direct comparison,
makes the guard cover the already-required source-window crossings while
retaining the independent four-cell parent buffer, and leaves every physical,
residual, disclosure, and Git boundary unchanged.

## C3h owner disposition -- 2026-08-23

Xin-Yi Liu selected **Option A** and approved V1--V5. The C3g direct critical
root, physical-derivative refinement, independent parameter-map Jacobian, and
final `N=80` primary plus simultaneous-explicit-`Phi` point gate are accepted
as completed inputs to the repaired local-topology gate.

The next calculation is prospectively fixed as follows:

```text
field degree:              N = 80
local tensor bounds:       phi_H in [3.375, 6.625]
                           eta   in [0.3125, 0.4875]
local tensor shape:        53 x 29 = 1537 states
parameter steps:           Delta phi_H = 0.0625
                           Delta eta   = 0.00625
authoritative comparison:  existing 33 x 17 direct map
                           versus fresh 53 x 29 direct map
coverage-only map:         17 x 13
```

Every fresh state must pass the complete unchanged C3e point gate, including
the scoped `1e-6` primary reconstructed-`Phi` Maxwell ceiling, the unchanged
explicit equation, boundary, Gauss, and Noether ceilings, and cross-route
thermodynamic/field comparisons. The driver must use deterministic neighboring
continuation, refuse a nonempty output directory, checkpoint every accepted or
failed state, preserve driver/solver checksums, and stop at the first state
failure, integrity change, inherited non-scientific 2700-second operational
runtime ceiling, or new method requirement. The expected point-map runtime is
approximately 10 minutes from the measured C3e per-state cost; runtime does not
alter a scientific tolerance.
All 1537 states are solved fresh. In particular, the 405 coordinates shared
with the accepted `33 x 17` map are recomputed rather than copied or reused as
accepted numerical values. At those overlaps, fresh and stored
`(T,mu,s,rho_canonical)` must agree coordinatewise to relative `1e-10`, scaled
by `max(1,abs(a),abs(b))`, under the already frozen duplicate-run criterion.

The repaired guards are

```text
nominal:  phi_H in [3.500, 6.500], eta in [0.3250, 0.4750]
inward:   phi_H in [3.625, 6.375], eta in [0.3375, 0.4625]
outward:  phi_H in [3.375, 6.625], eta in [0.3125, 0.4875].
```

The guard moves retain the old physical increments `(0.125,0.0125)`, equal to
two cells of the new local tensor. They are not reinterpreted as one new
half-sized cell.

All other U3/U4 rules remain active. In particular, the unique component
continued from the accepted direct critical root must have exactly two simple
transverse source-`mu_BH` window crossings at each representative
temperature; the calibrated below path must have exactly two folds and one
negative-susceptibility middle branch; the critical and above paths must keep
their required ordering and signs; and no eligible feature may contact a
guard edge. The independent four-cell buffer remains measured against the
original C3e parent bounds `[3,7] x [0.30,0.50]` in the original refinement
intervals `(0.125,0.0125)`. Cross-resolution and direct-versus-smooth feature
positions may move by at most those same original refinement intervals. This
preserves the previously frozen stability scale rather than tightening it
after seeing the C3g return.

Component selection is deterministic. The direct row-linear isotherm graph is
primary and is split into contiguous `phi_H` intervals after source-window
clipping. At `T_c`, exactly one interval must bracket `phi_H,c` between its two
window crossings, its row-linear `eta(phi_H,c)` must agree with `eta_c` within
`0.0125`, and the critical `mu_c` must lie inside the frozen critical window.
Below `T_c`, exactly one clipped interval must contain both folds in
increasing-`phi_H` order, show the direct derivative sign pattern `+,-,+`, and
overlap the critical interval in `phi_H`. Above `T_c`, exactly one clipped
interval must overlap the critical interval, preserve the low/high
window-edge crossing order, and have positive direct susceptibility
throughout. Zero or multiple eligible intervals is a hard stop. On every
chosen component, both source-window edges must be crossed through strict
sign-changing brackets; a tangent contact is not a crossing. No clipped
endpoint may lie on a parameter or guard edge. No additional temperature
sweep is inferred from this component-matching definition.

Direct finite differences decide accepted feature counts, signs, ordering,
and reported positions. The smooth tensor route is secondary, but its required
agreement is still a hard-stop consistency gate rather than an averaging or
rescue mechanism. Crossings are matched by source-window edge and increasing
`phi_H`; folds are matched by increasing `phi_H`; the critical root is matched
directly. Coordinatewise `(phi_H,eta)` shifts are gated against
`(0.125,0.0125)`. Shifts in `(T,mu,rho_canonical)` and distances from the local
map edges in new-cell units are reported diagnostics only because no
acceptance scale for those quantities was owner-approved. The audit must
evaluate both window crossings for all three representative temperatures,
every guard variant, all folds and the root, all parent buffers, and every
direct/smooth and `33 x 17`/`53 x 29` comparison; the narrower C3g diagnostic
is not reused as a substitute for this complete gate. The `17 x 13` direct and
smooth routes remain coverage/localization evidence only and cannot fail or
rescue C3h topology acceptance.

The below-temperature calibration remains exactly one
`scipy.optimize.brentq(xtol=1e-10)` root in
`0.90 <= T_-/T_c <= 0.999`, fitting only the fold midpoint to
`0.8106741185`. Both folds and their separation remain non-fitted diagnostics.
No `T_+`, density, residual threshold, or source ordinate may be fitted.

If and only if this repaired local gate passes, V4 opens the previously frozen
`N=80,120,150` critical/five-state campaign with calibration repeated at each
accepted resolution. DOP853, verifier, package, privacy, and final owner gates
remain ordered after that campaign. The absolute source-density ordinate,
global topology, quantitative fold-shape reproduction, free energy,
coexistence, Phase 5C, empirical-QCD claims, commit, push, pull request, merge,
tag, release, and branch deletion remain closed. Work returns at the first new
failure or method change.

## C3h fresh-map result and C3i owner return -- 2026-08-23

The owner-approved fresh local calculation completed all `53 x 29 = 1537`
states at `N=80` in deterministic serpentine order. All 1537 primary and
simultaneous-explicit-`Phi` point gates pass. The append-only point ledger
contains every state, the aggregate map is complete, all 405 coordinates
shared with the accepted `33 x 17` map were solved rather than copied, and no
scientific or operational runtime ceiling was reached.

The next frozen overlap gate nevertheless fails:

| compared observable | maximum scaled fresh/stored difference | coordinates above `1e-10` |
| --- | ---: | ---: |
| primary `T_BH` | `1.3559564582e-10` | 4 |
| primary `mu_BH` | `8.3005043407e-12` | 0 |
| primary `s_BH` | `2.1115788377e-11` | 0 |
| primary `rho_canonical_BH` | `2.1111183109e-11` | 0 |

The four failures are `(phi_H,eta)=(4.875,0.475)`,
`(5.125,0.475)`, `(5.125,0.4875)`, and `(5.375,0.4875)`. Their
primary-temperature differences lie between `1.0185596810e-10` and
`1.3559564582e-10`. Each old and new solve passes the unchanged point gate,
but the two serpentine traversals approach these coordinates from opposite
eta directions and terminate with primary scaled nonlinear residuals between
approximately `1.2e-9` and `2.4e-9`.

A separate read-only diagnostic compares the already stored simultaneous
explicit-`Phi` observables at all 405 coordinates without changing the C3h
decision:

| explicit-`Phi` observable | maximum scaled fresh/stored difference |
| --- | ---: |
| `T_BH` | `2.5635049639e-13` |
| `mu_BH` | `3.4172664698e-13` |
| `s_BH` | `1.1431063208e-12` |
| `rho_canonical_BH` | `1.1540775334e-12` |

Thus state identity, charge branch, and the independently solved explicit
formulation agree much more tightly than `1e-10`. This is evidence that the
literal C3h failure is localized to primary-route temperature sensitivity to
the continuation direction and nonlinear termination, not evidence for a
different physical branch. It does not retrospectively substitute the
explicit route for the recorded primary overlap gate, round the four excesses
down, or authorize a tolerance or route-role change.

The approved V4 ordering therefore stops before the repaired topology audit,
`N=80,120,150`, DOP853, verifier, or package work. No Git or release action is
opened.

### C3i owner recommendations

- **W1 -- preserve both the completed map and the literal hard stop.** Record
  `1537/1537` point gates as passing, retain the complete map as provisional
  numerical evidence, and keep the four primary-temperature overlap failures
  visible. **Recommendation: approve.**
- **W2 -- run a bounded route-conditioning audit.** Replay only the four
  failed coordinates plus matched passing controls from lower-eta,
  upper-eta, and public neutral initializations. Keep the equations, field
  degree, root method, root and polish triggers, tolerances, point gates, and
  `1e-10` reporting scale unchanged. Compare both primary and simultaneous
  explicit-`Phi` observables and preserve every route, including failures.
  **Recommendation: approve.**
- **W3 -- return before changing criterion semantics.** Use the bounded audit
  only to decide prospectively whether cross-continuation uniqueness belongs
  to the primary route, the independently solved simultaneous route, or both.
  Do not make that route-role amendment from the present post-result evidence,
  and do not run topology first. **Recommendation: approve.**
- **W4 -- preserve all downstream closures.** Keep repaired topology,
  `N=80,120,150`, DOP853, verifier/package, source density, global topology,
  fold shape, free energy, coexistence, Phase 5C, empirical-QCD, Git, and
  release work closed until a later prospective owner decision.
  **Recommendation: approve.**

### C3i owner response paths

- **A -- approve W1--W4:** preserve the hard stop and run only the bounded
  multi-seed route-conditioning audit, then return for a prospective route-role
  decision. **Recommended.**
- **B -- artifact-only semantic review:** do not replay points; use the current
  405-state primary/explicit evidence to consider restoring `1e-10` to its
  original complete-verifier-repeat scope and treating cross-continuation
  primary differences as a conditioning diagnostic. This still requires a
  prospective owner amendment before topology.
- **C -- exact complete-map repetition:** rerun the entire `53 x 29` traversal
  with identical ordering to test literal complete-run determinism. This costs
  approximately another 500 seconds and does not by itself diagnose
  opposite-direction seed sensitivity.
- **D -- status walkthrough only:** discuss the result without opening work.
- **E -- custom response:** provide another bounded instruction.

The recommended path is **A**. It investigates the only failed quantity and
the continuation-direction mechanism directly, keeps every tolerance and
hard-stop result unchanged, and avoids spending another full-map runtime on a
same-order repeat that is unlikely to distinguish seed-path sensitivity.

## C3i classical-example re-scope -- 2026-08-23

Xin-Yi Liu selected custom Option E to review whether the research-grade
critical-topology campaign was necessary for a classical HoloForge example.
After that scope review, the owner selected the new recommended Option A: keep
the completed finite-density solver and evidence, preserve C3h as a failed
optional extension, and finish a smaller public Forge/Verify benchmark.

This decision does not rewrite or waive C3h. The `53 x 29` map remains a
complete provisional calculation whose four primary-temperature overlap
comparisons fail the frozen cross-continuation gate. No multi-seed rescue,
topology audit, map repetition, tolerance change, or post-hoc substitution of
the explicit route is part of the public core.

### Reduced public claim

The Phase 5B core may claim only that HoloForge:

1. solves representative neutral and charged DGR EMD backgrounds with the
   flux-reduced Chebyshev formulation;
2. independently solves the geometry, scalar, and Maxwell potential together
   at the declared controls and verifies Gauss and Noether conservation;
3. directly locates the source model's reported critical-coordinate
   neighborhood at `N=80` and reproduces `(T_c,mu_c)` within the existing
   source-coordinate tolerances; and
4. shows spectral convergence of the fixed located state from
   `N=80 -> 120 -> 150`.

It may not claim absolute reproduction of the Figure 5 density ordinate,
accepted Figure 5 topology, global branch completeness, an equal-free-energy
coexistence line, critical exponents, a physical-QCD critical point, or
empirical validation. The approved Figure 5 vector anchors remain public
provenance and a horizontal-window diagnostic only. Because the source gives
no verified map from `rho_source_figure5` to `rho_canonical_BH`, the source
critical coordinates are the owner-reviewed alternative quantitative
literature check for this finite-density classical example.

### Frozen reduced calculation

The bounded verifier uses only these calculations:

```text
direct critical locator:
  degree N = 80
  initial (phi_H,eta) = (4.800667,0.401127)
  five-point constant-T steps Delta phi_H = 0.25, 0.125, 0.0625
  independent validation step Delta phi_H = 0.03125

fixed located-state refinement:
  N = 80, 120, 150

representative controls at N = 80:
  neutral       (phi_H,eta) = (4.84,0.00)
  charged       (phi_H,eta) = (4.84,0.40)
  high charge   (phi_H,eta) = (7.00,0.50)
```

The primary solver, explicit-Maxwell formulation, equations, boundary
conditions, source scales, canonical density `rho_canonical_BH=q/2`, root and
polish rules, and all point tolerances are unchanged. The reduced verifier
retains the globally scoped `1e-6` ceiling only for the known conditioned
primary reconstructed-Maxwell row; explicit physical equations remain at
`1e-5`, explicit boundaries and Gauss drift at `1e-7`, and Noether drift at
`1e-6`. Primary/explicit differences in `(T,mu,s,rho_canonical)` remain at
most `5e-6`.

The direct critical derivative conditions, independent normalized
`J(T,mu)` and isotherm-tangent diagnostics, and step-to-step critical-coordinate
changes remain at most `2e-3`. The source-coordinate gates remain
`|T_c-143 MeV| <= 5 MeV`, `|mu_c-783 MeV| <= 10 MeV`,
`|phi_H,c-4.84| <= 0.20`, and `|eta_c-0.40| <= 0.04`.
For the fixed located state, the maximum scaled `N=120 -> 150` change in
`(T,mu,s,rho_canonical)` remains at most `2e-3` and must improve over the
`N=80 -> 120` change whenever the latter exceeds the existing `1e-8`
ordering floor.

Two complete reduced verifier runs must agree in every reported physical
observable to `1e-10` under the existing
`abs(a-b)/max(1,abs(a),abs(b))` scale. Strict JSON, human CLI, overwrite
protection, model-card/schema, source-checkout, installed-wheel, privacy, and
package tests remain required. The public artifacts are a strict JSON record,
a selected-state CSV, and a computed verification plot. The inherited
operational runtime ceiling for one complete reduced verifier is 600 seconds;
runtime does not alter a scientific tolerance.

### Preserved optional extension

The full Figure 5 topology campaign, C3h route-conditioning audit, dense-map
cross-continuation criterion, calibrated below-temperature path, DOP853
five-state comparison, free energy, coexistence, and Phase 5C remain closed.
They may be reopened only by a later owner-reviewed contract and are not
prerequisites for publishing the classical finite-density benchmark.

### C3i final owner decision -- 2026-08-23

After reviewing the completed reduced verifier and the visually checked owner
packet, Xin-Yi Liu selected final Option A. The owner approves:

1. the reduced numerical result and its seven passing acceptance gates;
2. promotion of the reduced model card from `reference/unreviewed` to
   `reproduced/approved`;
3. the stated evidence boundary, including the blocked Figure 5 absolute
   ordinate and the preserved C3h failure; and
4. bounded Git and pull-request integration, with merge conditional on green
   authoritative CI.

This decision does not authorize a release, a change to the unrelated
Gubser--Nellore tolerance, the optional topology campaign, DOP853 extension,
free-energy/coexistence work, or Phase 5C.
