"""Scientific and numerical checks for the hard-wall vector benchmark."""

import unittest

import numpy as np

from holoforge.benchmarks.hard_wall_vector import (
    DEFAULT_CROSS_SOLVER_TOLERANCE,
    DEFAULT_RATIO_TOLERANCE,
    HardWallConfig,
    analytic_dimensionless_masses,
    hard_wall_cutoff_refinement,
    solve_hard_wall_spectrum,
)


class HardWallEquationTests(unittest.TestCase):
    def test_analytic_spectrum_uses_bessel_zeros(self) -> None:
        values = analytic_dimensionless_masses(4)
        np.testing.assert_allclose(
            values,
            [2.4048255577, 5.5200781103, 8.6537279129, 11.7915344391],
            rtol=0.0,
            atol=1.0e-10,
        )

    def test_invalid_inputs_fail_clearly(self) -> None:
        with self.assertRaisesRegex(ValueError, "z_m"):
            HardWallConfig(z_m_gev_inverse=0.0)
        with self.assertRaisesRegex(ValueError, "epsilon_fraction"):
            HardWallConfig(epsilon_fraction=1.0)
        with self.assertRaisesRegex(ValueError, "mesh_points"):
            HardWallConfig(collocation_mesh_points=10)
        with self.assertRaisesRegex(ValueError, "num_modes"):
            analytic_dimensionless_masses(0)
        with self.assertRaisesRegex(ValueError, "method"):
            solve_hard_wall_spectrum(method="unknown")
        with self.assertRaisesRegex(ValueError, "at least three"):
            hard_wall_cutoff_refinement(cutoff_fractions=[1.0e-2, 1.0e-3])
        with self.assertRaisesRegex(ValueError, "strictly decreasing"):
            hard_wall_cutoff_refinement(
                cutoff_fractions=[1.0e-2, 2.0e-2, 1.0e-3]
            )


class HardWallNumericalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.config = HardWallConfig()
        cls.shooting = solve_hard_wall_spectrum(
            cls.config, num_modes=4, method="shooting"
        )
        cls.collocation = solve_hard_wall_spectrum(
            cls.config, num_modes=4, method="collocation"
        )

    def test_shooting_meets_analytic_ratio_tolerance(self) -> None:
        self.assertLessEqual(
            self.shooting.max_ratio_relative_error, DEFAULT_RATIO_TOLERANCE
        )

    def test_collocation_meets_analytic_ratio_tolerance(self) -> None:
        self.assertLessEqual(
            self.collocation.max_ratio_relative_error, DEFAULT_RATIO_TOLERANCE
        )

    def test_independent_routes_agree(self) -> None:
        differences = np.abs(
            self.shooting.mass_ratios - self.collocation.mass_ratios
        ) / self.collocation.mass_ratios
        self.assertLessEqual(
            float(np.max(differences[1:])), DEFAULT_CROSS_SOLVER_TOLERANCE
        )

    def test_scale_changes_masses_but_not_ratios(self) -> None:
        doubled_wall = solve_hard_wall_spectrum(
            HardWallConfig(z_m_gev_inverse=2.0),
            num_modes=3,
            method="shooting",
        )
        np.testing.assert_allclose(
            doubled_wall.dimensionless_masses,
            self.shooting.dimensionless_masses[:3],
            rtol=1.0e-11,
            atol=1.0e-12,
        )
        np.testing.assert_allclose(
            doubled_wall.masses_gev,
            0.5 * self.shooting.masses_gev[:3],
            rtol=1.0e-11,
            atol=1.0e-12,
        )
        np.testing.assert_allclose(
            doubled_wall.mass_ratios,
            self.shooting.mass_ratios[:3],
            rtol=1.0e-11,
            atol=1.0e-12,
        )

    def test_record_states_scope_and_finite_cutoff(self) -> None:
        record = self.shooting.to_dict()
        self.assertTrue(record["passed"])
        self.assertIn("not precision validation", record["scope"])
        self.assertTrue(
            record["numerical_method"][
                "finite_cutoff_is_separate_from_solver_tolerance"
            ]
        )

    def test_three_level_cutoff_refinement_improves(self) -> None:
        study = hard_wall_cutoff_refinement(num_modes=4, method="shooting")
        self.assertEqual(len(study.results), 3)
        self.assertTrue(study.improves_at_every_level)
        self.assertLess(
            study.max_ratio_relative_errors[-1],
            study.max_ratio_relative_errors[0],
        )
        self.assertIn("finite-cutoff", study.to_dict()["interpretation"])


if __name__ == "__main__":
    unittest.main()
