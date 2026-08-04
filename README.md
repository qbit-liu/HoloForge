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

Version 0.1 starts with the quadratic soft-wall vector-meson spectrum. This is
a useful first benchmark because the numerical eigenvalue problem can be
checked against the exact result
`m_n^2 = 4 kappa^2 (n + 1)`.

Version 0.2 adds a second, structurally different benchmark: the linear
instability and nonlinear dimension-two condensate of the minimal probe-limit
holographic superconductor.

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
holoforge verify soft-wall-vector
python3 -m unittest discover -s tests -v
```

Conda users may replace the first two commands with
`conda create -n holoforge python=3.11` followed by
`conda activate holoforge`.

To change the soft-wall scale or emit machine-readable output:

```bash
holoforge verify soft-wall-vector --kappa 0.388 --json
```

Run the holographic-superconductor verifier and regenerate the dimension-two
condensate curve with:

```bash
holoforge verify holographic-superconductor
holoforge verify holographic-superconductor \
  --plot artifacts/holographic-superconductor-delta2.png
```

The checked development output is shown in the
[`Delta = 2` benchmark guide](docs/benchmarks/holographic-superconductor.md).

For benchmark use without schema-test dependencies, install with
`python3 -m pip install -e .`. Until the package is installed, the command can
also be run from the checkout with `PYTHONPATH=src python3 -m holoforge ...`.


## Repository map

- [`CONSTITUTION.md`](CONSTITUTION.md) defines the scientific rules of the
  project.
- [`docs/version-0.1.md`](docs/version-0.1.md),
  [`docs/version-0.1.1.md`](docs/version-0.1.1.md), and
  [`docs/version-0.2.md`](docs/version-0.2.md) define the scientific release
  contracts; [`docs/version-0.2.1.md`](docs/version-0.2.1.md) defines the
  privacy-workflow patch, and [`docs/version-0.2.2.md`](docs/version-0.2.2.md)
  defines the reusable gate-workflow patch.
- [`CONTRIBUTING.md`](CONTRIBUTING.md) explains the scientific and software
  contribution workflow.
- [`CITATION.cff`](CITATION.cff) provides machine-readable citation metadata.
- [`CHANGELOG.md`](CHANGELOG.md) records release-level changes.
- [`schemas/`](schemas/) contains machine-readable model-card and
  hypothesis-card contracts.
- [`domains/`](domains/) contains literature-anchored, testable models.
- [`incubator/`](incubator/) contains only public-safe Explore examples and
  proposals.
- [`src/holoforge/`](src/holoforge/) contains reusable software.
- [`tests/`](tests/) holds analytic, numerical, schema, and interface checks.

## Project status

This is an early scientific release (`0.2.2`), not a precision-QCD or
materials-prediction package. Its benchmarks reproduce published model
calculations; they do not establish those models as complete descriptions of
QCD or real materials.

## License

HoloForge is released under the
[BSD 3-Clause License](LICENSE), copyright 2026 Xin-Yi Liu.
