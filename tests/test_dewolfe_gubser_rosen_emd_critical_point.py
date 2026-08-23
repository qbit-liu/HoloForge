"""Scientific and interface checks for the finite-density DGR EMD example."""

import csv
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

import numpy as np

from holoforge.benchmarks.dewolfe_gubser_rosen_emd import gauge_coupling
from holoforge.benchmarks.adapters.dewolfe_gubser_rosen_emd_finite_density import (
    DEWOLFE_GUBSER_ROSEN_FINITE_DENSITY_MODEL_CARD,
)
from holoforge.benchmarks.dewolfe_gubser_rosen_emd_critical_point import (
    ChargedSolverConfig,
    charged_equation_diagnostics,
    charged_point_from_profile,
    explicit_maxwell_diagnostics,
    explicit_maxwell_point_from_profile,
    explicit_noether_diagnostics,
    save_dewolfe_gubser_rosen_emd_finite_density_artifacts,
    solve_charged_profile,
    solve_explicit_maxwell_profile,
    verify_dewolfe_gubser_rosen_emd_finite_density,
)


class DeWolfeGubserRosenPhase5BPreflightTests(unittest.TestCase):
    """Exercise one charged point without running the still-closed full scan."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.profile = solve_charged_profile(4.84, 0.40, 80)
        cls.point = charged_point_from_profile(cls.profile)
        cls.diagnostics = charged_equation_diagnostics(cls.profile)
        cls.explicit_profile = solve_explicit_maxwell_profile(cls.profile)
        cls.explicit_point = explicit_maxwell_point_from_profile(
            cls.explicit_profile
        )
        cls.explicit_diagnostics = explicit_maxwell_diagnostics(
            cls.explicit_profile, cls.profile
        )

    def test_selected_point_passes_implemented_equation_and_constraint_checks(
        self,
    ) -> None:
        self.assertTrue(self.profile.nonlinear.success)
        self.assertTrue(np.isfinite(self.diagnostics.maxwell_equation))
        self.assertLessEqual(
            self.profile.nonlinear.final_scaled_residual, 1.0e-6
        )
        self.assertLessEqual(
            self.diagnostics.maximum_evaluated_equation_residual, 1.0e-5
        )
        self.assertLessEqual(self.diagnostics.constraint, 1.0e-5)
        self.assertLessEqual(self.diagnostics.maxwell_equation, 1.0e-7)
        self.assertLessEqual(
            self.diagnostics.gauss_flux_relative_drift, 1.0e-7
        )
        self.assertLessEqual(
            self.diagnostics.maximum_boundary_residual, 1.0e-7
        )
        self.assertLessEqual(
            self.diagnostics.phi_h_target_relative_error, 1.0e-7
        )
        self.assertLessEqual(
            self.diagnostics.eta_algebraic_consistency_error, 1.0e-7
        )
        self.assertGreater(self.diagnostics.minimum_blackening_interior, 0.0)
        self.assertLess(self.diagnostics.horizon_blackening_derivative, 0.0)
        self.assertLessEqual(
            self.diagnostics.electric_potential_horizon, 1.0e-12
        )
        self.assertLess(
            self.diagnostics.maximum_electric_potential_z_derivative, 0.0
        )
        self.assertLessEqual(
            self.diagnostics.chemical_potential_reconstruction_relative_error,
            1.0e-9,
        )
        self.assertLessEqual(
            self.diagnostics.uv_minus_phi2_q_over_2_relative_error,
            1.0e-7,
        )
        self.assertAlmostEqual(
            self.diagnostics.uv_minus_phi2,
            self.profile.q / 2.0,
            places=7,
        )

    def test_orientation_and_source_neighborhood_coordinates_are_consistent(
        self,
    ) -> None:
        self.assertGreater(self.profile.q, 0.0)
        self.assertAlmostEqual(self.profile.phi_h, 4.84, places=12)
        self.assertAlmostEqual(self.profile.eta, 0.40, places=12)
        self.assertLessEqual(abs(self.point.temperature_mev - 143.0), 5.0)
        self.assertLessEqual(
            abs(self.point.chemical_potential_mev - 783.0), 10.0
        )

    def test_canonical_density_and_source_ordinate_remain_distinct(self) -> None:
        # The physical density remains rho=q/2 at kappa_5=1.  The digitized
        # source-artwork ordinate is only a label until its dictionary is
        # independently resolved; it must never replace the numerical value.
        self.assertAlmostEqual(
            self.point.density, self.profile.q / 2.0, places=14
        )
        serialized = self.point.to_dict()
        self.assertIn("rho_canonical_BH", serialized)
        self.assertEqual(
            serialized["rho_canonical_BH"], self.profile.q / 2.0
        )
        self.assertNotIn("rho_BH", serialized)
        self.assertNotIn("rho_source_figure5", serialized)
        self.assertEqual(serialized["review_state"], "approved")
        self.assertEqual(serialized["reviewed_by"], "Xin-Yi Liu")
        self.assertEqual(serialized["reviewed_on"], "2026-08-23")
        self.assertEqual(
            serialized["density_normalization_state"],
            "canonical-resolved-source-ordinate-blocked",
        )
        self.assertEqual(
            serialized["figure_5_axes"],
            {"abscissa": "mu_BH", "ordinate": "rho_source_figure5"},
        )
        verification = serialized["figure_5_verification"]
        self.assertEqual(
            verification["canonical_topology"]["coordinates"],
            ["rho_canonical_BH", "mu_BH"],
        )
        self.assertEqual(
            verification["absolute_ordinate_comparison"]["source_ordinate"],
            "rho_source_figure5",
        )
        self.assertEqual(
            verification["absolute_ordinate_comparison"]["status"],
            "blocked",
        )

    def test_inverse_f_h_squared_value_is_non_inferential_diagnostic(
        self,
    ) -> None:
        serialized = self.point.to_dict()
        f_h = float(gauge_coupling(self.profile.phi_h))
        self.assertAlmostEqual(
            serialized["rho_inverse_f_h_squared_diagnostic_BH"],
            (self.profile.q / 2.0) / f_h**2,
            places=14,
        )
        self.assertEqual(
            serialized["rho_inverse_f_h_squared_diagnostic_state"],
            "unverified-non-inferential",
        )
        self.assertIs(
            serialized[
                "rho_inverse_f_h_squared_diagnostic_affects_acceptance"
            ],
            False,
        )

    def test_selected_point_repeat_is_bitwise_identical_in_one_process(
        self,
    ) -> None:
        repeated = solve_charged_profile(4.84, 0.40, 80)
        repeated_point = charged_point_from_profile(repeated)
        np.testing.assert_array_equal(
            self.profile.blackening, repeated.blackening
        )
        np.testing.assert_array_equal(
            self.profile.warp_factor, repeated.warp_factor
        )
        np.testing.assert_array_equal(
            self.profile.scalar_factor, repeated.scalar_factor
        )
        self.assertEqual(self.point.to_dict(), repeated_point.to_dict())

    def test_explicit_maxwell_route_solves_all_four_equations_together(
        self,
    ) -> None:
        profile = self.explicit_profile
        diagnostics = self.explicit_diagnostics
        self.assertTrue(profile.nonlinear.success)
        self.assertLessEqual(
            profile.nonlinear.final_scaled_residual, 1.0e-6
        )
        self.assertLessEqual(
            diagnostics["maximum_evaluated_equation_residual"], 1.0e-5
        )
        self.assertLessEqual(diagnostics["constraint"], 1.0e-5)
        self.assertLessEqual(
            diagnostics["maximum_boundary_residual"], 1.0e-7
        )
        self.assertLessEqual(
            diagnostics["gauss_flux_relative_drift"], 1.0e-7
        )
        self.assertLessEqual(
            diagnostics["phi_h_target_relative_error"], 1.0e-7
        )
        self.assertLessEqual(
            diagnostics["eta_relative_error"], 1.0e-7
        )
        self.assertGreater(diagnostics["minimum_blackening_interior"], 0.0)
        self.assertLess(diagnostics["horizon_blackening_derivative"], 0.0)
        self.assertAlmostEqual(
            profile.electric_potential[0], profile.chemical_potential, places=14
        )
        self.assertLessEqual(abs(profile.electric_potential[-1]), 1.0e-12)
        self.assertLessEqual(
            float(np.max(np.diff(profile.electric_potential))), 1.0e-12
        )

    def test_explicit_and_flux_reduced_routes_agree_at_central_point(
        self,
    ) -> None:
        diagnostics = self.explicit_diagnostics
        for key in (
            "maximum_background_field_difference",
            "electric_coefficient_difference",
            "electric_potential_difference",
            "x_h_relative_difference",
            "q_relative_difference",
            "temperature_relative_difference",
            "chemical_potential_relative_difference",
            "entropy_relative_difference",
            "density_relative_difference",
            "reference_mu_reconstruction_relative_error",
        ):
            self.assertLessEqual(diagnostics[key], 1.0e-7, msg=key)

    def test_explicit_noether_charge_is_conserved_and_horizon_anchored(
        self,
    ) -> None:
        diagnostics = explicit_noether_diagnostics(self.explicit_profile)
        self.assertEqual(
            diagnostics,
            {
                key: self.explicit_diagnostics[key]
                for key in diagnostics
            },
        )
        self.assertLessEqual(
            diagnostics["noether_charge_relative_drift"], 1.0e-6
        )
        self.assertLessEqual(
            diagnostics["noether_horizon_identity_relative_error"],
            1.0e-12,
        )
        expected_horizon = (
            -2.0 * self.explicit_point.temperature * self.explicit_point.entropy
        )
        self.assertAlmostEqual(
            diagnostics["noether_charge_horizon"], expected_horizon, places=12
        )
        self.assertAlmostEqual(
            diagnostics["noether_thermodynamic_horizon"],
            expected_horizon,
            places=12,
        )
        self.assertLess(diagnostics["noether_charge_horizon"], 0.0)
        self.assertEqual(diagnostics["noether_interior_v_minimum"], 0.1)
        self.assertEqual(diagnostics["noether_interior_v_maximum"], 0.98)

    def test_explicit_maxwell_control_points_pass_frozen_gates(self) -> None:
        for phi_h, eta in ((4.84, 0.0), (7.0, 0.5)):
            with self.subTest(phi_h=phi_h, eta=eta):
                reference = solve_charged_profile(phi_h, eta, 80)
                explicit = solve_explicit_maxwell_profile(reference)
                diagnostics = explicit_maxwell_diagnostics(
                    explicit, reference
                )
                self.assertLessEqual(
                    explicit.nonlinear.final_scaled_residual, 1.0e-6
                )
                self.assertLessEqual(
                    diagnostics["maximum_evaluated_equation_residual"],
                    1.0e-5,
                )
                self.assertLessEqual(diagnostics["constraint"], 1.0e-5)
                self.assertLessEqual(
                    diagnostics["maximum_boundary_residual"], 1.0e-7
                )
                self.assertLessEqual(
                    diagnostics["gauss_flux_relative_drift"], 1.0e-7
                )
                self.assertLessEqual(
                    diagnostics["maximum_background_field_difference"],
                    1.0e-7,
                )
                self.assertLessEqual(
                    diagnostics["electric_potential_difference"], 1.0e-7
                )
                self.assertLessEqual(
                    diagnostics["chemical_potential_relative_difference"],
                    1.0e-7,
                )
                self.assertLessEqual(
                    diagnostics["q_relative_difference"], 1.0e-7
                )
                self.assertLessEqual(
                    diagnostics["noether_charge_relative_drift"], 1.0e-6
                )
                self.assertLessEqual(
                    diagnostics["noether_horizon_identity_relative_error"],
                    1.0e-12,
                )
                if eta == 0.0:
                    self.assertEqual(explicit.q, 0.0)
                    self.assertEqual(explicit.chemical_potential, 0.0)
                    np.testing.assert_array_equal(
                        explicit.electric_coefficient,
                        np.zeros_like(explicit.electric_coefficient),
                    )

    def test_explicit_maxwell_central_point_is_stable_from_80_to_120(
        self,
    ) -> None:
        reference_120 = solve_charged_profile(4.84, 0.40, 120)
        explicit_120 = solve_explicit_maxwell_profile(reference_120)
        point_120 = explicit_maxwell_point_from_profile(explicit_120)
        diagnostics_120 = explicit_maxwell_diagnostics(
            explicit_120, reference_120
        )
        self.assertLessEqual(
            diagnostics_120["maximum_evaluated_equation_residual"], 1.0e-5
        )
        self.assertLessEqual(diagnostics_120["constraint"], 1.0e-5)
        for field in (
            "temperature",
            "chemical_potential",
            "entropy",
            "density",
        ):
            value_80 = getattr(self.explicit_point, field)
            value_120 = getattr(point_120, field)
            relative_difference = abs(value_80 - value_120) / max(
                abs(value_80), abs(value_120), 1.0e-300
            )
            self.assertLessEqual(relative_difference, 1.0e-6, msg=field)

    def test_invalid_inputs_fail_closed(self) -> None:
        with self.assertRaisesRegex(ValueError, "phi_h"):
            solve_charged_profile(0.9, 0.40, 80)
        with self.assertRaisesRegex(ValueError, "eta"):
            solve_charged_profile(4.84, 0.91, 80)
        with self.assertRaisesRegex(ValueError, "degree"):
            solve_charged_profile(4.84, 0.40, 11)

    def test_failed_nonlinear_solve_does_not_return_a_profile(self) -> None:
        constrained = ChargedSolverConfig(
            maximum_evaluations_factor=1,
            polish_maximum_evaluations=1,
        )
        with self.assertRaisesRegex(RuntimeError, "charged"):
            solve_charged_profile(4.84, 0.40, 12, config=constrained)


class DeWolfeGubserRosenFiniteDensityVerifierTests(unittest.TestCase):
    """Exercise the owner-approved reduced classical-example contract once."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.record = verify_dewolfe_gubser_rosen_emd_finite_density()
        cls.payload = cls.record.to_dict()

    def test_all_declared_reduced_contract_gates_pass(self) -> None:
        self.assertTrue(self.record.passed)
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
        self.assertTrue(all(item["passed"] for item in checks.values()))
        self.assertEqual(
            self.payload["results"]["summary"]["reported_state_count"],
            6,
        )

    def test_direct_critical_coordinates_match_the_source_neighborhood(
        self,
    ) -> None:
        critical = self.payload["results"]["critical"]
        source = critical["final_source_coordinates"]
        errors = critical["source_coordinate_errors"]
        self.assertLessEqual(abs(source["T_MeV"] - 143.0), 5.0)
        self.assertLessEqual(abs(source["mu_MeV"] - 783.0), 10.0)
        self.assertLessEqual(errors["phi_H_absolute_error"], 0.20)
        self.assertLessEqual(errors["eta_absolute_error"], 0.04)
        self.assertLessEqual(
            critical["maximum_normalized_critical_diagnostic"],
            2.0e-3,
        )
        self.assertLessEqual(critical["maximum_step_change"], 2.0e-3)

    def test_fixed_state_refines_and_independent_route_agrees(self) -> None:
        result = self.payload["results"]
        changes = result["refinement"]["changes"]
        self.assertEqual(
            [(item["coarse_degree"], item["fine_degree"]) for item in changes],
            [(80, 120), (120, 150)],
        )
        self.assertLessEqual(changes[-1]["maximum_change"], 2.0e-3)
        self.assertEqual(result["refinement"]["ordering_failures"], [])
        self.assertLessEqual(
            result["summary"]["maximum_route_observable_difference"],
            5.0e-6,
        )

    def test_figure_5_absolute_ordinate_is_explicitly_out_of_scope(
        self,
    ) -> None:
        result = self.payload["results"]
        separation = result["figure_5_absolute_ordinate_comparison"]
        self.assertEqual(separation["status"], "blocked")
        self.assertFalse(separation["affects_acceptance"])
        self.assertEqual(len(result["figure_5_reference_records"]), 3)
        self.assertTrue(
            all(
                item["entry_count"] == 12
                for item in result["figure_5_reference_records"]
            )
        )
        self.assertIn("global phase diagram", self.payload["scope"])

    def test_record_is_strict_json_and_records_owner_approval(self) -> None:
        encoded = json.dumps(
            self.payload,
            allow_nan=False,
            sort_keys=True,
        )
        self.assertEqual(json.loads(encoded)["passed"], True)
        self.assertEqual(self.payload["result_review_state"], "approved")
        self.assertEqual(self.payload["result_reviewed_by"], "Xin-Yi Liu")
        self.assertEqual(self.payload["result_reviewed_on"], "2026-08-23")
        extension = self.payload["preserved_optional_extension"]
        self.assertFalse(extension["affects_reduced_core_acceptance"])
        self.assertIn("failed", extension["c3h_status"])

    def test_model_card_reference_matches_reviewed_file_bytes(self) -> None:
        root = Path(__file__).resolve().parents[1]
        path = (
            root
            / DEWOLFE_GUBSER_ROSEN_FINITE_DENSITY_MODEL_CARD.repository_path
        )
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        self.assertEqual(
            digest,
            DEWOLFE_GUBSER_ROSEN_FINITE_DENSITY_MODEL_CARD.sha256,
        )

    def test_artifacts_are_complete_and_fail_closed_on_overwrite(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "artifacts"
            paths = save_dewolfe_gubser_rosen_emd_finite_density_artifacts(
                self.record,
                output,
            )
            self.assertEqual(set(paths), {"json", "csv", "plot"})
            self.assertTrue(all(path.is_file() for path in paths.values()))
            self.assertGreater(paths["plot"].stat().st_size, 1000)
            saved = json.loads(paths["json"].read_text(encoding="utf-8"))
            self.assertTrue(saved["passed"])
            with paths["csv"].open(encoding="utf-8", newline="") as handle:
                rows = list(csv.DictReader(handle))
            self.assertEqual(len(rows), 12)
            self.assertEqual({row["route"] for row in rows}, {"primary", "explicit"})
            with self.assertRaisesRegex(ValueError, "refusing to overwrite"):
                save_dewolfe_gubser_rosen_emd_finite_density_artifacts(
                    self.record,
                    output,
                )


if __name__ == "__main__":
    unittest.main()
