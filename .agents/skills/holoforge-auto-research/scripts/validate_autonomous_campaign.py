#!/usr/bin/env python3
"""Validate HoloForge autonomous-research mission, state, and package records.

Semantic checks use only the Python standard library. For launch and resumption,
use --schemas-root with the pinned framework schemas to also validate every
supplied record structurally; that mode requires the jsonschema test dependency.
A semantic-only pass does not establish schema completeness or launch authority.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
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
REQUIRED_CHECKS = {
    "scientific_opportunity", "physical_claim", "source_and_novelty",
    "numerical_credibility", "independent_reproduction", "hostile_review",
}
CANDIDATE_PHASES = {
    "selected", "discovery", "confirmation", "verification", "critique",
    "packaging", "awaiting-owner",
}
REASONING_EFFORTS = {"platform-default", "low", "medium", "high", "xhigh", "max", "ultra"}
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
NULLABLE_BUDGETS = {
    "source_limit", "construction_hours", "compute_hours", "wall_time_hours",
    "storage_gb",
}
COUNT_BUDGETS = {
    "source_limit", "candidate_limit", "pivot_limit", "repair_limit_per_candidate",
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



def validate_schema(record: dict[str, Any], schemas_root: Path, name: str) -> None:
    """Use the maintained schema engine only when full preflight is requested."""
    try:
        from jsonschema import Draft202012Validator, FormatChecker
        from jsonschema.exceptions import SchemaError, ValidationError as SchemaValidationError
    except ImportError as exc:
        raise ValidationError(
            "--schemas-root requires jsonschema; install the documented test dependencies"
        ) from exc
    require("date-time" in FormatChecker.checkers,
            "--schemas-root requires rfc3339-validator; install the documented test dependencies")
    schema = load_json(schemas_root / name)
    try:
        Draft202012Validator.check_schema(schema)
        Draft202012Validator(schema, format_checker=FormatChecker()).validate(record)
    except (SchemaError, SchemaValidationError) as exc:
        location = "/".join(str(item) for item in exc.absolute_path) or "<root>"
        raise ValidationError(f"schema {name} at {location}: {exc.message}") from exc


def canonical_sha256(value: dict[str, Any]) -> str:
    encoded = json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValidationError(message)


def finite_nonnegative(value: Any, *, integer: bool = False) -> bool:
    """Keep usage finite even when the owner sets no numerical cap."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return False
    if integer and not isinstance(value, int):
        return False
    return value >= 0 and (isinstance(value, int) or math.isfinite(value))


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
    require("expires_on" in authorization, "authorization requires explicit expires_on")
    if mission.get("status") == "owner-authorized":
        require(bool(authorization.get("authorized_on")), "authorized mission requires authorized_on")
        try:
            authorized_on = date.fromisoformat(authorization["authorized_on"])
            expires_on = (
                None if authorization["expires_on"] is None
                else date.fromisoformat(authorization["expires_on"])
            )
        except (TypeError, ValueError) as exc:
            raise ValidationError("authorization dates must use ISO YYYY-MM-DD") from exc
        if expires_on is not None:
            require(expires_on >= authorized_on, "mission expiry cannot precede authorization")
        require(authorized_on <= date.today(), "owner authorization has not started")
        if expires_on is not None:
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
        model = role.get("model")
        require(isinstance(model, str) and bool(model.strip()), "every role must record a nonempty model string")
        effort = role.get("reasoning_effort")
        require(isinstance(effort, str) and effort in REASONING_EFFORTS, "every role must record a supported reasoning effort")

    external = mission.get("external_actions", {})
    require(set(external.get("forbidden", [])) == FORBIDDEN_ACTIONS, "mission must forbid every required no-touch action")
    require(set(mission.get("terminal_outcomes", [])) == TERMINAL_OUTCOMES, "mission must preserve every honest terminal outcome")

    budgets = mission.get("budgets", {})
    require(isinstance(budgets, dict), "budgets must be an object")
    for limit in (*BUDGET_MAP.values(), "repair_limit_per_candidate"):
        require(limit in budgets, f"missing budget: {limit}")
        value = budgets[limit]
        if value is None and limit in NULLABLE_BUDGETS:
            continue
        require(finite_nonnegative(value, integer=limit in COUNT_BUDGETS), f"invalid budget: {limit}")
    require(budgets.get("candidate_limit", 0) >= 1, "candidate_limit must be positive")
    if budgets["source_limit"] is not None:
        require(budgets["source_limit"] >= 1, "source_limit must be positive")
    for limit in ("compute_hours", "wall_time_hours", "storage_gb"):
        if budgets[limit] is not None:
            require(budgets[limit] > 0, f"{limit} must be positive")

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
    require(isinstance(used, dict), "budgets_used must be an object")
    limits = mission["budgets"]
    for used_name, limit_name in BUDGET_MAP.items():
        value = used.get(used_name)
        require(finite_nonnegative(value, integer=limit_name in COUNT_BUDGETS), f"invalid used budget: {used_name}")
        if limits[limit_name] is not None:
            require(value <= limits[limit_name], f"budget exceeded: {used_name}")

    candidates = state.get("candidate_ledger", [])
    require(isinstance(candidates, list), "candidate_ledger must be an array")
    ids = [item.get("candidate_id") for item in candidates if isinstance(item, dict)]
    require(len(ids) == len(candidates) == len(set(ids)), "candidate identifiers must be unique")
    require(used.get("candidates") == len(candidates), "used candidate count must match the ledger")
    for candidate in candidates:
        repairs = candidate.get("repairs_used")
        require(finite_nonnegative(repairs, integer=True), "invalid candidate repairs_used")
        require(repairs <= limits["repair_limit_per_candidate"], "candidate repair budget exceeded")

    transitions = state.get("transitions", [])
    require(isinstance(transitions, list), "transitions must be an array")
    if transitions:
        require(mission.get("status") == "owner-authorized", "executed state requires an owner-authorized mission")
    delegated = set(mission["authorization"]["delegated_decisions"])
    candidate_map = {item["candidate_id"]: item for item in candidates}
    current = "initialized"
    active_candidate = None
    pivot_count = 0
    for index, transition in enumerate(transitions, start=1):
        require(transition.get("sequence") == index, "transition sequence must be contiguous")
        require(transition.get("from") == current, "transition chain is discontinuous")
        after = transition.get("to")
        require(legal_transition(current, after), f"illegal transition: {current} -> {after}")
        decision = transition.get("delegated_decision")
        require(decision in delegated, f"transition uses undelegated decision: {decision}")
        expected_decision = (
            "candidate_generation" if after == "searching" and current == "initialized"
            else "candidate_pivot" if after == "searching"
            else "candidate_selection" if after == "selected"
            else "gate_transition"
        )
        require(decision == expected_decision, f"transition requires {expected_decision}: {current} -> {after}")
        candidate_id = transition.get("candidate_id")
        require(candidate_id is None or candidate_id in candidate_map, "transition candidate must exist in the ledger")
        if after in CANDIDATE_PHASES:
            require(candidate_id is not None, "candidate phase requires a candidate identifier")
            if after == "selected":
                active_candidate = candidate_id
            require(candidate_id == active_candidate, "candidate changed without a preserved pivot")
            contract_hash = candidate_map[candidate_id].get("gate_contract_sha256")
            require(isinstance(contract_hash, str) and len(contract_hash) == 64 and all(c in "0123456789abcdef" for c in contract_hash), "selected candidate requires a frozen gate contract hash")
            if after == "discovery":
                require("local_execution" in delegated, "discovery requires local_execution delegation")
        require(bool(transition.get("recommendation")), "transition recommendation is required")
        require(bool(transition.get("reason")), "transition reason is required")
        for path in transition.get("evidence_refs", []):
            safe_relative_path(path, "transition evidence path")
        if after == "searching" and current != "initialized":
            require(decision == "candidate_pivot", "return to searching requires candidate_pivot")
            require("candidate_selection" in delegated, "pivot requires candidate_selection delegation")
            require(candidate_id is not None and candidate_map[candidate_id].get("status") == "stopped", "pivot requires a preserved stopped candidate")
            if active_candidate is not None:
                require(candidate_id == active_candidate, "pivot must preserve the active candidate")
            active_candidate = None
            pivot_count += 1
        current = after
    require(state.get("phase") == current, "state phase must equal the last transition target")
    require(used.get("pivots") == pivot_count, "used pivot count must match transitions")

    outcome = state.get("terminal_outcome")
    if current == "terminal":
        require(outcome in TERMINAL_OUTCOMES, "terminal phase requires an allowed outcome")
        if outcome == "submission-ready-candidate":
            require(transitions[-1].get("from") == "awaiting-owner", "submission-ready outcome requires completed confirmation, verification, critique, and packaging phases")
            require(active_candidate is not None and candidate_map[active_candidate].get("status") == "packaged", "submission-ready outcome requires a packaged candidate")
            require(transitions[-1].get("candidate_id") == active_candidate, "submission-ready terminal transition must name the packaged candidate")
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

    checks = package.get("checks", {})
    require(isinstance(checks, dict) and set(checks) == REQUIRED_CHECKS, "package must contain all six nonaggregate checks")
    for check in checks.values():
        for path in check.get("evidence_refs", []):
            safe_relative_path(path, "check evidence path")

    if outcome == "submission-ready-candidate":
        require(package.get("manuscript", {}).get("status") == "ready", "submission-ready candidate requires manuscript")
        require(package.get("code", {}).get("status") == "ready", "submission-ready candidate requires code")
        require(bool(package.get("claims")), "submission-ready candidate requires at least one claim")
        require(all(item.get("status") == "pass" for item in checks.values()), "submission-ready candidate requires every nonaggregate check to pass")
        require(all(item.get("evidence_refs") for item in checks.values()), "submission-ready candidate requires evidence for every check")
        for product_name in ("manuscript", "code"):
            safe_relative_path(package[product_name].get("path"), f"ready {product_name} path")
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
    root = root.resolve()
    artifact_paths = set()
    for artifact in package.get("artifacts", []):
        relative = safe_relative_path(artifact.get("path"), "artifact path")
        require(relative not in artifact_paths, "artifact paths must be unique")
        artifact_paths.add(relative)
        path = (root / relative).resolve()
        require(path.is_relative_to(root.resolve()), "artifact escapes project root")
        require(path.is_file(), f"artifact is missing: {relative}")
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        require(digest == artifact.get("sha256"), f"artifact hash mismatch: {relative}")
    references = [path for claim in package.get("claims", []) for path in claim.get("evidence_refs", [])]
    references += [path for check in package.get("checks", {}).values() for path in check.get("evidence_refs", [])]
    for reference in references:
        relative = safe_relative_path(reference, "evidence path")
        require(relative in artifact_paths, f"evidence reference is absent from hashed artifacts: {relative}")
    for product_name in ("manuscript", "code"):
        product = package.get(product_name, {})
        if product.get("path") is None:
            continue
        relative = safe_relative_path(product["path"], f"{product_name} path")
        product_path = (root / relative).resolve()
        require(product_path.is_relative_to(root.resolve()), f"{product_name} escapes project root")
        require(product_path.exists(), f"{product_name} is missing: {relative}")
        if product_path.is_dir():
            files = [path for path in product_path.rglob("*") if path.is_file()]
            require(bool(files), f"{product_name} directory is empty")
            for path in files:
                require(path.resolve().is_relative_to(root.resolve()), f"{product_name} file escapes project root")
                require(path.relative_to(root).as_posix() in artifact_paths, f"{product_name} file is absent from hashed artifacts")
        else:
            require(relative in artifact_paths, f"{product_name} is absent from hashed artifacts: {relative}")


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("mission", type=Path, help="frozen autonomous mission JSON")
    result.add_argument("--state", type=Path, help="campaign state JSON")
    result.add_argument("--package", type=Path, dest="package_path", help="terminal package JSON")
    result.add_argument("--framework-root", type=Path, help="read-only pinned HoloForge checkout")
    result.add_argument("--project-root", type=Path, help="private project root for artifact hash checks")
    result.add_argument("--schemas-root", type=Path, help="pinned schema directory; required for full structural preflight")
    result.add_argument("--json", action="store_true", help="emit a machine-readable result")
    return result


def main() -> int:
    arguments = parser().parse_args()
    try:
        mission = load_json(arguments.mission)
        if arguments.schemas_root:
            validate_schema(mission, arguments.schemas_root, "autonomous-mission.schema.json")
        validate_mission(mission)
        state = None
        package = None
        if arguments.state:
            state = load_json(arguments.state)
            if arguments.schemas_root:
                validate_schema(state, arguments.schemas_root, "autonomous-campaign-state.schema.json")
            validate_state(mission, state)
        if arguments.package_path:
            require(state is not None, "--package requires --state")
            package = load_json(arguments.package_path)
            if arguments.schemas_root:
                validate_schema(package, arguments.schemas_root, "autonomous-terminal-package.schema.json")
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
    if arguments.schemas_root:
        checked.append("schemas")
    if state is not None:
        checked.append("state")
    if package is not None:
        checked.append("package")
    if arguments.framework_root:
        checked.append("framework")
    if arguments.project_root:
        checked.append("artifacts")
    if arguments.json:
        print(json.dumps({"status": "pass", "checked": checked, "schema_validation": bool(arguments.schemas_root)}, sort_keys=True))
    else:
        print("PASS: autonomous campaign " + ", ".join(checked))
        if not arguments.schemas_root:
            print("JSON Schema NOT checked; use --schemas-root before launch or resumption.")
        print("Manual scientific, novelty, authorship, disclosure, and submission review remain required.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
