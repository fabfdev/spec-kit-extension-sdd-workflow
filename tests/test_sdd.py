import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/sdd.py"
spec = importlib.util.spec_from_file_location("sdd", SCRIPT)
sdd = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sdd)


class WorkflowTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        subprocess.run(["git", "init", "-q", str(self.root)], check=True)
        self.directory = self.root / "specs/sample"
        self.directory.mkdir(parents=True)
        (self.root / "feature.py").write_text("value = 1\n")
        (self.root / "check.py").write_text("from feature import value\nassert value == 1\n")
        (self.root / ".gitignore").write_text("__pycache__/\n")
        self.cmd = '"{}" check.py'.format(sys.executable)
        self.prd = '''# Sample
**Size:** small
**Approved:** 2026-11-05 — user: "sim"
- RF-01: Return the required value.
- AC-01 (RF-01): When called, the result shall equal one.
**Final gate:** `{cmd}`

## T1 — Return value
**Status:** pending
**Requirements:** RF-01
**Criteria:** AC-01
**Depends on:** none
**Files:** `feature.py`, `check.py`
**Gate:** `{cmd}`

## Checks
| Criterion | Task | Evidence | Proof command |
|-----------|------|----------|---------------|
| AC-01 | T1 | check.py:2 | `{cmd}` |
'''.format(cmd=self.cmd)
        (self.directory / "prd.md").write_text(self.prd)

    def edit(self, old, new):
        path = self.directory / "prd.md"
        path.write_text(path.read_text().replace(old, new))

    def accept(self):
        result = sdd.scan(self.root, "sample", [])
        sdd.write_json(self.directory / "analysis-review.json", {
            "snapshot": result["snapshot"], "reviewed": result["required_review"], "findings": []})
        sdd.record_analysis(self.root, "sample")
        data = sdd.validate(self.root, "sample")
        sdd.analysis_ready(self.root, "sample", data)
        sdd.write_json(self.directory / "execution.json", sdd.execution_state(self.root, data))

    def complete(self):
        self.accept()
        sdd.prove(self.root, "sample", "T1")
        self.edit("**Status:** pending", "**Status:** done")
        result = sdd.prove(self.root, "sample")
        sdd.write_json(self.directory / "verification.json", {
            "tree": result["tree"], "reviewer": "independent", "reviewer_id": "review-session-1",
            "criteria": [{"id": "AC-01", "result": "pass", "evidence": "check.py:2 asserts value == 1"}],
            "findings": []})

    def test_valid_small_and_cli(self):
        sdd.validate(self.root, "sample")
        result = subprocess.run([sys.executable, str(SCRIPT), "validate", "sample", "--root", str(self.root)],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_unapproved_execution_rejected_but_draft_allowed(self):
        self.edit('**Approved:** 2026-11-05 — user: "sim"', "")
        sdd.validate(self.root, "sample", "tasks")
        with self.assertRaisesRegex(ValueError, "approvals"):
            sdd.validate(self.root, "sample")

    def test_duplicate_requirements_and_criteria_rejected(self):
        self.edit("- RF-01:", "- RF-01: Duplicate.\n- RF-01:")
        with self.assertRaisesRegex(ValueError, "unique RF"):
            sdd.validate(self.root, "sample")

    def test_unknown_requirement_rejected(self):
        self.edit("(RF-01)", "(RF-02)")
        with self.assertRaisesRegex(ValueError, "unknown requirement"):
            sdd.validate(self.root, "sample")

    def test_uncovered_requirement_rejected(self):
        self.edit("**Final gate:**", "- RF-02: Other.\n- AC-02 (RF-02): Result is two.\n**Final gate:**")
        with self.assertRaisesRegex(ValueError, "Uncovered requirement"):
            sdd.validate(self.root, "sample")

    def test_forward_or_cyclic_dependency_rejected(self):
        self.edit("**Depends on:** none", "**Depends on:** T1")
        with self.assertRaisesRegex(ValueError, "cyclic"):
            sdd.validate(self.root, "sample")

    def test_missing_check_rejected(self):
        self.edit("| AC-01 | T1 | check.py:2 | `{}` |".format(self.cmd), "")
        with self.assertRaisesRegex(ValueError, "exactly one row"):
            sdd.validate(self.root, "sample")

    def test_full_work_requires_design_and_tasks(self):
        self.edit("**Size:** small", "**Size:** full")
        with self.assertRaisesRegex(ValueError, "requires techspec"):
            sdd.validate(self.root, "sample")

    def test_path_escape_rejected(self):
        self.edit("`feature.py`", "`../../outside.py`")
        with self.assertRaisesRegex(ValueError, "escapes"):
            sdd.validate(self.root, "sample")

    def test_first_scan_full_then_unchanged(self):
        self.accept()
        self.assertEqual(sdd.scan(self.root, "sample", [])["mode"], "unchanged")

    def test_invalid_cache_requires_full_review_and_can_be_replaced(self):
        (self.directory / "analysis.json").write_text("{invalid cache")
        self.assertEqual(sdd.scan(self.root, "sample", [])["mode"], "full")
        self.accept()
        self.assertEqual(sdd.scan(self.root, "sample", [])["mode"], "unchanged")

    def test_source_change_is_delta_and_invalidates_ready(self):
        self.accept()
        (self.root / "feature.py").write_text("value = 2\n")
        result = sdd.scan(self.root, "sample", [])
        self.assertEqual(result["mode"], "delta")
        self.assertIn("feature.py", result["changed"])
        with self.assertRaisesRegex(ValueError, "stale"):
            sdd.analysis_ready(self.root, "sample", sdd.validate(self.root, "sample"))

    def test_authority_change_forces_full(self):
        self.accept()
        (self.root / "AGENTS.md").write_text("New architecture constraint\n")
        self.assertEqual(sdd.scan(self.root, "sample", [])["mode"], "full")

    def test_nested_authority_change_forces_full(self):
        (self.root / "src").mkdir()
        self.edit("`feature.py`", "`src/feature.py`")
        self.accept()
        (self.root / "src/AGENTS.md").write_text("Use another layer\n")
        self.assertEqual(sdd.scan(self.root, "sample", [])["mode"], "full")

    def test_new_missing_include_is_detected_and_retained(self):
        self.accept()
        result = sdd.scan(self.root, "sample", ["future-contract.json"])
        self.assertIn("future-contract.json", result["changed"])
        pending = sdd.read_json(self.directory / "analysis-inputs.json")
        self.assertIn("future-contract.json", pending["inputs"])

    def test_pending_include_survives_rescan_before_acceptance(self):
        sdd.scan(self.root, "sample", ["future-contract.json"])
        sdd.scan(self.root, "sample", [])
        pending = sdd.read_json(self.directory / "analysis-inputs.json")
        self.assertIn("future-contract.json", pending["inputs"])

    def test_final_proofs_reject_unreviewed_command_changes(self):
        self.accept()
        self.edit(self.cmd, "true")
        self.edit("**Status:** pending", "**Status:** done")
        with self.assertRaisesRegex(ValueError, "plan changed"):
            sdd.prove(self.root, "sample")

    def test_final_close_rejects_unreviewed_plan_changes(self):
        self.complete()
        self.edit(self.cmd, "true")
        with self.assertRaisesRegex(ValueError, "plan changed"):
            sdd.finish(self.root, "sample")

    def test_gate_rejects_changed_architecture_authority(self):
        self.accept()
        (self.root / "AGENTS.md").write_text("New binding rule\n")
        with self.assertRaisesRegex(ValueError, "authority changed"):
            sdd.prove(self.root, "sample", "T1")

    def test_removed_include_is_detected(self):
        (self.root / "contract.json").write_text("{}")
        result = sdd.scan(self.root, "sample", ["contract.json"])
        sdd.write_json(self.directory / "analysis-review.json", {
            "snapshot": result["snapshot"], "reviewed": result["required_review"], "findings": []})
        sdd.record_analysis(self.root, "sample")
        (self.root / "contract.json").unlink()
        self.assertIn("contract.json", sdd.scan(self.root, "sample", [])["changed"])

    def test_stale_snapshot_cannot_be_recorded(self):
        result = sdd.scan(self.root, "sample", [])
        sdd.write_json(self.directory / "analysis-review.json", {
            "snapshot": result["snapshot"], "reviewed": result["required_review"], "findings": []})
        (self.root / "feature.py").write_text("value = 3\n")
        with self.assertRaisesRegex(ValueError, "Stale"):
            sdd.record_analysis(self.root, "sample")

    def test_unreviewed_inputs_rejected(self):
        result = sdd.scan(self.root, "sample", [])
        sdd.write_json(self.directory / "analysis-review.json", {
            "snapshot": result["snapshot"], "reviewed": [], "findings": []})
        with self.assertRaisesRegex(ValueError, "every required input"):
            sdd.record_analysis(self.root, "sample")

    def test_low_findings_block_until_fixed(self):
        with self.assertRaisesRegex(ValueError, "Unresolved"):
            sdd.findings_closed([{"id": "A1", "severity": "LOW", "location": "T1", "summary": "Gap",
                                  "evidence": "Missing edge case", "status": "open"}])

    def test_gate_allows_first_implementation_source_changes(self):
        self.accept()
        (self.root / "feature.py").write_text("value = 1  # implemented\n")
        self.assertEqual(sdd.prove(self.root, "sample", "T1")["task"], "T1")

    def test_gate_rejects_unreviewed_plan_changes(self):
        self.accept()
        self.edit("Return value", "Change delivery")
        with self.assertRaisesRegex(ValueError, "plan changed"):
            sdd.prove(self.root, "sample", "T1")

    def test_handoff_does_not_invalidate_approved_execution_plan(self):
        self.accept()
        with (self.directory / "prd.md").open("a") as stream:
            stream.write("\n## Handoff\nNext: finish T1; no decisions changed.\n")
        self.assertEqual(sdd.prove(self.root, "sample", "T1")["task"], "T1")

    def test_failing_command_blocks_proof(self):
        self.accept()
        self.edit("**Status:** pending", "**Status:** done")
        (self.root / "feature.py").write_text("value = 2\n")
        with self.assertRaisesRegex(ValueError, "Proofs failed"):
            sdd.prove(self.root, "sample")
        self.assertFalse(sdd.read_json(self.directory / "proofs.json")["passed"])

    def test_final_commands_deduplicated_and_review_required(self):
        self.accept()
        self.edit("**Status:** pending", "**Status:** done")
        result = sdd.prove(self.root, "sample")
        self.assertEqual(result["commands"], 1)
        with self.assertRaises(FileNotFoundError):
            sdd.finish(self.root, "sample")

    def test_complete_feature_and_stale_code_rejected(self):
        self.complete()
        self.assertEqual(sdd.finish(self.root, "sample")["status"], "verified")
        (self.root / "feature.py").write_text("value = 3\n")
        with self.assertRaisesRegex(ValueError, "current project contents"):
            sdd.finish(self.root, "sample")

    def test_self_review_rejected(self):
        self.complete()
        review = sdd.read_json(self.directory / "verification.json")
        review["reviewer"] = "self"
        sdd.write_json(self.directory / "verification.json", review)
        with self.assertRaisesRegex(ValueError, "independent reviewer"):
            sdd.finish(self.root, "sample")

    def test_missing_review_criterion_rejected(self):
        self.complete()
        review = sdd.read_json(self.directory / "verification.json")
        review["criteria"] = []
        sdd.write_json(self.directory / "verification.json", review)
        with self.assertRaisesRegex(ValueError, "one evidence row"):
            sdd.finish(self.root, "sample")

    def test_delivery_metadata_does_not_invalidate_proofs(self):
        path = self.root / "docs/kanban/feature-sample.md"
        path.parent.mkdir(parents=True)
        path.write_text("---\nname: sample\nstatus: in-progress\npr:\n---\n")
        self.complete()
        path.write_text("---\nname: sample\nstatus: in-review\npr: https://example.org/pr/1\n---\n")
        self.assertEqual(sdd.finish(self.root, "sample")["status"], "verified")

    def test_ignored_declared_input_invalidates_final_evidence(self):
        with (self.root / ".gitignore").open("a") as stream:
            stream.write("contract.json\n")
        (self.root / "contract.json").write_text('{"version": 1}')
        sdd.scan(self.root, "sample", ["contract.json"])
        self.complete()
        (self.root / "contract.json").write_text('{"version": 2}')
        with self.assertRaisesRegex(ValueError, "current project contents"):
            sdd.finish(self.root, "sample")


if __name__ == "__main__":
    unittest.main()
