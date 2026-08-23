"""Analytic tests for the shared Chebyshev collocation grid."""

import unittest

import numpy as np

from holoforge.numerics import chebyshev_lobatto_grid
from holoforge.numerics.interpolation import (
    deterministic_barycentric_interpolator,
)


class ChebyshevGridTests(unittest.TestCase):
    def test_nodes_are_ascending_and_include_mapped_endpoints(self) -> None:
        grid = chebyshev_lobatto_grid(12, 2.0, 5.0)

        self.assertEqual(grid.size, 13)
        self.assertEqual(grid.nodes[0], 2.0)
        self.assertEqual(grid.nodes[-1], 5.0)
        self.assertTrue(np.all(np.diff(grid.nodes) > 0.0))
        self.assertGreater(grid.maximum_spacing, grid.minimum_spacing)

    def test_first_and_second_derivatives_are_exact_for_polynomials(self) -> None:
        grid = chebyshev_lobatto_grid(12, -0.7, 2.3)
        z = grid.nodes
        values = z**7 - 2.0 * z**4 + 0.5 * z**2 - 3.0
        exact_first = 7.0 * z**6 - 8.0 * z**3 + z
        exact_second = 42.0 * z**5 - 24.0 * z**2 + 1.0

        np.testing.assert_allclose(
            grid.first_derivative @ values,
            exact_first,
            rtol=0.0,
            atol=2.0e-10,
        )
        np.testing.assert_allclose(
            grid.second_derivative @ values,
            exact_second,
            rtol=0.0,
            atol=2.0e-8,
        )

    def test_constant_derivative_and_matrix_immutability(self) -> None:
        grid = chebyshev_lobatto_grid(10, 0.0, 4.0)
        np.testing.assert_allclose(
            grid.first_derivative @ np.ones(grid.size),
            0.0,
            rtol=0.0,
            atol=2.0e-14,
        )
        self.assertFalse(grid.nodes.flags.writeable)
        self.assertFalse(grid.first_derivative.flags.writeable)
        self.assertFalse(grid.second_derivative.flags.writeable)

    def test_invalid_inputs_fail_clearly(self) -> None:
        for invalid_degree in (True, 1, 3.5):
            with self.subTest(degree=invalid_degree):
                with self.assertRaisesRegex(ValueError, "degree"):
                    chebyshev_lobatto_grid(invalid_degree)  # type: ignore[arg-type]
        with self.assertRaisesRegex(ValueError, "lower_bound"):
            chebyshev_lobatto_grid(8, float("nan"), 1.0)
        with self.assertRaisesRegex(ValueError, "upper_bound"):
            chebyshev_lobatto_grid(8, 0.0, float("inf"))
        with self.assertRaisesRegex(ValueError, "less than"):
            chebyshev_lobatto_grid(8, 1.0, 1.0)

    def test_shared_barycentric_interpolator_is_deterministic(self) -> None:
        nodes = np.linspace(-1.0, 1.0, 9)
        values = nodes**4 - 0.5 * nodes
        first = deterministic_barycentric_interpolator(nodes, values)
        second = deterministic_barycentric_interpolator(nodes, values)
        targets = np.linspace(-0.9, 0.9, 17)
        np.testing.assert_array_equal(first(targets), second(targets))


if __name__ == "__main__":
    unittest.main()
