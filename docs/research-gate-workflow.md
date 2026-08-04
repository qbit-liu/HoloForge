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
   implementation, numerical verdict, evidence boundary, and next action.
7. **Decision record and commit:** after human approval, record what was
   accepted and what remains closed, then commit one logical reviewed gate.

If a stop condition fires, stop the gate, preserve the negative result, and
return to owner review. Do not expand the scope to rescue the hypothesis.

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
- a hostile critic section followed by the exact owner decisions; and
- a footer reiterating the disclosure boundary.

The reusable source is
[`docs/templates/review-packet-template.tex`](templates/review-packet-template.tex).
Compile twice, inspect the log for layout warnings, render every page to an
image, and visually check clipping, overlaps, equations, tables, plots,
headers, and page numbers before delivery.

## Public contribution boundary

Public HoloForge may receive the generic workflow, reusable framework
improvements, or a separately reviewed reproduction package. It must not
receive unpublished candidate identities, private literature notes, working
equations, intermediate results, local paths, confidential correspondence, or
the private repository's history.
