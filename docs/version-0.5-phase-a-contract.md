# Version 0.5 Phase A — Benchmark Registry Migration Contract

**Status:** Decisions A1-A4 approved by Xin-Yi Liu on 2026-08-06. Xin-Yi Liu
approved the completed local Phase A implementation checkpoint on 2026-08-07.
Commit, Candidate A implementation, publication, and release remain separate
decisions.

## Recommendation

Implement Phase A as a behavior-preserving migration of the three existing
`verify` commands to one explicit in-repository benchmark registry. Keep
comparison and audit commands outside this registry for now. Do not add the
selected Version 0.5 benchmark until the migrated commands pass their frozen
compatibility tests.

## Frozen baseline

- Public baseline: HoloForge `v0.4.0`, commit
  `6914dbd82a94902125d0a73ef5c4ec3c9b61aaf5`.
- Existing registered targets after migration:
  `soft-wall-vector`, `hard-wall-vector`, and
  `holographic-superconductor`.
- No model equation, solver, default, tolerance, result, support label,
  model-card content, or evidence-bundle scientific state may change.
- `compare vector-spectrum` and both `audit` commands retain their present
  implementation in Phase A.
- No version bump occurs inside the registry refactor commit.

## Public need

The current CLI manually imports every model, creates every benchmark parser,
dispatches through benchmark-name conditionals, renders each result, and owns
all model-card and evidence-profile metadata. Adding one benchmark therefore
requires editing several unrelated parts of the same central module.

Phase A should separate generic command execution from benchmark-specific
configuration without pretending that heterogeneous numerical problems share
one solver interface.

## Proposed generic contracts

Add a small module at `src/holoforge/core/registry.py` containing public-beta
data contracts equivalent to the following shapes:

```text
ModelCardReference
  identifier: string
  schema_version: string
  repository_path: relative string
  sha256: lowercase hexadecimal string

BenchmarkExecution
  payload: JSON-compatible mapping
  passed: boolean
  artifacts: mapping from artifact role to Path

BenchmarkAdapter
  identifier: string
  description: string
  configure_parser(parser): add benchmark-specific options
  execute(namespace): return BenchmarkExecution
  render_human(execution): return ordered text lines
  scientific_state(payload): return evidence compatibility metadata
  model_cards: tuple of ModelCardReference
```

The exact Python annotations may be adjusted during implementation, but these
responsibilities and their separation are frozen. The adapter must not expose
or standardize a numerical solver signature.

## Deterministic registry

Add `src/holoforge/benchmarks/registry.py` with an explicit immutable tuple of
built-in adapters. Avoid decorators, import-time mutation, filesystem scans,
entry points, and environment-dependent discovery.

Registry construction must fail before command execution when:

- an identifier is empty, malformed, or duplicated;
- required adapter functions are not callable;
- a model-card path is absolute or escapes the repository-relative contract;
- a digest is malformed; or
- the explicit adapter order is nondeterministic.

Help output should list adapters in stable identifier order regardless of
their declaration order.

Adding a later in-repository benchmark may require adding one adapter to the
explicit built-in tuple. It must not require a new conditional branch in
`holoforge.cli`, `holoforge.core.evidence`, or the bundle writer.

## Generic `verify` execution path

The central CLI should:

1. create the top-level `verify` parser;
2. ask the registry to create one subparser per adapter;
3. add common `--json` and `--bundle-dir` options uniformly;
4. resolve the selected adapter by its validated identifier;
5. execute it and receive one `BenchmarkExecution`;
6. generate an optional bundle from the adapter's scientific state and model
   cards;
7. render either the existing human output or existing JSON output; and
8. return the frozen exit meaning.

The protected meanings are:

```text
0 = calculation completed and every scientific acceptance gate passed
1 = calculation completed but at least one scientific acceptance gate failed
2 = invalid input, unsupported setup, or controlled execution failure
```

Programming defects outside the declared controlled failures must not be
converted silently into exit `2`.

## Benchmark-specific adapter responsibilities

Each built-in adapter owns only command-facing glue:

- benchmark-specific argument definitions;
- construction and validation of the existing configuration object;
- invocation of the existing verifier;
- preservation of existing error text and controlled exception types;
- current human rendering;
- optional artifact generation;
- the current evidence scientific-state profile; and
- the current model-card reference.

Physics, solver code, acceptance calculations, result classes, and model-card
files remain unchanged in Phase A.

The public extension procedure is documented in the
[`benchmark-extension-guide.md`](benchmark-extension-guide.md).

## Compatibility snapshot

Before refactoring, tests must freeze representative behavior for each current
verifier:

- default human output;
- representative JSON output;
- a valid nondefault configuration;
- invalid-input message and exit `2`;
- a deliberately failed scientific tolerance where supported and exit `1`;
- evidence-bundle model-card references and scientific state; and
- the deterministic scientific-payload digest, excluding runtime-only
  metadata by the existing Version 0.4 rule.

Runtime version strings, timestamps, and absolute temporary output paths may
be normalized in comparisons. Scientific values, keys, meanings, ordering of
human lines, error wording, and digests may not be normalized away.

## Planned file scope

Phase A is limited to:

- `src/holoforge/core/registry.py`;
- `src/holoforge/core/__init__.py`;
- `src/holoforge/benchmarks/registry.py`;
- `src/holoforge/benchmarks/__init__.py`;
- `src/holoforge/cli.py`;
- `tests/test_benchmark_registry.py`;
- focused updates to `tests/test_cli.py`, `tests/test_evidence.py`, and
  `tests/test_evidence_schemas.py` only when needed for compatibility
  snapshots; and
- one public benchmark-extension guide.

Changing a benchmark physics module, model card, schema, reference dataset,
comparison implementation, or numerical test is outside Phase A and triggers
owner review.

## Acceptance criteria

Phase A passes only if:

1. Registry construction is deterministic and rejects malformed or duplicate
   adapters.
2. The three current `verify` commands are dispatched solely through the
   registry.
3. `holoforge.cli` contains no condition on a benchmark identifier.
4. The evidence bundle writer contains no benchmark identifier or
   benchmark-specific special case.
5. Existing default and nondefault human and JSON behavior matches the frozen
   compatibility snapshots.
6. Existing invalid inputs and controlled numerical failures retain their
   messages and exit meanings.
7. Existing evidence scientific states, model-card references, and
   deterministic payload identities are unchanged.
8. A synthetic test adapter can be registered and executed without editing
   central dispatch code.
9. Registry help ordering is stable, and duplicate identifiers fail before a
   calculation begins.
10. All 101 tests present at the contract baseline remain green, together with
    the new registry and snapshot tests.
11. The wheel installs cleanly and all three registered commands run from the
    installed wheel rather than the repository checkout.
12. `git diff --check` and the public privacy/export audit pass.

## Stop conditions

Stop and return to owner review if:

- one adapter must expose benchmark-internal solver state to satisfy the
  generic dispatcher;
- preserving an output or evidence digest requires hidden import order or
  mutable global registration;
- generic exception handling would hide programming defects;
- a benchmark result, tolerance, default, or interpretation changes;
- comparison or audit commands must be refactored to make registry migration
  work;
- the proposed file scope expands into model physics or schema migration; or
- any private or unpublished material appears in the public change.

## Owner decisions

### Decision A1 — contract shape

**Recommendation: approve.**

- **Reason:** the adapter standardizes command execution and evidence handoff
  while leaving heterogeneous solvers alone.
- **Opens:** implementation of the three generic data contracts.
- **Remains closed:** a common solver API and external plugins.
- **Uncertainty:** artifact rendering may require one optional typed callback,
  but it must remain explicit and generic.

### Decision A2 — deterministic built-in registry

**Recommendation: approve.**

- **Reason:** an explicit immutable built-in list is auditable and avoids
  import-order or arbitrary-code-loading behavior.
- **Opens:** migration of the three current verifiers.
- **Remains closed:** entry-point discovery and remote registries.
- **Uncertainty:** adding a benchmark still edits one declarative list; Version
  0.5 tests bounded extensibility rather than zero-touch external plugins.

### Decision A3 — compatibility and scope gates

**Recommendation: approve.**

- **Reason:** snapshots and the narrow file list protect the v0.4 scientific
  calculations while the command architecture changes.
- **Opens:** the planned source and test files only.
- **Remains closed:** physics, model cards, schemas, comparison refactoring,
  and version bumping.
- **Uncertainty:** human-output snapshots may expose accidental whitespace
  dependencies; any deliberate formatting change should be a later proposal.

### Decision A4 — implementation authorization

**Recommendation: approve Phase A implementation after A1–A3.**

- **Reason:** the acceptance and stop conditions now make the refactor
  reviewable before Candidate A is added.
- **Opens:** local Phase A code and tests on the current feature branch.
- **Remains closed:** commit, push, pull request, merge, Candidate A
  implementation, tag, and release.
- **Uncertainty:** a stop condition may return Phase A to contract review.

## Owner response recorded

Xin-Yi Liu approved Decisions A1-A4 on 2026-08-06. The generic adapter shape,
deterministic built-in registry, compatibility gates, planned file scope, and
stop conditions are accepted. This authorizes local Phase A implementation on
the current feature branch. It does not authorize Candidate A implementation,
commit, push, pull request, merge, tag, or release. Candidate A remains behind
the completed-and-reviewed Phase A checkpoint.

## Local implementation review checkpoint

The approved Phase A scope has been implemented on the feature branch without
changing a benchmark physics module, model card, schema, comparison model, or
package version.

Validation evidence:

- the three existing verifiers are registered through one immutable,
  identifier-sorted built-in registry;
- malformed identifiers, callbacks, model-card paths, digests, duplicate
  entries, and non-adapter entries fail before execution;
- a synthetic adapter passes the generic parser, execution, JSON, scientific
  state, model-card, and evidence-bundle path without a central special case;
- the migrated CLI contains no condition on a benchmark identifier, and the
  evidence writer contains no built-in benchmark identifier;
- all 109 tests pass, including the 101-test Version 0.4 baseline and eight new
  registry tests;
- representative human and normalized JSON output hashes are identical before
  and after migration for all three verifiers;
- side-by-side execution from baseline commit
  `6914dbd82a94902125d0a73ef5c4ec3c9b61aaf5` produces byte-identical result,
  configuration, and model-card context records;
- the corresponding scientific-payload digests are unchanged:
  `ab922c54698ca5f8b87a6180d66c938671ec5a26bfefb3a7326495b663ae83d5`
  for soft wall,
  `1bb3e5148128903e397410134d648707f6889ea06b6aeb4df6c65b1f9246b809`
  for hard wall, and
  `7bf4e719283433bc294e4c7f4f02fd64aba15f90a15186bb59365293f7989eab`
  for the superconductor benchmark;
- a clean wheel installs into a separate environment and runs all three
  registered commands from `site-packages`; and
- the public privacy scan passes for all thirteen proposed files.

This checkpoint establishes behavior preservation for the local Phase A
implementation. It does not approve a commit or automatically open Candidate
A implementation; both remain owner-controlled decisions.

## Owner checkpoint response recorded

Xin-Yi Liu approved this Phase A implementation checkpoint on 2026-08-07. The
reported behavior preservation, compatibility evidence, installed-wheel check,
and privacy audit are accepted for the local checkpoint. No commit, push, pull
request, merge, tag, or release is authorized by this approval. Candidate A
implementation also remains paused pending the separately requested compiled
scientific-contract review packet.
