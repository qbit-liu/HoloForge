# Gubser--Rocha top-down-derived EMD control

This Forge/Verify control entry targets the homogeneous equal-charge charged
dilatonic black brane of Gubser and Rocha
([arXiv:0911.2898v2](https://arxiv.org/abs/0911.2898v2)). It uses a coupled
Chebyshev solve and the source closed-form family as an independent reference.
The five-dimensional model is a consistent truncation of maximal gauged
supergravity with a type IIB lift. It is therefore a classical top-down-derived
reference for HoloForge's numerical infrastructure, not one of the project's
representative bottom-up examples.

The benchmark reproduces the bosonic background and source Eqs. (2)--(6). The
paper's only figure belongs to its separate charged-fermion analysis; the
current program does not solve that Dirac system or reproduce source Figure 1.

The owner approved the scientific and numerical contract on 2026-08-19. The
implementation and numerical preflight remain unreviewed. In particular, the
larger unequal-charge theory is unstable for `xi > 1`; those cases are retained
only as exact verification points and are not stable phase claims.

See
[`docs/benchmarks/gubser-rocha-emd.md`](../../../docs/benchmarks/gubser-rocha-emd.md)
for equations, acceptance gates, current preflight evidence, and limitations.
