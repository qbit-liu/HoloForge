"""Scientific, numerical, and plotting tests for the v0.2 benchmark."""

import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

from holoforge.benchmarks.holographic_superconductor import (
    CondensateConfig,
    OnsetConfig,
    SUPERCONDUCTOR_DEFINITION,
    save_condensate_plot,
    solve_condensate_branch,
    solve_onset,
    verify_superconductor,
)


class SuperconductorConventionTests(unittest.TestCase):
    def test_uv_sources_are_not_conflated(self) -> None:
        conditions = SUPERCONDUCTOR_DEFINITION.boundary_conditions
        gauge = next(item for item in conditions if item.field == "phi")
        scalar = next(
            item
            for item in conditions
            if item.field == "psi" and item.location.startswith("u = 0")
        )

        self.assertIn("mu != 0", gauge.expression)
        self.assertIn("gauge-field source", gauge.role)
        self.assertIn("psi_- = 0", scalar.expression)
        self.assertIn("scalar source", scalar.role)

    def test_invalid_numerical_inputs_fail_clearly(self) -> None:
        with self.assertRaisesRegex(ValueError, "radial_cutoff"):
            OnsetConfig(radial_cutoff=0.0)
        with self.assertRaisesRegex(ValueError, "root_bracket"):
            OnsetConfig(root_bracket=(5.0, 3.0))
        with self.assertRaisesRegex(ValueError, "branch_points"):
            CondensateConfig(branch_points=3)
        with self.assertRaisesRegex(ValueError, "minimum_horizon_scalar"):
            CondensateConfig(
                minimum_horizon_scalar=2.0,
                maximum_horizon_scalar=1.0,
            )


class SuperconductorNumericalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = verify_superconductor()

    def test_linear_onset_reproduces_published_critical_temperature(self) -> None:
        self.assertAlmostEqual(
            self.result.onset.critical_mu_over_horizon,
            4.06371366,
            places=7,
        )
        self.assertAlmostEqual(
            self.result.onset.tc_over_sqrt_rho,
            0.11842676,
            places=7,
        )
        self.assertLess(self.result.cutoff_difference, 1.0e-6)

    def test_nonlinear_branch_reproduces_dimension_two_curve(self) -> None:
        branch = self.result.branch
        self.assertLess(
            branch.maximum_scalar_source_residual,
            self.result.source_tolerance,
        )
        self.assertTrue(branch.is_monotonic)
        self.assertAlmostEqual(branch.near_critical_amplitude, 144.0, delta=4.0)
        low_point = branch.lowest_temperature_point
        self.assertLess(low_point.temperature_over_tc, 0.06)
        self.assertAlmostEqual(
            low_point.sqrt_condensate_over_tc, 8.44, delta=0.1
        )
        self.assertTrue(self.result.passed)

    def test_nonlinear_observable_is_stable_under_cutoff_refinement(self) -> None:
        critical_ratio = self.result.onset.tc_over_sqrt_rho
        common = {
            "mesh_points": 250,
            "branch_points": 16,
            "tolerance": 1.0e-6,
        }
        coarse = solve_condensate_branch(
            critical_ratio,
            CondensateConfig(radial_cutoff=2.0e-5, **common),
        )
        fine = solve_condensate_branch(
            critical_ratio,
            CondensateConfig(radial_cutoff=1.0e-5, **common),
        )

        self.assertLess(
            abs(
                coarse.lowest_temperature_point.sqrt_condensate_over_tc
                - fine.lowest_temperature_point.sqrt_condensate_over_tc
            ),
            1.0e-5,
        )
        self.assertLess(
            abs(
                coarse.lowest_temperature_point.temperature_over_tc
                - fine.lowest_temperature_point.temperature_over_tc
            ),
            1.0e-6,
        )

    def test_machine_record_contains_ensemble_and_curve_evidence(self) -> None:
        payload = self.result.to_dict()
        round_trip = json.loads(json.dumps(payload))

        self.assertEqual(
            round_trip["configuration"]["quantization"],
            "Delta = 2 with psi_- = 0",
        )
        self.assertIn(
            "grand canonical", round_trip["configuration"]["onset_ensemble"]
        )
        self.assertEqual(
            round_trip["numerical_method"]["curve_axis_y"],
            "sqrt(<O_2>)/T_c",
        )
        self.assertEqual(
            len(round_trip["results"]["condensate_branch"]["points"]),
            self.result.branch.config.branch_points,
        )
        self.assertTrue(round_trip["passed"])

    @unittest.skipUnless(
        importlib.util.find_spec("matplotlib") is not None,
        "Matplotlib plot extra is not installed",
    )
    def test_plot_artifact_is_created_from_computed_curve(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "condensate.png"
            saved = save_condensate_plot(self.result, output)
            self.assertEqual(saved, output.resolve())
            self.assertTrue(output.is_file())
            self.assertGreater(output.stat().st_size, 10_000)


if __name__ == "__main__":
    unittest.main()
