# Research-progress snapshots

HoloForge can render one project-local research state as Markdown/Mermaid and
as standalone SVG, PNG, or PDF figures. The JSON state is canonical; figures
are generated views and must be refreshed after a durable research milestone.

The snapshot describes the actual research project: source review, frozen
questions, calculations, verification, stops, owner decisions, and later
branches. It is not a HoloForge software-development chart and is not
background telemetry.

## Figure styles

Set the optional top-level `figure_style` field to one of:

- `compact` — the recommended owner-review and PDF-packet style. It uses a
  clean stage rail, uniform rounded boxes, semantic status colors, a strong
  outline for the current or blocked stage, and dashed boxes for pending or
  skipped work. Group membership remains in the canonical JSON and Mermaid
  view but does not add visual boxes to the standalone figure.
- `grouped` — the original detailed map. It shows group clusters and uses
  different node shapes for tasks, checks, decisions, and outcomes.

Records created before `figure_style` existed remain valid and render with
`grouped`. The checked-in example selects `compact`, so new projects receive
the simpler owner-facing style by default when they copy the example.

Use `layout_direction: "TB"` for a vertical research path and `"LR"` for a
wide map. The compact style is designed first for `TB`, which normally fits a
dedicated progress page in the review-packet template.

## Status language and accessibility

Every node retains a written status as well as a color:

| Semantic status | Compact appearance |
| --- | --- |
| `completed` | pale green with a green border |
| `current` | pale amber with a strong amber border |
| `pending` | pale blue with a dashed blue border |
| `blocked` | pale red with a strong red border |
| `skipped` | pale slate with a dashed slate border |

An optional stage-level `status_label` may refine the displayed wording when
the semantic state remains accurate, for example `"SOURCE STOP"` on a
`blocked` stage or `"PROPOSED"` on a `pending` stage. It must not disguise a
failed or blocked stage as completed.

Stage completion means only that the workflow task is recorded as finished.
It does not increase the scientific-support level of a claim.

## Render from one state

Copy the generic state and replace every example stage with reviewed project
state:

```bash
cp .agents/skills/holoforge-research-gate/assets/research-progress.example.json \
  /path/to/private-project/research-progress.json
```

Then render every view from that same JSON file:

```bash
python .agents/skills/holoforge-research-gate/scripts/render_research_progress.py \
  /path/to/private-project/research-progress.json \
  --output /path/to/private-project/research-progress.md \
  --figure-output /path/to/private-project/research-progress.svg \
  --figure-output /path/to/private-project/research-progress.pdf
```

Markdown rendering needs only Python. Standalone figures require the
maintained Graphviz `dot` program. Keep the SVG as the ordinary full-size view.
Embed the PDF on its own page only when an owner-review packet is already
needed; set `\HoloForgeIncludeProgress`, `\researchprogressfile`, and
`\researchprogressupdated` in
[`review-packet-template.tex`](templates/review-packet-template.tex).

## Privacy boundary

Keep unpublished state and generated figures in the access-controlled research
repository. A generic style or renderer improvement may enter public
HoloForge only after the public-export workflow; candidate identities,
equations, values, outcomes, private paths, and repository history remain
private unless separately cleared for disclosure.
