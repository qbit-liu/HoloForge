"""Tests for repository-scoped HoloForge skills and export preflight."""

from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / ".agents" / "skills"
AUDIT_SCRIPT = (
    SKILLS / "holoforge-public-export" / "scripts" / "audit_export.py"
)


class AgentSkillTests(unittest.TestCase):
    def test_repository_skills_have_complete_metadata(self) -> None:
        expected = {
            "holoforge-research-gate",
            "holoforge-public-export",
            "holoforge-add-benchmark",
        }
        self.assertEqual(
            {path.name for path in SKILLS.iterdir() if path.is_dir()}, expected
        )

        for name in expected:
            skill = (SKILLS / name / "SKILL.md").read_text(encoding="utf-8")
            metadata = (
                SKILLS / name / "agents" / "openai.yaml"
            ).read_text(encoding="utf-8")
            self.assertIn(f"name: {name}", skill)
            self.assertIn("description:", skill)
            self.assertNotIn("TODO", skill)
            self.assertIn(f"${name}", metadata)

    def run_audit(self, *arguments: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(AUDIT_SCRIPT), *arguments],
            check=False,
            capture_output=True,
            text=True,
        )

    def test_export_audit_accepts_clean_text(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            candidate = Path(directory) / "public.md"
            candidate.write_text("Public benchmark documentation.\n", encoding="utf-8")
            completed = self.run_audit(str(candidate))

        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
        self.assertIn("PASS:", completed.stdout)
        self.assertIn("Manual scientific", completed.stdout)

    def test_export_audit_rejects_home_paths_without_echoing_them(self) -> None:
        cases = (
            ("macOS home path", "/Users/example/research/working-note.md"),
            ("Linux home path", "/home/example/research/working-note.md"),
            ("Windows home path", r"C:\Users\example\research\working-note.md"),
        )
        for expected_rule, private_path in cases:
            with self.subTest(expected_rule=expected_rule):
                with tempfile.TemporaryDirectory() as directory:
                    candidate = Path(directory) / "leak.txt"
                    candidate.write_text(private_path, encoding="utf-8")
                    completed = self.run_audit(str(candidate))

                self.assertEqual(completed.returncode, 1)
                self.assertIn(expected_rule, completed.stdout)
                self.assertNotIn(private_path, completed.stdout)

    def test_export_audit_rejects_private_key_marker(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            candidate = Path(directory) / "key.txt"
            candidate.write_text(
                "-----BEGIN SYNTHETIC PRIVATE KEY-----\n", encoding="utf-8"
            )
            completed = self.run_audit(str(candidate))

        self.assertEqual(completed.returncode, 1)
        self.assertIn("private key material", completed.stdout)

    def test_export_audit_rejects_custom_token_without_echoing_it(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            candidate = root / "candidate.txt"
            token_file = root / "tokens.txt"
            secret_token = "synthetic-private-candidate"
            candidate.write_text(f"contains {secret_token}\n", encoding="utf-8")
            token_file.write_text(f"{secret_token}\n", encoding="utf-8")
            completed = self.run_audit(
                str(candidate), "--forbid-file", str(token_file)
            )

        self.assertEqual(completed.returncode, 1)
        self.assertIn("custom forbidden token", completed.stdout)
        self.assertNotIn(secret_token, completed.stdout)

    def test_export_audit_reports_missing_path_as_error(self) -> None:
        completed = self.run_audit("definitely-missing-export-path")
        self.assertEqual(completed.returncode, 2)
        self.assertIn("audit error:", completed.stderr)


if __name__ == "__main__":
    unittest.main()
