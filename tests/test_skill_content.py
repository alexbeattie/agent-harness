
from pathlib import Path
import json
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "source" / "skills"
MANIFEST = ROOT / "config" / "skills.json"
GENERATED_REFERENCES = {
    SKILLS / "repo-pstack-mode" / "references" / "host-routing.md",
    SKILLS / "repo-pstack-mode" / "references" / "agents" / "comment-sicko.md",
}


class SkillContentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.entries = json.loads(MANIFEST.read_text(encoding="utf-8"))["skills"]
        cls.by_name = {entry["name"]: entry for entry in cls.entries}

    def test_manifest_covers_one_source_per_skill(self):
        names = [entry["name"] for entry in self.entries]
        self.assertEqual(len(names), len(set(names)))
        self.assertEqual(set(names), {path.parent.name for path in SKILLS.glob("*/SKILL.md")})
        for entry in self.entries:
            for field in ("description", "when", "example", "limits", "provenance"):
                self.assertTrue(entry[field].strip(), f'{entry["name"]}: {field}')
            self.assertEqual(entry["source"], f'source/skills/{entry["name"]}')
            self.assertTrue((ROOT / entry["source"] / "SKILL.md").is_file())
            for dep in entry["dependencies"]:
                self.assertIn(dep, self.by_name, f'{entry["name"]}: {dep}')

    def test_relative_references_resolve_in_installed_layout(self):
        for file in SKILLS.rglob("*.md"):
            for ref in re.findall(r"\]\(([^)]+)\)", file.read_text(encoding="utf-8")):
                if ref.startswith(("https://", "http://", "#")):
                    continue
                target = (file.parent / ref.split("#", 1)[0]).resolve()
                self.assertTrue(
                    target.is_file() or target in GENERATED_REFERENCES,
                    f"{file.relative_to(ROOT)} -> {ref}",
                )
                if target.is_file() and target.name == "SKILL.md":
                    source_name = file.relative_to(SKILLS).parts[0]
                    if target.parent.name != source_name:
                        self.assertIn(target.parent.name, self.by_name[source_name]["dependencies"])

    def test_bold_skill_mentions_name_bundled_skills(self):
        for file in SKILLS.rglob("*.md"):
            for name in re.findall(r"\*\*([a-z0-9-]+)\*\* skill", file.read_text(encoding="utf-8")):
                self.assertIn(name, self.by_name, f"{file.relative_to(ROOT)} names unbundled skill {name}")

    def test_no_host_secrets_or_unavailable_runtime_assumptions(self):
        forbidden = re.compile(
            r"/Users/|[A-Za-z]:\\Users\\|\bgh pr\b|\btmux\b|"
            r"--dangerously-skip-permissions|--auto-approve|"
            r"\bgpt-\d|\bclaude-(?:opus|fable|sonnet)-\d",
            re.IGNORECASE,
        )
        for file in [*SKILLS.rglob("*.md"), *(ROOT / "source" / "agents").glob("*.md")]:
            content = file.read_text(encoding="utf-8")
            self.assertIsNone(forbidden.search(content), str(file))
            self.assertLess(len(content.splitlines()), 400, str(file))

    def test_atlassian_skill_material_is_excluded(self):
        notice = (ROOT / "THIRD-PARTY-NOTICES.md").read_text(encoding="utf-8")
        self.assertIn("excluded", notice)
        self.assertIn("Atlassian", notice)
        for name in ("twg", "twg-jira", "twg-engineering-work"):
            content = (SKILLS / name / "SKILL.md").read_text(encoding="utf-8")
            self.assertIn("htwg", content)
            self.assertNotIn("/Users/", content)

    def test_agents_are_present_for_generated_copy(self):
        for name in ("poteto-agent.md", "comment-sicko.md"):
            self.assertTrue((ROOT / "source" / "agents" / name).is_file())


if __name__ == "__main__":
    unittest.main()
