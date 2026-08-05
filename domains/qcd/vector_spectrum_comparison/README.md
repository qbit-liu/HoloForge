# Vector-spectrum controlled comparison

This v0.3 domain compares two established bottom-up AdS/QCD constructions
against the same dimensionless radial vector-meson mass ratios:

- the quadratic soft wall of arXiv:hep-ph/0602229; and
- the hard wall of arXiv:hep-ph/0501128.

The frozen PDG snapshot under
`src/holoforge/data/reference/pdg-2026-rho-masses.json` records source locators,
uncertainties, conventions, state-assignment caveats, licensing, and hashes of
the reviewed source PDFs. It is deliberately not a live query: a future PDG
update must create a new versioned dataset rather than silently changing this
comparison.

The reusable `holoforge.core.normalize_spectrum` transformation computes these
ratios and propagates a full input covariance with the exact Jacobian. This is
important here because the common `rho(770)^0` denominator correlates the two
excited-state ratios even when the three listed masses are initially treated
as independent.

The hard-wall verifier uses the published UV Dirichlet and IR Neumann
conditions. Its zero-cutoff reference is generated with
`scipy.special.jn_zeros`; the finite-cutoff problem is then solved independently
by adaptive shooting and global collocation. The implementation reports
finite-cutoff effects separately from solver tolerances because agreement with
the analytic Bessel zeros is a numerical reproduction gate, not an empirical
claim about QCD.

The default scenario uses `rho(1450)` and `rho(1700)` as candidate modes, while
the listed `rho(1570)` is retained as an excluded, ambiguous `n=2` alternative.
PDG omits `rho(1570)` from its Summary Table and notes that it may be an
OZI-violating decay mode of `rho(1700)`, so HoloForge does not silently assume
that it is an independent radial state.

Xin-Yi Liu approved the data transcription, the default candidate assignments,
and the excluded `rho(1570)` alternative on 2026-08-05. This records review of
the documented convention without turning a candidate state assignment into
an exact physical identification. Model agreement remains a bounded
phenomenological comparison, not proof of QCD duality or precision validation.
