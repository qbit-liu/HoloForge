# Version 0.6 specification — inspectable capability contracts

## Purpose

Version 0.6 lets a user or agent determine what a built-in verifier explicitly
supports before running it. It adds a solver-free index over existing public
benchmark evidence; it does not create new physical evidence.

The public problem is narrow: benchmark-specific model cards and guides record
coverage and limitations, but software cannot query that boundary through one
uniform contract. Version 0.6 supplies that missing inspection layer while
leaving the heterogeneous scientific solvers and the protected Version 0.5
adapter interface intact.

## Capability receipt

Every built-in `verify` benchmark has exactly one receipt conforming to
`schemas/benchmark-capability.schema.json` at schema version `0.6`. A receipt
declares:

- the benchmark identifier, mode, and support level;
- covered solution branches and ensembles;
- parameter coverage as fixed, bounded, finite-set, or configurable;
- machine-readable outputs and their `result`, `evidence`, or `diagnostic`
  artifact roles;
- transformations already supported by public validation evidence;
- known excluded or unqualified routes;
- model-card and documentation references; and
- AI and human-review provenance.

The runtime rejects missing or unknown fields, invalid identifiers, empty
declaration sets, duplicate capability IDs, contradictory review provenance,
unsafe repository paths, an empty registry, duplicate benchmark receipts, a
receipt set that differs from the built-in benchmark registry, or model-card
references that differ from the corresponding adapter.

## Inspection command and Python API

The CLI form is:

```bash
holoforge inspect benchmark BENCHMARK
holoforge inspect benchmark BENCHMARK --require CAPABILITY_ID --json
```

`--require` is repeatable. Each exact identifier is classified as:

- `qualified`: a declared output or validated transformation;
- `known-gap`: an explicitly declared exclusion or unqualified route; or
- `not-declared`: absent from both sets.

With no requirements, successful receipt inspection exits `0`. With
requirements, exit `0` means every identifier is `qualified`; exit `1` means
at least one identifier is a known gap or is not declared; exit `2` is invalid
input or a controlled contract failure. Inspection never invokes an adapter or
solver.

The public Python entry point is
`holoforge.capabilities.inspect_benchmark_capabilities`. Typed fail-closed
contracts are exported as:

- `holoforge.core.CapabilityInspection`;
- `holoforge.core.CapabilityReceipt`;
- `holoforge.core.CapabilityReceiptError`; and
- `holoforge.core.CapabilityRegistry`.

## Scientific boundary

A receipt is an index of declared public evidence. It does not infer support
from similar wording, answer a natural-language physics question, establish
that a model is true, certify novelty or publishability, or authorize a private
research direction. `not-declared` means only that this public receipt makes no
qualification statement.

A downstream transformation is qualified only when its domain, conventions,
uncertainty propagation, numerical convergence, acceptance evidence, and
limitations are themselves declared. The presence of upstream numerical
arrays is not sufficient.

## Compatibility and non-goals

Version 0.6 does not change any accepted benchmark equation, boundary
condition, ensemble, numerical method, default, tolerance, result, or claim.
It adds no universal solver API, dynamic plugin discovery, remote registry,
LLM-based scientific judge, generic `research` command, or new benchmark.

The Version 0.5 command and Python surfaces remain valid. Capability receipts
are a new Version 0.6 schema and are not folded into the existing Version 0.1
model-card schema.

## Required validation

- JSON Schema validation for the schema and all built-in receipts;
- one receipt per built-in benchmark and exact adapter model-card alignment;
- fail-closed malformed, duplicate, incomplete, unsafe-path, and contradictory
  provenance tests;
- exact-ID classification and controlled CLI exit tests;
- a no-solver-execution regression test;
- installed-package resource inspection;
- public privacy and content-policy checks;
- the complete unit suite and documented soft-wall verifier;
- `git diff --check`, public-export scanning, and final owner review.

Commit, push, pull request, merge, release, and branch deletion remain separate
owner decisions.
