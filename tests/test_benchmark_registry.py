"""Contracts and compatibility gates for deterministic benchmark dispatch."""

from __future__ import annotations

from dataclasses import replace
import io
import json
from pathlib import Path
import tempfile
import unittest
from contextlib import redirect_stdout

from holoforge.benchmarks.registry import BUILTIN_BENCHMARKS
from holoforge.cli import build_parser, main
from holoforge.core.registry import (
    BenchmarkAdapter,
    BenchmarkExecution,
    BenchmarkRegistry,
    BenchmarkRegistryError,
    ModelCardReference,
)


ROOT = Path(__file__).resolve().parents[1]
SYNTHETIC_CARD = ModelCardReference(
    identifier="synthetic.public.registry-test",
    schema_version="0.5-test",
    repository_path="domains/synthetic/model-card.json",
    sha256="0" * 64,
)


def configure_synthetic(parser) -> None:
    parser.add_argument("--control", type=float, default=2.0)


def execute_synthetic(args) -> BenchmarkExecution:
    payload = {
        "schema_version": "0.5-test",
        "benchmark": "synthetic-registry-test",
        "support_level": "reproduced",
        "configuration": {"control": args.control},
        "numerical_method": {"route": "synthetic maintained function"},
        "results": [{"value": 2.0 * args.control}],
        "acceptance_checks": [
            {
                "id": "synthetic-pass",
                "description": "Synthetic adapter reaches generic dispatch.",
                "passed": True,
            }
        ],
        "software_versions": {"holoforge": "test", "python": "test"},
        "passed": True,
        "scope": "Synthetic registry fixture; no scientific claim.",
    }
    return BenchmarkExecution(payload=payload, passed=True)


def render_synthetic(execution: BenchmarkExecution):
    return (f"synthetic value = {execution.payload['results'][0]['value']:g}",)


def synthetic_state(payload):
    return {
        "model_identifier": SYNTHETIC_CARD.identifier,
        "ensemble": "synthetic registry test",
        "fixed_variables": {"background": "synthetic"},
        "approximation": "synthetic infrastructure fixture",
        "phase_branch": "synthetic branch",
        "parameters": {"control": payload["configuration"]["control"]},
        "declared_controls": ["control"],
        "boundary_source_conditions": {"boundary": "synthetic"},
        "conventions": {"units": "dimensionless"},
        "source_record_versions": {"fixture": "0.5-test"},
    }


SYNTHETIC_ADAPTER = BenchmarkAdapter(
    identifier="synthetic-registry-test",
    description="Exercise generic benchmark registration.",
    configure_parser=configure_synthetic,
    execute=execute_synthetic,
    render_human=render_synthetic,
    scientific_state=synthetic_state,
    model_cards=(SYNTHETIC_CARD,),
)


class BenchmarkRegistryTests(unittest.TestCase):
    def test_registry_order_is_identifier_sorted(self) -> None:
        reverse = tuple(reversed(tuple(BUILTIN_BENCHMARKS)))
        registry = BenchmarkRegistry(reverse)
        self.assertEqual(registry.identifiers, tuple(sorted(registry.identifiers)))
        self.assertEqual(registry.identifiers, BUILTIN_BENCHMARKS.identifiers)

    def test_builtin_adapter_glue_is_isolated_by_benchmark(self) -> None:
        expected_modules = {
            "dewolfe-gubser-rosen-emd": (
                "holoforge.benchmarks.adapters.dewolfe_gubser_rosen_emd"
            ),
            "dewolfe-gubser-rosen-emd-finite-density": (
                "holoforge.benchmarks.adapters."
                "dewolfe_gubser_rosen_emd_finite_density"
            ),
            "gubser-nellore-ed": (
                "holoforge.benchmarks.adapters.gubser_nellore_ed"
            ),
            "gubser-rocha-emd": (
                "holoforge.benchmarks.adapters.gubser_rocha_emd"
            ),
            "hard-wall-vector": (
                "holoforge.benchmarks.adapters.hard_wall_vector"
            ),
            "hard-wall-chiral": (
                "holoforge.benchmarks.adapters.hard_wall_chiral"
            ),
            "holographic-superconductor": (
                "holoforge.benchmarks.adapters.holographic_superconductor"
            ),
            "holographic-superconductor-optical": (
                "holoforge.benchmarks.adapters."
                "holographic_superconductor_optical"
            ),
            "linear-axion-dc": (
                "holoforge.benchmarks.adapters.linear_axion_dc"
            ),
            "soft-wall-vector": (
                "holoforge.benchmarks.adapters.soft_wall_vector"
            ),
        }
        self.assertEqual(
            {
                adapter.identifier: adapter.execute.__module__
                for adapter in BUILTIN_BENCHMARKS
            },
            expected_modules,
        )

        composition_root = (
            ROOT / "src" / "holoforge" / "benchmarks" / "registry.py"
        ).read_text()
        self.assertNotIn("def _configure_", composition_root)
        self.assertNotIn("def _execute_", composition_root)
        self.assertNotIn("def _render_", composition_root)

    def test_architecture_guide_documents_the_adapter_boundary(self) -> None:
        readme = (ROOT / "README.md").read_text()
        architecture = (ROOT / "docs" / "architecture.md").read_text()
        self.assertIn("docs/architecture.md", readme)
        self.assertIn("src/holoforge/benchmarks/adapters/", architecture)
        self.assertIn("composition root", architecture)
        self.assertIn("does not standardize equations", architecture)

    def test_duplicate_identifier_fails_before_execution(self) -> None:
        duplicate = replace(SYNTHETIC_ADAPTER, description="duplicate")
        with self.assertRaisesRegex(
            BenchmarkRegistryError, "duplicate benchmark identifier"
        ):
            BenchmarkRegistry((SYNTHETIC_ADAPTER, duplicate))

    def test_malformed_adapter_metadata_fails_closed(self) -> None:
        cases = (
            replace(SYNTHETIC_ADAPTER, identifier="Invalid Identifier"),
            replace(SYNTHETIC_ADAPTER, description=""),
            replace(SYNTHETIC_ADAPTER, execute=None),
            replace(SYNTHETIC_ADAPTER, model_cards=()),
            replace(
                SYNTHETIC_ADAPTER,
                model_cards=(replace(SYNTHETIC_CARD, repository_path="/tmp/card"),),
            ),
            replace(
                SYNTHETIC_ADAPTER,
                model_cards=(replace(SYNTHETIC_CARD, repository_path="../card"),),
            ),
            replace(
                SYNTHETIC_ADAPTER,
                model_cards=(replace(SYNTHETIC_CARD, sha256="not-a-digest"),),
            ),
        )
        for adapter in cases:
            with self.subTest(adapter=adapter):
                with self.assertRaises(BenchmarkRegistryError):
                    BenchmarkRegistry((adapter,))

    def test_non_adapter_entry_fails_with_registry_error(self) -> None:
        with self.assertRaisesRegex(BenchmarkRegistryError, "BenchmarkAdapter"):
            BenchmarkRegistry((object(),))

    def test_synthetic_adapter_uses_generic_cli_and_bundle_path(self) -> None:
        registry = BenchmarkRegistry((SYNTHETIC_ADAPTER,))
        output = io.StringIO()
        with tempfile.TemporaryDirectory() as directory:
            bundle = Path(directory) / "bundle"
            with redirect_stdout(output):
                status = main(
                    [
                        "verify",
                        "synthetic-registry-test",
                        "--control",
                        "3",
                        "--bundle-dir",
                        str(bundle),
                        "--json",
                    ],
                    benchmark_registry=registry,
                )
            payload = json.loads(output.getvalue())
            manifest = json.loads((bundle / "manifest.json").read_text())

        self.assertEqual(status, 0)
        self.assertEqual(payload["results"][0]["value"], 6.0)
        self.assertEqual(Path(payload["evidence_bundle"]), bundle)
        self.assertEqual(manifest["scientific_state"], synthetic_state(payload))
        self.assertEqual(manifest["model_cards"], [SYNTHETIC_CARD.to_dict()])

    def test_help_uses_stable_registry_order(self) -> None:
        parser = build_parser(BUILTIN_BENCHMARKS)
        output = io.StringIO()
        with self.assertRaises(SystemExit), redirect_stdout(output):
            parser.parse_args(["verify", "--help"])
        help_text = output.getvalue()
        positions = [
            help_text.index(identifier)
            for identifier in BUILTIN_BENCHMARKS.identifiers
        ]
        self.assertEqual(positions, sorted(positions))

    def test_builtin_bundle_metadata_comes_from_adapter(self) -> None:
        adapter = BUILTIN_BENCHMARKS.get("soft-wall-vector")
        output = io.StringIO()
        with tempfile.TemporaryDirectory() as directory:
            bundle = Path(directory) / "bundle"
            with redirect_stdout(output):
                status = main(
                    [
                        "verify",
                        adapter.identifier,
                        "--grid-points",
                        "600",
                        "--bundle-dir",
                        str(bundle),
                        "--json",
                    ]
                )
            result = json.loads((bundle / "records" / "result.json").read_text())
            manifest = json.loads((bundle / "manifest.json").read_text())

        self.assertEqual(status, 0)
        self.assertEqual(manifest["scientific_state"], adapter.scientific_state(result))
        self.assertEqual(
            manifest["model_cards"],
            [reference.to_dict() for reference in adapter.model_cards],
        )

    def test_cli_has_no_benchmark_identifier_condition(self) -> None:
        source = (ROOT / "src" / "holoforge" / "cli.py").read_text()
        self.assertNotIn("args.benchmark ==", source)
        self.assertNotIn("command_identity == \"verify ", source)


if __name__ == "__main__":
    unittest.main()
