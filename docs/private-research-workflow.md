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

1. **Intake:** record the candidate dictionary, assumptions, falsification
   test, AI involvement, and decision owner in a private hypothesis card.
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
