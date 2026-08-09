# Version 0.5 Public Benchmark Shortlist

**Status:** Candidate A selected by Xin-Yi Liu on 2026-08-06 for preparation
of a separate scientific contract. No scientific implementation is authorized
by this document.

## Screening rule

The Version 0.5 benchmark must test the proposed extension contract while
remaining a bounded Forge/Verify reproduction. The screen therefore requires:

- public primary literature with identifiable equations or numerical values;
- no dependence on private HoloForge research;
- a bottom-up effective action or a clearly delimited universal
  gauge/gravity reference sector;
- a numerical or observable class not already represented adequately;
- explicit sources, responses, ensemble, normalization, and boundary
  conditions;
- a source-supported acceptance target and at least one independent numerical
  check; and
- a practical CI runtime using maintained NumPy/SciPy functionality.

Novelty is not a selection criterion. This benchmark should verify software
and a published calculation; it should not become a new research project.

## Comparative shortlist

| Candidate | New capability | Cost | Main strength | Main risk | Recommendation |
| --- | --- | --- | --- | --- | --- |
| A. Linear-axion DC conductivity | Coupled transport, explicit translation-breaking sources, radially conserved flux | Medium | Strongest test of registry, source/response metadata, horizon regularity, and a numerical-to-analytic gate | Zero-frequency normalization and coupled constraint handling must be frozen carefully | **First choice** |
| B. AdS black-brane shear QNM | Complex eigenfrequency, ingoing horizon condition, hydrodynamic dispersion | High | Strong test of complex root finding, mode tracking, and QNM acceptance evidence | Greater numerical fragility and a less specifically bottom-up scientific identity | Second choice |
| C. Holographic strip entanglement entropy | Singular quadrature, turning-point solve, UV subtraction, nonlocal observable | Low to medium | Broadens HoloForge beyond spectra and local transport with exact analytic checks | Weaker stress test of the command adapter and no dynamical boundary-value problem | Fallback |

## Candidate A — linear-axion DC conductivity

### Public source

T. Andrade and B. Withers, “A simple holographic model of momentum
relaxation,” [arXiv:1311.5157v2](https://arxiv.org/abs/1311.5157), especially
Eqs. (2.1)–(2.9) and (3.2)–(3.21).

### Frozen candidate identity

Use the four-dimensional bulk case (`d = 3` in the source) of the bottom-up
Einstein-Maxwell model with two massless scalar fields:

```text
S = integral sqrt(-g) [R - 2 Lambda
    - (1/2) sum_I (partial psi_I)^2 - (1/4) F^2].
```

The scalar sources are linear in boundary position and arranged isotropically,
`psi_I = alpha delta_Ia x^a`. They explicitly relax boundary momentum while
leaving the bulk background homogeneous. The chemical potential `mu` is a
nonzero gauge-field source. These are physical sources and must not be
described as source-free boundary conditions.

For `d = 3`, the source's analytic result becomes

```text
sigma_DC = 1 + mu^2 / alpha^2.
```

### Proposed numerical proof

Do more than evaluate the closed formula. Construct the analytic charged black
brane, solve the source-normalized zero-frequency or controlled small-frequency
transport system with ingoing horizon regularity, and extract the boundary
current. Compare that numerical result with the radially conserved horizon
flux and Eq. (3.21).

The detailed contract should require:

- the background horizon condition and positive-temperature domain;
- nonzero `mu` and translation-breaking scalar sources `alpha`;
- unit boundary electric-field source and vanishing unwanted operator source;
- a radial-flux conservation residual;
- at least three parameter points away from `alpha = 0`;
- cutoff and solver-tolerance refinement;
- numerical agreement with `1 + mu^2/alpha^2`; and
- a clear statement that finite model DC conductivity is not empirical
  validation of a real material.

### Assessment

This is the recommended candidate. It is explicitly bottom-up, introduces
transport and momentum relaxation, uses nontrivial source/response data, and
has an analytic horizon formula suitable for a hard acceptance gate. It is
complex enough to prove the extension contract without requiring a new
research program.

The main uncertainty is whether the cleanest numerical route should use the
strict DC conserved-flux system or a small-frequency optical-conductivity
limit. That choice must be resolved in the separate scientific contract before
implementation.

## Candidate B — AdS black-brane shear quasinormal mode

### Public source

P. K. Kovtun and A. O. Starinets, “Quasinormal modes and holography,”
[arXiv:hep-th/0506184v2](https://arxiv.org/abs/hep-th/0506184), especially the
gauge-invariant shear-channel discussion around Eqs. (4.30)–(4.33) and the
tabulated `q = 1` spectrum.

### Frozen candidate identity

Use the gauge-invariant shear perturbation of the planar AdS black brane with:

- ingoing behavior at the future horizon;
- a vanishing boundary source for a quasinormal mode; and
- the source's dimensionless frequency and momentum conventions.

The hydrodynamic target is

```text
w = -i q^2 / 2 + higher-order terms,
```

and the source also reports a finite-momentum shear value at `q = 1` that can
serve as a separate regression target after conventions are checked.

### Proposed numerical proof

Use maintained complex ODE integration and root finding, with a second
formulation or determinant normalization check. Require a small-momentum
sequence that recovers the diffusion coefficient, negative imaginary parts for
accepted modes, cutoff and tolerance refinement, and a source-residual gate.

### Assessment

This candidate offers the strongest test of complex spectral infrastructure
and would prepare HoloForge for later QNM benchmarks. It is ranked second
because complex root enumeration, spurious roots, branch tracking, and an
independent solver make it materially more expensive. The source's setting is
a universal Einstein-gravity reference calculation embedded in a specific
AdS/CFT example, not a new phenomenological bottom-up application; that scope
would need to remain explicit.

## Candidate C — holographic strip entanglement entropy

### Public source

S. Ryu and T. Takayanagi, “Holographic Derivation of Entanglement Entropy from
AdS/CFT,” [arXiv:hep-th/0603001v2](https://arxiv.org/abs/hep-th/0603001),
especially Eqs. (3.2) and (4.1)–(4.3).

### Frozen candidate identity

Use the codimension-two minimal surface for a straight boundary strip. The
pure-AdS width and finite-area terms provide gamma-function references. The
finite-temperature AdS black-brane calculation provides a turning-point
integral and a large-width thermal-entropy limit.

### Proposed numerical proof

Use SciPy quadrature and root finding with an explicit endpoint
regularization. Require agreement with the pure-AdS analytic width relation,
cutoff-independent convergence of the subtracted finite term, and recovery of
the finite-temperature large-width entropy-density coefficient.

### Assessment

This is the least expensive candidate and cleanly introduces a nonlocal
observable, singular quadrature, UV subtraction, and turning-point inversion.
It is the fallback if Candidate A's transport normalization cannot be frozen
without broadening scope. It is a weaker proof of benchmark dispatch and
boundary-value extensibility, and it is a general AdS/CFT reference sector
rather than a phenomenological bottom-up matter model.

## Recommendation and decision boundary

Select **Candidate A, the linear-axion DC-conductivity benchmark**, subject to
a separate owner-reviewed scientific contract. It best balances bottom-up
identity, architectural coverage, public-source clarity, falsifiable numerical
checks, and CI cost.

Selecting Candidate A would authorize only preparation of its detailed
contract. It would not yet authorize implementation, tolerance selection after
viewing results, publication, private-research transfer, or claims about real
materials. Candidates B and C should remain documented alternatives rather
than being silently discarded.

## Owner decision

Choose one of the following:

1. **Candidate A — recommended:** freeze a linear-axion DC-conductivity
   scientific contract next.
2. Candidate B: freeze a shear-QNM scientific contract next and accept the
   higher numerical cost.
3. Candidate C: freeze a strip-entanglement scientific contract next as the
   lowest-cost route.
4. Select none and revise the shortlist before implementation.

Xin-Yi Liu selected Candidate A on 2026-08-06. This records the benchmark
direction and authorizes only preparation of its detailed contract. Candidates
B and C remain documented alternatives. Implementation, tolerance changes,
commit, publication, and release remain closed pending later review.
