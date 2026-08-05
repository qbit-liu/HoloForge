# Hard-Wall Vector Spectrum

This domain record contains the v0.3 hard-wall Forge/Verify benchmark.

- Scientific guide:
  [`docs/benchmarks/hard-wall-vector.md`](../../../docs/benchmarks/hard-wall-vector.md)
- Machine-readable record: [`model-card.json`](model-card.json)
- Implementation:
  [`hard_wall_vector.py`](../../../src/holoforge/benchmarks/hard_wall_vector.py)
- Verification tests:
  [`test_hard_wall_vector.py`](../../../tests/test_hard_wall_vector.py)

Run either maintained-library numerical route with:

```bash
holoforge verify hard-wall-vector --method shooting
holoforge verify hard-wall-vector --method collocation
```

The model card is marked `unreviewed` until its scientific transcription and
interpretation limits receive owner review.
