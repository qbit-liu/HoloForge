# HoloForge agent instructions

These instructions apply to coding and research agents working in this public
repository. Start from the repository root so the project files and local
workflows are available.

## Project identity

HoloForge is a verification-first platform for bottom-up gauge/gravity
modelling. Preserve the separation between:

- **Forge/Verify:** literature-anchored models and reproducible checks; and
- **Explore:** falsifiable hypotheses whose support and disclosure state must
  remain explicit.

Read `CONSTITUTION.md` before changing a scientific contract. Do not describe a
passing model calculation as empirical validation of nature.

## Start every task

1. Inspect `git status` and preserve unrelated user changes.
2. Read `README.md` and the documentation relevant to the requested task.
3. Classify the work as Forge/Verify, Explore, or infrastructure/documentation.
4. State the intended files, validation, and scientific boundary before a
   substantial change.
5. Prefer a narrow, reversible implementation and maintained library
   functions over custom numerical primitives.

For instruction upgrades, concurrent-task maintenance, status retrieval or
research resumption, follow `docs/agent-maintenance.md`. Honor the current
request and authorization already recorded for its scope. A routine maintenance
step or status answer does not open a scientific gate or require a new A-E menu.

For a first session, follow `docs/agent-quickstart.md`.

## Choose the matching workflow

- Adding or extending a public benchmark: read and follow
  `.agents/skills/holoforge-add-benchmark/SKILL.md`.
- Running a bounded Explore gate: read and follow
  `.agents/skills/holoforge-research-gate/SKILL.md`.
- Preparing, running, or auditing an owner-authorized end-to-end autonomous
  Explore campaign: read and follow
  `.agents/skills/holoforge-auto-research/SKILL.md`.
- Moving any artifact from private research into this repository: read and
  follow `.agents/skills/holoforge-public-export/SKILL.md`.

If the agent runtime exposes repository skills, invoke the matching skill. If
it does not, open the named `SKILL.md` and follow it as the task procedure.
These workflows do not replace human scientific or disclosure approval.

## Scientific and privacy rules

- Record conventions, equations, boundary conditions, ensemble, numerical
  method, tolerances, validation evidence, and limitations.
- Treat numerics as evidence for a named claim-bearing physical decision, not
  as the default research endpoint. Before numerical work, freeze the
  claim-sufficiency criteria in `docs/research-gate-workflow.md`. Once they
  pass, stop numerical refinement unless more work can change that decision,
  test a distinct physical alternative, or materially strengthen the claim.
  Never obtain sufficiency by weakening a threshold or dropping a failed check.
- Use the support and review labels defined in `docs/scientific-support.md`.
- Mark material AI involvement; human review must not erase AI provenance.
- During an active private Explore gate, update its research knowledge base at
  durable milestones. Keep working knowledge explicitly provisional,
  evidence-linked, and separate from human-reviewed stable knowledge; preserve
  challenged or retired entries and their non-inference boundaries. Capture
  reusable knowledge from literature, dictionaries, derivations, methods,
  data, results, decisions, and reproducibility work, not only failures.
- Before a new Explore intake, read the private reviewed-knowledge and closure-
  lesson indexes, inspect primary evidence for applicable entries, and record
  how their stable IDs change the new scorecard or contract. Also declare the
  portfolio intent, search shape, domains considered or excluded, and actual
  candidate coverage. Before capability matching, assess scientific
  opportunity through physical importance, gap plausibility, falsifiability,
  physical or conceptual holographic leverage, computational or
  representational holographic leverage, explanatory or predictive depth,
  outcome value, and owner fit. A computational-leverage claim must name the
  hard original problem, best nonholographic baseline, dictionary and validity
  regime, accessible observables, accuracy, robustness, and total construction
  and compute cost; an extra dimension alone is not an advantage. The named
  human owner decides scientific value; capability receipts must not select
  the question. Then classify the horizon as open
  discovery, strategic development, or short-horizon execution. For
  publication-targeted work, record the minimum publishable physical claim,
  earliest honest physical-discriminator gate and prerequisites, numerical-
  dependence lane, campaign construction budget, separate candidate-wide
  repair budget, and non-aggregate scientific-opportunity, physical-claim,
  source-and-novelty, and numerical-credibility status. Only the short-horizon
  lane normally reaches the discriminator in the first or second detailed
  gate; question-necessary model and capability construction may use an owner-
  approved strategic campaign.
- When a blocker recurs or a repair budget is nearly exhausted, use the bounded
  impasse protocol in `docs/research-gate-workflow.md`: combine targeted
  authoritative source search with an independent physics audit, then freeze
  at most one scoped repair. The repair budget is cumulative across a
  publication-targeted candidate; after one failed numerical repair, require a
  portfolio-level reassessment before any second repair. Do not use internet
  search as authority, weaken a threshold post hoc, or relabel a technical stop
  as a physical result.
- At every closed Explore gate, preserve the result and complete the generic
  closure retrospective in `docs/templates/research-retrospective-template.md`;
  feed lessons into future gates without rewriting the closed one.
- Keep unpublished hypotheses, calculations, results, literature notes, and
  manuscripts in a separate access-controlled repository.
- Never add secrets, private filesystem paths, confidential correspondence,
  or unpublished candidate identifiers to this public repository.
- Do not infer that approval to calculate authorizes publication or public
  transfer.
- When an owner-approved bounded autonomy window is recorded for a frozen
  Explore gate, finish its listed routine work without requesting approval at
  every intermediate source, plot, test, or implementation choice. Return at
  the first declared outcome, stop, scope or threshold change, cost or repair
  overrun, impasse, interpretation or publication judgment, disclosure or
  external communication, or unlisted Git/remote action. The window never
  rolls over to another gate or candidate.
- For an owner-authorized autonomous campaign, treat the mission hash as the
  campaign authority. Use one coordinator as the sole canonical writer and
  keep literature, execution, and verification roles read-only. Do not touch
  the pinned HoloForge checkout, other projects, frozen contracts or thresholds,
  raw evidence, human review states, credentials, global configuration, remote
  Git state, external communications, disclosure, or submission. Return at the
  first illegal transition, integrity mismatch, budget overrun, path escape, or
  undelegated decision. A stopped campaign is a valid terminal deliverable.

## Validation

Use the documented environment and choose checks by change type in
`docs/agent-maintenance.md`. For executable infrastructure or scientific changes,
run the relevant focused checks, then complete these integration checks once:

```bash
python -m unittest discover -s tests -v
holoforge verify soft-wall-vector
```

Run the relevant benchmark or comparison command for scientific changes. Also
inspect the final diff and run `git diff --check`. Changes to scientific
results require synchronized documentation, model records, and tests.
For documentation-only changes, check the affected links, skills and policies;
do not run numerical campaigns. Full CI remains required for public integration.

## Git and review

- Keep commits and pull requests limited to one logical change.
- Stage only intended files; never discard unrelated work.
- For owner-requested work in this public repository, standing owner
  authorization permits scoped local commits and normal fast-forward pushes
  to the existing `origin` remote and intended branch. Complete the relevant
  local validation and public-content review, inspect the outgoing commits,
  and check the remote state first. Do not ask again for each routine push;
  verify the remote commit and report CI afterward.
- Merging, releases, branch deletion, force pushes or history rewrites, changing
  the remote destination, and private export or scientific disclosure require
  separate explicit authorization. A later task-specific restriction overrides
  the standing public-repository permission.
- Treat a bounded autonomy window as execution authority only. A local commit
  must be explicitly included in it; push, merge, release, branch deletion,
  public export, and disclosure remain separate owner decisions for that
  research scope. Standing public-repository permission does not expand a
  frozen Explore window or autonomous mission, or permit its pinned framework
  to be changed.
- Before requesting an owner decision, give an item-by-item recommendation,
  reason, scope opened, scope remaining closed, and important uncertainty.
- At an owner gate, also state completed, current, and proposed next stages,
  then offer A-E paths: approve all recommendations, approve selected items,
  request revision or evidence, status walkthrough only, or a custom response.
  Recommend one path and never infer authorization beyond its stated scope.
- When a progress picture is requested, map the actual research project rather
  than HoloForge development. Keep its state and full-size figure project-local;
  embed a dated PDF snapshot in a review packet only when that packet is needed.
