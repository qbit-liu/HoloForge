# HoloForge research-acceleration plan — Version 3

## Purpose

HoloForge should increase the rate at which a researcher reaches a defensible
physical claim without weakening verification, privacy, provenance, or human
scientific authority. It cannot promise publication, and benchmark, test,
pull-request, report, and release counts are not research-output metrics.

This plan replaces an infrastructure-first sequence with a research-pulled
sequence. It preserves the existing Forge/Verify and Explore boundary and does
not authorize disclosure of any private project.

The original first-pilot proposal favored an already qualified route. Owner
review on 2026-08-29 clarified that this was a bounded pilot tactic, not a
general definition of valuable Explore research. The current workflow first
assesses scientific opportunity and then assigns open-discovery, strategic-
development, or short-horizon execution scope.

## Corrections to the previous proposal

1. Fix the public integrity boundary before adding research features, but keep
   that patch scientifically result-neutral.
2. Do not add a large research runtime, eleven schemas, event sourcing, broad
   inference utilities, or multi-agent orchestration before a real research
   pilot demonstrates the need.
3. Draft new research contracts inside one private pilot first. Promote only
   the smallest reusable, disclosure-safe subset through a later public-export
   review.
4. Treat calibration role and regime relation as separate concepts:
   `calibration`, `validation`, and `held_out` describe use of evidence;
   `interpolation`, `extrapolation`, and `analytic_limit` describe where the
   result lies relative to that evidence.
5. Replace one universal minimum-publishable checklist with a common evidence
   core plus claim-type profiles. Data-calibrated phenomenology, analytic or
   formal results, numerical-method results, and model-internal predictions do
   not require identical evidence.
6. A future readiness command may audit record completeness. It must not
   certify novelty, physical truth, or publication worth.

## Phase 1 — Version 0.5.9 integrity hardening

The patch release is limited to fail-closed correctness, evidence integrity,
privacy, and reproducibility:

- require at least one acceptance check and derive pass state from those
  checks;
- reject disagreement between execution state and serialized result state;
- prevent extension metadata from replacing canonical result fields;
- require an explicit recognized support label;
- reject non-finite public JSON;
- reject artifact symlinks at bundle creation;
- build evidence bundles transactionally so a failed write leaves no partial
  bundle;
- validate consistency among the manifest, configuration, model context, and
  result records; and
- record a stronger, privacy-safe numerical environment fingerprint.

This phase must not change scientific equations, parameters, defaults,
tolerances, benchmark results, or acceptance criteria. A benchmark-specific
backend discrepancy belongs in a separate bounded diagnostic and does not
authorize a post-hoc tolerance change.

## Phase 2 — Private research pilot

After the integrity patch, run one domain-appropriate private vertical slice
around an owner-selected scientific opportunity. Candidate selection remains
a separate human decision informed by importance, gap plausibility,
falsifiability, holographic leverage, explanatory depth, outcome value, and
owner fit. Capability receipts then determine the honest horizon and cost:
open discovery, strategic development, or short-horizon execution.

Only short-horizon execution normally reaches the frozen physical
discriminator in the first or second substantive study. Strategic development
may construct several question-necessary capabilities through prospectively
bounded milestones and a planned physics checkpoint. Planned construction is
separate from the post-failure numerical-repair budget.

The pilot should draft only the records it actually needs, which may include:

- research question and closest-prior-work map;
- minimum defensible claim and falsification condition;
- study design and evidence-role split;
- uncertainty and robustness budget;
- claim-to-evidence ledger; and
- readiness gaps requiring human judgment.

Git history and the existing HoloForge gate records remain the default durable
ledger. An event-sourced runtime is justified only if the pilot demonstrates a
specific state-consistency problem that Git and validated records cannot
solve.

## Phase 3 — Version 0.6 public promotion

After the pilot closes or reaches an owner-reviewed durable milestone, perform
a new public-export audit. Cleanly reimplement only proven reusable behavior.
Likely candidates include:

- a new hypothesis-card version in which `analogy` is conditional;
- separate evidence-role and regime-relation fields;
- a minimal claim or study contract;
- deterministic completeness checks; and
- a local workspace command only if it removed a demonstrated failure mode.

Version 0.1 hypothesis cards must remain readable. A new schema version must
have explicit migration documentation and tests; it must not silently change
the meaning of an existing card.

## Common evidence core and conditional profiles

Every serious claim needs a precise statement, declared scope, baseline or
source connection, discriminating evidence, limitations, provenance, and
human review. Additional requirements depend on claim type:

- **Data-calibrated phenomenology:** disjoint calibration and held-out roles,
  input and parameter uncertainty, identifiability, and model-form robustness.
- **Model-internal numerical prediction:** convergence, an independent check,
  parameter and branch dependence, and explicit model non-inference.
- **Analytic or formal claim:** stated assumptions, derivation, exact or
  asymptotic checks, and independent human or symbolic audit; held-out data may
  be not applicable.
- **Numerical-method claim:** benchmark suite, error and conditioning analysis,
  independent implementations where practical, and a delimited applicability
  regime.

A robust negative result advances research only when it tests a meaningful
question and excludes a declared alternative or region. A technical stop is
not a physical negative result.

## Deferred work

Until the private pilot supplies evidence of need, defer:

- a universal research runtime or solver interface;
- broad Bayesian or machine-learning infrastructure;
- generic domain physics packs;
- automatic paper-worth or novelty scoring;
- candidate-ranking by one opaque score;
- multi-agent orchestration; and
- new public reproduction benchmarks unrelated to the selected claim.

## Release boundary

Documentation may be merged without creating a release. Version `0.5.9` is for
the bounded integrity patch. The private pilot is a research milestone, not a
public package release. Version `0.6.0` follows only after the pilot establishes
which research contracts or tools are genuinely reusable.
