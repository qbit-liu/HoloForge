# Version 0.5.9 specification — fail-closed integrity hardening

## Purpose

Version 0.5.9 closes scientific-state and evidence-integrity gaps without
changing any accepted benchmark calculation. It is a patch-level correction
to invalid states that could previously appear passing or internally
consistent.

## Result contracts

- An acceptance record contains at least one check.
- Check state is explicitly boolean and any numerical check value is finite.
- A verification result derives its pass state from its checks.
- Benchmark execution state, serialized result state, and derived check state
  must agree.
- Extension metadata cannot replace a canonical field.
- Public result payloads contain strict finite JSON and an explicit recognized
  support label.

These requirements implement the existing Constitution rule that successful
execution alone is insufficient and that every benchmark declares at least
one analytic, convergence, regression, or external-data check.

## Evidence bundles

Bundle inputs are validated before the destination is changed. Records and
artifacts are assembled in a private staging directory; the completed bundle
is moved into place only after serialization, privacy checks, hashing, and
manifest validation succeed. A failed write leaves a new destination absent or
an existing empty destination empty.

Artifact inputs and bundle destinations must not be symbolic links. Auditing
continues to reject symbolic or undeclared bundle files and now also compares
the manifest semantically with the configuration, model-card context, and
result records.

Support level, acceptance state and checks, software versions, scope, and
limitations must agree across their duplicated evidence locations. Hash
agreement alone is not sufficient.

## JSON and environment provenance

Every command's `--json` path rejects non-finite or non-serializable content
with controlled exit `2`. Evidence JSON remains deterministic and finite.

Runtime provenance adds Python implementation, byte order, operating-system
class, machine architecture, and a SHA-256 fingerprint of the NumPy and SciPy
build reports. Raw build reports, paths, hostnames, usernames, and environment
variables are not recorded.

## Compatibility boundary

All documented Version 0.5 commands, successful output meanings, Python import
paths, scientific equations, defaults, tolerances, and accepted results remain
unchanged. Inputs that are empty, contradictory, non-boolean, non-finite,
implicitly labelled, or symbolic now fail closed.

The published evidence-bundle schema remains Version `0.4` in this patch. It is
not silently tightened in place. Runtime audit applies the Constitution's
stronger semantic invariants; a future stricter machine-readable schema
requires a new schema version and migration note.

The Gubser--Nellore backend-sensitive residual is not part of this generic
hardening contract. Any investigation remains a separate bounded diagnostic
and cannot change a tolerance without scientific review.

## Required validation

- contract and registry fail-closed tests;
- evidence creation, relocation, integrity, semantic-consistency, privacy, and
  schema tests;
- strict CLI JSON tests;
- runtime-provenance privacy tests;
- complete public unit-test suite;
- every current verifier required by CI;
- packaging and cross-platform CI; and
- public-export scanning plus final diff review.
