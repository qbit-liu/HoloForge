"""Validate generated v0.3 records against their machine contracts."""

import json
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator
from referencing import Registry, Resource

from holoforge.comparisons.vector_spectrum import (
    build_vector_spectrum_comparison,
)


ROOT = Path(__file__).resolve().parents[1]
MODEL_SCHEMA_PATH = ROOT / "schemas" / "model-prediction.schema.json"
COMPARISON_SCHEMA_PATH = ROOT / "schemas" / "comparison-record.schema.json"


def load_json(path: Path):
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


class ComparisonSchemaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.model_schema = load_json(MODEL_SCHEMA_PATH)
        cls.comparison_schema = load_json(COMPARISON_SCHEMA_PATH)
        Draft202012Validator.check_schema(cls.model_schema)
        Draft202012Validator.check_schema(cls.comparison_schema)
        registry = Registry().with_resource(
            cls.model_schema["$id"], Resource.from_contents(cls.model_schema)
        )
        cls.comparison_validator = Draft202012Validator(
            cls.comparison_schema, registry=registry
        )
        cls.payload = build_vector_spectrum_comparison().to_dict()

    def test_generated_model_predictions_validate(self) -> None:
        validator = Draft202012Validator(self.model_schema)
        for prediction in self.payload["model_predictions"]:
            validator.validate(prediction)

    def test_generated_comparison_record_validates(self) -> None:
        self.comparison_validator.validate(self.payload)

    def test_descriptive_metrics_cannot_become_acceptance_gates(self) -> None:
        invalid = json.loads(json.dumps(self.payload))
        invalid["descriptive_comparisons"][0]["is_acceptance_gate"] = True
        self.assertFalse(self.comparison_validator.is_valid(invalid))


if __name__ == "__main__":
    unittest.main()
