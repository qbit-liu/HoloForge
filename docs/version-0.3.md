# HoloForge Version 0.3 Specification

**Status:** approved by Xin-Yi Liu as the public implementation contract on
2026-08-05.

## Recommendation

Implement Version 0.3 as a controlled comparison of the quadratic soft-wall
and hard-wall AdS/QCD vector spectra. This is the smallest public calculation
that exercises two bottom-up constructions, independent numerical methods,
convergence evidence, and uncertainty-aware reference data against the same
observable. It does not depend on any private Explore candidate.

## Objective

Version 0.3 tests whether HoloForge can compare two established bottom-up
models without hiding differences in their infrared physics, boundary
conditions, calibration, or empirical interpretation.

The comparison uses dimensionless radial vector-meson mass ratios. Dividing by
the lowest vector mass removes the single dimensionful scale from each model,
so the comparison does not gain an artificial advantage from separate
multi-parameter fits.

## Public source basis

- **Hard wall:** J. Erlich, E. Katz, D. T. Son, and M. A. Stephanov,
  *QCD and a Holographic Model of Hadrons*,
  [arXiv:hep-ph/0501128](https://arxiv.org/abs/hep-ph/0501128).
- **Quadratic soft wall:** A. Karch, E. Katz, D. T. Son, and
  M. A. Stephanov, *Linear Confinement and AdS/QCD*,
  [arXiv:hep-ph/0602229](https://arxiv.org/abs/hep-ph/0602229).
- **Reference data:** the fixed 2026 Particle Data Group edition,
  F. Takahashi et al., *Review of Particle Physics*, Int. J. Mod. Phys. A 41,
  2630011 (2026), with exact listing locators, source hashes, and access dates
  stored in the dataset. The snapshot is fixed for reproducibility rather than
  silently following future online values.

## Scientific contract

### Soft-wall construction

Retain the existing transverse-vector problem

```text
-psi'' + (kappa^4 z^2 + 3/(4 z^2)) psi = m^2 psi,
m_n^2 = 4 kappa^2 (n + 1).
```

The current verifier, defaults, and acceptance gate remain unchanged. Version
0.3 may add an independent solver route but must not alter the v0.2 result.

### Hard-wall construction

Use a transverse vector field on a slice of AdS5 with UV normalizability and
the standard IR Neumann condition. In the original vector variable,

```text
partial_z[(1/z) partial_z V] + (m^2/z) V = 0,
V(epsilon) = 0,
partial_z V(z_m) = 0.
```

In the zero-cutoff analytic limit, the masses obey

```text
m_n z_m = j_(0,n+1),
```

where `j_(0,n+1)` is a zero of the Bessel function `J_0`. The implementation
must use maintained SciPy special-function, integration, root-finding, and
linear-algebra routines when they match the mathematical task.

### Common observable

For both models and the reference dataset, report

```text
R_n = m_n / m_0.
```

The experimental ratio covariance must include the shared uncertainty of the
denominator. State assignments, confidence/status labels, asymmetric source
uncertainties, and any symmetrization rule must remain visible. A numerical
goodness-of-comparison measure is descriptive evidence, not a validation gate
for either phenomenological model.

## Reusable public components

Version 0.3 may introduce only the common structures demonstrated by this
comparison:

- a versioned reference-dataset schema with source, edition, locator, license,
  units, uncertainty, convention, state-assignment, and transformation
  metadata;
- a model-prediction record containing the construction, calibration rule,
  observable values, numerical uncertainties, and solver provenance;
- a comparison record containing aligned entries, covariance-aware residuals,
  excluded entries with reasons, and explicit interpretation limits; and
- a deterministic table and plot generated entirely from the stored dataset
  and computed predictions.

Do not add a general fitting framework, database client, model-ranking score,
or abstraction unsupported by these two constructions.

## Numerical verification

1. Preserve the soft-wall tridiagonal finite-difference solver.
2. Implement the hard-wall result with its analytic Bessel-zero reference and
   at least one numerical boundary-value or shooting calculation.
3. Add an independent maintained-library numerical route so that at least one
   spectrum is checked by two genuinely different numerical formulations.
4. Record at least three resolutions or cutoff choices for every convergence
   claim.
5. Separate discretization error, finite-cutoff error, solver tolerance, and
   external-data uncertainty in the output.

## Acceptance criteria

At the documented defaults:

1. the first four hard-wall numerical mass ratios agree with the analytic
   Bessel-zero ratios to a maximum relative error of `5e-4`;
2. the independent numerical routes agree on their common first four ratios to
   a maximum relative difference of `1e-3`;
3. the declared three-level refinement study shows no accepted ratio moving
   away from its analytic value at the finest level beyond the stated
   numerical tolerance;
4. the existing soft-wall and holographic-superconductor verification records
   and command defaults remain unchanged and pass their existing gates;
5. the reference dataset validates against its schema and records the frozen
   edition, exact source locator, access date, unit, uncertainty convention,
   assignment status, transformation, and license;
6. the comparison artifact is reproducible from a clean installation and
   identifies every fitted, calibrated, derived, included, and excluded value;
7. human-readable and JSON outputs state that agreement with selected masses
   is phenomenological comparison, not proof of QCD duality or precision-model
   validation; and
8. all scientific, numerical, schema, CLI, privacy, package, and skill tests
   pass on the supported Python versions.

## Explicitly not included

- A new or unpublished Explore hypothesis, candidate identity, private source,
  private calculation, or private result.
- A precision global fit, Bayesian model selection, or claim that one model is
  universally superior.
- Axial, pseudoscalar, baryon, finite-temperature, or finite-density sectors.
- Backreaction, top-down embeddings, or a claim that either model is derived
  from QCD in the relevant regime.
- Silent replacement of the frozen reference-data edition by newer online
  values.

## Stop conditions

Pause implementation and return to specification review if the chosen PDG
entries cannot be assigned reproducibly, their uncertainty metadata cannot be
redistributed with clear attribution, the two models would not be compared
under one common calibration rule, or the independent solver requires custom
numerical primitives without a documented necessity.

## Definition of done

Version 0.3 is complete only when both constructions produce inspectable
verification records, the independent-solver and refinement gates pass, the
frozen dataset and generated comparison artifact are reproducible from a clean
wheel, all older benchmarks remain unchanged, and the owner reviews the
scientific conventions and interpretation limits.
