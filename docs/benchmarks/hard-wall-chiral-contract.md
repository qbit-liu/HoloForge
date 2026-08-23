# Hard-wall chiral QCD benchmark contract

## Status and authorization boundary

This document began as the pre-implementation owner-review contract for Phase
3 of the classical benchmark sequence and now records the bounded stops,
amendments, accepted result, release preparation, and public release closure.
It is public-source Forge/Verify work. Xin-Yi Liu approved Decisions C1--C6,
R1--R3, and the final result Decisions 1--5 through separate Option A
decisions on 2026-08-20. The accepted result retains material AI provenance
and the scientific limitations below.

- **Completed:** Phase 0 spectral infrastructure, Phase 1 Gubser--Nellore ED,
  and Phase 2 Gubser--Rocha EMD are released in Version 0.5.3. Phase 3 is
  released in Version 0.5.4 after the frozen contract, UV stop, R1--R3
  amendment, bounded implementation, owner-accepted result, scientific commit
  (`9c6c3b0`), release-preparation commit (`2d1abd2`), pull request 24, green
  remote CI, merge commit (`a79f944`), annotated tag, and public release.
- **Current:** Phase 3 scientific and delivery work is closed.
- **Proposed next:** prepare the separate Phase 4 optical-conductivity
  scientific contract and owner-review packet only; implementation remains a
  later owner decision.

Each historical authorization below remained bounded at the time it was
given. Later owner decisions opened the recorded remote and release actions;
they did not retrospectively broaden an earlier authorization or change the
frozen scientific contract.

## Recommendation

Add one bottom-up hard-wall chiral QCD benchmark based on Erlich, Katz, Son,
and Stephanov. Reuse the existing HoloForge hard-wall vector benchmark as a
protected regression anchor, and extend the verified scope to the transverse
axial, pion/longitudinal-axial, decay-constant, and rho-pion-pion sectors.

Use Chebyshev--Gauss--Lobatto collocation as the primary method. Use SciPy
adaptive boundary-value collocation at decreasing finite UV cutoffs as an
independent route for selected axial and pion quantities. Reproduce the seven
Model A entries in source Table II from the printed Model A parameters without
refitting them. The source paper contains no figure, so the central table is
the required quick quantitative reproduction target.

## Primary public source and provenance

Joshua Erlich, Emanuel Katz, Dam T. Son, and Mikhail A. Stephanov,
"QCD and a holographic model of hadrons," *Physical Review Letters* **95**,
261602 (2005),
[arXiv:hep-ph/0501128v2](https://arxiv.org/abs/hep-ph/0501128),
[doi:10.1103/PhysRevLett.95.261602](https://doi.org/10.1103/PhysRevLett.95.261602).

The public arXiv v2 PDF and TeX source inspected for this contract have
SHA-256 digests

```text
PDF:            b2f29ea72e37467b0f54d169948bce86b873f138009443de333512b4350b0881
source archive: 3591ab1c15b727f31219a4f3b581b45af396de87fea18f8d49b65833e463b3aa
```

The contract uses source Eqs. (1)--(3), (5), (11), (14), (16)--(20), and
(22), together with Model A in Table II. The PDF and complete TeX source were
inspected directly. No source PDF, TeX archive, or copyrighted table image
will be committed. HoloForge will regenerate a comparison table and, if
useful, a plot of computed-to-source ratios from its own numerical results.

## Claim and review state before implementation

| Item | Support level | Review state |
| --- | --- | --- |
| Source action, equations, boundary conditions, and Table II values | `established-source` | AI-transcribed, awaiting owner review |
| Dimensionless rewriting and exact-endpoint factorizations below | direct derivation from the source equations | AI-assisted, awaiting owner review |
| Future HoloForge calculation and Model A table reproduction | not yet supported | closed until every gate passes and the owner accepts the result |
| Phenomenological precision, empirical QCD validation, or superiority to other holographic QCD models | not a benchmark result | closed |

Human review may change the review state but must not erase AI provenance or
raise the support level beyond the evidence.

## Physical model and frozen parameters

Use the source's two-flavor `SU(2)_L x SU(2)_R` bottom-up model on a slice of
AdS5, with the AdS radius set to one, `0 < z <= z_m`, and gauge choice
`A_z = 0`. In the source convention,

```text
S = integral d^5x sqrt(g) Tr{
      |D X|^2 + 3 |X|^2
      - [F_L^2 + F_R^2]/(4 g5^2)
    },

D_mu X = partial_mu X - i A_L,mu X + i X A_R,mu,
X_0(z) = (1/2) [m_q z + sigma z^3] 1_2,
v(z) = m_q z + sigma z^3.
```

Match the vector-current OPE as in source Eq. (11):

```text
g5^2 = 12 pi^2/N_c,   N_c = 3,   g5 = 2 pi.
```

Freeze the printed Model A inputs, with no new fit:

```text
z_m^{-1}       = 323 MeV,
m_q            = 2.29 MeV,
sigma^{1/3}    = 327 MeV.
```

These values and the source table are rounded. Consequently, the table gate
below tests reproduction at one-percent accuracy rather than treating the
printed digits as exact hidden fit data.

## Dimensionless equations

Let

```text
u = z/z_m in [0, 1],
lambda = q^2 z_m^2,
mhat = m_q z_m,
sigmahat = sigma z_m^3,
v(u) = mhat u + sigmahat u^3.
```

Primes in the rest of this contract mean `d/du`.

### Vector sector

The normalizable vector modes obey source Eq. (5):

```text
d/du [(1/u) V'] + (lambda/u) V = 0,
V(0) = 0,
V'(1) = 0,
integral_0^1 du V^2/u = 1.
```

The exact zero-cutoff spectrum is fixed by `J_0(sqrt(lambda)) = 0`. Phase 3
must call or compare with the existing `hard-wall-vector` implementation; it
must not silently replace that benchmark's equations, defaults, or public
records.

### Transverse axial sector

The normalizable axial-vector modes obey source Eq. (16):

```text
d/du [(1/u) A'] + (lambda/u) A
  - g5^2 v(u)^2 A/u^3 = 0,
A(0) = 0,
A'(1) = 0,
integral_0^1 du A^2/u = 1.
```

The lowest positive eigenvalue gives `m_a1 = sqrt(lambda_a1)/z_m`.

### Pion and longitudinal-axial sector

Write `A_mu = A_mu,perp + partial_mu phi`. The coupled source Eqs. (17) and
(18), multiplied only by known powers of `u` to remove removable endpoint
singularities, are

```text
u^2 phi'' - u phi' + g5^2 v(u)^2 [pi - phi] = 0,

-lambda phi' + g5^2 [v(u)/u]^2 pi' = 0,

phi(0) = 0,
pi(0) = 0,
phi'(1) = 0.
```

The lowest positive physical eigenvalue gives
`m_pi = sqrt(lambda_pi)/z_m`. Spurious infinite, complex, negative, gauge, or
constraint-null eigenpairs from the generalized matrix pencil are rejected by
prospective algebraic rules and by direct residual evaluation; no eigenpair
may be selected because it is close to the source number.

For canonical four-dimensional pion normalization, introduce dimensionless
profiles by `phi_source(z) = z_m phi(u)` and
`pi_source(z) = z_m pi(u)`. Their common scale is fixed by

```text
integral_0^1 du [
  phi'(u)^2/(g5^2 u)
  + v(u)^2 [pi(u)-phi(u)]^2/u^3
] = 1.
```

### Decay constants and rho-pion-pion coupling

For the zero-momentum axial bulk-to-boundary field `A_0(u)`, solve the
transverse axial equation at `lambda = 0` with

```text
A_0(0) = 1,
A_0'(1) = 0,
(f_pi z_m)^2 = -(1/g5^2) limit_{u->0} A_0'(u)/u.
```

For a normalized vector or axial mode `psi`, source Eq. (14) gives

```text
sqrt(F_psi) z_m
  = sqrt( abs[limit_{u->0} psi'(u)/u] / g5 ).
```

Source Eq. (22) becomes

```text
g_rho_pi_pi = g5 integral_0^1 du V_rho(u) [
  phi'(u)^2/(g5^2 u)
  + v(u)^2 [pi(u)-phi(u)]^2/u^3
].
```

The sign of each eigenfunction is fixed prospectively by requiring its first
nonzero interior value to be positive. The absolute sign of a single
three-point coupling is convention-dependent; the benchmark compares the
positive magnitude reported in Table II.

## Primary numerical route

Use the existing HoloForge `chebyshev_lobatto_grid` primitive on the exact
interval `u in [0,1]`. Use deterministic degrees `N = 64, 80, 96`, where `N`
is the polynomial degree and the final `N = 96` result is reported.

Factor the normalizable UV behavior before forming matrices:

```text
V(u)   = u^2 Vbar(u),
A(u)   = u^2 Abar(u),
phi(u) = u^2 phibar(u),
pi(u)  = u^2 pibar(u),
A_0(u) = 1 + u^2 a0bar(u).  [Superseded for A_0 only by approved R2.]
```

Apply the displayed equations after algebraic substitution, take analytic
endpoint limits, and impose the IR rows explicitly. Use
`scipy.linalg.eigvals` or `scipy.linalg.eig` for the generalized eigenvalue
problems and maintained NumPy/SciPy quadrature or Chebyshev interpolation for
normalization and observables. The implementation must record the raw and
filtered eigenvalue counts and every rejection reason.

The lowest admissible vector, axial, and pion modes are selected by ascending
positive real `lambda` only after they pass the imaginary-part, equation,
boundary, and normalization diagnostics. A source value is never used as an
eigenvalue-search bracket or ranking criterion.

## Independent numerical route

Use `scipy.integrate.solve_bvp` on the finite intervals

```text
epsilon <= u <= 1,
epsilon in (2e-5, 1e-5, 5e-6).
```

Use fourth-order adaptive collocation with the physical equations, not the
spectral differentiation matrices. Check:

1. the existing hard-wall vector result through its already independent
   shooting and adaptive-collocation routes;
2. the `lambda = 0` axial solution and `f_pi`;
3. the lowest transverse axial eigenvalue and decay constant; and
4. the lowest pion eigenvalue, pion normalization, and `g_rho_pi_pi`.

Unknown eigenvalues are `solve_bvp` parameters. A fixed nonzero IR amplitude
removes the homogeneous scaling degeneracy; modes are canonically normalized
only after convergence. Initial guesses may use smooth analytic shapes and
the converged solution at the preceding cutoff, but not a private program,
unpublished datum, or fitted source output.

The independent route is diagnostic evidence. The final reported values come
from the exact-endpoint spectral route unless a new owner-approved amendment
changes this contract before a production rerun.

## Frozen quantitative targets

Reproduce the complete Model A column of source Table II from the frozen
printed parameters:

| Observable | Source Model A target |
| --- | ---: |
| `m_pi` | 139.6 MeV |
| `m_rho` | 775.8 MeV |
| `m_a1` | 1363 MeV |
| `f_pi` | 92.4 MeV |
| `sqrt(F_rho)` | 329 MeV |
| `sqrt(F_a1)` | 486 MeV |
| `g_rho_pi_pi` | 4.48 |

The three starred source entries `m_pi`, `m_rho`, and `f_pi` were used by the
authors to determine Model A. HoloForge freezes the authors' printed
parameters and recomputes them; it does not perform or claim an independent
fit. Model B is outside Phase 3.

Also test the Gell-Mann--Oakes--Renner limit from source Eq. (19). With
`sigma` and `z_m` fixed, repeat the pion and `f_pi` calculations for

```text
m_q/m_q,ModelA in (1, 1/2, 1/4, 1/8),
R_GMOR = m_pi^2 f_pi^2/(2 m_q sigma).
```

Because the source relation is `R_GMOR = 1 + O(m_q)`, the physical Model A
ratio is reported but is not required to equal one exactly.

## Preregistered acceptance gates

Every gate is prospective. A miss stops acceptance and returns to the owner;
it does not authorize changing a threshold after inspecting Table II.

1. **Conventions and source identity.** `g5^2 = 12 pi^2/N_c` and `g5 = 2 pi`
   at `N_c = 3` agree to `1e-13` relative error. The recorded Model A inputs
   exactly match the three printed values above, with no fitted replacement.
2. **Protected vector anchor.** `holoforge verify hard-wall-vector` passes
   unchanged. The Phase 3 lowest vector eigenvalue agrees with the first
   `J_0` zero to `1e-6` relative error.
3. **Direct equations and boundaries.** On an independent Chebyshev grid of
   degree at least `2N`, each final factored physical equation has scaled
   residual infinity norm at most `1e-7`. Every UV and IR boundary residual is
   at most `1e-8`.
4. **Admissible spectra.** Report all raw and filtered eigenvalue counts. Every
   accepted eigenvalue is finite and positive, has relative imaginary part at
   most `1e-10`, and passes Gate 3 without source-based selection.
5. **Normalization and extraction.** Vector, axial, and pion normalization
   residuals are each at most `1e-8`. UV derivatives are extracted from the
   factored endpoint limits, not a fitted near-boundary polynomial.
6. **Spectral refinement.** For all seven Table II observables, the maximum
   relative change from `N = 80` to `N = 96` is at most `2e-4` and is smaller
   than the `N = 64` to `N = 80` change whenever the earlier change exceeds
   `1e-10`.
7. **Independent route and cutoff.** For the selected axial and pion
   quantities, the final two finite-cutoff results change by at most `2e-4`.
   Their maximum relative disagreement with the `N = 96` spectral values is
   at most `1e-3`. The existing vector benchmark's independent-route gates
   also remain passing.
8. **Table II reproduction.** Each of the seven final HoloForge values differs
   from the printed Model A target by at most `1.0%` relative error. The
   comparison artifact labels the three fitted source rows and the four source
   predictions.
9. **GMOR limit.** The absolute error `abs(R_GMOR - 1)` decreases at every
   quark-mass halving unless it is already below `1e-5`, and is at most `1.0%`
   at `m_q/m_q,ModelA = 1/8`.
10. **Determinism and interfaces.** Two complete runs have maximum relative
    difference at most `1e-11` in physical observables. JSON serialization,
    model-card schema, CLI, public-content policy, privacy audit, and all
    existing tests pass.

Passing these gates permits only a future proposal that the bounded source
calculation is `reproduced`. Automated success cannot approve the model card
or scientific claim.

## Proposed evidence and implementation artifacts

After owner approval, the bounded local implementation may touch only the
following logical artifacts, with exact filenames adjusted only for existing
repository registries:

- `src/holoforge/benchmarks/hard_wall_chiral.py`;
- benchmark export and CLI registry entries;
- `tests/test_hard_wall_chiral.py` and narrow CLI/model-card tests;
- `domains/qcd/hard_wall_chiral/model-card.json` and domain README;
- `docs/benchmarks/hard-wall-chiral.md` and the main benchmark index;
- HoloForge-generated JSON and CSV evidence for Table II and GMOR; and
- one HoloForge-generated Model A comparison graphic, clearly labeled as a
  reconstruction rather than a source figure.

The implementation must preserve equations, parameters, degree sequence,
cutoff sequence, targets, and thresholds in both machine-readable and human
documentation. It must record Python, NumPy, and SciPy versions and mark
material AI involvement.

## Mandatory stops and exclusions

Stop and return to owner review if:

- any equation, sign, normalization, boundary condition, or Table II unit is
  ambiguous;
- exact-endpoint factorization produces a rank-deficient or spuriously
  selected physical spectrum;
- the independent route lands on a different mode or any acceptance gate
  misses;
- a threshold, degree, cutoff, solver, parameter, or target would need to
  change after seeing the result;
- implementation would require the owner's temporary Mathematica programs,
  a private path, unpublished result, or confidential identifier; or
- an existing benchmark default or compatibility contract would change.

Phase 3 excludes Model B fitting, strange quarks, baryons, glueballs, the
chiral anomaly and Chern--Simons sector, finite temperature or density,
higher-dimensional operators, improved holographic QCD, and claims about
phenomenological precision. It also excludes Git/public actions beyond the
later action explicitly approved at a future gate.

## Hostile critic before implementation

**"Three of seven table entries are fitted, so this is not a seven-prediction
test."** Correct. The artifact must mark `m_pi`, `m_rho`, and `f_pi` as source
fit targets. Recomputing them checks equations and parameter transcription;
only the other four rows are source predictions. HoloForge will not advertise
a seven-observable prediction.

**"Rounded parameters make a tight reproduction gate artificial."** Correct.
The printed `323`, `2.29`, and `327` inputs do not encode the authors' hidden
fit precision. The one-percent Table II gate is intentionally separate from
the much tighter numerical convergence and independent-route gates.

**"The pion matrix pencil can manufacture spurious eigenvalues."** This is the
main numerical risk. Prospective UV factorization, raw-spectrum accounting,
source-blind filtering, independent residuals, degree refinement, and a
finite-cutoff `solve_bvp` comparison are all mandatory. A source-looking root
that fails any one of them is rejected.

**"GMOR is only a leading-order relation."** Correct. The physical Model A
ratio is not forced to one. The gate tests convergence toward one under a
frozen quark-mass sequence, matching the source's `O(m_q^2)` remainder in the
unnormalized relation.

**"The rho-pion-pion agreement could overstate the effective action."** The
source explicitly warns that omitted `F^3` terms may affect this three-meson
amplitude. Reproducing `4.48` verifies the truncated source model only; it is
not evidence that the coupling is robust under higher operators.

**"A hard IR wall is not QCD confinement."** Correct. The IR Neumann choice is
a phenomenological model input, and the source notes possible boundary terms
and about ten-percent sensitivity of the rho decay constant. A passing table
does not validate this boundary condition in nature.

## Owner decisions requested

### C1 -- source, scope, and parameters

**Recommendation: approve.** Use only the public v2 source equations and Model
A, with `N_f = 2`, `N_c = 3`, `g5 = 2 pi`, and the three printed parameters.

- **Reason:** this is a classical bottom-up chiral benchmark with a compact,
  reviewable source target.
- **Opens:** only the stated zero-temperature meson sectors of Model A.
- **Remains closed:** Model B fitting, extensions, private research, and
  phenomenological validation.
- **Uncertainty:** the published inputs and outputs are rounded.

### C2 -- equations, boundary conditions, and normalizations

**Recommendation: approve after checking the displayed pion conventions.**
Freeze the vector, axial, pion, decay-constant, and coupling formulas above.

- **Reason:** these are the minimum equations required to reproduce all seven
  Table II entries and the GMOR relation.
- **Opens:** only the displayed eigenproblems, zero-mode BVP, and integrals.
- **Remains closed:** alternate IR terms, higher operators, and a different
  pion gauge convention.
- **Uncertainty:** the coupled pion sector is the most normalization-sensitive
  part of the contract.

### C3 -- numerical routes

**Recommendation: approve.** Use exact-endpoint factored Chebyshev collocation
at `N = 64, 80, 96` as primary and finite-cutoff `solve_bvp` as independent.

- **Reason:** this follows the owner's preferred spectral practice while
  retaining a maintained-library check with different discretization errors.
- **Opens:** only the deterministic routes and refinements specified above.
- **Remains closed:** shooting as the primary method, private Mathematica code,
  random restarts, and post-result method selection.
- **Uncertainty:** the generalized pion pencil may require an owner-reviewed
  amendment if endpoint rank is defective.

### C4 -- targets and gates

**Recommendation: approve.** Reproduce all of Model A Table II at one percent,
separately require tight numerical convergence, and test the small-mass GMOR
limit rather than imposing exact GMOR at physical `m_q`.

- **Reason:** the gates distinguish source rounding and fitting from numerical
  accuracy and from a leading-order chiral identity.
- **Opens:** a future `reproduced` proposal only after every gate passes.
- **Remains closed:** accepting a visually plausible table with failed
  residual, refinement, independent-route, or determinism evidence.
- **Uncertainty:** prospective thresholds may expose a real numerical stop.

### C5 -- evidence boundary and artifact set

**Recommendation: approve.** Produce original JSON/CSV evidence and a clearly
labeled HoloForge Table II comparison graphic; preserve the source's hard-wall
and omitted-operator limitations.

- **Reason:** the source has no figure, so a computed table comparison provides
  the requested rapid validity view without copying source artwork.
- **Opens:** only public-source reproduction evidence after review.
- **Remains closed:** empirical validation, precision-QCD claims, novelty, and
  private-material transfer.
- **Uncertainty:** `g_rho_pi_pi` is explicitly sensitive to omitted terms.

### C6 -- bounded implementation authorization

**Recommendation: approve only with C1--C5.** Authorize the proposed local
implementation and complete preflight, then stop for owner review.

- **Reason:** the scientific and numerical contract is prospective and
  auditable before results exist.
- **Opens:** only the listed Phase 3 files, local calculations, tests, and
  unaccepted review artifacts.
- **Remains closed:** accepting a result or model card, commit, push, pull
  request, merge, tag, release, or beginning Phase 4.
- **Uncertainty:** any new source, endpoint, eigenvalue, normalization, or gate
  problem requires a documented return.

## Owner response paths

- **A -- approve all recommendations:** approve C1--C6 and authorize only the
  bounded local implementation and preflight, followed by a mandatory stop.
- **B -- approve selected items:** name the approved decisions; all others stay
  closed.
- **C -- request revision or more evidence:** identify the convention,
  equation, method, target, threshold, or limitation to revise.
- **D -- status walkthrough only:** discuss the packet and authorize no Phase 3
  implementation.
- **E -- custom response:** state a different bounded instruction.

**Recommended path: A.** It advances Phase 3 to a local spectral preflight
while preserving a mandatory owner gate before result acceptance or any Git
or release action.

## C1--C6 owner disposition

Xin-Yi Liu selected Option A on 2026-08-20 and approved C1--C6. This authorized
only the listed local implementation and preflight. It did not accept a Phase
3 result or model card and did not authorize any commit, push, pull request,
merge, tag, release, or Phase 4 work.

## First preflight stop: axial zero-mode UV logarithm

The source equation for the zero-momentum axial bulk-to-boundary field is

```text
A_0'' - A_0'/u - g5^2 [v(u)/u]^2 A_0 = 0,
v(u)/u = mhat + sigmahat u^2.
```

For nonzero `m_q`, its UV expansion begins

```text
A_0(u) = 1 + (g5^2 mhat^2/2) u^2 log(u) + O(u^2).
```

Therefore the approved regular factorization
`A_0 = 1 + u^2 a0bar(u)` does not have a smooth endpoint coefficient, and
`A_0'(u)/u` contains the expected `m_q^2 log(u)` dependence. Treating it as a
regular exact-endpoint Chebyshev field would silently change the analytic
contract.

An ignored public-source-only scratch diagnostic independently solved the full
displayed equation with `solve_bvp` and backward DOP853 integration. At the
three frozen independent-route cutoffs it found

| `epsilon` | `f_pi` from DOP853 |
| ---: | ---: |
| `2e-5` | `92.2447331043 MeV` |
| `1e-5` | `92.2644336389 MeV` |
| `5e-6` | `92.2841299819 MeV` |

The last two relative cutoff changes are `2.1352e-4` and `2.1343e-4`, just
above frozen Gate 7's `2e-4` ceiling. This is not numerical noise: the two
successive squared-decay-constant increments divided by `m_q^2 log(2)` are
`0.9999989` and `0.9999996`. They reproduce the UV logarithm quantitatively.

The public v2 TeX archive also retains a numerical note that the authors used
`epsilon_z = 1e-10 MeV^-1`. With the Model A wall this is
`epsilon = epsilon_z/z_m = 3.23e-8`. Backward DOP853 gives
`f_pi = 92.4272797851 MeV` there, within `2.96e-4` relative error of the
printed `92.4 MeV` target.

The same scratch diagnostic found `m_pi = 139.585 MeV`,
`m_a1 = 1358.24 MeV`, `sqrt(F_rho) = 329.812 MeV`,
`sqrt(F_a1) = 485.833 MeV`, and `g_rho_pi_pi = 4.48529`. Every value is within
`0.35%` of its printed Model A target. These are feasibility measurements from
an ignored diagnostic, not production spectral evidence or an accepted
reproduction.

This is a classified numerical-contract stop, not a failure of the hard-wall
chiral model or of the Table II target.

## Proposed prospective amendment after the UV stop

### R1 -- explicit source regulator for `f_pi`

**Recommendation: approve.** Retain the full displayed `v(u)^2`, including the
term proportional to `m_q^2`, and evaluate the source Eq. (20) decay constant
at the public-source numerical regulator
`epsilon_z = 1e-10 MeV^-1`, or `epsilon = 3.23e-8` for Model A.

- **Reason:** the full equation reproduces both the analytic UV logarithm and
  the printed Model A value; dropping `m_q^2` would be a nonuniform change in
  the pion boundary layer and would not reproduce the same source problem.
- **Opens:** only the explicitly regulated source Eq. (20) evaluation.
- **Remains closed:** calling the unrenormalized `epsilon -> 0` limit finite,
  adding an unreviewed counterterm, or changing the source Table II target.
- **Uncertainty:** the regulator is preserved in the public v2 TeX archive's
  numerical note rather than printed in the final four-page article.

### R2 -- method and gate replacement for the axial zero mode

**Recommendation: approve.** Keep exact-endpoint factored Chebyshev
generalized eigenproblems at `N = 64, 80, 96` for the normalizable vector,
axial, and pion modes. Replace only the axial zero-mode exact-endpoint solve by
backward DOP853 integration from `A_0'(1) = 0`, normalized to
`A_0(epsilon) = 1` at the R1 regulator.

Replace Gate 7's inapplicable `f_pi` cutoff-convergence clause by all of:

1. DOP853 and `solve_bvp` agree on `f_pi` to `1e-7` relative error at each of
   `epsilon = (2e-5, 1e-5, 5e-6)`;
2. each successive value of
   `(f_pi,fine^2 - f_pi,coarse^2)/(m_q^2 log 2)` differs from one by at most
   `1e-5`;
3. the DOP853 result at `epsilon = 3.23e-8` passes the unchanged one-percent
   Table II gate; and
4. the remaining axial/pion cutoff and cross-route gates retain their approved
   thresholds.

- **Reason:** these checks test the actual analytic cutoff dependence instead
  of demanding false convergence of an unrenormalized quantity.
- **Opens:** one maintained-library axial zero-mode route and an independent
  collocation/log-slope validation.
- **Remains closed:** changing the spectral method for normalizable modes,
  weakening Table II, residual, refinement, determinism, or interface gates,
  and selecting a method after table comparison.
- **Uncertainty:** production spectral work may expose a separate pion-pencil
  or normalization stop; that still requires owner review.

### R3 -- resume boundary

**Recommendation: approve only with R1--R2.** Resume the bounded local Phase 3
implementation and run every retained or revised gate, then stop again for
result review.

- **Reason:** the preflight identifies and analytically explains the only
  current contract mismatch while leaving the scientific target unchanged.
- **Opens:** only the previously listed local implementation artifacts and the
  revised preflight.
- **Remains closed:** accepting a result or model card, commit, push, pull
  request, merge, tag, release, or beginning Phase 4.
- **Uncertainty:** any new equation, eigenvalue, normalization, convergence, or
  evidence problem is another mandatory stop.

## R1--R3 owner response paths

- **A -- approve all recommendations:** approve R1--R3 and resume only the
  bounded local implementation and complete preflight, followed by a new
  owner gate.
- **B -- approve selected items:** name the approved amendments; all others
  remain closed.
- **C -- request revision or more evidence:** identify the UV convention,
  regulator, method, or gate to revise.
- **D -- status walkthrough only:** discuss the stop without resuming work.
- **E -- custom response:** state another bounded instruction.

**Recommended path: A.** It preserves the full source equation, explains the
cutoff behavior analytically, reproduces the public-source numerical regulator,
and changes no Table II target or normalizable-mode spectral gate.

## R1--R3 owner disposition

Xin-Yi Liu selected **Option A** on 2026-08-20 and approved R1--R3. This opens
only the bounded local Phase 3 implementation and amended complete preflight,
followed by a mandatory owner-review stop. Result and model-card acceptance,
commit, push, pull request, merge, tag, release, and Phase 4 remain closed.

## Amended complete preflight evidence

The owner-authorized local implementation passes all eleven scientific and
interface gates without another threshold, target, degree, cutoff, regulator,
or source-parameter change. The final Model A values are:

| Observable | HoloForge | Source | Relative error | Source role |
| --- | ---: | ---: | ---: | --- |
| `m_pi` [MeV] | 139.58524 | 139.6 | 0.0106% | fit target |
| `m_rho` [MeV] | 776.75866 | 775.8 | 0.1236% | fit target |
| `m_a1` [MeV] | 1358.24318 | 1363 | 0.3490% | prediction |
| `f_pi` [MeV] | 92.42728 | 92.4 | 0.0295% | fit target |
| `sqrt(F_rho)` [MeV] | 329.81203 | 329 | 0.2468% | prediction |
| `sqrt(F_a1)` [MeV] | 485.83344 | 486 | 0.0343% | prediction |
| `g_rho_pi_pi` | 4.485286 | 4.48 | 0.1180% | prediction |

The maximum final spectral change is `1.12e-12`, the largest selected
finite-cutoff change is `5.59e-9`, and the largest spectral--`solve_bvp`
difference is `1.87e-9`. DOP853 and `solve_bvp` agree on `f_pi` to
`2.45e-11` at the diagnostic cutoffs. The two UV log-slope ratios are
`0.999998925` and `0.999999703`.

The GMOR ratios at `m_q/m_q,ModelA = (1,1/2,1/4,1/8)` are
`(1.039371,1.017081,1.007892,1.003784)`, so the error decreases at every
halving and finishes at `0.3784%`.

The final repository suite passes `197/197` tests. A wheel built from the
checkout was installed into a separate temporary environment; its installed
`holoforge verify hard-wall-chiral --json` command passed all eleven gates
with the same maximum table error and retained
`result_review_state = awaiting-owner-review`.

The public-source paper contains no plotted figure. HoloForge therefore
generates a new Table II ratio and GMOR comparison graphic and labels it as
not a source figure. The JSON, CSV, graphic, guide, tests, and model card retain
AI provenance and the fit-target/prediction and non-inference boundaries.

These are passing implementation measurements, not yet an owner-accepted
result or model card.

## Phase 3 result owner decisions

1. **Accept the implementation realization. Recommendation: approve.** Accept
   the source-blind QZ candidate ordering, deterministic local bordered
   eigenpair refinement, and twice-denser operator-norm backward-error metric
   as compliant implementations of the approved spectral contract.
2. **Accept the numerical result. Recommendation: approve.** Accept all eleven
   gates and the bounded seven-row Model A and GMOR result at `reproduced`,
   retaining the three fit-target and four prediction labels.
3. **Accept the evidence boundary. Recommendation: approve.** Accept the
   explicit source regulator, UV-log evidence, generated JSON/CSV/graphic, and
   every stated non-inference boundary.
4. **Synchronize review fields. Recommendation: approve.** Change only the
   numerical claim and model-card provenance from `unreviewed` to
   owner-approved while preserving material AI assistance.
5. **Authorize a scoped local commit. Recommendation: approve.** Commit the
   accepted Phase 3 implementation and synchronized public evidence as one
   logical change. Push, pull request, merge, tag, release, Phase 4, and new
   model sectors remain closed.

### Phase 3 result response paths

- **A -- approve all recommendations:** approve Decisions 1--5, synchronize
  the result/model-card review fields, and create one scoped local commit.
- **B -- approve selected items:** name the approved decisions; every other
  item remains closed.
- **C -- request revision or more evidence:** identify the equation, method,
  diagnostic, result, artifact, or boundary to revise.
- **D -- status walkthrough only:** discuss the evidence without changing
  review fields or Git state.
- **E -- custom response:** state another bounded instruction.

**Recommended path: A.** All frozen and amended gates pass with margin, the
independent installed wheel agrees, the source-fit rows are not presented as
predictions, and the private/remote/release boundaries remain closed.

## Phase 3 result owner disposition

Xin-Yi Liu selected **Option A** on 2026-08-20 and approved Decisions 1--5.
The source-blind spectral realization, all eleven numerical gates, the bounded
seven-row Model A and GMOR result at `reproduced`, the evidence and
non-inference boundaries, and the synchronized review fields are accepted.
Material AI assistance remains explicit.

This disposition authorizes exactly one scoped local Phase 3 commit. Push,
pull request, merge, tag, release, Phase 4, additional model sectors, and any
change to the frozen equations, inputs, regulator, thresholds, or reported
values remain closed.

## Version 0.5.4 release-preparation owner disposition

After the scientific commit, the owner selected **Option A** on 2026-08-20 for
a bounded local release-preparation pass. This authorizes synchronized Version
0.5.4 metadata and changelog entries, explicit hard-wall-chiral coverage in the
Python test matrix, installed-wheel smoke test, and Linux, macOS, and Windows
wheel-portability job, regenerated version-stamped evidence, release
validation, and exactly one scoped local release-preparation commit.

This authorization stops before push, pull request, remote CI, merge, tag,
release, Phase 4, or another model sector. It changes delivery preparation,
not the accepted `reproduced` support level, equations, numerical method,
thresholds, results, or non-inference boundaries.

## Version 0.5.4 public release closure

Through later, separate Option A decisions on 2026-08-20, the owner authorized
the bounded remote delivery sequence. Branch `codex/hard-wall-chiral-contract`
was pushed, pull request 24 passed its required remote checks, and the pull
request was merged into `main` as `a79f944`. Annotated tag `v0.5.4` and the
corresponding public GitHub release were then created and verified. Phase 3 is
therefore closed as a released Forge/Verify benchmark.

This closure records delivery state only. It does not alter the accepted
equations, methods, numerical values, thresholds, `reproduced` support level,
AI provenance, limitations, or non-inference boundaries. It also does not
authorize a post-release scientific change.

## Phase 4 contract-preparation owner disposition

Xin-Yi Liu selected **Option A** on 2026-08-20 to record the Phase 3 release
closure and prepare only the Phase 4 HHH optical-conductivity scientific
contract and standard PDF owner-review packet. This opens public-source
contract research and documentation only. Solver implementation, numerical
production, result or model-card acceptance, commit, push, pull request,
merge, tag, release, and any private-research transfer remain closed pending
the Phase 4 contract owner gate.
