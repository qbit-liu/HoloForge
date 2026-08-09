# HoloForge Version 0.5 Specification

**Status:** implemented and approved by Xin-Yi Liu for the public `v0.5.0`
release on 2026-08-09.

## Recommendation

Make Version 0.5 the **stable-extension and compatibility beta**.

Version 0.4 made individual calculations portable and auditable. Version 0.5
should test whether a new literature-anchored benchmark can enter HoloForge
through one declared extension contract without adding another model-specific
branch to the central command implementation. At the same time, it should
define the limited interfaces that users may rely on throughout the `0.5.x`
series.

This is a public Forge/Verify infrastructure milestone. It must not contain or
depend on private Explore candidates, calculations, paths, results, or Git
history.

## Present evidence and architectural gap

HoloForge already provides:

- shared scientific descriptors and a `VerificationRecord` result envelope;
- three heterogeneous executable benchmarks;
- model-card, comparison, evidence-bundle, and compatibility schemas;
- portable evidence generation and integrity auditing; and
- agent and contributor workflows with explicit privacy boundaries.

The current command layer still imports each benchmark directly, constructs
each argument parser manually, dispatches each calculation through a dedicated
conditional branch, and stores model-card metadata in central constants. A
fourth benchmark would therefore extend a pattern that does not yet demonstrate
bounded modular growth.

The current CI suite also runs its Python-version matrix only on Ubuntu. The
project declares Python `>=3.9`, but portable evidence bundles have not yet
been exercised on all three major CI operating systems. Schema migration,
deprecation, support, and security-reporting policies are not yet public
contracts.

## Version 0.5 objectives

Version 0.5 should answer five questions:

1. Can an in-repository benchmark register its command, configuration,
   verifier, renderers, model card, and evidence context without editing the
   central dispatch logic?
2. Can all existing commands migrate to that route without changing their
   names, defaults, numerical results, JSON records, exit meanings, or evidence
   bundles?
3. Can one newly selected public benchmark use the same extension route
   without adding a one-off core interface?
4. Which CLI, Python, JSON, and schema surfaces are protected during the
   `0.5.x` series, and how will incompatible changes be announced?
5. Do installation, verification, bundle relocation, and auditing work on
   supported Python versions and representative Linux, macOS, and Windows
   runners?

## In-repository benchmark extension contract

Add one small benchmark adapter and registry under `holoforge.core`. Each
registered benchmark should declare:

- a unique command identifier and short public description;
- the function that adds benchmark-specific arguments to a parser;
- a configuration builder with clear validation failures;
- one bounded verifier returning a common execution outcome;
- human-readable and JSON rendering routes;
- the model-card identifier, repository-relative path, and verified digest;
- the evidence-bundle scientific context; and
- optional artifact generation declared explicitly rather than inferred.

The registry should own discovery and dispatch for in-repository benchmarks.
The central CLI may create the top-level `verify` command and ask the registry
to populate it, but it must not contain benchmark-name conditionals after the
migration.

The adapter must not force heterogeneous equations into a common solver
signature. Model physics and numerical methods remain in the benchmark module;
the adapter standardizes command execution and evidence handoff only.

Dynamic third-party plugin discovery, package entry points, remote registries,
and arbitrary code loading are explicitly deferred. Version 0.5 first needs a
reviewed in-repository contract and a clear security boundary.

## Protected `0.5.x` compatibility surface

The following behavior should be protected from incompatible patch releases:

- existing CLI command names, defaults, options, and exit meanings;
- exit `0` for a passed verification, exit `1` for a completed but failed
  scientific acceptance gate, and exit `2` for invalid input or an execution
  setup failure;
- existing top-level keys and meanings in machine-readable verification,
  comparison, bundle-audit, and compatibility records;
- every schema version shipped by Version 0.5;
- integrity and scientific-payload digest semantics for evidence bundles; and
- the deliberately exported public objects documented in the Version 0.5
  Python API reference.

Internal solver helpers, undocumented module contents, formatting whitespace,
and newly additive record fields are not frozen. This is a `0.5.x` beta
guarantee, not the final Version 1.0 API promise.

## Schema, deprecation, support, and security policy

Version 0.5 should add public policies with these minimum rules:

- readers accept every schema version released within the supported `0.5.x`
  line;
- a schema change that invalidates a previously valid record requires a new
  schema version and an explicit migration note;
- automatic migration is allowed only when it is deterministic and preserves
  scientific meaning; otherwise the tool must fail with a reviewable message;
- deprecated CLI or Python surfaces remain functional for the rest of the
  `0.5.x` line and emit a documented warning before removal in a later minor or
  major release;
- the supported Python range and operating-system test scope are stated
  explicitly; and
- security or confidentiality reports have a private reporting route and must
  not be opened as public issues when they could expose credentials or
  unpublished work.

## Cross-platform verification

Keep the current full Ubuntu matrix for Python 3.9, 3.11, and 3.14. Add bounded
Python 3.11 smoke jobs on macOS and Windows that:

1. install the built wheel in a clean environment;
2. run the core contract, CLI, schema, evidence, and selected benchmark tests;
3. execute at least one registered verifier;
4. create an evidence bundle;
5. move the bundle to a different directory; and
6. pass its integrity audit after relocation.

Operating-system-specific numerical differences must be measured before a
tolerance is changed. A platform failure may not be hidden by silently
weakening a scientific gate.

## New-benchmark proof

The new benchmark is an acceptance test for the extension contract, not a
reason to enlarge Version 0.5 indefinitely. It must:

- come from identified public primary literature;
- use a bottom-up effective action or a clearly delimited universal
  gauge/gravity reference sector;
- introduce a distinct observable or numerical problem class;
- use maintained numerical-library functions when they fit the problem;
- declare action, dimensions, signs, coordinates, ensemble, sources,
  responses, UV conditions, and IR or horizon conditions;
- have an analytic or source-tabulated target plus convergence and residual
  evidence;
- finish within a practical CI budget; and
- enter through the registry without a new benchmark-specific core or CLI
  conditional.

The candidates and recommendation are recorded in
[`version-0.5-benchmark-shortlist.md`](version-0.5-benchmark-shortlist.md).
Selection requires owner review before the detailed scientific contract or
implementation begins.

## Implementation phases

### Phase A — infrastructure migration

- Freeze registry and adapter tests before refactoring.
- Register the three existing benchmarks.
- Remove benchmark-specific dispatch and model-card constants from the central
  CLI.
- Prove byte-for-byte or structured equality of existing JSON results and
  scientific-payload identities where runtime metadata is excluded.

The detailed owner-review contract is
[`version-0.5-phase-a-contract.md`](version-0.5-phase-a-contract.md).

### Phase B — policy and portability

- Publish compatibility, schema-migration, deprecation, support, and security
  policies.
- Document the protected Python API surface.
- Add the bounded macOS and Windows smoke jobs.
- Run a fresh-user and fresh-agent usability exercise from a built wheel.

### Phase C — selected benchmark

- Freeze a separate literature and numerical contract for the owner-selected
  candidate.
- Implement its module, adapter, model card, guide, tests, and optional
  artifacts.
- Confirm that no central dispatch or evidence special case was needed.

The selected benchmark has a merged, publicly reviewable implementation whose
scientific result and provenance were owner-approved on 2026-08-09.
Its equations, finite-frequency reconstruction, radial-flux audit, DC
extrapolation, refinements, machine record, and exact numerical results are
documented in the
[`linear-axion-dc` guide](benchmarks/linear-axion-dc.md). The model-card support
level remains `reproduced`; release approval does not broaden that claim.

Candidate A's detailed owner-review contract is
[`benchmarks/linear-axion-dc-contract.md`](benchmarks/linear-axion-dc-contract.md).

Each phase should be a separately reviewable logical change. Approval of this
specification does not automatically approve Phase C's scientific contract.

## Acceptance criteria

Version 0.5 is acceptable only if all of the following pass:

1. Registry identifiers are unique and deterministic.
2. Every existing verifier is reachable solely through the registry.
3. Existing CLI invocations, defaults, exit meanings, numerical results, and
   ordinary JSON semantics remain unchanged.
4. Existing evidence bundles retain their scientific-payload identity when
   deterministic scientific content is unchanged.
5. Missing or malformed adapter metadata fails closed with an actionable
   error.
6. Adding a synthetic test adapter requires no central CLI conditional.
7. The selected public benchmark also requires no central CLI or evidence
   special case.
8. The selected benchmark passes its separately reviewed analytic or external
   reference, convergence, residual, and invalid-input gates.
9. Supported `0.5.x` schemas and protected interface behavior have regression
   tests.
10. A moved evidence bundle passes on Linux, macOS, and Windows smoke jobs.
11. The complete existing suite and package build remain green.
12. The public-export preflight and manual review find no private path,
    candidate identifier, unpublished equation, result, or research history.

## Explicitly not included

- Dynamic third-party plugins or untrusted plugin loading.
- A remote model, artifact, or benchmark registry.
- A workflow engine, notebook service, database, or cloud execution layer.
- Automatic scientific approval, benchmark promotion, or model ranking.
- A private Explore candidate, result, source map, negative gate, or Git
  history.
- Reopening, identifying, or disclosing any private Explore project.
- Freezing all internal Python functions as the Version 1.0 API.
- A claim that a passing reference calculation validates nature.

## Stop conditions

Pause and return to owner review if:

- a common adapter requires benchmarks to share an unsuitable solver
  interface;
- migration changes an existing numerical result, default, exit meaning, or
  evidence digest;
- registry behavior depends on import order, hidden filesystem state, or
  unsafe dynamic loading;
- the selected benchmark lacks a source-supported normalization, boundary
  condition, or acceptance target;
- cross-platform differences cannot be separated from a scientific
  discrepancy;
- the new benchmark needs a one-off central interface rather than the approved
  extension contract; or
- any proposed public file exposes private or unpublished research.

## Owner decisions

### Decision 1 — milestone identity

**Recommendation: approve Version 0.5 as the stable-extension and
compatibility beta.**

- **Reason:** portable evidence exists, but a new benchmark still requires
  central CLI wiring and the protected pre-1.0 interfaces are undefined.
- **Opens:** treating the five objectives in this specification as the proposed
  Version 0.5 release contract.
- **Remains closed:** implementation, benchmark selection, commit, publication,
  and release.
- **Uncertainty:** the registry audit may reveal a smaller protected surface
  than currently anticipated.

### Decision 2 — extension boundary

**Recommendation: approve the in-repository registry and adapter while
deferring dynamic third-party plugins.**

- **Reason:** this removes current central special cases and tests modularity
  without adding arbitrary code discovery or an unreviewed security surface.
- **Opens:** a registry contract and migration plan for existing benchmarks.
- **Remains closed:** package entry-point discovery, remote registries, and
  third-party plugin compatibility claims.
- **Uncertainty:** optional artifact generation may need one narrowly typed
  capability in the adapter rather than a single uniform callback.

### Decision 3 — compatibility and portability scope

**Recommendation: approve the protected `0.5.x` surface, policy work, and
bounded cross-platform smoke jobs.**

- **Reason:** the project should state what patch releases preserve and verify
  that portable bundles are not Linux-only before approaching Version 1.0.
- **Opens:** policy drafts, compatibility tests, and Python 3.11 macOS/Windows
  smoke coverage in addition to the full Ubuntu Python matrix.
- **Remains closed:** a permanent Version 1.0 API freeze and an obligation to
  run every expensive numerical test on every operating system.
- **Uncertainty:** CI timing may require a documented small benchmark subset,
  but not weaker scientific tolerances.

### Decision 4 — benchmark candidate

**Recommendation: select Candidate A, the linear-axion DC-conductivity
benchmark.**

- **Reason:** it is an established bottom-up transport calculation with
  explicit sources, a horizon regularity problem, a conserved flux, and an
  analytic acceptance target.
- **Opens:** preparation of a separate detailed scientific contract for owner
  review.
- **Remains closed:** benchmark implementation and rejection of Candidates B
  or C as future reference benchmarks.
- **Uncertainty:** the contract must choose between a strict DC flux solve and
  a controlled small-frequency limit before any tolerance is set.

### Decision 5 — phased control and boundary

**Recommendation: approve the phases, acceptance criteria, stop conditions,
and strict public/private boundary.**

- **Reason:** separate infrastructure, policy, and scientific gates prevent a
  convenient refactor from silently changing benchmark meaning or exposing
  research material.
- **Opens:** preparation of the Phase A implementation plan and the selected
  benchmark's scientific contract after Decisions 1–4 are approved.
- **Remains closed:** code implementation, public commit, push, pull request,
  merge, tag, and release until separately authorized.
- **Uncertainty:** a stop condition may send one phase back to specification
  review without invalidating the rest of the milestone.

## Owner response recorded

Xin-Yi Liu approved Decisions 1–5 on 2026-08-06. Version 0.5 is therefore
defined as the stable-extension and compatibility beta; the in-repository
registry boundary, protected `0.5.x` surface, policy and portability scope,
phased controls, acceptance criteria, stop conditions, and public/private
boundary are accepted. Candidate A, the linear-axion DC-conductivity
benchmark, is selected only for preparation of a separate scientific
contract. No registry refactor, benchmark implementation, commit, push, pull
request, merge, tag, release, private transfer, or research disclosure is
authorized by this approval record.

## Subsequent implementation and release record

After the specification approval above, Xin-Yi Liu separately approved the
Phase A registry migration, the selected benchmark's frozen scientific
contract and reproduced support state, its implementation and provenance, the
public commits and pull request, merge, and the `v0.5.0` release on
2026-08-09. Version 0.5 also publishes the bounded
[compatibility and support policy](version-0.5-compatibility-policy.md) and
tests built-wheel portability on Ubuntu, macOS, and Windows. The historical
decision boundaries above are retained to show that scientific approval did
not silently authorize publication.
