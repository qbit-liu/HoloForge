#!/usr/bin/env python3
"""Render a project-local HoloForge research-progress snapshot."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any, Mapping, Optional, Sequence


ALLOWED_STAGE_STATUSES = frozenset(
    {"completed", "current", "pending", "blocked", "skipped"}
)
ALLOWED_STAGE_KINDS = frozenset({"task", "check", "decision", "outcome"})
ALLOWED_TRANSITION_KINDS = frozenset({"normal", "advance", "revision", "stop"})
ALLOWED_LAYOUT_DIRECTIONS = frozenset({"LR", "TB"})
ALLOWED_FIGURE_FORMATS = frozenset({"pdf", "png", "svg"})
RESPONSE_IDS = ("A", "B", "C", "D", "E")
ID_PATTERN = re.compile(r"^[a-z][a-z0-9_-]*$")

STATUS_LABELS = {
    "completed": "COMPLETED",
    "current": "CURRENT",
    "pending": "PENDING",
    "blocked": "BLOCKED",
    "skipped": "SKIPPED",
}
STATUS_COLORS = {
    "completed": ("#e7f4ea", "#2f6b3c"),
    "current": ("#fff1c7", "#b7791f"),
    "pending": ("#f1f3f5", "#6b7280"),
    "blocked": ("#fde8e8", "#a33a3a"),
    "skipped": ("#eee9f7", "#72569a"),
}
TRANSITION_STYLES = {
    "normal": ("#475569", "solid", "1.4"),
    "advance": ("#2f6b3c", "bold", "2.0"),
    "revision": ("#b7791f", "dashed", "1.6"),
    "stop": ("#a33a3a", "dashed", "1.6"),
}
DOT_SHAPES = {
    "task": "box",
    "check": "hexagon",
    "decision": "diamond",
    "outcome": "ellipse",
}


class ProgressError(ValueError):
    """Raised when a research-progress record cannot be rendered safely."""


def _require_text(record: Mapping[str, Any], key: str) -> str:
    value = record.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ProgressError(f"{key!r} must be a nonempty string")
    return value.strip()


def _require_text_list(record: Mapping[str, Any], key: str) -> list[str]:
    value = record.get(key)
    if not isinstance(value, list) or not all(
        isinstance(item, str) and item.strip() for item in value
    ):
        raise ProgressError(f"{key!r} must be a list of strings")
    return [item.strip() for item in value]


def _optional_text(record: Mapping[str, Any], key: str) -> str:
    value = record.get(key, "")
    if not isinstance(value, str):
        raise ProgressError(f"{key!r} must be a string when provided")
    return value.strip()


def _validate_groups(state: Mapping[str, Any]) -> set[str]:
    groups = state.get("groups")
    if not isinstance(groups, list) or not groups:
        raise ProgressError("'groups' must be a nonempty list")

    group_ids: set[str] = set()
    for index, group in enumerate(groups):
        if not isinstance(group, dict):
            raise ProgressError(f"groups[{index}] must be an object")
        group_id = _require_text(group, "id")
        _require_text(group, "label")
        if not ID_PATTERN.fullmatch(group_id):
            raise ProgressError(f"group id {group_id!r} must match {ID_PATTERN.pattern}")
        if group_id in group_ids:
            raise ProgressError(f"duplicate group id {group_id!r}")
        group_ids.add(group_id)
    return group_ids


def _validate_stages(state: Mapping[str, Any], group_ids: set[str]) -> set[str]:
    stages = state.get("stages")
    if not isinstance(stages, list) or not stages:
        raise ProgressError("'stages' must be a nonempty list")

    stage_ids: set[str] = set()
    current_ids: list[str] = []
    for index, stage in enumerate(stages):
        if not isinstance(stage, dict):
            raise ProgressError(f"stages[{index}] must be an object")
        stage_id = _require_text(stage, "id")
        _require_text(stage, "label")
        group_id = _require_text(stage, "group")
        kind = _require_text(stage, "kind")
        status = _require_text(stage, "status")
        if not ID_PATTERN.fullmatch(stage_id):
            raise ProgressError(f"stage id {stage_id!r} must match {ID_PATTERN.pattern}")
        if stage_id in stage_ids:
            raise ProgressError(f"duplicate stage id {stage_id!r}")
        if group_id not in group_ids:
            raise ProgressError(f"stage {stage_id!r} uses unknown group {group_id!r}")
        if kind not in ALLOWED_STAGE_KINDS:
            allowed = ", ".join(sorted(ALLOWED_STAGE_KINDS))
            raise ProgressError(f"stage kind {kind!r} is not one of: {allowed}")
        if status not in ALLOWED_STAGE_STATUSES:
            allowed = ", ".join(sorted(ALLOWED_STAGE_STATUSES))
            raise ProgressError(f"stage status {status!r} is not one of: {allowed}")
        stage_ids.add(stage_id)
        if status == "current":
            current_ids.append(stage_id)

    if len(current_ids) != 1:
        raise ProgressError("exactly one stage must have status 'current'")
    if state["current_stage"] != current_ids[0]:
        raise ProgressError("'current_stage' must identify the stage marked 'current'")
    return stage_ids


def _validate_transitions(state: Mapping[str, Any], stage_ids: set[str]) -> None:
    transitions = state.get("transitions")
    if not isinstance(transitions, list) or not transitions:
        raise ProgressError("'transitions' must be a nonempty list")

    seen: set[tuple[str, str, str]] = set()
    for index, transition in enumerate(transitions):
        if not isinstance(transition, dict):
            raise ProgressError(f"transitions[{index}] must be an object")
        source = _require_text(transition, "from")
        target = _require_text(transition, "to")
        label = _optional_text(transition, "label")
        kind = _require_text(transition, "kind")
        constraint = transition.get("constraint", True)
        if source not in stage_ids or target not in stage_ids:
            raise ProgressError(
                f"transition {source!r} -> {target!r} references an unknown stage"
            )
        if source == target:
            raise ProgressError(f"transition {source!r} cannot point to itself")
        if kind not in ALLOWED_TRANSITION_KINDS:
            allowed = ", ".join(sorted(ALLOWED_TRANSITION_KINDS))
            raise ProgressError(f"transition kind {kind!r} is not one of: {allowed}")
        if not isinstance(constraint, bool):
            raise ProgressError("transition 'constraint' must be true or false")
        identity = (source, target, label)
        if identity in seen:
            raise ProgressError(f"duplicate transition {source!r} -> {target!r}")
        seen.add(identity)


def _validate_owner_menu(state: Mapping[str, Any]) -> None:
    awaiting_owner = state.get("awaiting_owner")
    if not isinstance(awaiting_owner, bool):
        raise ProgressError("'awaiting_owner' must be true or false")

    owner_decisions = _require_text_list(state, "owner_decisions")
    response_options = state.get("response_options")
    recommended_option = state.get("recommended_option")
    if awaiting_owner:
        if not owner_decisions:
            raise ProgressError("owner decisions are required while awaiting the owner")
        if not isinstance(response_options, list) or len(response_options) != 5:
            raise ProgressError("owner review requires exactly five response options")
        option_ids: list[str] = []
        for index, option in enumerate(response_options):
            if not isinstance(option, dict):
                raise ProgressError(f"response_options[{index}] must be an object")
            option_ids.append(_require_text(option, "id"))
            _require_text(option, "label")
            _require_text(option, "effect")
        if tuple(option_ids) != RESPONSE_IDS:
            raise ProgressError("response option ids must appear in A, B, C, D, E order")
        if recommended_option not in RESPONSE_IDS:
            raise ProgressError("'recommended_option' must identify one option A-E")
    else:
        if owner_decisions:
            raise ProgressError("owner decisions must be empty when not awaiting the owner")
        if response_options not in (None, []):
            raise ProgressError("response options must be empty when not awaiting the owner")
        if recommended_option is not None:
            raise ProgressError("recommended_option must be null when not awaiting the owner")


def validate_state(state: Any) -> Mapping[str, Any]:
    """Validate the project-level research-progress contract."""

    if not isinstance(state, dict):
        raise ProgressError("the top-level JSON value must be an object")
    for key in (
        "schema_version",
        "research_id",
        "title",
        "current_gate",
        "disclosure",
        "updated_at",
        "layout_direction",
        "current_stage",
        "next_action",
    ):
        _require_text(state, key)
    if state["schema_version"] != "1":
        raise ProgressError("'schema_version' must be '1'")
    if state["layout_direction"] not in ALLOWED_LAYOUT_DIRECTIONS:
        raise ProgressError("'layout_direction' must be 'LR' or 'TB'")

    group_ids = _validate_groups(state)
    stage_ids = _validate_stages(state, group_ids)
    _validate_transitions(state, stage_ids)
    _require_text_list(state, "completed_summary")
    _require_text_list(state, "scope_remaining_closed")
    _validate_owner_menu(state)
    return state


def load_state(path: Path) -> Mapping[str, Any]:
    """Load and validate one UTF-8 JSON research-progress file."""

    try:
        state = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise ProgressError(f"invalid JSON: {error}") from error
    return validate_state(state)


def _mermaid_text(value: str) -> str:
    return (
        value.replace("&", "&amp;")
        .replace('"', "'")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace("\n", "<br/>")
    )


def _markdown_text(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ")


def _dot_text(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")


def _stage_maps(
    state: Mapping[str, Any],
) -> tuple[dict[str, int], dict[str, Mapping[str, Any]]]:
    indexes = {
        stage["id"]: index
        for index, stage in enumerate(state["stages"], start=1)
    }
    records = {stage["id"]: stage for stage in state["stages"]}
    return indexes, records


def _mermaid_node(node_id: str, label: str, kind: str) -> str:
    if kind == "decision":
        return f'  {node_id}{{"{label}"}}'
    if kind == "outcome":
        return f'  {node_id}(["{label}"])'
    return f'  {node_id}["{label}"]'


def render_markdown(state: Mapping[str, Any]) -> str:
    """Return Markdown with a grouped Mermaid research-progress graph."""

    validate_state(state)
    indexes, stages = _stage_maps(state)
    current = stages[state["current_stage"]]
    lines = [
        "<!-- Generated by render_research_progress.py; edit the JSON state. -->",
        f"# Research progress: {state['title']}",
        "",
        "| Field | Current value |",
        "| --- | --- |",
        f"| Research | `{_markdown_text(state['research_id'])}` |",
        f"| Current gate | {_markdown_text(state['current_gate'])} |",
        f"| Current stage | {_markdown_text(current['label'])} |",
        f"| Disclosure | {_markdown_text(state['disclosure'])} |",
        f"| Updated | {_markdown_text(state['updated_at'])} |",
        f"| Awaiting owner | {'Yes' if state['awaiting_owner'] else 'No'} |",
        "",
        "## Research workflow position",
        "",
        "```mermaid",
        f"flowchart {state['layout_direction']}",
    ]

    for group_index, group in enumerate(state["groups"], start=1):
        lines.append(
            f'  subgraph group_{group_index}["{_mermaid_text(group["label"])}"]'
        )
        for stage in state["stages"]:
            if stage["group"] != group["id"]:
                continue
            node_id = f"stage_{indexes[stage['id']]}"
            status = stage["status"]
            label = (
                f"{_mermaid_text(stage['label'])}<br/>"
                f"[{STATUS_LABELS[status]}]"
            )
            lines.append(_mermaid_node(node_id, label, stage["kind"]))
        lines.append("  end")

    for transition in state["transitions"]:
        source = f"stage_{indexes[transition['from']]}"
        target = f"stage_{indexes[transition['to']]}"
        label = _optional_text(transition, "label")
        if label:
            lines.append(f"  {source} -->|{_mermaid_text(label)}| {target}")
        else:
            lines.append(f"  {source} --> {target}")

    for stage in state["stages"]:
        node_id = f"stage_{indexes[stage['id']]}"
        lines.append(f"  class {node_id} {stage['status']}")
    lines.extend(
        [
            "  classDef completed fill:#e7f4ea,stroke:#2f6b3c,color:#17211a",
            "  classDef current fill:#fff1c7,stroke:#b7791f,color:#2a2113,stroke-width:3px",
            "  classDef pending fill:#f1f3f5,stroke:#6b7280,color:#252a31",
            "  classDef blocked fill:#fde8e8,stroke:#a33a3a,color:#2b1717",
            "  classDef skipped fill:#eee9f7,stroke:#72569a,color:#211a2b",
            "```",
            "",
            "> A completed stage means the recorded workflow task is finished. It does",
            "> not by itself raise the scientific-support level of any claim.",
            "",
            "## What is done",
            "",
        ]
    )
    lines.extend(f"- {item}" for item in state["completed_summary"])
    lines.extend(
        [
            "",
            "## What happens next",
            "",
            state["next_action"],
            "",
            "## Scope remaining closed",
            "",
        ]
    )
    lines.extend(f"- {item}" for item in state["scope_remaining_closed"])

    if state["awaiting_owner"]:
        lines.extend(["", "## Waiting for owner", ""])
        lines.extend(
            f"{index}. {decision}"
            for index, decision in enumerate(state["owner_decisions"], start=1)
        )
        lines.extend(
            [
                "",
                "### Response options",
                "",
                "| Option | Meaning | Effect |",
                "| --- | --- | --- |",
            ]
        )
        for option in state["response_options"]:
            marker = (
                " **(Recommended)**"
                if option["id"] == state["recommended_option"]
                else ""
            )
            lines.append(
                f"| {option['id']}{marker} | {_markdown_text(option['label'])} | "
                f"{_markdown_text(option['effect'])} |"
            )

    lines.extend(
        [
            "",
            "> This is an agent-updated research snapshot, not background telemetry.",
            "> GitHub shows the latest committed and pushed snapshot; unpublished",
            "> project snapshots remain in the private research repository.",
            "",
        ]
    )
    return "\n".join(lines)


def render_dot(state: Mapping[str, Any]) -> str:
    """Return Graphviz DOT for a publication-quality progress figure."""

    validate_state(state)
    indexes, _ = _stage_maps(state)
    title = _dot_text(state["title"])
    subtitle = _dot_text(
        f"Current gate: {state['current_gate']} | Updated: {state['updated_at']} | "
        f"Disclosure: {state['disclosure']}"
    )
    lines = [
        "digraph research_progress {",
        "  graph [",
        f'    rankdir="{state["layout_direction"]}",',
        '    bgcolor="#ffffff",',
        '    fontname="Helvetica",',
        '    fontsize="18",',
        '    labelloc="t",',
        f'    label="{title}\\n{subtitle}",',
        '    pad="0.20",',
        '    nodesep="0.32",',
        '    ranksep="0.60",',
        '    newrank="true",',
        '    splines="spline"',
        "  ];",
        "  node [",
        '    style="rounded,filled",',
        '    fontname="Helvetica",',
        '    fontsize="10",',
        '    margin="0.13,0.08",',
        '    color="#6b7280",',
        '    fontcolor="#1f2937",',
        '    penwidth="1.3"',
        "  ];",
        "  edge [",
        '    fontname="Helvetica",',
        '    fontsize="8.5",',
        '    color="#475569",',
        '    fontcolor="#334155",',
        '    arrowsize="0.72",',
        '    penwidth="1.4"',
        "  ];",
    ]

    for group_index, group in enumerate(state["groups"], start=1):
        lines.extend(
            [
                f"  subgraph cluster_{group_index} {{",
                f'    label="{_dot_text(group["label"])}";',
                '    color="#cbd5e1";',
                '    fontcolor="#334155";',
                '    fontname="Helvetica";',
                '    fontsize="11";',
                '    style="rounded";',
                '    penwidth="1.0";',
            ]
        )
        for stage in state["stages"]:
            if stage["group"] != group["id"]:
                continue
            node_id = f"stage_{indexes[stage['id']]}"
            fill, stroke = STATUS_COLORS[stage["status"]]
            penwidth = "3.0" if stage["status"] == "current" else "1.3"
            shape = DOT_SHAPES[stage["kind"]]
            style = (
                "filled"
                if stage["kind"] in {"decision", "outcome"}
                else "rounded,filled"
            )
            label = _dot_text(
                f"{stage['label']}\n[{STATUS_LABELS[stage['status']]}]"
            )
            lines.append(
                f'    {node_id} [label="{label}", shape="{shape}", '
                f'style="{style}", fillcolor="{fill}", color="{stroke}", '
                f'penwidth="{penwidth}"];'
            )
        lines.append("  }")

    for transition in state["transitions"]:
        source = f"stage_{indexes[transition['from']]}"
        target = f"stage_{indexes[transition['to']]}"
        color, style, penwidth = TRANSITION_STYLES[transition["kind"]]
        attributes = [
            f'color="{color}"',
            f'fontcolor="{color}"',
            f'style="{style}"',
            f'penwidth="{penwidth}"',
        ]
        label = _optional_text(transition, "label")
        if label:
            attributes.append(f'label="{_dot_text(label)}"')
        if transition.get("constraint", True) is False:
            attributes.append('constraint="false"')
        lines.append(f"  {source} -> {target} [{', '.join(attributes)}];")

    lines.append("}")
    return "\n".join(lines) + "\n"


def render_figure(dot_source: str, output: Path) -> None:
    """Use the maintained Graphviz layout engine for SVG, PNG, or PDF."""

    figure_format = output.suffix.lower().lstrip(".")
    if figure_format not in ALLOWED_FIGURE_FORMATS:
        allowed = ", ".join(sorted(ALLOWED_FIGURE_FORMATS))
        raise ProgressError(f"figure output must use one of: {allowed}")
    dot = shutil.which("dot")
    if dot is None:
        raise ProgressError(
            "Graphviz 'dot' is required for standalone SVG, PNG, or PDF output"
        )
    graphviz_format = "png:cairo" if figure_format == "png" else figure_format
    completed = subprocess.run(
        [dot, f"-T{graphviz_format}", "-o", str(output)],
        input=dot_source,
        check=False,
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0:
        message = completed.stderr.strip().splitlines()
        detail = message[-1] if message else "unknown Graphviz error"
        raise ProgressError(f"Graphviz rendering failed: {detail}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Render a validated HoloForge research-progress snapshot."
    )
    parser.add_argument("state", type=Path, help="UTF-8 JSON progress-state file")
    parser.add_argument(
        "--output",
        type=Path,
        help="write Markdown/Mermaid to this path instead of standard output",
    )
    parser.add_argument("--dot-output", type=Path, help="write Graphviz DOT here")
    parser.add_argument(
        "--figure-output",
        action="append",
        default=[],
        type=Path,
        help="render a standalone .svg, .png, or .pdf; may be repeated",
    )
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        state = load_state(args.state)
        markdown = render_markdown(state)
        dot_source = render_dot(state)
        produced_output = False
        if args.output is not None:
            args.output.write_text(markdown, encoding="utf-8")
            produced_output = True
        if args.dot_output is not None:
            args.dot_output.write_text(dot_source, encoding="utf-8")
            produced_output = True
        for figure_output in args.figure_output:
            render_figure(dot_source, figure_output)
            produced_output = True
        if not produced_output:
            print(markdown, end="")
    except (OSError, ProgressError) as error:
        print(f"progress error: {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
