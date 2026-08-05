# Soft-Wall and Hard-Wall Vector-Spectrum Comparison

## Question

Can HoloForge compare two established bottom-up constructions on the same
observable without hiding their different infrared assumptions, numerical
errors, data conventions, or phenomenological limitations?

The common observable is

```text
R_n = m_n / m_0.
```

This removes the single dimensionful scale from each construction. The lowest
state is a calibration anchor, not a goodness-of-comparison data point.

## Frozen reference data

The packaged snapshot transcribes three 2024 Particle Data Group light-meson
summary-table listings:

```text
rho(770)^0: 775.26 +/- 0.23 MeV  (anchor)
rho(1450):  1465 +/- 25 MeV      (candidate n=1)
rho(1700):  1720 +/- 20 MeV      (candidate n=2)
```

The snapshot records the exact table-page locator, edition, access date,
license, source-file SHA-256 hash, mass convention, and state-assignment
status. It is packaged with the wheel rather than fetched live.

The listed mass errors are initially treated as independent because the
summary table does not provide their covariance. After normalization, the
shared `rho(770)^0` denominator generates a positive covariance between the
two excited-state ratios. HoloForge propagates that covariance with the exact
Jacobian rather than treating the ratios as independent.

## Model predictions

The quadratic soft wall predicts

```text
R_n = sqrt(n + 1).
```

The hard wall predicts

```text
R_n = j_(0,n+1) / j_(0,1).
```

The checked table and plot under `docs/generated/vector-spectrum/` are
generated from the packaged dataset and the two executable solvers. The JSON
record preserves solver settings, numerical errors, covariance-aware
residuals, exclusions, and interpretation limits.

## Run and regenerate

```bash
holoforge compare vector-spectrum
holoforge compare vector-spectrum --json
holoforge compare vector-spectrum \
  --output-dir docs/generated/vector-spectrum
```

## Interpretation limits

The `rho(1450)` and `rho(1700)` radial assignments are visible candidate
assignments, not exact QCD labels. The covariance-aware chi-square values are
descriptive diagnostics and are deliberately excluded from release acceptance
gates. They do not prove QCD duality, establish precision validity, or justify
a universal ranking of the two constructions.

The frozen dataset and hard-wall model card remain marked `unreviewed` until
their source transcription, assignments, and interpretation limits receive
owner review.
