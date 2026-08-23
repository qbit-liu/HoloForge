# HHH optical conductivity and superfluid density

This Forge/Verify entry extends the protected dimension-two HHH condensate
benchmark with the zero-momentum transverse Maxwell response. It verifies the
exact normal conductivity, the near-critical superfluid-density coefficient,
and agreement between spectral, Riccati, static-London, and finite-frequency
routes.

The existing condensate benchmark already reproduces source Figure 1's right
panel. The public rightmost curve in source Figure 2 is explicitly **not
reproduced**: its public caption, vector geometry, and condensate-rescaled
counterpart cannot be reconciled under the declared equations and
normalizations. HoloForge preserves that result as provenance-only evidence
and does not generate a source overlay or corrected caption.

Run:

```bash
holoforge verify holographic-superconductor-optical
holoforge verify holographic-superconductor-optical --json
holoforge verify holographic-superconductor-optical \
  --plot artifacts/hhh-near-critical-optical.png
```

The optional plot contains only HoloForge-computed static and finite-frequency
near-critical data. It is a model diagnostic, not a source-figure
reproduction.

See
[`docs/benchmarks/holographic-superconductor-optical.md`](../../../docs/benchmarks/holographic-superconductor-optical.md)
for equations, methods, numerical evidence, and limitations. The
[current contract](../../../docs/benchmarks/holographic-superconductor-optical-contract.md)
records the frozen accepted scope, while the
[development history](../../../docs/benchmarks/history/holographic-superconductor-optical-development-history.md)
preserves every mandatory stop and superseded route.

Xin-Yi Liu approved the corrected scientific result and bounded promotion on
2026-08-21. Material AI involvement remains recorded in the model card and
machine-readable verifier output.
