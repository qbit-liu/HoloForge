# Private Explore Research Workflow

This workflow lets a researcher use HoloForge for genuinely novel work without
publishing the project before they are ready. Scientific support and public
visibility are separate decisions.

## Three locations with different purposes

1. **Public HoloForge repository** — reusable framework code, schemas,
   published benchmarks, synthetic examples, and material explicitly cleared
   for release.
2. **Separate private research repository** — unpublished hypotheses, detailed
   literature notes, calculations, intermediate results, manuscript drafts,
   and confidential collaboration material.
3. **Reviewed public reproduction package** — the minimum code, inputs,
   provenance, tests, and documentation needed to reproduce results that have
   been accepted for publication or otherwise approved for disclosure.

The private repository should have restricted access and its own history. Do
not place it inside the public HoloForge checkout. The ignored directories
`/.private-research/` and `/unpublished/` are last-resort accidental-commit
guards, not secure storage.

## Private project structure

A private project may reuse the public HoloForge package and schemas while
keeping its research record independent:

```text
private-project/
  README.private.md
  hypothesis-card.json
  RESEARCH_LESSONS.md
  notes/
  code/
  results/
  RETROSPECTIVE.md
  paper/
```

The private project should pin the HoloForge version or commit it depends on,
record its own environment, and preserve negative results. It may extend the
public schemas locally, but those extensions are not automatically part of the
HoloForge public contract.

Use `RESEARCH_LESSONS.md` as the inspectable private knowledge base, following
the generic [`research-knowledge-template.md`](templates/research-knowledge-template.md).
Maintain two visibly separate states in that file: a working queue updated
after durable research milestones, and reviewed knowledge whose evidence,
scope, support level, review state, and non-inference boundary were checked by
a named human. Reviewed knowledge can come from literature, dictionaries,
derivations, methods, data, results, decisions, or reproducibility work;
closure lessons remain a subtype admitted only after owner-reviewed closure.
Working entries may be provisional, corroborated, challenged, ready for owner
review, promoted, or retired. A live observation may sharpen the next check,
but it must not silently become reviewed knowledge or rewrite the frozen gate.

## Research gates

The concise gate sequence below is expanded in the reusable
[research-gate workflow](research-gate-workflow.md), including frozen
contracts, hostile critic reports, owner decisions, local Git records, and the
standard PDF review-packet style. Every request for owner approval or choice
must also include an item-by-item recommendation and its reason, an A-E
response menu, and a completed/current/next status summary. The optional
agent-updated research-progress map is generated from a state file kept in the
private repository. Its standalone figure tracks literature, frozen gates,
parallel checks, decisions, and later research stages; a dated PDF rendering
may also be embedded in an owner-review packet.

After an approved gate is recorded and closed, the agent must repeat the
completed/current/next summary and present fresh A-E choices for the next
eligible handoff. This requirement applies even when the recommendation is to
remain paused. The new menu does not reopen the completed gate, authorize a
calculation, or turn `no approval pending` into an approval. A separate
portfolio choice must be identified as a separate gate rather than inserted as
false pending state in the closed research project.

1. **Intake:** read the current private reviewed-knowledge and closure-lesson
   indexes and record which stable knowledge and lesson IDs and evidence apply
   to this candidate. Translate each into a candidate-specific control; if none
   applies, record the knowledge classes and tags searched. Then record the
   portfolio intent, search shape, domains considered or deliberately excluded,
   and candidate-pool coverage. For publication-targeted work, complete the
   separate publication-pathway assessment before prioritizing a lead. Then
   record the candidate dictionary, assumptions, falsification test, AI
   involvement, and decision owner in a private hypothesis card and complete
   the five-part Explore intake scorecard: source-complete inputs, an invariant
   target beyond the generic baseline, a cheap kill test, a positive-result
   endpoint, and a cost ceiling. A detailed gate opens only after all five
   pass; a conditional item may open only one cheaper bounded evidence task.
2. **Screening:** search prior work and test dimensional, symmetry, boundary,
   and ensemble consistency before investing in a large calculation.
3. **Discriminating calculation:** compare against a simpler baseline and use a
   preregistered keep/reject criterion where practical.
4. **Live knowledge update:** after source review, contract freeze,
   calculation, verification, criticism, and owner decisions, update the
   evidence-linked working queue and preserve its non-inference boundary.
   Distill decision-relevant paper knowledge with an exact source version and
   locator; do not copy every paper note into the knowledge base.
5. **Internal decision and reflection:** retain, revise, or reject the
   hypothesis, then complete the generic
   [closure retrospective](templates/research-retrospective-template.md). Record
   the outcome class, evidence, lesson, non-inference boundary, prospective
   workflow change, and reopening trigger. Keeping the work private does not
   change its scientific-support label.
6. **Publication:** submit and revise the paper without copying confidential
   correspondence into the public project.
7. **Release review:** after journal acceptance or another explicit disclosure
   decision, select the exact artifacts that may become public.

### When a gate becomes stuck

Use the bounded impasse protocol in the research-gate workflow when a blocker
recurs or the approved repair budget is nearly exhausted. Classify the blocker,
search targeted primary and authoritative external evidence, audit the physics
independently, inspect the matching numerical or implementation layer, and
freeze at most one scoped repair before returning to the owner. Internet search
is an evidence-locating step, not a substitute for physical reasoning. Preserve
an unresolved source or technical stop if the bounded repair fails; do not
silently loosen thresholds or expand the hypothesis.

## Public export checklist

Before copying any artifact into HoloForge, a human reviewer must confirm:

- the research owner explicitly approved the public export;
- every result is published or otherwise cleared for disclosure;
- claims cite public sources or an accepted publication;
- secrets, credentials, private paths, restricted data, confidential notes,
  reviewer correspondence, and unrelated history are absent;
- the package contains only the inputs and outputs needed for reproduction;
- model or hypothesis cards, environment metadata, tests, limitations, and
  licensing are complete;
- the export is reviewed as a narrow pull request before merge and release.

If confidential material is accidentally committed, stop publication, revoke
any exposed credential, and remove the material from all reachable history
before continuing. Deleting only the latest file is not sufficient once a
commit has been shared.
