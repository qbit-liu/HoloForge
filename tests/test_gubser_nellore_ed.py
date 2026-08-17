"""Scientific, numerical, artifact, and interface gates for the ED benchmark."""

import hashlib
import json
import math
from pathlib import Path
import tempfile
import unittest

import numpy as np

from holoforge.benchmarks.gubser_nellore_ed import (
    COSH_CALIBRATION,
    QCD_LIKE,
    SOURCE_ARCHIVE_SHA256,
    SOURCE_PDF_SHA256,
    coupled_equation_diagnostics,
    get_preset,
    save_gubser_nellore_artifacts,
    solve_coupled_profile,
    verify_gubser_nellore_ed,
)
from holoforge.benchmarks.adapters.gubser_nellore_ed import (
    GUBSER_NELLORE_MODEL_CARD,
)


ROOT = Path(__file__).resolve().parents[1]


class GubserNelloreEinsteinDilatonTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.record = verify_gubser_nellore_ed(profile="anchor")
        cls.payload = cls.record.to_dict()

    def test_complete_anchor_contract_passes(self) -> None:
        self.assertTrue(self.record.passed)
        self.assertTrue(all(check.passed for check in self.record.acceptance_checks))
        self.assertEqual(len(self.record.acceptance_checks), 14)

    def test_duplicate_complete_run_is_deterministic(self) -> None:
        determinism = self.payload["results"]["determinism"]
        self.assertTrue(determinism["repeat_enabled"])
        self.assertLessEqual(determinism["maximum_scaled_difference"], 1.0e-12)
        checks = {
            item["id"]: item for item in self.payload["acceptance_checks"]
        }
        self.assertIn("physical observables", checks["determinism"]["description"])

    def test_primary_and_verification_branches_remain_distinct(self) -> None:
        presets = self.payload["results"]["presets"]
        cosh = presets["cosh-calibration"]
        qcd = presets["qcd-like"]
        self.assertEqual(cosh["primary_degree"], 80)
        self.assertEqual(qcd["primary_degree"], 80)
        self.assertEqual(cosh["horizon_count"], 260)
        self.assertEqual(qcd["horizon_count"], 526)
        self.assertEqual(cosh["verification_horizon_count"], 100)
        self.assertEqual(qcd["verification_horizon_count"], 106)
        self.assertEqual(cosh["degrees"], [40, 60, 80])
        self.assertEqual(qcd["degrees"], [80, 120, 150])
        self.assertEqual(
            {row["role"] for row in qcd["profiles"]},
            {"primary", "verification"},
        )

    def test_equation_refinement_and_independent_gates_have_margin(self) -> None:
        checks = {
            item["id"]: item for item in self.payload["acceptance_checks"]
        }
        self.assertLessEqual(checks["collocation-residual"]["value"], 1.0e-9)
        self.assertLessEqual(checks["independent-equations"]["value"], 1.0e-7)
        self.assertLessEqual(checks["spectral-refinement"]["value"], 2.0e-4)
        self.assertLessEqual(checks["dop853-comparison"]["value"], 5.0e-4)
        self.assertEqual(checks["refinement-order"]["value"], 0.0)

    def test_thermodynamic_and_figure_gates_have_margin(self) -> None:
        checks = {
            item["id"]: item for item in self.payload["acceptance_checks"]
        }
        self.assertLessEqual(checks["thermodynamic-derivative"]["value"], 1.0e-3)
        self.assertLessEqual(checks["figure-2-reproduction"]["value"], 1.5e-3)
        self.assertLessEqual(checks["figure-3-reproduction"]["value"], 5.0e-3)
        registration = self.payload["results"]["presets"]["qcd-like"]["figure"][
            "registration"
        ]
        self.assertEqual(registration["source_minimum_coordinate"], 0.9618971489)
        self.assertIn("not a predicted critical temperature", registration["interpretation"])

    def test_record_is_strict_json_and_retains_public_source_digests(self) -> None:
        encoded = json.dumps(self.payload, allow_nan=False, sort_keys=True)
        self.assertTrue(encoded)
        self.assertEqual(
            self.payload["primary_source"]["pdf_sha256"], SOURCE_PDF_SHA256
        )
        self.assertEqual(
            self.payload["primary_source"]["source_archive_sha256"],
            SOURCE_ARCHIVE_SHA256,
        )
        self.assertEqual(self.payload["review_state"], "approved")
        self.assertEqual(self.payload["reviewed_by"], "Xin-Yi Liu")
        self.assertEqual(self.payload["reviewed_on"], "2026-08-17")
        self.assertEqual(self.payload["reference_data"]["review_state"], "approved")
        self.assertTrue(self.payload["generated_by_ai"])

    def test_registered_model_card_digest_matches_approved_record(self) -> None:
        path = ROOT / GUBSER_NELLORE_MODEL_CARD.repository_path
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        self.assertEqual(digest, GUBSER_NELLORE_MODEL_CARD.sha256)
        card = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(card["provenance"]["review_status"], "approved")
        self.assertEqual(card["provenance"]["reviewed_by"], "Xin-Yi Liu")
        self.assertEqual(card["provenance"]["reviewed_on"], "2026-08-17")

    def test_reproduction_artifacts_are_complete_and_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "artifacts"
            paths = save_gubser_nellore_artifacts(self.record, output)
            self.assertEqual(set(paths), {"json", "csv", "plot"})
            self.assertTrue(all(path.is_file() for path in paths.values()))
            self.assertGreater(paths["plot"].stat().st_size, 10_000)
            saved = json.loads(paths["json"].read_text(encoding="utf-8"))
            self.assertTrue(saved["passed"])
            with self.assertRaisesRegex(ValueError, "refusing to overwrite"):
                save_gubser_nellore_artifacts(self.record, output)

    def test_potential_identities_and_short_profile_are_independent_checks(self) -> None:
        self.assertIs(get_preset("cosh-calibration"), COSH_CALIBRATION)
        self.assertIs(get_preset("qcd-like"), QCD_LIKE)
        for preset in (COSH_CALIBRATION, QCD_LIKE):
            self.assertAlmostEqual(preset.potential(0.0), -12.0, places=12)
            self.assertAlmostEqual(preset.first_derivative(0.0), 0.0, places=12)
            self.assertAlmostEqual(
                preset.delta * (preset.delta - 4.0),
                preset.mass_squared,
                places=12,
            )
        profile = solve_coupled_profile(COSH_CALIBRATION, 0.5, 40)
        repeated = solve_coupled_profile(COSH_CALIBRATION, 0.5, 40)
        diagnostics = coupled_equation_diagnostics(profile)
        self.assertTrue(profile.nonlinear.success)
        self.assertLess(profile.nonlinear.final_scaled_residual, 1.0e-9)
        self.assertLess(diagnostics.maximum_boundary_residual, 1.0e-7)
        self.assertTrue(math.isfinite(profile.phi_h))
        np.testing.assert_array_equal(profile.blackening, repeated.blackening)
        np.testing.assert_array_equal(profile.warp_factor, repeated.warp_factor)
        np.testing.assert_array_equal(profile.scalar_factor, repeated.scalar_factor)

    def test_invalid_public_inputs_fail_clearly(self) -> None:
        with self.assertRaisesRegex(ValueError, "profile"):
            verify_gubser_nellore_ed(profile="unknown")
        with self.assertRaisesRegex(ValueError, "unknown Gubser"):
            get_preset("unknown")


if __name__ == "__main__":
    unittest.main()
