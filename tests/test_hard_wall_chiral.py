"""Scientific, numerical, artifact, and review-state gates for Phase 3."""

import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from holoforge.benchmarks.adapters.hard_wall_chiral import (
    HARD_WALL_CHIRAL_MODEL_CARD,
)
from holoforge.benchmarks.hard_wall_chiral import (
    SOURCE_ARCHIVE_SHA256,
    SOURCE_PDF_SHA256,
    save_hard_wall_chiral_artifacts,
    solve_axial_zero_dop853,
    solve_spectral_mode,
    verify_hard_wall_chiral,
)


ROOT = Path(__file__).resolve().parents[1]


class HardWallChiralTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.record = verify_hard_wall_chiral()
        cls.payload = cls.record.to_dict()
        cls.checks = {
            item["id"]: item for item in cls.payload["acceptance_checks"]
        }

    def test_complete_contract_passes_and_records_owner_acceptance(self) -> None:
        self.assertTrue(self.record.passed)
        self.assertEqual(len(self.record.acceptance_checks), 11)
        self.assertTrue(all(item.passed for item in self.record.acceptance_checks))
        self.assertEqual(self.payload["result_review_state"], "approved")
        self.assertEqual(self.payload["result_reviewed_by"], "Xin-Yi Liu")
        self.assertEqual(self.payload["result_reviewed_on"], "2026-08-20")
        self.assertIn("owner-approved", self.payload["scope"])

    def test_table_ii_reproduction_labels_fits_and_predictions(self) -> None:
        rows = {
            row["observable"]: row for row in self.payload["results"]["table"]
        }
        self.assertEqual(len(rows), 7)
        self.assertEqual(
            {
                key
                for key, row in rows.items()
                if row["source_role"] == "source fit target"
            },
            {"m_pi_MeV", "m_rho_MeV", "f_pi_MeV"},
        )
        self.assertLessEqual(
            max(row["relative_error"] for row in rows.values()), 1.0e-2
        )
        self.assertAlmostEqual(rows["m_pi_MeV"]["computed"], 139.5852394, places=5)
        self.assertAlmostEqual(rows["m_a1_MeV"]["computed"], 1358.243178, places=5)

    def test_spectrum_accounting_is_source_blind_and_finite(self) -> None:
        final = self.payload["results"]["levels"][-1]
        self.assertEqual(final["degree"], 96)
        for kind in ("vector", "axial", "pion"):
            mode = final["modes"][kind]
            accounting = mode["spectrum_accounting"]
            self.assertGreater(accounting["raw_count"], 0)
            self.assertGreater(accounting["admissible_count"], 0)
            self.assertFalse(accounting["source_value_used_for_selection"])
            self.assertLessEqual(
                mode["diagnostics"]["maximum_equation_residual"], 1.0e-7
            )
            self.assertLessEqual(
                mode["diagnostics"]["maximum_boundary_residual"], 1.0e-8
            )

    def test_refinement_and_independent_routes_have_margin(self) -> None:
        summary = self.payload["results"]["summary"]
        self.assertLessEqual(summary["maximum_final_refinement"], 2.0e-4)
        self.assertEqual(summary["refinement_ordering_failures"], 0)
        self.assertLessEqual(summary["maximum_cutoff_change"], 2.0e-4)
        self.assertLessEqual(summary["maximum_cross_route_difference"], 1.0e-3)
        self.assertLessEqual(summary["maximum_fpi_route_difference"], 1.0e-7)
        self.assertLessEqual(summary["maximum_fpi_log_slope_error"], 1.0e-5)

    def test_gmor_approaches_one_monotonically(self) -> None:
        rows = self.payload["results"]["gmor"]
        self.assertEqual([row["m_q_factor"] for row in rows], [1.0, 0.5, 0.25, 0.125])
        errors = [row["absolute_error"] for row in rows]
        self.assertTrue(all(later < earlier for earlier, later in zip(errors, errors[1:])))
        self.assertLessEqual(errors[-1], 1.0e-2)

    def test_duplicate_complete_run_is_deterministic(self) -> None:
        determinism = self.payload["results"]["determinism"]
        self.assertTrue(determinism["repeat_enabled"])
        self.assertLessEqual(determinism["maximum_scaled_difference"], 1.0e-11)
        self.assertTrue(self.checks["determinism"]["passed"])

    def test_source_digests_and_strict_json_are_preserved(self) -> None:
        self.assertEqual(
            self.payload["primary_source"]["pdf_sha256"], SOURCE_PDF_SHA256
        )
        self.assertEqual(
            self.payload["primary_source"]["source_archive_sha256"],
            SOURCE_ARCHIVE_SHA256,
        )
        self.assertTrue(json.dumps(self.payload, allow_nan=False, sort_keys=True))
        self.assertTrue(self.payload["generated_by_ai"])

    def test_model_card_digest_and_owner_reviewed_result_claim(self) -> None:
        path = ROOT / HARD_WALL_CHIRAL_MODEL_CARD.repository_path
        self.assertEqual(
            hashlib.sha256(path.read_bytes()).hexdigest(),
            HARD_WALL_CHIRAL_MODEL_CARD.sha256,
        )
        card = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(card["claims"][1]["review_status"], "approved")
        self.assertEqual(card["claims"][1]["reviewed_by"], "Xin-Yi Liu")
        self.assertEqual(card["claims"][1]["reviewed_on"], "2026-08-20")
        self.assertEqual(card["provenance"]["review_status"], "approved")
        self.assertEqual(card["provenance"]["reviewed_by"], "Xin-Yi Liu")
        self.assertEqual(card["provenance"]["reviewed_on"], "2026-08-20")
        self.assertIn("fit targets", " ".join(card["limitations"]))

    def test_artifacts_are_complete_and_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "artifacts"
            paths = save_hard_wall_chiral_artifacts(self.record, output)
            self.assertEqual(set(paths), {"json", "csv", "plot"})
            self.assertTrue(all(path.is_file() for path in paths.values()))
            self.assertGreater(paths["plot"].stat().st_size, 10_000)
            saved = json.loads(paths["json"].read_text(encoding="utf-8"))
            self.assertTrue(saved["passed"])
            self.assertEqual(saved["result_review_state"], "approved")
            self.assertEqual(saved["result_reviewed_by"], "Xin-Yi Liu")
            with self.assertRaisesRegex(ValueError, "refusing to overwrite"):
                save_hard_wall_chiral_artifacts(self.record, output)

    def test_public_inputs_fail_clearly(self) -> None:
        with self.assertRaisesRegex(ValueError, "kind"):
            solve_spectral_mode("unknown", 64)
        with self.assertRaisesRegex(ValueError, "degree"):
            solve_spectral_mode("vector", 20)
        with self.assertRaisesRegex(ValueError, "mhat"):
            solve_spectral_mode("pion", 64, mhat=-1.0)
        with self.assertRaisesRegex(ValueError, "epsilon"):
            solve_axial_zero_dop853(0.0)


if __name__ == "__main__":
    unittest.main()
