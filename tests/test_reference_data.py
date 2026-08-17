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
    / "src"
    / "holoforge"
    / "data"
    / "reference"
    / "pdg-2026-rho-masses.json"
)
GUBSER_NELLORE_PATHS = (
    ROOT
    / "src"
    / "holoforge"
    / "data"
    / "reference"
    / "gubser-nellore-figure-2-anchors.json",
    ROOT
    / "src"
    / "holoforge"
    / "data"
    / "reference"
    / "gubser-nellore-figure-3-anchors.json",
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
        self.assertEqual(self.dataset["provenance"]["review_status"], "approved")
        self.assertEqual(self.dataset["provenance"]["reviewed_by"], "Xin-Yi Liu")
        self.assertEqual(self.dataset["provenance"]["reviewed_on"], "2026-08-05")

    def test_gubser_nellore_vector_anchor_records_are_valid_and_approved(self) -> None:
        datasets = [load_json(path) for path in GUBSER_NELLORE_PATHS]
        for dataset in datasets:
            with self.subTest(dataset=dataset["id"]):
                self.validator.validate(dataset)
                self.assertEqual(
                    dataset["provenance"]["review_status"], "approved"
                )
                self.assertEqual(
                    dataset["provenance"]["reviewed_by"], "Xin-Yi Liu"
                )
                self.assertEqual(
                    dataset["provenance"]["reviewed_on"], "2026-08-17"
                )
                self.assertTrue(all(entry["included"] for entry in dataset["entries"]))
                self.assertTrue(
                    all(
                        entry["assignment_status"] == "anchor"
                        for entry in dataset["entries"]
                    )
                )
        self.assertEqual(len(datasets[0]["entries"]), 9)
        self.assertEqual(len(datasets[1]["entries"]), 12)
        self.assertEqual(
            datasets[0]["edition"]["artifacts"][0]["sha256"],
            datasets[1]["edition"]["artifacts"][0]["sha256"],
        )

    def test_snapshot_has_one_anchor_and_visible_assignments(self) -> None:
        entries = self.dataset["entries"]
        anchors = [entry for entry in entries if entry["assignment_status"] == "anchor"]
        self.assertEqual(len(anchors), 1)
        self.assertTrue(all(entry["notes"] for entry in entries))
        self.assertTrue(all(entry["unit"] == "MeV" for entry in entries))
        self.assertEqual(
            [entry["model_mode"] for entry in entries], [0, 1, 2, 2]
        )
        included = [entry for entry in entries if entry["included"]]
        self.assertEqual([entry["model_mode"] for entry in included], [0, 1, 2])
        rho_1570 = next(entry for entry in entries if entry["id"] == "rho-1570")
        self.assertFalse(rho_1570["included"])
        self.assertEqual(rho_1570["assignment_status"], "ambiguous")

    def test_frozen_source_has_hash_license_and_locators(self) -> None:
        edition = self.dataset["edition"]
        artifacts = edition["artifacts"]
        self.assertEqual(len(artifacts), 4)
        self.assertTrue(all(len(artifact["sha256"]) == 64 for artifact in artifacts))
        self.assertEqual(edition["license"], "CC BY 4.0")
        artifact_ids = {artifact["id"] for artifact in artifacts}
        self.assertTrue(
            all(entry["source_locator"] for entry in self.dataset["entries"])
        )
        self.assertTrue(
            all(
                entry["source_artifact"] in artifact_ids
                for entry in self.dataset["entries"]
            )
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

    def test_incomplete_component_uncertainty_is_rejected(self) -> None:
        invalid = copy.deepcopy(self.dataset)
        invalid["entries"][2]["uncertainty"]["components"] = [
            {"label": "statistical", "sigma": 36.0}
        ]
        with self.assertRaises(ValidationError):
            self.validator.validate(invalid)


if __name__ == "__main__":
    unittest.main()
