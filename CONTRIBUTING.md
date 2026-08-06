# Contributing to HoloForge

HoloForge welcomes reproducible software, documentation, benchmarks, and
carefully scoped research hypotheses. Contributions must follow the
[Scientific Constitution](CONSTITUTION.md).

## Development setup

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[test]"
python -m unittest discover -s tests -v
holoforge verify soft-wall-vector
```

Contributors using Codex, Claude Code, or another coding agent should first
follow the [agent quick-start guide](docs/agent-quickstart.md). The canonical
repository context is `AGENTS.md`; `CLAUDE.md` imports the same instructions so
the scientific and privacy rules are not duplicated across agent products.

## Choose the correct workflow

### Forge/Verify

A mature benchmark belongs in `domains/`. Open a Forge/Verify benchmark issue
before substantial implementation. The proposal must identify:

- public primary sources and the equations being reproduced;
- action, dimensions, signs, normalizations, coordinates, and units;
- UV, IR, or horizon boundary conditions and the physical ensemble;
- inputs, observables, numerical method, and failure criteria;
- analytic, convergence, residual, regression, or external-data checks;
- limitations of what a passing calculation establishes.

Add or update a valid model card and automated tests with the implementation.
Contributors using an agent may invoke `$holoforge-add-benchmark` from the
repository-scoped skills for this workflow.

### Explore

A speculative cross-domain application begins with a hypothesis card. It must
state the candidate dictionary, prior-work screen, calculable observable, and a
result that would falsify the idea. AI involvement must be recorded. Explore
work cannot be labelled established because code executes.

Before screening, classify it as a new-domain application, a new-subfield or
new-phenomenon application within a holographically studied parent field, or a
method-transfer/model-improvement project. Follow the bounded
[research-gate workflow](docs/research-gate-workflow.md); freeze each contract
before calculation and keep scientific support, owner authorization, and
disclosure status separate. Every owner decision list must include an explicit
item-by-item recommendation and a concise evidence-based reason.

If the idea is novel, potentially publishable, or otherwise not cleared for
public release, develop it in a separate private repository by following the
[private Explore workflow](docs/private-research-workflow.md). The public
`incubator/` accepts only synthetic examples, public-literature dry runs, or
material whose owner has explicitly approved disclosure.
Contributors using an agent may invoke `$holoforge-research-gate` for a bounded
gate and `$holoforge-public-export` for any proposed private-to-public
promotion. Automated scanning supplements rather than replaces human privacy,
provenance, licensing, and scientific review.

## Pull requests

Keep each pull request narrow. Explain why the change is needed, distinguish
scientific changes from software refactoring, and list the exact verification
performed. Changes to scientific results require updated documentation and
tests. Do not submit secrets, private filesystem paths, or unpublished research
material. A pull request that exports formerly private work must identify the
public source or publication and confirm the research owner's explicit release
approval without copying confidential review or working notes.

By contributing, you agree that your contribution is licensed under the
project's [BSD 3-Clause License](LICENSE).
