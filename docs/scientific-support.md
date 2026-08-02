# Scientific Support and Review State

HoloForge records two independent labels for a claim:

- **Support level** describes the evidence: `established-source`, `reproduced`,
  `model-extension`, or `hypothesis`.
- **Review state** describes human checking: `unreviewed`, `checked`,
  `approved`, or `rejected`.

For example, a formula copied from a paper can be `established-source` while
still `unreviewed` in HoloForge. A numerical value becomes `reproduced` only
after an identified calculation passes its declared tolerance. Neither label
alone means that nature agrees with the model.

When a claim was generated or materially rewritten by AI, `generated_by_ai`
must be `true`. Human review may change the review state, but must not erase the
provenance.

A claim marked `checked`, `approved`, or `rejected` must also record the human
reviewer's name and review date. This makes scientific approval attributable
without erasing AI assistance.
