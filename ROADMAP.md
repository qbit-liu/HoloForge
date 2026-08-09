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

## Version 0.3 — controlled comparison (complete)

- Add convergence studies and cross-solver comparisons.
- Introduce reference datasets with uncertainty and convention metadata.
- Compare at least two bottom-up constructions against the same observable.
- Implement the proposed
  [soft-wall versus hard-wall vector-spectrum contract](docs/version-0.3.md)
  without depending on private Explore research.

## Version 0.4 — portable evidence bundles (complete)

- Bind configuration, scientific context, source records, results, acceptance
  checks, software versions, limitations, artifacts, and checksums into one
  relocatable evidence bundle.
- Add a fail-closed `same-state-family` compatibility preflight for ensemble,
  approximation, branch, parameter, boundary/source, convention, and unit
  metadata.
- Add optional bundle output to existing public verification and comparison
  commands without changing their defaults or scientific results.
- Demonstrate the workflow only with existing public benchmarks and synthetic
  mismatch fixtures.
- Follow the approved [Version 0.4 contract](docs/version-0.4.md) with public
  schemas, documentation, command integration, and regression coverage.

## Version 0.5 — stable extension and compatibility beta (complete)

- Replace benchmark-specific central dispatch with a tested in-repository
  registry and adapter while preserving existing public behavior.
- Define the limited CLI, Python, JSON, and schema surfaces protected during
  the `0.5.x` series.
- Publish schema-migration, backward-compatibility, deprecation, support, and
  security-reporting policies.
- Exercise installation and portable evidence auditing on Linux, macOS, and
  Windows CI runners.
- Add one owner-selected, literature-anchored public benchmark through the
  extension contract without a new central special case.
- Follow the implemented [Version 0.5 specification](docs/version-0.5.md),
  [compatibility policy](docs/version-0.5-compatibility-policy.md), and
  [public benchmark shortlist](docs/version-0.5-benchmark-shortlist.md).

## Explore-mode milestone

- Publicly demonstrate the screening gates with synthetic or already-published
  material.
- Run the first genuinely novel hypothesis in a separate private repository;
  disclose it only after journal acceptance or another explicit release
  decision by the research owner.

The roadmap intentionally does not name a speculative application before that
screening is done.
