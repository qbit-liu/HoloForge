"""Interface tests for machine- and human-readable verification output."""

import io
import json
from pathlib import Path
import tempfile
import unittest
from contextlib import nullcontext, redirect_stderr, redirect_stdout
from unittest.mock import patch

from jsonschema import Draft202012Validator

from holoforge.cli import main


ROOT = Path(__file__).resolve().parents[1]


class FastGubserNelloreResult:
    """Small interface fixture; the full scientific solve has focused tests."""

    passed = True

    def to_dict(self):
        return {
            "schema_version": "0.1",
            "benchmark": "gubser-nellore-ed",
            "support_level": "reproduced",
            "configuration": {
                "profile": "anchor",
                "bulk_dimension": 5,
                "ensemble": "zero chemical potential and zero Maxwell field",
                "units": "L = 1, kappa_5^2 = 1",
                "potentials": [],
                "dop853_target_phi_h": [0.25, 0.5, 1.0, 2.0, 4.0],
                "T_c_plot_registration": 0.9618971489,
            },
            "numerical_method": {"route": "test interface fixture"},
            "results": {
                "presets": {
                    "cosh-calibration": {
                        "horizon_count": 1,
                        "maximum_equation_residual": 0.0,
                        "figure": {"maximum_anchor_error": 0.0},
                    },
                    "qcd-like": {
                        "horizon_count": 1,
                        "maximum_equation_residual": 0.0,
                        "figure": {"maximum_anchor_error": 0.0},
                    },
                }
            },
            "acceptance_checks": [
                {
                    "id": "interface-fixture",
                    "description": "Generic CLI dispatch reaches the ED adapter.",
                    "passed": True,
                    "value": 0.0,
                }
            ],
            "software_versions": {"holoforge": "test", "python": "test"},
            "passed": True,
            "scope": "Interface fixture; no scientific result.",
            "primary_source": {
                "pdf_sha256": "0" * 64,
                "source_archive_sha256": "1" * 64,
            },
        }


class FastHardWallChiralResult:
    """Small interface fixture; focused tests run the complete reproduction."""

    passed = True

    def to_dict(self):
        return {
            "schema_version": "0.1",
            "benchmark": "hard-wall-chiral",
            "support_level": "reproduced",
            "configuration": {
                "g5": 6.283185307179586,
                "z_m_inverse_MeV": 323.0,
                "m_q_MeV": 2.29,
                "sigma_cube_root_MeV": 327.0,
            },
            "numerical_method": {"primary_route": "test interface fixture"},
            "results": {
                "table": [
                    {
                        "observable": "m_pi_MeV",
                        "computed": 139.585,
                        "target": 139.6,
                        "relative_error": 1.1e-4,
                        "source_role": "source fit target",
                    }
                ]
            },
            "acceptance_checks": [
                {
                    "id": "interface-fixture",
                    "description": "Generic dispatch reaches the hard-wall chiral adapter.",
                    "passed": True,
                    "value": 0.0,
                }
            ],
            "software_versions": {"holoforge": "test", "python": "test"},
            "passed": True,
            "scope": "Interface fixture; no scientific result.",
            "primary_source": {
                "pdf_sha256": "0" * 64,
                "source_archive_sha256": "1" * 64,
            },
            "result_review_state": "approved",
            "result_reviewed_by": "Xin-Yi Liu",
            "result_reviewed_on": "2026-08-20",
        }


class FastSuperconductorOpticalResult:
    """Small optical fixture; focused tests run the complete verifier."""

    passed = True

    def to_dict(self):
        return {
            "benchmark": "holographic-superconductor-optical",
            "support_level": "reproduced",
            "configuration": {
                "quantization": "Delta = 2 with psi_- = 0",
                "temperature_targets": {
                    "low_temperature": 0.0026,
                    "near_critical": [0.99, 0.995, 0.9975, 0.999],
                },
                "near_critical_frequencies": [0.2, 0.1, 0.05, 0.025],
                "near_critical_spectral_degrees": [128, 160, 192],
            },
            "numerical_method": {"route": "test interface fixture"},
            "results": {
                "near_critical_pole": {
                    "slope": 23.96884335,
                    "literature_coefficient": 24.0,
                    "literature_relative_error": 0.00129819,
                    "finite_frequency_slope": 23.96883307,
                    "maximum_static_pole_relative_difference": 4.24e-7,
                    "points": [
                        {
                            "responses": [
                                {
                                    "equation_residual": 5.6e-8,
                                    "resolution_audit": {
                                        "equation_residual": 1.38e-7
                                    },
                                }
                            ]
                        }
                    ],
                },
                "figure_2_provenance": {
                    "status": "not_reproduced",
                    "acceptance_role": "provenance-only",
                },
            },
            "acceptance_checks": [
                {
                    "id": "interface-fixture",
                    "description": "Generic dispatch reaches the optical adapter.",
                    "passed": True,
                    "value": 0.0,
                }
            ],
            "software_versions": {"holoforge": "test", "python": "test"},
            "passed": True,
            "scope": (
                "Interface fixture; not empirical validation and Figure 2 "
                "is not reproduced."
            ),
            "source_provenance": {
                "pdf_sha256": "0" * 64,
                "archive_sha256": "1" * 64,
            },
            "result_review_state": "approved",
            "result_reviewed_by": "Xin-Yi Liu",
            "result_reviewed_on": "2026-08-21",
        }


class CommandLineTests(unittest.TestCase):
    def test_json_output_contains_evidence_and_passes(self) -> None:
        output = io.StringIO()
        with redirect_stdout(output):
            status = main(
                [
                    "verify",
                    "soft-wall-vector",
                    "--grid-points",
                    "600",
                    "--tolerance",
                    "2e-4",
                    "--json",
                ]
            )
        payload = json.loads(output.getvalue())

        self.assertEqual(status, 0)
        self.assertTrue(payload["passed"])
        self.assertEqual(payload["support_level"], "reproduced")
        self.assertEqual(len(payload["results"]), 4)
        self.assertEqual(payload["configuration"]["num_modes"], 4)
        self.assertEqual(
            payload["numerical_method"]["eigensolver"],
            "scipy.linalg.eigvalsh_tridiagonal",
        )
        self.assertEqual(
            payload["numerical_method"]["operator_structure"],
            "real symmetric tridiagonal",
        )
        self.assertIn("python", payload["software_versions"])
        self.assertIn("numpy", payload["software_versions"])
        self.assertIn("scipy", payload["software_versions"])
        self.assertIn("not empirical validation", payload["scope"])

    def test_failed_acceptance_gate_returns_nonzero(self) -> None:
        output = io.StringIO()
        with redirect_stdout(output):
            status = main(
                [
                    "verify",
                    "soft-wall-vector",
                    "--grid-points",
                    "300",
                    "--tolerance",
                    "1e-12",
                ]
            )
        self.assertEqual(status, 1)
        self.assertIn("FAIL", output.getvalue())

    def test_soft_wall_spectral_json_contains_refinement_evidence(self) -> None:
        output = io.StringIO()
        with redirect_stdout(output):
            status = main(
                [
                    "verify",
                    "soft-wall-vector",
                    "--method",
                    "spectral",
                    "--json",
                ]
            )
        payload = json.loads(output.getvalue())

        self.assertEqual(status, 0)
        self.assertTrue(payload["passed"])
        self.assertEqual(payload["numerical_method"]["route"], "spectral")
        self.assertEqual(
            [level["degree"] for level in payload["spectral_convergence"]["levels"]],
            [24, 32, 40],
        )

    def test_invalid_configuration_has_clear_error(self) -> None:
        error = io.StringIO()
        with redirect_stderr(error):
            status = main(
                ["verify", "soft-wall-vector", "--kappa", "0"]
            )
        self.assertEqual(status, 2)
        self.assertIn("kappa_gev must be", error.getvalue())

    def test_nonfinite_tolerance_is_rejected(self) -> None:
        error = io.StringIO()
        with redirect_stderr(error):
            status = main(
                ["verify", "soft-wall-vector", "--tolerance", "nan"]
            )
        self.assertEqual(status, 2)
        self.assertIn("tolerance must be finite", error.getvalue())

    def test_superconductor_json_contains_sources_and_curve(self) -> None:
        output = io.StringIO()
        with redirect_stdout(output):
            status = main(
                [
                    "verify",
                    "holographic-superconductor",
                    "--branch-points",
                    "8",
                    "--json",
                ]
            )
        payload = json.loads(output.getvalue())

        self.assertEqual(status, 0)
        self.assertTrue(payload["passed"])
        self.assertEqual(payload["benchmark"], "holographic-superconductor")
        self.assertEqual(
            payload["configuration"]["quantization"],
            "Delta = 2 with psi_- = 0",
        )
        self.assertEqual(
            len(payload["results"]["condensate_branch"]["points"]), 8
        )

    def test_invalid_superconductor_cutoff_has_clear_error(self) -> None:
        error = io.StringIO()
        with redirect_stderr(error):
            status = main(
                [
                    "verify",
                    "holographic-superconductor",
                    "--radial-cutoff",
                    "0",
                ]
            )
        self.assertEqual(status, 2)
        self.assertIn("radial_cutoff", error.getvalue())

    def test_superconductor_optical_json_uses_registered_adapter(self) -> None:
        output = io.StringIO()
        with patch(
            "holoforge.benchmarks.adapters.holographic_superconductor_optical."
            "verify_holographic_superconductor_optical",
            return_value=FastSuperconductorOpticalResult(),
        ), redirect_stdout(output):
            status = main(
                ["verify", "holographic-superconductor-optical", "--json"]
            )
        payload = json.loads(output.getvalue())
        self.assertEqual(status, 0)
        self.assertTrue(payload["passed"])
        self.assertEqual(payload["support_level"], "reproduced")
        self.assertEqual(
            payload["results"]["figure_2_provenance"]["status"],
            "not_reproduced",
        )

    def test_superconductor_optical_human_output_states_boundary(self) -> None:
        output = io.StringIO()
        with patch(
            "holoforge.benchmarks.adapters.holographic_superconductor_optical."
            "verify_holographic_superconductor_optical",
            return_value=FastSuperconductorOpticalResult(),
        ), redirect_stdout(output):
            status = main(["verify", "holographic-superconductor-optical"])
        rendered = output.getvalue()
        self.assertEqual(status, 0)
        self.assertIn("static London C_2 = 23.96884335", rendered)
        self.assertIn("not_reproduced (provenance-only)", rendered)
        self.assertIn("not empirical validation", rendered)

    def test_hard_wall_json_contains_boundary_and_ratio_evidence(self) -> None:
        output = io.StringIO()
        with redirect_stdout(output):
            status = main(["verify", "hard-wall-vector", "--json"])
        payload = json.loads(output.getvalue())

        self.assertEqual(status, 0)
        self.assertTrue(payload["passed"])
        self.assertEqual(payload["benchmark"], "hard-wall-vector")
        self.assertEqual(payload["numerical_method"]["route"], "shooting")
        self.assertEqual(len(payload["results"]), 4)

    def test_invalid_hard_wall_cutoff_has_clear_error(self) -> None:
        error = io.StringIO()
        with redirect_stderr(error):
            status = main(
                [
                    "verify",
                    "hard-wall-vector",
                    "--epsilon-fraction",
                    "1",
                ]
            )
        self.assertEqual(status, 2)
        self.assertIn("epsilon_fraction", error.getvalue())

    def test_hard_wall_spectral_json_contains_refinement_evidence(self) -> None:
        output = io.StringIO()
        with redirect_stdout(output):
            status = main(
                [
                    "verify",
                    "hard-wall-vector",
                    "--method",
                    "spectral",
                    "--json",
                ]
            )
        payload = json.loads(output.getvalue())

        self.assertEqual(status, 0)
        self.assertTrue(payload["passed"])
        self.assertEqual(payload["numerical_method"]["route"], "spectral")
        self.assertEqual(payload["spectral_convergence"]["degrees"], [24, 32, 40])

    def test_hard_wall_chiral_json_uses_registered_adapter(self) -> None:
        output = io.StringIO()
        with patch(
            "holoforge.benchmarks.adapters.hard_wall_chiral.verify_hard_wall_chiral",
            return_value=FastHardWallChiralResult(),
        ), redirect_stdout(output):
            status = main(["verify", "hard-wall-chiral", "--json"])
        payload = json.loads(output.getvalue())
        self.assertEqual(status, 0)
        self.assertEqual(payload["benchmark"], "hard-wall-chiral")
        self.assertEqual(payload["result_review_state"], "approved")

    def test_linear_axion_dc_json_contains_sources_and_dc_checks(self) -> None:
        output = io.StringIO()
        with redirect_stdout(output):
            status = main(["verify", "linear-axion-dc", "--json"])
        payload = json.loads(output.getvalue())

        self.assertEqual(status, 0)
        self.assertTrue(payload["passed"])
        self.assertEqual(payload["benchmark"], "linear-axion-dc")
        self.assertIn("grand canonical", payload["configuration"]["ensemble"])
        self.assertEqual(len(payload["results"]["cases"]), 3)
        self.assertEqual(len(payload["acceptance_checks"]), 15)

    def test_linear_axion_dc_human_output_states_scope(self) -> None:
        output = io.StringIO()
        with redirect_stdout(output):
            status = main(["verify", "linear-axion-dc"])

        self.assertEqual(status, 0)
        self.assertIn("PASS: all declared acceptance gates", output.getvalue())
        self.assertIn("not empirical validation", output.getvalue())

    def test_gubser_nellore_json_uses_registered_adapter(self) -> None:
        output = io.StringIO()
        with patch(
            "holoforge.benchmarks.adapters.gubser_nellore_ed.verify_gubser_nellore_ed",
            return_value=FastGubserNelloreResult(),
        ), redirect_stdout(output):
            status = main(["verify", "gubser-nellore-ed", "--json"])
        payload = json.loads(output.getvalue())
        self.assertEqual(status, 0)
        self.assertEqual(payload["benchmark"], "gubser-nellore-ed")
        self.assertTrue(payload["passed"])

    def test_vector_comparison_json_and_artifacts(self) -> None:
        output = io.StringIO()
        with tempfile.TemporaryDirectory() as directory:
            with redirect_stdout(output):
                status = main(
                    [
                        "compare",
                        "vector-spectrum",
                        "--output-dir",
                        directory,
                        "--no-plot",
                        "--json",
                    ]
                )
            payload = json.loads(output.getvalue())
            self.assertEqual(status, 0)
            self.assertTrue(payload["passed"])
            self.assertEqual(len(payload["model_predictions"]), 2)
            self.assertTrue(Path(payload["artifacts"]["json"]).is_file())
            self.assertNotIn("plot", payload["artifacts"])

    def test_soft_wall_bundle_can_be_created_and_audited(self) -> None:
        output = io.StringIO()
        with tempfile.TemporaryDirectory() as directory:
            bundle = Path(directory) / "bundle"
            with redirect_stdout(output):
                status = main(
                    [
                        "verify",
                        "soft-wall-vector",
                        "--grid-points",
                        "600",
                        "--tolerance",
                        "2e-4",
                        "--bundle-dir",
                        str(bundle),
                        "--json",
                    ]
                )
            payload = json.loads(output.getvalue())
            self.assertEqual(status, 0)
            self.assertEqual(Path(payload["evidence_bundle"]), bundle)

            output = io.StringIO()
            with redirect_stdout(output):
                audit_status = main(["audit", "bundle", str(bundle), "--json"])
            audit_payload = json.loads(output.getvalue())
            self.assertEqual(audit_status, 0)
            self.assertTrue(audit_payload["passed"])

    def test_bundle_generation_preserves_existing_directory_content(self) -> None:
        error = io.StringIO()
        with tempfile.TemporaryDirectory() as directory:
            bundle = Path(directory) / "bundle"
            bundle.mkdir()
            marker = bundle / "keep.txt"
            marker.write_text("keep", encoding="utf-8")
            with redirect_stderr(error):
                status = main(
                    [
                        "verify",
                        "soft-wall-vector",
                        "--bundle-dir",
                        str(bundle),
                    ]
                )
            self.assertEqual(status, 2)
            self.assertEqual(marker.read_text(encoding="utf-8"), "keep")
            self.assertIn("must be empty", error.getvalue())

    def test_every_current_command_can_emit_an_auditable_bundle(self) -> None:
        bundle_schema = json.loads(
            (ROOT / "schemas/evidence-bundle.schema.json").read_text()
        )
        validator = Draft202012Validator(bundle_schema)
        cases = (
            ("soft-wall", ["verify", "soft-wall-vector", "--grid-points", "600"]),
            ("hard-wall", ["verify", "hard-wall-vector", "--modes", "2"]),
            ("hard-wall-chiral", ["verify", "hard-wall-chiral"]),
            (
                "superconductor",
                [
                    "verify",
                    "holographic-superconductor",
                    "--branch-points",
                    "8",
                ],
            ),
            (
                "superconductor-optical",
                ["verify", "holographic-superconductor-optical"],
            ),
            ("linear-axion", ["verify", "linear-axion-dc"]),
            ("gubser-nellore", ["verify", "gubser-nellore-ed"]),
            ("comparison", ["compare", "vector-spectrum"]),
        )
        with tempfile.TemporaryDirectory() as directory:
            for label, command in cases:
                with self.subTest(command=label):
                    bundle = Path(directory) / label
                    output = io.StringIO()
                    context = (
                        patch(
                            "holoforge.benchmarks.adapters.gubser_nellore_ed.verify_gubser_nellore_ed",
                            return_value=FastGubserNelloreResult(),
                        )
                        if label == "gubser-nellore"
                        else (
                            patch(
                                "holoforge.benchmarks.adapters.hard_wall_chiral.verify_hard_wall_chiral",
                                return_value=FastHardWallChiralResult(),
                            )
                            if label == "hard-wall-chiral"
                            else (
                                patch(
                                    "holoforge.benchmarks.adapters."
                                    "holographic_superconductor_optical."
                                    "verify_holographic_superconductor_optical",
                                    return_value=(
                                        FastSuperconductorOpticalResult()
                                    ),
                                )
                                if label == "superconductor-optical"
                                else nullcontext()
                            )
                        )
                    )
                    with context, redirect_stdout(output):
                        status = main(command + ["--bundle-dir", str(bundle)])
                    self.assertEqual(status, 0, output.getvalue())
                    audit_output = io.StringIO()
                    with redirect_stdout(audit_output):
                        audit_status = main(
                            ["audit", "bundle", str(bundle), "--json"]
                        )
                    self.assertEqual(audit_status, 0, audit_output.getvalue())
                    validator.validate(
                        json.loads((bundle / "manifest.json").read_text())
                    )


if __name__ == "__main__":
    unittest.main()
