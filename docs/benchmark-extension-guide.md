# In-Repository Benchmark Extension Guide

HoloForge Version 0.5 uses one validated registry for public Forge/Verify
benchmarks. This guide explains the software boundary; it does not replace the
scientific contract, literature review, model-card review, or owner approval
required for a new benchmark.

## Boundary

A benchmark adapter standardizes command execution and evidence handoff. It
does not standardize equations, boundary conditions, solver signatures, or
scientific acceptance gates. Those remain in the benchmark's physics module
and reviewed documentation.

Version 0.5 supports an explicit tuple of in-repository adapters. Dynamic
entry points, remote registries, arbitrary package discovery, and third-party
plugin loading are intentionally unsupported.

## Required adapter data

Each `BenchmarkAdapter` declares:

- a unique lowercase hyphenated command identifier;
- a short public description;
- a callback that adds benchmark-specific command arguments;
- an execution callback returning a `BenchmarkExecution`;
- a human renderer for that execution;
- a callback returning complete evidence compatibility metadata; and
- one or more immutable `ModelCardReference` values.

`BenchmarkExecution` contains only a JSON-compatible result mapping, the
declared pass/fail outcome, and explicitly named artifact paths. It deliberately
contains no common numerical-solver state.

## Adding an established public benchmark

1. Follow the repository's `holoforge-add-benchmark` workflow and obtain owner
   approval for the scientific and numerical contract before implementation.
2. Implement model physics in its own module using maintained numerical-library
   functions where they fit the problem.
3. Add command-facing callbacks and a `BenchmarkAdapter` in
   `holoforge.benchmarks.registry`.
4. Add the adapter once to the explicit `BUILTIN_BENCHMARKS` tuple.
5. Do not add a benchmark-name condition to `holoforge.cli`, the evidence
   writer, or another central dispatcher.
6. Add the model card, benchmark guide, analytic or literature target,
   convergence evidence, invalid-input checks, and command/evidence tests.
7. Run the full test suite, the installed-wheel command checks, and the public
   privacy/export preflight before requesting review.

Adding one adapter to the built-in tuple is a deliberate public code-review
event. Version 0.5 tests bounded modularity; it does not promise unreviewed or
zero-touch plugin installation.

## Controlled failures

Adapters may translate documented invalid inputs or expected numerical setup
failures into `BenchmarkExecutionError`. The central command returns exit `2`
and preserves the error message. Programming defects and undeclared exception
types must propagate instead of being silently relabelled as user errors.

The protected exit meanings are:

```text
0 = calculation completed and all scientific acceptance gates passed
1 = calculation completed but at least one scientific gate failed
2 = invalid input, unsupported setup, or controlled execution failure
```

## Evidence and artifacts

The adapter's scientific-state callback must declare the model identifier,
ensemble, fixed variables, approximation, phase branch, parameters, declared
controls, boundary sources, conventions, and source-record versions. Every
model-card reference uses a repository-relative path and a verified SHA-256
digest.

Artifacts are opt-in outputs produced by the benchmark. The generic command
layer passes them to the evidence writer and exposes their paths in JSON; it
does not infer artifact meaning from the benchmark identifier.

## Minimum extension tests

A new adapter must demonstrate:

- deterministic registry ordering and a unique valid identifier;
- unchanged generic help, JSON, human, and exit behavior;
- clear invalid-input and controlled-failure messages;
- exact model-card references and scientific-state metadata in its bundle;
- a relocatable bundle that passes integrity audit;
- analytic or source-data agreement and the preregistered numerical gates;
- convergence or cutoff refinement appropriate to the calculation; and
- absence of benchmark-specific conditions in the central CLI and evidence
  writer.

The registry test suite includes a synthetic adapter to prove that the generic
execution and bundle path work without editing central dispatch code.

## Privacy and scientific claims

Only public, literature-anchored Forge/Verify material belongs in this
registry. Unpublished Explore hypotheses, calculations, paths, results, and
identifiers remain in a separate access-controlled repository. A passing
adapter verifies its declared calculation; it is not empirical validation of
nature and does not authorize publication or disclosure.
