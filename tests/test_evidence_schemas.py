"""Validate generated Version 0.4 evidence records against their schemas."""

import json
from pathlib import Path
import tempfile
import unittest

from jsonschema import Draft202012Validator, FormatChecker

from holoforge.core.evidence import audit_same_state_family
from tests.test_evidence import write_synthetic_bundle


ROOT = Path(__file__).resolve().parents[1]


class EvidenceSchemaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.bundle_schema = json.loads(
            (ROOT / "schemas/evidence-bundle.schema.json").read_text()
        )
        cls.compatibility_schema = json.loads(
            (ROOT / "schemas/evidence-compatibility.schema.json").read_text()
        )
        Draft202012Validator.check_schema(cls.bundle_schema)
        Draft202012Validator.check_schema(cls.compatibility_schema)

    def test_generated_manifest_validates(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            bundle = Path(directory) / "bundle"
            write_synthetic_bundle(bundle)
            manifest = json.loads((bundle / "manifest.json").read_text())
            validator = Draft202012Validator(
                self.bundle_schema, format_checker=FormatChecker()
            )
            validator.validate(manifest)

    def test_compatibility_report_validates(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            first = Path(directory) / "first"
            second = Path(directory) / "second"
            write_synthetic_bundle(first, control=1.0)
            write_synthetic_bundle(second, control=2.0)
            report = audit_same_state_family(first, second).to_dict()
            Draft202012Validator(self.compatibility_schema).validate(report)


if __name__ == "__main__":
    unittest.main()
