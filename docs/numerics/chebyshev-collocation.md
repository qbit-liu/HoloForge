# Chebyshev Collocation Numerical Primitive

HoloForge provides a small shared Chebyshev--Gauss--Lobatto grid utility for
smooth finite-interval problems. It is numerical infrastructure, not a
universal holographic solver: every benchmark remains responsible for its own
equations, boundary conditions, gauge or constraint treatment, mode filtering,
and scientific acceptance gates.

## Definition and convention

The implementation follows the standard dense differentiation-matrix
construction described in L. N. Trefethen, *Spectral Methods in MATLAB*,
Chapter 6. For polynomial degree `N`, it returns `N + 1` Lobatto nodes,
including both endpoints. HoloForge orders the nodes from the lower to the upper
physical bound so UV/IR and boundary/horizon rows are not implicit.

The returned first- and second-derivative matrices are read-only. A benchmark
that imposes boundary conditions by row replacement must copy the operator and
state the physical role of each replacement in its own contract.

## Verification

`tests/test_chebyshev.py` checks:

- interval mapping and node ordering;
- exact first and second derivatives of resolved polynomials;
- the derivative of a constant;
- immutable returned arrays; and
- clear failures for invalid degrees and intervals.

The soft-wall and hard-wall vector benchmarks add model-level tests against
their exact spectra, three polynomial degrees, and independent existing
solvers. Passing these checks verifies the implemented collocation problems; it
does not establish that one numerical method is preferable for every model.

## Limitations

The matrices are dense and intended for modest one-dimensional benchmark
resolutions. Singular endpoints must be regularized or excluded by the calling
benchmark. Coupled constrained systems require explicit rank, residual, and
spurious-mode checks beyond this utility.
