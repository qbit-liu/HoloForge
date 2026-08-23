"""Current contract tests for the Phase 4 HHH optical benchmark."""

import hashlib
import json
import math
from pathlib import Path
import tempfile
import unittest

from holoforge.benchmarks.adapters.holographic_superconductor_optical import (
    SUPERCONDUCTOR_OPTICAL_MODEL_CARD,
)
from holoforge.benchmarks.holographic_superconductor_optical import (
    FIGURE_2_STATUS,
    ConditionedBackgroundConfig,
    conductivity_from_uv,
    coordinate_transform_identity_error,
    dimensionless_frequency,
    frobenius_identity_error,
    save_optical_diagnostic_plot,
    verify_holographic_superconductor_optical,
)


PORTABLE_REGRESSION_ATOL = 1.0e-8


class OpticalContractUnitTests(unittest.TestCase):
    """Keep cheap convention and fail-closed checks in default discovery."""

    def test_frequency_dictionary_and_ingoing_identity(self) -> None:
        self.assertAlmostEqual(
            dimensionless_frequency(1.0), 3.0 / (4.0 * math.pi), places=14
        )
        self.assertLess(coordinate_transform_identity_error(0.37, 2.4), 1e-12)
        self.assertLess(
            frobenius_identity_error(dimensionless_frequency(40.0), 3.2),
            1e-12,
        )

    def test_invalid_inputs_fail_closed(self) -> None:
        with self.assertRaisesRegex(ValueError, "omega_over_temperature"):
            dimensionless_frequency(0.0)
        with self.assertRaisesRegex(ValueError, "nonzero"):
            conductivity_from_uv(0.0, 1.0, 1.0)
        with self.assertRaisesRegex(ValueError, "max_seed_ratio"):
            ConditionedBackgroundConfig(max_seed_ratio=1.051)


class OpticalCurrentVerificationTests(unittest.TestCase):
    """Run the accepted verifier once and inspect its complete evidence."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.result = verify_holographic_superconductor_optical()
        cls.payload = cls.result.to_dict()

    def test_all_twelve_current_gates_pass(self) -> None:
        expected = {
            "protected-hhh-benchmark",
            "optical-convention-identities",
            "optical-backgrounds",
            "optical-response-numerics",
            "independent-response-route",
            "exact-normal-conductivity",
            "near-critical-literature-coefficient",
            "near-critical-fit-stability",
            "static-london-numerics",
            "static-finite-frequency-agreement",
            "low-temperature-condensate-scale",
            "causality-passivity-sanity",
        }
        checks = {item.identifier: item for item in self.result.acceptance_checks}
        self.assertEqual(set(checks), expected)
        self.assertTrue(all(item.passed for item in checks.values()))
        self.assertTrue(self.result.passed)
        self.assertTrue(self.payload["passed"])

    def test_owner_approved_quantities_are_unchanged(self) -> None:
        near = self.result.near_critical
        self.assertAlmostEqual(
            near.slope,
            23.96884334975214,
            delta=PORTABLE_REGRESSION_ATOL,
        )
        self.assertAlmostEqual(
            near.finite_frequency_slope,
            23.968833072939002,
            delta=PORTABLE_REGRESSION_ATOL,
        )
        self.assertAlmostEqual(
            self.result.low_temperature_condensate_scale,
            8.443622405101506,
            delta=PORTABLE_REGRESSION_ATOL,
        )

    def test_independent_residuals_and_routes_remain_inside_frozen_gates(
        self,
    ) -> None:
        self.assertLessEqual(
            max(item.numerical_gate_ratio for item in self.result.reported_responses),
            1.0,
        )
        self.assertLessEqual(
            self.result.near_critical.maximum_static_pole_relative_difference,
            5.0e-4,
        )

    def test_figure_2_remains_a_non_inferential_non_reproduction(self) -> None:
        evidence = self.result.figure_2_provenance
        self.assertEqual(evidence.status, FIGURE_2_STATUS)
        self.assertFalse(evidence.source_gate_passed)
        self.assertFalse(
            any(
                "figure-2" in item.identifier
                for item in self.result.acceptance_checks
            )
        )

    def test_record_is_strict_json_and_model_card_bytes_are_frozen(self) -> None:
        encoded = json.dumps(self.payload, allow_nan=False, sort_keys=True)
        self.assertIn('"status": "not_reproduced"', encoded)
        root = Path(__file__).resolve().parents[1]
        path = root / SUPERCONDUCTOR_OPTICAL_MODEL_CARD.repository_path
        self.assertEqual(
            hashlib.sha256(path.read_bytes()).hexdigest(),
            SUPERCONDUCTOR_OPTICAL_MODEL_CARD.sha256,
        )

    def test_original_diagnostic_artifact_is_created(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "near-critical.png"
            self.assertEqual(
                save_optical_diagnostic_plot(self.result, output), output
            )
            self.assertTrue(output.is_file())
            self.assertGreater(output.stat().st_size, 10_000)


if __name__ == "__main__":
    unittest.main()
