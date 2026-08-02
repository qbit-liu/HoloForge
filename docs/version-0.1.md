# HoloForge Version 0.1 Specification

**Status:** complete and approved by Xin-Yi Liu on 2026-08-02.

## Objective

Version 0.1 establishes the smallest end-to-end proof that HoloForge can encode
a published bottom-up model, solve it independently, classify its claims, and
detect a numerically inadequate reproduction.

## Included

- The Scientific Constitution and four-level claim taxonomy.
- Separate `domains/` and `incubator/` workflows.
- JSON Schema contracts for model cards and hypothesis cards, each at schema
  version `0.1`.
- One mature benchmark: transverse vector modes in the quadratic soft-wall
  model of Karch, Katz, Son, and Stephanov.
- A reusable Python implementation and `holoforge verify` command.
- Tests of the analytic formula, finite-difference spectrum, numerical
  convergence, schema examples, and command-line output.

## Explicitly not included

- A universal gauge/gravity software abstraction.
- Parameter fitting to experimental meson data.
- Backreaction, chiral symmetry breaking, axial modes, finite temperature, or
  topological sectors.
- Claims that the benchmark is a complete or precision description of QCD.
- Automatic promotion of AI-generated ideas from Explore to Forge/Verify.

## Benchmark acceptance criteria

With `kappa = 1 GeV`, four requested modes, 1,200 interior grid points, and
`z_max = 10 GeV^-1`:

1. the analytic values are `m_n^2 = 4, 8, 12, 16 GeV^2`;
2. the maximum relative numerical error is below `2e-4`;
3. increasing the grid resolution gives the approximately second-order error
   reduction expected from the centered stencil;
4. malformed configurations fail with a clear error;
5. machine-readable output contains parameters, results, errors, tolerance,
   pass/fail status, solver details, and software versions.

These criteria verify the discretized eigenvalue solver against this exact
problem. They do not establish phenomenological agreement with QCD.

## Definition of done

Version 0.1 is complete when all tests pass from a clean checkout, all example
cards satisfy their schemas, the documented command reproduces the acceptance
criteria, and a human has reviewed the scientific conventions. The release is
distributed under the BSD 3-Clause License.
