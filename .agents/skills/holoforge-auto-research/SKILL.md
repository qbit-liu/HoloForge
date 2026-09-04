---
name: holoforge-auto-research
description: Run or prepare a governed end-to-end HoloForge Explore campaign in which an agent may generate and select research candidates, execute derivations and code, verify evidence, pivot within a frozen budget, and assemble a paper-and-code package without routine human choices. Use for true auto mode, autonomous paper-seeking research, unattended HoloForge campaigns, or auditing such a campaign. Do not use it to guarantee publication, change the public framework, manufacture human approval, submit or disclose work, or bypass the research-gate workflow.
---

# HoloForge Auto Research

Use this skill as the campaign-level controller above repeated
`holoforge-research-gate` runs. Read `CONSTITUTION.md`, `AGENTS.md`,
`docs/autonomous-research-workflow.md`, `docs/private-research-workflow.md`, and
`docs/research-gate-workflow.md` before preparing or running a campaign.

The mode is autonomous execution, not guaranteed success. Its terminal product
is either a submission-ready **candidate** package with paper, code, evidence,
and reproduction instructions, or an equally complete audited stop package.

## Establish the campaign before research

1. Work in a dedicated access-controlled research repository. Treat the pinned
   public HoloForge checkout as read-only.
2. Copy the three JSON examples in `assets/` into the private project. Replace
   their synthetic content without copying unpublished material back here.
3. Freeze the mission: research envelope, success definition, claim-sufficiency
   criteria, delegated decisions, budgets, roles, no-touch boundary, terminal
   outcomes, and exact HoloForge commit.
4. Run `scripts/validate_autonomous_campaign.py MISSION --framework-root PATH`.
5. Obtain one explicit owner authorization for that exact mission. Do not infer
   authorization from a conversational preference for the recommended option.

The authorization may delegate candidate generation, candidate selection,
routine gate transitions, bounded revisions, candidate pivots, local execution,
and local commits. It never delegates threshold changes, scientific review
labels, publication or disclosure decisions, external communication, remote Git
actions, secret access, or changes to HoloForge.

## Use separated agent roles

Use one coordinator as the sole canonical writer. Give the other roles read-only
access to immutable snapshots or evidence bundles:

- a director/coordinator maintains the mission, state, candidate ledger, and
  terminal package;
- a literature and prior-art auditor searches sources and challenges novelty;
- a theory/numerics executor derives, implements, and tests the frozen claim;
- an independent verifier/hostile critic reproduces results and attacks the
  interpretation.

Do not let multiple agents edit the same checkout or approve one another's
claims. A single agent may fill several roles only when the mission records the
loss of independence.

## Run the autonomous loop

Follow the state machine and evidence requirements in
`references/campaign-workflow.md`:

1. Search broadly inside the frozen portfolio envelope.
2. Screen candidates using scientific opportunity before execution readiness.
3. Select the strongest candidate that satisfies the frozen selection policy.
4. Freeze and execute a bounded research gate.
5. Separate fast discovery from independent confirmation.
6. Reproduce, criticize, and package the result.
7. Follow the coordinator's recorded recommendation automatically only when the
   transition is delegated, legal, within budget, and leaves all thresholds and
   contracts unchanged.
8. If the candidate stops, preserve it and pivot only while the mission's
   candidate and pivot budgets remain. Never hide failed candidates.

Before launch, after every durable transition, before resuming, and before the
terminal handoff, validate the mission, state, and package. Keep their canonical
JSON hashes in the state and package.

## Enforce the no-touch boundary

Read `references/no-touch-policy.md`. Stop immediately when an action would:

- modify the pinned HoloForge checkout or another research project;
- rewrite a frozen question, discriminator, threshold, exclusion, or budget;
- delete, overwrite, or conceal raw evidence or stopped candidates;
- assign human-reviewed, novelty-confirmed, or publication-authorized status;
- exceed a source, compute, storage, repair, candidate, pivot, or wall-time cap;
- access undeclared secrets, accounts, global configuration, or system paths;
- push, merge, release, submit, publish, message a person, purchase, or create a
  continuing external service.

Return to the owner with the exact blocker. Do not substitute a weaker question
or threshold to keep the run alive.

## Finish with an audited terminal package

The coordinator must return:

- the frozen mission, complete state and candidate ledger, source ledger, raw
  and processed evidence, code, tests, environment lock, and reproduction log;
- a manuscript and figures only when the claim survived confirmation and
  hostile review, otherwise an explicit `not-produced` manuscript status;
- claim, non-claim, limitation, provenance, budget, and artifact-hash records;
- one allowed terminal outcome from the workflow, with stopped candidates and
  negative evidence preserved; and
- an owner handoff that distinguishes submission readiness from the still-open
  human decisions on scientific judgment, authorship, disclosure, and submission.

Run the validator one final time. Never describe its pass as peer review,
novelty certification, empirical validation of nature, or publication approval.
