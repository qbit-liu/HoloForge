"""Scientific and numerical tests for the first HoloForge benchmark."""

import unittest

import numpy as np

from holoforge.benchmarks.soft_wall_vector import (
    DEFAULT_TOLERANCE,
    SoftWallConfig,
    analytic_mass_squared,
    schrodinger_potential,
    solve_spectrum,
)


class SoftWallEquationTests(unittest.TestCase):
    def test_analytic_spectrum_and_scale(self) -> None:
        values = analytic_mass_squared(num_modes=4, kappa_gev=0.5)
        np.testing.assert_allclose(values, [1.0, 2.0, 3.0, 4.0])

    def test_potential_restores_kappa_dimensions(self) -> None:
        z = np.array([1.0, 2.0])
        values = schrodinger_potential(z, kappa_gev=0.5)
        expected = 0.5**4 * z**2 + 3.0 / (4.0 * z**2)
        np.testing.assert_allclose(values, expected)

    def test_invalid_physical_and_numerical_inputs_fail(self) -> None:
        with self.assertRaisesRegex(ValueError, "kappa"):
            SoftWallConfig(kappa_gev=0.0)
        with self.assertRaisesRegex(ValueError, "kappa"):
            SoftWallConfig(kappa_gev="not-a-number")  # type: ignore[arg-type]
        with self.assertRaisesRegex(ValueError, "grid_points"):
            SoftWallConfig(grid_points=2)
        with self.assertRaisesRegex(ValueError, "z_max"):
            SoftWallConfig(z_max_gev_inverse=-1.0)
        with self.assertRaisesRegex(ValueError, "num_modes"):
            analytic_mass_squared(num_modes=0, kappa_gev=1.0)
        with self.assertRaisesRegex(ValueError, "z_gev_inverse"):
            schrodinger_potential([0.0, 1.0], kappa_gev=1.0)


class SoftWallNumericalTests(unittest.TestCase):
    def test_default_solver_meets_declared_acceptance_tolerance(self) -> None:
        result = solve_spectrum(SoftWallConfig(), num_modes=4)
        np.testing.assert_allclose(
            result.analytic_mass_squared_gev2,
            [4.0, 8.0, 12.0, 16.0],
            rtol=0.0,
            atol=1.0e-14,
        )
        self.assertLessEqual(result.max_relative_error, DEFAULT_TOLERANCE)

    def test_grid_refinement_reduces_spectral_error(self) -> None:
        coarse = solve_spectrum(SoftWallConfig(grid_points=300), num_modes=4)
        fine = solve_spectrum(SoftWallConfig(grid_points=600), num_modes=4)

        observed_order = np.log(
            coarse.max_relative_error / fine.max_relative_error
        ) / np.log(
            coarse.grid_spacing_gev_inverse
            / fine.grid_spacing_gev_inverse
        )

        self.assertLess(fine.max_relative_error, coarse.max_relative_error)
        self.assertGreater(observed_order, 1.8)
        self.assertLess(observed_order, 2.2)

    def test_dimensionless_solution_is_scale_covariant(self) -> None:
        unit_scale = solve_spectrum(
            SoftWallConfig(kappa_gev=1.0, grid_points=600), num_modes=3
        )
        half_scale = solve_spectrum(
            SoftWallConfig(kappa_gev=0.5, grid_points=600), num_modes=3
        )
        np.testing.assert_allclose(
            half_scale.numerical_mass_squared_gev2,
            0.25 * unit_scale.numerical_mass_squared_gev2,
            rtol=1.0e-11,
            atol=1.0e-12,
        )


if __name__ == "__main__":
    unittest.main()
