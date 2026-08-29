"""Contracts for solver-free benchmark capability inspection."""

from __future__ import annotations

import copy
from importlib import resources
import io
import json
from pathlib import Path
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

from jsonschema import Draft202012Validator, FormatChecker, ValidationError

from holoforge.benchmarks.registry import BUILTIN_BENCHMARKS
from holoforge.capabilities import BUILTIN_CAPABILITIES
from holoforge.cli import main
from holoforge.core.capabilities import (
    CapabilityReceipt,
    CapabilityReceiptError,
    CapabilityRegistry,
)


ROOT = Path(__file__).resolve().parents[1]
RECEIPT_DIRECTORY = ROOT / "src" / "holoforge" / "data" / "capabilities"


def load_receipt(identifier: str):
    return json.loads((RECEIPT_DIRECTORY / f"{identifier}.json").read_text())


class CapabilitySchemaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.schema = json.loads(
            (ROOT / "schemas" / "benchmark-capability.schema.json").read_text()
        )
        Draft202012Validator.check_schema(cls.schema)
        cls.validator = Draft202012Validator(
            cls.schema, format_checker=FormatChecker()
        )

    def test_every_builtin_receipt_is_schema_valid_and_owner_approved(self) -> None:
        receipt_paths = sorted(
            RECEIPT_DIRECTORY.glob("*.json"), key=lambda path: path.stem
        )
        self.assertEqual(
            [path.stem for path in receipt_paths],
            list(BUILTIN_BENCHMARKS.identifiers),
        )
        for path in receipt_paths:
            with self.subTest(path=path):
                receipt = json.loads(path.read_text())
                self.validator.validate(receipt)
                self.assertEqual(receipt["benchmark_id"], path.stem)
                provenance = receipt["provenance"]
                self.assertEqual(provenance["review_status"], "approved")
                self.assertEqual(provenance["reviewed_by"], "Xin-Yi Liu")
                self.assertEqual(provenance["reviewed_on"], "2026-08-29")

    def test_schema_rejects_approved_receipt_without_reviewer(self) -> None:
        receipt = load_receipt("soft-wall-vector")
        del receipt["provenance"]["reviewed_by"]
        del receipt["provenance"]["reviewed_on"]
        with self.assertRaises(ValidationError):
            self.validator.validate(receipt)


class CapabilityRuntimeTests(unittest.TestCase):
    def test_registry_exactly_matches_builtins_and_model_cards(self) -> None:
        self.assertEqual(
            BUILTIN_CAPABILITIES.identifiers,
            BUILTIN_BENCHMARKS.identifiers,
        )
        for adapter in BUILTIN_BENCHMARKS:
            receipt = BUILTIN_CAPABILITIES.get(adapter.identifier).to_dict()
            declared = {
                (item["identifier"], item["repository_path"])
                for item in receipt["evidence"]["model_cards"]
            }
            expected = {
                (item.identifier, item.repository_path)
                for item in adapter.model_cards
            }
            self.assertEqual(declared, expected)
            for path in receipt["evidence"]["documentation"]:
                self.assertTrue((ROOT / path).is_file())

    def test_exact_id_classification_is_non_aggregate(self) -> None:
        receipt = BUILTIN_CAPABILITIES.get("soft-wall-vector")
        self.assertEqual(
            receipt.inspect("observable.vector-squared-masses").status,
            "qualified",
        )
        self.assertEqual(
            receipt.inspect("gap.decay-constants").status,
            "known-gap",
        )
        self.assertEqual(
            receipt.inspect("observable.not-declared").status,
            "not-declared",
        )
        payload = receipt.to_dict(("observable.vector-squared-masses",))
        self.assertFalse(payload["inspection"]["solver_executed"])
        self.assertEqual(
            payload["inspection"]["scientific_judgment"], "not-performed"
        )

    def test_runtime_rejects_malformed_or_contradictory_receipts(self) -> None:
        base = load_receipt("soft-wall-vector")
        cases = []

        unknown = copy.deepcopy(base)
        unknown["undeclared"] = True
        cases.append(unknown)

        duplicate = copy.deepcopy(base)
        duplicate["known_gaps"][0]["id"] = duplicate["outputs"][0]["id"]
        cases.append(duplicate)

        empty = copy.deepcopy(base)
        empty["outputs"] = []
        cases.append(empty)

        unsafe = copy.deepcopy(base)
        unsafe["evidence"]["documentation"] = ["../private.md"]
        cases.append(unsafe)

        contradictory = copy.deepcopy(base)
        contradictory["provenance"]["review_status"] = "unreviewed"
        contradictory["provenance"]["reviewed_by"] = "Reviewer"
        cases.append(contradictory)

        for receipt in cases:
            with self.subTest(receipt=receipt):
                with self.assertRaises(CapabilityReceiptError):
                    CapabilityReceipt(receipt)

    def test_registry_rejects_duplicate_receipts(self) -> None:
        receipt = CapabilityReceipt(load_receipt("soft-wall-vector"))
        with self.assertRaisesRegex(
            CapabilityReceiptError, "duplicate benchmark capability receipt"
        ):
            CapabilityRegistry((receipt, receipt))

    def test_packaged_resources_include_every_receipt(self) -> None:
        packaged = sorted(
            item.name.removesuffix(".json")
            for item in resources.files("holoforge.data.capabilities").iterdir()
            if item.name.endswith(".json")
        )
        self.assertEqual(packaged, list(BUILTIN_BENCHMARKS.identifiers))
        setup = (ROOT / "setup.cfg").read_text()
        self.assertIn("data/capabilities/*.json", setup)


class CapabilityCliTests(unittest.TestCase):
    def test_inspect_never_dispatches_a_benchmark_solver(self) -> None:
        output = io.StringIO()
        with (
            patch.object(
                BUILTIN_BENCHMARKS,
                "get",
                side_effect=AssertionError("solver dispatch reached"),
            ),
            redirect_stdout(output),
        ):
            status = main(
                [
                    "inspect",
                    "benchmark",
                    "soft-wall-vector",
                    "--require",
                    "observable.vector-squared-masses",
                    "--json",
                ]
            )
        payload = json.loads(output.getvalue())
        self.assertEqual(status, 0)
        self.assertFalse(payload["inspection"]["solver_executed"])

    def test_unqualified_requirement_uses_controlled_exit_one(self) -> None:
        output = io.StringIO()
        with redirect_stdout(output):
            status = main(
                [
                    "inspect",
                    "benchmark",
                    "soft-wall-vector",
                    "--require",
                    "gap.decay-constants",
                    "--json",
                ]
            )
        payload = json.loads(output.getvalue())
        self.assertEqual(status, 1)
        self.assertEqual(
            payload["inspection"]["requirements"][0]["status"],
            "known-gap",
        )


if __name__ == "__main__":
    unittest.main()
