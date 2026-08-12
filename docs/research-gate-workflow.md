# Research Gate Workflow

This workflow turns an Explore idea into an auditable sequence of bounded
decisions without requiring unpublished research to be public. It is a process
contract, not a claim that a candidate is novel or correct.

## Three valid Explore novelty tracks

Classify the intended contribution before screening it:

1. **New-domain application:** gauge/gravity duality has not credibly been
   applied to the parent scientific field.
2. **New-subfield or new-phenomenon application:** the parent field has
   holographic research, but a specific subfield, phenomenon, regime,
   mechanism, or observable has not been treated.
3. **Method transfer or model improvement:** an established method is moved
   into a neighboring holographic problem, or an existing model receives a
   sharper consistency, verification, or predictive test.

All three can be scientifically valuable. The class must be stated explicitly,
and any priority or novelty claim requires a targeted literature search.

## Qualify candidates with an Explore intake scorecard

Before writing a detailed frozen contract, complete the generic
[`Explore intake scorecard`](../.agents/skills/holoforge-research-gate/assets/explore-intake-scorecard.example.md)
inside the private research repository. It tests five conditions that should
be cheap to decide before substantial calculation:

First read the current private lesson index and the primary evidence behind
potentially relevant entries. Record the index revision, applicable stable
lesson IDs, and the candidate-specific control each lesson adds to the
scorecard. Search by failure mode and numerical risk as well as topic. If no
lesson applies, record which tags were checked. Prior failure guides the next
test; it is not evidence that a different candidate must fail.

1. **Source-complete inputs:** the primary sources and private records identify
   every equation, convention, branch, ensemble, coefficient, and comparison
   needed by the proposed first gate, or identify one bounded source check
   that can settle the gap.
2. **Invariant target beyond the generic baseline:** the candidate names a
   dimensionless ratio, branch-resolved feature, consistency condition, or
   other observable that cannot be removed by conventions or obtained from a
   simpler generic model alone.
3. **Cheap kill test:** one preregistered source, analytic, or low-cost
   numerical check can reject the candidate before a solver or broad scan.
4. **Positive-result endpoint:** the record states exactly what result would
   count as meaningful, what evidence it would support, and which next
   decision it would open.
5. **Cost ceiling:** the owner fixes the maximum literature, implementation,
   compute, and review cost of the first gate and the conditions that stop
   further investment.

Mark every item `pass`, `conditional`, or `fail` and cite the evidence. A
detailed gate opens only when all five pass. One or more conditional items may
open only a single named intake-evidence task that is cheaper than the proposed
gate. Any failed item defers or rejects the candidate. There is no aggregate
score that can hide a failed scientific prerequisite.

The scorecard ranks readiness for the next bounded test, not novelty,
importance, truth, or publication value. It remains private when it contains
unpublished candidate identities, literature notes, equations, or results.

## One gate, one bounded question

Every research gate should contain the following records:

1. **Frozen contract:** written before the calculation and limited to one
   question. It fixes inputs, methods, diagnostics, acceptance thresholds,
   stop conditions, exclusions, and the decision owner.
2. **Calculation and durable artifacts:** code, configuration, environment
   metadata, machine-readable results, and plots needed to inspect the gate.
   Prefer well-tested library functions over new local implementations.
3. **Tests and independent checks:** analytic checks, convergence, residuals,
   alternative solvers, conservation laws, or other defenses proportional to
   the scientific risk.
4. **Result record:** supported findings first, followed by numerical evidence,
   limitations, reproduction instructions, and explicit non-claims.
5. **Hostile critic report:** the strongest alternative explanations,
   uncontrolled assumptions, window artifacts, missing comparisons, and the
   cheapest defensible next test.
6. **Owner review:** a short list of separate decisions covering the
   implementation, numerical verdict, evidence boundary, and next action,
   followed by an explicit recommendation for every requested choice.
7. **Decision record:** after human approval, record what was accepted and what
   remains closed.
8. **Closure retrospective and commit:** classify the outcome, preserve what
   failed as well as what held, state the reusable lesson and non-inference
   boundary, name a reopening trigger, then commit one logical reviewed gate.

If a stop condition fires, stop the gate, preserve the bounded stopped result
under its correct outcome class, and return to owner review. Do not expand the
scope to rescue the hypothesis.

## Learn from every closed gate

Every closed gate receives a short research retrospective, including gates
with positive, negative, inconclusive, conditional, source-stopped,
prior-art-stopped, or technically stopped outcomes. Use
[`docs/templates/research-retrospective-template.md`](templates/research-retrospective-template.md)
and follow [Learning From Every Research Result](learning-from-results.md).

The retrospective links the primary evidence and records what held, what
failed, what the gate taught, what must not be inferred, one prospective
workflow improvement when warranted, and the evidence required to reopen the
direction. Give the lesson a stable ID, retrieval tags, and explicit
applicability and non-applicability conditions. It does not replace the result
record or hostile critic report.

Lessons feed forward into later intake scorecards, contracts, numerical
methods, and stop rules. They must not retroactively change the frozen gate,
acceptance threshold, support label, or owner decision. Keep any retrospective
that names unpublished candidates or results in the private research
repository. Public HoloForge receives only generic, privacy-reviewed workflow
improvements or separately disclosure-approved artifacts.

## Every decision request includes a recommendation

An owner should not receive a menu of approvals and choices without the
reviewer's scientific judgment. Every owner-review gate must end with a
**Recommendation** section that:

1. maps each numbered decision to a recommended response, such as `approve`,
   `revise`, `reject`, `pause`, or one named option;
2. gives the shortest evidence-based reason for the recommendation;
3. states what work the recommendation opens and what remains closed; and
4. identifies the most important tradeoff or uncertainty when the choice is
   not clear-cut.

If the evidence cannot support a preferred scientific option, the
recommendation is to pause and obtain the named missing evidence. The
recommendation must not be omitted or replaced by an unsupported guess.

A recommendation is advice, not owner approval. The decision owner retains the
final choice unless authority for a bounded class of routine gates has been
explicitly delegated and recorded.

## Give the owner clear response paths

After the numbered recommendations, offer these five response paths. Adapt the
details to the gate, but do not change their meaning:

- **Option A — approve all recommendations:** apply every item-by-item
  recommended response and only the scope each item says it opens.
- **Option B — approve selected items:** the owner names decision numbers;
  unselected decisions and later work remain closed.
- **Option C — request revision or evidence:** pause while the owner identifies
  a concern or the missing evidence to obtain.
- **Option D — status walkthrough only:** explain what is completed, the
  current stage, the proposed next stage, and what remains closed, without
  treating the request as approval.
- **Option E — custom response:** accept the owner's own wording and confirm
  any ambiguous mapping before acting.

Mark the option recommended for the present evidence and explain why. Option A
is not automatically recommended: a failed stop condition, unresolved
uncertainty, or missing evidence may make Option C or D safer. The menu is a
convenience layer over the numbered decisions, not blanket authorization for
unlisted work, publication, merging, or release.

## Repeat the choices after a gate closes

Recording an owner decision does not end the conversational handoff. The
closure receipt must repeat the completed/current/next status, identify what
remains closed, and name the next eligible decision. It must then give the
owner a fresh A-E response menu for that next handoff, with an item-by-item
recommendation when new work is proposed. Do not end only with statements such
as `no approval is pending` or `a later portfolio decision is required` when
the eligible choices can already be named.

The fresh menu is not retrospective approval and does not silently reopen the
closed gate. If no scientifically justified next action exists, recommend that
the project remain paused and make the status-walkthrough path explicit. If
the next choice belongs to a separate project or portfolio gate, say so and
keep the closed project's own state accurate. A project whose canonical state
has `awaiting_owner: false` must not receive a fabricated pending owner menu
merely to satisfy the conversational handoff rule.

## Agent-updated workflow snapshot

A reviewable research-progress picture is possible without adding a workflow
server. It represents the state of one research project: literature screening,
frozen questions, theoretical and numerical checks, verification, critic
review, owner decisions, feedback loops, later gates, and possible completion.
It is not a timeline of HoloForge's own software development.

The research-gate skill includes:

- `assets/research-progress.example.json`, a generic project-state template;
  and
- `scripts/render_research_progress.py`, a renderer that validates groups,
  stages, transitions, branches, one current stage, and the owner menu.

Copy the JSON template into the research project, update it after each durable
milestone, and render Markdown/Mermaid from the public HoloForge checkout:

```bash
python PATH_TO_HOLOFORGE/.agents/skills/holoforge-research-gate/scripts/render_research_progress.py \
  RESEARCH_PROGRESS.json --output RESEARCH_PROGRESS.md
```

For a standalone figure and a PDF-ready copy, use the maintained Graphviz
layout engine:

```bash
python PATH_TO_HOLOFORGE/.agents/skills/holoforge-research-gate/scripts/render_research_progress.py \
  RESEARCH_PROGRESS.json --output RESEARCH_PROGRESS.md \
  --figure-output RESEARCH_PROGRESS.svg \
  --figure-output RESEARCH_PROGRESS.pdf
```

The SVG is the ordinary full-size progress figure. The PDF rendering may be
embedded as a dated snapshot in an owner-review packet. Both are derived from
the same project-local JSON record; the embedded page does not replace the
standalone figure or the canonical state. If Graphviz `dot` is unavailable,
the Markdown/Mermaid route still works without it.

The state records completed work, one current research stage, pending and
blocked branches, next action, closed scope, owner decisions, and A-E response
paths. The renderer fails on malformed state, unknown or duplicate stages,
invalid transitions, more than one current stage, or an incomplete owner menu.
Marking a stage completed means that workflow task is recorded as finished; it
does not itself raise a claim's scientific-support level.

This is an **agent-updated live snapshot**, not automatic background telemetry.
It is current after the agent updates the JSON and reruns the renderer. GitHub
can display the Mermaid picture but only at the latest committed and pushed
state. Unpublished project state and generated figures remain in the private
research repository unless a separate public-export review authorizes them.

## Three statuses that must not be confused

- **Scientific support:** what the current evidence establishes, using the
  support labels in the Scientific Constitution.
- **Research authorization:** what calculation or review the owner has allowed
  next.
- **Disclosure status:** whether an artifact is private, cleared for a public
  pull request, or released.

Approval to continue a calculation is not approval to publish it. Keeping a
result private does not strengthen or weaken its scientific support.

## Local Git record for private research

Use a separate access-controlled repository for unpublished work. Recommended
practice is:

- keep a durable main branch and short-lived gate branches;
- commit one logical literature, derivation, implementation, validation, or
  decision change at a time;
- use descriptive messages that state the scientific scope;
- preserve reviewed negative results and rejected hypotheses;
- preserve a closure retrospective that makes each accepted outcome,
  non-inference boundary, reusable lesson, and reopening trigger searchable;
- do not rewrite reviewed history merely to make it look cleaner; and
- use optional annotated local tags for reviewed gates, remembering that a tag
  does not strengthen a scientific claim.

The private repository is a research ledger. It should not be made public as a
shortcut. Follow the separate [public-export checklist](private-research-workflow.md#public-export-checklist).

## Owner-review PDF packet

When equations, tables, or plots are hard to review reliably in Markdown,
prepare a concise PDF packet in the standard HoloForge style:

- 11-point article typography, 0.76-inch margins, and page numbers;
- a running left header naming the gate and a right header stating the
  disclosure class;
- a title, subtitle, owner/date line, and shaded outcome-first summary;
- numbered sections and equations;
- compact booktabs-style tables with declared tolerances;
- one plot per page when a figure is needed, with no uncontrolled
  extrapolation;
- navy `Supported` and `Not supported` evidence statements;
- a hostile critic section followed by the exact owner decisions;
- an item-by-item recommended response with a concise reason and scope effect;
- the completed, current, and proposed next stage plus the A-E response
  paths;
- when requested, a dated research-progress snapshot generated from the same
  project-local state as the standalone figure; and
- a footer reiterating the disclosure boundary.

The reusable source is
[`docs/templates/review-packet-template.tex`](templates/review-packet-template.tex).
Compile twice, inspect the log for layout warnings, render every page to an
image, and visually check clipping, overlaps, equations, tables, plots,
headers, and page numbers before delivery.

The standalone SVG remains the easiest way to inspect the full research map.
When a review packet is already required, enable the template's optional
progress page by defining `\HoloForgeIncludeProgress`, set the generated PDF
path and timestamp, and compile it into the packet. Do not create a PDF solely
to show the progress figure when the standalone SVG or Markdown view is
sufficient.

This conditional rule applies to both private Explore gates and public
Forge/Verify scientific-contract reviews. When the decision owner has stated
that Markdown equations are difficult to review, prepare and verify the PDF
before requesting scientific approval. The requirement must be read from this
checked-in workflow and the matching agent skill, not inferred from
conversational memory.

## Public contribution boundary

Public HoloForge may receive the generic workflow, reusable framework
improvements, or a separately reviewed reproduction package. It must not
receive unpublished candidate identities, private literature notes, working
equations, intermediate results, local paths, confidential correspondence, or
the private repository's history.
