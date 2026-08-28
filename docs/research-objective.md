# HoloForge research objective

## Objective

HoloForge should increase the rate at which a researcher reaches a defensible
new quantitative physical claim, subject to correctness, provenance,
uncertainty, robustness, privacy, and human scientific review. It cannot
guarantee a publication or replace judgment about significance and novelty.
Any future readiness audit must not certify novelty, physical truth, or
publication worth.

Benchmark count, test count, pull-request count, report count, release count,
and agent activity measure engineering work. They are not research-output
metrics.

## Two research loops

Use a fast **discovery loop** to compare candidates, test the simplest
alternative, and reach the first physical discriminator with bounded effort.
Use the heavier **confirmation loop** only after a result supplies a credible
signal, robust exclusion, or scientifically important tension.

```text
discovery:
  physical question -> closest prior work -> bounded claim
  -> cheap analytic/source checks -> signal pilot -> retain/revise/stop

confirmation:
  frozen claim -> necessary baseline -> full calculation
  -> uncertainty and robustness -> independent check
  -> hostile review -> human readiness decision
```

For publication-targeted Explore work, the first or second substantive study
should reach the frozen physical discriminator. A longer solver-qualification
campaign is justified only when the numerical method is itself the declared
research output.

## Evidence core

Every serious claim needs:

- a precise statement and model or evidence boundary;
- a mechanism, discriminator, or controlled question;
- connection to a primary source, baseline, or exact limit;
- a result not silently reused as both calibration and prediction;
- numerical or analytic credibility appropriate to the claim;
- uncertainty, limitations, and non-inference boundaries;
- reproducible evidence links and provenance; and
- named human review.

Additional requirements are conditional on claim type. Held-out data are
mandatory for data-calibrated predictive claims, but may be not applicable to
a formal derivation or exact identity. Analytic claims require explicit
assumptions and an independent derivation audit; numerical-method claims
require error, conditioning, and applicability evidence.

## Separate evidence role from regime relation

Future research contracts must not combine how evidence was used with where a
prediction lies:

| Axis | Examples |
| --- | --- |
| Evidence role | `calibration`, `validation`, `held_out`, `none` |
| Regime relation | `interpolation`, `extrapolation`, `analytic_limit`, `not_applicable` |

A calibrated extrapolation is still calibrated. An interpolating result can
still be held out. Keeping these axes separate prevents fitted descriptions
from being relabelled as predictions.

## Research-pulled development

Do not add a public benchmark, schema, abstraction, renderer, agent role, or
runtime merely to make HoloForge look complete. Add it when it fixes a
scientific-integrity problem or when a bounded research project demonstrates
that the capability is reusable.

The next capability proof is one private, end-to-end vertical slice using a
qualified route and an owner-selected physical question. Draft its records in
the private repository, preserve its Git history, and promote only the minimum
generic artifact after a separate public-export review. The public roadmap
must not identify or disclose the private candidate.

## Valid outcomes

A research cycle may end with a supported claim, a robust negative result, an
inconclusive result, a prior-art or source stop, or a technical stop. These
outcomes are not interchangeable. In particular, a failed calculation is not
a physical negative result, and a stable calculation is not by itself a
publishable physical claim.
