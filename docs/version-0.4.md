# HoloForge Version 0.4 Specification

**Status:** implemented and approved by Xin-Yi Liu for the public `v0.4.0`
release on 2026-08-06.

## Recommendation

Make Version 0.4 the **portable evidence-bundle and scientific-compatibility
release**.

HoloForge already produces machine-readable benchmark and comparison records,
but it does not yet bind a result to its configuration, scientific context,
source records, acceptance checks, software versions, generated artifacts, and
checksums as one relocatable unit. It also does not provide a generic preflight
that rejects attempts to combine records from incompatible ensembles,
approximation levels, branches, source conditions, or parameter sets.

Version 0.4 should make that provenance enforceable without adding a new
physics model or changing any existing scientific result.

## Objective

Version 0.4 should answer two public framework questions:

1. Can a HoloForge calculation be moved to another directory or machine and
   audited as the same calculation without relying on private paths or
   undocumented local state?
2. Before a derivative, continuation, or same-family synthesis is attempted,
   can HoloForge identify whether its input records actually describe one
   compatible physical state family?

A passing bundle audit establishes integrity, declared provenance, and
contract compatibility. It does not establish that the underlying model is a
correct description of nature or that combining compatible records is
scientifically interesting.

## Public need

The current public interfaces already record many necessary ingredients:

- benchmark definitions, configurations, numerical methods, results,
  acceptance checks, software versions, and scope;
- reviewed model cards with equations, conventions, boundary conditions,
  observables, limitations, and source provenance; and
- versioned reference-data, prediction, and comparison records.

The missing layer is a portable manifest that binds those records and artifacts
together and an explicit compatibility contract for calculations that claim to
belong to one state family. Version 0.4 should add that layer rather than a new
benchmark.

## Evidence bundle

An evidence bundle should use a small, inspectable directory layout:

```text
evidence-bundle/
  manifest.json
  records/
    model-card.json
    configuration.json
    result.json
  artifacts/
    ... optional generated tables or figures ...
```

The versioned manifest should require:

- bundle identifier and schema version;
- HoloForge version and normalized command identity;
- model-card identifier and content hash;
- support level and disclosure class;
- ensemble and variables held fixed;
- approximation/backreaction level;
- phase or branch identifier;
- parameter set and explicitly varied controls;
- boundary and source conditions relevant to the observable;
- observable, units, normalization, and convention identifiers;
- numerical method, configuration, and software versions;
- acceptance checks, pass/fail state, scope, and limitations;
- every included record and artifact with a relative path, role, media type,
  and SHA-256 digest; and
- a deterministic scientific-payload digest that excludes timestamps and
  other execution metadata that do not change the calculation.

Absolute filesystem paths, credentials, hostnames, user names, and undeclared
external files are forbidden. Timestamps may be recorded as execution metadata
but may not alter the scientific-payload digest.

## Compatibility preflight

Version 0.4 should implement one narrow relation:
`same-state-family`. It is intended for inputs that will be differentiated,
continued, or synthesized as one physical branch.

The preflight should compare:

- model or construction identifier;
- ensemble and fixed variables;
- approximation and backreaction level;
- phase and branch identity;
- parameters other than explicitly declared controls;
- boundary/source conditions;
- observable conventions, normalization, and units; and
- source-record and schema versions.

The result should be a machine-readable report containing every matched field,
every mismatch, the declared controls allowed to vary, and an overall
pass/fail state. It must not silently coerce units, infer a branch from file
names, or treat missing metadata as compatible.

Cross-model phenomenological comparison is not part of this relation. The
controlled-comparison contracts introduced in Version 0.3 remain the correct
path for comparing different constructions on a common observable.

## Command surface

All current public verification and comparison commands should gain an
optional portable-output path:

```text
holoforge verify <benchmark> --bundle-dir PATH
holoforge compare <comparison> --bundle-dir PATH
```

Two audit commands should be added:

```text
holoforge audit bundle PATH
holoforge audit compatibility BUNDLE_A BUNDLE_B \
  --relation same-state-family
```

Every command should support human-readable output and `--json`. Existing
commands, defaults, exit codes, and ordinary JSON output must remain unchanged
when `--bundle-dir` is absent.

## Clean public implementation

Version 0.4 should be implemented from this public specification and the
existing public benchmarks. It should not copy a private research artifact,
private path, candidate identity, unpublished equation, numerical result,
literature note, or private Git history.

Public demonstrations should use only:

- existing literature-anchored HoloForge benchmarks;
- existing controlled-comparison records; and
- deliberately synthetic mismatch fixtures that contain no novel scientific
  claim.

The export preflight scanner and manual disclosure review must be run on every
proposed Version 0.4 file before a public pull request.

## Implementation surfaces

The implementation proposal is limited to:

- `schemas/evidence-bundle.schema.json`;
- `schemas/evidence-compatibility.schema.json`;
- a shared evidence-bundle module under `src/holoforge/core/`;
- additive `audit` commands and `--bundle-dir` options in the CLI;
- focused bundle, digest, portability, mismatch, CLI, schema, and privacy
  tests;
- one public guide for creating and auditing bundles; and
- synchronized schema documentation, agent onboarding, changelog, and roadmap
  records.

If implementation requires benchmark-specific bundle writers rather than one
shared adapter around existing result records, stop and return to specification
review.

## Acceptance criteria

Version 0.4 is acceptable only if all of the following pass:

1. Every current public `verify` and `compare` command can emit a bundle without
   changing its numerical result, default configuration, acceptance gate, or
   existing JSON output.
2. Every emitted bundle validates against the Version 0.4 schema and contains
   only relative internal paths.
3. Moving a complete bundle to a different directory preserves a passing audit.
4. Changing one byte in a declared record or artifact causes the integrity
   audit to fail and identify the affected path.
5. Reordering JSON object keys does not change the deterministic scientific-
   payload digest.
6. The `same-state-family` preflight rejects, in separate focused tests,
   mismatched ensemble, approximation level, branch, undeclared parameter,
   and boundary/source condition.
7. Missing required compatibility metadata fails closed rather than producing
   a warning-only pass.
8. A positive fixture with only explicitly declared control variables changed
   passes and reports those changes.
9. Bundle generation records limitations and support level and never converts
   a benchmark pass into empirical validation or candidate promotion.
10. The public-export scanner reports no private path, credential, forbidden
    token, or unpublished-content leak in the proposed change.
11. All existing scientific, numerical, schema, CLI, package, skill, and
    privacy tests remain green on supported Python versions.

## Explicitly not included

- A new benchmark, physical model, observable, fit, or scientific result.
- A private Explore candidate, source, calculation, result, or workflow history.
- Automatic export from a private repository.
- A remote artifact registry, database, cloud service, notebook runner,
  workflow engine, or experiment-tracking platform.
- Cryptographic signing, identity attestation, or long-term archival service.
- Automatic unit conversion, ensemble transformation, branch inference, or
  repair of incomplete metadata.
- Cross-model ranking or replacement of the Version 0.3 controlled-comparison
  contract.
- A claim that schema-valid or compatible inputs are physically correct.
- Freezing the public Python or CLI interface as the Version 1.0 contract.

## Stop conditions

Pause implementation and return to owner review if:

- deterministic scientific content cannot be separated cleanly from runtime
  metadata;
- portable bundles require absolute paths or undeclared external files;
- compatibility depends on model-specific hidden heuristics rather than
  explicit manifest fields;
- artifact inclusion creates a provenance or licensing problem;
- bundle generation changes an existing numerical result, default, or
  acceptance gate;
- supporting all current commands requires duplicated benchmark-specific
  implementations; or
- the proposed public change contains any private or unpublished material.

## Path toward Version 1.0

Version 0.4 would make individual calculations portable and their scientific
context auditable. The remaining blockers before a Version 1.0 proposal would
then be explicit rather than model-specific:

1. freeze the minimum stable Python and CLI interfaces;
2. define schema migration and backward-compatibility policy;
3. verify bundle portability across every supported Python version and CI
   operating system;
4. define deprecation, support, and security-reporting policies;
5. demonstrate that a new public benchmark can use the stable contracts without
   adding another one-off interface; and
6. conduct a final documentation and contributor usability review.

Version 1.0 should mean that these public contracts are stable and maintainable,
not that HoloForge contains every gauge/gravity model or that its phenomenology
has been empirically validated.

## Owner decisions

1. Approve Version 0.4 as the portable evidence-bundle and compatibility-
   preflight release.
2. Approve the narrow `same-state-family` relation and keep cross-model
   comparison under the existing Version 0.3 contract.
3. Approve optional bundle output for every current public verification and
   comparison command, with no change when the option is absent.
4. Approve the acceptance criteria, stop conditions, explicit exclusions, and
   clean public implementation boundary.
5. Implement the approved contract as a separate logical change.

Xin-Yi Liu approved all five decisions on 2026-08-06. That approval authorized
implementation. Commit, push, pull request, merge, tag, and release remain
separate repository actions requiring their own explicit authorization.
