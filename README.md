# HoloForge

[![CI](https://github.com/qbit-liu/HoloForge/actions/workflows/ci.yml/badge.svg)](https://github.com/qbit-liu/HoloForge/actions/workflows/ci.yml)

HoloForge is a verification-first platform for **bottom-up gauge/gravity
modelling**. It is intended to make scientific assumptions, conventions,
equations, numerical choices, validation evidence, and limitations inspectable
alongside executable calculations.

HoloForge has two deliberately separated modes:

- **Forge/Verify** reproduces established models and checks their analytic and
  numerical consequences.
- **Explore** records new cross-domain ideas as falsifiable hypotheses without
  presenting them as established physics.

Explore recognizes three useful research tracks: applications to a genuinely
new parent domain, applications to an unexplored subfield or phenomenon inside
an already holographic parent field, and method transfer or model improvement.
See the [research-gate workflow](docs/research-gate-workflow.md).

## Framework scope

HoloForge is not organized around one physical domain, model family, or
observable. Its reusable contract is the chain from assumptions and sources
to equations, boundary conditions, numerical evidence, observables, and
explicit limitations.

The current public release contains a deliberately small reference suite,
chosen because its calculations have analytic or literature checks suitable
for testing that contract. These examples demonstrate the framework; they do
not define HoloForge's scientific scope or priority. Technical model details
belong in the linked benchmark guides and version specifications.

## Release maturity and research use

A pre-1.0 HoloForge release can be used for a bounded calculation when that
calculation's equations, conventions, solver, acceptance gates, and exact
package version or Git commit are recorded and independently checked. The
`0.x` version number means the public interfaces may still change; it does not
make a passing benchmark scientifically untrustworthy.

Private research should combine a pinned HoloForge release with
project-specific equations, code, and validation in a separate repository.
HoloForge 1.0 will denote a stable public framework contract, not the first
version capable of supporting any scientific research.

## Privacy for Explore research

HoloForge does **not** require novel work to be public while it is in progress.
Potentially publishable Explore projects should use HoloForge from a separate,
access-controlled repository. The public `incubator/` is reserved for synthetic
examples, public-literature dry runs, and work explicitly approved for
disclosure. After journal acceptance or another deliberate release decision, a
reviewed reproducibility package may be promoted into this repository. See the
[private-research workflow](docs/private-research-workflow.md).

## Quick start

HoloForge currently requires Python 3.9 or newer, NumPy, and SciPy.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python3 -m pip install -e ".[test]"
holoforge --help
python3 -m unittest discover -s tests -v
```

Conda users may replace the first two commands with
`conda create -n holoforge python=3.11` followed by
`conda activate holoforge`.

For benchmark use without schema-test dependencies, install with
`python3 -m pip install -e .`. Until the package is installed, the command can
also be run from the checkout with `PYTHONPATH=src python3 -m holoforge ...`.

## Start with an AI coding agent

Open the cloned HoloForge folder as the agent's workspace so it can see the
repository instructions, documentation, and scoped workflows. Begin with the
[agent quick-start guide](docs/agent-quickstart.md), which provides setup
commands, an inspect-only first prompt, task-specific prompts, private Explore
guidance, and a checklist for reviewing agent-generated changes.

- `AGENTS.md` is the canonical cross-agent project context and is read by
  Codex.
- `CLAUDE.md` imports that same context for Claude Code.
- Agents without automatic project-instruction or skill discovery should be
  asked explicitly to read `AGENTS.md` and the matching workflow under
  `.agents/skills/`.

An agent can help execute a workflow, but it does not replace the benchmark
acceptance gates, scientific review, or explicit authorization to disclose
private research.

## Included reference implementations

The following are the reference calculations implemented today. Their names
identify executable examples, not a restriction on future HoloForge domains.

| Capability demonstrated | Command | Documentation |
| --- | --- | --- |
| Spectral eigenvalue verification with analytic and independent numerical checks | `holoforge verify soft-wall-vector` and `holoforge verify hard-wall-vector` | [soft-wall guide](docs/benchmarks/soft-wall-vector.md) and [hard-wall guide](docs/benchmarks/hard-wall-vector.md) |
| Linear-instability and nonlinear-condensate verification | `holoforge verify holographic-superconductor` | [condensate benchmark guide](docs/benchmarks/holographic-superconductor.md) |
| Controlled model/reference comparison with uncertainty provenance | `holoforge compare vector-spectrum` | [comparison guide](docs/benchmarks/vector-spectrum-comparison.md) |

Commands accept documented options for machine-readable records and generated
artifacts. Plot generation requires the optional dependency installed with
`python3 -m pip install -e ".[plot]"`.

## Repository map

- [`CONSTITUTION.md`](CONSTITUTION.md) defines the scientific rules of the
  project.
- [`docs/version-*.md`](docs/) contains the scientific and infrastructure
  contracts for each public release.
- [`CONTRIBUTING.md`](CONTRIBUTING.md) explains the scientific and software
  contribution workflow.
- [`docs/agent-quickstart.md`](docs/agent-quickstart.md) explains how a new
  user starts HoloForge safely with Codex, Claude Code, or another agent.
- [`CITATION.cff`](CITATION.cff) provides machine-readable citation metadata.
- [`CHANGELOG.md`](CHANGELOG.md) records release-level changes.
- [`schemas/`](schemas/) contains machine-readable model-card and
  hypothesis-card, reference-data, prediction, and comparison contracts.
- [`domains/`](domains/) contains literature-anchored, testable models.
- [`incubator/`](incubator/) contains only public-safe Explore examples and
  proposals.
- [`.agents/skills/`](.agents/skills/) contains repository-scoped reusable
  workflows for research gates, benchmark development, and privacy-reviewed
  public exports. Supported agents may discover these skills automatically;
  every agent can instead read the matching `SKILL.md` directly.
- [`src/holoforge/`](src/holoforge/) contains reusable software.
- [`tests/`](tests/) holds analytic, numerical, schema, and interface checks.

## Reusable agent skills

The checked-in skills package procedures that are specific to HoloForge:

- `$holoforge-research-gate` runs one frozen Explore gate through evidence,
  criticism, recommendations, owner review, and decision recording;
- `$holoforge-public-export` audits a proposed private-to-public artifact and
  includes a deterministic scanner for common private-path and forbidden-token
  leaks; and
- `$holoforge-add-benchmark` guides a literature-anchored Forge/Verify
  benchmark from contract through implementation and validation.

These skills do not contain unpublished candidate identities, scientific
results, private numerical implementations, or personal global preferences.
They are repository workflows, not substitutes for scientific review.

## Project status

This is an early scientific release (`0.3.0`), not a universal phenomenology
or first-principles prediction package. Its current reference implementations
reproduce published model calculations; they do not establish those models as
complete descriptions of their target physical systems.

## License

HoloForge is released under the
[BSD 3-Clause License](LICENSE), copyright 2026 Xin-Yi Liu.
