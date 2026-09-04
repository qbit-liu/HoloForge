"""Contracts and fail-closed semantics for experimental autonomous research."""

from __future__ import annotations

import copy
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Optional

import jsonschema


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / ".agents" / "skills" / "holoforge-auto-research"
ASSETS = SKILL / "assets"
SCRIPT = SKILL / "scripts" / "validate_autonomous_campaign.py"
SCHEMAS = ROOT / "schemas"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def digest(value: dict) -> str:
    encoded = json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


class AutonomousResearchTests(unittest.TestCase):
    def setUp(self) -> None:
        self.mission = load(ASSETS / "autonomous-mission.example.json")
        self.state = load(ASSETS / "autonomous-campaign-state.example.json")
        self.package = load(ASSETS / "autonomous-terminal-package.example.json")

    def run_validator(
        self,
        mission: dict,
        state: Optional[dict] = None,
        package: Optional[dict] = None,
    ) -> subprocess.CompletedProcess[str]:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            mission_path = root / "mission.json"
            mission_path.write_text(json.dumps(mission), encoding="utf-8")
            command = [sys.executable, str(SCRIPT), str(mission_path)]
            if state is not None:
                state_path = root / "state.json"
                state_path.write_text(json.dumps(state), encoding="utf-8")
                command.extend(["--state", str(state_path)])
            if package is not None:
                package_path = root / "package.json"
                package_path.write_text(json.dumps(package), encoding="utf-8")
                command.extend(["--package", str(package_path)])
            return subprocess.run(
                command, check=False, capture_output=True, text=True
            )

    def test_examples_conform_to_schemas(self) -> None:
        cases = (
            (self.mission, "autonomous-mission.schema.json"),
            (self.state, "autonomous-campaign-state.schema.json"),
            (self.package, "autonomous-terminal-package.schema.json"),
        )
        for instance, schema_name in cases:
            with self.subTest(schema=schema_name):
                schema = load(SCHEMAS / schema_name)
                jsonschema.Draft202012Validator.check_schema(schema)
                jsonschema.validate(instance=instance, schema=schema)

    def test_synthetic_terminal_package_passes_semantic_validator(self) -> None:
        completed = self.run_validator(self.mission, self.state, self.package)
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
        self.assertIn("PASS:", completed.stdout)
        self.assertIn("Manual scientific", completed.stdout)

    def test_framework_must_remain_read_only(self) -> None:
        mission = copy.deepcopy(self.mission)
        mission["pinned_framework"]["write_policy"] = "read-write"
        completed = self.run_validator(mission)
        self.assertEqual(completed.returncode, 1)
        self.assertIn("read-only", completed.stderr)

    def test_all_no_touch_actions_are_mandatory(self) -> None:
        mission = copy.deepcopy(self.mission)
        mission["external_actions"]["forbidden"].remove("remote-git-action")
        completed = self.run_validator(mission)
        self.assertEqual(completed.returncode, 1)
        self.assertIn("every required no-touch action", completed.stderr)

    def test_expired_owner_authorization_fails_closed(self) -> None:
        mission = copy.deepcopy(self.mission)
        mission["authorization"]["authorized_on"] = "2020-01-01"
        mission["authorization"]["expires_on"] = "2020-01-02"
        completed = self.run_validator(mission)
        self.assertEqual(completed.returncode, 1)
        self.assertIn("expired", completed.stderr)

    def test_only_coordinator_can_write_canonical_state(self) -> None:
        mission = copy.deepcopy(self.mission)
        mission["roles"][1]["write_access"] = "canonical"
        completed = self.run_validator(mission)
        self.assertEqual(completed.returncode, 1)
        self.assertIn("one canonical coordinator", completed.stderr)

    def test_state_is_bound_to_exact_mission_hash(self) -> None:
        state = copy.deepcopy(self.state)
        state["mission_sha256"] = "0" * 64
        completed = self.run_validator(self.mission, state)
        self.assertEqual(completed.returncode, 1)
        self.assertIn("mission hash mismatch", completed.stderr)

    def test_budget_overrun_fails_closed(self) -> None:
        state = copy.deepcopy(self.state)
        state["budgets_used"]["sources"] = self.mission["budgets"]["source_limit"] + 1
        completed = self.run_validator(self.mission, state)
        self.assertEqual(completed.returncode, 1)
        self.assertIn("budget exceeded", completed.stderr)

    def test_illegal_transition_fails_closed(self) -> None:
        state = copy.deepcopy(self.state)
        state["transitions"][1]["to"] = "packaging"
        completed = self.run_validator(self.mission, state)
        self.assertEqual(completed.returncode, 1)
        self.assertIn("illegal transition", completed.stderr)

    def test_path_escape_fails_closed(self) -> None:
        state = copy.deepcopy(self.state)
        state["touched_paths"].append("../outside.txt")
        completed = self.run_validator(self.mission, state)
        self.assertEqual(completed.returncode, 1)
        self.assertIn("must not escape", completed.stderr)

    def test_stopped_outcome_cannot_claim_ready_manuscript(self) -> None:
        package = copy.deepcopy(self.package)
        package["manuscript"] = {"status": "ready", "path": "campaign/paper/main.pdf"}
        completed = self.run_validator(self.mission, self.state, package)
        self.assertEqual(completed.returncode, 1)
        self.assertIn("stopped outcome", completed.stderr)

    def test_package_is_bound_to_exact_state_hash(self) -> None:
        package = copy.deepcopy(self.package)
        package["state_sha256"] = "f" * 64
        completed = self.run_validator(self.mission, self.state, package)
        self.assertEqual(completed.returncode, 1)
        self.assertIn("state hash mismatch", completed.stderr)

    def test_human_decisions_cannot_be_silently_removed(self) -> None:
        package = copy.deepcopy(self.package)
        package["owner_decisions_remaining"].remove("submission")
        completed = self.run_validator(self.mission, self.state, package)
        self.assertEqual(completed.returncode, 1)
        self.assertIn("must remain open", completed.stderr)


if __name__ == "__main__":
    unittest.main()
