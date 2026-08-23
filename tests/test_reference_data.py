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
DGR_FIGURE_3_PATHS = (
    ROOT
    / "src"
    / "holoforge"
    / "data"
    / "reference"
    / "dewolfe-gubser-rosen-figure-3-entropy.json",
    ROOT
    / "src"
    / "holoforge"
    / "data"
    / "reference"
    / "dewolfe-gubser-rosen-figure-3-susceptibility.json",
)
DGR_FIGURE_5_PATHS = (
    ROOT
    / "src"
    / "holoforge"
    / "data"
    / "reference"
    / "dewolfe-gubser-rosen-figure-5-above-tc.json",
    ROOT
    / "src"
    / "holoforge"
    / "data"
    / "reference"
    / "dewolfe-gubser-rosen-figure-5-at-tc.json",
    ROOT
    / "src"
    / "holoforge"
    / "data"
    / "reference"
    / "dewolfe-gubser-rosen-figure-5-below-tc.json",
)
DGR_FIGURE_5_RHO_ANCHORS = (5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 18)
DGR_FIGURE_5_MU_ANCHORS = (
    (
        0.763360248,
        0.769184501,
        0.772491083,
        0.774429108,
        0.775677302,
        0.776608413,
        0.777384213,
        0.778201412,
        0.779162673,
        0.780265316,
        0.783136041,
        0.786922967,
    ),
    (
        0.798016580,
        0.802130292,
        0.804082027,
        0.804868047,
        0.805101632,
        0.805121624,
        0.805103109,
        0.805190607,
        0.805484660,
        0.806013227,
        0.807772507,
        0.810528785,
    ),
    (
        0.804842255,
        0.808652241,
        0.810375950,
        0.810812705,
        0.810850854,
        0.810712157,
        0.810562202,
        0.810497383,
        0.810678207,
        0.811037943,
        0.812599677,
        0.815169234,
    ),
)
DGR_FIGURE_5_PANEL_DIGESTS = (
    "c6a56d588ee5491c2e06359d3d718b8fd21a24ebcf4f888b796a0a6db87d0719",
    "5282e9a4174fd124a18a6aa53861182277b7c46024e8b6e301c39839942ed8a3",
    "5519dfc2f0abfa1f721f28432a7b748e73c15d532104e21c14d32b5395814064",
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

    def test_dgr_figure_3_vector_anchor_records_are_valid_and_approved(self) -> None:
        datasets = [load_json(path) for path in DGR_FIGURE_3_PATHS]
        for dataset in datasets:
            with self.subTest(dataset=dataset["id"]):
                self.validator.validate(dataset)
                self.assertEqual(dataset["provenance"]["review_status"], "approved")
                self.assertEqual(dataset["provenance"]["reviewed_by"], "Xin-Yi Liu")
                self.assertEqual(dataset["provenance"]["reviewed_on"], "2026-08-22")
                self.assertTrue(all(entry["included"] for entry in dataset["entries"]))
                self.assertTrue(
                    all(
                        entry["assignment_status"] == "anchor"
                        for entry in dataset["entries"]
                    )
                )
                self.assertIn(
                    "third-party lattice markers are excluded",
                    dataset["conventions"][2]["value"],
                )
        self.assertEqual([len(item["entries"]) for item in datasets], [11, 11])
        self.assertEqual(
            datasets[0]["edition"]["artifacts"][0]["sha256"],
            datasets[1]["edition"]["artifacts"][0]["sha256"],
        )

    def test_dgr_figure_5_vector_anchor_records_are_valid_and_approved(
        self,
    ) -> None:
        datasets = [load_json(path) for path in DGR_FIGURE_5_PATHS]
        for dataset, expected_mu, panel_digest in zip(
            datasets,
            DGR_FIGURE_5_MU_ANCHORS,
            DGR_FIGURE_5_PANEL_DIGESTS,
        ):
            with self.subTest(dataset=dataset["id"]):
                self.validator.validate(dataset)
                self.assertEqual(
                    dataset["provenance"]["review_status"], "approved"
                )
                self.assertEqual(
                    dataset["provenance"]["reviewed_by"], "Xin-Yi Liu"
                )
                self.assertEqual(
                    dataset["provenance"]["reviewed_on"], "2026-08-22"
                )
                self.assertEqual(len(dataset["entries"]), 12)
                self.assertEqual(
                    [entry["id"] for entry in dataset["entries"]],
                    [f"rho-{rho}" for rho in DGR_FIGURE_5_RHO_ANCHORS],
                )
                self.assertEqual(
                    [entry["value"] for entry in dataset["entries"]],
                    list(expected_mu),
                )
                self.assertTrue(
                    all(entry["included"] for entry in dataset["entries"])
                )
                self.assertTrue(
                    all(
                        entry["assignment_status"] == "anchor"
                        for entry in dataset["entries"]
                    )
                )
                coordinate_value = dataset["conventions"][0]["value"]
                self.assertEqual(
                    coordinate_value,
                    "mu_BH is the dimensionless abscissa and "
                    "rho_source_figure5 is the dimensionless ordinate in "
                    "the source black-hole variables",
                )
                self.assertNotIn(
                    "rho_source_figure5 is the dimensionless abscissa",
                    coordinate_value,
                )
                comparison = next(
                    item
                    for item in dataset["conventions"]
                    if item["name"] == "absolute ordinate comparison"
                )
                self.assertIn("blocked", comparison["value"])
                extraction = next(
                    item
                    for item in dataset["conventions"]
                    if item["name"] == "anchor extraction"
                )
                self.assertIn(panel_digest, extraction["rationale"])
                self.assertTrue(
                    all(
                        entry["label"].startswith(
                            "rho_source_figure5 = "
                        )
                        for entry in dataset["entries"]
                    )
                )
                transform = dataset["transformations"][0]["expression"]
                self.assertIn("mu_BH =", transform)
                self.assertIn("rho_source_figure5 =", transform)
                self.assertNotIn("rho_BH", json.dumps(dataset, sort_keys=True))
        self.assertEqual(
            len(
                {
                    dataset["edition"]["artifacts"][0]["sha256"]
                    for dataset in datasets
                }
            ),
            1,
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
