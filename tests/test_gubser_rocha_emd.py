"""Scientific, numerical, artifact, and review gates for the EMD preflight."""

import hashlib
import json
import math
from pathlib import Path
import tempfile
import unittest

import numpy as np

from holoforge.benchmarks.adapters.gubser_rocha_emd import (
    GUBSER_ROCHA_MODEL_CARD,
)
from holoforge.benchmarks.gubser_rocha_emd import (
    DEFAULT_COLLOCATION_TOLERANCE,
    DEFAULT_FIELD_TOLERANCE,
    DEFAULT_POLISH_MAXIMUM_EVALUATIONS,
    DEFAULT_POLISH_TRIGGER_TOLERANCE,
    DEFAULT_REFINEMENT_ORDER_FLOOR,
    DEFAULT_REFINEMENT_TOLERANCE,
    EMDSolverConfig,
    SOURCE_ARCHIVE_SHA256,
    SOURCE_PDF_SHA256,
    charge_geometry,
    exact_factor_fields,
    exact_thermodynamics,
    gauge_coupling,
    save_gubser_rocha_artifacts,
    scalar_potential,
    scalar_potential_prime,
    scalar_potential_second,
    solve_emd_profile,
    verify_gubser_rocha_emd,
)


ROOT = Path(__file__).resolve().parents[1]


class GubserRochaEMDTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.record = verify_gubser_rocha_emd()
        cls.payload = cls.record.to_dict()
        cls.checks = {
            item["id"]: item for item in cls.payload["acceptance_checks"]
        }

    def test_amended_preflight_passes_all_declared_gates(self) -> None:
        self.assertTrue(self.record.passed)
        self.assertEqual(len(self.record.acceptance_checks), 13)
        failed = [
            identifier
            for identifier, check in self.checks.items()
            if not check["passed"]
        ]
        self.assertEqual(failed, [])
        refinement = self.payload["results"]["refinement"]
        self.assertLessEqual(
            refinement["maximum_final_change"], DEFAULT_REFINEMENT_TOLERANCE
        )
        self.assertEqual(
            refinement["ordering_floor"], DEFAULT_REFINEMENT_ORDER_FLOOR
        )
        self.assertEqual(refinement["ordering_failures"], 0)
        self.assertIn(
            "zero ordering failures",
            self.checks["spectral-refinement"]["criterion"],
        )

    def test_amended_polish_cap_reaches_accepted_library_states(self) -> None:
        self.assertEqual(
            EMDSolverConfig().polish_maximum_evaluations,
            DEFAULT_POLISH_MAXIMUM_EVALUATIONS,
        )
        self.assertEqual(DEFAULT_POLISH_MAXIMUM_EVALUATIONS, 32)
        self.assertEqual(DEFAULT_POLISH_TRIGGER_TOLERANCE, 1.0e-9)
        self.assertEqual(DEFAULT_COLLOCATION_TOLERANCE, 3.0e-9)
        self.assertTrue(self.checks["nonlinear-solver"]["passed"])
        applied_polishes = [
            row
            for row in self.payload["results"]["continuation_solves"]
            if row["nonlinear"]["polish"]["applied"]
        ]
        self.assertTrue(
            all(
                row["nonlinear"]["polish"]["library_success"]
                and 0 < row["nonlinear"]["polish"]["function_evaluations"]
                <= DEFAULT_POLISH_MAXIMUM_EVALUATIONS
                for row in applied_polishes
            )
        )
        self.assertTrue(
            all(
                row["nonlinear"]["final_success"]
                and row["nonlinear"]["final_scaled_residual"]
                <= DEFAULT_COLLOCATION_TOLERANCE
                for row in self.payload["results"]["continuation_solves"]
            )
        )

    def test_equations_constraint_flux_and_exact_fields_have_margin(self) -> None:
        for identifier in (
            "collocation-residual",
            "independent-equations",
            "einstein-constraint",
            "boundary-and-source",
            "maxwell-flux",
            "exact-fields",
        ):
            self.assertTrue(self.checks[identifier]["passed"], identifier)
        self.assertLessEqual(
            self.checks["exact-fields"]["value"], DEFAULT_FIELD_TOLERANCE
        )

    def test_source_thermodynamics_eos_low_temperature_and_neutral_gates_pass(self) -> None:
        for identifier in (
            "source-algebra",
            "source-thermodynamics",
            "equation-of-state",
            "low-temperature-relation",
            "neutral-limit-and-determinism",
        ):
            self.assertTrue(self.checks[identifier]["passed"], identifier)
        self.assertEqual(len(self.payload["results"]["cases"]), 7)
        for case in self.payload["results"]["cases"]:
            if case["xi"] > 1.0:
                self.assertIn("stability not claimed", case["stability_interpretation"])

    def test_duplicate_complete_run_is_deterministic(self) -> None:
        determinism = self.payload["results"]["determinism"]
        self.assertTrue(determinism["repeat_enabled"])
        self.assertEqual(determinism["maximum_scaled_difference"], 0.0)

    def test_record_is_strict_json_and_retains_review_boundaries(self) -> None:
        encoded = json.dumps(self.payload, allow_nan=False, sort_keys=True)
        self.assertTrue(encoded)
        self.assertEqual(self.payload["primary_source"]["pdf_sha256"], SOURCE_PDF_SHA256)
        self.assertEqual(
            self.payload["primary_source"]["source_archive_sha256"],
            SOURCE_ARCHIVE_SHA256,
        )
        self.assertEqual(self.payload["contract_review"]["review_state"], "approved")
        self.assertEqual(len(self.payload["contract_review"]["amendments"]), 3)
        self.assertEqual(
            self.payload["configuration"]["polish_trigger_tolerance"],
            DEFAULT_POLISH_TRIGGER_TOLERANCE,
        )
        self.assertEqual(
            self.payload["configuration"]["collocation_tolerance"],
            DEFAULT_COLLOCATION_TOLERANCE,
        )
        self.assertEqual(self.payload["result_review_state"], "approved")
        self.assertEqual(self.payload["result_reviewed_by"], "Xin-Yi Liu")
        self.assertEqual(self.payload["result_reviewed_on"], "2026-08-19")
        self.assertFalse(
            self.payload["primary_source"]["equation_7_specific_heats_in_scope"]
        )
        self.assertFalse(self.payload["primary_source"]["figure_1_in_scope"])
        self.assertIn(
            "top-down consistent truncation",
            self.payload["primary_source"]["model_origin"],
        )
        self.assertIn("top-down-derived", self.payload["scope"])
        self.assertIn("Source Figure 1", self.payload["scope"])
        self.assertEqual(self.payload["support_level"], "reproduced")
        self.assertIn("Owner-reviewed reproduction", self.payload["scope"])

    def test_registered_model_card_records_owner_approved_reproduction(self) -> None:
        path = ROOT / GUBSER_ROCHA_MODEL_CARD.repository_path
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        self.assertEqual(digest, GUBSER_ROCHA_MODEL_CARD.sha256)
        card = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(card["maturity"], "reproduced")
        self.assertEqual(card["provenance"]["review_status"], "approved")
        self.assertEqual(card["provenance"]["reviewed_by"], "Xin-Yi Liu")
        reproduced_claims = [
            claim for claim in card["claims"]
            if claim["support_level"] == "reproduced"
        ]
        self.assertEqual(len(reproduced_claims), 1)
        self.assertEqual(reproduced_claims[0]["review_status"], "approved")
        self.assertEqual(card["validation"]["last_verified"], "2026-08-19")
        self.assertTrue(
            all(test["status"] == "pass" for test in card["validation"]["tests"])
        )
        model_origin = next(
            item for item in card["conventions"] if item["name"] == "model origin"
        )
        self.assertIn("Top-down", model_origin["value"])
        self.assertTrue(
            any("not a bottom-up example" in item for item in card["limitations"])
        )

    def test_artifacts_are_complete_and_fail_closed_on_overwrite(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "artifacts"
            paths = save_gubser_rocha_artifacts(self.record, output)
            self.assertEqual(set(paths), {"json", "csv", "plot"})
            self.assertTrue(all(path.is_file() for path in paths.values()))
            self.assertGreater(paths["plot"].stat().st_size, 10_000)
            saved = json.loads(paths["json"].read_text(encoding="utf-8"))
            self.assertTrue(saved["passed"])
            rows = paths["csv"].read_text(encoding="utf-8").splitlines()
            self.assertEqual(len(rows), 8)
            with self.assertRaisesRegex(ValueError, "refusing to overwrite"):
                save_gubser_rocha_artifacts(self.record, output)

    def test_canonical_source_functions_and_neutral_fields(self) -> None:
        self.assertAlmostEqual(float(scalar_potential(0.0)), -12.0, places=12)
        self.assertAlmostEqual(float(scalar_potential_prime(0.0)), 0.0, places=12)
        self.assertAlmostEqual(float(scalar_potential_second(0.0)), -4.0, places=12)
        self.assertAlmostEqual(float(gauge_coupling(0.0)), 1.0, places=12)
        theta, z_h, omega = charge_geometry(0.0)
        self.assertEqual((theta, z_h, omega), (0.0, 1.0, 0.0))
        fields = exact_factor_fields(0.0, (0.0, 0.5, 1.0))
        np.testing.assert_array_equal(fields[0], np.zeros(3))
        np.testing.assert_array_equal(fields[1], np.ones(3))
        np.testing.assert_array_equal(fields[2], np.zeros(3))
        np.testing.assert_array_equal(fields[3], np.zeros(3))
        neutral = exact_thermodynamics(0.0)
        self.assertAlmostEqual(neutral.temperature, 1.0 / math.pi, places=14)

    def test_invalid_and_unapproved_solver_inputs_fail_clearly(self) -> None:
        with self.assertRaisesRegex(ValueError, "xi"):
            solve_emd_profile(-1.0, 20)
        with self.assertRaisesRegex(ValueError, "degree"):
            solve_emd_profile(0.0, 8)
        with self.assertRaisesRegex(ValueError, "lower-charge seed"):
            solve_emd_profile(0.5, 20)


if __name__ == "__main__":
    unittest.main()
