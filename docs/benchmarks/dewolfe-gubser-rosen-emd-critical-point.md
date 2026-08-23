# DeWolfe--Gubser--Rosen finite-density EMD classical benchmark

## Scope and review state

This Forge/Verify benchmark is the finite-density Phase 5B extension of
HoloForge's released
[`dewolfe-gubser-rosen-emd`](dewolfe-gubser-rosen-emd.md) benchmark. It uses
the phenomenological bottom-up Einstein--Maxwell--dilaton (EMD) model of
O. DeWolfe, S. S. Gubser, and C. Rosen, “A holographic critical point,”
*Phys. Rev. D* 83, 086005 (2011),
[arXiv:1012.1864v2](https://arxiv.org/abs/1012.1864).

On 2026-08-23, Xin-Yi Liu approved C3i Option A: re-scope the public classical
example to a bounded contract that verifies representative finite-density
backgrounds, the source model's reported critical-coordinate neighborhood,
and an independent equation formulation. The earlier C3h topology campaign
remains preserved as a failed optional extension; it does not block this
reduced core and none of its frozen failures is waived.

The reduced verifier reports six states: the located critical state at
`N=80,120,150`, plus neutral `(phi_H,eta)=(4.84,0)`, representative charged
`(4.84,0.40)`, and high-charge `(7.0,0.50)` controls at `N=80`. It locates

```text
(T_c, mu_c) = (142.973974 MeV, 781.693762 MeV),
```

against the paper's reported `(143 MeV,783 MeV)` neighborhood. All states are
checked with the flux-reduced primary formulation and a simultaneous
geometry--scalar--Maxwell formulation, independently evaluated physical
equations and Einstein constraint, conserved Gauss and Noether charges,
boundary conditions, fixed-state spectral refinement, and duplicate complete
runs. Xin-Yi Liu approved the reduced numerical result, model card, and
evidence boundary through final Option A on 2026-08-23. This approval does not
waive C3h or authorize the optional topology campaign, Phase 5C, or a release.

## Canonical density and unresolved source ordinate

The charged Chebyshev point solver converges deterministically through
`N = 150` at the source critical neighborhood and reproduces the quoted
`T` and `mu` coordinates with strong margins for the three implemented
compact equations and the Einstein constraint. The separately reconstructed
Maxwell field passes its equation, Gauss-drift, chemical-potential
reconstruction, and UV `-Phi_2=q/2` checks. The fresh extended map also passes
the independently differentiated explicit-`Phi` Noether diagnostic. However,
the accepted Gauss-law and UV-tail dictionary gives
`rho_canonical = q/2 = 1.3368309001`, whereas the paper prints
`rho_c = 9.9022` and its Figure 5 anchors begin at `rho = 5`.

The two ranges remain disjoint over the complete frozen critical tolerance
box. The canonical solver output is therefore named `rho_canonical_BH`, while
the digitized paper ordinate is named `rho_source_figure5`; `mu_BH` is the
paper abscissa. A bounded source
audit found that the plotted value is numerically close to
`rho_canonical_BH/f(phi_H)^2`, but no reviewed primary statement authorizes
that horizon-dependent factor. It is retained only as an explicitly
unverified, non-inferential diagnostic and cannot steer continuation, fitting,
critical-point location, acceptance, or physical-unit output.

The approved bounded map tested topology in the canonical
`(rho_canonical_BH, mu_BH)` variables. Absolute ordinate comparison to the 36
`rho_source_figure5` anchors remains blocked; no density rescaling, anchor RMS
fit, or Figure 5 absolute-density reproduction claim is permitted. DOP853 and
global-topology acceptance remain outside the reduced core.

## Historical topology-extension audit (preserved, not core acceptance)

### Provisional bounded-map outcome

The exact `9 x 9` survey and `13 x 13` refinement completed at `N=80` with
81/81 and 169/169 states passing the implemented point gates. On the
refinement grid, the largest physical-equation residual is `4.54e-7`, the
largest reconstructed Maxwell residual is `3.83e-8`, and normalized Gauss
drift is at most `5.89e-8`. These are unreviewed implementation results, not an
accepted reproduction.

For each fixed `phi_H` row, temperature is monotone in `eta`. Linear
interpolation in `eta` at fixed temperature followed by finite differences
along the 13 `phi_H` rows gives

| `T_BH` | sign changes of `d mu_BH / d rho_canonical_BH` | minimum slope |
| --- | ---: | ---: |
| `0.5600000000` | 2 | `-3.70e-3` |
| `143/252 = 0.5674603175` | 0 | `+1.19e-4` |
| `0.5750000000` | 0 | `+4.07e-3` |

The first and third rows show the expected local below/above change. The
source critical-temperature row lies close to coalescence, and the sampled
parameter-map Jacobian reaches `1.43e-4` near `(4.85,0.40)`, but neither value
resolves the critical tangent as zero. A separate bicubic tensor-spline search
locates the provisional diagnostic
`(phi_H,eta,T_BH,mu_BH,rho_canonical_BH) =`
`(4.8005928,0.4011273,0.5673573,0.8042108,1.4171485)` and gives a two/one/zero
spinodal-root pattern at its temperature minus `0.005`, at the candidate, and
plus `0.005`. Because that tangent is imposed by interpolation, it remains a
localization diagnostic rather than a resolved critical result.

Moreover, all three extracted paths use the full `phi_H` interval and touch
both `phi_H=4.2` and `phi_H=5.5`.
Because the frozen branch-integrity gate requires reported paths to stay off
scan boundaries, this is a hard stop: the canonical topology gate does not
pass, and the map may not be enlarged without a new owner decision.

The inverse-`f_H^2` diagnostic spans `[4.1468822732,21.3072334271]` but never
enters a solve, interpolation target, topology decision, or gate. The absolute
`rho_source_figure5` comparison was not evaluated.

## C3c simultaneous-Maxwell check and extended-map stop

The secondary spectral route solves the electric potential together with the
geometry and scalar rather than eliminating it through conserved flux. It
uses the regular UV factorization

```text
Phi(u) = mu - u^(2/nu) e(u),
K(u)   = 2 e(u) + nu u e'(u),
D Phi  = -u^(2/nu) K(u),
```

and computes the electric backreaction directly from `e(u)`. The nonlinear
unknowns are `(h,c,p,e,log(x_H),mu)`. The Maxwell UV regularity row,
`eta`-fixed horizon flux, and `Phi(z_H)=0` make the simultaneous system
square. The Einstein/Hamiltonian equation remains an independent diagnostic;
adding it at every node on top of all four dynamical equations would
overdetermine the Bianchi-related system.

All exact frozen controls pass. At `(phi_H,eta,N)=(4.84,0.40,80)`, the maximum
four-equation residual is `2.69e-8`, Gauss drift is `7.04e-12`, and the
explicit versus flux-reduced differences in the background and `mu` are
`1.54e-12` and `2.20e-12`. At `(7.0,0.50,80)`, the corresponding maximum
equation residual is `2.56e-6`, constraint and boundary residuals are
`6.03e-8`, and Gauss drift is `1.34e-9`. The central `N=120` check improves
the maximum equation residual to `3.87e-10`. Eleven focused tests pass.

The approved extension then started the `17 x 13`, `N=80` survey on
`phi_H in [3,7]`, `eta in [0.30,0.50]`. It stored 170 passing states and one
failing state before the mandatory stop. At
`(phi_H,eta)=(6.25,0.4833333333333333)`, every solve, equation, constraint,
boundary, reconstructed-`mu`, and UV-density row passes, but normalized
reconstructed Gauss drift is `1.4251413e-7`, above the frozen `1e-7` ceiling.

Consequently, 50 survey states and the complete `33 x 17` refinement remain
unattempted. No fixed-temperature path, boundary-contact result, smooth
critical candidate, or Figure 5 topology is evaluated from the incomplete
map. This is a near-threshold numerical-diagnostic stop, not a failed EMD
background and not permission to loosen the gate post hoc.

## C3d stopped-state conditioning audit and owner return

The exact stopped state was replayed through the original deterministic
continuation and then refined from `N=80` to `N=120` without changing the
solver or `1e-7` Gauss ceiling. The reconstructed-potential Gauss drifts are
`1.4251412979e-7` and `1.4274904166e-7`: the miss does not improve with
spectral resolution. On those same solutions, the already-approved
UV-factorized explicit-`Phi` route gives conserved-flux drifts
`6.6899574769e-10` and `1.3472556404e-13`, while the primary thermodynamic
observables change by less than `3e-9` and both formulations agree in fields,
charge, and chemical potential to `1e-11`--`1e-13` at `N=120`.

The old failure is localized to the two lowest independent-grid samples. It
differentiates a potential of magnitude about `1.195` across a local change
of only `8.03e-7`, producing a conditioning ratio near `1.49e6`. The stable
`1.43e-7` floor is therefore a reconstruction-differentiation artifact rather
than evidence against the charged background or Maxwell equation.

The audit also found that the incomplete C3c map did not evaluate the
prospectively frozen Noether row,

```text
Q_N^(z) = exp(3 A) h' + q Phi = -2 kappa_5^2 T s,
```

even though its normalized drift ceiling is `1e-6`. The 170 previous states
passed their implemented gates only. Because the saved summaries cannot
support a retrospective Noether check, the next valid map must start from its
first state after that diagnostic is implemented.

The prospective C3e recommendation is map-wide rather than a one-point
exception: preserve the primary solver and all ceilings, use the simultaneous
explicit-`Phi` conserved flux as the authoritative Gauss gate, keep the old
reconstructed drift as a non-gating conditioning monitor, add the Noether
gate, and rerun the complete `17 x 13` plus `33 x 17` map from scratch. This
change was approved by Xin-Yi Liu through C3e Option A on 2026-08-23. The
`1e-7` explicit-flux ceiling remains primary. The owner's possible `1e-6`
fallback is conditional on a fixed `N=80 -> 120` audit in which all equations,
constraints, endpoints, boundary conditions, density, and cross-formulation
checks pass and explicit Gauss drift remains between `1e-7` and `1e-6` as a
stable numerical floor. It is not an immediate relaxation and cannot vary by
state. The absolute source Figure 5 ordinate, density rescaling, free energy,
coexistence, Phase 5C, Git integration, and release remain closed.

For the fresh map, the direct Noether gate is fixed before execution on 80
logarithmic samples over `0.1 <= (z/z_H)^2 <= 0.98`, with a separate `1e-12`
horizon-identity check. This retains the solved interior blackening derivative
as independent evidence while avoiding the analytically understood UV
roundoff amplification of `h=1+O((z/z_H)^4)`.

The C3e high-charge smoke control subsequently isolated a second
reconstructed-potential conditioning floor: its primary reconstructed-Maxwell
residual changed from `1.5455e-7` to `1.2589e-7` to `1.2322e-7` at
`N=80,120,150`, while the simultaneous explicit route and all boundaries
passed with strong margins. Under the owner's conditional `1e-6` instruction,
this row alone now has one global `1e-6` ceiling. Explicit Gauss remains at
`1e-7`, explicit equations at `1e-5`, and all original values remain reported.

## C3e fresh-map return and C3g owner gate

The repaired `17 x 13` survey and `33 x 17` refinement completed from their
first states with 221/221 and 561/561 point gates passing. The largest
refinement-grid values include `6.25e-8` scaled nonlinear residual,
`2.45e-6` maximum primary equation residual, `2.09e-7` reconstructed-Maxwell
residual under the scoped `1e-6` conditioning ceiling, `1.34e-9`
authoritative explicit Gauss drift, `2.54e-7` direct Noether drift, and
`6.03e-8` explicit boundary residual. Explicit-primary thermodynamic and
electric-potential differences remain below `2.0e-10` and `5.7e-11`.

The direct refinement-grid topology is:

| `T_BH` | sign changes | minimum `d mu / d rho` | direct result |
| ---: | ---: | ---: | --- |
| `0.56` | 2 | `-3.7743e-3` | local S shape |
| `143/252` | 0 | `+3.8024e-4` | positive susceptibility |
| `0.575` | 0 | `+4.2902e-3` | positive susceptibility |

The two `T=0.56` folds occur near
`(phi_H,eta,mu_BH)=(4.55151,0.42393,0.82807)` and
`(5.09494,0.39950,0.83106)`. A refinement spline diagnostic localizes the
critical neighborhood near
`(phi_H,eta,T_BH,mu_BH,rho_canonical_BH)=`
`(4.80067,0.40113,0.567355,0.80422,1.41700)`, but it is not a direct critical
solution.

Every full isotherm is an open contour joining `eta=0.50` and `eta=0.30`.
Because the current Gate 6 forbids any reported path from touching a scan
boundary, the audit correctly stops before critical acceptance. The map's
temperature secants are strictly negative in both parameter directions, so
blindly widening the rectangle would move rather than remove those open-tail
contacts.

The approved Figure 5 records give source-backed horizontal windows without
using the blocked density conversion:

```text
above T_c: [0.763360248, 0.786922967]
at T_c:    [0.798016580, 0.810528785]
below T_c: [0.804842255, 0.815169234].
```

All parameter-boundary contacts lie outside these windows. The new owner
return therefore recommends prospectively testing only the connected
near-critical component clipped to those horizontal windows, with parameter
buffers, survey-to-refinement stability, and one-refinement-interval inward
and outward perturbations of a fixed inner parameter guard. Full-contour
contacts would remain reported non-gating coverage facts;
no global-isotherm completeness claim would follow.

The current `T=0.56` folds also lie outside the below-panel horizontal window,
so a boundary-rule change alone cannot pass. Because the source does not
publish the outer-panel temperature, C3g proposes one disclosed
horizontal-only calibration of `T_-` after the direct critical conditions
locate `T_c`. Within the already frozen `0.90 <= T_-/T_c <= 0.999` range, one
unique bracketed scalar root would match the model fold midpoint to
`0.8106741185`, the midpoint of the stored discrete-anchor extrema
`0.810497383` and `0.810850854`. Those source values are not independently
extracted continuous-path spinodals. The fitted temperature is therefore a
localization calibration, not a prediction or identification of the paper's
unpublished temperature; individual folds and their separation remain
non-fitted diagnostics, and the historical `2e-3` scale cannot validate fold
shape. A read-only localization near `T_BH=0.5655` remains diagnostic until
the prospective amendment is approved.

The proposed component rule follows the branch containing the direct critical
root, requires a unique below continuation with exactly two folds and the same
above continuation, and clips it to the three source windows. Every clipped
path must have exactly two transverse window crossings, no parameter-edge
contact, and four refinement-cell buffers. A fixed inner guard
`[3.5,6.5] x [0.35,0.45]` is perturbed inward and outward by one refinement
interval; component identity, fold count/sign, root ordering, and feature
positions must remain stable across those perturbations, both map grids, and
direct versus smooth diagnostics. Direct critical conditions remain
authoritative.

The complete C3g recommendations and A--E response paths are recorded in the
[`Phase 5B contract`](dewolfe-gubser-rosen-emd-phase-5b-contract.md). Direct
critical conditions, the calibrated local topology, `N=80,120,150`, DOP853,
and later verifier validation were approved through C3g Option A on
2026-08-23 and must run in that order until completion or the first new stop.
Git and release actions remain closed.

## C3g result and C3h owner return

The direct critical subgate passes. Direct five-point constant-temperature
derivatives converge at

```text
(phi_H,c, eta_c, T_c, mu_c, rho_canonical,c)
=(4.8000914, 0.4011509, 0.5673570, 0.8042117, 1.4182254),
(T_c, mu_c) = (142.9740 MeV, 781.6938 MeV).
```

The fine normalized critical conditions are below `7.31e-8`. Independent
parameter-map `J(T,mu)` and isotherm-tangent diagnostics decrease from
`O(1e-3)` to `O(1e-5)` under the three frozen steps, while `J(T,rho)` remains
near `-1.25`. The final primary plus simultaneous-explicit-`Phi` point gate
also passes.

The following local-topology gate stops for two non-residual reasons. First,
the `17 x 13` direct finite-difference path loses its two folds at
`T_BH=0.5650031108447`, while the fold midpoint remains `0.0013904874` above
the calibration target. It therefore has no permitted calibration root. The
`33 x 17` direct path has one root at `T_-=0.5654799518161`, with fold
chemical potentials `0.8105220546` and `0.8108261824`, and both smooth maps
also have one nearby root. The direct survey/refinement fold-count requirement
therefore fails.

Second, the above-panel low-window crossing occurs at `eta=0.35255`. This is
more than four fine cells from the parent-map edge and lies
inside the nominal and outward guards, but it lies outside the frozen inward
guard `eta >= 0.3625`. Only one window crossing remains inside that perturbed
guard, so the literal guard-stability requirement fails.

Changing a differential-equation tolerance cannot resolve either condition.
The approved sequence therefore stops before `N=80,120,150`, DOP853, or the
verifier. The contract records the prospective C3h repair: retain the coarse
map as coverage evidence, compare direct topology on the existing refinement
against a fresh local tensor map with half-sized parameter steps, and enlarge
only the guard's eta coverage while keeping two transverse source-window
crossings, the four-parent-cell buffer, component identity, ordering, and
direct-authoritative rules. That amendment requires a new owner decision.
The proposed local tensor is exactly `53 x 29` on
`[3.375,6.625] x [0.3125,0.4875]`, with parameter steps
`(0.0625,0.00625)`.

Xin-Yi Liu approved C3h Option A on 2026-08-23. The `53 x 29`, `N=80`
calculation may therefore run with every C3e point gate unchanged. Its direct
topology is compared authoritatively with the existing `33 x 17` direct map;
the `17 x 13` map is retained as coverage and smooth-localization evidence.
The repaired nominal/inward/outward eta guards are respectively
`[0.325,0.475]`, `[0.3375,0.4625]`, and `[0.3125,0.4875]`. The original
four-cell parent-map buffer and original one-refinement-interval feature-shift
ceiling remain unchanged. Later spectral-resolution, DOP853, verifier, and Git
work remains conditional on this repaired local gate passing.

## C3h fresh-map result and C3i owner return

The fresh `53 x 29`, `N=80` map completes with all `1537/1537` primary plus
simultaneous-explicit-`Phi` point gates passing. All 405 coordinates shared
with the accepted `33 x 17` map were recomputed. The owner-frozen
cross-continuation comparison then fails narrowly: four coordinates exceed
`1e-10` only in the primary `T_BH`, with maximum
`1.3559564582e-10`. Primary `mu_BH`, `s_BH`, and
`rho_canonical_BH` remain below `2.12e-11`.

The four points lie at `eta=0.475` or `0.4875`, where the old and new
serpentine maps approach from opposite eta directions. Their primary scaled
nonlinear residuals are `O(1e-9)`. A read-only comparison of the already
computed simultaneous explicit-`Phi` route agrees across all 405 coordinates
to at most `1.16e-12` in every observable, including a maximum
`T_BH` difference `2.56e-13`. This localizes the discrepancy to
primary-route continuation/termination sensitivity rather than branch
identity, but it does not change the literal C3h decision.

The approved ordering therefore stops before topology, `N=80,120,150`,
DOP853, or verifier work. The Phase 5B contract records C3i A--E paths and
recommends a bounded, unchanged-method replay of the four failures plus matched
controls from lower-eta, upper-eta, and neutral initializations before any
prospective route-role amendment.

## Reduced public verifier

The public benchmark identifier is

```text
dewolfe-gubser-rosen-emd-finite-density
```

The released Phase 5A equations, defaults, artifacts, and command remain
unchanged. The reduced Phase 5B core targets only:

1. representative neutral and finite-density EMD backgrounds;
2. the source model's reported critical-coordinate neighborhood near
   `(T_c, mu_c) = (143 MeV, 783 MeV)`; and
3. spectral refinement plus agreement between the flux-reduced and
   simultaneous-Maxwell formulations.

Source Figures 4 and 5 may be used as provenance or optional branch-topology
diagnostics, but neither full figure is a required reproduction target. The
absolute Figure 5 density ordinate, global topology, critical exponents, free
energies, a coexistence line, and all Phase 5C work remain outside this
benchmark.

## Model, ensemble, and scales

With `L = kappa_5 = 1` during the black-hole solve, the source action and
functions are

```text
S = 1/(2 kappa_5^2) integral d^5x sqrt(-g) [
      R - 1/2 (partial phi)^2
        - 1/4 f_EMD(phi) F_ab F^ab - V(phi)
    ],

V(phi) = -12 cosh(0.606 phi) + 2.057 phi^2,
f_EMD(phi) = sech[(6/5)(phi-2)] / sech(12/5).
```

The grand-canonical variables are `(T, mu)`, while `s` and `rho` are derived
densities. The source scale dictionary is frozen without refitting:

```text
lambda_T   = 252 MeV,
lambda_mu  = 972 MeV,
lambda_rho = (77 MeV)^3,
lambda_s   = (121 MeV)^3.
```

The displayed integer scales retain the previously recorded source-rounding
mismatch. They map the candidate coordinates to
`T_c,BH = 143/252` and `mu_c,BH = 783/972`.

## Charged equations and inward-radial sign

Use the conformal radial coordinate `z`, increasing from the boundary at
`z=0` to the horizon at `z=z_H`:

```text
ds^2 = exp(2 A(z)) [-h(z) dt^2 + d x_vec^2 + dz^2/h(z)],
A_a dx^a = Phi(z) dt.
```

The charged equations are

```text
A'' - A'^2 + phi'^2/6 = 0,

h'' + 3 A' h' - exp(-2 A) f_EMD Phi'^2 = 0,

Phi'' + A' Phi' + (f_EMD,phi/f_EMD) phi' Phi' = 0,

h phi'' + (3 A' h + h') phi'
  - exp(2 A) V_phi
  + 1/2 exp(-2 A) f_EMD,phi Phi'^2 = 0.
```

The independent Einstein constraint is

```text
6 A' h' + h (24 A'^2 - phi'^2)
  + 2 exp(2 A) V + exp(-2 A) f_EMD Phi'^2 = 0.
```

At positive chemical potential and density, regularity fixes
`Phi(z_H)=0` and the inward-coordinate derivative has a fixed negative sign
in the regular bulk:

```text
q = -f_EMD exp(A) Phi' > 0,
Phi' = -q exp(-A)/f_EMD,
mu_BH = q integral_0^z_H dz exp(-A)/f_EMD,
rho_canonical_BH = q/(2 kappa_5^2).
```

Because `f_EMD>0` and `exp(A)>0`, `Phi'<0` for `0<z<=z_H` and approaches
`0^-` at the asymptotically AdS boundary. It cannot become positive on a
regular positive-density solution. The Maxwell field is eliminated
analytically from the collocated fields, but its `q^2` backreaction remains in
the metric and scalar equations; this is not a probe approximation.

The signed inward-radial diagnostics are

```text
Q_G^(z) = f_EMD exp(A) Phi' = -q,
Q_N^(z) = exp(3 A) h' + q Phi = -2 kappa_5^2 T s.
```

The independent outward `B=0` integration uses the source-positive Gauss
orientation. Only magnitudes and thermodynamic observables are compared after
the full UV dictionary is applied.

## Boundary problem and thermodynamics

The primary route retains the Phase 5A UV factorization,

```text
x = z^nu,
u = x/x_H in [0,1],
A = -log(z) + x^2 C(u),
phi = x P(u),
h = H(u),

H(0)=1,  H(1)=0,  P(0)=1.
```

The physical continuation parameters are the horizon scalar `phi_H` and

```text
eta = q/[exp(3 A_H) sqrt(-2 V_H f_EMD,H)].
```

The source critical neighborhood is `(phi_H, eta) approximately (4.84,0.40)`.
The exact horizon constraint and undivided scalar regularity equation are
retained. Thermodynamics are extracted from

```text
T_BH = abs(h'_H)/(4 pi),
s_BH = 2 pi exp(3 A_H)/kappa_5^2.
```

## Figure 5 topology target and blocked source ordinate

The three source panels are labelled only `T>T_c`, `T=T_c`, and `T<T_c`.
The middle panel carries the source critical-temperature label. The two
unpublished outer-panel temperature windows remain frozen historical inputs:

```text
T_minus/T_c in [0.90,0.999],
T_plus/T_c  in [1.001,1.10].
```

Each panel retains 12 fixed, source-vector-derived `mu_BH` anchors at

```text
rho_source_figure5 = 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 18.
```

The 36 numerical anchors and public-source digests are frozen in the
[`Phase 5B contract`](dewolfe-gubser-rosen-emd-phase-5b-contract.md). Source
artwork and third-party lattice points are not redistributed. No point may be
deleted, rescaled, or assigned its own temperature. Because
`rho_source_figure5` has no verified map to `rho_canonical_BH`, the bounded map
does not fit either outer temperature or evaluate the historical anchor-error
thresholds.

The separately evaluated canonical topology is mandatory:

- above `T_c`, the path is single-valued with positive susceptibility;
- below `T_c`, it has exactly two spinodals and a
  negative-susceptibility middle branch; and
- at `T_c`, the spinodals coalesce and the susceptibility diverges.

The S-shaped path diagnoses extrema and an unstable branch. It does not by
itself establish an equal-free-energy coexistence line.

## Frozen numerical routes

The primary Chebyshev calculation uses

```text
critical patch: phi_H in [4.2,5.5], eta in [0.30,0.50],
survey maps:    9 x 9 then 13 x 13 at N=80,
reported states: N=(80,120,150), with N=150 reported.
```

Neighboring states are continued deterministically. The nonlinear solve uses
`scipy.optimize.root(method="hybr", xtol=1e-11)` and, only when triggered, a
recorded `scipy.optimize.least_squares(method="trf")` polish capped at 32
evaluations. Random restarts, best-of-seed selection, shooting fallback, and
private programs are forbidden.

The critical point is located from canonical density,

```text
(partial mu/partial rho)_T = 0,
(partial^2 mu/partial rho^2)_T = 0,
```

and checked independently through the degeneracy of
`partial(T,mu)/partial(phi_H,eta)`. Five states spanning the three Figure 5
paths are also integrated in outward `B=0` gauge with a fourth-order regular
horizon series and `solve_ivp(method="DOP853", rtol=1e-10, atol=1e-12)`.

## Historical full-campaign gates

These thresholds are preserved for the optional topology extension. They are
not reduced-core gates, and the C3i re-scope does not alter or waive them.

1. Source algebra and exact dictionary checks pass at `1e-12` where exact.
2. Every final library solve succeeds with scaled collocation residual at
   most `1e-6`.
3. All four equations on an independent grid of at least `2N` are at most
   `1e-5` individually.
4. The Einstein constraint is at most `1e-5`; endpoint and both undivided
   horizon equations are at most `1e-7`.
5. Normalized Gauss and Noether drift are at most `1e-7` and `1e-6`.
6. Requested `(phi_H,eta,T,rho_canonical)` targets have relative error at most
   `1e-7`. Full-contour boundary contacts remain reported coverage facts; the
   owner-approved C3g local rule instead requires the unique critical-root
   component clipped to each frozen source-`mu` window to retain two
   transverse crossings, four-parent-cell buffers, no clipped parameter-edge
   contact, and stable identity/order under its frozen guard perturbations.
7. `N=120 -> 150` changes in `(T,mu,s,rho_canonical)` and critical coordinates are at
   most `2e-3` and improve over `N=80 -> 120` above a `1e-8` floor.
8. The DOP853 route agrees in `(T,mu,s,rho_canonical)` within `5e-3`; its final cutoff
   change is at most `1e-3`.
9. The critical point lies within `5 MeV` of `143 MeV`, `10 MeV` of `783 MeV`,
   `0.20` of `phi_H=4.84`, and `0.04` of `eta=0.40`.
10. Both normalized critical derivatives and the independent parameter-map
    Jacobian diagnostic are at most `2e-3` under refinement.
11. The historical `2e-3` maximum and `7.5e-4` RMS source-anchor thresholds
    remain recorded but blocked; they cannot pass, fail, or affect the
    canonical topology result while the source ordinate is unresolved.
12. All three canonical Figure 5 topology conditions pass exactly as stated
    above in `(rho_canonical_BH,mu_BH)`.
13. Duplicate full runs agree in physical observables to `1e-10`; strict
    JSON, human output, bundle, overwrite, and installed-wheel checks pass.
14. Released behavior stays unchanged and the diff contains no private data,
    source artwork, unpublished identifier, secret, or temporary-program
    dependency. A full verifier longer than 45 minutes returns for review
    before CI integration.

## Reduced-core acceptance and artifacts

The public classical example requires all six selected states to pass the
frozen point gates, the primary and simultaneous-Maxwell thermodynamic
observables to agree within `5e-6`, and the located critical coordinates to
meet the source-neighborhood tolerances. Normalized critical diagnostics and
step changes must be at most `2e-3`. The fixed critical state must refine from
`N=80` to `120` to `150`, with final scaled change at most `2e-3` and no
worsening above the `1e-8` floor. Duplicate full runs must agree within
`1e-10`. Figure 5 records must remain provenance-only and cannot influence
acceptance.

The interface is

```bash
holoforge verify dewolfe-gubser-rosen-emd-finite-density
holoforge verify dewolfe-gubser-rosen-emd-finite-density --json
holoforge verify dewolfe-gubser-rosen-emd-finite-density \
  --output-dir OUTPUT_DIR
```

The output directory contains strict JSON, a twelve-row CSV covering both
routes for six states, and a HoloForge-generated verification plot. Existing
artifact files are never overwritten. A passing exit code establishes only
the declared model calculation; final result and model-card acceptance still
require owner review.

The full approved scientific and numerical contract is
[`dewolfe-gubser-rosen-emd-phase-5b-contract.md`](dewolfe-gubser-rosen-emd-phase-5b-contract.md).
The full contract, including the preserved negative topology history, is
recorded there.

## Interpretation limits

- DGR is a phenomenological bottom-up model without a systematic uncertainty
  estimate for the candidate critical point.
- A passing reduced verifier reproduces only the selected source-model
  calculation; it would not empirically validate a QCD critical point.
- Phase 5B does not compute renormalized free energies, an equal-free-energy
  coexistence line, critical exponents, finite-`N` fluctuations, experimental
  relevance, or a top-down embedding.
- Negative susceptibility is retained only as the unstable middle-branch
  diagnostic and is not called a stable phase.
- `rho_source_figure5` is a digitized source-artwork coordinate, not a second
  physical density. `rho_canonical_BH/f_H^2` is non-inferential diagnostic
  output only and cannot enter a gate.
- Numerical result acceptance and model-card approval remain with the owner;
  the optional topology campaign and Phase 5C require separate authorization.
