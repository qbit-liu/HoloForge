"""Focused tests for portable evidence and compatibility contracts."""

import json
from pathlib import Path
import shutil
import tempfile
import unittest

from holoforge.benchmarks.registry import (
    HARD_WALL_MODEL_CARD,
    LINEAR_AXION_MODEL_CARD,
    SOFT_WALL_MODEL_CARD,
    SUPERCONDUCTOR_MODEL_CARD,
)
from holoforge.core.evidence import (
    EvidenceBundleError,
    audit_evidence_bundle,
    audit_same_state_family,
    canonical_json_sha256,
    file_sha256,
    write_evidence_bundle,
)


ROOT = Path(__file__).resolve().parents[1]


def synthetic_result():
    return {
        "benchmark": "synthetic-public-evidence-test",
        "support_level": "reproduced",
        "configuration": {"control": 1.0, "grid_points": 20},
        "numerical_method": {"library": "maintained.test.function"},
        "results": [{"value": 2.0}],
        "acceptance_checks": [
            {
                "id": "synthetic-check",
                "description": "Synthetic public test fixture passes.",
                "passed": True,
            }
        ],
        "software_versions": {"holoforge": "test", "python": "test"},
        "passed": True,
        "scope": "Synthetic infrastructure fixture; no scientific claim.",
    }


def synthetic_state(control=1.0, ensemble="synthetic ensemble"):
    return {
        "model_identifier": "synthetic.public.test",
        "ensemble": ensemble,
        "fixed_variables": {"background": "synthetic"},
        "approximation": "synthetic infrastructure fixture",
        "phase_branch": "synthetic branch",
        "parameters": {"control": control, "fixed_parameter": 3.0},
        "declared_controls": ["control"],
        "boundary_source_conditions": {"boundary": "synthetic"},
        "conventions": {"units": "dimensionless"},
        "source_record_versions": {"fixture": "0.4"},
    }


def write_synthetic_bundle(
    path, control=1.0, ensemble="synthetic ensemble", **state_updates
):
    state = synthetic_state(control=control, ensemble=ensemble)
    state.update(state_updates)
    return write_evidence_bundle(
        path,
        command_identity="verify synthetic-public-evidence-test",
        result_record=synthetic_result(),
        scientific_state=state,
        model_card_references=(SOFT_WALL_MODEL_CARD.to_dict(),),
        created_at_utc="2026-08-06T00:00:00Z",
    )


class EvidenceBundleTests(unittest.TestCase):
    def test_canonical_digest_ignores_object_key_order(self) -> None:
        left = {"outer": {"b": 2, "a": 1}, "items": [3, 4]}
        right = {"items": [3, 4], "outer": {"a": 1, "b": 2}}
        self.assertEqual(canonical_json_sha256(left), canonical_json_sha256(right))

    def test_bundle_remains_valid_after_it_moves(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            original = Path(directory) / "original"
            moved = Path(directory) / "moved"
            write_synthetic_bundle(original)
            shutil.move(str(original), str(moved))

            report = audit_evidence_bundle(moved)

            self.assertTrue(report.passed, report.to_dict())
            manifest = json.loads((moved / "manifest.json").read_text())
            self.assertTrue(
                all(not Path(item["path"]).is_absolute() for item in manifest["files"])
            )

    def test_mutated_record_fails_with_affected_path(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            bundle = Path(directory) / "bundle"
            write_synthetic_bundle(bundle)
            result_path = bundle / "records" / "result.json"
            result_path.write_text(result_path.read_text() + " ", encoding="utf-8")

            report = audit_evidence_bundle(bundle)

            self.assertFalse(report.passed)
            details = " ".join(str(check["detail"]) for check in report.checks)
            self.assertIn("records/result.json", details)

    def test_execution_timestamp_does_not_change_scientific_identity(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            first = Path(directory) / "first"
            second = Path(directory) / "second"
            write_evidence_bundle(
                first,
                command_identity="verify synthetic-public-evidence-test",
                result_record=synthetic_result(),
                scientific_state=synthetic_state(),
                model_card_references=(SOFT_WALL_MODEL_CARD.to_dict(),),
                created_at_utc="2026-08-06T00:00:00Z",
            )
            write_evidence_bundle(
                second,
                command_identity="verify synthetic-public-evidence-test",
                result_record=synthetic_result(),
                scientific_state=synthetic_state(),
                model_card_references=(SOFT_WALL_MODEL_CARD.to_dict(),),
                created_at_utc="2026-08-06T01:00:00Z",
            )
            first_manifest = json.loads((first / "manifest.json").read_text())
            second_manifest = json.loads((second / "manifest.json").read_text())

            self.assertEqual(first_manifest["bundle_id"], second_manifest["bundle_id"])
            self.assertEqual(
                first_manifest["scientific_payload_digest"],
                second_manifest["scientific_payload_digest"],
            )

    def test_declared_control_change_is_compatible(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            first = Path(directory) / "first"
            second = Path(directory) / "second"
            write_synthetic_bundle(first, control=1.0)
            write_synthetic_bundle(second, control=2.0)

            report = audit_same_state_family(first, second)

            self.assertTrue(report.passed, report.to_dict())
            self.assertEqual(report.declared_controls, ("control",))
            self.assertEqual(report.control_changes[0]["field"], "parameters.control")

    def test_ensemble_mismatch_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            first = Path(directory) / "first"
            second = Path(directory) / "second"
            write_synthetic_bundle(first)
            write_synthetic_bundle(second, ensemble="different ensemble")

            report = audit_same_state_family(first, second)

            self.assertFalse(report.passed)
            self.assertIn("ensemble", [item["field"] for item in report.mismatches])

    def test_approximation_mismatch_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            first = Path(directory) / "first"
            second = Path(directory) / "second"
            write_synthetic_bundle(first)
            write_synthetic_bundle(second, approximation="different approximation")
            report = audit_same_state_family(first, second)
            self.assertFalse(report.passed)
            self.assertIn(
                "approximation", [item["field"] for item in report.mismatches]
            )

    def test_phase_branch_mismatch_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            first = Path(directory) / "first"
            second = Path(directory) / "second"
            write_synthetic_bundle(first)
            write_synthetic_bundle(second, phase_branch="different branch")
            report = audit_same_state_family(first, second)
            self.assertFalse(report.passed)
            self.assertIn(
                "phase_branch", [item["field"] for item in report.mismatches]
            )

    def test_undeclared_parameter_mismatch_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            first = Path(directory) / "first"
            second = Path(directory) / "second"
            write_synthetic_bundle(first)
            changed = synthetic_state()["parameters"]
            changed["fixed_parameter"] = 4.0
            write_synthetic_bundle(second, parameters=changed)
            report = audit_same_state_family(first, second)
            self.assertFalse(report.passed)
            self.assertIn(
                "parameters.fixed_parameter",
                [item["field"] for item in report.mismatches],
            )

    def test_boundary_source_mismatch_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            first = Path(directory) / "first"
            second = Path(directory) / "second"
            write_synthetic_bundle(first)
            write_synthetic_bundle(
                second,
                boundary_source_conditions={"boundary": "different source"},
            )
            report = audit_same_state_family(first, second)
            self.assertFalse(report.passed)
            self.assertIn(
                "boundary_source_conditions",
                [item["field"] for item in report.mismatches],
            )

    def test_missing_compatibility_metadata_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            first = Path(directory) / "first"
            second = Path(directory) / "second"
            write_synthetic_bundle(first)
            write_synthetic_bundle(second)
            manifest_path = second / "manifest.json"
            manifest = json.loads(manifest_path.read_text())
            del manifest["scientific_state"]["ensemble"]
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

            report = audit_same_state_family(first, second)

            self.assertFalse(report.passed)
            self.assertIn("bundle_b", [item["field"] for item in report.mismatches])

    def test_absolute_metadata_path_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            result = synthetic_result()
            result["configuration"]["input"] = "/private/input.json"
            with self.assertRaises(EvidenceBundleError):
                write_evidence_bundle(
                    Path(directory) / "bundle",
                    command_identity="verify synthetic-public-evidence-test",
                    result_record=result,
                    scientific_state=synthetic_state(),
                    model_card_references=(SOFT_WALL_MODEL_CARD.to_dict(),),
                )

    def test_private_identity_metadata_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            result = synthetic_result()
            result["configuration"]["username"] = "example"
            with self.assertRaises(EvidenceBundleError):
                write_evidence_bundle(
                    Path(directory) / "bundle",
                    command_identity="verify synthetic-public-evidence-test",
                    result_record=result,
                    scientific_state=synthetic_state(),
                    model_card_references=(SOFT_WALL_MODEL_CARD.to_dict(),),
                )

    def test_manifest_records_support_level_and_limitations(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            bundle = Path(directory) / "bundle"
            write_synthetic_bundle(bundle)
            manifest = json.loads((bundle / "manifest.json").read_text())
            self.assertEqual(manifest["support_level"], "reproduced")
            self.assertIn("no scientific claim", manifest["limitations"][0])

    def test_existing_content_is_not_overwritten(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            bundle = Path(directory) / "bundle"
            bundle.mkdir()
            marker = bundle / "keep.txt"
            marker.write_text("preserve", encoding="utf-8")
            with self.assertRaises(EvidenceBundleError):
                write_synthetic_bundle(bundle)
            self.assertEqual(marker.read_text(encoding="utf-8"), "preserve")

    def test_embedded_model_card_hashes_match_public_records(self) -> None:
        for reference in (
            SOFT_WALL_MODEL_CARD,
            HARD_WALL_MODEL_CARD,
            SUPERCONDUCTOR_MODEL_CARD,
            LINEAR_AXION_MODEL_CARD,
        ):
            with self.subTest(model_card=reference.identifier):
                model_card_path = ROOT / reference.repository_path
                self.assertEqual(file_sha256(model_card_path), reference.sha256)

    def test_artifact_is_copied_and_audited_inside_bundle(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "figure.txt"
            source.write_text("synthetic artifact", encoding="utf-8")
            bundle = Path(directory) / "bundle"
            write_evidence_bundle(
                bundle,
                command_identity="verify synthetic-public-evidence-test",
                result_record=synthetic_result(),
                scientific_state=synthetic_state(),
                model_card_references=(SOFT_WALL_MODEL_CARD.to_dict(),),
                artifacts={"figure": source},
            )
            manifest = json.loads((bundle / "manifest.json").read_text())
            artifact_entries = [
                item for item in manifest["files"]
                if item["role"] == "artifact:figure"
            ]
            self.assertEqual(len(artifact_entries), 1)
            self.assertTrue((bundle / artifact_entries[0]["path"]).is_file())
            self.assertTrue(audit_evidence_bundle(bundle).passed)


if __name__ == "__main__":
    unittest.main()
