# HoloForge Version 0.2.2 Specification

**Status:** released on 2026-08-04.

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
- Separate scientific-support, research-authorization, and disclosure states.
- Local private-Git guidance that preserves reviewed and negative results.
- A sanitized owner-review PDF style guide and reusable LaTeX template.
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
4. Public policy tests reject private paths and require the generic workflow's
   owner-review and disclosure boundaries.
5. The full pre-existing scientific and policy test suite passes.
6. A built and installed wheel reports version `0.2.2`.
