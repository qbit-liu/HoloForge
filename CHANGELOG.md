# Changelog

All notable changes to HoloForge are recorded here.

## [Unreleased]

### Documentation

- Record the completed Phase 5A implementation and Version 0.5.6 integration,
  pull-request and post-merge CI, annotated tag, tag CI, and GitHub release as
  the Phase 5A closure point. Phase 5B and Phase 5C remain closed pending
  separate owner-reviewed contracts.

## [0.5.6] - 2026-08-22

### Added

- An owner-approved DeWolfe--Gubser--Rosen bottom-up EMD benchmark reproducing
  both zero-density black-hole curves in source Figure 3 with a UV-factorized
  Chebyshev background, independent scalar-coordinate DOP853 reconstruction,
  explicit Maxwell response, convergence, residual, determinism, and
  source-anchor checks.
- Approved model-card, derived public Figure 3 anchor records, strict JSON/CSV
  evidence, HoloForge-generated reproduction plot, benchmark guide, frozen
  scientific contract, CLI adapter, and focused tests for Phase 5A.

### Changed

- Protect the new `holoforge verify dewolfe-gubser-rosen-emd` command and
  `holoforge.benchmarks.verify_dewolfe_gubser_rosen_emd` export in the Version
  0.5 compatibility policy.
- Extend installed-wheel and cross-platform portability CI with the DGR
  verifier and focused scientific contract tests.

### Documentation

- Record the completed Version 0.5.5 integration, post-merge CI, tag, and
  release as the Phase 4 closure point.
- Record the owner-selected DeWolfe--Gubser--Rosen bottom-up EMD sequence as
  Phase 5: Figure 3 at zero chemical potential in Phase 5A, finite-density
  Figure 5 and the critical point in Phase 5B, and selected critical exponents
  in Phase 5C. Figure 4 is an optional charged-scan diagnostic rather than a
  required reproduction target.
- Add the owner-approved prospective Phase 5A Forge/Verify contract, bounded
  implementation, Figure 3 preflight, and result-review packet. The numerical
  gates pass, and Xin-Yi Liu approved the bounded result and model card as a
  `reproduced` source-model calculation on 2026-08-22. This does not validate
  QCD or open finite-density Phase 5B.

### Scientific results

- All fourteen Phase 5A gates pass. Maximum Figure 3 anchor errors are
  `0.08398744` for `s/T^3` against `0.15` and `0.002607142` for `chi_2/T^2`
  against `0.005`; the Chebyshev--DOP853 maximum relative difference is
  `1.163957e-6` against `5e-4`, and duplicate-run observable difference is
  exactly zero.
- The result reproduces the selected public source-model curves only. It does
  not empirically validate QCD or lattice data and does not calculate Figure
  5, the critical point, finite-density phase structure, or critical exponents.

## [0.5.5] - 2026-08-21

### Added

- An owner-approved HHH optical-response benchmark with a source-free UV
  series transfer, Chebyshev bulk solve, independent Riccati-form DOP853
  response, static and finite-frequency superfluid-density checks, portable
  evidence, and an original near-critical diagnostic.

### Changed

- The Python test matrix, installed-wheel smoke test, and Linux, macOS, and
  Windows portability jobs now run the HHH optical verifier; portability also
  runs its focused scientific contract tests.
- Removed an undocumented test-only `3e-8` fence from the already rejected W2
  tiny-element diagnostic after Python 3.9 exposed backend-sensitive roundoff.
  The public `1e-8` exact-normal gate, equation and boundary residual gates,
  resolution budget, and W2 negative status are unchanged.
- Reclassified the superseded high-degree X exact-normal ladder as a portable
  roundoff-plateau diagnostic after Windows measured a maximum independent
  residual of `1.50452e-7` at `N=640`, while its exact conductivity, boundary,
  conditioning, truncation, and resolution checks remained far inside their
  frozen ceilings. The diagnostic now uses the already owner-reviewed `1e-6`
  control residual ceiling; the historical X2 failure, accepted verifier
  gates, exact-normal `1e-8` observable gate, and physical results are
  unchanged.

### Scientific results

- The benchmark reproduces the exact normal conductivity and the HHH
  near-critical dimension-two coefficient `C_2 = 24`: the independent static
  and finite-frequency fits give `23.96884335` and `23.96883307`. It also
  protects the existing Figure 1 right-panel condensate reproduction. Source
  Figure 2 remains explicitly `not_reproduced` because its public caption,
  vector path, and condensate-rescaled counterpart cannot be reconciled. A
  passing result verifies this bounded probe-limit model calculation; it is
  not empirical validation of a material or microscopic pairing mechanism.

## [0.5.4] - 2026-08-20

### Added

- An owner-approved two-flavor hard-wall chiral Model A benchmark with
  source-blind Chebyshev generalized eigenproblems, independent adaptive
  collocation, all seven source Table II entries, and the GMOR limit.

### Changed

- Installed-wheel and Linux, macOS, and Windows portability checks now run the
  hard-wall chiral verifier and its focused scientific contract tests.

### Scientific results

- All eleven frozen gates pass. The benchmark labels `m_pi`, `m_rho`, and
  `f_pi` as source fit targets and the other four Table II entries as source
  predictions. Its generated comparison graphic is explicitly not a source
  figure. Passing reproduces the bounded effective-model calculation; it does
  not empirically validate QCD, a hard IR wall, or omitted higher operators.

## [0.5.3] - 2026-08-19

### Added

- A clean-room Chebyshev--Gauss--Lobatto numerical module plus opt-in spectral
  routes for the soft-wall and hard-wall vector benchmarks, with three-level
  polynomial-degree convergence evidence.
- A clean-room zero-density Gubser--Nellore Einstein--dilaton benchmark with
  coupled Chebyshev collocation, exact endpoints, independent DOP853 checks,
  derived Figure 2/3 anchors, artifact generation, and an owner-approved model
  record that retains its AI provenance.
- A clean-room Gubser--Rocha Einstein--Maxwell--dilaton control benchmark with
  coupled Chebyshev collocation, exact-background, equation, constraint, flux,
  refinement, thermodynamic, low-temperature, neutral-limit, determinism,
  artifact, and portable-bundle checks.
- A current architecture guide covering the Forge/Verify execution path,
  repository layers, dependency rules, extension point, and deliberate
  Version 0.5 non-goals.
- A generic two-state research-knowledge template that keeps live working
  observations separate from human-reviewed knowledge and owner-accepted
  closure lessons.

### Changed

- Isolated each built-in benchmark's command-facing adapter glue in its own
  module and reduced `holoforge.benchmarks.registry` to the explicit
  composition root.
- Explore workflows now capture reusable knowledge from literature, model
  dictionaries, derivations, numerical methods, data, bounded results,
  decisions, and reproducibility work. General items require named human review;
  closure lessons still require owner-reviewed closure.
- Classical bottom-up benchmark contracts now require a quantitative central
  source figure or table when feasible, or an owner-reviewed reason and an
  alternative quantitative literature check.
- The Gubser--Rocha final scaled-collocation ceiling is prospectively set to
  the method-conditioned `2e-8` after successive release-candidate runs
  measured `1.960378e-9` on Ubuntu and `3.6060792132977416e-9` on Python
  3.11.16, while the degree-80 binary64 differentiation scale was
  `epsilon ||D2||_inf = 1.2124701243009436e-8`. Its `1e-9` TRF-polish trigger
  and every independent physics gate are unchanged; both earlier runs remain
  recorded as failures of their then-active ceilings.

### Scientific results

- The new spectral routes independently reproduce the existing analytic
  soft-wall and hard-wall targets. The Einstein--dilaton implementation is
  locally passing its preregistered coupled-equation, convergence, independent
  DOP853, determinism, and source-curve gates. Its model card, derived anchors,
  and reproduced claim were approved by Xin-Yi Liu on 2026-08-17; the new
  soft-/hard-wall spectral-route claims remain unreviewed. No passing
  calculation is presented as empirical validation of QCD.
- The owner-approved Gubser--Rocha control reproduces only the bosonic
  background and source Eqs. (2)--(6) within thirteen numerical gates. It is a
  top-down-derived control, not a representative bottom-up example, and it
  does not reproduce the paper's charged-fermion Figure 1 or establish
  stability, a Fermi liquid, QCD, or empirical agreement with any material.

## [0.5.2] - 2026-08-12

### Added

- A generic closure-retrospective template and outcome taxonomy for positive,
  negative, inconclusive, conditional, source-stopped, prior-art-stopped, and
  technically stopped Explore gates.
- An agent-facing lesson-retrieval checkpoint with stable lesson IDs, retrieval
  tags, primary-evidence review, applicability boundaries, and explicit
  candidate-specific controls in the Explore intake scorecard.

### Changed

- Closed research gates now preserve both their bounded result and a reusable
  lesson with a non-inference boundary and reopening trigger.
- New Explore intakes must review relevant prior lessons before assigning
  readiness statuses; prior failure guides a sharper test but is not evidence
  that a new candidate is false.

### Scientific results

- No model equation, solver, default, acceptance tolerance, benchmark output,
  schema contract, or scientific result changed. No private Explore artifact,
  identifier, path, unpublished result, or private lesson ledger is included.

## [0.5.1] - 2026-08-11

### Added

- A validated research-progress renderer and generic JSON template that model
  project-local research groups, parallel checks, branches, feedback loops,
  and one current stage. It produces Markdown/Mermaid without extra packages
  and standalone SVG, PNG, or PDF through the maintained Graphviz engine.

### Changed

- Owner-review handoffs now include completed/current/next status, closed
  scope, one recommended A-E response path, and a status-only option that does
  not authorize further work.
- The review-packet template can include an optional dated progress page while
  preserving the standalone figure and private project state as the canonical
  research record.

### Scientific results

- No model equation, solver, default, acceptance tolerance, benchmark output,
  schema contract, or scientific result changed. No private Explore artifact,
  identifier, path, or unpublished result is included.

## [0.5.0] - 2026-08-09

### Added

- A deterministic in-repository benchmark registry and adapter contract for
  command execution, evidence handoff, model-card references, and controlled
  failures without a common numerical-solver abstraction.
- The literature-anchored linear-axion DC-conductivity verifier, model card,
  scientific contract, source-map and finite-frequency reconstruction checks,
  radial-flux audit, DC extrapolation, refinements, and public guide.
- A protected `0.5.x` command, Python API, schema-migration, deprecation,
  platform-support, and private security-reporting policy.
- Built-wheel portability checks on Ubuntu, macOS, and Windows, including
  evidence-bundle relocation and integrity audit.
- A reusable compiled-PDF owner-review rule for scientific contracts whose
  equations, tables, or plots are difficult to review reliably in Markdown.

### Changed

- Migrated all existing verification commands to generic registry dispatch
  while preserving names, defaults, JSON semantics, exit meanings, model-card
  digests, and evidence behavior.
- Extended installed-wheel smoke coverage to all four public verifiers.

### Scientific results

- Reproduced the selected four-dimensional Andrade-Withers linear-axion model
  result `sigma_DC = 1 + mu^2/alpha^2` for three frozen nonzero-source cases
  within the preregistered numerical gates. This verifies the declared
  bottom-up calculation; it is not empirical validation of a material,
  microscopic mechanism, or top-down embedding.
- No private Explore candidate, calculation, identifier, path, or unpublished
  research result is included.

## [0.4.0] - 2026-08-06

### Added

- Cross-agent onboarding through a canonical `AGENTS.md`, a Claude Code
  compatibility import, and a first-session guide with safe prompts,
  workflow selection, validation, and private Explore boundaries.
- Portable evidence bundles for every current verification and comparison
  command, with relative paths, SHA-256 file hashes, deterministic scientific
  payload identities, model-card provenance, acceptance evidence, software
  versions, support levels, and limitations.
- `holoforge audit bundle` integrity checks and a fail-closed
  `holoforge audit compatibility` preflight for the narrow
  `same-state-family` relation.
- Versioned evidence-bundle and compatibility-report schemas, public usage
  guidance, and focused portability, mutation, schema, CLI, and privacy tests.

### Changed

- Reframed the README around HoloForge's domain-general gauge/gravity contract
  and moved concrete model names into a compact reference-implementation
  section, where they document current executable examples rather than define
  the platform's scope.
- Added optional `--bundle-dir` output without changing existing command
  defaults, ordinary JSON records when the option is omitted, numerical
  methods, or acceptance gates.

### Scientific results

- No model equation, solver, default, acceptance tolerance, benchmark result,
  or scientific interpretation changed. New schemas describe infrastructure
  evidence only. No private research artifact or result is included.

## [0.3.0] - 2026-08-05

### Added

- A hard-wall transverse-vector benchmark with analytic Bessel-zero reference,
  adaptive shooting, independent global collocation, and UV-cutoff refinement.
- Reusable ground-state normalization with full covariance propagation for a
  shared reference denominator.
- Frozen, hashed 2026 Particle Data Group rho-meson listings with explicit
  uncertainty, source, license, convention, assignment, exclusion, and human
  review provenance.
- Reference-dataset, model-prediction, and controlled-comparison schemas.
- A `holoforge compare vector-spectrum` workflow with reproducible JSON,
  Markdown, and plot artifacts comparing quadratic soft-wall and hard-wall
  vector spectra.

### Changed

- Marked the hard-wall model card, PDG transcription, default candidate
  assignments, and excluded `rho(1570)` alternative as reviewed and approved
  by Xin-Yi Liu while retaining their scientific limitations.
- Generalized the README project-status language so HoloForge remains clearly
  identified as a gauge/gravity platform rather than a QCD-only package.

### Scientific results

- The hard-wall shooting and collocation routes reproduce the first four
  normalized Bessel-zero masses within their declared `5e-4` and `1e-3`
  acceptance tolerances, with monotonic three-level UV-cutoff refinement.
- The default descriptive comparison treats `rho(1450)` and `rho(1700)` as
  candidate radial assignments and records `rho(1570)` as an excluded,
  ambiguous `n=2` alternative.
- Covariance-aware agreement values are descriptive diagnostics, not model
  acceptance gates or evidence of precision QCD validity. No private Explore
  candidate, calculation, or unpublished result is included.

## [0.2.3] - 2026-08-05

### Added

- Three repository-scoped HoloForge Agent Skills for research gates,
  benchmark development, and privacy-reviewed public exports.
- A tested export preflight scanner for common home paths, private-key
  markers, and caller-supplied forbidden tokens.

### Changed

- Required every owner approval or choice list to include an item-by-item
  recommendation, concise reason, scope effect, and main uncertainty.
- Clarified that pre-1.0 interface evolution is separate from the scientific
  readiness of a pinned, bounded, independently checked calculation.

### Scientific results

- No model equation, solver, default, acceptance tolerance, benchmark output,
  schema contract, or scientific result changed from `v0.2.2`. No private
  research artifact, implementation, or result is included.

## [0.2.2] - 2026-08-04

### Added

- A generic contract-to-decision research-gate workflow for private Explore
  projects.
- A reusable LaTeX template and visual-QA checklist for owner-review PDF
  packets.
- Policy regression checks for gate records, three novelty tracks, and the
  public/private disclosure boundary.

### Changed

- Distinguished new-domain, new-subfield/new-phenomenon, and method-transfer
  or model-improvement Explore tracks.
- Clarified that scientific support, research authorization, and disclosure
  status are independent.

### Scientific results

- No model equation, solver, default, acceptance tolerance, benchmark output,
  schema contract, or scientific result changed from `v0.2.1`. No private
  research artifact or result is included.

## [0.2.1] - 2026-08-02

### Added

- A documented private-repository workflow for novel Explore projects.
- A public synthetic dry run that demonstrates the Explore screening gates.
- Regression checks and ignore guards for the public/private boundary.

### Changed

- Clarified that Explore is a scientific-support category, not an obligation
  to disclose unpublished research.
- Restricted the public incubator and Explore issue form to synthetic,
  public-source, or explicitly approved material.

### Scientific results

- No model equation, solver, default, acceptance tolerance, benchmark output,
  schema contract, or scientific result changed from `v0.2.0`.

## [0.2.0] - 2026-08-02

### Added

- Shared scientific descriptors and verification-result contracts.
- Linear-onset and nonlinear-condensate verification for the minimal
  probe-limit holographic superconductor in the `Delta = 2` quantization.
- Regenerated Figure 1 right-panel observable with optional Matplotlib output.

### Changed

- The soft-wall vector benchmark now emits the shared v0.2 verification
  envelope while preserving its numerical method and acceptance gate.

### Scientific results

- Development result: `mu_c/r_h = 4.06371366` and
  `T_c/sqrt(rho) = 0.11842676`.
- Development result: the nonlinear curve reproduces the near-critical
  coefficient `144` and approaches
  `sqrt(<O_2>)/T_c approximately 8.44` within the probe-limit calculation.

## [0.1.1] - 2026-08-02

### Added

- GitHub Actions test matrix and package-build smoke test.
- Citation metadata, contribution guidance, and structured issue forms.
- Pull-request checks for scientific support, provenance, and private data.

### Changed

- Documented the `v0.1.1` maintenance scope and clarified the proposed
  holographic-superconductor UV sources for future `v0.2.0` work.

### Scientific results

- No model equation, solver, default, acceptance tolerance, or benchmark result
  changed from `v0.1.0`.

## [0.1.0] - 2026-08-02

- Established the Scientific Constitution and support taxonomy.
- Added machine-readable model-card and hypothesis-card schemas.
- Added the verified quadratic soft-wall vector-spectrum benchmark.

[0.5.6]: https://github.com/qbit-liu/HoloForge/compare/v0.5.5...v0.5.6
[0.5.5]: https://github.com/qbit-liu/HoloForge/compare/v0.5.4...v0.5.5
[0.5.4]: https://github.com/qbit-liu/HoloForge/compare/v0.5.3...v0.5.4
[0.5.3]: https://github.com/qbit-liu/HoloForge/compare/v0.5.2...v0.5.3
[0.5.2]: https://github.com/qbit-liu/HoloForge/compare/v0.5.1...v0.5.2
[0.5.1]: https://github.com/qbit-liu/HoloForge/compare/v0.5.0...v0.5.1
[0.5.0]: https://github.com/qbit-liu/HoloForge/compare/v0.4.0...v0.5.0
[0.4.0]: https://github.com/qbit-liu/HoloForge/compare/v0.3.0...v0.4.0
[0.3.0]: https://github.com/qbit-liu/HoloForge/compare/v0.2.3...v0.3.0
[0.2.3]: https://github.com/qbit-liu/HoloForge/compare/v0.2.2...v0.2.3
[0.2.2]: https://github.com/qbit-liu/HoloForge/compare/v0.2.1...v0.2.2
[0.2.1]: https://github.com/qbit-liu/HoloForge/compare/v0.2.0...v0.2.1
[0.2.0]: https://github.com/qbit-liu/HoloForge/compare/v0.1.1...v0.2.0
[0.1.1]: https://github.com/qbit-liu/HoloForge/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/qbit-liu/HoloForge/releases/tag/v0.1.0
