"""Regression checks for HoloForge's public/private research boundary."""

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class PublicContentPolicyTests(unittest.TestCase):
    def test_private_workspace_names_are_ignored(self) -> None:
        entries = {
            line.strip()
            for line in (ROOT / ".gitignore").read_text(encoding="utf-8").splitlines()
        }
        self.assertIn("/.private-research/", entries)
        self.assertIn("/unpublished/", entries)

    def test_public_incubator_example_makes_no_novelty_claim(self) -> None:
        with (
            ROOT / "incubator/examples/hypothesis-card.example.json"
        ).open(encoding="utf-8") as handle:
            card = json.load(handle)

        self.assertTrue(card["title"].startswith("Example only:"))
        self.assertEqual(
            card["target_domain"], "unspecified-strongly-coupled-system"
        )
        self.assertEqual(card["prior_work"]["search_status"], "not-searched")
        self.assertEqual(card["claims"][0]["support_level"], "hypothesis")
        self.assertEqual(card["claims"][0]["review_status"], "unreviewed")

    def test_policy_requires_an_external_private_repository(self) -> None:
        constitution = (ROOT / "CONSTITUTION.md").read_text(encoding="utf-8")
        workflow = (ROOT / "docs/private-research-workflow.md").read_text(
            encoding="utf-8"
        )
        incubator = (ROOT / "incubator/README.md").read_text(encoding="utf-8")

        combined = "\n".join((constitution, workflow, incubator)).lower()
        self.assertIn("separate private repository", combined)
        self.assertIn("journal acceptance", combined)
        self.assertIn("explicit", combined)
        self.assertNotIn("/users/", combined)

    def test_synthetic_dry_run_stops_before_a_claim(self) -> None:
        dry_run = (ROOT / "docs/explore-public-dry-run.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("not a novel research project", dry_run.lower())
        self.assertIn("stop: novelty", dry_run.lower())
        self.assertIn("do not promote", dry_run.lower())


if __name__ == "__main__":
    unittest.main()
