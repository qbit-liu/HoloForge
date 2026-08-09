# Linear-axion DC conductivity

This Forge/Verify model record reproduces the exact four-dimensional DC
electric conductivity of the homogeneous linear-axion model in Andrade and
Withers, arXiv:1311.5157v2.

The background has a nonzero chemical-potential source and nonzero spatially
linear massless-scalar sources. It is homogeneous because the bulk stress
tensor is homogeneous, not because translation-breaking sources are absent.

The numerical verifier integrates the source paper's two complex ingoing
master fields at four finite frequencies. It constructs a unit gauge-field
source with zero scalar/metric fluctuation sources, reconstructs the original
coupled equations, checks the finite-frequency radial flux identity, extracts
the boundary current, and extrapolates the DC limit. The analytic expression
is used only as an acceptance target.

Run the focused implementation tests with:

```bash
python3 -m unittest tests.test_linear_axion_dc -v
```

Xin-Yi Liu approved the reproduced claim and the recorded AI-assisted
provenance on 2026-08-09. The support level remains `reproduced`. No material
interpretation, top-down embedding, full optical spectrum, or private-research
result is included.
