# Hard-wall chiral Model A

This provisional Forge/Verify record implements the public two-flavor
hard-wall chiral model of Erlich, Katz, Son, and Stephanov,
[arXiv:hep-ph/0501128v2](https://arxiv.org/abs/hep-ph/0501128).

The primary route uses exact-endpoint UV-factorized Chebyshev generalized
eigenproblems for the rho, transverse a1, and pion modes. Adaptive
`solve_bvp` calculations check the normalizable modes at three UV cutoffs. A
backward DOP853 route evaluates the axial zero mode with the public-source
regulator and is checked against adaptive collocation and its analytic UV
logarithm.

Run locally with:

```bash
holoforge verify hard-wall-chiral
holoforge verify hard-wall-chiral --json
holoforge verify hard-wall-chiral --output-dir OUTPUT_DIR
python3 -m unittest tests.test_hard_wall_chiral -v
```

The comparison labels `m_pi`, `m_rho`, and `f_pi` as source fit targets and
the remaining four Table II entries as source predictions. Passing reproduces
the selected truncated effective-model calculation; it does not validate QCD
or the hard-wall boundary condition in nature. Xin-Yi Liu approved the
AI-assisted numerical result and model-card provenance on 2026-08-20; that
review does not widen the recorded scientific or publication scope.
