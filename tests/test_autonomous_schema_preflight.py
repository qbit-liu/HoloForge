"""Full preflight rejects structurally incomplete campaign records."""

from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from jsonschema import FormatChecker


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / ".agents/skills/holoforge-auto-research"
SCRIPT = SKILL / "scripts/validate_autonomous_campaign.py"
SCHEMAS = ROOT / "schemas"


class SchemaPreflightTests(unittest.TestCase):
    def setUp(self) -> None:
        self.records = {
            kind: json.loads((SKILL / "assets" / filename).read_text())
            for kind, filename in (
                ("mission", "autonomous-mission.example.json"),
                ("state", "autonomous-campaign-state.example.json"),
                ("package", "autonomous-terminal-package.example.json"),
            )
        }

    def run_cli(self, records=None, *, full=True, no_site=False, schemas=SCHEMAS):
        records = self.records if records is None else records
        with tempfile.TemporaryDirectory() as directory:
            paths = {}
            for kind, record in records.items():
                path = Path(directory) / f"{kind}.json"
                path.write_text(json.dumps(record))
                paths[kind] = path
            command = [sys.executable, "-B"] + (["-S"] if no_site else [])
            command += [str(SCRIPT), str(paths["mission"]), "--json"]
            for kind in ("state", "package"):
                if kind in paths:
                    command += [f"--{kind}", str(paths[kind])]
            if full:
                command += ["--schemas-root", str(schemas)]
            result = subprocess.run(command, capture_output=True, text=True, check=False)
        self.assertNotIn("Traceback", result.stderr)
        return result.returncode, json.loads(result.stdout)

    def test_complete_examples_pass_full_preflight(self) -> None:
        code, result = self.run_cli()
        self.assertEqual(code, 0, result)
        self.assertTrue(result["schema_validation"])
        self.assertEqual(set(result["checked"]), {"mission", "state", "package", "schemas"})

    def test_missing_owner_decision_provenance_and_role_fields_fail(self) -> None:
        cases = (
            ("authorization", "owner"), ("authorization", "decision_record"), ("provenance",),
            ("roles", 0, "responsibility"), ("roles", 0, "independence"),
        )
        for path in cases:
            with self.subTest(path=path):
                mission = copy.deepcopy(self.records["mission"])
                target = mission
                for part in path[:-1]:
                    target = target[part]
                del target[path[-1]]
                code, result = self.run_cli({"mission": mission})
                self.assertEqual(code, 1, result)
                self.assertIn("schema autonomous-mission", result["error"])

    def test_each_supplied_record_is_checked_against_its_schema(self) -> None:
        for kind in ("state", "package"):
            with self.subTest(record=kind):
                records = copy.deepcopy(self.records)
                del records[kind]["provenance"]
                code, result = self.run_cli(records)
                self.assertEqual(code, 1, result)
                self.assertIn("schema autonomous-", result["error"])
                self.assertIn("provenance", result["error"])

    def test_date_time_format_is_checked(self) -> None:
        self.records["state"]["last_updated"] = "not-a-date"
        code, result = self.run_cli()
        self.assertEqual(code, 1, result)
        self.assertIn("last_updated", result["error"])

    def test_semantic_only_result_declares_missing_schema_check(self) -> None:
        code, result = self.run_cli(full=False, no_site=True)
        self.assertEqual(code, 0, result)
        self.assertFalse(result["schema_validation"])
        self.assertNotIn("schemas", result["checked"])

    def test_requested_schema_check_fails_without_dependency(self) -> None:
        code, result = self.run_cli(no_site=True)
        self.assertEqual(code, 1, result)
        self.assertIn("requires jsonschema", result["error"])

    def test_missing_schema_fails_without_fallback(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            code, result = self.run_cli(schemas=Path(directory))
        self.assertEqual(code, 1, result)
        self.assertIn("cannot read valid JSON record", result["error"])

    def test_missing_timestamp_checker_fails_without_fallback(self) -> None:
        spec = importlib.util.spec_from_file_location("schema_preflight_validator", SCRIPT)
        validator = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(validator)
        remaining = {
            name: checker for name, checker in FormatChecker.checkers.items()
            if name != "date-time"
        }
        with patch.dict(FormatChecker.checkers, remaining, clear=True):
            with self.assertRaisesRegex(validator.ValidationError, "rfc3339-validator"):
                validator.validate_schema(
                    self.records["mission"], SCHEMAS, "autonomous-mission.schema.json"
                )


if __name__ == "__main__":
    unittest.main()
