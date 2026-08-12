---
name: holoforge-research-gate
description: Run a bounded, auditable HoloForge Explore research gate from frozen contract through verification, hostile criticism, owner recommendations, decision recording, and a scoped commit. Use for speculative holography screening, private feasibility calculations, owner-review packets, negative-result preservation, or deciding whether a candidate may advance. Do not use it to bypass owner approval, make novelty claims, or publish private work.
---

# HoloForge Research Gate

Run one question-sized scientific gate. Preserve negative results and keep
scientific support, authorization, and disclosure as separate states.

## Load the controlling records

1. Read `CONSTITUTION.md`.
2. Read `docs/research-gate-workflow.md` completely.
3. Read `docs/scientific-support.md`.
4. For unpublished work, also read `docs/private-research-workflow.md` and
   inspect the private project's current hypothesis card, decision log, and Git
   status.
5. Before a new intake, read the private project's lesson index and the primary
   evidence behind potentially applicable entries. Record the index revision,
   stable lesson IDs, and applicability in the intake scorecard.

Treat the repository documents as authoritative when they are stricter than
this summary.

## Qualify the candidate before a detailed gate

Before freezing a calculation contract, copy and complete
`assets/explore-intake-scorecard.example.md` in the private project. Audit five
questions: source-complete inputs, an invariant target beyond the generic
baseline, a cheap kill test, a defined positive-result endpoint, and an
explicit cost ceiling.

Retrieve prior lessons by failure mode and method risk as well as topic. For
each applicable stable lesson ID, add a candidate-specific source check,
baseline, diagnostic, threshold, or stop rule. If none applies, record which
tags were searched. Never infer that a new candidate fails because an earlier
one did, and never copy an old threshold without re-establishing applicability.

Use `pass`, `conditional`, or `fail` for each item. A detailed research gate
may open only when all five items pass. A conditional item may open only one
named, bounded evidence task that is cheaper than the proposed gate. Any
failed item defers or rejects the candidate; do not compensate for it by
adding scores from other rows. Record the evidence and owner disposition so
the intake decision remains auditable.

## Run one gate

1. State the question, frozen inputs, allowed methods, acceptance criteria,
   stop conditions, exclusions, decision owner, and disclosure class before
   calculation.
2. Check primary literature and provenance needed for this gate. Distinguish a
   missing source from evidence that no source exists.
3. Perform only the authorized calculation. Reuse appropriate maintained
   library functions before writing a numerical primitive.
4. Verify the result with the checks appropriate to its claim: analytic limits,
   residuals, constraints, sources, Ward identities, convergence, independent
   methods, and comparison data.
5. Write a hostile critic report that identifies the strongest alternative
   explanation and the cheapest discriminating next test.
6. Prepare an outcome-first owner review. For every numbered decision, give a
   recommended response, concise evidence-based reason, work opened, work
   remaining closed, and the leading uncertainty or tradeoff. State what is
   completed, the current stage, the proposed next stage, and what remains
   closed.
7. End the request with five response paths: A, approve all item-by-item
   recommendations; B, approve only named decisions; C, request a revision or
   named missing evidence; D, receive a status walkthrough without authorizing
   work; and E, give a free-form custom response. Mark one path as recommended
   for the present evidence, and confirm any ambiguous custom response.
8. Stop for the owner unless authority for this exact class of bounded gate is
   already delegated and recorded.
9. After the decision, record the selected responses and complete a project-
   local closure retrospective from
   `docs/templates/research-retrospective-template.md`. Classify the outcome,
   assign a stable lesson ID and retrieval tags, link primary evidence,
   preserve what failed, state applicability and what must not be inferred,
   record any prospective intake or contract lesson, and name the evidence
   required to reopen the direction. Do not use reflection to rewrite the
   frozen gate or strengthen its support label.
10. Update status and evidence boundaries, run checks, and commit only the
    reviewed gate and its retrospective. The closure handoff must then repeat
    completed/current/next status and fresh A-E choices for the next eligible
    decision; do not end only with `no approval pending`.

## Maintain a progress snapshot

When the owner wants workflow visibility, represent the research project, not
the development history of HoloForge. Copy
`assets/research-progress.example.json` into the private project and replace
its generic groups, stages, transitions, branches, and status values with the
reviewed state of that research. Keep exactly one stage `current`.

Render Markdown/Mermaid plus standalone vector and PDF figures with:

```bash
python PATH_TO_HOLOFORGE/.agents/skills/holoforge-research-gate/scripts/render_research_progress.py \
  RESEARCH_PROGRESS.json --output RESEARCH_PROGRESS.md \
  --figure-output RESEARCH_PROGRESS.svg \
  --figure-output RESEARCH_PROGRESS.pdf
```

Markdown output requires only Python. Standalone SVG, PNG, or PDF output uses
the maintained Graphviz `dot` layout engine when it is installed. Use the
standalone SVG as the ordinary full-size progress view. When preparing an
owner-review packet, include the PDF rendering as a dated snapshot on its own
page by defining `\HoloForgeIncludeProgress` in the packet source and setting
the generated PDF path and timestamp. Do not replace the project-local state
file or standalone figure with the embedded copy.

Update and re-render the snapshot after the contract is frozen, calculation
finishes, verification or criticism changes the evidence boundary, an owner
decision is recorded, or the gate closes. At every handoff, offer to explain
the completed, current, and next stages directly in conversation. After a
closure, give fresh A-E response paths for the next eligible decision even if
the recommendation is to remain paused. Do not add a fabricated owner menu to
a closed project whose canonical state correctly has `awaiting_owner: false`;
identify a separate portfolio or project decision as a separate handoff.

The snapshot is agent-updated state, not background telemetry. Stage completion
means a workflow task is recorded as finished; it does not itself strengthen a
scientific claim. A local file can change during an active agent session;
GitHub shows only the latest committed and pushed snapshot. Keep unpublished
state and figures in the private project and never copy them into public
HoloForge without a separate export review.

## Apply hard boundaries

- Do not enlarge a failed gate to rescue a hypothesis.
- Do not infer a physical claim from solver convergence alone.
- Do not classify a source, prior-art, representation, or numerical failure as
  a physical negative result unless the frozen physical endpoint actually
  passed.
- Do not call a literature screen exhaustive unless its search contract and
  coverage justify that label.
- Do not move unpublished identities, equations, data, paths, or results into
  public HoloForge.
- Do not treat a recommendation as owner approval.
- If evidence is insufficient, recommend pausing for one named missing piece
  of evidence.

## Deliver the gate

Return:

1. the bounded outcome first;
2. supported and not-supported statements;
3. verification performed and failures preserved;
4. the outcome class and bounded lesson;
5. the critic verdict;
6. numbered owner decisions with item-by-item recommendations;
7. the exact work that remains unauthorized; and
8. the A-E response paths, including the recommended path and status-only
   path.

Apply the same delivery contract to the receipt after a gate is recorded and
closed. The post-closure menu governs only the newly stated next handoff and
never retroactively enlarges the completed gate.

When a PDF review packet is requested, use
`docs/templates/review-packet-template.tex`, compile twice, render every page,
and visually inspect equations, tables, figures, and page breaks. When a
research-progress view is requested, generate its PDF from the same project
state and enable the template's optional progress-snapshot page.
