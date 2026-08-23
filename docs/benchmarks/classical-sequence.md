# Classical benchmark sequence

This page is the current index for the six-phase Forge/Verify program. It
separates the result that was actually reproduced from attractive but
unverified extensions. A passing calculation verifies the declared model
contract; it is not empirical validation of nature.

| Phase | Benchmark and command | Quantitative literature target | Current result and strongest boundary | Delivery state |
| ---: | --- | --- | --- | --- |
| 0 | Spectral foundation: `holoforge verify soft-wall-vector`; `holoforge verify hard-wall-vector --method spectral` | Quadratic soft-wall analytic spectrum and hard-wall Bessel zeros | Spectral primitives agree with analytic targets; the hard-wall spectral route is the canonical sequence path | complete; included in Version 0.5.3 sequence closure |
| 1 | Gubser--Nellore ED: `holoforge verify gubser-nellore-ed` | Source Figures 2 and 3 thermodynamics | Fourteen spectral/ODE/source-figure gates pass; this is a phenomenological ED calibration, not empirical QCD validation | released in Version 0.5.3 |
| 2 | Gubser--Rocha EMD: `holoforge verify gubser-rocha-emd` | Exact charged background, thermodynamics, and low-temperature linear entropy | Exact solution controls the coupled Chebyshev BVP; the model is top-down-derived and retained as a numerical control, not a representative bottom-up example | released in Version 0.5.3 |
| 3 | Hard-wall chiral QCD: `holoforge verify hard-wall-chiral` | GMOR and the seven Model A entries of source Table II | Chebyshev eigenvalue/BVP result passes the table and independent-route gates; no Model B fit or broader QCD claim | released in Version 0.5.4 |
| 4 | HHH optical response: `holoforge verify holographic-superconductor-optical` | Exact normal response, protected Figure 1 condensate, and near-critical `C_2=24` | `C_2=23.96884334975214`; source Figure 2 is explicitly not reproduced and has no gate | released in Version 0.5.5 |
| 5A | DGR EMD at zero density: `holoforge verify dewolfe-gubser-rosen-emd` | Both source Figure 3 curves | Fourteen spectral, DOP853, source-figure, and reproducibility gates pass; finite density is separate | released in Version 0.5.6 |
| 5B | DGR EMD at finite density: `holoforge verify dewolfe-gubser-rosen-emd-finite-density` | Reported critical neighborhood `(143,783) MeV` | `(142.973974,781.693762) MeV`; seven reduced-core gates pass, while Figure 5 absolute ordinate/topology and Phase 5C remain closed | merged to `main`; no separate release required for sequence closure |

## Program boundary

The classical-example program is complete through the owner-approved reduced
Phase 5B result. Phase 5C critical scaling and the historical dense Figure 5
topology campaign are optional future extensions, not unfinished work in this
sequence. The active Phase 4 and 5B contracts deliberately summarize only
current requirements; their complete development histories remain preserved
under [`docs/benchmarks/history`](history/).
