"""Tests for reusable covariance-aware comparison transformations."""

import unittest

import numpy as np

from holoforge.core import normalize_spectrum


class NormalizedSpectrumTests(unittest.TestCase):
    def test_ratios_and_shared_denominator_covariance(self) -> None:
        masses = np.array([2.0, 4.0, 6.0])
        covariance = np.diag([0.1**2, 0.2**2, 0.3**2])

        result = normalize_spectrum(masses, covariance)

        np.testing.assert_allclose(result.ratios, [1.0, 2.0, 3.0])
        np.testing.assert_allclose(result.ratio_covariance[0], 0.0, atol=1.0e-15)
        np.testing.assert_allclose(result.ratio_covariance[:, 0], 0.0, atol=1.0e-15)

        expected_covariance_12 = (
            masses[1] * masses[2] * covariance[0, 0] / masses[0] ** 4
        )
        self.assertAlmostEqual(
            result.ratio_covariance[1, 2], expected_covariance_12
        )
        self.assertGreater(result.ratio_covariance[1, 2], 0.0)

    def test_jacobian_matches_finite_difference(self) -> None:
        masses = np.array([3.0, 5.0, 8.0])
        result = normalize_spectrum(masses, np.eye(3))
        step = 1.0e-6

        numerical_jacobian = np.empty((3, 3), dtype=float)
        for column in range(3):
            offset = np.zeros(3)
            offset[column] = step
            plus = normalize_spectrum(masses + offset).ratios
            minus = normalize_spectrum(masses - offset).ratios
            numerical_jacobian[:, column] = (plus - minus) / (2.0 * step)

        np.testing.assert_allclose(
            result.jacobian, numerical_jacobian, rtol=1.0e-9, atol=1.0e-10
        )

    def test_ratios_and_covariance_are_scale_invariant(self) -> None:
        masses = np.array([1.0, 1.8, 2.4])
        covariance = np.diag([0.01, 0.04, 0.09])
        scale = 7.0

        original = normalize_spectrum(masses, covariance)
        rescaled = normalize_spectrum(
            scale * masses, scale**2 * covariance
        )

        np.testing.assert_allclose(rescaled.ratios, original.ratios)
        np.testing.assert_allclose(
            rescaled.ratio_covariance, original.ratio_covariance
        )

    def test_record_preserves_labels_and_covariance(self) -> None:
        result = normalize_spectrum([1.0, 2.0], np.diag([0.01, 0.04]))
        record = result.to_dict(labels=["ground", "first"])

        self.assertEqual(record["entries"][0]["label"], "ground")
        self.assertEqual(record["entries"][1]["ratio"], 2.0)
        self.assertEqual(len(record["ratio_covariance"]), 2)
        with self.assertRaisesRegex(ValueError, "labels"):
            result.to_dict(labels=["ground"])

    def test_invalid_inputs_fail_clearly(self) -> None:
        with self.assertRaisesRegex(ValueError, "masses"):
            normalize_spectrum([1.0])
        with self.assertRaisesRegex(ValueError, "positive"):
            normalize_spectrum([1.0, 0.0])
        with self.assertRaisesRegex(ValueError, "anchor_index"):
            normalize_spectrum([1.0, 2.0], anchor_index=2)
        with self.assertRaisesRegex(ValueError, "shape"):
            normalize_spectrum([1.0, 2.0], np.eye(3))
        with self.assertRaisesRegex(ValueError, "symmetric"):
            normalize_spectrum([1.0, 2.0], [[1.0, 1.0], [0.0, 1.0]])
        with self.assertRaisesRegex(ValueError, "positive semidefinite"):
            normalize_spectrum([1.0, 2.0], [[1.0, 2.0], [2.0, 1.0]])


if __name__ == "__main__":
    unittest.main()
