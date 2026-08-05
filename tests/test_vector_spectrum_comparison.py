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

    def test_reference_assignments_remain_unreviewed_and_visible(self) -> None:
        payload = self.result.to_dict()
        self.assertEqual(payload["reference"]["review_status"], "unreviewed")
        statuses = [
            entry["assignment_status"]
            for entry in payload["reference"]["entries"]
        ]
        self.assertEqual(statuses, ["anchor", "candidate", "candidate"])

    def test_table_states_interpretation_limit(self) -> None:
        table = render_vector_spectrum_table(self.result)
        self.assertIn("PDG 2024 ratio", table)
        self.assertIn("not acceptance gates", table)
        self.assertIn("do not establish model superiority", table)

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
