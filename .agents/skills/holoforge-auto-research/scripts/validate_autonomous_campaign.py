#!/usr/bin/env python3
"""Validate HoloForge autonomous-research mission, state, and package records.

The script uses only the Python standard library so the preflight remains
available before project dependencies are installed. JSON Schema tests in the
public repository separately check the full structural contracts.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from datetime import date
from pathlib import Path, PurePosixPath
from typing import Any


DELEGATED_DECISIONS = {
    "candidate_generation",
    "candidate_selection",
    "gate_transition",
    "bounded_revision",
    "candidate_pivot",
    "local_execution",
    "local_commit",
}
FORBIDDEN_ACTIONS = {
    "modify-framework",
    "modify-other-project",
    "change-frozen-contract",
    "relax-threshold",
    "erase-evidence",
    "assign-human-review",
    "access-undeclared-secret",
    "external-communication",
    "remote-git-action",
    "publication-or-submission",
    "purchase-or-account-action",
    "persistent-system-change",
}
TERMINAL_OUTCOMES = {
    "submission-ready-candidate",
    "no-publishable-result-within-budget",
    "source-stop",
    "prior-art-stop",
    "technical-stop",
    "budget-stop",
    "policy-stop",
    "owner-return",
}
OWNER_DECISIONS = {"scientific-verdict", "authorship", "disclosure", "submission"}
ROLE_ACCESS = {
    "coordinator": "canonical",
    "literature-auditor": "read-only",
    "theory-numerics-executor": "read-only",
    "verifier-critic": "read-only",
}
FORWARD = {
    "initialized": {"searching"},
    "searching": {"screening"},
    "screening": {"selected", "searching"},
    "selected": {"discovery"},
    "discovery": {"confirmation", "searching"},
    "confirmation": {"verification", "searching"},
    "verification": {"critique", "searching"},
    "critique": {"packaging", "searching"},
    "packaging": {"awaiting-owner"},
    "awaiting-owner": set(),
    "terminal": set(),
}
BUDGET_MAP = {
    "sources": "source_limit",
    "construction_hours": "construction_hours",
    "compute_hours": "compute_hours",
    "wall_time_hours": "wall_time_hours",
    "storage_gb": "storage_gb",
    "candidates": "candidate_limit",
    "pivots": "pivot_limit",
}


class ValidationError(ValueError):
    """Raised for a fail-closed campaign contract violation."""


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValidationError(f"cannot read valid JSON record: {path.name}") from exc
    if not isinstance(value, dict):
        raise ValidationError(f"record must be a JSON object: {path.name}")
    return value


def canonical_sha256(value: dict[str, Any]) -> str:
    encoded = json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValidationError(message)


def safe_relative_path(value: Any, label: str) -> str:
    require(isinstance(value, str) and bool(value.strip()), f"{label} must be nonempty")
    require("\\" not in value, f"{label} must use portable forward slashes")
    require(value not in {".", ".."}, f"{label} must name a scoped path")
    require(not value.startswith("~"), f"{label} must not use home expansion")
    path = PurePosixPath(value)
    require(not path.is_absolute(), f"{label} must be relative")
    require(".." not in path.parts, f"{label} must not escape its root")
    require(not (len(value) >= 2 and value[1] == ":"), f"{label} must not use a drive path")
    return value.rstrip("/")


def under(path: str, root: str) -> bool:
    return path == root or path.startswith(root + "/")


def validate_mission(mission: dict[str, Any]) -> None:
    require(mission.get("schema_version") == "0.1", "unsupported mission schema")
    require(mission.get("mode") == "autonomous-explore", "mission mode must be autonomous-explore")
    require(mission.get("maturity") == "experimental", "auto mode must remain experimental")
    require(mission.get("status") in {"draft", "owner-authorized", "closed"}, "invalid mission status")

    authorization = mission.get("authorization", {})
    require(isinstance(authorization, dict), "authorization must be an object")
    delegated = authorization.get("delegated_decisions", [])
    require(isinstance(delegated, list), "delegated_decisions must be an array")
    require(set(delegated) <= DELEGATED_DECISIONS, "mission contains an unknown delegated decision")
    if mission.get("status") == "owner-authorized":
        require(bool(authorization.get("authorized_on")), "authorized mission requires authorized_on")
        require(bool(authorization.get("expires_on")), "authorized mission requires expires_on")
        try:
            authorized_on = date.fromisoformat(authorization["authorized_on"])
            expires_on = date.fromisoformat(authorization["expires_on"])
        except (TypeError, ValueError) as exc:
            raise ValidationError("authorization dates must use ISO YYYY-MM-DD") from exc
        require(expires_on >= authorized_on, "mission expiry cannot precede authorization")
        require(date.today() <= expires_on, "owner authorization has expired")
    if authorization.get("local_commit_allowed"):
        require("local_commit" in delegated, "local commits require local_commit delegation")

    framework = mission.get("pinned_framework", {})
    require(framework.get("name") == "HoloForge", "pinned framework must be HoloForge")
    require(framework.get("write_policy") == "read-only", "framework write policy must be read-only")
    require(framework.get("require_clean") is True, "framework clean check must be required")
    commit = framework.get("commit", "")
    require(isinstance(commit, str) and len(commit) == 40 and all(c in "0123456789abcdef" for c in commit), "framework commit must be a full lowercase Git SHA")

    workspace = mission.get("workspace", {})
    require(workspace.get("canonical_writer") == "coordinator", "coordinator must be the canonical writer")
    allowed = [safe_relative_path(value, "allowed write root") for value in workspace.get("allowed_write_roots", [])]
    forbidden = [safe_relative_path(value, "forbidden path") for value in workspace.get("forbidden_paths", [])]
    require(bool(allowed), "at least one allowed write root is required")
    require(bool(forbidden), "at least one forbidden path is required")
    for path in allowed:
        require(not any(under(path, item) or under(item, path) for item in forbidden), "allowed and forbidden paths must not overlap")

    roles = mission.get("roles", [])
    require(isinstance(roles, list), "roles must be an array")
    role_map = {item.get("role"): item.get("write_access") for item in roles if isinstance(item, dict)}
    require(role_map == ROLE_ACCESS and len(roles) == len(ROLE_ACCESS), "roles must contain one canonical coordinator and three read-only independent roles")
    for role in roles:
        require(bool(role.get("model")), "every role must record its model")
        require(bool(role.get("reasoning_effort")), "every role must record its reasoning effort")

    external = mission.get("external_actions", {})
    require(set(external.get("forbidden", [])) == FORBIDDEN_ACTIONS, "mission must forbid every required no-touch action")
    require(set(mission.get("terminal_outcomes", [])) == TERMINAL_OUTCOMES, "mission must preserve every honest terminal outcome")

    budgets = mission.get("budgets", {})
    for limit in BUDGET_MAP.values():
        value = budgets.get(limit)
        require(isinstance(value, (int, float)) and not isinstance(value, bool) and value >= 0, f"invalid budget: {limit}")
    require(budgets.get("candidate_limit", 0) >= 1, "candidate_limit must be positive")
    require(budgets.get("source_limit", 0) >= 1, "source_limit must be positive")
    require(budgets.get("compute_hours", 0) > 0, "compute_hours must be positive")
    require(budgets.get("wall_time_hours", 0) > 0, "wall_time_hours must be positive")
    require(budgets.get("storage_gb", 0) > 0, "storage_gb must be positive")

    contract = mission.get("scientific_contract", {})
    require(contract.get("threshold_policy") == "frozen-no-relaxation", "thresholds must be frozen without relaxation")
    require(contract.get("independent_confirmation") is True, "independent confirmation must be required")
    require(bool(contract.get("claim_sufficiency")), "claim-sufficiency criteria are required")
    require(bool(contract.get("physical_discriminator")), "a physical discriminator is required")
    require(bool(mission.get("deliverables")), "terminal deliverables are required")


def legal_transition(before: str, after: str) -> bool:
    if after == "terminal" and before != "terminal":
        return True
    return after in FORWARD.get(before, set())


def validate_state(mission: dict[str, Any], state: dict[str, Any]) -> None:
    require(state.get("schema_version") == "0.1", "unsupported state schema")
    require(state.get("mission_id") == mission.get("mission_id"), "state mission_id mismatch")
    require(state.get("mission_sha256") == canonical_sha256(mission), "state mission hash mismatch")
    require(state.get("framework_commit") == mission["pinned_framework"]["commit"], "state framework commit mismatch")

    used = state.get("budgets_used", {})
    limits = mission["budgets"]
    for used_name, limit_name in BUDGET_MAP.items():
        value = used.get(used_name)
        require(isinstance(value, (int, float)) and not isinstance(value, bool) and value >= 0, f"invalid used budget: {used_name}")
        require(value <= limits[limit_name], f"budget exceeded: {used_name}")

    candidates = state.get("candidate_ledger", [])
    require(isinstance(candidates, list), "candidate_ledger must be an array")
    ids = [item.get("candidate_id") for item in candidates if isinstance(item, dict)]
    require(len(ids) == len(candidates) == len(set(ids)), "candidate identifiers must be unique")
    require(used.get("candidates") == len(candidates), "used candidate count must match the ledger")
    for candidate in candidates:
        require(candidate.get("repairs_used", -1) <= limits["repair_limit_per_candidate"], "candidate repair budget exceeded")

    transitions = state.get("transitions", [])
    require(isinstance(transitions, list), "transitions must be an array")
    delegated = set(mission["authorization"]["delegated_decisions"])
    current = "initialized"
    pivot_count = 0
    for index, transition in enumerate(transitions, start=1):
        require(transition.get("sequence") == index, "transition sequence must be contiguous")
        require(transition.get("from") == current, "transition chain is discontinuous")
        after = transition.get("to")
        require(legal_transition(current, after), f"illegal transition: {current} -> {after}")
        decision = transition.get("delegated_decision")
        require(decision in delegated, f"transition uses undelegated decision: {decision}")
        require(bool(transition.get("recommendation")), "transition recommendation is required")
        require(bool(transition.get("reason")), "transition reason is required")
        for path in transition.get("evidence_refs", []):
            safe_relative_path(path, "transition evidence path")
        if after == "searching" and current != "initialized":
            require(decision == "candidate_pivot", "return to searching requires candidate_pivot")
            pivot_count += 1
        current = after
    require(state.get("phase") == current, "state phase must equal the last transition target")
    require(used.get("pivots") == pivot_count, "used pivot count must match transitions")

    outcome = state.get("terminal_outcome")
    if current == "terminal":
        require(outcome in TERMINAL_OUTCOMES, "terminal phase requires an allowed outcome")
    else:
        require(outcome is None, "nonterminal phase cannot have a terminal outcome")

    allowed = [safe_relative_path(value, "allowed write root") for value in mission["workspace"]["allowed_write_roots"]]
    forbidden = [safe_relative_path(value, "forbidden path") for value in mission["workspace"]["forbidden_paths"]]
    for value in state.get("touched_paths", []):
        path = safe_relative_path(value, "touched path")
        require(any(under(path, root) for root in allowed), "touched path is outside allowed write roots")
        require(not any(under(path, root) for root in forbidden), "touched path enters a forbidden root")


def validate_package(mission: dict[str, Any], state: dict[str, Any], package: dict[str, Any]) -> None:
    require(state.get("phase") == "terminal", "terminal package requires terminal state")
    require(package.get("schema_version") == "0.1", "unsupported package schema")
    require(package.get("mission_id") == mission.get("mission_id"), "package mission_id mismatch")
    require(package.get("mission_sha256") == canonical_sha256(mission), "package mission hash mismatch")
    require(package.get("state_sha256") == canonical_sha256(state), "package state hash mismatch")
    outcome = package.get("outcome")
    require(outcome == state.get("terminal_outcome"), "package outcome mismatch")
    require(package.get("framework_clean") is True, "package must record a clean pinned framework")
    require(package.get("external_actions_performed") is False, "package cannot close after an external action")
    require(set(package.get("owner_decisions_remaining", [])) == OWNER_DECISIONS, "human scientific, authorship, disclosure, and submission decisions must remain open")

    for product_name in ("manuscript", "code"):
        product = package.get(product_name, {})
        if product.get("path") is not None:
            safe_relative_path(product["path"], f"{product_name} path")
    for artifact in package.get("artifacts", []):
        safe_relative_path(artifact.get("path"), "artifact path")
    for claim in package.get("claims", []):
        for path in claim.get("evidence_refs", []):
            safe_relative_path(path, "claim evidence path")
        review_status = claim.get("review_status")
        if review_status != "unreviewed":
            require(bool(claim.get("reviewed_by")) and bool(claim.get("reviewed_on")), "non-unreviewed claims require human reviewer metadata")

    if outcome == "submission-ready-candidate":
        require(package.get("manuscript", {}).get("status") == "ready", "submission-ready candidate requires manuscript")
        require(package.get("code", {}).get("status") == "ready", "submission-ready candidate requires code")
        require(bool(package.get("claims")), "submission-ready candidate requires at least one claim")
        checks = package.get("checks", {})
        require(all(item.get("status") == "pass" for item in checks.values()), "submission-ready candidate requires every nonaggregate check to pass")
    else:
        require(package.get("manuscript", {}).get("status") != "ready", "stopped outcome cannot claim a ready manuscript")


def git_output(root: Path, *arguments: str) -> str:
    completed = subprocess.run(
        ["git", *arguments], cwd=root, check=False, capture_output=True, text=True
    )
    if completed.returncode:
        raise ValidationError("cannot inspect pinned framework Git state")
    return completed.stdout.strip()


def validate_framework(mission: dict[str, Any], root: Path) -> None:
    require(root.is_dir(), "framework root does not exist")
    require(git_output(root, "rev-parse", "HEAD") == mission["pinned_framework"]["commit"], "framework HEAD does not match the mission pin")
    require(not git_output(root, "status", "--porcelain"), "pinned framework worktree is not clean")


def validate_project_artifacts(package: dict[str, Any], root: Path) -> None:
    require(root.is_dir(), "project root does not exist")
    for artifact in package.get("artifacts", []):
        relative = safe_relative_path(artifact.get("path"), "artifact path")
        path = (root / relative).resolve()
        require(path.is_relative_to(root.resolve()), "artifact escapes project root")
        require(path.is_file(), f"artifact is missing: {relative}")
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        require(digest == artifact.get("sha256"), f"artifact hash mismatch: {relative}")


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("mission", type=Path, help="frozen autonomous mission JSON")
    result.add_argument("--state", type=Path, help="campaign state JSON")
    result.add_argument("--package", type=Path, dest="package_path", help="terminal package JSON")
    result.add_argument("--framework-root", type=Path, help="read-only pinned HoloForge checkout")
    result.add_argument("--project-root", type=Path, help="private project root for artifact hash checks")
    result.add_argument("--json", action="store_true", help="emit a machine-readable result")
    return result


def main() -> int:
    arguments = parser().parse_args()
    try:
        mission = load_json(arguments.mission)
        validate_mission(mission)
        state = None
        package = None
        if arguments.state:
            state = load_json(arguments.state)
            validate_state(mission, state)
        if arguments.package_path:
            require(state is not None, "--package requires --state")
            package = load_json(arguments.package_path)
            validate_package(mission, state, package)
        if arguments.framework_root:
            validate_framework(mission, arguments.framework_root)
        if arguments.project_root:
            require(package is not None, "--project-root requires --package")
            validate_project_artifacts(package, arguments.project_root)
    except (ValidationError, KeyError, TypeError, AttributeError) as exc:
        if not isinstance(exc, ValidationError):
            exc = ValidationError("malformed campaign record")
        if arguments.json:
            print(json.dumps({"status": "fail", "error": str(exc)}, sort_keys=True))
        else:
            print(f"FAIL: {exc}", file=sys.stderr)
        return 1

    checked = ["mission"]
    if state is not None:
        checked.append("state")
    if package is not None:
        checked.append("package")
    if arguments.framework_root:
        checked.append("framework")
    if arguments.project_root:
        checked.append("artifacts")
    if arguments.json:
        print(json.dumps({"status": "pass", "checked": checked}, sort_keys=True))
    else:
        print("PASS: autonomous campaign " + ", ".join(checked))
        print("Manual scientific, novelty, authorship, disclosure, and submission review remain required.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
