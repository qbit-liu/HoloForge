"""Regression checks for the Version 0.5 public compatibility contract."""

from pathlib import Path
import unittest

import holoforge
from holoforge import benchmarks, comparisons, core


ROOT = Path(__file__).resolve().parents[1]


class Version05PolicyTests(unittest.TestCase):
    def test_every_deliberate_package_export_is_documented(self) -> None:
        policy = (ROOT / "docs/version-0.5-compatibility-policy.md").read_text()
        for module in (core, benchmarks, comparisons):
            for name in module.__all__:
                with self.subTest(module=module.__name__, name=name):
                    self.assertIn(f"`{module.__name__}.{name}`", policy)

    def test_policy_freezes_commands_schemas_and_failure_meanings(self) -> None:
        policy = (ROOT / "docs/version-0.5-compatibility-policy.md").read_text()
        for command in (
            "holoforge verify soft-wall-vector",
            "holoforge verify hard-wall-vector",
            "holoforge verify holographic-superconductor",
            "holoforge verify linear-axion-dc",
            "holoforge compare vector-spectrum",
            "holoforge audit bundle",
            "holoforge audit compatibility",
        ):
            self.assertIn(command, policy)
        for schema_version in ("`0.1`", "`0.3`", "`0.4`"):
            self.assertIn(schema_version, policy)
        for exit_code in ("Exit `0`", "Exit `1`", "Exit `2`"):
            self.assertIn(exit_code, policy)
        self.assertIn("fail closed", policy)
        self.assertIn("rest of `0.5.x`", policy)

    def test_security_policy_uses_a_private_route(self) -> None:
        policy = (ROOT / "SECURITY.md").read_text()
        normalized = " ".join(policy.split())
        self.assertIn("security/advisories/new", policy)
        self.assertIn("Do not include the sensitive details", normalized)
        self.assertIn("unpublished research", policy)

    def test_ci_covers_wheel_relocation_on_three_operating_systems(self) -> None:
        workflow = (ROOT / ".github/workflows/ci.yml").read_text()
        for runner in ("ubuntu-latest", "macos-latest", "windows-latest"):
            self.assertIn(runner, workflow)
        self.assertIn("python -m build --wheel", workflow)
        self.assertIn("--force-reinstall dist/*.whl", workflow)
        self.assertIn("holoforge verify linear-axion-dc", workflow)
        self.assertIn("holoforge audit bundle relocated/portability-bundle", workflow)
        self.assertNotIn("continue-on-error", workflow)

    def test_release_metadata_is_synchronized(self) -> None:
        self.assertEqual(holoforge.__version__, "0.5.0")
        citation = (ROOT / "CITATION.cff").read_text()
        changelog = (ROOT / "CHANGELOG.md").read_text()
        readme = (ROOT / "README.md").read_text()
        self.assertIn("version: 0.5.0", citation)
        self.assertIn("date-released: 2026-08-09", citation)
        self.assertIn("## [0.5.0] - 2026-08-09", changelog)
        self.assertIn("latest public release is `0.5.0`", readme)


if __name__ == "__main__":
    unittest.main()
