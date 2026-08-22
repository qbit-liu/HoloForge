"""Scientific, numerical, artifact, and review gates for DGR Phase 5A."""

import hashlib
import json
import math
from pathlib import Path
import tempfile
import unittest

import numpy as np

from holoforge.benchmarks.adapters.dewolfe_gubser_rosen_emd import (
    DEWOLFE_GUBSER_ROSEN_ADAPTER,
    DEWOLFE_GUBSER_ROSEN_MODEL_CARD,
)
from holoforge.benchmarks.dewolfe_gubser_rosen_emd import (
    DEFAULT_DEGREES,
    DEFAULT_TARGET_PHI_H,
    DGR_POTENTIAL,
    LAMBDA_MU_MEV,
    LAMBDA_RHO_MEV3,
    LAMBDA_S_MEV3,
    LAMBDA_T_MEV,
    PRINTED_SCALE_PRODUCT_RELATIVE_MISMATCH,
    SOURCE_ARCHIVE_SHA256,
    SOURCE_FIGURE_3_SHA256,
    SOURCE_PDF_SHA256,
    gauge_coupling,
    gauge_log_derivative,
    save_dewolfe_gubser_rosen_artifacts,
    solve_targeted_branch,
    verify_dewolfe_gubser_rosen_emd,
)
from holoforge.core.registry import BenchmarkExecution


ROOT = Path(__file__).resolve().parents[1]


class DeWolfeGubserRosenPhase5ATests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.record = verify_dewolfe_gubser_rosen_emd()
        cls.payload = cls.record.to_dict()
        cls.checks = {
            check["id"]: check for check in cls.payload["acceptance_checks"]
        }

    def test_complete_frozen_contract_passes(self) -> None:
        self.assertTrue(self.record.passed)
        self.assertEqual(len(self.record.acceptance_checks), 14)
        self.assertTrue(all(check.passed for check in self.record.acceptance_checks))

    def test_duplicate_complete_run_is_deterministic(self) -> None:
        determinism = self.payload["results"]["determinism"]
        self.assertTrue(determinism["repeat_enabled"])
        self.assertLessEqual(determinism["maximum_scaled_difference"], 1.0e-12)
        self.assertTrue(self.checks["determinism"]["passed"])

    def test_primary_equation_and_target_gates_have_margin(self) -> None:
        self.assertLessEqual(self.checks["nonlinear-solver"]["value"], 1.0e-8)
        self.assertLessEqual(self.checks["independent-equations"]["value"], 1.0e-6)
        self.assertLessEqual(self.checks["einstein-constraint"]["value"], 1.0e-6)
        self.assertLessEqual(
            self.checks["exact-endpoints-and-regularity"]["value"],
            1.0e-8,
        )
        self.assertLessEqual(
            self.checks["physical-horizon-targets"]["value"],
            1.0e-9,
        )

    def test_refinement_maxwell_and_independent_gates_have_margin(self) -> None:
        self.assertLessEqual(self.checks["spectral-refinement"]["value"], 2.0e-4)
        self.assertLessEqual(self.checks["quadrature-refinement"]["value"], 2.0e-5)
        self.assertLessEqual(
            self.checks["explicit-maxwell-response"]["value"],
            1.0e-6,
        )
        self.assertLessEqual(
            self.checks["dop853-background-comparison"]["value"],
            5.0e-4,
        )
        summary = self.payload["results"]["summary"]
        self.assertEqual(summary["refinement_ordering_failures"], 0)
        self.assertEqual(summary["quadrature_ordering_failures"], 0)
        self.assertLessEqual(summary["maximum_maxwell_flux_drift"], 1.0e-8)

    def test_figure_3_entropy_and_susceptibility_gates_have_margin(self) -> None:
        self.assertLessEqual(self.checks["figure-3-entropy"]["value"], 0.15)
        self.assertLessEqual(
            self.checks["figure-3-susceptibility"]["value"],
            0.005,
        )
        figure = self.payload["results"]["figure_3"]
        self.assertEqual(len(figure["entropy"]["anchors"]), 11)
        self.assertEqual(len(figure["susceptibility"]["anchors"]), 11)

    def test_aligned_physical_target_branches_are_retained(self) -> None:
        branches = self.payload["results"]["degree_branches"]
        self.assertEqual(tuple(int(item) for item in branches), DEFAULT_DEGREES)
        for degree in DEFAULT_DEGREES:
            branch = branches[str(degree)]
            self.assertEqual(branch["target_count"], len(DEFAULT_TARGET_PHI_H))
            self.assertLessEqual(branch["maximum_target_relative_error"], 1.0e-9)
            self.assertLessEqual(branch["maximum_collocation_residual"], 1.0e-8)
        curve = self.payload["results"]["curve"]
        self.assertTrue(np.all(np.diff([row["phi_h"] for row in curve]) > 0.0))
        self.assertTrue(np.all(np.diff([row["x_h"] for row in curve]) > 0.0))
        self.assertTrue(
            np.all(np.diff([row["temperature_BH"] for row in curve]) < 0.0)
        )

    def test_source_functions_and_rounded_scale_dictionary_are_explicit(self) -> None:
        self.assertAlmostEqual(DGR_POTENTIAL.potential(0.0), -12.0, places=12)
        self.assertAlmostEqual(DGR_POTENTIAL.first_derivative(0.0), 0.0, places=12)
        self.assertAlmostEqual(
            DGR_POTENTIAL.delta * (DGR_POTENTIAL.delta - 4.0),
            DGR_POTENTIAL.mass_squared,
            places=12,
        )
        self.assertAlmostEqual(gauge_coupling(0.0), 1.0, places=12)
        self.assertAlmostEqual(gauge_log_derivative(2.0), 0.0, places=12)
        mismatch = abs(
            LAMBDA_T_MEV * LAMBDA_S_MEV3
            - LAMBDA_MU_MEV * LAMBDA_RHO_MEV3
        ) / (LAMBDA_MU_MEV * LAMBDA_RHO_MEV3)
        self.assertAlmostEqual(
            mismatch,
            PRINTED_SCALE_PRODUCT_RELATIVE_MISMATCH,
            places=15,
        )
        self.assertEqual(LAMBDA_T_MEV, 252.0)

    def test_short_target_branch_is_deterministic_and_exact(self) -> None:
        targets = (1.5, 1.75, 2.0, 2.25, 2.5)
        branch = solve_targeted_branch(80, targets)
        repeated = solve_targeted_branch(80, targets)
        self.assertEqual(branch.degree, 80)
        self.assertEqual(branch.targets, targets)
        np.testing.assert_array_equal(
            [point.temperature for point in branch.points],
            [point.temperature for point in repeated.points],
        )
        for profile, target in zip(branch.profiles, targets):
            self.assertLess(abs(profile.phi_h - target) / target, 1.0e-9)
            self.assertTrue(profile.nonlinear.success)

    def test_strict_json_and_public_source_provenance_are_bounded(self) -> None:
        encoded = json.dumps(self.payload, allow_nan=False, sort_keys=True)
        self.assertTrue(encoded)
        source = self.payload["primary_source"]
        self.assertEqual(source["pdf_sha256"], SOURCE_PDF_SHA256)
        self.assertEqual(source["source_archive_sha256"], SOURCE_ARCHIVE_SHA256)
        self.assertEqual(source["figure_3_sha256"], SOURCE_FIGURE_3_SHA256)
        self.assertFalse(source["raw_source_artwork_redistributed"])
        self.assertFalse(source["lattice_points_included"])
        self.assertEqual(self.payload["support_level"], "reproduced")
        self.assertEqual(self.payload["result_review_state"], "approved")
        self.assertEqual(self.payload["result_reviewed_by"], "Xin-Yi Liu")
        self.assertEqual(self.payload["result_reviewed_on"], "2026-08-22")
        self.assertEqual(self.payload["reference_data"]["review_state"], "approved")
        self.assertIn("Figure 5 is mandatory", self.payload["contract_review"]["phase_5b_amendment"])
        self.assertIn("does not calculate Figure 5", self.payload["scope"])

    def test_model_card_digest_and_review_boundary_match_adapter(self) -> None:
        path = ROOT / DEWOLFE_GUBSER_ROSEN_MODEL_CARD.repository_path
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        self.assertEqual(digest, DEWOLFE_GUBSER_ROSEN_MODEL_CARD.sha256)
        card = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(card["maturity"], "reproduced")
        self.assertEqual(card["provenance"]["review_status"], "approved")
        self.assertEqual(card["provenance"]["reviewed_by"], "Xin-Yi Liu")
        self.assertEqual(card["provenance"]["reviewed_on"], "2026-08-22")
        levels = {claim["support_level"] for claim in card["claims"]}
        self.assertEqual(levels, {"established-source", "reproduced"})
        self.assertTrue(all(claim["review_status"] == "approved" for claim in card["claims"]))
        reproduced = next(
            claim
            for claim in card["claims"]
            if claim["support_level"] == "reproduced"
        )
        self.assertEqual(reproduced["reviewed_by"], "Xin-Yi Liu")
        self.assertEqual(reproduced["reviewed_on"], "2026-08-22")

    def test_artifacts_are_complete_and_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "artifacts"
            paths = save_dewolfe_gubser_rosen_artifacts(self.record, output)
            self.assertEqual(set(paths), {"json", "csv", "plot"})
            self.assertTrue(all(path.is_file() for path in paths.values()))
            self.assertGreater(paths["plot"].stat().st_size, 10_000)
            saved = json.loads(paths["json"].read_text(encoding="utf-8"))
            self.assertTrue(saved["passed"])
            self.assertEqual(saved["result_review_state"], "approved")
            self.assertEqual(saved["result_reviewed_by"], "Xin-Yi Liu")
            self.assertEqual(saved["result_reviewed_on"], "2026-08-22")
            with self.assertRaisesRegex(ValueError, "refusing to overwrite"):
                save_dewolfe_gubser_rosen_artifacts(self.record, output)

    def test_human_and_bundle_state_keep_owner_review_visible(self) -> None:
        execution = BenchmarkExecution(payload=self.payload, passed=True)
        human = "\n".join(DEWOLFE_GUBSER_ROSEN_ADAPTER.render_human(execution))
        self.assertIn("owner-approved", human)
        self.assertIn("Support level: reproduced", human)
        state = DEWOLFE_GUBSER_ROSEN_ADAPTER.scientific_state(self.payload)
        self.assertEqual(state["conventions"]["result_review_state"], "approved")
        self.assertIn("Figure 5 is mandatory", state["conventions"]["phase_5b_boundary"])

    def test_invalid_public_inputs_fail_clearly(self) -> None:
        with self.assertRaisesRegex(ValueError, "degree"):
            solve_targeted_branch(39)
        with self.assertRaisesRegex(ValueError, "at least five"):
            solve_targeted_branch(80, (1.5, 2.0, 2.5, 3.0))
        with self.assertRaisesRegex(ValueError, "strictly increasing"):
            solve_targeted_branch(80, (1.5, 2.0, 2.0, 2.5, 3.0))
        with self.assertRaisesRegex(ValueError, "approved"):
            solve_targeted_branch(80, (1.4, 1.5, 2.0, 2.5, 3.0))
        with self.assertRaisesRegex(ValueError, "positive finite"):
            solve_targeted_branch(80, (1.5, 2.0, 2.5, 3.0, math.nan))


if __name__ == "__main__":
    unittest.main()
