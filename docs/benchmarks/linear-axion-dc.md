# Linear-axion DC conductivity benchmark

## Scope

This benchmark reproduces the four-bulk-dimensional electric DC conductivity
of the homogeneous linear-axion model in T. Andrade and B. Withers,
“A simple holographic model of momentum relaxation,” JHEP 05 (2014) 101,
[arXiv:1311.5157v2](https://arxiv.org/abs/1311.5157).

It is a bottom-up Einstein-Maxwell theory coupled to two massless scalars. The
chemical potential and spatially linear scalar profiles are nonzero boundary
sources. Passing the verifier reproduces this selected effective-model result;
it does not validate a material, a microscopic momentum-relaxation mechanism,
or a top-down string construction.

## Numerical route

The verifier does not obtain a pass by evaluating the exact DC expression.
For each frozen parameter case, it:

1. integrates two independent complex ingoing master solutions with SciPy's
   `solve_ivp` and DOP853;
2. fits their UV coefficients with `numpy.linalg.lstsq`;
3. uses `numpy.linalg.solve` to impose a unit gauge perturbation and zero
   gauge-invariant scalar/metric fluctuation source;
4. reconstructs the source-paper fields and checks Eqs. (3.8) and (3.9);
5. checks the finite-frequency radial flux identity;
6. extracts `a_x = a_x^(0) + J_x/r + ...` and computes
   `sigma(omega) = J_x/[i omega a_x^(0)]`; and
7. extrapolates the boundary and three radial-flux DC limits before comparing
   with `1 + mu^2/alpha^2`.

The apparent four-source-condition/two-amplitude mismatch is resolved by the
residual boundary diffeomorphism. The growing coefficient of the reconstructed
field `phi` is minus the gauge-invariant combination
`omega chi_0 - i alpha^2 H_tx^(0)`. When it vanishes, one residual gauge choice
sets both individual scalar and metric fluctuation sources to zero.

## Frozen cases and results

The four frequencies are `0.08`, `0.05`, `0.03`, and `0.02` in horizon units.
The real response is fit with a constant plus `omega^2`. Because
`sigma(-omega) = sigma(omega)*`, the imaginary-response diagnostic uses a free
intercept plus the first two odd powers, `omega` and `omega^3`; the free
intercept is tested against zero rather than imposed to vanish.

| Case | `mu` | `alpha` | Numerical DC | Exact DC | Relative error |
| --- | ---: | ---: | ---: | ---: | ---: |
| P1 | `0.5` | `1.0` | `1.249536` | `1.25` | `3.72e-4` |
| P2 | `1.0` | `1.0` | `1.997625` | `2.00` | `1.19e-3` |
| P3 | `1.0` | `sqrt(2)` | `1.499303` | `1.50` | `4.65e-4` |

These are implementation results inside the selected model. Xin-Yi Liu
approved the reproduced claim and its recorded AI-assisted provenance on
2026-08-09. The support level remains `reproduced`; approval does not turn the
calculation into empirical validation.

## Validation summary

The frozen contract contains thirteen scientific and numerical gates. The
current local implementation passes them all:

- worst UV source-matrix condition number: `3.179` against `< 1e10`;
- worst unwanted-source residual: `9.82e-13` against `<= 1e-8`;
- worst reconstructed-equation residual: `1.25e-16` against `<= 1e-6`;
- worst finite-frequency flux residual: `8.97e-15` against `<= 1e-6`;
- worst radial DC relative spread: `8.73e-4` against `<= 5e-3`;
- worst imaginary intercept: `6.97e-4` against `<= 5e-3`;
- worst frequency-fit change: `7.49e-4` against `<= 3e-3`;
- worst horizon-cutoff change: `5.14e-7` against `<= 2e-3`;
- worst UV-endpoint change: `1.51e-4` against `<= 2e-3`; and
- worst tolerance-refinement change: `2.88e-7` against `<= 1e-3`.

The equation and flux residuals use analytic derivatives reconstructed from
the master solutions on a staggered diagnostic grid. They test the
master-to-source transformation and source equations; the separate cutoff,
UV, tolerance, and DC-fit gates provide the numerical-convergence evidence.

## Commands

After installation:

```bash
holoforge verify linear-axion-dc
holoforge verify linear-axion-dc --json
python3 -m unittest tests.test_linear_axion_dc -v
```

The complete frozen contract, exact thresholds, failure classification, and
record requirements are in
[`linear-axion-dc-contract.md`](linear-axion-dc-contract.md).

## Limitations

- The benchmark excludes `mu = 0`, `alpha = 0`, and extremal backgrounds.
- It verifies a bounded DC extrapolation, not a full optical spectrum.
- The fields are classical and the model is phenomenological and bottom-up.
- No fit to experimental transport data is performed.
- Commit, publication, and release require separate owner decisions. The model
  card records the owner's 2026-08-09 scientific and provenance review.
