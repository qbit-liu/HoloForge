# Gubser--Nellore Einstein--dilaton thermodynamics

This Forge/Verify record implements the five-dimensional, zero-density,
single-scalar bottom-up model of Gubser and Nellore,
[arXiv:0804.0434v2](https://arxiv.org/abs/0804.0434). It reproduces the
pure-cosh calibration curve in Figure 2 and the QCD-like red black-hole curve
in Figure 3.

The primary numerical route is a coupled Chebyshev--Lobatto boundary-value
solve with exact UV and horizon endpoints. A scalar-coordinate DOP853 route
provides an independent discretization and evolution-direction check. The
derived vector-figure anchors, source digests, equations, conventions,
boundary conditions, convergence tests, and interpretation limits are all
recorded explicitly.

Run the bounded verifier with:

```bash
holoforge verify gubser-nellore-ed
holoforge verify gubser-nellore-ed --profile figure --output-dir OUTPUT_DIR
python3 -m unittest tests.test_gubser_nellore_ed -v
```

This is Einstein--dilaton at zero chemical potential, not EMD or iHQCD.
`T_c_plot` is a plot registration rather than a predicted critical
temperature. Passing reproduces the selected effective-model calculations; it
does not empirically validate QCD. Xin-Yi Liu approved the AI-assisted model
record, derived anchors, and reproduced claim on 2026-08-17; that review does
not erase AI provenance or broaden the claim.
