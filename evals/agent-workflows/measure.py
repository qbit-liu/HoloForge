"""Summarize explicitly supplied Codex JSONL logs without exposing their text.

This parser targets the telemetry observed in the recorded pilot. Missing usage
is unavailable. It does not estimate billing or inspect any default log folder.
"""

from __future__ import annotations

import argparse
from datetime import datetime
import hashlib
import json
from pathlib import Path


USAGE_KEYS = (
    "input_tokens", "cached_input_tokens", "cache_write_input_tokens",
    "output_tokens", "reasoning_output_tokens", "total_tokens",
)


def summarize(records):
    responses, starts, ends, calls, settings = {}, {}, {}, set(), set()
    last_cumulative = None
    for index, record in enumerate(records):
        payload = record.get("payload", {})
        kind = record.get("type")
        if kind == "turn_context":
            settings.add((payload.get("model"), payload.get("effort")))
        elif kind == "token_usage_record":
            identifier, usage = payload.get("response_id"), payload.get("usage")
            if not identifier or not isinstance(usage, dict):
                raise ValueError("Token record lacks response identity or usage")
            if identifier in responses and responses[identifier] != usage:
                raise ValueError("Conflicting usage for the same response")
            responses[identifier] = usage
            last_cumulative = payload.get("thread_token_usage")
        elif kind == "event_msg":
            identifier = payload.get("turn_id")
            if payload.get("type") == "task_started":
                starts[identifier] = record["timestamp"]
            elif payload.get("type") == "task_complete":
                ends[identifier] = (record["timestamp"], payload.get("duration_ms"))
        elif kind == "response_item" and payload.get("type") in ("function_call", "custom_tool_call"):
            calls.add(payload.get("call_id") or payload.get("id") or str(index))

    totals = None
    if responses and all(all(key in value for key in USAGE_KEYS) for value in responses.values()):
        if not all(type(value[key]) is int and value[key] >= 0 for value in responses.values() for key in USAGE_KEYS):
            raise ValueError("Invalid runtime token count")
        totals = {key: sum(value[key] for value in responses.values()) for key in USAGE_KEYS}
        if last_cumulative is not None and any(last_cumulative.get(key) != totals[key] for key in USAGE_KEYS):
            raise ValueError("Per-response usage disagrees with cumulative thread usage")
        if totals["cached_input_tokens"] > totals["input_tokens"]:
            raise ValueError("Cached input exceeds total input")
        totals["uncached_input_tokens"] = totals["input_tokens"] - totals["cached_input_tokens"]

    duration = None
    if ends and all(type(value[1]) is int and value[1] >= 0 for value in ends.values()):
        duration = sum(value[1] for value in ends.values()) / 1000
    return {
        "runtime_settings": [{"model": model, "effort": effort} for model, effort in sorted(settings, key=str)],
        "complete": bool(starts) and starts.keys() == ends.keys(),
        "turns_started": len(starts), "turns_completed": len(ends),
        "first_started": min(starts.values()) if starts else None,
        "last_completed": max(value[0] for value in ends.values()) if ends else None,
        "sum_turn_seconds": duration, "top_level_tool_calls": len(calls),
        "response_count": len(responses), "tokens": totals,
    }


def measure(path):
    raw = path.read_bytes()
    result = summarize([json.loads(line) for line in raw.decode().splitlines() if line.strip()])
    result["source_sha256"] = hashlib.sha256(raw).hexdigest()
    return result


def aggregate(rows):
    complete = bool(rows) and all(row["complete"] for row in rows)
    seconds = None
    if complete:
        start = min(row["first_started"] for row in rows)
        end = max(row["last_completed"] for row in rows)
        seconds = (datetime.fromisoformat(end.replace("Z", "+00:00")) - datetime.fromisoformat(start.replace("Z", "+00:00"))).total_seconds()
    keys = (*USAGE_KEYS, "uncached_input_tokens")
    tokens = ({key: sum(row["tokens"][key] for row in rows) for key in keys}
              if rows and all(row["tokens"] is not None for row in rows) else None)
    duration = (sum(row["sum_turn_seconds"] for row in rows)
                if rows and all(row["sum_turn_seconds"] is not None for row in rows) else None)
    return {
        "complete": complete, "roles": len(rows),
        "turns": sum(row["turns_completed"] for row in rows),
        "cohort_elapsed_seconds": seconds, "sum_turn_seconds": duration,
        "top_level_tool_calls": sum(row["top_level_tool_calls"] for row in rows),
        "tokens": tokens,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("logs", type=Path, nargs="+")
    args = parser.parse_args()
    try:
        rows = [measure(path) for path in args.logs]
        result = {"roles": rows, "aggregate": aggregate(rows)}
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(json.dumps({"error": str(exc)}))
        return 2
    print(json.dumps(result, indent=2))
    return 0 if result["aggregate"]["complete"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
