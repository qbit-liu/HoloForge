"""Synthetic resource and authorization policies; no private campaign records."""

from __future__ import annotations

import copy
from datetime import date, timedelta
import importlib.util
import json
from pathlib import Path
import unittest

import jsonschema


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / ".agents" / "skills" / "holoforge-auto-research"
SCRIPT = SKILL / "scripts" / "validate_autonomous_campaign.py"
spec = importlib.util.spec_from_file_location("uncapped_campaign_validator", SCRIPT)
validator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validator)

NULLABLE = (
    "source_limit", "construction_hours", "compute_hours", "wall_time_hours",
    "storage_gb",
)
REQUIRED_FINITE = ("candidate_limit", "pivot_limit", "repair_limit_per_candidate")
MALFORMED_NUMBERS = (
    True, False, "unlimited", "null", [], {}, -1,
    float("inf"), float("-inf"), float("nan"),
)


class UncappedResourceTests(unittest.TestCase):
    def setUp(self) -> None:
        assets = SKILL / "assets"
        self.mission = json.loads((assets / "autonomous-mission.example.json").read_text())
        self.state = json.loads((assets / "autonomous-campaign-state.example.json").read_text())
        self.package = json.loads((assets / "autonomous-terminal-package.example.json").read_text())
        self.mission["authorization"].update(
            authorized_on=(date.today() - timedelta(days=1)).isoformat(),
            expires_on=(date.today() + timedelta(days=1)).isoformat(),
        )

    def sync_hashes(self) -> None:
        self.state["mission_sha256"] = validator.canonical_sha256(self.mission)
        self.package["mission_sha256"] = self.state["mission_sha256"]
        self.package["state_sha256"] = validator.canonical_sha256(self.state)

    def validate_records(self) -> None:
        self.sync_hashes()
        validator.validate_mission(self.mission)
        validator.validate_state(self.mission, self.state)
        validator.validate_package(self.mission, self.state, self.package)

    def validate_schemas(self) -> None:
        cases = (
            (self.mission, "autonomous-mission.schema.json"),
            (self.state, "autonomous-campaign-state.schema.json"),
            (self.package, "autonomous-terminal-package.schema.json"),
        )
        for record, filename in cases:
            schema = json.loads((ROOT / "schemas" / filename).read_text())
            jsonschema.Draft202012Validator.check_schema(schema)
            jsonschema.Draft202012Validator(
                schema, format_checker=jsonschema.FormatChecker()
            ).validate(record)

    def uncap_resources(self) -> None:
        self.mission["budgets"].update(dict.fromkeys(NULLABLE))

    def add_candidate(self, repairs=0) -> None:
        self.state["candidate_ledger"] = [{
            "candidate_id": "candidate-001", "status": "stopped",
            "disposition": "Synthetic stopped candidate for repair accounting.",
            "gate_contract_sha256": None, "repairs_used": repairs,
        }]
        self.state["budgets_used"]["candidates"] = 1

    def test_original_finite_contract_and_three_schemas_pass(self) -> None:
        self.validate_records()
        self.validate_schemas()

    def test_uncapped_contract_and_three_schemas_pass(self) -> None:
        self.uncap_resources()
        self.mission["authorization"]["expires_on"] = None
        self.state["budgets_used"].update(
            sources=1000000, construction_hours=1000000.25,
            compute_hours=1000000.5, wall_time_hours=1000000.75,
            storage_gb=1000000.125,
        )
        self.validate_records()
        self.validate_schemas()
        self.assertEqual(self.mission["schema_version"], "0.1")

    def test_each_resource_can_be_uncapped_independently(self) -> None:
        original = copy.deepcopy(self.mission)
        for name in NULLABLE:
            with self.subTest(resource=name):
                self.mission = copy.deepcopy(original)
                self.mission["budgets"][name] = None
                self.validate_records()
                self.validate_schemas()

    def test_finite_resource_boundaries_and_overruns(self) -> None:
        for used_name, limit_name in validator.BUDGET_MAP.items():
            if limit_name not in NULLABLE:
                continue
            with self.subTest(resource=limit_name):
                original = self.state["budgets_used"][used_name]
                self.state["budgets_used"][used_name] = self.mission["budgets"][limit_name]
                self.validate_records()
                self.state["budgets_used"][used_name] += 1
                with self.assertRaisesRegex(validator.ValidationError, "budget exceeded"):
                    self.validate_records()
                self.state["budgets_used"][used_name] = original

    def test_mixed_policy_preserves_remaining_finite_cap(self) -> None:
        self.uncap_resources()
        self.mission["budgets"]["compute_hours"] = 1
        self.state["budgets_used"].update(sources=1000000, compute_hours=2)
        with self.assertRaisesRegex(validator.ValidationError, "budget exceeded: compute_hours"):
            self.validate_records()

    def test_all_budget_keys_remain_required(self) -> None:
        self.uncap_resources()
        for name in (*NULLABLE, *REQUIRED_FINITE):
            with self.subTest(budget=name):
                value = self.mission["budgets"].pop(name)
                with self.assertRaisesRegex(validator.ValidationError, "missing budget"):
                    validator.validate_mission(self.mission)
                with self.assertRaises(jsonschema.ValidationError):
                    self.validate_schemas()
                self.mission["budgets"][name] = value

    def test_numeric_caps_must_be_finite_and_well_typed(self) -> None:
        for name in (*NULLABLE, *REQUIRED_FINITE):
            original = self.mission["budgets"][name]
            for value in MALFORMED_NUMBERS:
                with self.subTest(budget=name, value=value):
                    self.mission["budgets"][name] = value
                    with self.assertRaisesRegex(validator.ValidationError, "invalid budget"):
                        validator.validate_mission(self.mission)
            self.mission["budgets"][name] = original

    def test_candidate_pivot_and_repair_caps_cannot_be_null(self) -> None:
        self.uncap_resources()
        for name in REQUIRED_FINITE:
            with self.subTest(budget=name):
                original = self.mission["budgets"][name]
                self.mission["budgets"][name] = None
                with self.assertRaisesRegex(validator.ValidationError, "invalid budget"):
                    validator.validate_mission(self.mission)
                with self.assertRaises(jsonschema.ValidationError):
                    self.validate_schemas()
                self.mission["budgets"][name] = original

    def test_count_caps_must_be_integer_values(self) -> None:
        for name in ("source_limit", *REQUIRED_FINITE):
            for value in (1.5, 1.0):
                with self.subTest(budget=name, value=value):
                    mission = copy.deepcopy(self.mission)
                    mission["budgets"][name] = value
                    with self.assertRaisesRegex(validator.ValidationError, "invalid budget"):
                        validator.validate_mission(mission)

    def test_existing_positive_minima_remain_enforced(self) -> None:
        for name in ("source_limit", "compute_hours", "wall_time_hours", "storage_gb", "candidate_limit"):
            with self.subTest(budget=name):
                mission = copy.deepcopy(self.mission)
                mission["budgets"][name] = 0
                with self.assertRaisesRegex(validator.ValidationError, "must be positive"):
                    validator.validate_mission(mission)

    def test_zero_construction_pivot_and_repair_allowances_remain_valid(self) -> None:
        self.mission["budgets"].update(
            construction_hours=0, pivot_limit=0, repair_limit_per_candidate=0
        )
        self.add_candidate(repairs=0)
        self.validate_records()

    def test_usage_is_required_finite_and_nonnegative_with_either_policy(self) -> None:
        for uncapped in (False, True):
            if uncapped:
                self.uncap_resources()
            for name in self.state["budgets_used"]:
                original = self.state["budgets_used"][name]
                for value in (*MALFORMED_NUMBERS, None):
                    with self.subTest(uncapped=uncapped, usage=name, value=value):
                        self.state["budgets_used"][name] = value
                        with self.assertRaisesRegex(validator.ValidationError, "invalid used budget"):
                            self.validate_records()
                self.state["budgets_used"][name] = original

    def test_usage_fields_cannot_be_omitted_when_uncapped(self) -> None:
        self.uncap_resources()
        for name in tuple(self.state["budgets_used"]):
            with self.subTest(usage=name):
                value = self.state["budgets_used"].pop(name)
                with self.assertRaisesRegex(validator.ValidationError, "invalid used budget"):
                    self.validate_records()
                self.state["budgets_used"][name] = value

    def test_usage_counts_remain_integer(self) -> None:
        self.uncap_resources()
        for name in ("sources", "candidates", "pivots"):
            original = self.state["budgets_used"][name]
            for value in (0.5, 1.0):
                with self.subTest(usage=name, value=value):
                    self.state["budgets_used"][name] = value
                    with self.assertRaisesRegex(validator.ValidationError, "invalid used budget"):
                        self.validate_records()
            self.state["budgets_used"][name] = original

    def test_large_finite_integer_usage_does_not_require_float_conversion(self) -> None:
        self.uncap_resources()
        self.state["budgets_used"]["sources"] = 10 ** 400
        self.validate_records()

    def test_uncapped_resources_preserve_candidate_and_pivot_limits(self) -> None:
        self.uncap_resources()
        for name, limit in (("candidates", "candidate_limit"), ("pivots", "pivot_limit")):
            with self.subTest(usage=name):
                original = self.state["budgets_used"][name]
                self.state["budgets_used"][name] = self.mission["budgets"][limit] + 1
                with self.assertRaisesRegex(validator.ValidationError, "budget exceeded"):
                    self.validate_records()
                self.state["budgets_used"][name] = original

    def test_uncapped_resources_preserve_repair_limit(self) -> None:
        self.uncap_resources()
        self.add_candidate(repairs=self.mission["budgets"]["repair_limit_per_candidate"])
        self.validate_records()
        self.state["candidate_ledger"][0]["repairs_used"] += 1
        with self.assertRaisesRegex(validator.ValidationError, "candidate repair budget exceeded"):
            self.validate_records()

    def test_repair_usage_must_be_present_nonnegative_finite_integer(self) -> None:
        self.uncap_resources()
        for value in (*MALFORMED_NUMBERS, None, 0.5, 1.0):
            with self.subTest(repairs=value):
                self.add_candidate(repairs=value)
                with self.assertRaisesRegex(validator.ValidationError, "invalid candidate repairs_used"):
                    self.validate_records()
        self.state["candidate_ledger"][0].pop("repairs_used")
        with self.assertRaisesRegex(validator.ValidationError, "invalid candidate repairs_used"):
            self.validate_records()

    def test_explicit_null_expiry_is_valid(self) -> None:
        self.mission["authorization"]["expires_on"] = None
        self.validate_records()
        self.validate_schemas()

    def test_missing_expiry_is_never_interpreted_as_null(self) -> None:
        self.mission["authorization"].pop("expires_on")
        for status in ("draft", "owner-authorized", "closed"):
            with self.subTest(status=status):
                self.mission["status"] = status
                with self.assertRaisesRegex(validator.ValidationError, "explicit expires_on"):
                    validator.validate_mission(self.mission)
                with self.assertRaises(jsonschema.ValidationError):
                    self.validate_schemas()

    def test_finite_expiry_still_enforces_dates(self) -> None:
        today = date.today()
        cases = (
            (today - timedelta(days=2), today - timedelta(days=1), "has expired"),
            (today, today - timedelta(days=1), "cannot precede authorization"),
        )
        for authorized, expires, message in cases:
            with self.subTest(message=message):
                self.mission["authorization"].update(
                    authorized_on=authorized.isoformat(), expires_on=expires.isoformat()
                )
                with self.assertRaisesRegex(validator.ValidationError, message):
                    validator.validate_mission(self.mission)
        self.mission["authorization"].update(
            authorized_on=today.isoformat(), expires_on=today.isoformat()
        )
        self.validate_records()

    def test_no_expiry_still_requires_started_authorization(self) -> None:
        self.mission["authorization"].update(
            authorized_on=(date.today() + timedelta(days=1)).isoformat(), expires_on=None
        )
        with self.assertRaisesRegex(validator.ValidationError, "has not started"):
            validator.validate_mission(self.mission)

    def test_no_expiry_still_requires_authorized_on(self) -> None:
        self.mission["authorization"]["expires_on"] = None
        for value in (None, "", False):
            with self.subTest(authorized_on=value):
                self.mission["authorization"]["authorized_on"] = value
                with self.assertRaisesRegex(validator.ValidationError, "requires authorized_on"):
                    validator.validate_mission(self.mission)
        self.mission["authorization"].pop("authorized_on")
        with self.assertRaisesRegex(validator.ValidationError, "requires authorized_on"):
            validator.validate_mission(self.mission)

    def test_malformed_authorization_dates_are_rejected(self) -> None:
        for name in ("authorized_on", "expires_on"):
            for value in (True, 1, [], {}, "not-a-date", "2026-02-30"):
                with self.subTest(field=name, value=value):
                    mission = copy.deepcopy(self.mission)
                    mission["authorization"][name] = value
                    with self.assertRaises(validator.ValidationError):
                        validator.validate_mission(mission)

    def test_draft_with_explicit_null_dates_remains_unlaunchable(self) -> None:
        self.uncap_resources()
        self.mission["status"] = "draft"
        self.mission["authorization"].update(authorized_on=None, expires_on=None)
        validator.validate_mission(self.mission)
        self.validate_schemas()
        with self.assertRaisesRegex(validator.ValidationError, "owner-authorized"):
            self.validate_records()


if __name__ == "__main__":
    unittest.main()
