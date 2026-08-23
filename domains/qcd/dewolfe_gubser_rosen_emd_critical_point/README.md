# DeWolfe--Gubser--Rosen finite-density EMD

This Forge/Verify record implements a bounded classical example for the
phenomenological bottom-up Einstein--Maxwell--dilaton model of DeWolfe,
Gubser, and Rosen,
[arXiv:1012.1864v2](https://arxiv.org/abs/1012.1864).

The owner-approved reduced Phase 5B core verifies:

- neutral, representative charged, and high-charge backgrounds at `N=80`;
- a direct critical candidate at `N=80`, then the same located state at
  `N=120` and `N=150`;
- the reported source neighborhood `(T_c,mu_c)=(143 MeV,783 MeV)`;
- independently evaluated equations, constraint, boundaries, Gauss flux,
  Noether charge, and target conditions; and
- agreement between the primary flux-reduced Chebyshev formulation and a
  simultaneous geometry--scalar--Maxwell Chebyshev formulation.

The current calculation gives

```text
(T_c,mu_c) = (142.973974 MeV,781.693762 MeV).
```

The public command is

```bash
holoforge verify dewolfe-gubser-rosen-emd-finite-density
holoforge verify dewolfe-gubser-rosen-emd-finite-density --json
holoforge verify dewolfe-gubser-rosen-emd-finite-density \
  --output-dir OUTPUT_DIR
```

The source Figure 5 artwork uses `mu_BH` horizontally and an unresolved
`rho_source_figure5` vertically. The verified canonical dictionary is
`rho_canonical_BH=q/2`; no public source establishes a map between these two
density coordinates. Consequently the digitized Figure 5 anchors are
provenance-only, and neither absolute ordinate agreement nor full Figure 5
topology can affect this benchmark's acceptance.

The earlier C3h dense topology campaign is retained as a failed optional
extension. Its primary-temperature overlap gate remains failed; the reduced
contract does not waive or repair that result. Global phase topology,
coexistence, critical exponents, DOP853 cross-validation, and empirical QCD
claims are outside this example.

Xin-Yi Liu approved the reduced numerical result, model card, and evidence
boundary on 2026-08-23. This approval does not open the optional topology
campaign, Phase 5C, or a release.
See the [benchmark guide](../../../docs/benchmarks/dewolfe-gubser-rosen-emd-critical-point.md)
and [Phase 5B contract](../../../docs/benchmarks/dewolfe-gubser-rosen-emd-phase-5b-contract.md)
for equations, tolerances, provenance, and the optional-extension history.
