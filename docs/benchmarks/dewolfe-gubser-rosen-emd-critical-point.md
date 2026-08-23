# DeWolfe--Gubser--Rosen finite-density EMD guide

## What this example verifies

This owner-approved Forge/Verify example solves selected backgrounds of the
phenomenological bottom-up Einstein--Maxwell--dilaton model in
[arXiv:1012.1864v2](https://arxiv.org/abs/1012.1864). It reproduces the
reported critical-coordinate neighborhood, not a complete phase diagram:

```text
source:    (T_c, mu_c) = (143 MeV, 783 MeV)
HoloForge: (T_c, mu_c) = (142.973974 MeV, 781.693762 MeV)
```

The primary Chebyshev formulation uses conserved electric flux. A second
Chebyshev formulation solves the geometry, scalar, and Maxwell potential
together. Both routes evaluate the physical equations, Einstein constraint,
boundary conditions, Gauss flux, and Noether charge independently.

## Run it

```bash
holoforge verify dewolfe-gubser-rosen-emd-finite-density
holoforge verify dewolfe-gubser-rosen-emd-finite-density --json
holoforge verify dewolfe-gubser-rosen-emd-finite-density \
  --output-dir OUTPUT_DIR
```

The output directory contains strict JSON, a twelve-row selected-state CSV,
and a HoloForge-generated verification plot. Existing files are never
overwritten.

## Equations and conventions

In the inward conformal coordinate, the primary background equations are

```text
A'' - A'^2 + phi'^2/6 = 0,
h'' + 3 A' h' - exp(-2A) f_EMD Phi'^2 = 0,
h phi'' + (3 A' h + h') phi'
  - exp(2A) V_phi + exp(-2A) f_EMD,phi Phi'^2/2 = 0,
q = -f_EMD exp(A) Phi'.
```

The gauge field is regular at the horizon and its boundary value defines the
grand-canonical chemical potential. Positive charge has `Phi'<0` in this
coordinate, and the canonical density is `rho_canonical_BH=q/2`. The
simultaneous-Maxwell route uses `Phi=mu-u^(2/nu)e(u)` and collocates Maxwell's
equation rather than treating it only as a diagnostic.

The located state is refined through `N=80,120,150`, and representative
neutral, charged, and high-charge controls are solved at `N=80`. See the
[current Phase 5B contract](dewolfe-gubser-rosen-emd-phase-5b-contract.md) for
the frozen tolerances and scope boundary.

## Figure 5 and interpretation limits

The paper's Figure 5 abscissa is retained as `mu_BH`, but its digitized
ordinate is explicitly named `rho_source_figure5`. No verified public source
maps it to `rho_canonical_BH`. The artwork anchors are therefore provenance
only: neither absolute ordinate agreement nor global Figure 5 topology can
affect the seven reduced-core gates.

This is a reproduction inside a phenomenological model. It is not empirical
validation of a QCD critical point, and it does not compute an equal-free-
energy coexistence line or critical exponents. The longer historical guide
and stopped topology campaign are preserved in the
[full Phase 5B guide](history/dewolfe-gubser-rosen-emd-finite-density-full-guide.md).
