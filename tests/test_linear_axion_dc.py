"""Background and UV source-map tests for the Version 0.5 preflight."""

from dataclasses import replace
import json
import unittest

import numpy as np

from holoforge.benchmarks.linear_axion_dc import (
    DEFAULT_CONDITION_LIMIT,
    DEFAULT_DC_RELATIVE_TOLERANCE,
    DEFAULT_EQUATION_TOLERANCE,
    DEFAULT_FREQUENCIES,
    DEFAULT_FLUX_TOLERANCE,
    DEFAULT_FREQUENCY_STABILITY_TOLERANCE,
    DEFAULT_HORIZON_REFINEMENT_TOLERANCE,
    DEFAULT_IMAGINARY_INTERCEPT_TOLERANCE,
    DEFAULT_INTEGRATOR_REFINEMENT_TOLERANCE,
    DEFAULT_PARAMETER_CASES,
    DEFAULT_RADIAL_DC_TOLERANCE,
    DEFAULT_SOURCE_TOLERANCE,
    DEFAULT_UV_REFINEMENT_TOLERANCE,
    LinearAxionPreflightConfig,
    blackening_function,
    master_constants,
    run_background_preflight,
    run_source_map_preflight,
    solve_linear_axion_case,
    solve_linear_axion_frequency,
    verify_linear_axion_dc,
)


class LinearAxionConventionTests(unittest.TestCase):
    def test_invalid_or_singular_limits_fail_clearly(self) -> None:
        with self.assertRaisesRegex(ValueError, "chemical_potential"):
            LinearAxionPreflightConfig(chemical_potential=0.0)
        with self.assertRaisesRegex(ValueError, "axion_gradient"):
            LinearAxionPreflightConfig(axion_gradient=0.0)
        with self.assertRaisesRegex(ValueError, "frequency"):
            LinearAxionPreflightConfig(frequency=0.0)
        with self.assertRaisesRegex(ValueError, "positive temperature"):
            LinearAxionPreflightConfig(chemical_potential=4.0)
        with self.assertRaisesRegex(ValueError, "radial_points"):
            LinearAxionPreflightConfig(radial_points=20)

    def test_background_matches_exact_solution(self) -> None:
        config = LinearAxionPreflightConfig()
        result = run_background_preflight(config)

        self.assertLessEqual(result.horizon_residual, 1.0e-12)
        self.assertLessEqual(result.temperature_relative_error, 1.0e-10)
        self.assertLessEqual(
            result.maxwell_flux_relative_variation, 1.0e-10
        )
        self.assertTrue(result.passed)
        self.assertAlmostEqual(float(blackening_function(1.0, config)), 0.0)

    def test_master_constants_satisfy_source_quadratic(self) -> None:
        config = LinearAxionPreflightConfig()
        constants = master_constants(config)
        mu = config.chemical_potential
        alpha = config.axion_gradient
        for constant in constants:
            residual = (
                mu * constant**2
                - 3.0 * config.mass_parameter * constant
                - mu * alpha**2
            )
            self.assertAlmostEqual(residual, 0.0, places=12)


class LinearAxionSourceMapTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.results = {}
        for case, mu, alpha in DEFAULT_PARAMETER_CASES:
            for frequency in DEFAULT_FREQUENCIES:
                key = (case, frequency)
                cls.results[key] = run_source_map_preflight(
                    LinearAxionPreflightConfig(
                        chemical_potential=mu,
                        axion_gradient=alpha,
                        frequency=frequency,
                    )
                )

    def test_all_frozen_cases_have_a_well_conditioned_source_map(self) -> None:
        for key, result in self.results.items():
            with self.subTest(case=key[0], frequency=key[1]):
                self.assertLess(result.condition_number, DEFAULT_CONDITION_LIMIT)
                self.assertLessEqual(
                    result.gauge_source_residual, DEFAULT_SOURCE_TOLERANCE
                )
                self.assertLessEqual(
                    result.scalar_source_residual, DEFAULT_SOURCE_TOLERANCE
                )
                self.assertLessEqual(
                    result.metric_source_residual, DEFAULT_SOURCE_TOLERANCE
                )
                self.assertTrue(result.passed)

    def test_source_matrix_imposes_unit_gauge_and_zero_invariant_source(self) -> None:
        result = self.results[("P2", 0.05)]
        amplitudes = np.asarray(result.amplitudes, dtype=np.complex128)
        sources = result.source_matrix @ amplitudes

        np.testing.assert_allclose(
            sources,
            np.asarray((1.0, 0.0), dtype=np.complex128),
            rtol=0.0,
            atol=1.0e-12,
        )
        self.assertAlmostEqual(result.gauge_source.real, 1.0, places=10)
        self.assertAlmostEqual(result.gauge_source.imag, 0.0, places=10)

    def test_frobenius_exponent_error_decreases_with_horizon_cutoff(self) -> None:
        coarse_config = LinearAxionPreflightConfig(horizon_cutoff=1.0e-6)
        fine_config = replace(coarse_config, horizon_cutoff=5.0e-7)
        coarse = run_source_map_preflight(coarse_config)
        fine = run_source_map_preflight(fine_config)

        for coarse_error, fine_error in zip(
            coarse.frobenius_exponent_errors,
            fine.frobenius_exponent_errors,
        ):
            self.assertLess(fine_error, coarse_error)
            self.assertLess(fine_error / coarse_error, 0.51)

    def test_preflight_record_is_json_serializable_and_bounded(self) -> None:
        payload = json.loads(json.dumps(self.results[("P2", 0.05)].to_dict()))

        self.assertTrue(payload["passed"])
        self.assertEqual(payload["configuration"]["r0"], 1.0)
        self.assertIn("gauge-invariant", payload["source_map_interpretation"])
        self.assertIn("no conductivity", payload["scope"])


class LinearAxionConductivityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = verify_linear_axion_dc()

    def test_reconstructed_equations_and_flux_identity_pass(self) -> None:
        for case in self.result.cases:
            with self.subTest(case=case.identifier):
                self.assertLessEqual(
                    case.maximum_equation_residual,
                    DEFAULT_EQUATION_TOLERANCE,
                )
                self.assertLessEqual(
                    case.maximum_flux_balance_residual,
                    DEFAULT_FLUX_TOLERANCE,
                )
                self.assertLessEqual(
                    case.radial_dc_relative_spread,
                    DEFAULT_RADIAL_DC_TOLERANCE,
                )

    def test_boundary_response_reproduces_all_exact_dc_values(self) -> None:
        expected = {"P1": 1.25, "P2": 2.0, "P3": 1.5}
        for case in self.result.cases:
            with self.subTest(case=case.identifier):
                self.assertAlmostEqual(
                    case.exact_dc_conductivity,
                    expected[case.identifier],
                    places=12,
                )
                self.assertLessEqual(
                    case.dc_relative_error,
                    DEFAULT_DC_RELATIVE_TOLERANCE,
                )
                self.assertLessEqual(
                    abs(case.imaginary_dc_intercept),
                    DEFAULT_IMAGINARY_INTERCEPT_TOLERANCE,
                )
                self.assertLessEqual(
                    case.frequency_fit_change,
                    DEFAULT_FREQUENCY_STABILITY_TOLERANCE,
                )

    def test_all_three_frozen_refinements_pass(self) -> None:
        for evidence in self.result.refinements:
            with self.subTest(case=evidence.case_identifier):
                self.assertLessEqual(
                    evidence.horizon_cutoff_relative_change,
                    DEFAULT_HORIZON_REFINEMENT_TOLERANCE,
                )
                self.assertLessEqual(
                    evidence.uv_endpoint_relative_change,
                    DEFAULT_UV_REFINEMENT_TOLERANCE,
                )
                self.assertLessEqual(
                    evidence.integrator_tolerance_relative_change,
                    DEFAULT_INTEGRATOR_REFINEMENT_TOLERANCE,
                )
                self.assertLess(
                    evidence.maximum_frobenius_refinement_ratio,
                    0.51,
                )

    def test_machine_record_is_json_serializable_and_scoped(self) -> None:
        payload = json.loads(json.dumps(self.result.to_dict()))

        self.assertTrue(payload["passed"])
        self.assertEqual(payload["benchmark"], "linear-axion-dc")
        self.assertEqual(len(payload["results"]["cases"]), 3)
        self.assertEqual(
            payload["primary_source"]["arxiv"], "1311.5157v2"
        )
        self.assertIn("not empirical validation", payload["scope"])

    def test_expected_invalid_case_inputs_fail_clearly(self) -> None:
        with self.assertRaisesRegex(ValueError, "identifier"):
            solve_linear_axion_case("", 1.0, 1.0)
        with self.assertRaisesRegex(ValueError, "positive temperature"):
            solve_linear_axion_case("extremal", 4.0, 1.0)

    def test_one_frequency_uses_boundary_current_not_exact_target(self) -> None:
        result = solve_linear_axion_frequency(
            LinearAxionPreflightConfig(frequency=0.08)
        )

        self.assertNotAlmostEqual(result.conductivity.real, 2.0, places=3)
        self.assertGreater(abs(result.current_response), 0.0)
        self.assertLessEqual(
            result.equation_residual, DEFAULT_EQUATION_TOLERANCE
        )
        self.assertLessEqual(result.flux_balance_residual, DEFAULT_FLUX_TOLERANCE)


if __name__ == "__main__":
    unittest.main()
