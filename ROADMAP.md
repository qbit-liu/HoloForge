# Roadmap

## Version 0.1 — trustworthy foundation (complete)

- Freeze the constitution and scientific support labels.
- Validate model-card and hypothesis-card schemas.
- Reproduce the quadratic soft-wall vector spectrum analytically and
  numerically.
- Provide a small command-line verification path and automated tests.
- Release under the BSD 3-Clause License.

## Version 0.1.1 — public project hardening (complete)

- Run tests and package builds automatically on GitHub.
- Add citation metadata, contribution guidance, and structured issue forms.
- Preserve the `v0.1.0` scientific calculation and command interface.

## Version 0.2 — reusable model interface (complete)

- Define common background, fluctuation-equation, boundary-condition, solver,
  observable, and result interfaces.
- Add configuration serialization and provenance-rich result artifacts.
- Add a second benchmark with genuinely different boundary conditions so the
  interface is tested rather than assumed.
- For the candidate holographic-superconductor onset benchmark, distinguish the
  nonzero boundary gauge-field source (chemical potential in the grand
  canonical ensemble) from the vanishing scalar source used to model
  spontaneous condensation; state the ensemble explicitly.
- Reproduce the dimension-two nonlinear condensate curve corresponding to the
  right panel of Figure 1 in arXiv:0803.3295v1, using generated numerical data
  and an explicit fixed-density presentation.

## Version 0.2.1 — private Explore workflow (complete)

- Make clear that Explore is a scientific-support category, not a requirement
  to disclose work in progress.
- Keep novel and potentially publishable work in a separate private repository
  until journal acceptance or explicit release approval.
- Restrict the public incubator to synthetic examples, public-literature dry
  runs, and material approved for disclosure.
- Add accidental-commit guards, a public-export checklist, and policy tests.
- Exercise the public workflow on the deliberately synthetic hypothesis-card
  example without introducing a novel scientific claim.

## Version 0.2.2 — auditable research gates (complete)

- Distinguish new-domain, new-subfield/new-phenomenon, and method-transfer or
  model-improvement Explore tracks.
- Document the frozen-contract, calculation, verification, critic,
  owner-review, decision, and commit lifecycle.
- Keep scientific support, research authorization, and disclosure as separate
  states.
- Standardize outcome-first PDF owner-review packets with a reusable LaTeX
  template and rendered-page quality check.
- Preserve all private candidate identities, calculations, and results outside
  the public repository.

## Version 0.2.3 — reusable agent workflows (complete)

- Require an evidence-based recommendation for every owner decision request.
- Package research-gate, benchmark-development, and public-export procedures
  as repository-scoped Agent Skills.
- Add a deterministic export preflight utility and regression tests.
- Clarify the distinction between pre-1.0 interface stability and bounded
  scientific readiness.

## Version 0.3 — controlled comparison (specification proposed)

- Add convergence studies and cross-solver comparisons.
- Introduce reference datasets with uncertainty and convention metadata.
- Compare at least two bottom-up constructions against the same observable.
- Implement the proposed
  [soft-wall versus hard-wall vector-spectrum contract](docs/version-0.3.md)
  without depending on private Explore research.

## Explore-mode milestone

- Publicly demonstrate the screening gates with synthetic or already-published
  material.
- Run the first genuinely novel hypothesis in a separate private repository;
  disclose it only after journal acceptance or another explicit release
  decision by the research owner.

The roadmap intentionally does not name a speculative application before that
screening is done.
