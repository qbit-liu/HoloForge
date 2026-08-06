# Card Schemas

HoloForge v0.1 uses JSON Schema Draft 2020-12.

- `model-card.schema.json` is the contract for literature-anchored
  Forge/Verify models.
- `hypothesis-card.schema.json` is the stricter contract for Explore proposals;
  its scientific claims can only use the `hypothesis` support level.
- `reference-dataset.schema.json` records a frozen external dataset, including
  its edition, exact source, license, conventions, uncertainties, entry
  assignments, transformations, and review provenance.
- `model-prediction.schema.json` records one construction, calibration rule,
  solver provenance, aligned values, and numerical errors.
- `comparison-record.schema.json` records the aligned reference, model
  predictions, covariance-aware descriptive residuals, numerical gates,
  exclusions, and interpretation limits.
- `evidence-bundle.schema.json` records a portable bundle manifest with
  scientific-state metadata, relative file paths, checksums, acceptance
  evidence, software versions, support level, and limitations.
- `evidence-compatibility.schema.json` records every match, mismatch, declared
  control, and allowed control change in a fail-closed `same-state-family`
  preflight.

Canonical examples live at
`domains/qcd/soft_wall_vector/model-card.json`,
`domains/condensed_matter/holographic_superconductor/model-card.json`, and
`domains/qcd/hard_wall_vector/model-card.json`,
`incubator/examples/hypothesis-card.example.json`, and
`src/holoforge/data/reference/pdg-2026-rho-masses.json`.
Validate them by running:

```bash
python3 -m unittest tests.test_schemas -v
python3 -m unittest tests.test_evidence_schemas -v
```

Schema conformance checks structure and required provenance. It does not replace
human review of equations, sources, novelty, or physical reasoning.
For any non-`unreviewed` review state, the schemas require a reviewer name and
review date.
