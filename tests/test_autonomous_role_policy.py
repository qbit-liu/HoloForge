"""Model policy declarations are typed without assuming provider availability."""

from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / ".agents/skills/holoforge-auto-research"
SCRIPT = SKILL / "scripts/validate_autonomous_campaign.py"
spec = importlib.util.spec_from_file_location("role_policy_validator", SCRIPT)
validator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validator)


class RolePolicyTests(unittest.TestCase):
    def setUp(self) -> None:
        self.mission = json.loads(
            (SKILL / "assets/autonomous-mission.example.json").read_text()
        )

    def test_missing_empty_and_nonstring_model_are_rejected(self) -> None:
        for value in (None, "", " \n\t", 42, True, [], {}, ["model"]):
            with self.subTest(model=value):
                mission = copy.deepcopy(self.mission)
                mission["roles"][0]["model"] = value
                with self.assertRaisesRegex(validator.ValidationError, "model string"):
                    validator.validate_mission(mission)

    def test_malformed_effort_is_rejected(self) -> None:
        for value in (None, "", " ", "invented-effort", 1, True, [], {}):
            with self.subTest(effort=value):
                mission = copy.deepcopy(self.mission)
                mission["roles"][0]["reasoning_effort"] = value
                with self.assertRaisesRegex(validator.ValidationError, "reasoning effort"):
                    validator.validate_mission(mission)

    def test_schema_supported_efforts_remain_available_to_generic_policy(self) -> None:
        schema = json.loads((ROOT / "schemas/autonomous-mission.schema.json").read_text())
        efforts = schema["properties"]["roles"]["items"]["properties"]["reasoning_effort"]["enum"]
        for effort in efforts:
            with self.subTest(effort=effort):
                mission = copy.deepcopy(self.mission)
                mission["roles"][0].update(
                    model="provider-specific-model-snapshot", reasoning_effort=effort
                )
                validator.validate_mission(mission)

    def test_cli_invalid_effort_returns_controlled_failure(self) -> None:
        self.mission["roles"][0]["reasoning_effort"] = {"unsupported": True}
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "mission.json"
            path.write_text(json.dumps(self.mission))
            result = subprocess.run(
                [sys.executable, "-B", str(SCRIPT), str(path), "--json"],
                capture_output=True, text=True, check=False,
            )
        self.assertEqual(result.returncode, 1)
        self.assertEqual(json.loads(result.stdout)["status"], "fail")
        self.assertNotIn("Traceback", result.stderr)


if __name__ == "__main__":
    unittest.main()
