import importlib.util
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/update_installations.py"
spec = importlib.util.spec_from_file_location("updater", SCRIPT)
updater = importlib.util.module_from_spec(spec)
spec.loader.exec_module(updater)


class InstallationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name).resolve()

    def test_discover_only_installed_sdd_projects(self):
        installed = self.base / "app/.specify/presets/sdd-workflow"
        installed.mkdir(parents=True)
        (installed / "preset.yml").write_text("preset: old")
        (self.base / "other/.specify").mkdir(parents=True)
        self.assertEqual(updater.discover(self.base), [self.base / "app"])

    def test_internal_skill_directory_alias_is_deduplicated(self):
        project = self.base / "app"
        (project / ".specify").mkdir(parents=True)
        real = project / ".claude/skills/speckit-implement"
        real.mkdir(parents=True)
        (real / "SKILL.md").write_text("old")
        (project / ".agents").mkdir()
        (project / ".agents/skills").symlink_to("../.claude/skills")
        self.assertEqual(updater.project_paths(project),
                         [Path(".claude/skills/speckit-implement"), Path(".specify")])

    def test_external_alias_rejected_before_any_write(self):
        project = self.base / "app"
        (project / ".specify").mkdir(parents=True)
        (project / ".agents").mkdir()
        (project / ".agents/skills").symlink_to(self.base / "external")
        with self.assertRaisesRegex(ValueError, "outside the project"):
            updater.update_project(project, self.base, self.base / "backup")
        self.assertFalse((self.base / "backup").exists())

    def test_specify_aliases_rejected_before_backup_or_cli(self):
        for target in (self.base / "outside", self.base / "app/config/spec-kit"):
            project = self.base / "app"
            target.mkdir(parents=True, exist_ok=True)
            project.mkdir(exist_ok=True)
            (project / ".specify").symlink_to(target)
            with patch.object(updater, "run_cli") as cli:
                with self.assertRaisesRegex(ValueError, "configuration symlinks"):
                    updater.update_project(project, self.base, self.base / "backup")
                cli.assert_not_called()
            (project / ".specify").unlink()

    def test_empty_external_command_alias_rejected(self):
        project = self.base / "app"
        (project / ".specify").mkdir(parents=True)
        (project / ".claude").mkdir()
        (self.base / "external").mkdir()
        (project / ".claude/commands").symlink_to(self.base / "external")
        with self.assertRaises(ValueError):
            updater.update_project(project, self.base, self.base / "backup")
        self.assertFalse((self.base / "backup").exists())

    def test_priority_and_disabled_state_are_retained(self):
        project = self.base / "app"
        package = project / ".specify/presets/sdd-workflow"
        package.mkdir(parents=True)
        (package / "preset.yml").write_text('version: "2.0.0"')
        (package.parent / ".registry").write_text(
            '{"presets":{"sdd-workflow":{"priority":5,"enabled":false}}}')
        source = self.base / "sources"
        for name in ("spec-kit-preset-sdd-workflow", "spec-kit-extension-sdd-workflow"):
            (source / name).mkdir(parents=True)
        calls = []

        def install(_project, args):
            calls.append(args)
            if args[:2] == ["preset", "add"]:
                (package / "preset.yml").write_text('version: "4.2.0"')
                for path in ("scripts/sdd.py",):
                    target = package / path
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_text("asset")

        with patch.object(updater, "run_cli", side_effect=install):
            updater.update_project(project, source, self.base / "backup")
        add = next(call for call in calls if call[:2] == ["preset", "add"])
        self.assertEqual(add[-2:], ["--priority", "5"])
        self.assertIn(["preset", "disable", "sdd-workflow"], calls)

    def test_failed_cli_update_restores_package_and_generated_skill(self):
        project = self.base / "app"
        package = project / ".specify/presets/sdd-workflow"
        package.mkdir(parents=True)
        (package / "preset.yml").write_text('version: "2.0.0"')
        skill = project / ".claude/skills/speckit-implement/SKILL.md"
        skill.parent.mkdir(parents=True)
        skill.write_text("custom old content")
        application = project / "source.py"
        application.write_text("untouched")
        source = self.base / "sources"
        for name in ("spec-kit-preset-sdd-workflow", "spec-kit-extension-sdd-workflow"):
            (source / name).mkdir(parents=True)

        def fail_after_mutation(*args):
            skill.write_text("partial update")
            (package / "preset.yml").write_text("partial")
            raise RuntimeError("simulated CLI failure")

        with patch.object(updater, "run_cli", side_effect=fail_after_mutation):
            with self.assertRaisesRegex(RuntimeError, "simulated"):
                updater.update_project(project, source, self.base / "backup")
        self.assertEqual(skill.read_text(), "custom old content")
        self.assertIn("2.0.0", (package / "preset.yml").read_text())
        self.assertEqual(application.read_text(), "untouched")

    def test_global_update_preserves_symlinks_and_unrelated_skills(self):
        skills = self.base / "skills"
        real = self.base / "shared/speckit-implement"
        real.mkdir(parents=True)
        (real / "SKILL.md").write_text("old")
        skills.mkdir()
        (skills / "speckit-implement").symlink_to(real)
        unrelated = skills / "speckit-constitution/SKILL.md"
        unrelated.parent.mkdir()
        unrelated.write_text("keep")
        owned = {"speckit-implement": ("preset", "Continuous execution", "new body")}
        updated = updater.update_global(skills, owned, self.base / "backup")
        self.assertEqual(updated, ["speckit-implement"])
        self.assertTrue((skills / "speckit-implement").is_symlink())
        self.assertIn("new body", (real / "SKILL.md").read_text())
        self.assertEqual(unrelated.read_text(), "keep")
        self.assertEqual((self.base / "backup/speckit-implement.md").read_text(), "old")

    def test_retired_skill_backed_up_and_symlink_alias_unlinked(self):
        agents = self.base / "agents"
        real = agents / "speckit-sdd-workflow-worktrees"
        real.mkdir(parents=True)
        (real / "SKILL.md").write_text("old")
        claude = self.base / "claude"
        claude.mkdir()
        (claude / "speckit-sdd-workflow-worktrees").symlink_to(real)
        keep = agents / "speckit-implement"
        keep.mkdir()
        removed = updater.retire_global([claude, agents], self.base / "backup")
        self.assertEqual(len(removed), 2)
        self.assertFalse((claude / "speckit-sdd-workflow-worktrees").is_symlink())
        self.assertFalse(real.exists())
        self.assertTrue(keep.exists())
        self.assertEqual((self.base / "backup/agents/speckit-sdd-workflow-worktrees/SKILL.md").read_text(), "old")

    def test_global_skill_yaml_quotes_punctuation(self):
        content = updater.render_skill("speckit-plan", "preset", 'Plan: "approved"', "body")
        self.assertIn('description: "Plan: \\"approved\\""', content)


if __name__ == "__main__":
    unittest.main()
