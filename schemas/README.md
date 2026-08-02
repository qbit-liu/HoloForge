# Card Schemas

HoloForge v0.1 uses JSON Schema Draft 2020-12.

- `model-card.schema.json` is the contract for literature-anchored
  Forge/Verify models.
- `hypothesis-card.schema.json` is the stricter contract for Explore proposals;
  its scientific claims can only use the `hypothesis` support level.

Canonical examples live at
`domains/qcd/soft_wall_vector/model-card.json`,
`domains/condensed_matter/holographic_superconductor/model-card.json`, and
`incubator/examples/hypothesis-card.example.json`. Validate them by running:

```bash
python3 -m unittest tests.test_schemas -v
```

Schema conformance checks structure and required provenance. It does not replace
human review of equations, sources, novelty, or physical reasoning.
For any non-`unreviewed` review state, the schemas require a reviewer name and
review date.
