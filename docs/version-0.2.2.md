# HoloForge Version 0.2.2 Specification

**Status:** implemented for owner review on 2026-08-05.

## Objective

Version 0.2.2 makes the private Explore process reproducible without exposing
private research. It documents a generic contract-to-decision gate workflow,
restores the three accepted Explore novelty tracks, and standardizes concise
PDF owner-review packets.

## Included

- Three explicitly distinguished Explore tracks: new domain, new subfield or
  phenomenon, and method transfer or model improvement.
- A reusable frozen-contract, calculation, verification, critic, owner-review,
  decision, and commit sequence.
- A mandatory item-by-item recommendation, reason, scope effect, and tradeoff
  whenever an owner is asked to approve or choose.
- Separate scientific-support, research-authorization, and disclosure states.
- Local private-Git guidance that preserves reviewed and negative results.
- A sanitized owner-review PDF style guide and reusable LaTeX template.
- Three repository-scoped agent skills for research gates, Forge/Verify
  benchmark additions, and privacy-reviewed public exports.
- A deterministic export preflight utility that detects common home-directory
  paths, private-key markers, and caller-supplied forbidden tokens while still
  requiring manual scientific and disclosure review.
- A public explanation separating pre-1.0 interface stability from the
  scientific readiness of a pinned, bounded calculation.
- Documentation and policy regression tests for the public/private boundary.
- Package and citation version metadata for `0.2.2`.

## Explicitly unchanged

- Both benchmark actions, equations, boundary conditions, numerical methods,
  defaults, tolerances, outputs, plots, and model cards.
- The model-card and hypothesis-card schema versions and validation rules.
- The support-level and review-state taxonomies.
- The command-line interface.
- No private candidate identity, paper cache, equation, result, path, report,
  or repository history is included.

## Acceptance criteria

1. The public documentation identifies all three Explore novelty tracks.
2. The gate workflow freezes scope before calculation and separates owner
   authorization from scientific support and disclosure.
3. The PDF style and template are generic, reusable, and contain no private
   research information.
4. Every owner decision list includes an explicit item-by-item recommendation,
   reason, scope effect, and uncertainty or tradeoff; if evidence is
   insufficient, the recommendation is to pause for named missing evidence.
5. Public policy tests reject private paths and require the generic workflow's
   owner-review and disclosure boundaries.
6. All three repository skills pass structural validation and contain no
   private candidate information.
7. The export utility passes clean, leak, custom-token, and error-path tests
   and explicitly warns that manual review remains required.
8. The full pre-existing scientific and policy test suite passes.
9. A built and installed wheel reports version `0.2.2`.
