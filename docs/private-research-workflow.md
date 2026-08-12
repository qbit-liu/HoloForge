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
  notes/
  code/
  results/
  paper/
```

The private project should pin the HoloForge version or commit it depends on,
record its own environment, and preserve negative results. It may extend the
public schemas locally, but those extensions are not automatically part of the
HoloForge public contract.

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

1. **Intake:** record the candidate dictionary, assumptions, falsification
   test, AI involvement, and decision owner in a private hypothesis card. Then
   complete the five-part Explore intake scorecard: source-complete inputs,
   an invariant target beyond the generic baseline, a cheap kill test, a
   positive-result endpoint, and a cost ceiling. A detailed gate opens only
   after all five pass; a conditional item may open only one cheaper bounded
   evidence task.
2. **Screening:** search prior work and test dimensional, symmetry, boundary,
   and ensemble consistency before investing in a large calculation.
3. **Discriminating calculation:** compare against a simpler baseline and use a
   preregistered keep/reject criterion where practical.
4. **Internal decision:** retain, revise, or reject the hypothesis. Keeping the
   work private does not change its scientific-support label.
5. **Publication:** submit and revise the paper without copying confidential
   correspondence into the public project.
6. **Release review:** after journal acceptance or another explicit disclosure
   decision, select the exact artifacts that may become public.

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
