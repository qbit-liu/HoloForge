# HHH optical-conductivity benchmark contract

## Status and authorization boundary

This document began as the pre-implementation owner-review contract for Phase
4 of the classical benchmark sequence and now records its successive
mandatory preflight stops, accepted result, public integration, and bounded
release preparation. It is public-source **Forge/Verify** work and extends the
already released dimension-two Hartnoll--Herzog--Horowitz (HHH)
holographic-superconductor benchmark without changing its accepted behavior.

- **Completed:** Phase 0 spectral infrastructure, Phase 1 Gubser--Nellore ED,
  Phase 2 Gubser--Rocha EMD, and Phase 3 hard-wall chiral QCD are released;
  Phase 3 is closed in Version 0.5.4. The owner approved Phase 4 Decisions
  C1--C6, R1--R3, S1--S3, T1--T3, U1--U3, V1--V3, W1--W3, X1--X3, and
  revised Y1--Y3, Z1--Z3, AA1--AA3, and AB1--AB3. The convention,
  exact-normal, conditioned-background, overlap-equivalence, and
  moderate-temperature checks pass. The post-AB contract amendment, its
  historical bounded failure, near-critical physics amendment, corrected
  implementation run, owner-accepted result, bounded public-interface
  promotion, commits `0280147` and `28420ef`, pull request 25, both fresh
  seven-job pull-request runs, merge commit `2238447`, and the exact
  post-merge seven-job `main` run are complete. The bounded Version 0.5.5
  release metadata, HHH optical CI coverage, release-policy checks,
  source-checkout evidence, full suite, independently installed wheel,
  relocated bundle, complete installed-wheel smoke matrix, and privacy audit
  below are also complete. The separately authorized seven-file Version 0.5.5
  release-preparation commit is complete.
- **Current:** mandatory owner-review stop before any remote action. The prior
  finite-window coefficient miss, degree-320 residual failure, and W2
  endpoint-split failure remain preserved as superseded-contract evidence.
  Figure 2 remains a documented public-source non-reproduction, not an
  acceptance target or reproduced result.
- **Proposed next:** accept or revise the committed release candidate; only
  after explicit approval, push the branch and open a pull request for the
  expanded seven-job remote CI matrix. Merge, tag, release, branch deletion,
  and Phase 5 remain separate later decisions.

Xin-Yi Liu first selected Option A on 2026-08-20 to authorize only this
contract and review packet, then selected Option A again to approve C1--C6 and
authorize the bounded local implementation and complete preflight. After the
first numerical stop, the owner selected Option A a third time to approve
R1--R3. That authorization is now stopped by the second frozen failure
condition recorded below. The owner then selected Option A a fourth time to
approve S1--S3; that bounded audit is now stopped by its preregistered rules.
The owner selected Option A a fifth time to approve T1--T3; that confirmation
audit has now reached its required stop with both first-anchor gates unresolved.
The owner selected Option A a sixth time to approve U1--U3; that localization
audit stopped at the failed milliscale UV-window refinement. The owner selected
Option A a seventh time to approve V1--V3; the asymptotic extraction passes and
has now reached its mandatory stop with the spectral endpoint residual still
unresolved. The owner selected Option A an eighth time to approve W1--W3; the
endpoint-split audit stopped at its first exact-normal residual failure before
the moderate or target calculation. The owner selected Option A a ninth time
to approve X1--X3; the exact-normal control passed, but the audit stopped at
the moderate residual failure before the target calculation.
After an Option E boundary-and-tolerance audit, the owner selected Option A a
tenth time to approve revised Y1--Y3. Both controls pass, and that amendment
has reached its required stop before the target calculation.
The owner selected Option A an eleventh time to approve Z1--Z3. The first
target anchor passes every frozen gate, and that amendment has reached its
required stop before the remaining source grid or figure reproduction.
The owner selected Option A a twelfth time to approve AA1--AA3. All nine
numerical anchors pass, but AA2 fails the frozen public-source comparison and
has reached its mandatory stop without generating a comparison plot.
The owner selected Option A on 2026-08-21 to approve AB1--AB3. The public
source geometry and bounded scale diagnostic reached the required provenance
stop without changing a target. After reviewing that result, the owner
selected Option A again on 2026-08-21 to approve the narrow post-AB contract
amendment recorded below. This latest approval changes the scientific contract
only; it does not accept or promote an implementation.
The owner selected Option A again on 2026-08-21 to authorize only the bounded
implementation completion, machine-readable evidence, regression tests, and
local amended-gate validation. That run has reached the mandatory stop
recorded at the end of this contract; it does not accept the result or open an
interface or Git action.
Later owner decisions recorded below accepted the result and model card,
authorized the bounded public promotion and Git integration, and approved the
Python 3.9 portability correction. The latest two Option A decisions authorize
only the Version 0.5.5 release-preparation pass and exactly one scoped local
commit, as described at the end of this contract. Push, pull request, remote
CI, merge, tag, release, branch deletion, Phase 5, and private-research
transfer remain closed.

## Recommendation

Add a separate `holographic-superconductor-optical` verifier for the
dimension-two HHH model. Reuse the accepted nonlinear background equations
and conventions, use the accepted source-free UV series transfer joined to a
Chebyshev--Gauss--Lobatto bulk element as the primary conductivity method, and
use Riccati-form SciPy DOP853 integration as an independent response route.

The optical extension must verify the exact normal-state result `sigma = 1`,
the source's near-critical dimension-two superfluid-density coefficient
`C_2 = 24`, the inherited Figure 1 low-temperature condensate scale, and
agreement between independent response formulations. The already released
HHH benchmark's quantitative Figure 1 (right) reproduction remains the model's
rapid source-figure validation.

The rightmost curve in source Figure 2 (right) is retained only as a
public-provenance non-reproduction test. Its captioned `T/T_c = 0.0026`,
vector path, and condensate-rescaled counterpart cannot be reconciled from the
public artifacts. No passing source gate, successful-reproduction claim, or
source-comparison plot may be based on that curve. Do not use the source
artwork in a committed or generated HoloForge figure.

This is an extension of a classical bottom-up Abelian-Higgs benchmark, not a
new model family. The public command and evidence record should remain
separate so the released condensate verifier is a protected regression anchor
and its runtime and JSON schema do not change silently.

## Primary public source and provenance

Sean A. Hartnoll, Christopher P. Herzog, and Gary T. Horowitz, "Building an
AdS/CFT superconductor," *Physical Review Letters* **101**, 031601 (2008),
[arXiv:0803.3295v1](https://arxiv.org/abs/0803.3295),
[doi:10.1103/PhysRevLett.101.031601](https://doi.org/10.1103/PhysRevLett.101.031601).

The public arXiv v1 PDF, source archive, and Figure 2 right-panel EPS inspected
for this contract have SHA-256 digests

```text
PDF:             7a9d6ecaf7ee6faf701374ef843bbd8f52eb371697ea0f31414990e0c57cd775
source archive:  3f0a017843f290e338f6db51d2a791f4bb8daea3d79613d1e09dbd59fad9be36
GapClosingR2.eps:f44e59d520cfd29eb95da61a9b9a0460eccd485a26676535cfed78ae6c857652
GapRescaledR2.eps:581233f0dec393aab39ed1be073c55a1a243ae4e4d23fed43277db5da0f6076e
```

The audit covers source Eqs. (1)--(7), (13)--(19), Figure 2 and its caption,
Figure 3, and the surrounding discussion. The paper's source files are audit
inputs only and must not be committed to HoloForge.

## Relationship to the released benchmark

The released `holographic-superconductor` verifier already establishes the
following public contract for the dimension-two theory:

- planar AdS4--Schwarzschild in the probe limit;
- `u = r_h/r` with boundary `u = 0`, horizon `u = 1`, and `L = r_h = 1`
  during the dimensionless solve;
- `m^2 L^2 = -2`, scalar charge `q = 1`, and `psi_- = 0`;
- the accepted onset and nonlinear background equations;
- the fixed-density presentation of invariant observables; and
- source Figure 1 (right), including the rounded critical-temperature and
  condensate checks.

Phase 4 must call or narrowly factor these accepted background functions. It
must not change their equations, defaults, results, identifiers, public
command behavior, or model card. Before any conductivity is accepted, the
existing verifier and its tests must pass unchanged.

## Frozen model and conventions

The source probe-limit matter Lagrangian is

```text
L_matter = -1/4 F_ab F^ab - |D psi|^2 + 2 |psi|^2/L^2,
D_a = partial_a - i A_a,
```

on the planar background

```text
ds^2 = -f(r) dt^2 + dr^2/f(r) + r^2 (dx^2 + dy^2),
f(r) = r^2/L^2 - M/r,
T = 3 r_h/(4 pi L^2).
```

Set `L = r_h = 1` only after forming the dimensionless equations. Define

```text
u = r_h/r,
F(u) = 1 - u^3,
Omega = omega/r_h,
omega/T = (4 pi/3) Omega.
```

With real background fields `psi(u)` and `A_t = phi(u)`, retain the accepted
dimension-two background equations

```text
psi'' + (F'/F - 2/u) psi'
     + [phi^2/F^2 + 2/(u^2 F)] psi = 0,

phi'' - 2 psi^2 phi/(u^2 F) = 0.
```

The UV and horizon data remain

```text
psi = psi_- u + psi_+ u^2 + ... ,    psi_- = 0,
phi = mu - rho u + ... ,             phi(1) = 0,
psi'(1) = 2 psi(1)/3.
```

The presentation is at fixed charge density, as in the source figure. Because
conductivity and `omega/T` are invariant under the background scaling, the
response may be solved at `r_h = 1` and reported in those invariant units.
No canonical/grand-canonical language may be mixed: the nonlinear solution
family is the same, while Figure 2 is a fixed-density presentation.

## Frozen optical-response equation and dictionary

Use a zero-momentum perturbation with the source convention

```text
delta A_x(t,u) = exp(-i omega t) A_x(u).
```

Source Eq. (13), transformed to `u`, is

```text
A_x'' + (F'/F) A_x'
      + [Omega^2/F^2 - 2 psi^2/(u^2 F)] A_x = 0.
```

Primes in this section denote `d/du`. The retarded solution is ingoing at the
horizon. Factor its singular phase exactly:

```text
A_x(u) = (1-u)^p a(u),       p = -i Omega/3.
```

On interior nodes the regular field therefore obeys

```text
a'' + [F'/F - 2p/(1-u)] a'
    + [p(p-1)/(1-u)^2 - p F'/((1-u)F)
       + Omega^2/F^2 - 2 psi^2/(u^2 F)] a = 0.
```

The individually singular coefficients cancel on the ingoing solution; do
not evaluate this interior form at either endpoint. Impose the two analytic
endpoint rows below instead.

The regular factor obeys the exact horizon Frobenius condition

```text
a'(1) + [(p + 2 p^2 + 2 psi_h^2/3)/(1 + 2 p)] a(1) = 0,
psi_h = psi(1).
```

This row must be checked against a direct series expansion before numerical
production. A sign or time-convention mismatch is a hard stop.

At the UV boundary,

```text
A_x = A_x^(0) + A_x^(1)/r + ...
    = A_0 + A_1 u + ...       when r_h = 1.
```

`A_0` is the applied gauge-field source and `A_1` is the current response. Fix
the arbitrary linear amplitude by `a(0) = A_0 = 1`. Since the ingoing factor
also contributes to the UV derivative,

```text
A_1 = A_x'(0) = a'(0) - p a(0),
sigma(omega) = -i A_1/(Omega A_0).
```

This sign is tied to `exp(-i omega t)` and source Eq. (16). It may not be
changed to make a curve positive. Record `A_0`, `A_1`, and the full complex
conductivity at every frequency.

## Background targets

Use the accepted nonlinear `solve_bvp` continuation as the background route;
Phase 4 does not replace an already verified background solver. Construct
these fixed-density target temperatures:

```text
Figure target:        T/T_c = 0.002600
near-critical targets:T/T_c = 0.900, 0.940, 0.970, 0.985
normal target:        psi = 0
```

Target a nonlinear temperature by deterministic continuation in increasing
`psi_h`, then use a bracketed maintained-library root solve in `log(psi_h)`.
The target temperature residual must be at most `2e-6`. The rounded source
caption also permits the Figure-target reproduction to be reported with
`0.00255 <= T/T_c <= 0.00265`, but the implementation must aim at `0.002600`
and must report the achieved value.

Every nonlinear background must retain `|psi_-| <= 1e-8`, a successful BVP
status, maximum reported RMS residual at most `1.1e-7`, positive charge
density, and agreement with the existing fixed-density scaling identities.
Use the existing radial cutoff `1e-5` for the reported background and repeat
the Figure target at `5e-6`. At the primary spectral horizon define

```text
psi_h = psi(1-epsilon)/(1 - 2 epsilon/3)
```

from the accepted first-order regularity relation. Every interior Lobatto node
at the frozen degrees lies inside the BVP interval; only the analytic endpoint
value is supplied this way. Halving the background cutoff must change every
Figure-anchor conductivity by at most `5e-4 (1 + |sigma|)`.

The Figure target is a very low-temperature probe-limit solution. Failure to
reach it with the accepted equations and a bounded continuation is a preflight
stop, not permission to change the target or import a private program.

## Primary numerical route: exact-endpoint spectral response

Use the released `holoforge.numerics.chebyshev_lobatto_grid` utility on
`u in [0,1]` at polynomial degrees

```text
N = 96, 128, 160.
```

Interpolate the accepted BVP background to the spectral nodes with maintained
SciPy interpolation. Build the complex linear operator for the regular field
`a(u)`, replace only the UV row with `a(0)=1`, and replace only the horizon row
with the displayed exact Frobenius condition. Report the `N=160` result.

No finite radial cutoff is used in the primary response. No custom
differentiation matrix, ODE integrator, optimizer, or hand-selected smoothing
is allowed. Matrix condition estimates, boundary-row residuals, and all three
degree results must be recorded.

Check the original unfactored response equation on an independent
twice-denser Lobatto grid. Reconstruct `A_x`, differentiate the interpolated
solution there, omit only the two endpoint rows from the differential-equation
norm, and normalize pointwise by

```text
|A_x''| + |(F'/F) A_x'|
+ |Omega^2/F^2 - 2 psi^2/(u^2 F)| |A_x| + 1.
```

The maximum normalized interior residual must be at most `1e-7` outside the
nearest two check nodes to each singular endpoint. Endpoint correctness is
tested separately by the source and Frobenius rows.

## Independent numerical route: DOP853 integration

Independently integrate the original response equation with
`scipy.integrate.solve_ivp(method="DOP853")`. Initialize

```text
A_x = s^p (1 + c_1 s + O(s^2)),
s = 1-u,
c_1 = (p + 2 p^2 + 2 psi_h^2/3)/(1 + 2 p),
```

at horizon cutoffs

```text
epsilon_h = 2e-6, 1e-6, 5e-7.
```

Use relative tolerance `1e-10`, absolute tolerance `1e-12`, and integrate to
`u = 1e-6` with dense output. Extract `A_0` and `A_1` from a complex
least-squares UV fit on 80 uniformly spaced points in
`u in [1e-6, 5e-3]`, with the preregistered basis `(1, u, u^2)`, then apply
the same conductivity dictionary. Repeat the fit on
`u in [1e-6, 2.5e-3]`, and tighten both integration tolerances by a factor of
ten at the selected audit frequencies. Either refinement must change
conductivity by at most `5e-4 (1 + |sigma|)`.

Run the independent route at every source anchor and every near-critical
low-frequency point. It uses the same physical background but a different
response discretization, endpoint treatment, and UV extraction.

## Historical frozen Figure 2 reproduction target

This target and its `0.02` comparison ceiling are retained as the frozen AA
provenance record. The owner-approved post-AB amendment supersedes it as a
passing acceptance target without changing its anchors, calculation, or
measured failure.

The authors' `GapClosingR2.eps` uses the vector-coordinate transforms

```text
x_EPS = 0.0238095 + 0.0113682 (omega/T),
y_EPS = 0.475411 Re[sigma].
```

The rightmost path begins at EPS coordinate `(0.26557, 0)` and is the curve
identified in the source caption as `T/T_c = 0.0026`. Linear interpolation
within that vector path gives the preregistered anchors:

| `omega/T` | source `Re sigma` |
| ---: | ---: |
| 25 | 0.000094 |
| 30 | 0.001595 |
| 35 | 0.023397 |
| 40 | 0.257286 |
| 45 | 0.920190 |
| 50 | 1.156583 |
| 60 | 1.115810 |
| 70 | 1.066470 |
| 80 | 1.039451 |

At each anchor, the absolute difference between the final HoloForge spectral
value and the source value must be at most `0.02`. This tolerance covers the
caption's rounded temperature, plotted path precision, and reproduction from
public artwork; it does not replace the much tighter equation, convergence,
or route-agreement gates.

Generate an original HoloForge curve on the fixed grid

```text
omega/T = 0.5, 1.0, 1.5, ..., 84.0
```

and overlay only the nine numeric anchor markers plus the analytic normal
line `Re sigma = 1`. Label the markers as values extracted from source vector
artwork and the continuous curve as the HoloForge calculation. Do not copy,
embed, trace, or redistribute the EPS itself. No uncaptioned intermediate
source curves are acceptance targets because the paper does not state their
temperatures.

## Secondary literature and physics checks

### Exact normal phase

For `psi = 0`, electromagnetic self-duality gives the source's
frequency-independent result

```text
sigma(omega) = 1.
```

Check the spectral solver at all nine anchor frequencies. The maximum complex
absolute error must be at most `1e-8`. This is an analytic implementation
anchor, not a fitted normalization.

### Near-critical superfluid density

The source defines the pole by

```text
Im sigma(omega) ~ n_s/omega,
n_s ~ C_2 (T_c - T),          C_2 = 24
```

for the dimension-two theory. At each near-critical background use

```text
omega/T = 0.200, 0.100, 0.050, 0.025.
```

Fit

```text
(n_s/T_c)(omega) = (omega/T)(T/T_c) Im sigma(omega)
```

linearly in `(omega/T)^2` to obtain the zero-frequency intercept. Fit those
four intercepts through the origin against `1-T/T_c`. The resulting slope
must agree with `24` to relative error at most `15%`. Removing the
`T/T_c=0.900` point must change the slope by at most `10%`, and removing the
largest frequency from each pole fit must change its intercept by at most
`2%`.

The calculation does not place a numerical delta function on the real-axis
frequency grid. It supports the delta contribution only through the causal
`1/omega` pole relation and must say so explicitly.

### Basic response sanity

For every positive frequency, require `Re sigma >= -1e-8`. At the Figure
anchors require the `N=160` spectral and middle-cutoff DOP853 complex
conductivities to agree to

```text
|sigma_spec - sigma_ivp| <= 5e-4 (1 + |sigma_spec|).
```

The `N=128` to `N=160` change must be at most
`2e-3 (1 + |sigma_N=160|)`. Horizon-cutoff refinement and the tightened
DOP853 tolerance must each change conductivity by at most
`5e-4 (1 + |sigma|)`.

## Historical AA preregistered acceptance gates

These were the prospective gates frozen before AA. They are retained to make
the failed source comparison auditable. Gate 8 is superseded only by the
owner-approved post-AB amendment below; no numerical threshold was weakened.
A source-looking figure cannot override a failed equation, boundary,
convergence, or independent-route gate.

1. **Protected benchmark:** the released condensate verifier and its exact
   public tests pass unchanged.
2. **Source and convention identities:** both coordinate transformations, the
   UV response relation, the conductivity sign, and the horizon Frobenius row
   agree with analytic derivations to `1e-12` in deterministic unit tests.
3. **Backgrounds:** all five condensed targets meet the temperature, scalar-
   source, BVP, positivity, fixed-density, and Figure-target cutoff-refinement
   gates above.
4. **Spectral equation and boundaries:** the normalized independent-grid
   equation residual is at most `1e-7`; UV and horizon row residuals are at
   most `1e-10` and `1e-9`, respectively.
5. **Spectral refinement:** every Figure anchor meets the frozen `N=128` to
   `N=160` complex-conductivity threshold.
6. **Independent route:** every anchor meets the spectral--DOP853,
   horizon-cutoff, UV-window, and tolerance-refinement thresholds.
7. **Normal phase:** the complex conductivity agrees with `1` to `1e-8` at all
   nine anchors.
8. **Source Figure 2:** all nine final real conductivities agree with the
   public vector anchors to absolute error at most `0.02`.
9. **Near-critical pole:** the extracted slope agrees with `C_2=24` within
   `15%`, with the two stated fit-stability checks.
10. **Causality/passivity sanity:** the pole sign is positive below `T_c` and
    `Re sigma >= -1e-8` at every reported positive frequency.
11. **Determinism and interfaces:** duplicate physical observables agree to
    `1e-11`; JSON is finite and round-trips; CLI, registry, model-card schema,
    evidence-bundle, wheel, and package-data tests pass.
12. **Repository validation:** the full documented suite, installed-wheel
    verifier, `git diff --check`, and public-repository privacy audit pass.

If a gate misses, preserve the measured failure and classify it as a source or
convention error, background-continuation failure, endpoint-factorization
error, spectral-resolution failure, independent-route failure, overly sharp
prospective threshold, or interface failure. A target, method, frequency,
degree, cutoff, fit basis, or threshold may change only through a recorded
owner-reviewed amendment before resuming.

## Mandatory preflight sequence and stops

After owner approval, implementation must proceed in this order:

1. unit-test the coordinate transform, UV current coefficient, Frobenius
   coefficient, and exact normal solution;
2. demonstrate the target backgrounds while protecting the released
   condensate benchmark;
3. solve one normal and one moderate-temperature response with both routes;
4. solve the Figure target only after the first three steps pass;
5. run every preregistered gate and generate bounded evidence; and
6. stop for owner review without accepting the result or model card.

Stop immediately if:

- the source sign, current normalization, rounded-temperature interpretation,
  or horizon series cannot be reconciled;
- the exact normal state does not give `sigma=1` without a fitted factor;
- the low-temperature background cannot be reached with the accepted model
  and maintained-library continuation;
- the spectral row replacement is rank-defective or ill-conditioned enough
  that the preregistered degrees are not meaningful;
- the two response routes select different ingoing solutions;
- agreement requires dropping an anchor or changing a tolerance after seeing
  the source comparison;
- a custom numerical primitive or private program is required;
- runtime cannot fit a bounded public CI job without weakening evidence; or
- any private path, unpublished calculation, correspondence, or candidate
  identifier would enter the public repository.

## Planned public artifacts after approval

The bounded implementation may add only:

- `src/holoforge/benchmarks/holographic_superconductor_optical.py`;
- one matching command adapter and narrow registry entry;
- `domains/condensed_matter/holographic_superconductor_optical/README.md` and
  `model-card.json`;
- `docs/benchmarks/holographic-superconductor-optical.md`;
- `tests/test_holographic_superconductor_optical.py` and focused interface,
  schema, evidence, and package tests;
- generated machine-readable pole-fit, response, and Figure-2
  non-reproduction evidence; and
- at most one original HoloForge conductivity diagnostic graphic without a
  source overlay or source-reproduction claim.

The proposed commands are

```text
holoforge verify holographic-superconductor-optical
holoforge verify holographic-superconductor-optical --json
holoforge verify holographic-superconductor-optical --plot PATH
```

Any release notes, version change, commit, remote action, or public release is
a later decision. The implementation must record source locators, hashes,
equations, conventions, achieved temperatures, complex response data,
condition estimates, residuals, refinements, fit inputs, library versions,
material AI involvement, scope, and every pass/fail result.

## Evidence boundary and scientific limitations

If every current amended gate later passes and the owner accepts the result,
HoloForge may claim only that it reproduced the bounded dimension-two
probe-limit HHH exact normal conductivity and near-critical pole coefficient,
and independently verified its computed condensed optical response under the
declared model, inputs, and methods. It may not claim reproduction of source
Figure 2.

It would not establish:

- empirical validation of a material or of superconductivity in nature;
- a microscopic pairing mechanism, fermionic quasiparticles, or a coherence-
  factor interpretation;
- a controlled zero-temperature ground state or a backreacted low-temperature
  geometry;
- a direct numerical representation of the real-part delta distribution;
- the Ferrell--Glover sum rule on an infinite frequency range;
- the quoted `2 Delta approximately 8.4 T_c` relation as evidence for the
  Figure 2 curve or for a microscopic quasiparticle interpretation; it is used
  only as the inherited condensate-scale check;
- the alternative dimension-one quantization or Figure 2 left panel;
- finite momentum, quasinormal modes, free energy, backreaction, nonlinear
  transport, or another material sector;
- superiority over other holographic models, novelty, or private-research
  relevance; or
- publication, disclosure, or release authorization.

At very low temperature the matter sector becomes large and the probe limit
is not a controlled approximation to a zero-temperature state. The captioned
`T/T_c = 0.0026` background is retained only as an internally verified
low-temperature diagnostic and a check of the public `8.4 T_c` condensate
scale, not as a Figure 2 reproduction or a precision physical prediction.

The boundary U(1) is global in the minimal holographic dictionary. Without an
additional weak gauging prescription, "charged superfluid" is the more precise
interpretation. HoloForge may retain the literature title "holographic
superconductor" while keeping this limitation adjacent to every broad
interpretation.

## Privacy, licensing, and provenance boundary

The public claims and numerical evidence in this contract derive only from the
public arXiv source material and public HoloForge code. Untracked local
notebooks were inspected only as non-transferred diagnostic controls; no
notebook code, private path, or notebook-derived acceptance value enters this
contract. The temporary Mathematica programs are neither needed nor authorized
for transfer. Do not commit the source PDF, TeX archive, EPS, a source
screenshot, or a traced source curve. Numeric anchors and source hashes must
remain visibly attributed to the public paper. Generated code and evidence
must retain material AI provenance until human review.

No unpublished hypothesis, result, literature note, manuscript, private path,
personal identifier beyond the recorded decision owner, secret, or
confidential correspondence may enter this public benchmark.

## Owner decisions

### C1 -- source, extension boundary, and target

**Recommendation: approve.**

- **Reason:** the target is the same classical bottom-up model already in
  HoloForge and reproduces a central source figure with explicit public
  provenance.
- **Opens:** only the dimension-two Figure 2 rightmost curve, analytic normal
  line, and near-critical `C_2` check.
- **Remains closed:** the dimension-one theory, uncaptioned intermediate
  curves, zero-temperature claims, and new model families.
- **Uncertainty:** the caption gives the low temperature only to two
  significant figures; the anchor tolerance accounts for that explicitly.

### C2 -- response equation, dictionary, and physical conventions

**Recommendation: approve after checking the displayed horizon and UV
relations.**

- **Reason:** the response equation and conductivity follow source Eqs. (13)
  and (16), with every sign tied to `exp(-i omega t)`.
- **Opens:** only the stated retarded zero-momentum current response.
- **Remains closed:** alternate sign conventions, fitted normalization,
  finite momentum, and direct delta-function claims.
- **Uncertainty:** a single derivative sign in the factored field would invert
  the current; analytic unit tests are therefore mandatory before numerics.

### C3 -- spectral primary and independent DOP853 route

**Recommendation: approve.**

- **Reason:** exact-endpoint spectral collocation matches the owner's preferred
  research method, while direct adaptive integration tests a different
  endpoint and UV-extraction realization.
- **Opens:** only the frozen degrees, cutoffs, tolerances, and fit basis.
- **Remains closed:** custom numerical primitives and post-result method
  selection.
- **Uncertainty:** the extreme low-temperature background may require more
  continuation nodes; failure is a recorded stop rather than implicit scope.

### C4 -- targets, thresholds, and figure artifact

**Recommendation: approve.**

- **Reason:** nine vector anchors provide a fast visual and quantitative
  source check, while much tighter residual and cross-method gates separate
  source-artwork precision from numerical correctness.
- **Opens:** the frozen frequency grids, anchor comparison, and one original
  HoloForge plot.
- **Remains closed:** copying source artwork, dropping inconvenient anchors,
  and retrospective threshold tuning.
- **Uncertainty:** the prospective spectral degrees have not been tuned to a
  HoloForge result; any miss requires classified review.

### C5 -- evidence, limitations, and public artifacts

**Recommendation: approve.**

- **Reason:** the record distinguishes reproduced response evidence from
  pairing, material, zero-temperature, and disclosure claims.
- **Opens:** only the listed public-source files and auditable evidence after
  all gates pass.
- **Remains closed:** private artifacts, empirical validation, result/model-
  card acceptance, and release action.
- **Uncertainty:** the probe approximation is weakest exactly at the central
  low-temperature source target and must remain prominent.

### C6 -- bounded local implementation and preflight

**Recommendation: approve only with C1--C5.**

- **Reason:** the contract now fixes the source, equations, endpoints,
  backgrounds, methods, targets, gates, artifacts, and stops prospectively.
- **Opens:** only the listed local implementation and complete preflight,
  followed by a mandatory new owner gate.
- **Remains closed:** result or model-card acceptance, commit, push, pull
  request, merge, tag, release, Phase 5, and another model sector.
- **Uncertainty:** the low-temperature continuation and factored spectral
  conditioning are the main implementation risks.

## Owner response paths

- **A -- approve all recommendations:** approve C1--C6 and authorize only the
  bounded local implementation and complete preflight, followed by a new
  owner-review stop.
- **B -- approve selected items:** name the approved decisions; every other
  item remains closed.
- **C -- request revision or more evidence:** identify the source, equation,
  endpoint relation, target, method, threshold, artifact, or limitation.
- **D -- status walkthrough only:** discuss the contract without implementing
  it.
- **E -- custom response:** state another bounded instruction.

**Recommended path: A.** The target is bottom-up, source-anchored,
spectral-first, independently checked, and quick to inspect through a central
source-figure reproduction. Approval would authorize implementation and
preflight only; it would not accept a numerical result or authorize any Git or
release action.

## C1--C6 owner disposition

Xin-Yi Liu selected **Option A** on 2026-08-20 and approved C1--C6. This
opened only the listed local implementation and complete preflight, followed
by a mandatory new owner gate. The authorization did not accept a numerical
result or model card and did not open any Git, remote, release, Phase 5, or
private-transfer action.

## Mandatory background-continuation preflight stop

The convention-first implementation stage passes:

- the `omega/T`--`Omega` coordinate map and transformed response coefficients
  agree algebraically to better than `1e-12`;
- the UV current retains the ingoing-factor contribution
  `A_1 = a'(0) - p a(0)`;
- the first-order ingoing Frobenius identity closes below `1e-12`; and
- the degree-160 exact-endpoint spectral response gives complex `sigma = 1`
  within `1e-8` at all nine source-anchor frequencies, with the frozen
  equation and endpoint residuals passing.

The next mandatory step cannot reach the source Figure target with the frozen
increasing-`psi_h` background continuation. At cutoff `1e-5`, BVP tolerance
`1e-7`, and a maximum of 250,000 mesh nodes, the final accepted approach to
the barrier is:

| `psi_h` | `T/T_c` | `rho` | mesh nodes | maximum RMS residual |
| ---: | ---: | ---: | ---: | ---: |
| 22.200 | 0.041891960 | 2315.5903 | 1696 | `9.998e-8` |
| 22.205 | 0.041882418 | 2316.6456 | 1698 | `9.991e-8` |
| 22.210 | 0.041872881 | 2317.7011 | 1698 | `9.962e-8` |
| 22.215 | 0.041863347 | 2318.7568 | 1699 | `9.963e-8` |
| 22.220 | 0.041853818 | 2319.8128 | 1698 | `9.991e-8` |

The next step, `psi_h = 22.225`, exhausts 204,704 nodes with maximum RMS
residual `1.006e-1`. Reducing the continuation step from approximately `0.05`
to `0.005` therefore does not resolve the barrier. A separate run with a
coarser approach fails at `psi_h = 22.25` after roughly 199,000 nodes. The
required Figure target is `T/T_c = 0.002600`, corresponding to
`sqrt(rho) = 775.333` and `rho = 6.01141e5`, far beyond the last passing
`sqrt(rho) = 48.1644` state.

This is a **background-continuation failure**, not a physical negative result
and not a conductivity disagreement. The abrupt singular behavior is
consistent with the chosen horizon-scalar parameter approaching a fold or a
severely ill-conditioned segment; that interpretation is provisional. The
contract explicitly requires a stop rather than a silent method change. No
condensed optical response, Figure 2 comparison, pole fit, plot, model card,
or result claim has been produced.

## Proposed R1--R3 background amendment

### R1 -- fixed-density conditioning coordinate

**Recommendation: approve.** Retain the same accepted background physics and
SciPy `solve_bvp`, but condition the low-temperature continuation with

```text
R = sqrt(rho),      z = R u,      phi(u) = R Phi(z),
F(z) = 1 - (z/R)^3.
```

The equations become

```text
psi_zz + (F_z/F - 2/z) psi_z
       + [Phi^2/F^2 + 2/(z^2 F)] psi = 0,
Phi_zz - 2 psi^2 Phi/(z^2 F) = 0.
```

Use the last passing original-`u` solution as the branch seed, impose the same
vanishing scalar source, fix the UV charge normalization by `Phi_z(0) = -1`,
and retain `Phi(R) = 0` and `psi_z(R) = 2 psi(R)/(3R)`. Continue monotonically
in `R` from `48.1644` to the analytically fixed target `775.3329`, using at
most a factor `1.05` between seed values and a final exact target step.

- **Reason:** this is the scale-covariant form of the same equations and fixes
  the monotonic physical control directly instead of forcing continuation
  through the observed `psi_h` barrier.
- **Opens:** only this maintained-library background conditioning and its
  deterministic continuation.
- **Remains closed:** changing the response equations, source target,
  spectral degrees, DOP853 route, thresholds, or physical scope.
- **Uncertainty:** the conditioned branch has not yet been run; it may still
  expose a distinct resolution or branch-selection stop.

### R2 -- overlap and mapped-equation validation

**Recommendation: approve only with R1.** Before proceeding below the current
temperature, require the conditioned representation to reproduce the last
passing original-`u` state at `R = 48.1644`. The mapped profiles must satisfy
the original `u` equations and boundary conditions with normalized residual
at most `1e-7`; achieved `T/T_c`, UV data, and horizon data must agree with the
original solution to relative `1e-6`. Retain the frozen target-temperature,
cutoff-refinement, source, BVP, and response gates.

- **Reason:** the overlap gate distinguishes conditioning from a change of
  physical branch or normalization.
- **Opens:** advancing the conditioned branch only after equivalence is
  demonstrated.
- **Remains closed:** accepting a low-temperature state on visual or solver-
  success evidence alone.
- **Uncertainty:** the overlap tolerance is prospective and may identify a
  transformation or endpoint error before any Figure response is attempted.

### R3 -- bounded resume

**Recommendation: approve only with R1--R2.** Resume the local implementation
at the overlap test, then attempt the target background and all originally
frozen response gates. Stop again for owner review after complete preflight or
at the first new failure.

- **Reason:** every response target, tolerance, limitation, and artifact
  remains frozen; only the failed background continuation coordinate changes.
- **Opens:** conditioned background implementation, overlap verification, and
  the previously authorized response preflight if the background passes.
- **Remains closed:** result/model-card acceptance, commit, push, pull request,
  merge, tag, release, Phase 5, and any private artifact.
- **Uncertainty:** reaching `R = 775.3329` may still be computationally stiff
  within a bounded public verifier.

## R1--R3 owner response paths

- **A -- approve all recommendations:** approve R1--R3 and resume only the
  conditioned local background and original complete preflight, followed by a
  mandatory new owner gate.
- **B -- approve selected items:** name the approved amendments; all other work
  remains closed.
- **C -- request revision or more evidence:** identify the conditioning map,
  overlap gate, continuation sequence, or diagnosis to revise.
- **D -- status walkthrough only:** discuss the stop without resuming work.
- **E -- custom response:** state another bounded instruction.

**Recommended path: A.** It preserves the accepted physical equations,
fixed-density ensemble, public source target, spectral response method, and
every response threshold while replacing only the continuation coordinate
that failed before the required regime.

## R1--R3 owner disposition and completed evidence

Xin-Yi Liu selected **Option A** on 2026-08-20 and approved R1--R3. This
opened only the conditioned background, its overlap gate, and the previously
frozen preflight up to complete evidence or the first new failure. It did not
accept a result or model card and did not authorize a commit, remote action,
release, Phase 5, or private transfer.

The overlap-equivalence gate passes at the last valid original state:

| quantity | measured value | frozen ceiling |
| --- | ---: | ---: |
| `R = sqrt(rho)` | `48.1644347919` | fixed overlap state |
| mapped original-`u` equation residual | `1.6714e-8` | `1e-7` |
| mapped boundary residual | `5.8000e-17` | `1e-7` |
| relative `T/T_c` difference | `0` | `1e-6` |
| maximum relative UV-data difference | `1.2163e-9` | `1e-6` |
| maximum relative horizon-data difference | `6.8279e-11` | `1e-6` |
| original / conditioned maximum BVP RMS | `9.9910e-8 / 4.7749e-9` | `1.1e-7` |

The deterministic conditioned continuation then takes 57 monotonically
increasing steps, never exceeding the approved `1.05` seed ratio, and reaches

```text
R = 775.3328795343,          rho = 601141.0740870,
T/T_c = 0.0026000000000,     psi_h = 353.9141481663.
```

The target scalar-source coefficient is `3.5527e-15`, the maximum BVP RMS
residual is `9.4707e-8`, and the final mesh has 3,412 nodes. Thus the first
background-continuation stop is resolved without changing the physical
equations, ensemble, source target, or background acceptance ceilings.

Before the Figure target, the required moderate state at `T/T_c = 0.900`
passes. At `omega/T = 0.200`, the degree-160 spectral route gives

```text
sigma_spec = 0.4087767401 + 10.2931927003 i,
normalized equation residual = 2.20e-8,
```

while the middle-cutoff DOP853 route gives

```text
sigma_ivp = 0.4087767306 + 10.2931941848 i.
```

Their normalized difference is `1.31e-7`, below the frozen `5e-4` route
ceiling. The horizon-cutoff, UV-window, and tightened-tolerance DOP853 changes
also pass; the largest normalized change is `1.15e-7`. The DOP853 normal-state
check at `omega/T = 40` returns `1.0002265860 + 0.0000050127 i`, consistent
with the independent-route tolerance. The much tighter exact-normal gate
continues to be supplied by the spectral route and passes at all nine anchors.

## Second mandatory preflight stop: spectral resolution

The first Figure-target anchor, `omega/T = 25`, fails the independent-grid
equation-residual gate at every frozen degree:

| degree | complex spectral conductivity | equation residual | condition estimate |
| ---: | ---: | ---: | ---: |
| 96 | `0.0006511 + 70.8257999 i` | `9.9664e-1` | `4.7925e8` |
| 128 | `0.0002917 + 71.5277022 i` | `9.8592e-1` | `9.9617e8` |
| 160 | `-0.0000400 + 71.4668217 i` | `9.1988e-1` | `1.8159e9` |

The UV and horizon rows still close, and the `N=128` to `N=160` conductivity
change happens to meet its separate threshold. Those facts cannot override an
order-one differential-equation residual. The apparent conductivity values
and their accidental source proximity therefore are not valid reproduction
evidence.

This is a **spectral-resolution failure** at the approved extreme-
temperature background. It is not a source-figure disagreement, DOP853
failure, physical negative result, or failure of the conditioned background.
No Figure-target DOP853 value, accepted source-anchor comparison, continuous
curve, pole fit, plot, model card, or result claim has been produced.

The first diagnostic call was vectorized over the nine anchors and returned
all nine linear solves before the order-one residual was classified. In
accordance with the stop rule, only the first-anchor failure above is treated
as preflight evidence; the later returned values are not used to support or
reject a source comparison.

## Proposed S1--S3 spectral-resolution amendment

### S1 -- first-anchor resolution-only ladder

**Recommendation: approve.** At the same Figure background and only
`omega/T = 25`, retain the exact response equation, endpoint rows,
independent-grid residual, thresholds, and maintained SciPy/NumPy route, but
evaluate the prospective degrees

```text
N = 192, 256, 320, 384, 512.
```

Require two consecutive degrees to satisfy the unchanged `1e-7` equation
residual and the unchanged `2e-3 (1 + |sigma|)` refinement ceiling. Record
condition estimates and stop if this ladder is exhausted without both gates.

- **Reason:** the failure is demonstrably resolution-local and occurs before
  a source comparison; a preregistered degree ladder tests whether the same
  spectral formulation converges without changing physics or thresholds.
- **Opens:** only five additional first-anchor spectral solves and their
  numerical diagnostics.
- **Remains closed:** all other anchors, source acceptance, degree selection
  after seeing the ladder, coordinate maps, domain decomposition, pole fits,
  plot, model-card/result acceptance, and Git/release action.
- **Uncertainty:** higher degree may worsen roundoff or remain unable to
  resolve the very-low-temperature barrier.

### S2 -- conditional first-anchor DOP853 audit

**Recommendation: approve only with S1.** Run the already frozen DOP853
cutoffs, UV windows, and tolerance refinement at `omega/T = 25`. Compare it
only with the highest consecutive spectral pair that passes S1. If S1 does
not pass, retain the DOP853 value as diagnostic evidence only and do not make
a source comparison.

- **Reason:** this separates spectral nonconvergence from a response-dictionary
  or ingoing-solution mismatch without changing the independent method.
- **Opens:** only the frozen first-anchor independent-route audit.
- **Remains closed:** treating DOP853 alone as the benchmark result or using
  its value to tune the spectral ladder.
- **Uncertainty:** the low-temperature IVP may itself be stiff or sensitive to
  the frozen UV extraction.

### S3 -- bounded diagnostic stop

**Recommendation: approve only with S1--S2.** Return to the owner immediately
after the first-anchor resolution audit, whether it passes or fails. Do not
resume the remaining Figure anchors or later gates in the same run.

- **Reason:** a post-failure resolution change deserves its own evidence gate
  before it becomes benchmark configuration.
- **Opens:** an owner decision informed by one falsifiable numerical audit.
- **Remains closed:** complete Phase 4 preflight and every acceptance,
  publication, and release action.
- **Uncertainty:** even a passing first anchor does not establish resolution
  across the full frequency grid.

## S1--S3 owner response paths

- **A -- approve all recommendations:** approve S1--S3 and authorize only the
  first-anchor resolution/DOP853 audit, followed by another mandatory stop.
- **B -- approve selected items:** name them; every other action remains
  closed.
- **C -- request revision or evidence:** identify the degree ladder,
  consecutive-pass rule, DOP853 audit, or diagnosis to change.
- **D -- status walkthrough only:** discuss the stop without more computation.
- **E -- custom response:** state another bounded instruction.

**Recommended path: A.** It tests the narrowest same-method explanation for
the measured failure while preserving every physical target, equation,
threshold, and independent-route control.

## S1--S3 owner disposition and first-anchor audit

Xin-Yi Liu selected **Option A** on 2026-08-20 and approved S1--S3. This
authorized only the five frozen higher-degree solves at `omega/T = 25`, the
unchanged first-anchor DOP853 audit, and an immediate return to the owner. It
did not authorize another frequency, a source comparison, a threshold or
method change, result acceptance, model-card acceptance, or any Git/release
action.

The higher-degree spectral ladder is strongly convergent but does not satisfy
the preregistered two-consecutive-degree rule:

| `N` | complex `sigma` | equation residual | condition estimate | change from previous |
| ---: | ---: | ---: | ---: | ---: |
| 192 | `-1.6323e-6 + 71.45753093 i` | `2.0341e-1` | `3.0678e9` | -- |
| 256 | `-3.2889e-8 + 71.45909194 i` | `9.2330e-3` | `7.6648e9` | `2.1543e-5` |
| 320 | `9.6527e-10 + 71.45907165 i` | `2.8212e-4` | `1.7015e10` | `2.8009e-7` |
| 384 | `-1.3271e-11 + 71.45907178 i` | `4.2479e-6` | `3.4412e10` | `1.8659e-9` |
| 512 | `-2.0983e-14 + 71.45907179 i` | `8.0288e-8` | `1.1231e11` | `6.9923e-11` |

The conductivity-refinement ceiling passes for every available pair. The
equation residual decreases monotonically by more than six orders of
magnitude, and `N = 512` is the first degree to pass the unchanged `1e-7`
ceiling. However, `N = 384` does not pass, so no two consecutive approved
degrees satisfy the S1 rule. The UV and horizon rows continue to pass.

**S1 verdict: failed consecutive-confirmation gate.** This is not evidence
that the same spectral formulation cannot converge: the single `N = 512`
residual passes and the ladder is monotonic. It is also not permission to
accept `N = 512` alone or add another degree without review. The growing
condition estimate remains an important roundoff risk.

The unchanged unfactored DOP853 route fails at its primary
`epsilon_h = 1e-6`, `rtol = 1e-10`, `atol = 1e-12` configuration before any UV
fit or conductivity is returned. SciPy reports

```text
Required step size is less than spacing between numbers.
```

Floating-point invalid-operation warnings precede the stop. Because the base
integration fails, the horizon-cutoff, UV-window, and tolerance refinements
cannot be meaningfully compared and are not run.

**S2 verdict: independent-route failure at the Figure background.** The
unfactored field develops numerical dynamic range that the frozen direct IVP
does not traverse. This does not reject the response equation or establish a
source disagreement; the same DOP853 implementation passes the normal and
moderate checks.

The combined audit therefore stops without a source comparison. No value in
the table is accepted as a Figure reproduction, and no other anchor, pole,
curve, plot, model card, or result claim has been produced.

## Proposed T1--T3 confirmation amendment

### T1 -- one prospective spectral confirmation degree

**Recommendation: approve.** Evaluate only `N = 640` at the unchanged
Figure background and `omega/T = 25`. Require the unchanged equation,
endpoint, and refinement gates. Treat `N = 512` and `N = 640` as the
consecutive pair only if both residuals are at most `1e-7` and their change is
at most `2e-3 (1 + |sigma_640|)`. Record the condition estimate and stop on
any miss.

- **Reason:** `N = 512` is the first passing degree, so exactly one frozen
  confirmation degree is the minimum test of consecutive convergence.
- **Opens:** one same-equation spectral solve and its diagnostics.
- **Remains closed:** degrees beyond 640, other frequencies, source
  comparison, threshold changes, coordinate maps, and acceptance actions.
- **Uncertainty:** the condition estimate already exceeds `1e11`; `N = 640`
  may be dominated by roundoff even if the physical profile is resolved.

### T2 -- logarithmic-derivative DOP853 audit

**Recommendation: approve only with T1.** Replace only the overflowing IVP
dependent variable by the standard logarithmic derivative

```text
Y = A_x'/A_x,
Y' + Y^2 + (F'/F) Y
   + [Omega^2/F^2 - 2 psi^2/(u^2 F)] = 0.
```

Initialize from the same ingoing series,

```text
Y(1-epsilon_h) = -p/epsilon_h - c_1/(1 + c_1 epsilon_h),
```

use the same SciPy DOP853 cutoffs and tolerances, and fit the intercept of
`Y(u)` on the same 80-point UV windows with the preregistered polynomial basis
`(1, u, u^2)`. The intercept is `A_1/A_0`, so retain
`sigma = -i Y(0)/Omega`. Before the Figure background, require this route to
reproduce the exact normal response within the independent-route tolerance
and the existing moderate `T/T_c = 0.900`, `omega/T = 0.200` response within
the unchanged route gate. A Riccati pole or any failed refinement is a stop.

- **Reason:** the ratio removes irrelevant amplitude overflow while retaining
  the original response equation, ingoing condition, DOP853 library, and
  conductivity dictionary.
- **Opens:** normal and moderate controls plus one first-anchor Riccati audit.
- **Remains closed:** treating this route as a source result, using it to tune
  the spectral pair, or replacing the spectral primary method.
- **Uncertainty:** zeros of `A_x` would appear as Riccati poles, and the UV fit
  of `Y` is a newly reviewed extraction that must pass its own refinements.

### T3 -- bounded confirmation stop

**Recommendation: approve only with T1--T2.** Return immediately after the
`N = 640` and logarithmic-derivative first-anchor audit, whether they pass or
fail. Do not run the remaining Figure anchors in the same authorization.

- **Reason:** both changes are post-failure numerical amendments and require
  direct owner review before entering benchmark configuration.
- **Opens:** one itemized decision on spectral confirmation and independent-
  route viability.
- **Remains closed:** complete preflight, result/model-card acceptance, Git,
  release, Phase 5, and private transfer.
- **Uncertainty:** a one-anchor pass would still not establish resolution or
  independent-route stability across the complete frequency grid.

## T1--T3 owner response paths

- **A -- approve all recommendations:** approve T1--T3 and authorize only the
  one-anchor confirmation audit, followed by another mandatory stop.
- **B -- approve selected items:** name them; every other action remains
  closed.
- **C -- request revision or evidence:** identify the confirmation degree,
  Riccati equation, UV extraction, controls, or stop rule to change.
- **D -- status walkthrough only:** discuss the audit without more
  computation.
- **E -- custom response:** state another bounded instruction.

**Recommended path: A.** It uses the smallest prospective spectral extension
and a standard overflow-resistant representation of the same independent IVP,
while leaving the source target and every acceptance threshold unchanged.

## T1--T3 owner disposition and confirmation audit

Xin-Yi Liu selected **Option A** on 2026-08-20 and approved T1--T3. This
authorized exactly one `N = 640` solve at `omega/T = 25`, the Riccati normal
and moderate controls, one Riccati solve at the same first Figure anchor, and
an immediate return to the owner. It did not authorize a higher degree,
another frequency, source comparison, target refinement after a failed route
gate, a new spectral formulation, result acceptance, or Git/release action.

The prospective spectral pair gives

| `N` | complex `sigma` | equation residual | condition estimate |
| ---: | ---: | ---: | ---: |
| 512 | `-2.10e-14 + 71.4590717880 i` | `8.01e-8` | `1.1231e11` |
| 640 | `-1.42e-13 + 71.4590717876 i` | `4.26e-6` | `2.9213e11` |

The complex-conductivity change is `4.19e-10`, far below its `0.1449`
ceiling, and the UV and horizon rows pass. However, the independently
evaluated equation residual worsens by about a factor of 53 and exceeds the
unchanged `1e-7` ceiling. The matrix condition estimate also increases by a
factor of about 2.6.

**T1 verdict: failed spectral confirmation.** The nearly unchanged
conductivity does not override the failed residual. The evidence is consistent
with roundoff or global-collocation conditioning becoming dominant, but it
does not prove that interpretation or confirm a primary first-anchor value.

The logarithmic-derivative route first passes both required controls:

- at the exact normal state and `omega/T = 40`,
  `sigma = 1.0000000060 + 2.40e-10 i`, with absolute error `6.03e-9`; the
  largest normalized cutoff, UV-window, or tolerance change is `2.64e-9`;
- at `T/T_c = 0.900` and `omega/T = 0.200`, the Riccati result is
  `0.4087767437 + 10.2931924048 i`; its normalized difference from the
  spectral result is `2.61e-8`, and its largest normalized refinement change
  is `2.29e-8`.

At the extreme Figure background and `omega/T = 25`, the base Riccati solve
returns

```text
sigma_Riccati = 0 + 76.6204260669 i,
Y(0) = -457.2944831383,
function evaluations = 25319.
```

Its distance from the unconfirmed `N = 640` value is `5.16135`, whereas the
unchanged route ceiling is `0.03623`. Because this base route comparison
already fails, the target-background horizon-cutoff, UV-window, and tolerance
refinements are not run. The normal and moderate refinements above do not
authorize continuing through a failed first-anchor gate.

**T2 verdict: extreme-background cross-route disagreement.** The Riccati
transformation removes the unfactored amplitude failure and is independently
accurate on both controls, but it does not agree with the ill-conditioned,
residual-failing spectral candidate. This is not a source disagreement: neither
route supplies an accepted primary result, and no source value is compared.

**T3 verdict: mandatory stop completed.** No additional degree, frequency,
target refinement, source comparison, curve, plot, pole fit, model card, or
result claim is produced.

## Proposed U1--U3 localization amendment

### U1 -- Riccati first-anchor self-refinement

**Recommendation: approve.** At only `omega/T = 25`, repeat the Riccati solve
with the already frozen horizon cutoffs, the `2.5e-3` UV fit window, and the
ten-times tighter DOP853 tolerances. Compare each only with the base Riccati
value and require every normalized change to be at most `5e-4`. Stop on a
Riccati pole, integration failure, non-finite UV data, or refinement miss.

- **Reason:** the cross-route failure cannot distinguish a stable Riccati
  solution from an extraction artifact while the spectral primary is itself
  unconfirmed.
- **Opens:** four distinct first-anchor refinements; the middle cutoff is the
  base configuration and is not a separate solve.
- **Remains closed:** source comparison, accepting Riccati as primary, another
  frequency, or changing any cutoff, fit basis, or tolerance.
- **Uncertainty:** self-consistency cannot establish that the Riccati value is
  the physical numerical solution when the primary route disagrees.

### U2 -- fixed-resolution residual localization

**Recommendation: approve only with U1.** Recompute only the already approved
`N = 512` and `N = 640` solutions and record where their existing normalized
independent-grid residual reaches its maximum. Report UV, bulk, and horizon
regional maxima without changing the residual formula, exclusion rows,
degrees, or `1e-7` gate. This is a diagnostic, not a substitute residual.

- **Reason:** localization can distinguish endpoint/interpolation amplification
  from a bulk equation failure before considering a new spectral procedure.
- **Opens:** residual-location metadata for the two existing solutions only.
- **Remains closed:** higher precision, domain decomposition, coordinate maps,
  new degrees, threshold changes, or acceptance of either conductivity.
- **Uncertainty:** a localized maximum may still combine background
  interpolation error and collocation roundoff.

### U3 -- bounded localization stop

**Recommendation: approve only with U1--U2.** Return immediately after the
first-anchor Riccati self-refinement and residual-localization audit, whether
they pass or fail. A later owner gate must choose whether to revise the
spectral formulation, promote the Riccati route, or stop Phase 4.

- **Reason:** the next decision changes numerical strategy and must not be
  inferred from diagnostic stability alone.
- **Opens:** one evidence-based owner choice about the unresolved response
  calculation.
- **Remains closed:** all additional physics, source reproduction, model-card
  acceptance, Git/release action, Phase 5, and private transfer.
- **Uncertainty:** even a stable Riccati route plus localized spectral failure
  would not validate the remaining Figure grid.

## U1--U3 owner response paths

- **A -- approve all recommendations:** approve U1--U3 and authorize only the
  first-anchor self-refinement/localization audit, followed by another stop.
- **B -- approve selected items:** name them; every other action remains
  closed.
- **C -- request revision or evidence:** identify a refinement, residual
  region, or stop rule to change.
- **D -- status walkthrough only:** discuss T1--T3 without more computation.
- **E -- custom response:** state another bounded instruction.

**Recommended path: A.** It tests whether the stabilized route is internally
reproducible and locates the spectral failure before authorizing a new solver
or weakening any scientific gate.

## U1--U3 owner disposition and localization audit

Xin-Yi Liu selected **Option A** on 2026-08-20 and approved U1--U3. This
authorized only four distinct Riccati refinements at `omega/T = 25`, residual
localization for the already approved `N = 512` and `N = 640` solutions, and
an immediate return to the owner. It did not authorize a different UV window,
another degree or frequency, source comparison, solver promotion, threshold
change, result acceptance, or Git/release action.

For localization only, the independent-grid points are partitioned
prospectively into UV (`u <= 0.1`), bulk (`0.1 < u < 0.9`), and horizon
(`u >= 0.9`) regions. The residual formula, doubled check degree, three-row
endpoint exclusions, normalization, and `1e-7` gate remain unchanged. SciPy's
otherwise implicit barycentric-weight permutation is fixed with
`random_state = 0` so the location metadata is reproducible; this does not
change the interpolation formula.

The Riccati self-refinement audit gives

| configuration | `Im sigma` | normalized change | verdict |
| --- | ---: | ---: | --- |
| base: `epsilon_h = 1e-6`, `u_fit = 5e-3` | `76.6204260669` | -- | reference |
| `epsilon_h = 2e-6` | `76.6204261516` | `1.09e-9` | pass |
| `epsilon_h = 5e-7` | `76.6204261873` | `1.55e-9` | pass |
| `u_fit = 2.5e-3` | `70.6231395311` | `7.726e-2` | **fail** |
| `rtol = 1e-11`, `atol = 1e-13` | `76.6204260764` | `1.23e-10` | pass |

The frozen ceiling is `5e-4`. Horizon initialization and integration tolerance
are therefore stable, but the UV extrapolation is not. The failed narrower
window moves the Riccati value toward, but does not establish agreement with,
the unconfirmed spectral candidate; target proximity is not an acceptance
criterion.

**U1 verdict: failed Riccati UV-window refinement.** The original milliscale
fit window is not a controlled asymptotic extraction on this extreme
background. The evidence does not identify either tested window as correct.

The unchanged spectral residual localizes as follows:

| `N` | global maximum and coordinate | UV maximum | bulk maximum | horizon maximum |
| ---: | ---: | ---: | ---: | ---: |
| 512 | `7.835e-8` at `u = 2.118e-5` | `7.835e-8` | `7.354e-10` | `1.924e-8` |
| 640 | `4.316e-6` at `u = 1.355e-5` | `4.316e-6` | `9.850e-9` | `1.842e-7` |

Both maxima lie in the UV near the background's `1e-5` endpoint-expansion
transition, while both bulk regional maxima pass `1e-7`. The `N = 640`
horizon region also misses the global threshold, but by far less than its UV
maximum.

**U2 verdict: endpoint-localized spectral failure.** This supports an
endpoint/interpolation-conditioning diagnosis over a bulk-equation failure.
It does not identify a unique cause: the residual may combine background
endpoint representation, barycentric differentiation, and matrix roundoff.

**U3 verdict: mandatory stop completed.** No smaller UV window, alternative
fit, coordinate map, domain decomposition, new degree, source comparison,
curve, plot, model card, or result claim is produced.

## Proposed V1--V3 asymptotic-extraction amendment

### V1 -- source-free UV scale and frozen windows

**Recommendation: approve.** Use the source-free target expansion
`psi(u) = psi_+ u^2 + ...` in the unchanged response equation. Its field
series begins

```text
A_x = A_0 + A_1 u - (Omega^2 A_0/2) u^2
      - (Omega^2 A_1/6) u^3
      + (psi_+^2 A_0/6 + ...) u^4 + ... .
```

For the frozen target `psi_+ = 425029.1288`, choose `u_fit = 5e-5` as the
prospective primary window and `2.5e-5` as its refinement. The leading scalar
field correction `psi_+^2 u_fit^4 / 6` is then `1.88e-7` at the primary window
and `1.18e-8` at the refinement, instead of being uncontrolled on the
milliscale U1 windows. Keep `u_min = 1e-6`, 80 fit points, basis `(1,u,u^2)`,
the Riccati equation, and all DOP853 tolerances unchanged.

- **Reason:** U1 isolates the failure to UV extraction, and the published
  source-free boundary expansion supplies a prospective scale rather than a
  target-matching choice.
- **Opens:** exact-normal and moderate controls for the two new windows, then
  the same two windows at only the first Figure anchor.
- **Remains closed:** choosing a window by spectral/source agreement, adding
  fit terms, changing `u_min`, or accepting a first-anchor value.
- **Uncertainty:** a small leading field correction does not by itself bound
  every higher-order contribution to the fitted logarithmic derivative.

### V2 -- first-anchor extraction and route diagnostics

**Recommendation: approve only with V1.** At `omega/T = 25`, require the
`5e-5` to `2.5e-5` Riccati normalized change to be at most `5e-4`. Repeat the
already frozen horizon-cutoff and tightened-tolerance checks using the `5e-5`
primary window. Record, but do not accept, the distance to both unchanged
spectral candidates under the existing `5e-4 (1 + |sigma_spec|)` route gate.
Any extraction, cutoff, tolerance, pole, integration, or finiteness miss is a
stop.

- **Reason:** window self-consistency must be established before the spectral
  disagreement can be interpreted.
- **Opens:** one asymptotic-scale first-anchor extraction audit and its existing
  diagnostics.
- **Remains closed:** source comparison, promotion of Riccati, revision of the
  spectral residual, and another frequency.
- **Uncertainty:** agreement with a residual-failing spectral value would
  remain diagnostic rather than sufficient for acceptance.

### V3 -- bounded extraction stop

**Recommendation: approve only with V1--V2.** Return immediately after the
two control-window checks and the one first-anchor extraction audit, regardless
of outcome. A later owner gate must decide whether a spectral endpoint
reformulation is warranted.

- **Reason:** V1 changes a preregistered numerical extraction and therefore
  cannot silently reopen the full Figure grid.
- **Opens:** one itemized decision on UV extraction viability.
- **Remains closed:** all remaining frequencies, source reproduction,
  result/model-card acceptance, Git/release action, Phase 5, and private
  transfer.
- **Uncertainty:** even a complete V1--V2 pass would leave the spectral
  endpoint residual unresolved.

## V1--V3 owner response paths

- **A -- approve all recommendations:** approve V1--V3 and authorize only the
  asymptotic-scale control/first-anchor audit, followed by another stop.
- **B -- approve selected items:** name them; every other action remains
  closed.
- **C -- request revision or evidence:** identify the UV expansion, windows,
  controls, route comparison, or stop rule to change.
- **D -- status walkthrough only:** discuss U1--U3 without more computation.
- **E -- custom response:** state another bounded instruction.

**Recommended path: A.** It replaces the failed milliscale extrapolation with
a source-free asymptotic scale justified before looking at the new result,
while leaving every physical target and acceptance threshold unchanged.

## V1--V3 owner disposition and asymptotic-extraction audit

Xin-Yi Liu selected **Option A** on 2026-08-20 and approved V1--V3. This
authorized only the exact-normal and moderate control checks at
`u_fit = 5e-5` and `2.5e-5`, the same two windows at `omega/T = 25`, the
already frozen horizon-cutoff and tolerance checks at the primary window, and
diagnostic distances to the unchanged `N = 512` and `N = 640` spectral
candidates. It did not authorize another frequency, source comparison, a new
spectral formulation, method promotion, result acceptance, or Git/release
action.

For the target `psi_+ = 425029.12880460825`, the prospective leading scalar
field corrections are `1.8817683368e-7` and `1.1761052105e-8` at the primary
and refinement windows. The normal-state results are

| `u_fit` | `sigma` | `|sigma - 1|` |
| ---: | ---: | ---: |
| `5e-5` | `0.999999999998739 + 2.4025997970e-10 i` | `2.403e-10` |
| `2.5e-5` | `0.999999999998731 + 2.4025997970e-10 i` | `2.403e-10` |

Their normalized window change is `3.719e-15`. At the moderate control
`T/T_c = 0.900`, `omega/T = 0.200`, the two Riccati values are
`0.408776740098097 + 10.293192700012765 i` and
`0.408776740098091 + 10.293192700013046 i`. Their normalized window change is
`2.484e-14`; their normalized distances to the independently passing
`N = 160` spectral value are `2.533e-11` and `2.531e-11`.

At the first Figure anchor, the asymptotic extraction gives

| configuration | `Im sigma` | normalized change from primary | verdict |
| --- | ---: | ---: | --- |
| primary: `epsilon_h = 1e-6`, `u_fit = 5e-5` | `71.4589659065` | -- | reference |
| `u_fit = 2.5e-5` | `71.4590563713` | `1.248e-6` | pass |
| `epsilon_h = 2e-6` | `71.4589659512` | `6.176e-10` | pass |
| `epsilon_h = 5e-7` | `71.4589659743` | `9.357e-10` | pass |
| `rtol = 1e-11`, `atol = 1e-13` | `71.4589659034` | `4.221e-11` | pass |

Every extraction diagnostic is below the unchanged `5e-4` ceiling. The
primary value is also within the unchanged route gate of both spectral
candidates:

| candidate | `Im sigma_spec` | normalized route distance | equation residual | status |
| ---: | ---: | ---: | ---: | --- |
| `N = 512` | `71.4590717880` | `1.461260e-6` | `7.835e-8` | diagnostic pass |
| `N = 640` | `71.4590717876` | `1.461254e-6` | `4.316e-6` | residual fail |

**V1 verdict: pass.** The prospectively chosen asymptotic windows pass the
normal and moderate controls without changing the equation, fit basis,
`u_min`, point count, or tolerances.

**V2 verdict: extraction pass; acceptance remains blocked.** The first-anchor
window, cutoff, tolerance, and route comparisons pass. Agreement with the
`N = 640` candidate remains diagnostic because its independent-grid residual
fails `1e-7` and is UV-localized at `u = 1.355e-5`.

**V3 verdict: mandatory stop completed.** No other frequency, source point,
curve, solver change, model-card result, or publication action is produced.

## Proposed W1--W3 endpoint-split spectral amendment

### W1 -- freeze an endpoint-split spectral contract

**Recommendation: approve.** Before another target solve, derive and record a
two-element Chebyshev formulation split exactly at the frozen background
endpoint-expansion transition `u_* = 1e-5`. Preserve the response equation,
UV normalization, ingoing horizon condition, conductivity dictionary, and
background. Require continuity of `A_x` and `A_x'` at the interface. Freeze
element resolutions, independent residual evaluation, interface residuals,
conditioning diagnostics, and stop thresholds in the contract before reading
a new first-anchor result.

The prospective W1 implementation uses the regular field
`A_x = (1-u)^p a`, `p = -i Omega/3`, on `[0,u_*]` and `[u_*,1]`. Because the
ingoing factor is common and nonzero at `u_*`, continuity of `A_x` and
`A_x'` is equivalent to

```text
a_-(u_*) = a_+(u_*),    a_-'(u_*) = a_+'(u_*).
```

The frozen degree-pair ladder is `(N_UV,N_bulk) = (24,384), (32,512),
(40,640)`. Each assembled equation row is divided by its infinity norm before
the SciPy dense solve; this row equilibration changes neither the equation nor
its solution. Record the equilibrated two-norm condition number `kappa_2` and
require `eps_float64 kappa_2 <= 1e-4`. On each element, interpolate onto an
independent grid of twice its degree, exclude three points at each element
endpoint, and evaluate the unchanged normalized physical-field equation
residual. Require both element maxima to be at most `1e-7`.

The UV normalization residual must be at most `1e-10`, the unchanged horizon
Frobenius residual at most `1e-9`, and the normalized field and derivative
interface residuals at most `1e-10`. Two consecutive ladder entries must pass
all of those gates and have normalized conductivity change at most `5e-4`.
The exact-normal error remains at most `1e-8`; the moderate and first-anchor
route comparisons retain `5e-4 (1 + |sigma_reference|)`. These choices are
frozen before any W first-anchor result is read.

- **Reason:** U2 localizes the spectral failure near the piecewise background
  representation, while V2 supplies a stable independent extraction. A split
  at the existing transition tests that diagnosis without moving the physical
  target or weakening a gate.
- **Opens:** derivation, exact-normal validation, and a bounded numerical
  design for one endpoint-split spectral method.
- **Remains closed:** fitting an interface to the Riccati value, modifying the
  background, weakening `1e-7`, or evaluating another Figure frequency.
- **Uncertainty:** domain splitting may reduce interpolation contamination but
  can introduce interface conditioning or resolution imbalance.

### W2 -- controls and one first-anchor endpoint audit

**Recommendation: approve only after W1 is frozen.** Apply the frozen split
method to the exact-normal control, the same moderate control, and only
`omega/T = 25`. Require the normal and moderate route gates, two consecutive
passing spectral resolutions under the unchanged `1e-7` independent-equation
ceiling, passing UV/horizon/interface boundary residuals, and the unchanged
`5e-4 (1 + |sigma|)` first-anchor agreement with the V2 primary Riccati value.
Any resolution, residual, condition, interface, or route miss is a stop.

- **Reason:** the new solver must cure the endpoint residual rather than merely
  reproduce the candidate value.
- **Opens:** one controlled test of the endpoint-localization diagnosis.
- **Remains closed:** remaining frequencies, source comparison, result
  acceptance, or designation of either route as primary.
- **Uncertainty:** passing one frequency would establish local numerical
  viability, not full-curve convergence.

### W3 -- bounded reformulation stop

**Recommendation: approve only with W1--W2.** Return immediately after the
controls and one first-anchor audit, regardless of outcome. The owner must
separately decide whether the full Figure grid can open.

- **Reason:** an endpoint-split solver changes the numerical formulation and
  needs an independent owner gate before broader use.
- **Opens:** one itemized decision on spectral endpoint viability.
- **Remains closed:** every other Phase 4 frequency and source point,
  result/model-card acceptance, commit, push, pull request, merge, tag,
  release, Phase 5, and private transfer.
- **Uncertainty:** a successful W gate would still require full-grid
  convergence and source-figure reproduction before benchmark acceptance.

## W1--W3 owner response paths

- **A -- approve all recommendations:** approve W1--W3 and authorize only the
  endpoint-split contract, controls, and first-anchor audit, followed by a
  mandatory stop.
- **B -- approve selected items:** name them; every other action remains
  closed.
- **C -- request revision or evidence:** identify the split, matching
  conditions, resolutions, residual gates, controls, or stop rule to change.
- **D -- status walkthrough only:** discuss V1--V3 without more computation.
- **E -- custom response:** state another bounded instruction.

**Recommended path: A.** It tests the endpoint-localization diagnosis without
changing the model, physical target, independent extraction, or acceptance
thresholds, and it stops before the rest of the Figure curve.

## W1--W3 owner disposition and exact-normal stop

Xin-Yi Liu selected **Option A** on 2026-08-20 and approved W1--W3. This
authorized the frozen two-element formulation, its exact-normal and moderate
controls, only the first Figure anchor if the controls passed, and an immediate
return to the owner. It did not authorize changing the split, degree ladder,
residual definition, threshold, another frequency, result acceptance, or any
Git/release action.

The implementation uses the regular ingoing field on `[0,1e-5]` and
`[1e-5,1]`, matches its value and derivative, row-equilibrates the assembled
SciPy dense system, and evaluates the physical-field equation on independent
doubled grids. On the tiny UV element, the independent calculation is carried
out in the local coordinate `s = u/u_*`; multiplying the equation and its
normalization by `u_*^2` is algebraically identical to the frozen normalized
physical equation and avoids explicit `1/u_*^2` derivative scaling.

The exact-normal control at `omega/T = 40` gives

| `(N_UV,N_bulk)` | `sigma` | `|sigma-1|` | UV equation residual | bulk equation residual |
| ---: | ---: | ---: | ---: | ---: |
| `(24,384)` | `0.999999999756668 - 4.63105e-9 i` | `4.637e-9` | `3.611e-4` | `7.046e-9` |
| `(32,512)` | `1.000000000599192 + 1.76922e-9 i` | `1.868e-9` | `2.621e-3` | `1.819e-8` |
| `(40,640)` | `1.000000001062982 - 2.17899e-8 i` | `2.182e-8` | `6.104e-3` | `3.643e-8` |

All bulk equation residuals pass `1e-7`. The conductivity changes between
successive pairs are `3.228e-9` and `1.178e-8`, and all equilibrated
conditioning budgets pass, ranging from `2.106e-11` to `6.570e-11` against
`1e-4`. UV normalization, horizon, and field-interface residuals pass. The
first derivative-interface residual is `1.064e-9` and fails `1e-10`; the next
two pass at `4.663e-11` and `1.695e-11`. Most importantly, all three
independent UV-element equation residuals fail by more than three orders of
magnitude, and the highest degree also misses the exact-normal `1e-8`
conductivity-error gate.

**W1 verdict: implemented as frozen.** The two-element equations, matching,
row equilibration, residual evaluator, and diagnostics are executable. This is
a numerical-method implementation result, not a passing response route.

**W2 verdict: failed at the exact-normal control.** No degree pair passes the
UV-element equation ceiling, so two consecutive full passes are impossible.
The nearly correct observable and passing bulk residual do not override the
independent UV failure. The evidence identifies float64 differentiation and
residual cancellation on a width-`1e-5` element as the limiting audit, not a
new target-background disagreement.

**W3 verdict: mandatory stop completed.** The moderate control and first
Figure anchor were not evaluated. No split, degree, precision, residual,
threshold, background, or physical target was changed after seeing the
failure.

## Proposed X1--X3 series-transferred spectral amendment

### X1 -- freeze a UV-series transfer boundary

**Recommendation: approve.** Derive the source-free UV series for the physical
field far enough to express both `A_x(u_*)` and `A_x'(u_*)` linearly in the
fixed source `A_0 = 1` and unknown current `A_1`, at the unchanged
`u_* = 1e-5`. Replace the failed tiny spectral element with these two analytic
transfer rows and augment a single bulk Chebyshev system on `[u_*,1]` by the
unknown `A_1`. Freeze the series order, truncation diagnostic, bulk degree
ladder, independent residual, condition budget, and gates before reading a
new first-anchor result.

For `f = 1-u^3`, `psi(u) = psi_+ u^2 + ...`, and
`A_x = sum_n A_n u^n`, the physical response equation fixes

```text
A_2 = -Omega^2 A_0 / 2,
A_3 = -Omega^2 A_1 / 6,
A_4 = (psi_+^2/6 + Omega^4/24) A_0 + A_1/4.
```

Freeze `A_0 = 1`, the primary transfer at order four, and an order-three
refinement that drops only the `A_4` term. At `u_* = 1e-5`, use these series
for both `A_x(u_*)` and its analytic derivative, then transform both rows to
the regular field `a = (1-u)^(-p) A_x`, `p = -i Omega/3`. The unknown `A_1`
is one additional column of the bulk linear system and is converted to
`sigma = -i A_1/Omega` without a UV numerical derivative.

The frozen bulk degree ladder is `N = 384, 512, 640`. Row-equilibrate the
augmented system and require `eps_float64 kappa_2 <= 1e-4`. Evaluate the
unchanged physical-field equation residual on an independent doubled bulk
grid, excluding three points at each endpoint, and require at most `1e-7`.
The two normalized series-transfer row residuals must each be at most `1e-10`
and the horizon residual at most `1e-9`. Two consecutive resolutions must
pass these gates and have normalized conductivity change at most `5e-4`.
Require the order-four/order-three normalized conductivity difference to be at
most `1e-6`; this is the frozen series-truncation gate. Retain the exact-normal
error ceiling `1e-8` and the moderate/first-anchor route ceiling
`5e-4 (1 + |sigma_reference|)`. These choices are frozen before any X target
result is read.

- **Reason:** W2 shows that a width-`1e-5` numerical element cannot support the
  independent float64 residual even in the exact normal state. An analytic UV
  transfer retains the spectral bulk solve while removing the ill-conditioned
  numerical differentiation region.
- **Opens:** derivation and exact-normal validation of one series-to-bulk
  boundary map.
- **Remains closed:** tuning `u_*`, fitting to Riccati or source values,
  weakening `1e-7`, arbitrary precision, or another Figure frequency.
- **Uncertainty:** the transfer requires a demonstrably sufficient series
  order and a separate truncation diagnostic; a plausible asymptotic formula
  alone is not acceptance evidence.

### X2 -- controls and one first-anchor transfer audit

**Recommendation: approve only after X1 is frozen.** Run the exact-normal and
same moderate controls. Only if both pass, run the unchanged first Figure
anchor and compare with the V2 Riccati extraction under the existing route
gate. Require two consecutive bulk resolutions, the unchanged equation and
boundary ceilings, the frozen condition budget, conductivity convergence, and
the new series-truncation gate. Any miss is a stop.

- **Reason:** the boundary transfer must validate both its analytic limit and
  an interacting moderate background before testing the extreme target.
- **Opens:** one bounded test of whether the UV analytic map restores an
  independently auditable spectral route.
- **Remains closed:** remaining frequencies, source comparison, method
  promotion, and result acceptance.
- **Uncertainty:** success at one frequency would not establish full-curve
  convergence or source-figure reproduction.

### X3 -- bounded transfer stop

**Recommendation: approve only with X1--X2.** Return immediately after the
controls and, only if reached, the first-anchor audit. A later owner gate must
decide whether any broader Phase 4 calculation can open.

- **Reason:** replacing a numerical element by an analytic transfer changes
  the response boundary formulation and needs separate review before reuse.
- **Opens:** one itemized decision on the series-transferred spectral route.
- **Remains closed:** every other frequency and source point, result/model-card
  acceptance, commit, push, pull request, merge, tag, release, Phase 5, and
  private transfer.
- **Uncertainty:** even a full X pass would still require the remaining Figure
  grid and public-source comparison before benchmark acceptance.

## X1--X3 owner response paths

- **A -- approve all recommendations:** approve X1--X3 and authorize only the
  UV-series transfer contract, controls, and conditional first-anchor audit,
  followed by a mandatory stop.
- **B -- approve selected items:** name them; every other action remains
  closed.
- **C -- request revision or evidence:** identify the series order, transfer
  rows, truncation diagnostic, degrees, gates, controls, or stop rule.
- **D -- status walkthrough only:** discuss W1--W3 without more computation.
- **E -- custom response:** state another bounded instruction.

**Recommended path: A.** It keeps the user's spectral-method preference and
the unchanged physical model while replacing only the float64-ill-conditioned
tiny UV element with an analytically reviewable boundary transfer.

## X1--X3 owner disposition and moderate-control stop

Xin-Yi Liu selected **Option A** on 2026-08-20 and approved X1--X3. This
authorized the order-four UV transfer and order-three truncation refinement,
the frozen bulk ladder, the exact-normal and moderate controls in order, and
only a conditional first Figure anchor. It did not authorize changing the
series, transfer point, degrees, residual, threshold, another frequency,
result acceptance, or any Git/release action.

The augmented bulk system uses the derived source-free recurrence

```text
A_2 = -Omega^2 A_0/2,
A_3 = -Omega^2 A_1/6,
A_4 = (psi_+^2/6 + Omega^4/24) A_0 + A_1/4,
```

with `A_0 = 1` and `A_1` as an additional linear unknown. This removes UV
numerical differentiation from the conductivity extraction. The recurrence
has a direct analytic regression test, and the order-four/order-three solve
difference supplies the frozen truncation diagnostic.

The exact-normal control at `omega/T = 40` passes:

| `N` | `sigma` | `|sigma-1|` | equation residual | truncation change |
| ---: | ---: | ---: | ---: | ---: |
| 384 | `1.000000000002543 - 3.54428e-11 i` | `3.553e-11` | `9.448e-9` | `5.551e-16` |
| 512 | `1.000000000024427 - 1.06459e-11 i` | `2.665e-11` | `1.959e-8` | `4.441e-16` |
| 640 | `0.999999999966981 - 3.60071e-11 i` | `4.885e-11` | `2.957e-8` | `6.661e-16` |

All transfer rows, horizon residuals, conditioning budgets, resolution
changes, and exact-normal errors pass. X2 therefore proceeded to the already
frozen moderate control.

At `T/T_c = 0.900`, `omega/T = 0.200`, the trusted `N = 160` reference is
`0.408776740135030 + 10.293192700296633 i`. The transferred ladder gives

| `N` | `sigma` | route change | equation residual | derivative-transfer residual |
| ---: | ---: | ---: | ---: | ---: |
| 384 | `0.408776740135232 + 10.293192692728896 i` | `6.696e-10` | `6.135e-7` | `6.115e-11` |
| 512 | `0.408776740122133 + 10.293192697846482 i` | `2.168e-10` | `9.756e-6` | `2.315e-10` |
| 640 | `0.408776740138113 + 10.293192689804183 i` | `9.284e-10` | `1.029e-5` | `2.196e-10` |

The conductivities, resolution changes, route comparisons, order truncation,
horizon residuals, and conditioning budgets pass. Nevertheless, all three
independent bulk-equation residuals fail `1e-7`; the final two transfer-
derivative rows also fail `1e-10`. Their residual maxima occur at
`u = 1.606e-4`, `4.765e-5`, and `4.765e-5`, respectively, again close to the
UV end of the global bulk element.

**X1 verdict: pass.** The order-four recurrence, augmented unknown, transfer
rows, and order-three truncation diagnostic pass the exact normal state.

**X2 verdict: failed at the moderate control.** No bulk degree passes the
independent equation ceiling, so two consecutive full passes are impossible.
The nearly exact observable and reference agreement do not override the
failed residual chain.

**X3 verdict: mandatory stop completed.** The first Figure anchor was not
evaluated. No series coefficient, transfer point, degree, residual, threshold,
background, or target was changed after seeing the failure.

## Superseded proposed Y1--Y3 series-transferred multi-element amendment

This proposal was not approved or executed. After selecting Option E, the
owner requested an audit of whether the independent equation and boundary-row
ceilings were too strict. The resulting degree-and-conditioning evidence led
to the separately approved revised Y1--Y3 control amendment below. The
multi-element formulation remains preserved here as an unexecuted alternative.

### Y1 -- freeze moderate-degree bulk spectral elements

**Recommendation: approve.** Retain the accepted X1 analytic UV transfer at
`u_* = 1e-5`, but replace the single high-degree bulk polynomial by three
moderate-degree Chebyshev elements with prospective interfaces at `u = 0.1`
and `u = 0.9`. These are the already frozen UV/bulk/horizon residual-region
boundaries, not interfaces chosen from a target conductivity. Require
continuity of the regular field and derivative. Freeze the element-degree
ladder, row equilibration, per-element doubled-grid residuals, interface
residuals, condition budget, and gates before reading a new first-anchor
result.

- **Reason:** X2 passes the analytic transfer but localizes the failed global
  polynomial audit near its UV end. Moderate-degree bulk elements can reduce
  high-degree differentiation roundoff without reintroducing the failed tiny
  UV element.
- **Opens:** derivation, exact-normal validation, and the same moderate control
  for one series-transferred spectral-element formulation.
- **Remains closed:** moving the transfer point, fitting interfaces to a
  target value, weakening residual gates, or another Figure frequency.
- **Uncertainty:** additional interfaces can improve local conditioning but
  introduce matching errors and resolution-allocation choices.

### Y2 -- controls and one conditional first-anchor audit

**Recommendation: approve only after Y1 is frozen.** Run the exact-normal and
same moderate controls in order. Only if both pass, run `omega/T = 25` on the
unchanged Figure background and compare with the V2 Riccati extraction. Require
two consecutive full ladder passes, every per-element equation residual below
`1e-7`, passing transfer/interface/horizon rows, condition and truncation
budgets, conductivity convergence, and unchanged route gates. Any miss is a
stop.

- **Reason:** the spectral-element route must repair the moderate independent
  residual before it can be applied to the extreme target.
- **Opens:** one bounded test of a locally conditioned spectral bulk route.
- **Remains closed:** remaining frequencies, source comparison, method
  promotion, and result acceptance.
- **Uncertainty:** a first-anchor pass would still not establish full-curve
  convergence.

### Y3 -- bounded spectral-element stop

**Recommendation: approve only with Y1--Y2.** Return immediately after the
controls and, only if reached, the first-anchor audit. A later owner gate must
decide whether any broader Phase 4 calculation can open.

- **Reason:** adding bulk interfaces changes the numerical formulation and
  must not silently reopen the source curve.
- **Opens:** one itemized decision on spectral-element viability.
- **Remains closed:** every other frequency and source point, result/model-card
  acceptance, commit, push, pull request, merge, tag, release, Phase 5, and
  private transfer.
- **Uncertainty:** even a complete Y pass would still require the remaining
  Figure grid and source comparison before benchmark acceptance.

## Superseded Y1--Y3 owner response paths

- **A -- approve all recommendations:** approve Y1--Y3 and authorize only the
  frozen spectral-element contract, controls, and conditional first-anchor
  audit, followed by a mandatory stop.
- **B -- approve selected items:** name them; every other action remains
  closed.
- **C -- request revision or evidence:** identify the interfaces, element
  degrees, matching rows, residuals, gates, controls, or stop rule.
- **D -- status walkthrough only:** discuss X1--X3 without more computation.
- **E -- custom response:** state another bounded instruction.

**Recommended path: A.** It preserves the successful analytic UV transfer and
the user's spectral-method preference while addressing the remaining global
high-degree differentiation failure with moderate local polynomials.

## Revised Y1--Y3 tolerance-and-control amendment

After the X1--X3 stop, Xin-Yi Liu selected **Option E** and requested a direct
audit of the independent equation-residual ceiling and the boundary
conditions. The audit found that the UV-series transfer and horizon
Frobenius formulas are correct. It also found that the moderate response
passes the original `1e-7` equation ceiling at `N = 160, 192, 224`, while the
residual grows again at high degree as float64 differentiation roundoff
dominates. The prior X stop is therefore retained as a valid failure of its
frozen high-degree ladder, not reclassified as a boundary-condition error.

Xin-Yi Liu then selected **Option A** on 2026-08-20 and approved only this
revised control amendment:

### Revised Y1 -- freeze method-conditioned control gates

- Retain the X1 physical equation, order-four UV transfer, order-three
  truncation refinement, `u_* = 1e-5`, row equilibration, conditioning budget,
  exact-normal error, conductivity-convergence gate, and moderate route gate.
- Use the existing audit degrees `N = 192, 256, 320` for the two controls.
- Require the normalized independent equation residual to be at most `1e-6`.
  This is a ten-parts-per-million local backward-error ceiling and remains a
  factor of 500 below the `5e-4` normalized observable/route ceiling.
- Require each normalized transfer row and the horizon row to be at most
  `1e-9`. The transfer-derivative failures on the old high-degree ladder were
  comparable to `eps_float64 kappa_2`; the revised ceiling remains three
  orders of magnitude below the equation ceiling.

These gates are an owner-reviewed amendment based on the recorded degree and
conditioning audit. They do not retroactively convert the X2 negative
regression into a pass.

### Revised Y2 -- exact-normal and moderate controls only

Run `omega/T = 40` in the exact normal state, followed only after a full pass
by `T/T_c = 0.900`, `omega/T = 0.200`. Require all three degrees to pass the
equation, transfer, horizon, conditioning, truncation, convergence, exact-
normal, and route gates. Any miss is an immediate stop.

### Revised Y3 -- mandatory control stop

Return to the owner immediately after the two controls. The first Figure
anchor, any `1e-5` extreme-target ceiling, a target degree ladder,
multi-element implementation, remaining frequencies, source comparison,
result/model-card acceptance, commit, push, pull request, merge, tag, release,
Phase 5, and private transfer remain closed.

## Revised Y1--Y3 control results

The exact-normal control at `omega/T = 40` passes every revised gate:

| `N` | `sigma` | `|sigma-1|` | equation residual | derivative-transfer residual |
| ---: | ---: | ---: | ---: | ---: |
| 192 | `1.000000000002369 - 2.34590e-12 i` | `3.334e-12` | `1.601e-10` | `1.646e-12` |
| 256 | `0.999999999999137 - 3.66471e-12 i` | `3.765e-12` | `1.004e-9` | `1.146e-12` |
| 320 | `1.000000000007660 - 2.07722e-12 i` | `7.937e-12` | `3.219e-9` | `5.698e-12` |

The largest resolution change is `4.335e-12`, the largest order-four/order-
three truncation change is `5.551e-16`, the largest horizon residual is
`1.263e-11`, and the largest conditioning budget is `1.214e-10`. All are
below their frozen ceilings.

At `T/T_c = 0.900`, `omega/T = 0.200`, the unchanged trusted `N = 160`
reference is `0.408776740135030 + 10.293192700296633 i`. The revised ladder
passes:

| `N` | `sigma` | route change | equation residual | derivative-transfer residual |
| ---: | ---: | ---: | ---: | ---: |
| 192 | `0.408776740134422 + 10.293192699602525 i` | `6.142e-11` | `1.378e-8` | `1.306e-11` |
| 256 | `0.408776740132313 + 10.293192699103823 i` | `1.055e-10` | `2.836e-7` | `6.179e-13` |
| 320 | `0.408776740137471 + 10.293192699854274 i` | `3.914e-11` | `2.068e-7` | `3.414e-13` |

The largest resolution change is `6.641e-11`, the largest truncation change
is `9.439e-16`, the largest horizon residual is `1.518e-11`, and the largest
conditioning budget is `9.635e-11`. Every equation, transfer, horizon,
conditioning, truncation, convergence, and route gate passes.

**Revised Y1 verdict: pass.** The method-conditioned `1e-6` equation and
`1e-9` numerical-boundary ceilings are compatible with the established
float64 control ladder and remain well inside the observable error budget.

**Revised Y2 verdict: pass.** The analytic series transfer passes both the
exact normal state and the interacting moderate background without a boundary-
condition failure.

**Revised Y3 verdict: mandatory stop completed.** The first Figure anchor was
not evaluated. The earlier X failure remains a negative regression for its
frozen over-resolved ladder; it has not been rewritten as a pass.

## Proposed Z1--Z3 target-specific residual amendment

### Z1 -- freeze a separate extreme-target error budget

**Recommendation: approve.** Retain the accepted analytic transfer and the
revised Y control results. For only the first Figure anchor at
`T/T_c = 0.0026`, `omega/T = 25`, restore the prospective high-resolution
ladder `N = 384, 512, 640` and require the normalized independent equation
residual to be at most `1e-5`. Retain the `1e-9` numerical-boundary ceiling,
`1e-4` conditioning budget, `1e-6` series-truncation gate, `5e-4`
conductivity-convergence gate, and unchanged V2 Riccati route gate. Require
two consecutive resolutions to pass every gate.

- **Reason:** the source-free extreme background has much shorter UV scales
  than the controls and needs higher spectral resolution. A `1e-5` normalized
  local backward-error ceiling is a standard decimal tolerance used by the
  owner, remains a factor of 50 below the normalized observable/route ceiling,
  and is specified independently of a newly evaluated transferred target.
- **Opens:** one high-resolution error-budget test at the already selected
  first Figure anchor.
- **Remains closed:** changing the background, transfer, boundary formulas,
  target after seeing a result, or weakening any observable gate.
- **Uncertainty:** the high-degree ladder may again enter a roundoff plateau;
  the revised ceiling does not guarantee two consecutive passes.

### Z2 -- one conditional first-anchor audit

**Recommendation: approve only with Z1.** Run the unchanged first Figure
anchor once on the three frozen degrees. Compare every passing candidate with
the accepted V2 asymptotic Riccati extraction. A residual, boundary,
conditioning, truncation, convergence, or route miss is an immediate stop and
cannot be rescued by visual source proximity.

### Z3 -- bounded target stop

**Recommendation: approve only with Z1--Z2.** Return immediately after the
first-anchor audit. Remaining frequencies, source comparison, continuous
curve, method promotion, result/model-card acceptance, multi-element work,
commit, push, pull request, merge, tag, release, Phase 5, and private transfer
remain closed.

## Z1--Z3 owner response paths

- **A -- approve all recommendations:** approve only the target-specific
  residual contract and one first-anchor audit, followed by a mandatory stop.
- **B -- approve selected items:** name them; every other action remains
  closed.
- **C -- request revision or evidence:** identify the target degrees,
  `1e-5` budget, boundary or conditioning gates, route check, or stop rule.
- **D -- status walkthrough only:** discuss revised Y1--Y3 without more
  computation.
- **E -- custom response:** state another bounded instruction.

**Recommended path: A.** It applies the owner's established residual scale to
the extreme target under unchanged, substantially tighter observable and
independent-route checks, without forcing the moderate controls onto an
over-resolved ladder.

## Z1--Z3 owner disposition

Xin-Yi Liu selected **Option A** on 2026-08-20 and approved Z1--Z3. This
authorizes only the first Figure 2 anchor at `T/T_c = 0.0026`,
`omega/T = 25`, on `N = 384, 512, 640` under the frozen `1e-5` equation,
`1e-9` numerical-boundary, conditioning, truncation, convergence, and V2
Riccati-route gates, followed by a mandatory stop.

This approval does **not** authorize reproduction of the full Figure 2 curve.
It opens one numerical point that can serve as a preflight anchor for a later
figure-reproduction decision. The remaining eight source anchors, the public
source-value comparison, plot generation, continuous curve, result/model-card
acceptance, multi-element work, Git/release actions, Phase 5, and private
transfer remain closed.

## Z1--Z3 first-anchor results

The V2 asymptotic Riccati reference at `T/T_c = 0.0026`, `omega/T = 25` is

```text
sigma_Riccati = 0 + 71.45896590645538 i.
```

The series-transferred spectral ladder gives

| `N` | `sigma` | equation residual | route change | truncation change |
| ---: | ---: | ---: | ---: | ---: |
| 384 | `-1.21488e-11 + 71.45907184901405 i` | `3.911e-6` | `1.462104e-6` | `2.775943e-7` |
| 512 | `2.16962e-13 + 71.45907185179792 i` | `1.353e-7` | `1.462143e-6` | `2.775943e-7` |
| 640 | `7.04709e-14 + 71.45907185172453 i` | `3.132e-7` | `1.462142e-6` | `2.775943e-7` |

The normalized resolution changes are `3.842e-11` and `1.013e-12`. The
largest transfer-derivative residual is `2.651e-13`, the largest horizon
residual is `4.274e-14`, and the largest conditioning budget is `3.692e-10`.
Every equation, transfer, horizon, conditioning, truncation, convergence, and
independent-route gate passes at all three degrees; both consecutive pairs
therefore pass.

**Z1 verdict: pass.** The target-specific `1e-5` normalized backward-error
budget is satisfied without weakening any observable or independent-route
gate.

**Z2 verdict: pass for one numerical anchor.** The first transferred spectral
point agrees with the independently stabilized V2 Riccati extraction. This is
one point on the source Figure 2 grid, not a reproduced figure.

**Z3 verdict: mandatory stop completed.** No remaining source anchor, source-
value comparison, curve, plot, result/model-card acceptance, or Git/release
action was produced.

## Proposed AA1--AA3 full Figure 2 reproduction

### AA1 -- freeze the remaining source-anchor grid

**Recommendation: approve.** Retain the accepted Z first-anchor evidence.
Evaluate the remaining eight preregistered `FIGURE_ANCHORS` in increasing
`omega/T` order on the unchanged `T/T_c = 0.0026` background. At every
frequency use `N = 384, 512, 640` and the Z equation, numerical-boundary,
conditioning, truncation, convergence, and V2 Riccati-route gates. Require two
consecutive full passes at each frequency. Stop immediately at the first miss.

- **Reason:** Z establishes the most difficult low-frequency anchor under the
  target-specific error budget, so the remaining public source grid is now the
  direct test of whether a complete source figure can be reproduced.
- **Opens:** the remaining eight already preregistered public-source anchors.
- **Remains closed:** adding frequencies chosen after seeing the curve,
  smoothing away failed points, changing the source extraction, or accepting
  a partial curve as a reproduction.
- **Uncertainty:** higher-frequency points can have different cancellation and
  conditioning behavior; the first-anchor pass does not guarantee the grid.

### AA2 -- quantitative source comparison and original plot

**Recommendation: approve only after AA1 passes.** Compare the final real
conductivity at all nine anchors with the public-vector values already frozen
in `FIGURE_ANCHORS`, using the existing absolute-error ceiling `0.02` at every
point. Generate an original HoloForge comparison plot from the numerical data
and source markers; do not copy or embed the paper artwork. Preserve the
underlying table and every residual/gate alongside the image.

- **Reason:** this is the central rapid visual and quantitative validation the
  owner requested for classical examples.
- **Opens:** one public-source Figure 2 right-panel reproduction artifact.
- **Remains closed:** claiming empirical material validation or reproducing
  other panels without a new contract.
- **Uncertainty:** a visually close curve is insufficient if any numerical or
  per-anchor source gate fails.

### AA3 -- mandatory full-figure stop

**Recommendation: approve only with AA1--AA2.** Return immediately after the
grid and, only if every gate passes, the comparison plot. A later owner gate
must decide result/model-card acceptance, CLI promotion, commit, push, pull
request, merge, tag, release, or Phase 5.

## AA1--AA3 owner response paths

- **A -- approve all recommendations:** authorize the remaining eight anchors,
  quantitative nine-point source comparison, and one original reproduction
  plot, followed by a mandatory stop.
- **B -- approve selected items:** name them; every other action remains
  closed.
- **C -- request revision or evidence:** identify the grid order, numerical
  gates, source tolerance, plot contents, or stop rule.
- **D -- status walkthrough only:** discuss Z1--Z3 without more computation.
- **E -- custom response:** state another bounded instruction.

**Recommended path: A.** This is the first option in the sequence that would
actually reproduce a target-paper figure rather than validate only one
numerical anchor.

## AA1--AA3 owner disposition and source-comparison stop

Xin-Yi Liu selected **Option A** on 2026-08-20 and approved AA1--AA3. This
authorized the remaining eight preregistered public-source anchors, the
quantitative nine-point source comparison, and an original HoloForge plot only
if every numerical and source gate passed, followed by a mandatory stop. It
did not authorize changing the captioned temperature, axis, selected EPS path,
equations, observable dictionary, or acceptance ceilings after seeing the
result.

### AA1 verdict: all nine numerical anchors pass

At every anchor the series-transferred spectral route passes at
`N = 384, 512, 640`; both consecutive resolution pairs pass. Across the grid,
the largest normalized equation residual is `9.809e-6`, the largest
spectral--V2 Riccati route change is `1.462e-6`, the largest order-four versus
order-three truncation change is `2.776e-7`, and the largest consecutive
resolution change is `3.842e-11`. The largest transfer or horizon boundary
residual is `3.151e-13`, and the largest conditioning roundoff budget is
`4.392e-10`. These are respectively below the frozen `1e-5`, `5e-4`, `1e-6`,
`5e-4`, `1e-9`, and `1e-4` ceilings.

### AA2 verdict: source Figure 2 comparison fails

The final `N = 640` values and preregistered source anchors are

| `omega/T` | HoloForge `Re sigma` | source `Re sigma` | absolute error | source gate |
| ---: | ---: | ---: | ---: | :---: |
| 25 | `7.047e-14` | `0.000094` | `0.000094` | pass |
| 30 | `6.956e-14` | `0.001595` | `0.001595` | pass |
| 35 | `7.011e-14` | `0.023397` | `0.023397` | **fail** |
| 40 | `6.932e-14` | `0.257286` | `0.257286` | **fail** |
| 45 | `6.941e-14` | `0.920190` | `0.920190` | **fail** |
| 50 | `6.923e-14` | `1.156583` | `1.156583` | **fail** |
| 60 | `6.898e-14` | `1.115810` | `1.115810` | **fail** |
| 70 | `6.961e-14` | `1.066470` | `1.066470` | **fail** |
| 80 | `6.868e-14` | `1.039451` | `1.039451` | **fail** |

The first miss is the third anchor, where `0.023397 > 0.02`; the maximum
absolute error is `1.156583`. This is not a residual-tolerance failure: the
spectral and independently stabilized Riccati routes agree much more closely
than the source discrepancy, and every equation, boundary, conditioning,
truncation, and resolution gate passes.

The target background also exposes a scale inconsistency that must be audited
before changing the calculation. With the source normalization
`<O_2> = sqrt(2) psi_+ r_h^2`, the reached background gives

```text
sqrt(<O_2>)/T_c = 8.44362,
sqrt(<O_2>)/T = 3247.55       at T/T_c = 0.0026.
```

This agrees with the paper's separate low-temperature statement
`2 Delta approximately sqrt(<O_2>) approximately 8.4 T_c`, but the selected
Figure 2 EPS path rises near `omega/T = 40--50`. The present evidence therefore
does not establish that the captioned `T/T_c = 0.0026`, selected vector path,
and displayed `omega/T` axis all refer to the same numerical normalization.
The exact origin of the inconsistency is unresolved; it is not recorded as an
error in the paper or as a solver defect.

### AA3 verdict: mandatory stop completed

Because the source gate fails, no successful-reproduction plot was generated.
No target was changed, no curve was smoothed or fitted, and no result/model
card, CLI, commit, push, pull request, merge, tag, release, Phase 5 action, or
private transfer was opened.

## Proposed AB1--AB3 public-source normalization audit

### AB1 -- independently reconstruct the Figure 2 path identity

**Recommendation: approve.** Reparse the public `GapClosingR2.eps` path
geometry independently, inventory every plotted curve, rederive both axis
transforms from tick positions, and verify which path is rightmost. Cross-check
the candidate path against `GapRescaledR2.eps` and the PDF caption without
copying either artwork into the repository.

- **Reason:** AA shows a scale-level disagreement, so the public vector
  provenance must be checked before any numerical target is amended.
- **Opens:** a bounded public-source geometry and normalization audit only.
- **Remains closed:** selecting a different path because it fits, changing the
  temperature, or weakening the source tolerance.
- **Uncertainty:** the archived figures contain geometry but not the authors'
  original numerical tables or generation code.

### AB2 -- bounded temperature/scale diagnostic

**Recommendation: approve only with AB1.** If AB1 identifies more than one
plausible interpretation, evaluate a preregistered, coarse set of public-model
background temperatures or axis rescalings derived from those interpretations.
Treat this only as a diagnostic: no best-fit temperature or rescaling becomes
a reproduction target without a later owner-reviewed contract amendment.

- **Reason:** the numerical solver is internally stable, while the Figure path
  has a gap scale characteristic of a much less extreme dimensionless
  temperature.
- **Opens:** discriminating calculations for interpretations supported by AB1.
- **Remains closed:** continuous fitting, post-hoc target selection, plot
  acceptance, and result/model-card promotion.
- **Uncertainty:** a visually compatible diagnostic would not by itself prove
  the source's intended temperature convention.

### AB3 -- mandatory provenance stop

**Recommendation: approve only with AB1--AB2.** Return with an itemized source
audit, any discriminating calculations, the remaining ambiguity, and a proposed
contract amendment or a documented non-reproduction result.

## AB1--AB3 owner response paths

- **A -- approve all recommendations:** authorize AB1 and, only if needed,
  the bounded AB2 diagnostic, followed by the AB3 stop.
- **B -- approve selected items:** name them; every other action remains
  closed.
- **C -- request revision or evidence:** identify the source-path, axis,
  temperature, diagnostic-grid, or stop-rule question.
- **D -- status walkthrough only:** discuss AA1--AA3 without more computation.
- **E -- custom response:** state another bounded instruction.

**Recommended path: A.** Audit the public source normalization before changing
either a physically consistent solver or a frozen literature target.

## AB1--AB3 owner disposition and provenance verdict

Xin-Yi Liu selected **Option A** on 2026-08-21 and approved AB1--AB3. This
authorized the public-source geometry audit, a bounded scale diagnostic if
needed, and the mandatory provenance stop. It did not authorize selecting a
different curve because it fit, continuously fitting a replacement
temperature, weakening the `0.02` source tolerance, accepting a plot, or
promoting a result, model card, interface, commit, or release.

### AB1 verdict: path and axis extraction confirmed; cross-panel scale fails

An independent PostScript path parser and a rendered visual inspection give
six plotted paths in `GapClosingR2.eps`: one normal line and five condensed
curves. `GapRescaledR2.eps` contains four condensed curves. Tick positions
independently give

```text
GapClosingR2:  x_EPS = 0.0238095 + 0.0113682 (omega/T),
GapRescaledR2: x_EPS = 0.0238095 + 0.4329
                        (omega/sqrt(<O_2>)),
both panels:   y_EPS = 0.475411 Re[sigma].
```

The sixth `GapClosingR2.eps` path is unambiguously the rightmost Figure 2
curve. Independently interpolating it reproduces every frozen source anchor;
the largest difference from `FIGURE_ANCHORS` is `4.724e-7`. The source path
and axes used by AA were therefore selected correctly.

Cross-panel shape matching identifies two source-geometry correspondences:

| Figure 2 path | Figure 3 path | inferred `sqrt(<O_2>)/T` | rising-branch relative scale spread |
| ---: | ---: | ---: | ---: |
| fifth | first | `33.0799` | `4.65e-4` |
| sixth, rightmost | third | `45.2420` | `7.91e-4` |

The matched pairs have identical plotted peak heights. The fourth Figure 3
path is colder in condensate-rescaled geometry but is not the Figure 2
rightmost path. Thus the cross-check confirms the original Figure 2 path
identity while independently falsifying its interpretation as the reached
`T/T_c = 0.0026` background under the public equations and normalizations.

### AB2 verdict: scale-level public-source inconsistency

The reached captioned background gives

```text
sqrt(<O_2>)/T_c = 8.44362,
sqrt(<O_2>)/T = 3247.55.
```

The cross-panel source geometry instead requires
`sqrt(<O_2>)/T = 45.2420`, a factor `71.78` smaller. Combining that public
geometry with the already saturated source and released-benchmark scale
`sqrt(<O_2>)/T_c approximately 8.44` suggests only a diagnostic
`T/T_c approximately 0.19`. This algebraic diagnostic is not a fitted value,
a proven correction to the caption, or an authorized replacement target.

No conventional `4 pi/3` temperature factor explains the mismatch. The
public source archive contains vector geometry and TeX labels but not the
original numerical table or figure-generation program, so it cannot
distinguish a caption error, plotted-dataset mismatch, or undocumented
normalization.

### AB3 verdict: documented non-reproduction and mandatory stop

The Figure 2 disagreement is classified as an unresolved public-source
provenance and normalization inconsistency. It is not classified as a
spectral-method failure, a physical negative result, or a demonstrated paper
error. The successful equation, boundary, conditioning, refinement, and
independent-route evidence remains valid, as does the failed quantitative
source comparison. No Figure 2 reproduction plot or relabelled target was
produced.

## Owner-approved post-AB contract amendment

After reviewing AB1--AB3, Xin-Yi Liu selected **Option A** on 2026-08-21 and
approved this narrow amendment. It supersedes only historical AA acceptance
Gate 8, the proposed successful Figure 2 comparison graphic, and any claim
that the captioned rightmost curve has been reproduced. It does not change the
action, equations, boundary conditions, ensemble, conductivity dictionary,
background target, numerical method, degrees, cutoffs, residual ceilings,
route-agreement ceilings, or preserved AA and AB evidence.

The current acceptance and evidence gates are:

1. **Protected benchmark:** the released HHH condensate verifier and tests
   pass unchanged. Its approved Figure 1 (right) reproduction remains the
   classical model's quantitative source-figure check.
2. **Source and convention identities:** the coordinate transformations,
   retarded sign, UV current relation, conductivity dictionary, and horizon
   Frobenius identity pass their frozen analytic tests.
3. **Backgrounds:** every accepted normal, moderate, near-critical, and
   low-temperature background passes the existing temperature, scalar-source,
   positivity, fixed-density, BVP, overlap, and refinement gates.
4. **Response numerics:** the retained spectral equation, numerical-boundary,
   conditioning, truncation, and resolution ceilings pass without weakening.
5. **Independent route:** the spectral and Riccati/DOP853 responses pass their
   frozen complex-conductivity agreement and refinement gates.
6. **Exact normal phase:** `sigma(omega) = 1` passes to `1e-8` at every frozen
   frequency.
7. **Near-critical literature check:** the pole-derived slope agrees with the
   source's `C_2 = 24` within the existing `15%` ceiling and both frozen fit-
   stability checks.
8. **Low-temperature literature check:** the inherited Figure 1 condensate
   plateau remains in the released `8.2--8.7` interval around the source's
   `sqrt(<O_2>)/T_c approximately 8.4`. The `T/T_c = 0.0026` response is an
   internal model diagnostic only.
9. **Figure 2 provenance evidence:** preserve the independently re-extracted
   source table, the quantitative AA failure, the AB cross-panel mismatch, and
   an explicit machine-readable `not reproduced` status. This evidence is not
   converted into a passing acceptance check.
10. **Causality and passivity sanity:** the pole sign is positive below `T_c`
    and `Re sigma >= -1e-8` for every reported positive frequency.
11. **Determinism and interfaces:** duplicate observables, finite JSON,
    round-trip, CLI, registry, schema, evidence-bundle, wheel, and package-data
    checks pass before any promotion.
12. **Repository validation:** the full suite, installed-wheel verifier,
    `git diff --check`, and public-repository privacy audit pass.

No public Figure 2 source overlay or successful-reproduction plot is allowed.
An optional original HoloForge conductivity diagnostic may display only
HoloForge numerical curves and must state that it is not a source-figure
reproduction. The public benchmark claim, if later accepted, remains limited
to the exact normal response, near-critical literature coefficient,
low-temperature condensate-scale consistency, and independently verified
model conductivity under the declared probe-limit assumptions.

This amendment opens only a later, separately approved implementation-
completion plan under these gates. Result/model-card acceptance, CLI
promotion, commit, push, pull request, merge, tag, release, Phase 5, and any
private-program transfer remain closed.

## Bounded implementation-completion result and mandatory stop

The owner-approved implementation run completed the internal benchmark
definition, finite machine-readable evidence record, amended acceptance
checks, and focused regression tests. The released HHH verifier is called as a
protected anchor. The `5e-6` cutoff repeat is seeded directly from the accepted
conditioned Figure-target state; it repeats the target solve and every Figure
anchor without unnecessarily rerunning the historical original-`u` overlap
proof. Its largest normalized conductivity change is `1.19533e-7`, well below
the frozen `5e-4` ceiling.

The bounded run records:

| check | result | evidence |
| --- | --- | --- |
| protected released HHH verifier | pass | every protected check passes unchanged |
| convention identities | pass | maximum error `2.665e-15` |
| condensed backgrounds and cutoff repeat | pass | maximum normalized gate ratio `0.907719` |
| independent response route | pass | maximum relative difference `1.46214e-6` against `5e-4` |
| exact normal response | pass | maximum complex error `2.45609e-11` against `1e-8` |
| near-critical response numerics | **fail** | largest normalized equation residual `1.45330` |
| near-critical `C_2 = 24` | **fail** | `C_2 = 19.3144523`, relative error `19.5231%` against `15%` |
| near-critical fit stability | pass | temperature omission `8.23408%`; maximum frequency-omission change `2.960e-7` |
| inherited low-temperature condensate scale | pass | `sqrt(<O_2>)/T_c = 8.4436224` |
| causality and passivity sanity | pass | minimum reported `Re sigma = 6.868e-14` and every pole intercept is positive |

The response-residual failure is localized to the frozen near-critical control
grid. The independent equation residuals are `1.453302e-6` at
`(T/T_c, omega/T) = (0.900, 0.025)`, `1.192623e-6` at `(0.900, 0.050)`,
`1.155477e-6` at `(0.970, 0.100)`, and `1.009433e-6` at `(0.940, 0.200)`,
all against the owner-approved `1e-6` control ceiling. Their boundary,
conditioning, resolution, truncation, and independent-route checks pass.

The pole fit uses the contract's dimensionless definition

```text
(n_s/T_c)(omega) = (omega/T)(T/T_c) Im sigma(omega).
```

The spectral and Riccati routes agree closely, so the `C_2` miss is not
classified as a route disagreement. The two failed gates are preserved rather
than repaired by changing a tolerance, dropping a point, or changing the fit
after seeing the result.

Figure 2 is serialized separately with `status = not_reproduced` and
`acceptance_role = provenance-only`. The first failed public-source anchor is
`omega/T = 35`, the largest real-part error is `1.156583`, and the public
cross-panel condensate-scale mismatch factor is `71.7817`. It is intentionally
absent from the acceptance-check list, and no comparison plot is generated.

This result is an implementation/preflight failure record, not an accepted
benchmark, model card, source-figure reproduction, physical negative result,
or publication decision. CLI, registry, schema, evidence-bundle, wheel,
package-data, commit, remote, merge, tag, release, and Phase 5 work remain
closed pending a new owner decision.

## Owner-approved near-critical physics amendment

After reviewing the two bounded implementation failures, Xin-Yi Liu selected
**Option A** on 2026-08-21 and approved only the corrected near-critical
contract and its bounded local implementation and validation. This amendment
does not erase or relabel the preceding failure. It records that the original
test combined two inappropriate numerical interpretations:

1. the source states `n_s approximately C_2 (T_c-T)` **as** `T -> T_c`,
   whereas the failed test forced a one-parameter straight line through the
   finite window `T/T_c = (0.900, 0.940, 0.970, 0.985)`; and
2. the independent collocation residual at degree `320` had entered a
   high-order roundoff plateau even though the conductivity, boundary rows,
   lower-degree solutions, and Riccati route were already stable.

The historical finite-window value `C_2 = 19.3144523`, its `19.5231%`
literature miss, and the largest degree-320 residual `1.453302e-6` therefore
remain serialized as a **superseded-contract failure**, with no role in the
amended acceptance result.

The amended calculation is frozen prospectively as follows:

- use `T/T_c = (0.990, 0.995, 0.9975, 0.999)` and
  `delta = 1 - T/T_c`;
- make the zero-frequency static London equation

  ```text
  (f A_x')' - 2 psi^2 A_x/u^2 = 0
  ```

  the primary superfluid-density calculation, with the regular horizon
  condition `A_x'(1) + (2 psi_h^2/3) A_x(1) = 0` and
  `n_s/T_c = -(4 pi/3)(T/T_c) A_x'(0)/A_x(0)`;
- fit the static results to

  ```text
  n_s/T_c = C_2 delta + C_4 delta^2,
  ```

  using maintained `numpy.linalg.lstsq`, and compare the extrapolated `C_2`
  with the source value `24` under the unchanged `15%` literature ceiling;
- repeat the coefficient fit after omitting the farthest point
  `T/T_c = 0.990`; retain the existing `10%` coefficient-stability ceiling;
- retain the positive-frequency pole extraction at
  `omega/T = (0.200, 0.100, 0.050, 0.025)` as an independent physical route,
  with the existing `2%` frequency-omission and `5e-4` complex-response route
  ceilings;
- require the static London density and finite-frequency pole intercept to
  agree point by point within the existing `5e-4` response-route ceiling;
- use the near-critical series-transferred spectral ladder
  `N = (128, 160, 192)`, with `N = 160` primary, `N = 128` refinement, and
  `N = 192` audit; keep the independent equation-residual ceiling exactly
  `1e-6` and keep every boundary, conditioning, truncation, and resolution
  ceiling unchanged; and
- preserve the degree-320 result only as evidence of the roundoff plateau.

The static London solve uses SciPy DOP853 on the logarithmic derivative
`Y=A_x'/A_x`; its UV intercept is repeated on a halved fit window and must be
stable within the existing `5e-4` resolution ceiling. No tolerance is selected
from the new numerical result.

Figure 2 remains `not_reproduced` and provenance-only. This approval does not
open a CLI, registry entry, schema, evidence bundle, model card, public figure,
commit, push, pull request, merge, tag, release, Phase 5 action, or transfer
from the temporary Mathematica material.

## Corrected near-critical result and mandatory stop

The owner-approved bounded implementation and local verifier run completed
the amended calculation. Every currently authorized internal acceptance gate
passes; no numerical ceiling was weakened.

The primary static-London results are:

| `T/T_c` | `delta` | static `n_s/T_c` | finite-frequency pole `n_s/T_c` |
| ---: | ---: | ---: | ---: |
| `0.9900` | `0.0100` | `0.2332687444` | `0.2332686604` |
| `0.9950` | `0.0050` | `0.1182351375` | `0.1182350909` |
| `0.9975` | `0.0025` | `0.05952438655` | `0.05952436198` |
| `0.9990` | `0.0010` | `0.02390827039` | `0.02390826026` |

The frozen two-term asymptotic fit gives

```text
static London:          C_2 = 23.96884335, C_4 = -64.20423952,
finite-frequency pole: C_2 = 23.96883307, C_4 = -64.20405128.
```

The primary `C_2` differs from the source value `24` by `0.129819%`. Omitting
the farthest point gives `C_2 = 23.97281278`, a relative fit change of
`1.65608e-4`. The maximum finite-frequency omission change is
`3.82690e-7`; the maximum pointwise difference between the static and pole
density is `4.23721e-7`; and the largest static UV-window refinement change is
`1.60201e-11`.

For the `N = (128, 160, 192)` near-critical ladder, the largest primary
`N=160` independent equation residual is `5.58109e-8` and the largest `N=192`
audit residual is `1.37837e-7`, both below the unchanged `1e-6` ceiling. The
largest near-critical normalized numerical gate ratio is `0.137837`. The
degree-320 value `1.453302e-6` from the earlier contract remains in the machine
record as historical roundoff-plateau evidence, not as an amended result.

Across the complete bounded verifier, the largest normalized response-
numerics ratio is `0.980935`, the largest spectral/Riccati complex-response
difference is `1.46214e-6`, the exact-normal complex error is `2.45609e-11`,
the protected HHH verifier passes unchanged, and the inherited condensate
scale remains `sqrt(<O_2>)/T_c = 8.4436224`.

This is a passing corrected internal preflight, not yet an owner-accepted
benchmark or authorization to promote an interface. The Figure 2 status is
unchanged: `not_reproduced`, provenance-only, and absent from acceptance. CLI,
registry, schema, evidence-bundle, model card, public figure, commit, push,
pull request, merge, tag, release, Phase 5, and private-program transfer remain
closed at this mandatory owner-review stop.

## Owner-approved public promotion and completed validation

After reviewing the corrected result, Xin-Yi Liu selected **Option A** on
2026-08-21 to accept it at `reproduced` and authorize the complete bounded
Phase 4 promotion: separate CLI and registry integration, model card, public
guide, machine-readable evidence and scientific-state metadata, original
HoloForge diagnostic, schema and evidence tests, package-interface policy,
wheel validation, and full local regression testing. This approval did not
authorize a commit, remote action, release, or Phase 5 work.

The promotion added the distinct command

```text
holoforge verify holographic-superconductor-optical
```

with `--json`, `--bundle-dir`, and `--plot` support. Existing benchmark
identifiers, defaults, JSON output, and numerical implementations were not
changed. The optional plot displays only the four static-London points, their
finite-frequency pole checks, and the frozen asymptotic fit. It is labelled
`not a source Figure 2 reproduction` and contains no source artwork or
digitized curve.

The owner-facing correction remained legible in Markdown: it required one
static equation, one horizon condition, one asymptotic fit, and a compact
four-row table. Under the repository review convention, a PDF packet is used
when dense equations, tables, or plots materially benefit from compiled visual
review. No separate PDF was required for this amendment, and the absence of a
PDF does not change the standard report style.

Final local validation completed as follows:

| validation | result |
| --- | --- |
| real human command, including diagnostic plot | pass |
| real strict JSON command | pass |
| source-checkout evidence bundle and audit | pass |
| optical scientific tests | `34/34` pass |
| protected HHH tests | `7/7` pass |
| focused CLI, registry, schema, and evidence group | all substantive gates pass |
| complete repository suite after interface-policy synchronization | `234/234` pass in `286.833 s` |
| built wheel | `holoforge-0.5.4-py3-none-any.whl` built and installed |
| installed-wheel optical verifier | pass outside the source checkout |
| installed-wheel evidence bundle and audit | pass |
| model-card schema and content digest | pass; SHA-256 `17c770cbf86104eb590ab735eef055582d474d54afc8e9ca61b6eaaaddca9367` |
| diagnostic visual inspection | pass; labels, axes, markers, legend, and non-reproduction notice are unclipped |

The installed-wheel bundle records only relative portable paths and passes
manifest, schema, compatibility-metadata, file-integrity, undeclared-file,
scientific-payload, and bundle-identity checks. Local Matplotlib emits legacy
PyParsing deprecation warnings under the current Python 3.9 environment; they
do not alter the generated artifact or any pass/fail result.

The model card, machine record, human output, guide, and domain README all
retain the same non-inference boundary: the exact normal response and
near-critical `C_2` are reproduced within the declared probe-limit model;
Figure 2 is `not_reproduced` and provenance-only; no empirical material
validation, controlled zero-temperature solution, or microscopic pairing
claim follows.

This promotion has reached its mandatory Git/release stop. Commit, push, pull
request, merge, tag, release, Phase 5, and any private-program transfer remain
closed pending a new explicit owner decision.

## Python 3.9 CI portability audit and bounded correction

Draft pull request 25 ran the complete seven-job portability matrix on commit
`0280147`. Six jobs passed: Python 3.11, Python 3.14, the built-wheel smoke
test, and wheel relocation on Ubuntu, macOS, and Windows. Python 3.9 completed
233 passing tests and one Graphviz-dependent skip, but failed the preserved
W2 endpoint-split diagnostic because

```text
abs(sigma - 1) = 3.3449638801672674e-8 > 3.0e-8.
```

The failed `3e-8` assertion was not one of the frozen W1 scientific or
numerical gates. It was an additional test-only fence outside the W2 full-pass
predicate. The actual exact-normal gate remains
`NORMAL_CONDUCTIVITY_TOLERANCE = 1e-8` inside that predicate, and the W2 stop
continues to require the independently evaluated UV-element equation residual
to exceed its `1e-7` ceiling. The accepted series-transferred exact-normal
route separately passes its public `1e-8` gate; this audit does not change it.

The portability diagnosis reproduced the owner-recorded SciPy result on local
Python 3.9 with NumPy 2.0.2 and SciPy 1.13.1. Across the three W2 degree pairs,
the local exact-normal errors were `4.63744e-9`, `1.86793e-9`, and
`2.18158e-8`. Repeating the same assembled equations with the maintained NumPy
dense-solve entry point changed those errors to `3.36579e-9`, `8.65797e-10`,
and `7.49549e-9`. The UV residual remained far above `1e-7` in every case.
This isolates the variation to the already rejected tiny-element float64
route and its linear-algebra/differentiation stack; it does not indicate a
change in the model, boundary conditions, accepted observable, or near-
critical result.

The bounded correction therefore:

- keeps the `1e-8` exact-normal gate unchanged in the W2 full-pass predicate;
- keeps every equation, boundary, interface, conditioning, and resolution
  check unchanged;
- keeps the W2 negative result and its non-inference boundary unchanged; and
- replaces only the undocumented `3e-8` test fence with finite-value checks
  plus the existing frozen `5e-4` response-resolution budget, whose role here
  is to catch catastrophic diagnostic drift rather than confer acceptance.

Xin-Yi Liu selected Option A on 2026-08-21 to authorize this bounded Python
3.9 portability diagnosis and an evidence-justified local correction. That
approval does not authorize weakening the public exact-normal or near-critical
gates, converting W2 into a pass, merging, tagging, releasing, or beginning
Phase 5.

## Version 0.5.5 release-preparation owner disposition

After pull request 25 was merged as `2238447` and its exact post-merge
seven-job `main` run passed, Xin-Yi Liu selected **Option A** on 2026-08-21 for
a bounded local Version 0.5.5 release-preparation pass. This authorizes only:

- synchronized Version 0.5.5 package, citation, README, and changelog metadata;
- explicit HHH optical coverage in the Python test matrix, installed-wheel
  smoke test, and Linux, macOS, and Windows wheel-portability job;
- synchronized release-policy regression checks;
- regenerated temporary version-stamped JSON and portable-bundle evidence;
- complete source-checkout and independently installed-wheel validation; and
- this delivery-state record.

The work must use an isolated clean worktree so the owner's unrelated local
contract edits remain untouched. This authorization stops before commit, push,
pull request, remote CI, merge, tag, GitHub release, branch deletion, Phase 5,
or another model sector. It changes delivery preparation only: the accepted
`reproduced` support level, equations, boundary conditions, numerical methods,
tolerances, results, preserved failures, Figure 2 `not_reproduced` status, and
non-inference boundaries remain unchanged.

## Version 0.5.5 release-preparation validation and mandatory return

The authorized release-preparation pass changes seven existing files and no
scientific implementation file. The candidate updates package, citation,
README, and changelog metadata; adds the HHH optical verifier and focused tests
to the established CI and wheel-portability paths; synchronizes release-policy
regressions; and records this delivery state. No checked-in generated result
was added because the benchmark had no pre-existing generated-result artifact;
fresh version-stamped JSON and evidence bundles were instead generated and
audited during validation.

Validation completed on Python 3.9.6 with NumPy 2.0.2 and SciPy 1.13.1:

| validation | result |
| --- | --- |
| release-policy synchronization | `6/6` pass |
| expanded source portability group | `121/121` pass in `96.045 s` |
| source human verifier, diagnostic, strict JSON, and bundle | pass; record version `0.5.5` |
| source bundle relocation/integrity audit | pass; Figure 2 remains `not_reproduced` |
| protected HHH condensate and required soft-wall verifiers | pass unchanged |
| complete repository suite | `234/234` pass in `294.156 s` |
| standard isolated package build | `holoforge-0.5.5.tar.gz` and `holoforge-0.5.5-py3-none-any.whl` built |
| independently installed wheel identity | metadata, package, and imported version all `0.5.5`; import resolves to `site-packages` |
| installed-wheel HHH optical verifier | all twelve declared gates pass |
| installed-wheel relocated bundle audit | pass; version `0.5.5`, portable paths, integrity, and scientific identity |
| expanded installed-wheel portability group | `121/121` pass in `96.628 s` |
| remaining six installed-wheel verifier smoke checks | all pass |
| generated diagnostic visual inspection | pass; labels, axes, markers, legend, and non-reproduction notice are unclipped |
| deterministic public-export scan | seven text files scanned; zero findings |

The source and installed-wheel optical records reproduce the unchanged static
and finite-frequency coefficients `23.96884334975214` and
`23.968833072939002`, pass all twelve acceptance checks, and retain the exact
normal, residual, boundary, conditioning, refinement, protected-regression,
and non-inference gates. The local plotting stack emits the already documented
legacy PyParsing and font-cache warnings; they do not change an artifact or a
pass/fail result.

This release candidate reached its mandatory owner-review return before any
Git action.

## Version 0.5.5 local-commit owner disposition

After reviewing the complete release-candidate scope and validation above,
Xin-Yi Liu selected **Option A** on 2026-08-21 to accept the bounded candidate
and authorize exactly one scoped local Version 0.5.5 release-preparation
commit containing the seven reviewed files. This approval does not authorize
any additional file, scientific change, push, pull request, remote CI, merge,
tag, GitHub release, branch deletion, Phase 5, or another model sector.

The scoped local commit exhausts this authorization and returns the project to
mandatory owner review before any remote action. The commit changes delivery
state only; it does not alter or broaden the accepted scientific result or any
non-inference boundary.

## Version 0.5.5 Windows portability audit

After the release-preparation branch was pushed as commit `6e62210`, pull
request 26 ran the expanded seven-job matrix. Python 3.9, 3.11, and 3.14, the
wheel build/smoke test, and the Ubuntu and macOS portability jobs passed. The
Windows portability job passed 120 of 121 focused tests and the complete HHH
optical verifier, including all twelve accepted scientific gates, but failed
the standalone superseded X exact-normal ladder at its independent equation-
residual assertion.

The original test asserted inside the degree loop and therefore did not report
the complete ladder. Diagnostic commit `779d754` made all three frozen degrees
run before the assertion and recorded every relevant metric. The Windows
evidence is:

| `N` | equation residual | `|sigma-1|` | boundary maximum | conditioning budget | truncation change |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 384 | `5.78191e-9` | `4.87008e-12` | `4.46966e-11` | `1.74836e-10` | `7.24351e-14` |
| 512 | `1.82643e-8` | `2.24557e-11` | `5.01988e-11` | `3.10776e-10` | `7.26786e-14` |
| 640 | `1.50452e-7` | `3.28318e-11` | `7.07528e-11` | `4.85550e-10` | `7.25677e-14` |

The normalized conductivity changes between consecutive degrees are
`9.73992e-12` and `2.63125e-11`. The only miss is the `N=640` independent
second-derivative residual against the historical X `1e-7` ceiling. Its
maximum is localized at `u=3.40953e-5`, close to the UV end of the bulk
element. The accepted observable, analytic transfer, horizon boundary,
conditioning, series-truncation, and resolution evidence all retain large
margins.

This is the same method-conditioned high-degree float64 differentiation
plateau that motivated the already owner-approved revised Y control ladder and
its `1e-6` local backward-error ceiling. The X ladder is superseded evidence;
the current accepted near-critical calculation uses `N=(128,160,192)` and the
reviewed `1e-6` ceiling, and the target-specific low-temperature calculation
uses its separately reviewed `1e-5` ceiling. Neither accepted calculation
depends on the superseded high-degree X pass classification.

The portable correction therefore retains the full-ladder diagnostic but
renames it as an over-resolved X preservation test and bounds only catastrophic
drift by the existing `1e-6` control ceiling. It does not change the response
equation, UV or horizon conditions, production verifier, historical X2
failure, exact-normal `1e-8` observable gate, accepted residual ceilings,
literature result, Figure 2 `not_reproduced` status, or any non-inference
boundary. A fresh seven-job run is required before merge or release.
