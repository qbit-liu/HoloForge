# Vector-spectrum controlled comparison

This v0.3 domain compares two established bottom-up AdS/QCD constructions
against the same dimensionless radial vector-meson mass ratios:

- the quadratic soft wall of arXiv:hep-ph/0602229; and
- the hard wall of arXiv:hep-ph/0501128.

The frozen PDG snapshot under `reference-data/` records source locators,
uncertainties, conventions, state-assignment caveats, licensing, and a hash of
the reviewed source PDF. It is deliberately not a live query: a future PDG
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

The data transcription is currently marked `unreviewed`. Schema conformance
checks its structure and provenance, not the correctness of the physical state
assignments. Model agreement will be reported as a bounded phenomenological
comparison, not proof of QCD duality or precision validation.
