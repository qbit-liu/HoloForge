# HoloForge research-acceleration implementation brief — Version 3

This brief scopes the first public implementation batch. It supplements, and
does not replace, `AGENTS.md`, `CONSTITUTION.md`, the Version 0.5 compatibility
policy, or the repository skills.

The batch was intentionally result-neutral. Any qualified-route pilot language
in the associated planning record is a bounded first-pilot tactic, not a
general Explore admission rule. The current research-selection authority is
`docs/research-objective.md`: assess scientific opportunity first, let the
named human owner decide value and investment, and then choose open discovery,
strategic development, or short-horizon execution.

## Objective

Make HoloForge's existing verification and evidence boundaries fail closed
without changing any accepted physical result. Then return to the owner before
opening a private research pilot or a Version 0.6 research-runtime design.

## Authorized public batch

1. Harden `AcceptanceCheck`, `VerificationRecord`, and `BenchmarkExecution` so
   empty, non-boolean, non-finite, reserved-field, or contradictory states are
   rejected.
2. Require explicit support and pass/check consistency before writing an
   evidence bundle.
3. Stage bundle content outside the destination, reject symbolic artifact
   inputs, and publish the completed bundle only after every record and digest
   succeeds.
4. Audit semantic consistency among the manifest and the three canonical
   records, not only their file hashes.
5. Make every CLI JSON path reject non-finite values with controlled exit `2`.
6. Extend the privacy-safe runtime fingerprint without recording private paths,
   hostnames, usernames, secrets, or environment variables.
7. Add the research objective and update the public roadmap without naming a
   private candidate.

## Explicitly outside this batch

- scientific equations, solver choices, defaults, tolerances, or results;
- hypothesis-card Version 0.2;
- research-question, study, uncertainty, or readiness schemas;
- `holoforge research` commands;
- a private candidate or physical discriminator;
- benchmark-specific backend repair;
- multi-agent orchestration;
- commit, push, merge, release, branch deletion, or disclosure.

## Required validation

- focused contract, registry, CLI, evidence, schema, privacy, and provenance
  tests;
- existing full unit-test suite;
- every current verifier required by the repository validation contract;
- strict JSON and evidence-bundle relocation/audit checks;
- public-export scan of every new public document;
- `git diff --check` and a complete final diff review.

The batch is complete only when existing valid commands retain their meanings,
invalid scientific states fail closed, no private material is present, and the
owner receives a fresh itemized review before any Git or release action.
