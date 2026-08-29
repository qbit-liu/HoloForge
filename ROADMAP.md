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

## Version 0.5.9 — fail-closed integrity hardening (completed)

- Reject empty, contradictory, non-boolean, or non-finite verification state.
- Prevent extension metadata from replacing canonical result fields.
- Require explicit support labels and consistency across evidence records.
- Write evidence bundles transactionally and reject symbolic artifact inputs.
- Strengthen privacy-safe numerical environment fingerprints.
- Preserve all accepted equations, solvers, defaults, tolerances, results,
  commands, and supported Version 0.5 schemas.
- Follow the bounded
  [Version 0.5.9 specification](docs/version-0.5.9.md) and
  [research-acceleration implementation brief](docs/research-acceleration-agent-brief-v3.md).

## Version 0.6 — inspectable capability contracts (complete)

- Ship one fail-closed capability receipt for every built-in verifier.
- Record branch, ensemble, parameter, output, artifact-role, validated-
  transformation, evidence, and known-gap boundaries.
- Add a solver-free Python API and `holoforge inspect benchmark` command with
  exact-ID `qualified`, `known-gap`, and `not-declared` classifications.
- Keep benchmark equations, solvers, defaults, tolerances, results, and the
  protected Version 0.5 command meanings unchanged.
- Do not add a universal solver interface, dynamic plugins, an LLM scientific
  judge, or a generic research runtime in this milestone.
- Follow the bounded [Version 0.6 specification](docs/version-0.6.md).

## Classical benchmark sequence

This sequence records the owner-selected Forge/Verify progression. A completed
phase means that its bounded benchmark and release gate are closed; it does not
mean that the model is empirically validated.

| Phase | Benchmark | Central literature target | Primary method | State |
| ---: | --- | --- | --- | --- |
| 0 | Spectral numerical foundation | Soft-wall analytic spectrum and hard-wall Bessel spectrum | Chebyshev pseudospectral | complete |
| 1 | Gubser--Nellore ED | Source Figures 2 and 3 | Coupled Chebyshev BVP with DOP853 check | complete |
| 2 | Gubser--Rocha EMD control | Exact charged background, thermodynamics, and low-temperature linear entropy | Coupled Chebyshev BVP against exact solution | complete |
| 3 | Hard-wall chiral QCD | GMOR relation and source Table II | Chebyshev eigenvalue/BVP | complete |
| 4 | HHH optical conductivity | Near-critical coefficient and protected Figure 1 condensate result | Chebyshev fluctuation BVP with Riccati DOP853 check | complete in Version 0.5.5 |
| 5A | DeWolfe--Gubser--Rosen EMD at `mu = 0` | Both black-hole curves in source Figure 3 | One-parameter neutral Chebyshev background scan | complete in Version 0.5.6 |
| 5B | DeWolfe--Gubser--Rosen finite-density EMD | Representative charged backgrounds and the reported critical coordinates; Figure 5 remains provenance-only | Selected-state Chebyshev verification through flux-reduced and simultaneous-Maxwell formulations | reduced core complete on `main`; seven gates pass |
| 5C | DeWolfe--Gubser--Rosen critical scaling | Selected source critical exponents | Preregistered near-critical regressions | optional future extension, not required by the Phase 5B classical example |

The [classical benchmark sequence](docs/benchmarks/classical-sequence.md) is
closed through the reduced Phase 5B core. The Gubser--Rocha Phase 2 benchmark
is retained as a top-down-derived exact
control for the numerical infrastructure, not as a representative bottom-up
model. DeWolfe--Gubser--Rosen is the selected phenomenological bottom-up EMD
sequence. Phase 5A is deliberately limited to the zero-density calibration.
The re-scoped Phase 5B core verifies representative charged backgrounds and
the reported critical-coordinate neighborhood without requiring a global
phase diagram. The Figure 5 absolute ordinate and topology are not Phase 5B
acceptance targets. The preserved C3h topology hard stop and any Phase 5C
critical-scaling work remain separate optional extensions rather than
unfinished classical-example work.

## Explore-mode milestone

- Publicly demonstrate the screening gates with synthetic or already-published
  material.
- Use the [research objective](docs/research-objective.md) to select one private
  scientific opportunity and run an end-to-end vertical slice at its honest
  horizon: open discovery, strategic development, or short-horizon execution.
- Treat current capability receipts as cost and readiness evidence, not as a
  scientific-value ranking or a restriction to existing benchmark families.
- Treat that vertical slice as a research capability proof, not a public
  package release or a promise of a positive result.
- Draft new contracts inside the private project first, then promote only
  demonstrated reusable behavior through a separate public-export review.
- Do not add another public benchmark unless it directly unlocks an approved
  claim or supplies an otherwise missing integrity control.
- Disclose private work only after journal acceptance or another explicit
  release decision by the research owner.

The roadmap intentionally does not name a speculative application before that
screening is done. Documentation-only workflow changes do not by themselves
require a new package release.
