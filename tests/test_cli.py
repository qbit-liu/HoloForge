"""Interface tests for machine- and human-readable verification output."""

import io
import json
import unittest
from contextlib import redirect_stderr, redirect_stdout

from holoforge.cli import main


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


if __name__ == "__main__":
    unittest.main()
