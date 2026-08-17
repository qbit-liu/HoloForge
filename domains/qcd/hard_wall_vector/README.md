# Hard-Wall Vector Spectrum

This domain record contains the v0.3 hard-wall Forge/Verify benchmark.

- Scientific guide:
  [`docs/benchmarks/hard-wall-vector.md`](../../../docs/benchmarks/hard-wall-vector.md)
- Machine-readable record: [`model-card.json`](model-card.json)
- Implementation:
  [`hard_wall_vector.py`](../../../src/holoforge/benchmarks/hard_wall_vector.py)
- Verification tests:
  [`test_hard_wall_vector.py`](../../../tests/test_hard_wall_vector.py)

Run the maintained-library numerical routes with:

```bash
holoforge verify hard-wall-vector --method shooting
holoforge verify hard-wall-vector --method collocation
holoforge verify hard-wall-vector --method spectral
```

The original shooting and adaptive-collocation claim is owner-approved. The
new spectral-route claim remains explicitly `unreviewed` until scientific
owner review.
