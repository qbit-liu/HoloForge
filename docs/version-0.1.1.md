# HoloForge Version 0.1.1 Specification

**Status:** complete and approved by Xin-Yi Liu on 2026-08-02.

## Objective

Version 0.1.1 makes the first public release easier to test, cite, and
contribute to without changing its scientific calculation or public command
interface.

## Included

- Automated tests across the declared Python floor and representative newer
  versions.
- An independent wheel and source-distribution build check.
- Machine-readable software citation metadata.
- Contribution guidance and structured GitHub issue forms for bugs,
  Forge/Verify benchmarks, and Explore hypotheses.
- A pull-request checklist and changelog.

## Explicitly unchanged

- The quadratic soft-wall action, Schrödinger potential, and analytic spectrum.
- Numerical discretization, solver, defaults, tolerance, and output fields.
- Model-card and hypothesis-card schema versions.
- Scientific-support labels and promotion rules.

## Acceptance criteria

1. All 16 existing tests pass without modification to their expected physics.
2. The default soft-wall benchmark retains its `2e-4` acceptance tolerance and
   passes with the same numerical result as `v0.1.0`.
3. The source distribution and wheel build successfully, and the installed
   wheel reports version `0.1.1`.
4. The workflow, citation metadata, and GitHub issue forms are syntactically
   valid.
5. Repository checks find no private paths, secrets, generated build files, or
   unpublished research content in the proposed release.
