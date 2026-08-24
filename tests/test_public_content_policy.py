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

    def test_review_packet_uses_accessible_status_colors_and_critic_leads(self):
        template = (
            ROOT / "docs/templates/review-packet-template.tex"
        ).read_text(encoding="utf-8")
        workflow = " ".join(
            (ROOT / "docs/research-gate-workflow.md")
            .read_text(encoding="utf-8")
            .lower()
            .split()
        )
        skill = " ".join(
            (ROOT / ".agents/skills/holoforge-research-gate/SKILL.md")
            .read_text(encoding="utf-8")
            .lower()
            .split()
        )

        for command in (
            r"\statuspass",
            r"\statusfail",
            r"\statusstop",
            r"\statuspending",
            r"\statusskipped",
            r"\statusclosed",
            r"\statusretained",
        ):
            self.assertIn(command, template)

        self.assertIn("color is never the only carrier of meaning", workflow)
        self.assertIn("short bold challenge sentence", workflow)
        self.assertIn("semantic status commands", skill)
        self.assertIn("short bold challenge sentence", skill)

    def test_pdf_review_rule_covers_explore_and_forge_verify(self):
        workflow = " ".join(
            (ROOT / "docs/research-gate-workflow.md")
            .read_text(encoding="utf-8")
            .lower()
            .split()
        )
        benchmark_skill = " ".join(
            (ROOT / ".agents/skills/holoforge-add-benchmark/SKILL.md")
            .read_text(encoding="utf-8")
            .lower()
            .split()
        )

        self.assertIn("private explore gates", workflow)
        self.assertIn("public forge/verify scientific-contract reviews", workflow)
        self.assertIn("difficult to review reliably in markdown", benchmark_skill)
        self.assertIn("before requesting owner approval", benchmark_skill)
        self.assertIn("docs/templates/review-packet-template.tex", benchmark_skill)
        self.assertIn("compile twice", benchmark_skill)
        self.assertIn("render every page", benchmark_skill)
        self.assertIn("not itself approval", benchmark_skill)

        ignored = {
            line.strip()
            for line in (ROOT / ".gitignore").read_text(encoding="utf-8").splitlines()
        }
        self.assertIn("/output/", ignored)
        self.assertIn("/tmp/", ignored)

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

    def test_post_closure_handoff_repeats_status_and_response_paths(self):
        workflow = " ".join(
            (ROOT / "docs/research-gate-workflow.md")
            .read_text(encoding="utf-8")
            .lower()
            .split()
        )
        private_workflow = " ".join(
            (ROOT / "docs/private-research-workflow.md")
            .read_text(encoding="utf-8")
            .lower()
            .split()
        )
        skill = " ".join(
            (ROOT / ".agents/skills/holoforge-research-gate/SKILL.md")
            .read_text(encoding="utf-8")
            .lower()
            .split()
        )

        for text in (workflow, private_workflow, skill):
            self.assertIn("after", text)
            self.assertIn("closed", text)
            self.assertIn("completed/current/next", text)
            self.assertIn("a-e", text)
            self.assertIn("remain paused", text)

        self.assertIn("awaiting_owner: false", workflow)
        self.assertIn("must not receive a fabricated pending owner menu", workflow)
        self.assertIn("does not reopen the completed gate", private_workflow)

    def test_explore_intake_scorecard_requires_all_five_readiness_tests(self):
        workflow = (ROOT / "docs/research-gate-workflow.md").read_text(
            encoding="utf-8"
        ).lower()
        skill = (
            ROOT / ".agents/skills/holoforge-research-gate/SKILL.md"
        ).read_text(encoding="utf-8").lower()
        scorecard = (
            ROOT
            / ".agents/skills/holoforge-research-gate/assets/explore-intake-scorecard.example.md"
        ).read_text(encoding="utf-8").lower()
        combined = " ".join("\n".join((workflow, skill, scorecard)).split())

        for readiness_test in (
            "source-complete inputs",
            "invariant target beyond the generic baseline",
            "cheap kill test",
            "positive-result endpoint",
            "cost ceiling",
        ):
            self.assertIn(readiness_test, combined)

        self.assertIn("all five pass", combined)
        self.assertIn("one named evidence task", combined)
        self.assertIn("any failed item defers or rejects", combined)
        self.assertIn("not a novelty", scorecard)
        self.assertIn("prior-knowledge review", scorecard)
        self.assertIn("stable knowledge or lesson id", combined)
        self.assertIn("stable lesson id", combined)
        self.assertIn("primary evidence", combined)
        self.assertIn("candidate-specific control", combined)
        self.assertIn("if no item applies", scorecard)
        self.assertIn("previous gate's failure", scorecard)
        self.assertNotIn("/users/", scorecard)
        self.assertNotIn("holoforge-explore-private", scorecard)

    def test_intake_records_portfolio_intent_scope_and_publication_path(self):
        workflow = (
            ROOT / "docs/research-gate-workflow.md"
        ).read_text(encoding="utf-8").lower()
        private_workflow = (
            ROOT / "docs/private-research-workflow.md"
        ).read_text(encoding="utf-8").lower()
        skill = (
            ROOT / ".agents/skills/holoforge-research-gate/SKILL.md"
        ).read_text(encoding="utf-8").lower()
        scorecard = (
            ROOT
            / ".agents/skills/holoforge-research-gate/assets/explore-intake-scorecard.example.md"
        ).read_text(encoding="utf-8").lower()
        combined = " ".join(
            "\n".join((workflow, private_workflow, skill, scorecard)).split()
        )

        for required_term in (
            "portfolio intent",
            "publication-targeted",
            "search shape",
            "domains considered",
            "domains intentionally excluded",
            "domain-coverage",
            "publication-pathway assessment",
            "paper-shaped question",
            "physical discriminator or mechanism",
            "short gate sequence",
            "repair or pivot budget",
        ):
            self.assertIn(required_term, combined)

        self.assertIn("holographic qcd", workflow)
        self.assertIn("not a quota", combined)
        self.assertIn("does not establish novelty", scorecard)
        self.assertIn("does not establish novelty", workflow)
        self.assertIn("replace the five scientific readiness tests", workflow)
        self.assertNotIn("/users/", combined)
        self.assertNotIn("holoforge-explore-private", combined)

    def test_repeated_blockers_use_a_bounded_impasse_protocol(self):
        workflow = (
            ROOT / "docs/research-gate-workflow.md"
        ).read_text(encoding="utf-8").lower()
        private_workflow = (
            ROOT / "docs/private-research-workflow.md"
        ).read_text(encoding="utf-8").lower()
        skill = (
            ROOT / ".agents/skills/holoforge-research-gate/SKILL.md"
        ).read_text(encoding="utf-8").lower()
        instructions = (ROOT / "AGENTS.md").read_text(encoding="utf-8").lower()
        quickstart = (
            ROOT / "docs/agent-quickstart.md"
        ).read_text(encoding="utf-8").lower()
        combined = " ".join(
            "\n".join(
                (workflow, private_workflow, skill, instructions, quickstart)
            ).split()
        )

        for required_term in (
            "bounded impasse protocol",
            "classify the blocker",
            "targeted external evidence",
            "independent physics audit",
            "official documentation",
            "conditioning",
            "maintained library",
            "one bounded repair",
            "self-derived correction",
            "technical stop",
        ):
            self.assertIn(required_term, combined)

        self.assertIn("internet result is a locator for evidence", workflow)
        self.assertIn("does not validate a fix", skill)
        self.assertIn("do not loosen a threshold", workflow)
        self.assertNotIn("/users/", combined)
        self.assertNotIn("holoforge-explore-private", combined)

    def test_closed_gate_requires_a_generic_research_retrospective(self):
        workflow = (
            ROOT / "docs/research-gate-workflow.md"
        ).read_text(encoding="utf-8").lower()
        lesson_guide = (
            ROOT / "docs/learning-from-results.md"
        ).read_text(encoding="utf-8").lower()
        template = (
            ROOT / "docs/templates/research-retrospective-template.md"
        ).read_text(encoding="utf-8").lower()
        skill = (
            ROOT / ".agents/skills/holoforge-research-gate/SKILL.md"
        ).read_text(encoding="utf-8").lower()
        combined = "\n".join((workflow, lesson_guide, template, skill))

        for outcome in (
            "positive",
            "negative",
            "inconclusive",
            "conditional",
            "source stop",
            "prior-art stop",
            "technical stop",
        ):
            self.assertIn(outcome, combined)

        for required_boundary in (
            "what must not be inferred",
            "reopening trigger",
            "feed forward",
            "must not retroactively change",
            "physical negative result",
            "agent retrieval loop",
            "applicability to future gates",
            "stable lesson id",
            "retrieval tags",
        ):
            self.assertIn(required_boundary, combined)

        self.assertIn("research-retrospective-template.md", workflow)
        self.assertIn("research-retrospective-template.md", skill)
        self.assertNotIn("/users/", combined)
        self.assertNotIn("holoforge-explore-private", combined)
        for private_identifier in ("c01", "c02", "c03", "d001", "m001"):
            self.assertNotIn(private_identifier, combined)

    def test_source_stop_requires_a_version_of_record_audit(self):
        workflow = (
            ROOT / "docs/research-gate-workflow.md"
        ).read_text(encoding="utf-8").lower()
        skill = (
            ROOT / ".agents/skills/holoforge-research-gate/SKILL.md"
        ).read_text(encoding="utf-8").lower()
        combined = " ".join("\n".join((workflow, skill)).split())

        for required_term in (
            "source-normalization stop",
            "version of record",
            "accepted manuscript",
            "correction",
            "erratum",
            "doi",
            "version/date",
            "exact locator",
            "preprint evidence",
            "author intent",
            "private code",
        ):
            self.assertIn(required_term, combined)

        self.assertNotIn("/users/", combined)
        self.assertNotIn("holoforge-explore-private", combined)
        for private_identifier in ("c01", "c02", "c03", "d001", "m001"):
            self.assertNotIn(private_identifier, combined)

    def test_research_knowledge_covers_more_than_failure_lessons(self):
        workflow = (
            ROOT / "docs/research-gate-workflow.md"
        ).read_text(encoding="utf-8").lower()
        lesson_guide = (
            ROOT / "docs/learning-from-results.md"
        ).read_text(encoding="utf-8").lower()
        template = (
            ROOT / "docs/templates/research-knowledge-template.md"
        ).read_text(encoding="utf-8").lower()
        skill = (
            ROOT / ".agents/skills/holoforge-research-gate/SKILL.md"
        ).read_text(encoding="utf-8").lower()
        instructions = (ROOT / "AGENTS.md").read_text(encoding="utf-8").lower()
        combined = "\n".join(
            (workflow, lesson_guide, template, skill, instructions)
        )

        for required_term in (
            "working knowledge",
            "reviewed knowledge",
            "stable knowledge id",
            "stable lesson id",
            "knowledge class",
            "durable milestone",
            "provisional",
            "corroborated",
            "challenged",
            "ready for owner review",
            "promoted",
            "retired",
            "primary evidence",
            "what must not be inferred",
            "not background telemetry",
            "research-knowledge-template.md",
        ):
            self.assertIn(required_term, combined)

        for knowledge_class in (
            "literature/source",
            "model/dictionary",
            "analytic/derivation",
            "numerical/method",
            "data/comparison",
            "result",
            "decision/workflow",
            "tooling/reproducibility",
        ):
            self.assertIn(knowledge_class, combined)

        self.assertIn("named human", combined)
        self.assertIn("exact source version", combined)
        self.assertIn("do not ingest every paper", combined)
        self.assertIn("owner-reviewed closure", combined)
        self.assertIn("must not retroactively change", combined)
        self.assertNotIn("/users/", combined)
        self.assertNotIn("holoforge-explore-private", combined)
        for private_identifier in ("c01", "c02", "c03", "d001", "m001"):
            self.assertNotIn(private_identifier, combined)

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
