# HoloForge Version 0.2.1 Specification

**Status:** complete and approved in scope by Xin-Yi Liu on 2026-08-02.

## Objective

Version 0.2.1 makes the Explore workflow privacy-safe by default. It separates
scientific status from publication status and establishes a standard path for
using HoloForge in a private research repository before a reviewed public
release.

## Included

- A constitutional public/private research boundary.
- A documented external private-project lifecycle and public-export checklist.
- A public incubator policy limited to synthetic, public-source, or explicitly
  approved material.
- Git ignore guards, contribution checks, and policy regression tests.
- A dry run of the Explore gates using the existing synthetic hypothesis card.
- Package and citation version metadata for `0.2.1`.

## Explicitly unchanged

- Both benchmark actions, equations, boundary conditions, numerical methods,
  defaults, tolerances, outputs, and model cards.
- The model-card and hypothesis-card schema versions and validation rules.
- The support-level and review-state taxonomies.
- The command-line interface.

## Acceptance criteria

1. The Constitution, contributor guidance, public incubator, and GitHub forms
   state the same disclosure boundary.
2. The workflow recommends a separate access-controlled repository and states
   that ignore rules are not a security boundary.
3. A public export requires explicit owner approval and a privacy review.
4. The synthetic dry run stops rather than manufacturing a scientific claim
   from an underspecified example.
5. Automated policy checks and all pre-existing scientific tests pass.
6. A built and installed wheel reports version `0.2.1`.
