# Quadratic Soft-Wall Vector Benchmark

## Scientific source

The benchmark follows A. Karch, E. Katz, D. T. Son, and M. A. Stephanov,
“Linear Confinement and AdS/QCD,” *Physical Review D* **74**, 015005 (2006),
[arXiv:hep-ph/0602229](https://arxiv.org/abs/hep-ph/0602229), especially
Eqs. (8)–(15).

## Conventions and derivation

Use the conformally flat five-dimensional metric

```text
ds^2 = exp(2 A(z)) (dz^2 + eta_{mu nu} dx^mu dx^nu),
A(z) = -log(z/R),
Phi(z) = kappa^2 z^2,
B(z) = Phi(z) - A(z).
```

For a transverse vector mode, the field redefinition
`v_n = exp(B/2) psi_n` turns the Sturm–Liouville equation into

```text
-psi_n''(z) + V(z) psi_n(z) = m_n^2 psi_n(z),
V(z) = B'(z)^2 / 4 - B''(z) / 2
     = kappa^4 z^2 + 3 / (4 z^2).
```

Normalizability gives the exact spectrum

```text
m_n^2 = 4 kappa^2 (n + 1),  n = 0, 1, 2, ... .
```

Natural units are used. In the implementation, `kappa` is measured in GeV,
`z` in GeV^-1, and eigenvalues in GeV^2. The AdS radius cancels from this mode
equation.

## Numerical method

The implementation truncates the half-line to `0 < z < z_max`, imposes
Dirichlet conditions on the Schrödinger wavefunction at both ends, and uses a
second-order centered finite difference on a uniform interior grid. Only the
lowest requested eigenvalues of the symmetric tridiagonal Hamiltonian are
computed with SciPy's eigenvalue-only `eigvalsh_tridiagonal` routine. This
retains linear storage and avoids constructing a dense matrix or computing
unused eigenvectors.

The UV potential is never evaluated at `z = 0`; the first point is one grid
spacing inside the domain. The default `z_max = 10 / kappa` suppresses the
normalizable wavefunctions well before the artificial IR boundary for the first
few modes.

## Verification and limits

The default verification requires the first four eigenvalues to agree with the
analytic result within a maximum relative error of `2e-4`. Tests also require
the error to decrease with the approximately second-order rate expected from
the centered stencil. Machine-readable output records the complete numerical
configuration, method, boundary conditions, and Python/NumPy/SciPy versions.

This checks the equation, scale restoration, discretization, and eigenvalue
ordering. It does **not** test decay constants, experimental fits, chiral
physics, backreaction, or the phenomenological adequacy of the soft-wall model.
