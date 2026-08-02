# HoloForge Scientific Constitution

## 1. Purpose and scope

HoloForge is a bottom-up gauge/gravity research platform. Its purpose is to turn
models into inspectable chains from assumptions to equations, boundary
conditions, numerics, observables, and validation evidence. It is not restricted
to holographic QCD, but it does not claim a top-down string embedding unless one
is explicitly supplied and supported.

## 2. Two modes, one evidence standard

**Forge/Verify** reproduces and extends literature-anchored models. Every model
must state its source, conventions, parameters, equations, boundary conditions,
observables, validation tests, and known limitations.

**Explore** develops cross-domain analogies and candidate applications. Explore
work uses a hypothesis card, gives a falsification test, and cannot be presented
as established merely because code runs or an AI system proposed it. Novel,
unpublished Explore work may remain in a separate private workspace; Explore is
an evidence category, not a requirement to disclose research in progress.

## 3. Claim labels

Every consequential physical claim must carry one of these support levels:

1. `established-source` — directly supported by an identified primary source.
2. `reproduced` — independently recovered by a declared calculation or test.
3. `model-extension` — new within a stated model, but not independently
   established outside it.
4. `hypothesis` — speculative and awaiting a discriminating test.

AI authorship and scientific support are separate facts. AI-generated claims
must be marked as such and remain `unreviewed` until a human checks them.

## 4. Verification contract

A passing result requires more than successful execution. Each benchmark must
declare:

- units, signs, normalizations, coordinates, and boundary conditions;
- numerical domain, resolution, algorithm, tolerances, and software versions;
- at least one analytic, convergence, regression, or external-data check;
- failure criteria and limitations of what the check establishes.

Plots without underlying numerical checks are illustrations, not validation.

## 5. Separation and promotion

Mature, literature-anchored public work lives in `domains/`. The public
`incubator/` contains only synthetic examples, public-literature dry runs, or
speculative work whose owner has explicitly approved disclosure. Novel
research-in-progress should live in a separate private repository. Promotion to
`domains/` requires an identified source or derivation, a stable model card,
executable tests, documented failure modes, and human review. File location is
part of the scientific status and must not be changed merely for presentation.

## 6. Confidentiality and publication timing

HoloForge does not require researchers to open unpublished projects. By
default, novel Explore work may remain private until journal acceptance or
another explicit disclosure decision by its owner. Before any private work is
copied into this public repository, a human must approve the exact export and
check that it contains no secrets, private paths, restricted data, confidential
notes, or results that are not cleared for release. An ignored local directory
is not a confidentiality boundary; a separate access-controlled repository is
preferred.

## 7. Reproducibility and provenance

Inputs and defaults must be serializable; generated outputs must record the
configuration that produced them. Changes that alter scientific results require
updated tests and documentation. Negative results and failed hypotheses should
be retained when they provide useful provenance.

## 8. Scientific restraint

HoloForge distinguishes verification of an implementation, reproduction of a
model result, and empirical validation of nature. Passing one level never
silently implies the next. Known ambiguities and disagreements are part of the
model record, not defects to hide.

Adopted by Xin-Yi Liu on 2026-08-02.
