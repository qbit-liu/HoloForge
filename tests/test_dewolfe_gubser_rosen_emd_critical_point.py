"""Current contract tests for the reduced Phase 5B DGR EMD benchmark."""

import csv
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from holoforge.benchmarks.adapters.dewolfe_gubser_rosen_emd_finite_density import (
    DEWOLFE_GUBSER_ROSEN_FINITE_DENSITY_MODEL_CARD,
)
from holoforge.benchmarks.dewolfe_gubser_rosen_emd_critical_point import (
    ChargedSolverConfig,
    save_dewolfe_gubser_rosen_emd_finite_density_artifacts,
    verify_dewolfe_gubser_rosen_emd_finite_density,
)


PORTABLE_REGRESSION_ATOL = 1.0e-7


class DeWolfeGubserRosenPhase5BUnitTests(unittest.TestCase):
    """Keep cheap input validation in the default suite."""

    def test_invalid_solver_controls_fail_closed(self) -> None:
        with self.assertRaisesRegex(ValueError, "maximum_evaluations_factor"):
            ChargedSolverConfig(maximum_evaluations_factor=0)
        with self.assertRaisesRegex(ValueError, "root_tolerance"):
            ChargedSolverConfig(root_tolerance=0.0)


class DeWolfeGubserRosenPhase5BVerificationTests(unittest.TestCase):
    """Run the owner-approved reduced verifier once and inspect all evidence."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.record = verify_dewolfe_gubser_rosen_emd_finite_density()
        cls.payload = cls.record.to_dict()

    def test_all_seven_reduced_contract_gates_pass(self) -> None:
        checks = {
            item["id"]: item for item in self.payload["acceptance_checks"]
        }
        self.assertEqual(
            set(checks),
            {
                "charged-point-gates",
                "critical-source-coordinates",
                "critical-derivatives",
                "spectral-refinement",
                "independent-explicit-maxwell-route",
                "figure-5-scope-separation",
                "determinism",
            },
        )
        self.assertTrue(self.record.passed)
        self.assertTrue(all(item["passed"] for item in checks.values()))
        self.assertEqual(
            self.payload["results"]["summary"]["reported_state_count"], 6
        )

    def test_critical_coordinates_and_refinement_are_unchanged(self) -> None:
        result = self.payload["results"]
        source = result["critical"]["final_source_coordinates"]
        self.assertAlmostEqual(
            source["T_MeV"],
            142.9739737853875,
            delta=PORTABLE_REGRESSION_ATOL,
        )
        self.assertAlmostEqual(
            source["mu_MeV"],
            781.6937616656423,
            delta=PORTABLE_REGRESSION_ATOL,
        )
        changes = result["refinement"]["changes"]
        self.assertEqual(
            [(item["coarse_degree"], item["fine_degree"]) for item in changes],
            [(80, 120), (120, 150)],
        )
        self.assertLessEqual(changes[-1]["maximum_change"], 2.0e-3)
        self.assertEqual(result["refinement"]["ordering_failures"], [])

    def test_independent_maxwell_route_remains_inside_frozen_gate(self) -> None:
        maximum = self.payload["results"]["summary"][
            "maximum_route_observable_difference"
        ]
        self.assertLessEqual(maximum, 5.0e-6)

    def test_figure_5_and_failed_topology_extension_remain_separate(self) -> None:
        result = self.payload["results"]
        separation = result["figure_5_absolute_ordinate_comparison"]
        self.assertEqual(separation["status"], "blocked")
        self.assertFalse(separation["affects_acceptance"])
        self.assertEqual(len(result["figure_5_reference_records"]), 3)
        extension = self.payload["preserved_optional_extension"]
        self.assertIn("failed", extension["c3h_status"])
        self.assertFalse(extension["affects_reduced_core_acceptance"])

    def test_record_is_strict_json_approved_and_model_card_is_frozen(self) -> None:
        encoded = json.dumps(self.payload, allow_nan=False, sort_keys=True)
        self.assertTrue(json.loads(encoded)["passed"])
        self.assertEqual(self.payload["result_review_state"], "approved")
        self.assertEqual(self.payload["result_reviewed_by"], "Xin-Yi Liu")
        root = Path(__file__).resolve().parents[1]
        path = root / DEWOLFE_GUBSER_ROSEN_FINITE_DENSITY_MODEL_CARD.repository_path
        self.assertEqual(
            hashlib.sha256(path.read_bytes()).hexdigest(),
            DEWOLFE_GUBSER_ROSEN_FINITE_DENSITY_MODEL_CARD.sha256,
        )

    def test_artifacts_are_complete_and_fail_closed_on_overwrite(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "artifacts"
            paths = save_dewolfe_gubser_rosen_emd_finite_density_artifacts(
                self.record, output
            )
            self.assertEqual(set(paths), {"json", "csv", "plot"})
            self.assertTrue(all(path.is_file() for path in paths.values()))
            with paths["csv"].open(encoding="utf-8", newline="") as handle:
                rows = list(csv.DictReader(handle))
            self.assertEqual(len(rows), 12)
            self.assertEqual({row["route"] for row in rows}, {"primary", "explicit"})
            with self.assertRaisesRegex(ValueError, "refusing to overwrite"):
                save_dewolfe_gubser_rosen_emd_finite_density_artifacts(
                    self.record, output
                )


if __name__ == "__main__":
    unittest.main()
