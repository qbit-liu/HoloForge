# DeWolfe--Gubser--Rosen zero-density EMD thermodynamics

This Forge/Verify record implements the Phase 5A neutral sector of the
phenomenological bottom-up EMD model in DeWolfe, Gubser, and Rosen,
[arXiv:1012.1864v2](https://arxiv.org/abs/1012.1864). The bounded target is the
pair of black-hole curves in source Figure 3: `s/T^3` and `chi_2/T^2` at zero
chemical potential.

The primary calculation is a UV-factorized Chebyshev boundary-value solve at
three spectral degrees. Scalar-coordinate DOP853 backgrounds, an explicit
Maxwell solve, quadrature refinement, the Einstein constraint, and derived
public vector-path anchors provide independent checks.

```bash
holoforge verify dewolfe-gubser-rosen-emd
holoforge verify dewolfe-gubser-rosen-emd --output-dir OUTPUT_DIR
python3 -m unittest tests.test_dewolfe_gubser_rosen_emd -v
```

Xin-Yi Liu approved the bounded Figure 3 result, model card, and material AI
provenance on 2026-08-22. The support level is `reproduced`: passing verifies
the selected source-model calculation but does not validate QCD or lattice
data and does not open finite-density work. A later Phase 5B must reproduce
Figure 5 and the reported model critical point; Figure 4 is diagnostic only
unless a separate owner decision changes that boundary.
