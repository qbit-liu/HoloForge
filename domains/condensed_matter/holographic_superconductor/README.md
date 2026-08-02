# Minimal holographic superconductor

This Forge/Verify domain entry reproduces the probe-limit Abelian-Higgs model
of Hartnoll, Herzog, and Horowitz (arXiv:0803.3295v1) in the `Delta = 2`
quantization.

It contains two linked checks:

1. the linear normal-phase instability and critical temperature;
2. the nonlinear condensate branch corresponding to Figure 1's right panel.

The chemical potential is a nonzero boundary gauge-field source. Only the
scalar source is set to zero. See
[`docs/benchmarks/holographic-superconductor.md`](../../../docs/benchmarks/holographic-superconductor.md)
for equations, normalization, numerical methods, and limitations.

The scientific conventions and reproduced output were approved by Xin-Yi Liu
on 2026-08-02.
