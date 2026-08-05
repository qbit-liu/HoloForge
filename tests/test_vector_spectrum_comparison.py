"""End-to-end tests for the public v0.3 vector-spectrum comparison."""

import json
from pathlib import Path
import tempfile
import unittest

from holoforge.comparisons.vector_spectrum import (
    build_vector_spectrum_comparison,
    render_vector_spectrum_table,
    save_vector_spectrum_artifacts,
)


class VectorSpectrumComparisonTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = build_vector_spectrum_comparison()

    def test_all_numerical_gates_pass_without_empirical_gate(self) -> None:
        self.assertTrue(self.result.passed)
        self.assertTrue(all(check.passed for check in self.result.acceptance_checks))
        payload = self.result.to_dict()
        self.assertTrue(
            all(
                not item["is_acceptance_gate"]
                for item in payload["descriptive_comparisons"]
            )
        )

    def test_reference_approval_and_assignments_remain_visible(self) -> None:
        payload = self.result.to_dict()
        self.assertEqual(payload["reference"]["review_status"], "approved")
        statuses = [
            entry["assignment_status"]
            for entry in payload["reference"]["entries"]
        ]
        self.assertEqual(statuses, ["anchor", "candidate", "candidate"])
        self.assertEqual(
            [entry["id"] for entry in payload["excluded_entries"]],
            ["rho-1570"],
        )
        self.assertEqual(
            payload["excluded_entries"][0]["assignment_status"], "ambiguous"
        )

    def test_table_states_interpretation_limit(self) -> None:
        table = render_vector_spectrum_table(self.result)
        self.assertIn("PDG 2026 ratio", table)
        self.assertIn("rho(1570)", table)
        self.assertIn("excluded from the default comparison", table)
        self.assertIn("not acceptance gates", table)
        self.assertIn("do not establish model superiority", table)
        self.assertIn(
            "Reference convention review: approved by Xin-Yi Liu on 2026-08-05.",
            table,
        )

    def test_artifacts_are_generated_from_the_result(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            artifacts = save_vector_spectrum_artifacts(
                self.result, Path(directory), include_plot=True
            )
            for artifact in artifacts.values():
                self.assertTrue(Path(artifact).is_file())
            payload = json.loads(Path(artifacts["json"]).read_text())
            self.assertEqual(
                payload["comparison"], "soft-wall-hard-wall-vector-ratios"
            )
            self.assertTrue(payload["passed"])


if __name__ == "__main__":
    unittest.main()
