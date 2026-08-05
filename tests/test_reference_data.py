"""Validate the v0.3 frozen reference-data contract."""

import copy
import json
import unittest
from pathlib import Path
from typing import Any, Dict

from jsonschema import Draft202012Validator, FormatChecker, ValidationError


ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "schemas" / "reference-dataset.schema.json"
DATA_PATH = (
    ROOT
    / "domains"
    / "qcd"
    / "vector_spectrum_comparison"
    / "reference-data"
    / "pdg-2024-rho-masses.json"
)


def load_json(path: Path) -> Dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


class ReferenceDatasetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.schema = load_json(SCHEMA_PATH)
        cls.dataset = load_json(DATA_PATH)
        Draft202012Validator.check_schema(cls.schema)
        cls.validator = Draft202012Validator(
            cls.schema, format_checker=FormatChecker()
        )

    def test_pdg_snapshot_is_valid(self) -> None:
        self.validator.validate(self.dataset)

    def test_snapshot_has_one_anchor_and_visible_assignments(self) -> None:
        entries = self.dataset["entries"]
        anchors = [entry for entry in entries if entry["assignment_status"] == "anchor"]
        self.assertEqual(len(anchors), 1)
        self.assertTrue(all(entry["notes"] for entry in entries))
        self.assertTrue(all(entry["unit"] == "MeV" for entry in entries))

    def test_frozen_source_has_hash_license_and_locators(self) -> None:
        edition = self.dataset["edition"]
        self.assertEqual(len(edition["artifact_sha256"]), 64)
        self.assertEqual(edition["license"], "CC BY 4.0")
        self.assertTrue(
            all(entry["source_locator"] for entry in self.dataset["entries"])
        )

    def test_missing_source_locator_is_rejected(self) -> None:
        invalid = copy.deepcopy(self.dataset)
        del invalid["entries"][0]["source_locator"]
        with self.assertRaises(ValidationError):
            self.validator.validate(invalid)

    def test_incomplete_asymmetric_uncertainty_is_rejected(self) -> None:
        invalid = copy.deepcopy(self.dataset)
        invalid["entries"][1]["uncertainty"] = {
            "kind": "asymmetric",
            "plus": 25.0,
            "unit": "MeV",
            "source_text": "+25 MeV only",
        }
        with self.assertRaises(ValidationError):
            self.validator.validate(invalid)


if __name__ == "__main__":
    unittest.main()
