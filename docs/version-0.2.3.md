# HoloForge Version 0.2.3 Specification

**Status:** implemented for release review on 2026-08-05.

## Objective

Version 0.2.3 packages the reusable procedures exercised during the v0.2
development cycle without changing either public scientific benchmark. It
also makes owner recommendations mandatory and clarifies how a pinned pre-1.0
release can support bounded research while the public interfaces continue to
evolve.

## Included

- A mandatory item-by-item recommendation, concise evidence-based reason,
  scope effect, and main uncertainty whenever an owner is asked to approve or
  choose.
- Three repository-scoped Agent Skills for bounded research gates,
  Forge/Verify benchmark additions, and privacy-reviewed public exports.
- A deterministic export preflight utility that detects common home-directory
  paths, private-key markers, and caller-supplied forbidden tokens while still
  requiring manual scientific, provenance, licensing, and disclosure review.
- Public documentation separating pre-1.0 interface stability from the
  scientific readiness of a pinned, explicitly verified calculation.
- Skill-structure, export-utility, recommendation-policy, and privacy
  regression tests.

## Explicitly unchanged

- Both benchmark actions, equations, boundary conditions, numerical methods,
  defaults, tolerances, outputs, plots, and model cards.
- The model-card and hypothesis-card schema versions and validation rules.
- The support-level and review-state taxonomies.
- The command-line interface.
- No private candidate identity, paper cache, equation, result, data, path,
  report, numerical implementation, or repository history is included.

## Acceptance criteria

1. Every owner decision list includes an explicit item-by-item recommendation,
   reason, scope effect, and uncertainty or tradeoff; insufficient evidence
   produces a recommendation to pause for named missing evidence.
2. All three repository skills pass structural validation and contain no
   private candidate information.
3. The export utility passes clean, platform-home-path, private-key,
   custom-token, and error-path tests; it does not echo detected sensitive
   content and warns that manual review remains required.
4. The public documentation explains that scientific readiness is bounded by
   evidence and exact versioning rather than the major version number alone.
5. The complete scientific, numerical, schema, CLI, skill, and policy suite
   passes, and both public verifiers retain their v0.2.2 results.
6. A built and clean-installed wheel reports version `0.2.3`.
