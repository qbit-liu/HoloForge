"""Regression checks for public, cross-agent onboarding."""

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class AgentOnboardingTests(unittest.TestCase):
    def test_agent_entrypoints_are_linked_and_consistent(self) -> None:
        agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
        claude = (ROOT / "CLAUDE.md").read_text(encoding="utf-8")
        readme = (ROOT / "README.md").read_text(encoding="utf-8")

        self.assertIn("docs/agent-quickstart.md", agents)
        self.assertIn("@AGENTS.md", claude)
        self.assertIn("docs/agent-quickstart.md", readme)
        for workflow in (
            "holoforge-add-benchmark",
            "holoforge-research-gate",
            "holoforge-public-export",
        ):
            self.assertIn(workflow, agents)

    def test_quickstart_covers_supported_agent_paths_and_boundaries(self) -> None:
        guide = (ROOT / "docs" / "agent-quickstart.md").read_text(
            encoding="utf-8"
        )
        lower = " ".join(guide.lower().split())

        for expected in (
            "codex",
            "claude code",
            "other agents",
            "inspect-only first prompt",
            "separate access-controlled repository",
            "human disclosure approval",
            "python -m unittest discover -s tests -v",
        ):
            self.assertIn(expected, lower)

    def test_onboarding_is_public_safe(self) -> None:
        onboarding = "\n".join(
            path.read_text(encoding="utf-8")
            for path in (
                ROOT / "AGENTS.md",
                ROOT / "CLAUDE.md",
                ROOT / "docs" / "agent-quickstart.md",
            )
        )
        lower = onboarding.lower()

        self.assertNotIn("/users/", lower)
        self.assertNotIn("holoforge-explore-private", lower)
        for private_identifier in ("c01", "c02", "c03", "d001", "m001"):
            self.assertNotIn(private_identifier, lower)

    def test_claude_local_instructions_are_not_committed(self) -> None:
        ignored = {
            line.strip()
            for line in (ROOT / ".gitignore").read_text(encoding="utf-8").splitlines()
        }
        self.assertIn("CLAUDE.local.md", ignored)


if __name__ == "__main__":
    unittest.main()
