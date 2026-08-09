"""Interface tests for machine- and human-readable verification output."""

import io
import json
from pathlib import Path
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout

from jsonschema import Draft202012Validator

from holoforge.cli import main


ROOT = Path(__file__).resolve().parents[1]


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
            (
                "superconductor",
                [
                    "verify",
                    "holographic-superconductor",
                    "--branch-points",
                    "8",
                ],
            ),
            ("linear-axion", ["verify", "linear-axion-dc"]),
            ("comparison", ["compare", "vector-spectrum"]),
        )
        with tempfile.TemporaryDirectory() as directory:
            for label, command in cases:
                with self.subTest(command=label):
                    bundle = Path(directory) / label
                    output = io.StringIO()
                    with redirect_stdout(output):
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
