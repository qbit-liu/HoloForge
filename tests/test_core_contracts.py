"""Tests for the shared v0.2 benchmark contracts."""

import unittest

from holoforge.benchmarks.soft_wall_vector import (
    SoftWallConfig,
    solve_spectrum,
)
from holoforge.core import BoundaryConditionSpec


class CoreContractTests(unittest.TestCase):
    def test_boundary_condition_preserves_physical_role(self) -> None:
        condition = BoundaryConditionSpec(
            field="phi",
            location="UV",
            role="source",
            expression="phi(0) = mu",
            interpretation="Nonzero chemical-potential source.",
        )
        self.assertEqual(condition.to_dict()["role"], "source")
        self.assertIn("Nonzero", condition.to_dict()["interpretation"])

    def test_soft_wall_uses_common_verification_envelope(self) -> None:
        payload = solve_spectrum(
            SoftWallConfig(grid_points=600), num_modes=2
        ).to_dict(tolerance=2.0e-4)

        self.assertEqual(payload["benchmark"], "soft-wall-vector")
        self.assertEqual(payload["background"]["id"], "quadratic-soft-wall-ads5")
        self.assertEqual(payload["equations"][0]["id"], "vector-schrodinger")
        self.assertEqual(len(payload["boundary_conditions"]), 2)
        self.assertEqual(
            payload["solvers"][0]["library_function"],
            "scipy.linalg.eigvalsh_tridiagonal",
        )
        self.assertTrue(payload["acceptance_checks"][0]["passed"])


if __name__ == "__main__":
    unittest.main()
