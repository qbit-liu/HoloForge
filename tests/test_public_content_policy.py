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

    def test_generic_gate_workflow_preserves_three_tracks_and_boundaries(self):
        workflow = (ROOT / "docs/research-gate-workflow.md").read_text(
            encoding="utf-8"
        ).lower()

        self.assertIn("new-domain application", workflow)
        self.assertIn("new-subfield or new-phenomenon application", workflow)
        self.assertIn("method transfer or model improvement", workflow)
        self.assertIn("frozen contract", workflow)
        self.assertIn("hostile critic report", workflow)
        self.assertIn("owner review", workflow)
        self.assertIn("scientific support", workflow)
        self.assertIn("research authorization", workflow)
        self.assertIn("disclosure status", workflow)

    def test_review_packet_template_is_generic_and_privacy_safe(self):
        template = (
            ROOT / "docs/templates/review-packet-template.tex"
        ).read_text(encoding="utf-8")
        workflow = (ROOT / "docs/research-gate-workflow.md").read_text(
            encoding="utf-8"
        )
        combined = "\n".join((template, workflow))

        self.assertIn("Outcome.", template)
        self.assertIn("Supported:", template)
        self.assertIn("Not supported:", template)
        self.assertIn("Owner decisions", template)
        self.assertNotIn("/Users/", combined)
        self.assertNotIn("HoloForge-Explore-Private", combined)
        for private_identifier in ("C01", "C02", "C03", "D001", "M001"):
            self.assertNotIn(private_identifier, combined)

    def test_every_owner_decision_request_requires_a_recommendation(self):
        workflow = (ROOT / "docs/research-gate-workflow.md").read_text(
            encoding="utf-8"
        ).lower()
        template = (
            ROOT / "docs/templates/review-packet-template.tex"
        ).read_text(encoding="utf-8").lower()

        self.assertIn("every decision request includes a recommendation", workflow)
        self.assertIn("maps each numbered decision", workflow)
        self.assertIn("evidence-based reason", workflow)
        self.assertIn("what work the recommendation opens", workflow)
        self.assertIn("tradeoff or uncertainty", workflow)
        self.assertIn("recommendation is to pause", workflow)
        self.assertIn("recommendation is advice, not owner approval", workflow)
        self.assertIn("recommended selections", template)
        self.assertIn("reason and scope effect", template)

    def test_readme_leads_with_the_general_platform_not_example_domains(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        overview, implementations = readme.split(
            "## Included reference implementations", maxsplit=1
        )
        lower_overview = " ".join(overview.lower().split())

        self.assertIn("bottom-up gauge/gravity", lower_overview)
        self.assertIn("do not define holoforge's scientific scope", lower_overview)
        for example_specific_term in (
            "qcd",
            "soft-wall",
            "hard-wall",
            "vector-meson",
            "superconductor",
            "pdg",
            "kappa",
            "m_n^2",
        ):
            self.assertNotIn(example_specific_term, lower_overview)

        self.assertIn("holoforge verify soft-wall-vector", implementations)
        self.assertIn("holoforge verify holographic-superconductor", implementations)


if __name__ == "__main__":
    unittest.main()
