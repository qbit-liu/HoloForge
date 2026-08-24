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

For a first session, follow `docs/agent-quickstart.md`.

## Choose the matching workflow

- Adding or extending a public benchmark: read and follow
  `.agents/skills/holoforge-add-benchmark/SKILL.md`.
- Running a bounded Explore gate: read and follow
  `.agents/skills/holoforge-research-gate/SKILL.md`.
- Moving any artifact from private research into this repository: read and
  follow `.agents/skills/holoforge-public-export/SKILL.md`.

If the agent runtime exposes repository skills, invoke the matching skill. If
it does not, open the named `SKILL.md` and follow it as the task procedure.
These workflows do not replace human scientific or disclosure approval.

## Scientific and privacy rules

- Record conventions, equations, boundary conditions, ensemble, numerical
  method, tolerances, validation evidence, and limitations.
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
  candidate coverage. For publication-targeted work, assess the paper-shaped
  question and bounded path separately from scientific readiness.
- When a blocker recurs or a repair budget is nearly exhausted, use the bounded
  impasse protocol in `docs/research-gate-workflow.md`: combine targeted
  authoritative source search with an independent physics audit, then freeze
  at most one scoped repair. Do not use internet search as authority, weaken a
  threshold post hoc, or relabel a technical stop as a physical result.
- At every closed Explore gate, preserve the result and complete the generic
  closure retrospective in `docs/templates/research-retrospective-template.md`;
  feed lessons into future gates without rewriting the closed one.
- Keep unpublished hypotheses, calculations, results, literature notes, and
  manuscripts in a separate access-controlled repository.
- Never add secrets, private filesystem paths, confidential correspondence,
  or unpublished candidate identifiers to this public repository.
- Do not infer that approval to calculate authorizes publication or public
  transfer.

## Validation

Set up the development environment as documented in `README.md`, then run:

```bash
python -m unittest discover -s tests -v
holoforge verify soft-wall-vector
```

Run the relevant benchmark or comparison command for scientific changes. Also
inspect the final diff and run `git diff --check`. Changes to scientific
results require synchronized documentation, model records, and tests.

## Git and review

- Keep commits and pull requests limited to one logical change.
- Stage only intended files; never discard unrelated work.
- Do not push, merge, publish, release, or delete branches without explicit
  authorization.
- Before requesting an owner decision, give an item-by-item recommendation,
  reason, scope opened, scope remaining closed, and important uncertainty.
- At an owner gate, also state completed, current, and proposed next stages,
  then offer A-E paths: approve all recommendations, approve selected items,
  request revision or evidence, status walkthrough only, or a custom response.
  Recommend one path and never infer authorization beyond its stated scope.
- When a progress picture is requested, map the actual research project rather
  than HoloForge development. Keep its state and full-size figure project-local;
  embed a dated PDF snapshot in a review packet only when that packet is needed.
