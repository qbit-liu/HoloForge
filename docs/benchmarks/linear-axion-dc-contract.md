# Linear-Axion DC Conductivity Benchmark Contract

**Status:** Decisions B1-B5 were approved on 2026-08-06 and confirmed by
Xin-Yi Liu after review of the compiled scientific-contract packet on
2026-08-07. The contract is frozen and bounded implementation is authorized,
beginning with the UV source-map preflight. Model-card approval, commit, push,
pull request, merge, tag, and release remain separate decisions.

## Recommendation

Reproduce the exact four-bulk-dimensional DC conductivity of the homogeneous
linear-axion model and independently approach it through the source paper's
decoupled finite-frequency master equations.

This is a bottom-up Einstein–Maxwell–scalar construction. It contains no
D-brane model and requires no top-down string embedding. A passing benchmark
would reproduce the selected effective model, not validate a material or prove
that it is a complete theory of momentum relaxation.

## Primary public source

T. Andrade and B. Withers, “A simple holographic model of momentum
relaxation,” JHEP 05 (2014) 101,
[arXiv:1311.5157v2](https://arxiv.org/abs/1311.5157),
[DOI:10.1007/JHEP05(2014)101](https://doi.org/10.1007/JHEP05%282014%29101).

The contract uses source Eqs. (2.1)–(2.9), (3.2)–(3.21), (3.24)–(3.26), and
Appendix A. The arXiv v2 TeX source was inspected directly; no source archive,
figure, or copyrighted prose will be committed.

## Support and review state

- Source action, solution, fluctuation equations, and DC formula:
  `established-source`, AI-transcribed, approved by Xin-Yi Liu through the
  compiled contract review on 2026-08-07.
- Future HoloForge numerical agreement: remains unclaimed until the
  implementation passes every gate below.
- Novelty, phenomenological material agreement, and private research
  relevance: not claimed and outside this benchmark.

## Action and dimensions

Use four bulk dimensions, corresponding to `d = 3` in the source. With AdS
radius `L = 1`, metric signature `(-,+,+,+)`, and `16 pi G = 1`, the action is:

```text
S = integral_M sqrt(-g) [
      R - 2 Lambda
      - (1/2) sum_(I=1)^2 (partial psi_I)^2
      - (1/4) F^2
    ] d^4 x
    - 2 integral_boundary sqrt(-gamma) K d^3 x,

Lambda = -3,
F = dA.
```

The Gibbons–Hawking term fixes the variational convention but does not enter
the radial fluctuation solve directly.

## Background, coordinates, and sources

Use the source coordinate `r`, with the future horizon at `r = r0` and the UV
boundary at `r -> infinity`:

```text
ds^2 = -f(r) dt^2 + dr^2/f(r) + r^2 (dx^2 + dy^2),
A = A_t(r) dt,
psi_1 = alpha x,
psi_2 = alpha y.
```

The exact solution is:

```text
m0 = r0^3 [1 + mu^2/(4 r0^2) - alpha^2/(2 r0^2)],

f(r) = r^2 - alpha^2/2 - m0/r + mu^2 r0^2/(4 r^2),

A_t(r) = mu (1 - r0/r),

T = [3 r0 - alpha^2/(2 r0) - mu^2/(4 r0)]/(4 pi),

s = 4 pi r0^2.
```

The gauge is fixed so that `A_t(r0) = 0`. The chemical potential `mu` is a
nonzero boundary gauge-field source. The scalar profiles are also nonzero,
spatially dependent sources. Only the bulk stress tensor and background
geometry are homogeneous and isotropic.

The benchmark is grand canonical with fixed `mu` and fixed scalar-source
gradient `alpha`. The horizon scale determines `T`. It must never call this a
source-free UV problem.

## Scale convention and admissible domain

Use scaling symmetry to set `r0 = 1` in the numerical solve while recording
all inputs as the dimensionless ratios:

```text
mu_hat = mu/r0,
alpha_hat = alpha/r0,
omega_hat = omega/r0.
```

Require:

```text
mu_hat > 0,
alpha_hat > 0,
3 - alpha_hat^2/2 - mu_hat^2/4 > 0.
```

The last inequality is the positive-temperature condition. The singular
translation-invariant limit `alpha = 0`, the neutral master-field limit
`mu = 0`, and the extremal limit `T = 0` are explicit nondefault limits and
must fail clearly in the Version 0.5 verifier.

## Observable and exact target

The boundary current response is defined by:

```text
delta A_x = exp(-i omega t) a_x(r),
a_x(r) = a_x^(0) + J_x/r + ...,
E_x = i omega a_x^(0),
sigma(omega) = J_x/[i omega a_x^(0)].
```

For `d = 3`, source Eq. (3.21) gives the exact dimensionless target:

```text
sigma_DC = 1 + mu^2/alpha^2.
```

At fixed `mu` and `alpha`, this result is independent of temperature in four
bulk dimensions. HoloForge should report that as a result inside this model,
not as a universal statement about all momentum-relaxing theories.

## Independent numerical route

The verifier should approach the DC limit through the source's decoupled
finite-frequency master equations rather than merely evaluating Eq. (3.21).

For `d = 3`, define:

```text
c_plus/minus = [
  3 m0 plus/minus sqrt(9 m0^2 + 4 r0^2 mu^2 alpha^2)
] / (2 mu r0).
```

The two master fields obey:

```text
r^2 d/dr [f(r) d(Phi_plus/minus)/dr]
+ [
    r^2 omega^2/f(r)
    - mu^2 r0^2/r^2
    + c_plus/minus mu r0/r
  ] Phi_plus/minus = 0.
```

Reconstruct the source-paper fluctuation variables through:

```text
phi = r [c_plus Phi_plus + c_minus Phi_minus],
a_x = -i [Phi_plus + Phi_minus].
```

Also reconstruct the massless combination and radial flux specialized to
`d = 3`:

```text
B = 1 + mu^2 r0^2/(alpha^2 r^2),

lambda_1 = B^(-1) [
  a_x - i mu r0 phi/(alpha^2 r^2)
],

lambda_2 = B^(-1) [
  mu^2 r0^2 a_x/(alpha^2 r^2)
  + i mu r0 phi/(alpha^2 r^2)
],

Pi = f B lambda_1' - 2 f lambda_2/r.
```

At finite frequency, source Eq. (3.13) gives the flux-balance identity:

```text
Pi' + omega^2 B lambda_1/f = 0.
```

In the DC limit, `Pi` becomes radially conserved and source Eq. (3.16)
identifies:

```text
sigma_DC(r) = limit_(omega -> 0) [-Pi/(i omega lambda_1)].
```

The verifier should therefore test both the finite-frequency balance identity
and the radial agreement of independently extrapolated DC limits. This keeps
the horizon-flux argument visible rather than treating the closed formula as
an unexplained target.

Use `scipy.integrate.solve_ivp` with complex fields and the `DOP853` method.
Initialize each independent master solution from the ingoing Frobenius branch:

```text
Phi_plus/minus proportional to
(r-r0)^[-i omega/f'(r0)] [1 + O(r-r0)].
```

The horizon cutoff is a numerical regulator, not a physical boundary
condition. Its effect must be refined separately from the integrator tolerance.

## UV source map preflight

Before accepting any conductivity, construct one linear combination of the
two ingoing master solutions that satisfies all physical source conditions:

1. `a_x^(0) = 1`, fixing a unit boundary gauge perturbation;
2. no growing `O(r)` term in `phi`;
3. reconstructed `chi`, using `chi' = omega phi/(r^2 f)`, has no constant
   scalar-fluctuation source; and
4. the reconstructed metric perturbation from the source constraint has no
   boundary metric source after the allowed residual gauge choice.

Extract master-field UV coefficients with a declared least-squares fit in
`1/r`. Solve the two-master amplitude system with
`numpy.linalg.solve`; use `numpy.linalg.lstsq` for overdetermined UV fits.

The source-map preflight is a hard stop. If two ingoing master solutions plus
the documented residual gauge freedom cannot impose the four physical
conditions without ambiguity, return to owner review before computing or
reporting conductivity. Do not omit a source condition or import a private
solver to rescue the benchmark.

## Frozen parameter and frequency cases

With `r0 = 1`, use three default cases:

| Case | `mu` | `alpha` | Exact `sigma_DC` |
| --- | ---: | ---: | ---: |
| P1 | `0.5` | `1.0` | `1.25` |
| P2 | `1.0` | `1.0` | `2.0` |
| P3 | `1.0` | `sqrt(2)` | `1.5` |

All three are nonextremal and avoid the singular `mu = 0` and `alpha = 0`
master-field limits.

Use the preregistered sequence:

```text
omega/r0 = 0.08, 0.05, 0.03, 0.02.
```

Fit `Re sigma(omega)` against `omega^2` and take the intercept as the numerical
DC estimate. Record `Im sigma` and require a vanishing zero-frequency
intercept. Repeat the fit without the largest frequency as a stability check.
For the radial-flux DC audit, perform the same intercept fit at
`r/r0 = 1.5`, `5`, and `20`; these points avoid both numerical cutoffs and are
fixed before results are inspected.

## Default numerical controls

Propose these defaults before results are viewed:

```text
horizon cutoff:       epsilon_h = 1e-6 r0
UV endpoint:          r_max = 60 r0
solve_ivp method:     DOP853
relative tolerance:  1e-9
absolute tolerance:  1e-11
UV fit window:        final 20 percent of the radial samples
UV fit basis:         1, 1/r, 1/r^2
```

The implementation may return to owner review if the UV basis is
source-inconsistent. It may not add terms or weaken gates after inspecting a
disagreement without recording and approving the reason.

## Acceptance gates

Every default parameter case must pass:

1. **Background horizon:** `|f(r0)| <= 1e-12`.
2. **Temperature identity:** analytic differentiation of `f` agrees with the
   stated temperature to relative error `<= 1e-10`.
3. **Maxwell flux:** `r^2 A_t'(r)` is constant to relative variation
   `<= 1e-10` on the checked radial grid.
4. **Ingoing branch:** the initialized logarithmic derivative agrees with the
   Frobenius exponent and improves when `epsilon_h` is halved.
5. **UV source map:** normalized unwanted scalar and metric source residuals
   are each `<= 1e-8`; the amplitude-system condition number is `< 1e10`.
6. **Equation reconstruction:** reconstructed `a_x` and `phi` satisfy source
   Eqs. (3.8) and (3.9) with normalized maximum residual `<= 1e-6` on an
   independent check grid.
7. **Radial flux:** the reconstructed finite-frequency flux balance has
   normalized maximum residual `<= 1e-6`; DC intercepts of
   `-Pi/(i omega lambda_1)` at three preregistered radial locations agree to
   relative `<= 5e-3`.
8. **DC value:** the extrapolated `Re sigma(0)` agrees with
   `1 + mu^2/alpha^2` to relative error `<= 5e-3`.
9. **Imaginary intercept:** the extrapolated `Im sigma(0)` has absolute value
   `<= 5e-3`.
10. **Frequency-fit stability:** removing `omega/r0 = 0.08` changes the real DC
   intercept by relative `<= 3e-3`.
11. **Horizon refinement:** halving `epsilon_h` changes the real DC estimate by
    relative `<= 2e-3`.
12. **UV refinement:** increasing `r_max` from `60 r0` to `80 r0` changes the
    real DC estimate by relative `<= 2e-3`.
13. **Tolerance refinement:** tightening both integrator tolerances by a factor
    of ten changes the real DC estimate by relative `<= 1e-3`.

These thresholds are preregistered proposals. If an implementation misses
one, classify the miss before changing anything: equation/convention error,
source-map error, insufficient asymptotics, numerical failure, or an
overaggressive contract. A threshold change requires owner review and a
preserved record of the original failure.

## Machine-readable record

The verifier must record:

- arXiv version, DOI, equation locators, and model-card digest;
- action and sign conventions;
- `r0`, `mu`, `alpha`, temperature, entropy density, and exact DC target;
- the nonzero background sources and zero fluctuation-source conditions;
- master-field constants and every numerical control;
- complex conductivity at every frequency;
- UV fit coefficients, source residuals, condition numbers, equation
  residuals, radial-flux balance and DC-intercept evidence, and all refinement
  results;
- analytic and numerical DC values with signed and relative differences;
- software versions, pass/fail checks, scope, and limitations; and
- evidence-bundle compatibility metadata.

The proposed command is:

```text
holoforge verify linear-axion-dc
holoforge verify linear-axion-dc --json
```

No plot is required for Version 0.5.

## Planned public files

- `src/holoforge/benchmarks/linear_axion_dc.py`
- one adapter entry in `src/holoforge/benchmarks/registry.py`
- `domains/transport/linear_axion_dc/model-card.json`
- `domains/transport/linear_axion_dc/README.md`
- `docs/benchmarks/linear-axion-dc.md`
- `tests/test_linear_axion_dc.py`
- focused registry, CLI, schema, evidence, and package tests
- Version 0.5 release documentation after implementation review

## Scientific limitations

- The scalar sources explicitly break translations; they are homogeneous only
  at the level of the bulk stress tensor and background geometry.
- The benchmark treats the classical two-derivative bottom-up model and does
  not establish a microscopic lattice mechanism.
- The `d = 3` DC value is temperature independent only within the stated model
  and fixed-source convention.
- The default excludes zero momentum relaxation, neutrality, and extremality
  because the selected master-field variables become singular or require a
  separate limit.
- Agreement with Eq. (3.21) verifies the implementation and source-paper
  result, not a real material, universal transport law, or new research claim.

## Stop conditions

Stop before implementation or acceptance if:

- the action, `d = 3` reduction, time convention, current sign, or operator
  normalization cannot be reconciled with the primary source;
- the UV source-map preflight cannot impose gauge, scalar, and metric source
  conditions simultaneously;
- the master-field transformation is singular in a default case;
- small-frequency extrapolation is unstable under the preregistered sequence;
- agreement requires changing a source, ensemble, parameter case, or
  tolerance after seeing the result;
- a direct coupled solver, new model, or private code is needed to rescue the
  benchmark without a new reviewed contract;
- runtime cannot fit a bounded public CI job without weakening validation; or
- any unpublished or private research material would enter the public change.

## Owner decisions

### Decision B1 — source and physical conventions

**Recommendation: approve.**

- **Reason:** the contract preserves the source's bottom-up action, four-bulk-
  dimensional reduction, nonzero gauge and scalar sources, and grand-canonical
  interpretation.
- **Opens:** using these equations and conventions as the public benchmark
  target.
- **Remains closed:** top-down claims, source-free wording, and material
  phenomenology.
- **Uncertainty:** the detailed metric-source subtraction must pass the UV
  preflight before conductivity is accepted.

### Decision B2 — independent master-field route

**Recommendation: approve.**

- **Reason:** source Eqs. (3.24)–(3.26) provide a maintained-library numerical
  route independent of simply evaluating the analytic DC formula.
- **Opens:** finite-frequency `solve_ivp` integration and zero-frequency
  extrapolation after Phase A passes.
- **Remains closed:** a custom ODE integrator, direct coupled rescue solver,
  optical-spectrum publication, and parameter scans.
- **Uncertainty:** the UV source basis is the principal technical risk and is a
  hard stop rather than a tunable detail.

### Decision B3 — parameters and numerical gates

**Recommendation: approve.**

- **Reason:** three nonextremal cases test different exact conductivities, and
  frequency, horizon, UV, and tolerance refinements separate numerical error
  sources.
- **Opens:** the frozen cases, frequencies, defaults, and thirteen acceptance
  gates.
- **Remains closed:** retrospective tolerance weakening and singular limit
  claims.
- **Uncertainty:** the preregistered thresholds have not been tuned against a
  HoloForge implementation; a miss must return to classified owner review.

### Decision B4 — output and scientific limits

**Recommendation: approve.**

- **Reason:** the proposed record exposes every source, fit, residual,
  refinement, and limitation needed to audit the reproduction.
- **Opens:** the named public files and evidence metadata after implementation
  authorization.
- **Remains closed:** plots, empirical validation, novelty, and private
  research transfer.
- **Uncertainty:** no plot means the numerical review will rely on tables and
  machine records; a plot can be proposed later without becoming a gate.

### Decision B5 — sequencing and implementation authorization

**Recommendation: approve the contract now and authorize implementation only
after Phase A is green and reviewed.**

- **Reason:** Candidate A is the proof that the registry works; implementing it
  before migration would recreate the central special cases Version 0.5 is
  intended to remove.
- **Opens:** implementation after the Phase A review checkpoint, without a
  second scientific-contract rewrite unless a stop condition fires.
- **Remains closed:** implementation before Phase A, commit, push, pull
  request, merge, tag, and release.
- **Uncertainty:** a Phase A stop can delay Candidate A without changing its
  scientific selection.

## Owner response recorded

Xin-Yi Liu approved Decisions B1-B5 on 2026-08-06. The public source and
physical conventions, finite-frequency master-field route, frozen parameter
cases, thirteen numerical gates, machine record, scientific limitations, and
sequencing are accepted. Candidate A implementation may begin only after the
Phase A registry migration is green and has been presented for owner review.
This approval does not authorize implementation before that checkpoint, a
model-card support-state approval, commit, push, pull request, merge, tag, or
release.

On 2026-08-07, Xin-Yi Liu approved preparation of a compiled PDF review packet
and chose to keep Candidate A implementation paused until the packet is
reviewed. The Phase A checkpoint is now approved, but that explicit review hold
takes precedence over the earlier conditional implementation authorization.

## Final compiled-packet review recorded

Xin-Yi Liu approved Decisions B1-B5 after reviewing the compiled packet on
2026-08-07. The temporary review hold is lifted. This authorizes bounded local
implementation under the frozen contract, beginning with the analytic
background checks and the four-condition UV source-map preflight. If that
preflight is ambiguous or fails its declared source residuals, implementation
must stop before conductivity is computed. This approval does not authorize a
model-card support-state decision, commit, push, pull request, merge, tag, or
release.

## Local UV-preflight checkpoint

The approved background and UV source-map slice was implemented and checked
locally on 2026-08-07. This is implementation evidence, not a change to the
frozen contract and not a conductivity result.

The primary-source equations resolve the apparent mismatch between two master
amplitudes and four listed source conditions. At large `r`, the scalar equation
and `phi = r^2 f chi'/omega` give:

```text
phi_growing = -[omega chi_source - i alpha^2 H_tx_source].
```

Under the residual boundary diffeomorphism,
`delta chi_source = alpha^2 xi` and
`delta H_tx_source = -i omega xi`, so the bracket is gauge invariant. The two
independent amplitude equations are therefore the unit gauge source and the
vanishing growing-`phi` coefficient. When the second vanishes, one residual
diffeomorphism sets both individual scalar and metric fluctuation sources to
zero. Conditions 2–4 in the preflight are dependent physical checks, not three
additional amplitude equations.

Across all three frozen parameter cases and all four frozen frequencies, the
local preflight found:

| Check | Worst value | Contract gate |
| --- | ---: | ---: |
| Source-matrix condition number | `3.179` | `< 1e10` |
| Unit-gauge-source residual | `3.07e-14` | `<= 1e-8` |
| Gauge-invariant scalar-source residual | `9.76e-13` | `<= 1e-8` |
| Metric-source residual after scalar gauge fixing | `1.47e-14` | `<= 1e-8` |

The ingoing-exponent initialization error decreased by a factor of about
`0.5` when the horizon cutoff was halved. All analytic background checks and
all 12 source-map cases passed. The calculation remains stopped before the
conductivity, equation-reconstruction, radial-flux, DC-extrapolation, and
refinement gates.

## Local full-verification checkpoint

After owner authorization to continue, the bounded local implementation
completed the remaining frozen gates on 2026-08-09. This checkpoint supersedes
the earlier *execution stop* but preserves the preflight result above as part
of the audit trail; it does not change any source, case, frequency, fit basis,
threshold, or scientific limitation in the approved contract.

The boundary-current extrapolations are:

| Case | `mu` | `alpha` | Numerical DC | Exact DC | Relative error |
| --- | ---: | ---: | ---: | ---: | ---: |
| P1 | `0.5` | `1.0` | `1.249535612` | `1.25` | `3.72e-4` |
| P2 | `1.0` | `1.0` | `1.997624878` | `2.00` | `1.19e-3` |
| P3 | `1.0` | `sqrt(2)` | `1.499303104` | `1.50` | `4.65e-4` |

The worst values across the frozen cases are:

| Check | Worst value | Contract gate |
| --- | ---: | ---: |
| Reconstructed source equations | `1.25e-16` | `<= 1e-6` |
| Finite-frequency flux balance | `8.97e-15` | `<= 1e-6` |
| Radial DC relative spread | `8.73e-4` | `<= 5e-3` |
| Boundary DC relative error | `1.19e-3` | `<= 5e-3` |
| Imaginary DC intercept | `6.97e-4` | `<= 5e-3` |
| Frequency-fit change | `7.49e-4` | `<= 3e-3` |
| Horizon-cutoff change | `5.14e-7` | `<= 2e-3` |
| UV-endpoint change | `1.51e-4` | `<= 2e-3` |
| Integrator-tolerance change | `2.88e-7` | `<= 1e-3` |

The implementation uses SciPy's `solve_ivp` with DOP853 and NumPy's
least-squares and linear solves. The analytic expression is used only as the
acceptance target. The reconstructed-equation and flux residuals test the
source transformation with analytic derivatives on a staggered grid; the
separate cutoff, UV, tolerance, frequency, and DC gates supply the numerical
convergence evidence.

All fifteen machine checks representing the thirteen numbered contract gates
pass locally. The model card deliberately leaves its HoloForge reproduced
claim and AI-assisted provenance `unreviewed` pending owner review. This
checkpoint authorizes neither changing those fields nor committing, pushing,
publishing, tagging, or releasing the implementation.

## Full-verification owner response recorded

After reviewing the compiled six-page full-verification packet, Xin-Yi Liu
approved Decisions V1--V4 on 2026-08-09:

1. the equation and source reconstruction and gates 1--7 are scientifically
   accepted within the frozen contract;
2. the DC and refinement evidence and gates 8--13 are scientifically accepted
   within the frozen contract;
3. the model-card `reproduced` claim and its AI-assisted provenance are
   approved, with the support level remaining `reproduced`; and
4. the bounded public implementation is accepted as ready for a later scoped
   commit proposal.

This approval supersedes the pending review state in the immediately preceding
checkpoint but preserves it as the pre-approval record. It authorizes updating
the model-card review fields and registered digest. It does not authorize
staging, commit, push, pull request, merge, tag, release, empirical validation,
or any broader scientific claim.
