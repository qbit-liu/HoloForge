# Learning From Every Research Result

A research gate is useful even when it stops a hypothesis. HoloForge therefore
preserves both the evidence and a short closure retrospective for every closed
Explore gate. This rule applies to positive, negative, inconclusive,
conditional, source-stopped, prior-art-stopped, and technically stopped gates.

The retrospective is not a substitute for the result record. The result says
what the frozen gate established. The retrospective says how that bounded
experience should improve later candidate selection, contracts, methods, or
verification.

## Required evidence layers

A closed gate should retain the artifacts appropriate to its scope:

1. the frozen contract and source record;
2. code, configuration, environment metadata, tests, and machine-readable
   evidence when calculation was authorized;
3. the outcome-first result record, including limitations and explicit
   non-claims;
4. hostile criticism and owner review;
5. the recorded owner decision and progress-state update;
6. a closure retrospective; and
7. a scoped Git commit.

Do not delete a failed check because a later method works. That failure may be
the evidence that distinguishes a fragile representation from a reliable one.
Likewise, do not call an unavailable source, an ill-conditioned norm, or a
solver failure a physical negative result.

## Outcome classes

Choose one primary class and explain any secondary class:

- **positive:** the preregistered positive endpoint passed within its evidence
  boundary;
- **negative:** the preregistered physical negative endpoint passed;
- **inconclusive:** the evidence lies between declared endpoints;
- **conditional:** a bounded subtest passed, but a named prerequisite for the
  proposed claim remains open;
- **source stop:** required public or authorized inputs are missing or
  internally unresolved;
- **prior-art stop:** the proposed novelty target is already covered or needs
  material narrowing;
- **technical stop:** the frozen representation, numerical method, or
  verification contract failed without deciding the physical question.

These labels describe the gate, not the value of the research effort.

## Closure retrospective

Copy [`research-retrospective-template.md`](templates/research-retrospective-template.md)
into the research project when a gate closes. Record:

- the accepted outcome class and evidence links;
- what held, what failed, and the strongest unresolved alternative;
- the scientific, numerical, and workflow lessons;
- what must not be inferred;
- one concrete change, if any, to future intake or gate design; and
- the evidence required to reopen the direction.

Lessons feed forward. They may change how future candidates are scored or how
new contracts are written, but they must not retroactively change a frozen
contract, acceptance threshold, support label, or owner decision.

For a portfolio with several private directions, maintain a private index of
retrospectives so a later intake can find recurring failure modes. Keep the
index claim-bounded: link the primary records instead of replacing them with a
story about what “probably” happened.

## Privacy and public export

An unpublished retrospective remains in the separate private research
repository with its project identities, literature notes, calculations, and
results. Do not copy that ledger into public HoloForge.

Only generic workflow improvements, sanitized templates, or separately
disclosure-approved reproduction artifacts may be proposed publicly, and each
proposal must pass the public-export workflow. Learning from a private result
does not authorize disclosing that result.
