import importlib.util
import json
import io
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from contextlib import redirect_stdout

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/publish_release.py"
spec = importlib.util.spec_from_file_location("publisher", SCRIPT)
publisher = importlib.util.module_from_spec(spec)
spec.loader.exec_module(publisher)


class PublicationTests(unittest.TestCase):
    def publish(self, release, fail_second_branch=False):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for name, manifest in zip(publisher.REPOSITORIES, ("preset.yml", "extension.yml")):
                repository = root / name
                repository.mkdir()
                (repository / manifest).write_text('version: "3.0.0"')
            calls = []

            def run(args, repository, capture=False):
                calls.append(args)
                if args[:3] == ["git", "rev-parse", "HEAD"] or args[:3] == ["git", "rev-list", "-n"]:
                    return "abc\n"
                if args[:3] == ["git", "status", "--short"]:
                    return ""
                if args[:3] == ["git", "branch", "--show-current"]:
                    return "other" if fail_second_branch and "extension" in repository.name else "main"
                if args[:2] == ["gh", "api"]:
                    return '{"default_branch":"main"}'
                if args[:3] == ["gh", "release", "list"]:
                    return json.dumps([release] if release else [])
                return ""

            with redirect_stdout(io.StringIO()), patch.object(publisher, "run", side_effect=run), patch.object(
                    publisher.subprocess, "run", return_value=subprocess.CompletedProcess([], 0)), patch(
                    "sys.argv", [str(SCRIPT), "--apply", "--source-root", str(root)]):
                if fail_second_branch:
                    with self.assertRaisesRegex(RuntimeError, "default branch"):
                        publisher.main()
                else:
                    publisher.main()
            return calls

    def test_existing_draft_is_published(self):
        calls = self.publish({"tagName": "v3.0.0", "isDraft": True, "isPrerelease": False})
        edits = [call for call in calls if call[:3] == ["gh", "release", "edit"]]
        self.assertEqual(len(edits), 2)
        self.assertTrue(all("--draft=false" in call for call in edits))

    def test_existing_public_release_is_not_recreated(self):
        calls = self.publish({"tagName": "v3.0.0", "isDraft": False, "isPrerelease": False})
        self.assertFalse(any(call[:3] in (["gh", "release", "edit"], ["gh", "release", "create"])
                             for call in calls))

    def test_both_preflights_finish_before_any_push(self):
        calls = self.publish(None, fail_second_branch=True)
        self.assertFalse(any(call[:2] == ["git", "push"] for call in calls))


if __name__ == "__main__":
    unittest.main()
