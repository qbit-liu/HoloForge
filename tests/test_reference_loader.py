"""Tests for loading frozen resources from the installed package tree."""

import unittest

import numpy as np

from holoforge.reference_data import (
    load_pdg_2026_rho_spectrum,
    load_reference_dataset,
)


class ReferenceLoaderTests(unittest.TestCase):
    def test_packaged_dataset_loads_without_repository_path(self) -> None:
        dataset = load_reference_dataset()
        self.assertEqual(dataset["id"], "pdg-2026-rho-masses")
        self.assertEqual(dataset["edition"]["published_year"], 2026)
        self.assertEqual(
            [entry["id"] for entry in dataset["entries"] if not entry["included"]],
            ["rho-1570"],
        )

    def test_pdg_ratios_include_denominator_covariance(self) -> None:
        spectrum = load_pdg_2026_rho_spectrum()
        np.testing.assert_allclose(spectrum.normalized.ratios[0], 1.0)
        self.assertEqual(spectrum.model_modes.tolist(), [0, 1, 2])
        self.assertGreater(spectrum.normalized.ratio_covariance[1, 2], 0.0)
        self.assertEqual(
            spectrum.to_dict()["review_status"],
            "approved",
        )
        self.assertEqual(spectrum.to_dict()["reviewed_by"], "Xin-Yi Liu")
        self.assertEqual(spectrum.to_dict()["reviewed_on"], "2026-08-05")

    def test_unknown_resource_fails_clearly(self) -> None:
        with self.assertRaisesRegex(ValueError, "unknown packaged"):
            load_reference_dataset("data/reference/not-present.json")

    def test_gubser_nellore_anchors_load_from_package_resources(self) -> None:
        figure_2 = load_reference_dataset(
            "data/reference/gubser-nellore-figure-2-anchors.json"
        )
        figure_3 = load_reference_dataset(
            "data/reference/gubser-nellore-figure-3-anchors.json"
        )
        self.assertEqual(len(figure_2["entries"]), 9)
        self.assertEqual(len(figure_3["entries"]), 12)
        self.assertEqual(figure_2["provenance"]["review_status"], "approved")
        self.assertEqual(figure_2["provenance"]["reviewed_by"], "Xin-Yi Liu")
        self.assertEqual(figure_2["provenance"]["reviewed_on"], "2026-08-17")

    def test_dgr_figure_3_anchors_load_from_package_resources(self) -> None:
        entropy = load_reference_dataset(
            "data/reference/dewolfe-gubser-rosen-figure-3-entropy.json"
        )
        susceptibility = load_reference_dataset(
            "data/reference/dewolfe-gubser-rosen-figure-3-susceptibility.json"
        )
        self.assertEqual(len(entropy["entries"]), 11)
        self.assertEqual(len(susceptibility["entries"]), 11)
        for dataset in (entropy, susceptibility):
            self.assertEqual(dataset["provenance"]["review_status"], "approved")
            self.assertEqual(dataset["provenance"]["reviewed_by"], "Xin-Yi Liu")
            self.assertEqual(dataset["provenance"]["reviewed_on"], "2026-08-22")

    def test_dgr_figure_5_anchors_load_from_package_resources(self) -> None:
        names = ("above-tc", "at-tc", "below-tc")
        datasets = [
            load_reference_dataset(
                f"data/reference/dewolfe-gubser-rosen-figure-5-{name}.json"
            )
            for name in names
        ]
        self.assertEqual(
            [len(dataset["entries"]) for dataset in datasets], [12] * 3
        )
        for dataset in datasets:
            self.assertEqual(dataset["provenance"]["review_status"], "approved")
            self.assertEqual(dataset["provenance"]["reviewed_by"], "Xin-Yi Liu")
            self.assertEqual(dataset["provenance"]["reviewed_on"], "2026-08-22")
            self.assertEqual(
                dataset["conventions"][0]["value"],
                "mu_BH is the dimensionless abscissa and "
                "rho_source_figure5 is the dimensionless ordinate in "
                "the source black-hole variables",
            )
            self.assertTrue(
                all(
                    entry["label"].startswith("rho_source_figure5 = ")
                    for entry in dataset["entries"]
                )
            )


if __name__ == "__main__":
    unittest.main()
