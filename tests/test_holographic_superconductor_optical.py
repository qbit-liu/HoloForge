"""Scientific tests for the Phase 4 HHH optical-conductivity extension."""

import json
import math
from pathlib import Path
import tempfile
import unittest
import warnings

import numpy as np

from holoforge.benchmarks.holographic_superconductor_optical import (
    ASYMPTOTIC_UV_FIT_MAXIMA,
    BACKGROUND_BVP_TOLERANCE,
    BACKGROUND_EQUATION_TOLERANCE,
    BACKGROUND_OVERLAP_TOLERANCE,
    BACKGROUND_SOURCE_TOLERANCE,
    BACKGROUND_TEMPERATURE_TOLERANCE,
    ConditionedBackgroundConfig,
    ENDPOINT_SPLIT_CONDITIONING_BUDGET,
    ENDPOINT_SPLIT_DEGREE_PAIRS,
    ENDPOINT_SPLIT_EQUATION_TOLERANCE,
    ENDPOINT_SPLIT_HORIZON_TOLERANCE,
    ENDPOINT_SPLIT_INTERFACE_TOLERANCE,
    ENDPOINT_SPLIT_UV_TOLERANCE,
    FIGURE_ANCHORS,
    FIGURE_2_STATUS,
    FIGURE_SOURCE_ABSOLUTE_TOLERANCE,
    FIGURE_TEMPERATURE_OVER_TC,
    HISTORICAL_NEAR_CRITICAL_TEMPERATURES,
    HORIZON_CUTOFFS,
    LITERATURE_SUPERFLUID_COEFFICIENT,
    NEAR_CRITICAL_RELATIVE_TOLERANCE,
    NEAR_CRITICAL_SPECTRAL_DEGREES,
    NEAR_CRITICAL_TEMPERATURES,
    NORMAL_CONDUCTIVITY_TOLERANCE,
    RESPONSE_RESOLUTION_TOLERANCE,
    SPECTRAL_AUDIT_DEGREES,
    SPECTRAL_CONFIRMATION_DEGREE,
    UV_TRANSFER_BULK_DEGREES,
    UV_TRANSFER_CONTROL_BOUNDARY_TOLERANCE,
    UV_TRANSFER_CONTROL_DEGREES,
    UV_TRANSFER_CONTROL_EQUATION_TOLERANCE,
    UV_TRANSFER_CONDITIONING_BUDGET,
    UV_TRANSFER_EQUATION_TOLERANCE,
    UV_TRANSFER_HORIZON_TOLERANCE,
    UV_TRANSFER_ROW_TOLERANCE,
    UV_TRANSFER_TARGET_BOUNDARY_TOLERANCE,
    UV_TRANSFER_TARGET_DEGREES,
    UV_TRANSFER_TARGET_EQUATION_TOLERANCE,
    UV_TRANSFER_TRUNCATION_TOLERANCE,
    conductivity_from_uv,
    coordinate_transform_identity_error,
    dimensionless_frequency,
    frobenius_identity_error,
    horizon_frobenius_coefficient,
    horizon_log_derivative,
    leading_uv_scalar_field_correction,
    omega_over_temperature,
    solve_conditioned_background,
    solve_dop853_response,
    solve_endpoint_split_spectral_response,
    solve_original_background_at_temperature,
    solve_riccati_dop853_response,
    save_optical_diagnostic_plot,
    solve_static_london_response,
    solve_series_transferred_spectral_response,
    solve_spectral_response,
    uv_current_coefficient,
    uv_series_transfer_coefficients,
    verify_holographic_superconductor_optical,
)


class OpticalConventionTests(unittest.TestCase):
    def test_frequency_coordinate_transform_is_invertible(self) -> None:
        for value in (0.025, 1.0, 25.0, 80.0):
            self.assertAlmostEqual(
                omega_over_temperature(dimensionless_frequency(value)),
                value,
                places=14,
            )
        self.assertLess(coordinate_transform_identity_error(0.37, 2.4), 1e-12)

    def test_frobenius_row_satisfies_the_analytic_identity(self) -> None:
        frequency = dimensionless_frequency(40.0)
        coefficient = horizon_frobenius_coefficient(frequency, 3.2)
        self.assertTrue(math.isfinite(coefficient.real))
        self.assertTrue(math.isfinite(coefficient.imag))
        self.assertLess(frobenius_identity_error(frequency, 3.2), 1e-12)

    def test_uv_current_retains_the_ingoing_factor_derivative(self) -> None:
        frequency = dimensionless_frequency(35.0)
        source = 1.0 + 0.2j
        regular_derivative = -0.4 + 0.7j
        exponent = -1j * frequency / 3.0
        expected = regular_derivative - exponent * source
        current = uv_current_coefficient(source, regular_derivative, frequency)
        self.assertAlmostEqual(current.real, expected.real, places=14)
        self.assertAlmostEqual(current.imag, expected.imag, places=14)

    def test_riccati_horizon_value_matches_the_ingoing_series(self) -> None:
        frequency = dimensionless_frequency(25.0)
        horizon_scalar = 3.2
        cutoff = 1.0e-6
        exponent = -1j * frequency / 3.0
        coefficient = horizon_frobenius_coefficient(
            frequency, horizon_scalar
        )
        expected = (
            -exponent / cutoff
            - coefficient / (1.0 + coefficient * cutoff)
        )
        value = horizon_log_derivative(
            frequency, horizon_scalar, cutoff
        )
        self.assertAlmostEqual(value.real, expected.real, places=12)
        self.assertAlmostEqual(value.imag, expected.imag, places=12)

    def test_invalid_inputs_fail_clearly(self) -> None:
        with self.assertRaisesRegex(ValueError, "omega_over_temperature"):
            dimensionless_frequency(0.0)
        with self.assertRaisesRegex(ValueError, "horizon_scalar"):
            horizon_frobenius_coefficient(1.0, -1.0)
        with self.assertRaisesRegex(ValueError, "nonzero"):
            conductivity_from_uv(0.0, 1.0, 1.0)
        with self.assertRaisesRegex(ValueError, "max_seed_ratio"):
            ConditionedBackgroundConfig(max_seed_ratio=1.051)
        with self.assertRaisesRegex(ValueError, "scalar_response"):
            leading_uv_scalar_field_correction(math.nan, 5.0e-5)
        with self.assertRaisesRegex(ValueError, "series_order"):
            uv_series_transfer_coefficients(1.0, 0.0, series_order=5)

    def test_uv_series_transfer_matches_the_frozen_recurrence(self) -> None:
        frequency = dimensionless_frequency(25.0)
        scalar_response = 7.0
        coordinate = 1.0e-5
        transfer = uv_series_transfer_coefficients(
            frequency,
            scalar_response,
            coordinate,
            series_order=4,
        )
        exponent = -1j * frequency / 3.0
        phase = np.exp(exponent * math.log1p(-coordinate))
        fourth_source = scalar_response**2 / 6.0 + frequency**4 / 24.0
        expected_field_source = (
            1.0
            - 0.5 * frequency**2 * coordinate**2
            + fourth_source * coordinate**4
        )
        expected_field_current = (
            coordinate
            - frequency**2 * coordinate**3 / 6.0
            + coordinate**4 / 4.0
        )
        self.assertAlmostEqual(
            (phase * transfer.field_source).real,
            expected_field_source,
            places=14,
        )
        self.assertAlmostEqual(
            (phase * transfer.field_current).real,
            expected_field_current,
            places=14,
        )


class OpticalNormalStateTests(unittest.TestCase):
    def test_exact_normal_conductivity_at_all_source_anchors(self) -> None:
        for frequency, _ in FIGURE_ANCHORS:
            with self.subTest(omega_over_temperature=frequency):
                result = solve_spectral_response(frequency, degree=160)
                self.assertLess(abs(result.conductivity - 1.0), 1e-8)
                self.assertLess(result.equation_residual, 1e-7)
                self.assertLess(result.uv_boundary_residual, 1e-10)
                self.assertLess(result.horizon_boundary_residual, 1e-9)

    def test_dop853_normal_state_uses_the_same_conductivity_dictionary(self) -> None:
        result = solve_dop853_response(40.0)
        self.assertLess(abs(result.conductivity - 1.0), 1.0e-3)

    def test_riccati_normal_state_passes_route_and_refinement_gates(self) -> None:
        base = solve_riccati_dop853_response(40.0)
        self.assertLess(abs(base.conductivity - 1.0), 1.0e-3)
        refinements = [
            solve_riccati_dop853_response(40.0, horizon_cutoff=cutoff)
            for cutoff in HORIZON_CUTOFFS
        ]
        refinements.extend(
            (
                solve_riccati_dop853_response(
                    40.0, uv_fit_maximum=2.5e-3
                ),
                solve_riccati_dop853_response(
                    40.0,
                    relative_tolerance=1.0e-11,
                    absolute_tolerance=1.0e-13,
                ),
            )
        )
        for refined in refinements:
            self.assertLess(
                abs(refined.conductivity - base.conductivity),
                5.0e-4 * (1.0 + abs(base.conductivity)),
            )

    def test_riccati_normal_state_passes_asymptotic_window_gate(self) -> None:
        responses = [
            solve_riccati_dop853_response(40.0, uv_fit_maximum=window)
            for window in ASYMPTOTIC_UV_FIT_MAXIMA
        ]
        for response in responses:
            self.assertLess(abs(response.conductivity - 1.0), 1.0e-3)
        self.assertLessEqual(
            abs(responses[1].conductivity - responses[0].conductivity)
            / (1.0 + abs(responses[0].conductivity)),
            5.0e-4,
        )

    def test_endpoint_split_normal_state_preserves_the_w2_stop(self) -> None:
        responses = [
            solve_endpoint_split_spectral_response(
                40.0, uv_degree=uv_degree, bulk_degree=bulk_degree
            )
            for uv_degree, bulk_degree in ENDPOINT_SPLIT_DEGREE_PAIRS
        ]
        passed = []
        for response in responses:
            self.assertGreater(
                response.uv_element_residual.maximum,
                ENDPOINT_SPLIT_EQUATION_TOLERANCE,
            )
            self.assertLessEqual(
                response.bulk_element_residual.maximum,
                ENDPOINT_SPLIT_EQUATION_TOLERANCE,
            )
            self.assertLessEqual(
                response.uv_boundary_residual, ENDPOINT_SPLIT_UV_TOLERANCE
            )
            self.assertLessEqual(
                response.horizon_boundary_residual,
                ENDPOINT_SPLIT_HORIZON_TOLERANCE,
            )
            self.assertLessEqual(
                response.interface_field_residual,
                ENDPOINT_SPLIT_INTERFACE_TOLERANCE,
            )
            self.assertLessEqual(
                response.conditioning_roundoff_budget,
                ENDPOINT_SPLIT_CONDITIONING_BUDGET,
            )
            self.assertTrue(math.isfinite(response.conductivity.real))
            self.assertTrue(math.isfinite(response.conductivity.imag))
            # This endpoint-split route is preserved as a failed W2 method,
            # not as the accepted exact-normal calculation.  Keep the real
            # 1e-8 gate in the full-pass predicate below while using the
            # already frozen observable-stability budget only to reject a
            # catastrophic diagnostic drift across linear-algebra stacks.
            self.assertLessEqual(
                abs(response.conductivity - 1.0),
                RESPONSE_RESOLUTION_TOLERANCE,
            )
            passed.append(
                response.uv_element_residual.maximum
                <= ENDPOINT_SPLIT_EQUATION_TOLERANCE
                and response.bulk_element_residual.maximum
                <= ENDPOINT_SPLIT_EQUATION_TOLERANCE
                and response.interface_derivative_residual
                <= ENDPOINT_SPLIT_INTERFACE_TOLERANCE
                and abs(response.conductivity - 1.0)
                <= NORMAL_CONDUCTIVITY_TOLERANCE
            )
        self.assertFalse(any(passed))
        for left, right in zip(responses[:-1], responses[1:]):
            self.assertLessEqual(
                abs(right.conductivity - left.conductivity)
                / (1.0 + abs(left.conductivity)),
                RESPONSE_RESOLUTION_TOLERANCE,
            )

    def test_series_transferred_normal_state_preserves_overresolved_x_ladder(
        self,
    ) -> None:
        responses = []
        for degree in UV_TRANSFER_BULK_DEGREES:
            response = solve_series_transferred_spectral_response(
                40.0, degree=degree, series_order=4
            )
            refinement = solve_series_transferred_spectral_response(
                40.0, degree=degree, series_order=3
            )
            responses.append((response, refinement))

        primary = [response for response, _ in responses]
        diagnostic = json.dumps(
            {
                "ladder": [
                    {
                        "degree": response.degree,
                        "equation_residual": response.equation_residual,
                        "residual_coordinate": (
                            response.bulk_element_residual.maximum_coordinate
                        ),
                        "transfer_field_residual": (
                            response.transfer_field_residual
                        ),
                        "transfer_derivative_residual": (
                            response.transfer_derivative_residual
                        ),
                        "horizon_boundary_residual": (
                            response.horizon_boundary_residual
                        ),
                        "conditioning_roundoff_budget": (
                            response.conditioning_roundoff_budget
                        ),
                        "conductivity_error": abs(response.conductivity - 1.0),
                        "series_truncation_change": (
                            abs(response.conductivity - refinement.conductivity)
                            / (1.0 + abs(response.conductivity))
                        ),
                    }
                    for response, refinement in responses
                ],
                "resolution_changes": [
                    abs(right.conductivity - left.conductivity)
                    / (1.0 + abs(left.conductivity))
                    for left, right in zip(primary[:-1], primary[1:])
                ],
            },
            sort_keys=True,
        )
        # X is a superseded over-resolved diagnostic.  Preserve all of its
        # physical and boundary checks, but bound backend-sensitive
        # independent differentiation by the reviewed Y control ceiling.
        self.assertLessEqual(
            max(response.equation_residual for response in primary),
            UV_TRANSFER_CONTROL_EQUATION_TOLERANCE,
            msg=diagnostic,
        )
        for response, refinement in responses:
            self.assertLessEqual(
                response.transfer_field_residual,
                UV_TRANSFER_ROW_TOLERANCE,
            )
            self.assertLessEqual(
                response.transfer_derivative_residual,
                UV_TRANSFER_ROW_TOLERANCE,
            )
            self.assertLessEqual(
                response.horizon_boundary_residual,
                UV_TRANSFER_HORIZON_TOLERANCE,
            )
            self.assertLessEqual(
                response.conditioning_roundoff_budget,
                UV_TRANSFER_CONDITIONING_BUDGET,
            )
            self.assertLessEqual(abs(response.conductivity - 1.0), 1.0e-8)
            self.assertLessEqual(
                abs(response.conductivity - refinement.conductivity)
                / (1.0 + abs(response.conductivity)),
                UV_TRANSFER_TRUNCATION_TOLERANCE,
            )
        for left, right in zip(primary[:-1], primary[1:]):
            self.assertLessEqual(
                abs(right.conductivity - left.conductivity)
                / (1.0 + abs(left.conductivity)),
                5.0e-4,
            )

    def test_revised_series_transfer_normal_control_passes(self) -> None:
        primary = []
        for degree in UV_TRANSFER_CONTROL_DEGREES:
            response = solve_series_transferred_spectral_response(
                40.0, degree=degree, series_order=4
            )
            refinement = solve_series_transferred_spectral_response(
                40.0, degree=degree, series_order=3
            )
            primary.append(response)
            self.assertLessEqual(
                response.equation_residual,
                UV_TRANSFER_CONTROL_EQUATION_TOLERANCE,
            )
            self.assertLessEqual(
                response.transfer_field_residual,
                UV_TRANSFER_CONTROL_BOUNDARY_TOLERANCE,
            )
            self.assertLessEqual(
                response.transfer_derivative_residual,
                UV_TRANSFER_CONTROL_BOUNDARY_TOLERANCE,
            )
            self.assertLessEqual(
                response.horizon_boundary_residual,
                UV_TRANSFER_CONTROL_BOUNDARY_TOLERANCE,
            )
            self.assertLessEqual(
                response.conditioning_roundoff_budget,
                UV_TRANSFER_CONDITIONING_BUDGET,
            )
            self.assertLessEqual(abs(response.conductivity - 1.0), 1.0e-8)
            self.assertLessEqual(
                abs(response.conductivity - refinement.conductivity)
                / (1.0 + abs(response.conductivity)),
                UV_TRANSFER_TRUNCATION_TOLERANCE,
            )
        for left, right in zip(primary[:-1], primary[1:]):
            self.assertLessEqual(
                abs(right.conductivity - left.conductivity)
                / (1.0 + abs(left.conductivity)),
                5.0e-4,
            )


class ConditionedBackgroundTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = solve_conditioned_background()

    def test_overlap_reproduces_the_last_original_u_state(self) -> None:
        overlap = self.result.overlap
        self.assertTrue(overlap.passed)
        self.assertLessEqual(
            overlap.mapped_equation_residual, BACKGROUND_EQUATION_TOLERANCE
        )
        self.assertLessEqual(
            overlap.mapped_boundary_residual, BACKGROUND_EQUATION_TOLERANCE
        )
        self.assertLessEqual(
            overlap.temperature_relative_error, BACKGROUND_OVERLAP_TOLERANCE
        )
        self.assertLessEqual(
            overlap.uv_relative_error, BACKGROUND_OVERLAP_TOLERANCE
        )
        self.assertLessEqual(
            overlap.horizon_relative_error, BACKGROUND_OVERLAP_TOLERANCE
        )

    def test_fixed_density_continuation_reaches_the_figure_target(self) -> None:
        target = self.result.target
        self.assertTrue(self.result.passed)
        self.assertLessEqual(
            abs(target.temperature_over_tc - FIGURE_TEMPERATURE_OVER_TC),
            BACKGROUND_TEMPERATURE_TOLERANCE,
        )
        self.assertLessEqual(
            abs(target.scalar_source), BACKGROUND_SOURCE_TOLERANCE
        )
        self.assertLessEqual(
            target.bvp_max_rms_residual, BACKGROUND_BVP_TOLERANCE
        )
        self.assertGreater(target.charge_density, 0.0)
        self.assertGreater(len(self.result.steps), 1)
        previous = self.result.overlap.conditioned.radius
        for step in self.result.steps:
            self.assertGreater(step.radius, previous)
            self.assertLessEqual(
                step.radius / previous,
                self.result.config.max_seed_ratio * (1.0 + 1.0e-12),
            )
            previous = step.radius

    def test_target_scalar_profile_includes_frozen_endpoint_expansions(self) -> None:
        coordinate = np.asarray((0.0, 1.0e-6, 0.4, 1.0 - 1.0e-6, 1.0))
        scalar = self.result.target.scalar_profile(coordinate)
        self.assertTrue(np.all(np.isfinite(scalar)))
        self.assertEqual(scalar[0], 0.0)
        self.assertAlmostEqual(
            scalar[-1], self.result.target.horizon_scalar, places=12
        )

    def test_figure_target_preserves_the_spectral_resolution_stop(self) -> None:
        responses = [
            solve_spectral_response(
                FIGURE_ANCHORS[0][0],
                self.result.target.scalar_profile,
                horizon_scalar=self.result.target.horizon_scalar,
                degree=degree,
            )
            for degree in SPECTRAL_AUDIT_DEGREES
        ]
        residuals = [response.equation_residual for response in responses]
        self.assertTrue(np.all(np.diff(residuals) < 0.0))
        self.assertGreater(residuals[-2], 1.0e-7)
        self.assertLessEqual(residuals[-1], 1.0e-7)
        self.assertFalse(
            any(
                left.equation_residual <= 1.0e-7
                and right.equation_residual <= 1.0e-7
                for left, right in zip(responses[:-1], responses[1:])
            )
        )
        confirmation = solve_spectral_response(
            FIGURE_ANCHORS[0][0],
            self.result.target.scalar_profile,
            horizon_scalar=self.result.target.horizon_scalar,
            degree=SPECTRAL_CONFIRMATION_DEGREE,
        )
        self.assertGreater(confirmation.equation_residual, 1.0e-7)
        self.assertLessEqual(confirmation.uv_boundary_residual, 1.0e-10)
        self.assertLessEqual(confirmation.horizon_boundary_residual, 1.0e-9)
        self.assertLessEqual(
            abs(confirmation.conductivity - responses[-1].conductivity),
            2.0e-3 * (1.0 + abs(confirmation.conductivity)),
        )
        self.assertTrue(math.isfinite(confirmation.condition_number))
        self.assertGreater(
            confirmation.condition_number, responses[-1].condition_number
        )
        for response in (responses[-1], confirmation):
            localization = response.residual_localization
            self.assertEqual(response.equation_residual, localization.maximum)
            self.assertIn(
                localization.maximum_region, ("uv", "bulk", "horizon")
            )
            self.assertGreater(localization.maximum_coordinate, 0.0)
            self.assertLess(localization.maximum_coordinate, 1.0)
            self.assertEqual(
                localization.maximum,
                max(
                    localization.uv_maximum,
                    localization.bulk_maximum,
                    localization.horizon_maximum,
                ),
            )
            self.assertEqual(localization.maximum_region, "uv")
            self.assertLess(localization.bulk_maximum, 1.0e-7)
        self.assertLessEqual(
            responses[-1].residual_localization.horizon_maximum, 1.0e-7
        )
        self.assertGreater(
            confirmation.residual_localization.horizon_maximum, 1.0e-7
        )

    def test_figure_target_preserves_the_unfactored_dop853_stop(self) -> None:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", RuntimeWarning)
            with self.assertRaisesRegex(RuntimeError, "DOP853 response failed"):
                solve_dop853_response(
                    FIGURE_ANCHORS[0][0],
                    self.result.target.scalar_profile,
                    horizon_scalar=self.result.target.horizon_scalar,
                )

    def test_figure_target_riccati_refinements_and_disagreement_stop(self) -> None:
        frequency = FIGURE_ANCHORS[0][0]
        scalar_profile = self.result.target.scalar_profile
        horizon_scalar = self.result.target.horizon_scalar
        spectral = solve_spectral_response(
            frequency,
            scalar_profile,
            horizon_scalar=horizon_scalar,
            degree=SPECTRAL_CONFIRMATION_DEGREE,
        )
        base = solve_riccati_dop853_response(
            frequency,
            scalar_profile,
            horizon_scalar=horizon_scalar,
        )
        self.assertGreater(
            abs(spectral.conductivity - base.conductivity),
            5.0e-4 * (1.0 + abs(spectral.conductivity)),
        )
        cutoff_large = solve_riccati_dop853_response(
            frequency,
            scalar_profile,
            horizon_scalar=horizon_scalar,
            horizon_cutoff=2.0e-6,
        )
        cutoff_small = solve_riccati_dop853_response(
            frequency,
            scalar_profile,
            horizon_scalar=horizon_scalar,
            horizon_cutoff=5.0e-7,
        )
        narrow_uv = solve_riccati_dop853_response(
            frequency,
            scalar_profile,
            horizon_scalar=horizon_scalar,
            uv_fit_maximum=2.5e-3,
        )
        tight = solve_riccati_dop853_response(
            frequency,
            scalar_profile,
            horizon_scalar=horizon_scalar,
            relative_tolerance=1.0e-11,
            absolute_tolerance=1.0e-13,
        )
        for refined in (cutoff_large, cutoff_small, tight):
            self.assertLessEqual(
                abs(refined.conductivity - base.conductivity)
                / (1.0 + abs(base.conductivity)),
                5.0e-4,
            )
        self.assertGreater(
            abs(narrow_uv.conductivity - base.conductivity)
            / (1.0 + abs(base.conductivity)),
            5.0e-4,
        )

    def test_figure_target_asymptotic_extraction_audit(self) -> None:
        target = self.result.target
        frequency = FIGURE_ANCHORS[0][0]
        primary_window, refinement_window = ASYMPTOTIC_UV_FIT_MAXIMA
        corrections = [
            leading_uv_scalar_field_correction(
                target.scalar_response, window
            )
            for window in ASYMPTOTIC_UV_FIT_MAXIMA
        ]
        self.assertLessEqual(corrections[0], 2.0e-7)
        self.assertLessEqual(corrections[1], 1.2e-8)

        primary = solve_riccati_dop853_response(
            frequency,
            target.scalar_profile,
            horizon_scalar=target.horizon_scalar,
            uv_fit_maximum=primary_window,
        )
        refinement = solve_riccati_dop853_response(
            frequency,
            target.scalar_profile,
            horizon_scalar=target.horizon_scalar,
            uv_fit_maximum=refinement_window,
        )
        cutoff_large = solve_riccati_dop853_response(
            frequency,
            target.scalar_profile,
            horizon_scalar=target.horizon_scalar,
            horizon_cutoff=2.0e-6,
            uv_fit_maximum=primary_window,
        )
        cutoff_small = solve_riccati_dop853_response(
            frequency,
            target.scalar_profile,
            horizon_scalar=target.horizon_scalar,
            horizon_cutoff=5.0e-7,
            uv_fit_maximum=primary_window,
        )
        tight = solve_riccati_dop853_response(
            frequency,
            target.scalar_profile,
            horizon_scalar=target.horizon_scalar,
            uv_fit_maximum=primary_window,
            relative_tolerance=1.0e-11,
            absolute_tolerance=1.0e-13,
        )
        for response in (refinement, cutoff_large, cutoff_small, tight):
            self.assertLessEqual(
                abs(response.conductivity - primary.conductivity)
                / (1.0 + abs(primary.conductivity)),
                5.0e-4,
            )

        for degree in (512, SPECTRAL_CONFIRMATION_DEGREE):
            spectral = solve_spectral_response(
                frequency,
                target.scalar_profile,
                horizon_scalar=target.horizon_scalar,
                degree=degree,
            )
            self.assertLessEqual(
                abs(primary.conductivity - spectral.conductivity),
                5.0e-4 * (1.0 + abs(spectral.conductivity)),
            )
            self.assertEqual(spectral.residual_localization.maximum_region, "uv")
            if degree == SPECTRAL_CONFIRMATION_DEGREE:
                self.assertGreater(spectral.equation_residual, 1.0e-7)

    def test_series_transferred_grid_passes_numerics_but_not_source_figure(
        self,
    ) -> None:
        target = self.result.target
        source_errors = []
        for frequency, source_value in FIGURE_ANCHORS:
            reference = solve_riccati_dop853_response(
                frequency,
                target.scalar_profile,
                horizon_scalar=target.horizon_scalar,
                uv_fit_maximum=ASYMPTOTIC_UV_FIT_MAXIMA[0],
            )
            primary = []
            intrinsic_passes = []
            for degree in UV_TRANSFER_TARGET_DEGREES:
                response = solve_series_transferred_spectral_response(
                    frequency,
                    target.scalar_profile,
                    scalar_response=target.scalar_response,
                    horizon_scalar=target.horizon_scalar,
                    degree=degree,
                    series_order=4,
                )
                refinement = solve_series_transferred_spectral_response(
                    frequency,
                    target.scalar_profile,
                    scalar_response=target.scalar_response,
                    horizon_scalar=target.horizon_scalar,
                    degree=degree,
                    series_order=3,
                )
                primary.append(response)
                truncation_change = (
                    abs(response.conductivity - refinement.conductivity)
                    / (1.0 + abs(response.conductivity))
                )
                route_change = (
                    abs(response.conductivity - reference.conductivity)
                    / (1.0 + abs(reference.conductivity))
                )
                intrinsic_passes.append(
                    response.equation_residual
                    <= UV_TRANSFER_TARGET_EQUATION_TOLERANCE
                    and response.transfer_field_residual
                    <= UV_TRANSFER_TARGET_BOUNDARY_TOLERANCE
                    and response.transfer_derivative_residual
                    <= UV_TRANSFER_TARGET_BOUNDARY_TOLERANCE
                    and response.horizon_boundary_residual
                    <= UV_TRANSFER_TARGET_BOUNDARY_TOLERANCE
                    and response.conditioning_roundoff_budget
                    <= UV_TRANSFER_CONDITIONING_BUDGET
                    and truncation_change <= UV_TRANSFER_TRUNCATION_TOLERANCE
                    and route_change <= 5.0e-4
                )
            pair_passes = []
            for index, (left, right) in enumerate(
                zip(primary[:-1], primary[1:])
            ):
                resolution_change = (
                    abs(right.conductivity - left.conductivity)
                    / (1.0 + abs(left.conductivity))
                )
                pair_passes.append(
                    intrinsic_passes[index]
                    and intrinsic_passes[index + 1]
                    and resolution_change <= 5.0e-4
                )
            with self.subTest(omega_over_temperature=frequency):
                self.assertTrue(all(intrinsic_passes))
                self.assertTrue(all(pair_passes))
            source_errors.append(
                abs(primary[-1].conductivity.real - source_value)
            )

        self.assertLessEqual(
            source_errors[0], FIGURE_SOURCE_ABSOLUTE_TOLERANCE
        )
        self.assertLessEqual(
            source_errors[1], FIGURE_SOURCE_ABSOLUTE_TOLERANCE
        )
        self.assertGreater(
            source_errors[2], FIGURE_SOURCE_ABSOLUTE_TOLERANCE
        )
        self.assertGreater(max(source_errors), 1.0)

class ModerateResponseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.background = solve_original_background_at_temperature(0.900)

    def test_moderate_background_hits_the_frozen_temperature(self) -> None:
        self.assertLessEqual(
            abs(self.background.temperature_over_tc - 0.900),
            BACKGROUND_TEMPERATURE_TOLERANCE,
        )
        self.assertLessEqual(
            abs(self.background.scalar_source), BACKGROUND_SOURCE_TOLERANCE
        )
        self.assertLessEqual(
            self.background.bvp_max_rms_residual, BACKGROUND_BVP_TOLERANCE
        )

    def test_moderate_response_passes_both_routes_and_refinements(self) -> None:
        frequency = 0.200
        spectral = solve_spectral_response(
            frequency,
            self.background.scalar_profile,
            horizon_scalar=self.background.horizon_scalar,
            degree=160,
        )
        base = solve_dop853_response(
            frequency,
            self.background.scalar_profile,
            horizon_scalar=self.background.horizon_scalar,
        )
        scale = 1.0 + abs(spectral.conductivity)
        self.assertLess(spectral.equation_residual, 1.0e-7)
        self.assertLess(
            abs(spectral.conductivity - base.conductivity), 5.0e-4 * scale
        )
        for cutoff in HORIZON_CUTOFFS:
            refined = solve_dop853_response(
                frequency,
                self.background.scalar_profile,
                horizon_scalar=self.background.horizon_scalar,
                horizon_cutoff=cutoff,
            )
            self.assertLess(
                abs(refined.conductivity - base.conductivity),
                5.0e-4 * (1.0 + abs(base.conductivity)),
            )
        narrow = solve_dop853_response(
            frequency,
            self.background.scalar_profile,
            horizon_scalar=self.background.horizon_scalar,
            uv_fit_maximum=2.5e-3,
        )
        tight = solve_dop853_response(
            frequency,
            self.background.scalar_profile,
            horizon_scalar=self.background.horizon_scalar,
            relative_tolerance=1.0e-11,
            absolute_tolerance=1.0e-13,
        )
        for refined in (narrow, tight):
            self.assertLess(
                abs(refined.conductivity - base.conductivity),
                5.0e-4 * (1.0 + abs(base.conductivity)),
            )

        riccati = solve_riccati_dop853_response(
            frequency,
            self.background.scalar_profile,
            horizon_scalar=self.background.horizon_scalar,
        )
        self.assertLess(
            abs(spectral.conductivity - riccati.conductivity),
            5.0e-4 * scale,
        )
        riccati_refinements = [
            solve_riccati_dop853_response(
                frequency,
                self.background.scalar_profile,
                horizon_scalar=self.background.horizon_scalar,
                horizon_cutoff=cutoff,
            )
            for cutoff in HORIZON_CUTOFFS
        ]
        riccati_refinements.extend(
            (
                solve_riccati_dop853_response(
                    frequency,
                    self.background.scalar_profile,
                    horizon_scalar=self.background.horizon_scalar,
                    uv_fit_maximum=2.5e-3,
                ),
                solve_riccati_dop853_response(
                    frequency,
                    self.background.scalar_profile,
                    horizon_scalar=self.background.horizon_scalar,
                    relative_tolerance=1.0e-11,
                    absolute_tolerance=1.0e-13,
                ),
            )
        )
        for refined in riccati_refinements:
            self.assertLess(
                abs(refined.conductivity - riccati.conductivity),
                5.0e-4 * (1.0 + abs(riccati.conductivity)),
            )

    def test_moderate_riccati_passes_asymptotic_window_gate(self) -> None:
        frequency = 0.200
        spectral = solve_spectral_response(
            frequency,
            self.background.scalar_profile,
            horizon_scalar=self.background.horizon_scalar,
            degree=160,
        )
        responses = [
            solve_riccati_dop853_response(
                frequency,
                self.background.scalar_profile,
                horizon_scalar=self.background.horizon_scalar,
                uv_fit_maximum=window,
            )
            for window in ASYMPTOTIC_UV_FIT_MAXIMA
        ]
        for response in responses:
            self.assertLessEqual(
                abs(response.conductivity - spectral.conductivity),
                5.0e-4 * (1.0 + abs(spectral.conductivity)),
            )
        self.assertLessEqual(
            abs(responses[1].conductivity - responses[0].conductivity)
            / (1.0 + abs(responses[0].conductivity)),
            5.0e-4,
        )

    def test_moderate_series_transfer_preserves_the_x2_stop(self) -> None:
        frequency = 0.200
        reference = solve_spectral_response(
            frequency,
            self.background.scalar_profile,
            horizon_scalar=self.background.horizon_scalar,
            degree=160,
        )
        primary = []
        passed = []
        for degree in UV_TRANSFER_BULK_DEGREES:
            response = solve_series_transferred_spectral_response(
                frequency,
                self.background.scalar_profile,
                scalar_response=self.background.scalar_response,
                horizon_scalar=self.background.horizon_scalar,
                degree=degree,
                series_order=4,
            )
            refinement = solve_series_transferred_spectral_response(
                frequency,
                self.background.scalar_profile,
                scalar_response=self.background.scalar_response,
                horizon_scalar=self.background.horizon_scalar,
                degree=degree,
                series_order=3,
            )
            primary.append(response)
            self.assertGreater(
                response.equation_residual,
                UV_TRANSFER_EQUATION_TOLERANCE,
            )
            self.assertLessEqual(
                response.transfer_field_residual,
                UV_TRANSFER_ROW_TOLERANCE,
            )
            self.assertLessEqual(
                response.horizon_boundary_residual,
                UV_TRANSFER_HORIZON_TOLERANCE,
            )
            self.assertLessEqual(
                response.conditioning_roundoff_budget,
                UV_TRANSFER_CONDITIONING_BUDGET,
            )
            self.assertLessEqual(
                abs(response.conductivity - refinement.conductivity)
                / (1.0 + abs(response.conductivity)),
                UV_TRANSFER_TRUNCATION_TOLERANCE,
            )
            self.assertLessEqual(
                abs(response.conductivity - reference.conductivity),
                5.0e-4 * (1.0 + abs(reference.conductivity)),
            )
            passed.append(
                response.equation_residual
                <= UV_TRANSFER_EQUATION_TOLERANCE
                and response.transfer_derivative_residual
                <= UV_TRANSFER_ROW_TOLERANCE
            )
        self.assertFalse(
            any(left and right for left, right in zip(passed[:-1], passed[1:]))
        )
        for left, right in zip(primary[:-1], primary[1:]):
            self.assertLessEqual(
                abs(right.conductivity - left.conductivity)
                / (1.0 + abs(left.conductivity)),
                5.0e-4,
            )

    def test_revised_series_transfer_moderate_control_passes(self) -> None:
        frequency = 0.200
        reference = solve_spectral_response(
            frequency,
            self.background.scalar_profile,
            horizon_scalar=self.background.horizon_scalar,
            degree=160,
        )
        primary = []
        for degree in UV_TRANSFER_CONTROL_DEGREES:
            response = solve_series_transferred_spectral_response(
                frequency,
                self.background.scalar_profile,
                scalar_response=self.background.scalar_response,
                horizon_scalar=self.background.horizon_scalar,
                degree=degree,
                series_order=4,
            )
            refinement = solve_series_transferred_spectral_response(
                frequency,
                self.background.scalar_profile,
                scalar_response=self.background.scalar_response,
                horizon_scalar=self.background.horizon_scalar,
                degree=degree,
                series_order=3,
            )
            primary.append(response)
            self.assertLessEqual(
                response.equation_residual,
                UV_TRANSFER_CONTROL_EQUATION_TOLERANCE,
            )
            self.assertLessEqual(
                response.transfer_field_residual,
                UV_TRANSFER_CONTROL_BOUNDARY_TOLERANCE,
            )
            self.assertLessEqual(
                response.transfer_derivative_residual,
                UV_TRANSFER_CONTROL_BOUNDARY_TOLERANCE,
            )
            self.assertLessEqual(
                response.horizon_boundary_residual,
                UV_TRANSFER_CONTROL_BOUNDARY_TOLERANCE,
            )
            self.assertLessEqual(
                response.conditioning_roundoff_budget,
                UV_TRANSFER_CONDITIONING_BUDGET,
            )
            self.assertLessEqual(
                abs(response.conductivity - refinement.conductivity)
                / (1.0 + abs(response.conductivity)),
                UV_TRANSFER_TRUNCATION_TOLERANCE,
            )
            self.assertLessEqual(
                abs(response.conductivity - reference.conductivity),
                5.0e-4 * (1.0 + abs(reference.conductivity)),
            )
        for left, right in zip(primary[:-1], primary[1:]):
            self.assertLessEqual(
                abs(right.conductivity - left.conductivity)
                / (1.0 + abs(left.conductivity)),
                5.0e-4,
            )


class OpticalVerificationRecordTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = verify_holographic_superconductor_optical()
        cls.payload = cls.result.to_dict()

    def test_corrected_bounded_verification_passes_current_gates(self) -> None:
        failed = {
            check.identifier
            for check in self.result.acceptance_checks
            if not check.passed
        }
        self.assertEqual(failed, set())
        self.assertTrue(self.result.passed)
        self.assertTrue(self.payload["passed"])

    def test_historical_near_critical_failure_is_preserved(self) -> None:
        evidence = self.result.historical_near_critical_failure
        self.assertEqual(
            evidence.temperatures_over_tc,
            HISTORICAL_NEAR_CRITICAL_TEMPERATURES,
        )
        self.assertEqual(evidence.status, "superseded-contract-failure")
        self.assertAlmostEqual(
            evidence.through_origin_coefficient, 19.3144523284, places=8
        )
        self.assertGreater(
            evidence.maximum_equation_residual,
            evidence.equation_tolerance,
        )

    def test_near_critical_asymptotic_fit_reproduces_source_coefficient(
        self,
    ) -> None:
        evidence = self.result.near_critical
        self.assertEqual(
            tuple(item.temperature_over_tc for item in evidence.points),
            NEAR_CRITICAL_TEMPERATURES,
        )
        self.assertGreater(evidence.slope, 23.9)
        self.assertLess(evidence.slope, 24.1)
        self.assertAlmostEqual(
            evidence.literature_coefficient,
            LITERATURE_SUPERFLUID_COEFFICIENT,
        )
        self.assertLess(
            evidence.literature_relative_error,
            NEAR_CRITICAL_RELATIVE_TOLERANCE,
        )
        self.assertLess(evidence.slope_stability, 0.10)
        self.assertLess(evidence.maximum_intercept_stability, 0.02)
        self.assertLess(evidence.maximum_route_relative_difference, 5.0e-4)
        self.assertLess(
            evidence.maximum_static_pole_relative_difference, 5.0e-4
        )
        self.assertLess(
            evidence.maximum_static_uv_refinement_change,
            RESPONSE_RESOLUTION_TOLERANCE,
        )

    def test_near_critical_spectral_ladder_passes_unchanged_residual_gate(
        self,
    ) -> None:
        for point in self.result.near_critical.points:
            static_repeat = solve_static_london_response(point.background)
            self.assertAlmostEqual(
                static_repeat.superfluid_density_over_tc,
                point.static_london.superfluid_density_over_tc,
                places=11,
            )
            for response in point.responses:
                self.assertEqual(
                    response.spectral_degree,
                    NEAR_CRITICAL_SPECTRAL_DEGREES[1],
                )
                self.assertLessEqual(
                    response.equation_residual,
                    response.equation_tolerance,
                )
                self.assertIsNotNone(response.resolution_audit)
                audit = response.resolution_audit
                assert audit is not None
                self.assertEqual(
                    audit.degree, NEAR_CRITICAL_SPECTRAL_DEGREES[2]
                )
                self.assertLessEqual(
                    audit.equation_residual,
                    audit.equation_tolerance,
                )
                self.assertLessEqual(response.numerical_gate_ratio, 1.0)

    def test_background_cutoff_repeat_passes_without_repeating_overlap(self) -> None:
        self.assertEqual(
            self.result.refined_conditioned_background.radial_cutoff,
            5.0e-6,
        )
        changes = [
            item.background_cutoff_change
            for item in self.result.figure_2_provenance.responses
        ]
        self.assertTrue(all(item is not None for item in changes))
        self.assertLessEqual(
            max(float(item) for item in changes),
            RESPONSE_RESOLUTION_TOLERANCE,
        )

    def test_figure_2_failure_is_provenance_only(self) -> None:
        evidence = self.result.figure_2_provenance
        self.assertEqual(evidence.status, FIGURE_2_STATUS)
        self.assertFalse(evidence.source_gate_passed)
        self.assertEqual(evidence.first_failed_frequency, 35.0)
        self.assertGreater(evidence.maximum_source_absolute_error, 1.0)
        self.assertAlmostEqual(
            evidence.cross_panel_mismatch_factor, 71.7816869, places=6
        )
        check_ids = {
            check.identifier for check in self.result.acceptance_checks
        }
        self.assertFalse(any("figure-2" in item for item in check_ids))

    def test_machine_record_is_strictly_finite_json(self) -> None:
        rendered = json.dumps(self.payload, allow_nan=False, sort_keys=True)
        self.assertIn('"status": "not_reproduced"', rendered)
        self.assertIn('"status": "superseded-contract-failure"', rendered)
        self.assertIn('"material_ai_involvement": true', rendered)

    def test_original_near_critical_diagnostic_is_created(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "near-critical.png"
            saved = save_optical_diagnostic_plot(self.result, output)
            self.assertEqual(saved, output)
            self.assertTrue(output.is_file())
            self.assertGreater(output.stat().st_size, 10_000)


if __name__ == "__main__":
    unittest.main()
