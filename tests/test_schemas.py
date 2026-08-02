"""Validate the v0.1 schemas and their canonical examples."""

import copy
import json
import unittest
from pathlib import Path
from typing import Any, Dict

from jsonschema import Draft202012Validator, FormatChecker, ValidationError


ROOT = Path(__file__).resolve().parents[1]


def load_json(relative_path: str) -> Dict[str, Any]:
    with (ROOT / relative_path).open(encoding="utf-8") as handle:
        return json.load(handle)


class CardSchemaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.model_schema = load_json("schemas/model-card.schema.json")
        cls.hypothesis_schema = load_json("schemas/hypothesis-card.schema.json")
        Draft202012Validator.check_schema(cls.model_schema)
        Draft202012Validator.check_schema(cls.hypothesis_schema)
        cls.model_validator = Draft202012Validator(
            cls.model_schema, format_checker=FormatChecker()
        )
        cls.hypothesis_validator = Draft202012Validator(
            cls.hypothesis_schema, format_checker=FormatChecker()
        )

    def test_soft_wall_model_card_is_valid(self) -> None:
        card = load_json("domains/qcd/soft_wall_vector/model-card.json")
        self.model_validator.validate(card)

    def test_incubator_hypothesis_example_is_valid(self) -> None:
        card = load_json("incubator/examples/hypothesis-card.example.json")
        self.hypothesis_validator.validate(card)

    def test_model_card_cannot_silently_switch_to_explore_mode(self) -> None:
        card = load_json("domains/qcd/soft_wall_vector/model-card.json")
        invalid = copy.deepcopy(card)
        invalid["mode"] = "explore"
        with self.assertRaises(ValidationError):
            self.model_validator.validate(invalid)

    def test_hypothesis_claim_cannot_be_labelled_established(self) -> None:
        card = load_json("incubator/examples/hypothesis-card.example.json")
        invalid = copy.deepcopy(card)
        invalid["claims"][0]["support_level"] = "established-source"
        with self.assertRaises(ValidationError):
            self.hypothesis_validator.validate(invalid)

    def test_cards_require_ai_and_human_review_provenance(self) -> None:
        card = load_json("domains/qcd/soft_wall_vector/model-card.json")
        invalid = copy.deepcopy(card)
        del invalid["claims"][0]["generated_by_ai"]
        with self.assertRaises(ValidationError):
            self.model_validator.validate(invalid)

    def test_approved_claim_requires_named_reviewer_and_date(self) -> None:
        card = load_json("domains/qcd/soft_wall_vector/model-card.json")
        invalid = copy.deepcopy(card)
        del invalid["claims"][0]["reviewed_by"]
        with self.assertRaises(ValidationError):
            self.model_validator.validate(invalid)


if __name__ == "__main__":
    unittest.main()
