#!/usr/bin/env python3
"""SDD structural gates, incremental review snapshots and executable proofs.

Python 3.8+, standard library only. Semantic review remains an agent's job.
Canonical source: spec-kit-preset-sdd-workflow/scripts/sdd.py.
The extension ships a byte-identical copy for standalone maintenance workflows.
"""
import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
from collections import deque
from datetime import datetime, timezone
from pathlib import Path

VERSION = "3.0.0"
OUTPUTS = {"analysis-inputs.json", "analysis-review.json", "analysis.json",
           "proofs.json", "verification.json", "execution.json", "usage.jsonl"}
RF = r"RF-\d+(?:\.\d+)*"
AC = r"AC-\d+"


def fail(message):
    raise ValueError(message)


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def cached_review(path):
    if not path.exists():
        return {}
    try:
        data = read_json(path)
        if (not isinstance(data, dict) or not isinstance(data.get("inputs"), dict) or
                not isinstance(data.get("includes", []), list) or
                any(not isinstance(value, str) for value in data.get("includes", []))):
            return {}
        return data
    except (ValueError, OSError):
        return {}


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    temporary.replace(path)


def digest(data):
    return hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()


def file_hash(path):
    result = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            result.update(chunk)
    return result.hexdigest()


def local_path(root, value):
    path = (root / value).resolve()
    try:
        path.relative_to(root)
    except ValueError:
        fail("Path escapes project root: " + str(value))
    return path


def text(path):
    return path.read_text(encoding="utf-8") if path.is_file() else ""


def field(body, name):
    match = re.search(r"^\*\*" + re.escape(name) + r":\*\*[ \t]*(.+)$", body, re.M)
    return match.group(1).strip() if match else ""


def command(value):
    match = re.fullmatch(r"`([^`\n]+)`", value)
    return match.group(1) if match else ""


def approved(body):
    return bool(re.search(r'^\*\*Approved:\*\*\s*\d{4}-\d{2}-\d{2}\s+[—-]\s+user:\s*".+"\s*$', body, re.M))


def model(root, slug):
    directory = local_path(root, "specs/" + slug)
    prd = text(directory / "prd.md")
    if not prd:
        fail("Missing specs/{}/prd.md; run specify or maintenance scoping first".format(slug))
    tasks_path = directory / "tasks.md"
    tasks_text = text(tasks_path) or prd
    requirements = re.findall(r"^- (" + RF + r"): .+", prd, re.M)
    criteria = re.findall(r"^- (" + AC + r") \((" + RF + r")\): (.+)", prd, re.M)
    tasks = []
    for match in re.finditer(r"^## (T\d+) [—-] ([^\n]+)\n(.*?)(?=^## |\Z)", tasks_text, re.M | re.S):
        task_id, title, body = match.groups()
        tasks.append({"id": task_id, "title": title, "status": field(body, "Status"),
                      "requirements": re.findall(RF, field(body, "Requirements")),
                      "criteria": re.findall(AC, field(body, "Criteria")),
                      "dependencies": re.findall(r"\bT\d+\b", field(body, "Depends on")),
                      "files": re.findall(r"`([^`]+)`", field(body, "Files")),
                      "gate": command(field(body, "Gate")), "body": body})
    checks = []
    checks_section = re.search(r"^## Checks\s*\n(.*?)(?=^## |\Z)", tasks_text, re.M | re.S)
    for line in checks_section.group(1).splitlines() if checks_section else []:
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if cells and re.fullmatch(AC, cells[0]):
            if len(cells) != 4:
                fail("Check rows need exactly four columns; use a named script instead of a shell pipeline")
            checks.append({"id": cells[0], "task": cells[1], "evidence": cells[2].strip("`"),
                           "command": command(cells[3])})
    return {"directory": directory, "prd": prd, "tasks_text": tasks_text,
            "tasks_path": tasks_path if tasks_path.exists() else directory / "prd.md",
            "requirements": requirements, "criteria": criteria, "tasks": tasks, "checks": checks}


def validate(root, slug, stage="execute"):
    data = model(root, slug)
    reqs = data["requirements"]
    criteria = [row[0] for row in data["criteria"]]
    if not reqs or len(reqs) != len(set(reqs)):
        fail("PRD needs unique RF-XX requirement definitions")
    if not criteria or len(criteria) != len(set(criteria)):
        fail("PRD needs unique AC-XX (RF-XX): observable outcome definitions")
    if any(row[1] not in reqs for row in data["criteria"]):
        fail("Acceptance criterion references an unknown requirement")
    if set(reqs) != {row[1] for row in data["criteria"]}:
        fail("Every requirement needs an acceptance criterion")
    size = field(data["prd"], "Size")
    if size not in ("small", "full"):
        fail("PRD Size must be small or full")
    if stage == "spec":
        return data
    if size == "full" and (not (data["directory"] / "techspec.md").is_file() or
                           data["tasks_path"].name != "tasks.md"):
        fail("Full workflow requires techspec.md and consolidated tasks.md")
    tasks = data["tasks"]
    ids = [task["id"] for task in tasks]
    if not tasks or len(ids) != len(set(ids)):
        fail("Need unique ## T1 — Title task sections (migrate legacy N_task.md files first)")
    if size == "small" and len(tasks) > 3:
        fail("More than three atomic tasks: promote to full workflow")
    seen = set()
    for task in tasks:
        if task["status"] not in ("pending", "done"):
            fail(task["id"] + " Status must be pending or done")
        if not task["gate"] or not task["files"]:
            fail(task["id"] + " needs Files and an executable Gate")
        for path in task["files"]:
            local_path(root, path)
        if not task["requirements"] or not set(task["requirements"]) <= set(reqs):
            fail(task["id"] + " has missing or unknown Requirements")
        if not task["criteria"] or not set(task["criteria"]) <= set(criteria):
            fail(task["id"] + " has missing or unknown Criteria")
        if not set(task["dependencies"]) <= seen:
            fail(task["id"] + " depends on a missing, later or cyclic task")
        seen.add(task["id"])
    if {req for task in tasks for req in task["requirements"]} != set(reqs):
        fail("Uncovered requirement: every RF needs a task")
    if {ac for task in tasks for ac in task["criteria"]} != set(criteria):
        fail("Uncovered criterion: every AC needs a task")
    checks = data["checks"]
    if sorted(row["id"] for row in checks) != sorted(criteria):
        fail("Checks needs exactly one row per AC")
    by_id = {task["id"]: task for task in tasks}
    criterion_reqs = {row[0]: row[1] for row in data["criteria"]}
    for row in checks:
        task = by_id.get(row["task"])
        if (not task or row["id"] not in task["criteria"] or
                criterion_reqs[row["id"]] not in task["requirements"] or
                not row["command"] or not row["evidence"] or "<" in row["evidence"]):
            fail("Invalid task, requirement, evidence or proof command for " + row["id"])
    if not command(field(data["tasks_text"], "Final gate")):
        fail("Need **Final gate:** `project build/lint/typecheck/test command`")
    if stage == "execute" and (not approved(data["prd"]) or not approved(data["tasks_text"])):
        fail("Execution requires recorded real user approvals in PRD and tasks (one for inline small work)")
    return data


def review_inputs(root, data, includes):
    paths = {"docs/core/prd.md", "docs/core/sdd.md", "AGENTS.md", "CLAUDE.md",
             ".specify/memory/constitution.md", "package.json", "pyproject.toml"}
    paths.update(str(p.relative_to(root)) for p in data["directory"].glob("*.md"))
    paths.update(includes)
    for task in data["tasks"]:
        paths.update(task["files"])
    for value in list(paths):
        parent = local_path(root, value).parent
        while parent != root:
            paths.update(str((parent / name).relative_to(root)) for name in ("AGENTS.md", "CLAUDE.md"))
            parent = parent.parent
    result = {value: file_hash(local_path(root, value)) if local_path(root, value).is_file() else None
              for value in sorted(paths)}
    result["@runtime"] = file_hash(Path(__file__))
    reference = Path(__file__).resolve().parent.parent / "references/workflow.md"
    result["@protocol"] = file_hash(reference) if reference.exists() else None
    return result


def scan(root, slug, includes, force=False):
    data = validate(root, slug)
    cache_path = data["directory"] / "analysis.json"
    cache = cached_review(cache_path)
    pending_path = data["directory"] / "analysis-inputs.json"
    pending = cached_review(pending_path)
    includes = sorted(set(includes) | set(cache.get("includes", [])) | set(pending.get("includes", [])))
    inputs = review_inputs(root, data, includes)
    previous = cache.get("inputs", {})
    changed = sorted(key for key in set(inputs) | set(previous)
                     if key not in inputs or key not in previous or inputs[key] != previous[key])
    authorities = {"docs/core/prd.md", "docs/core/sdd.md", ".specify/memory/constitution.md",
                   "@runtime", "@protocol", "package.json", "pyproject.toml",
                   str((data["directory"] / "prd.md").relative_to(root))}
    full = force or not cache or any(key in authorities or key.endswith(("AGENTS.md", "CLAUDE.md")) for key in changed)
    mode = "full" if full else "delta" if changed else "unchanged"
    required = sorted(inputs) if full else changed
    snapshot = {"schema": 1, "inputs": inputs, "includes": includes, "digest": digest(inputs),
                "mode": mode, "required_review": required}
    write_json(data["directory"] / "analysis-inputs.json", snapshot)
    return {"mode": mode, "snapshot": snapshot["digest"], "changed": changed,
            "required_review": required, "previous_findings": cache.get("findings", [])}


def findings_closed(findings):
    if not isinstance(findings, list):
        fail("findings must be a list")
    ids = set()
    for finding in findings:
        if not isinstance(finding, dict) or not all(finding.get(key) for key in
                                                   ("id", "severity", "location", "summary", "evidence")):
            fail("Each finding needs id, severity, location, summary and evidence")
        if finding["id"] in ids:
            fail("Finding IDs must be unique")
        ids.add(finding["id"])
        if finding["severity"] not in ("CRITICAL", "HIGH", "MEDIUM", "LOW"):
            fail("Unknown severity")
        if finding.get("status") not in ("fixed", "dismissed") or not finding.get("resolution"):
            fail("Unresolved finding " + finding["id"] + "; fix and verify, or justify dismissal")


def record_analysis(root, slug):
    data = validate(root, slug)
    directory = data["directory"]
    pending = read_json(directory / "analysis-inputs.json")
    review = read_json(directory / "analysis-review.json")
    inputs = review_inputs(root, data, pending["includes"])
    if digest(inputs) != pending["digest"] or review.get("snapshot") != pending["digest"]:
        fail("Stale analysis snapshot: scan again and review changes")
    if not set(pending["required_review"]) <= set(review.get("reviewed", [])):
        fail("Review must account for every required input, including missing/deleted inputs")
    findings_closed(review.get("findings"))
    old_path = directory / "analysis.json"
    old = cached_review(old_path)
    if not {f["id"] for f in old.get("findings", [])} <= {f["id"] for f in review["findings"]}:
        fail("Keep prior findings and their resolutions in the cumulative report")
    write_json(old_path, dict(pending, findings=review["findings"]))
    return {"status": "ready", "snapshot": pending["digest"]}


def analysis_ready(root, slug, data):
    report = read_json(data["directory"] / "analysis.json")
    if report.get("digest") != digest(review_inputs(root, data, report.get("includes", []))):
        fail("Analysis is stale; run analyze and review its delta")
    findings_closed(report.get("findings"))


def plan_digest(data):
    # Progress marks change during Execute; approved task definitions do not.
    def definition(body):
        body = re.sub(r"^## Handoff\s*\n.*?(?=^## |\Z)", "", body, flags=re.M | re.S)
        return re.sub(r"^\*\*Status:\*\*.*$", "", body, flags=re.M).strip()
    return digest({"prd": definition(data["prd"]), "tasks": definition(data["tasks_text"]),
                   "techspec": text(data["directory"] / "techspec.md")})


def execution_state(root, data):
    inputs = review_inputs(root, data, [])
    authorities = {key: value for key, value in inputs.items()
                   if key.startswith("@") or key in ("docs/core/prd.md", "docs/core/sdd.md",
                                                      ".specify/memory/constitution.md") or
                   key.endswith(("AGENTS.md", "CLAUDE.md"))}
    return {"plan": plan_digest(data), "authorities": digest(authorities)}


def execution_ready(root, data):
    execution = read_json(data["directory"] / "execution.json")
    if execution != execution_state(root, data):
        fail("Approved plan changed or authority changed: re-analyze and run ready before continuing")


def tree_digest(root, data):
    result = subprocess.run(["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
                            cwd=root, check=True, stdout=subprocess.PIPE)
    paths = sorted(set(result.stdout.decode().split("\0")) - {""})
    hashes = {}
    for value in paths:
        path = root / value
        parts = Path(value).parts
        if len(parts) == 3 and parts[0] == "specs" and path.name in OUTPUTS:
            continue
        if path.is_symlink():
            hashes[value] = digest({"symlink": os.readlink(path)})
        elif value.startswith("docs/kanban/") and path.is_file():
            # Delivery metadata changes no executable or acceptance input.
            body = re.sub(r"^(status|worktree|tasks_done|tasks_total|pr|updated):.*$", "",
                          text(path), flags=re.M)
            hashes[value] = digest(body)
        else:
            hashes[value] = file_hash(path) if path.is_file() else None
    analysis = read_json(data["directory"] / "analysis.json")
    declared = review_inputs(root, data, analysis.get("includes", []))
    return digest({"files": hashes, "declared_inputs": declared})


def run_commands(root, commands):
    results = []
    for cmd in dict.fromkeys(commands):
        # These are the project's commands from the user-approved task definitions.
        with tempfile.TemporaryFile(mode="w+t") as output:
            completed = subprocess.run(cmd, cwd=root, shell=True, stdout=output, stderr=subprocess.STDOUT)
            output.seek(0)
            tail = deque(output, maxlen=30)
        results.append({"command": cmd, "exit_code": completed.returncode,
                        "output_tail": "".join(tail)[-8000:]})
        if completed.returncode:
            break
    return results


def prove(root, slug, task_id=None):
    data = validate(root, slug)
    execution_ready(root, data)
    if task_id:
        task = next((task for task in data["tasks"] if task["id"] == task_id), None)
        if not task:
            fail("Unknown task " + task_id)
        if any(t["status"] != "done" for t in data["tasks"] if t["id"] in task["dependencies"]):
            fail("Task dependencies are incomplete")
        results = run_commands(root, [task["gate"]])
        if any(row["exit_code"] for row in results):
            fail(json.dumps(results))
        return {"task": task_id, "results": results}
    if any(task["status"] != "done" for task in data["tasks"]):
        fail("All tasks must be done before final proofs")
    before = tree_digest(root, data)
    results = run_commands(root, [row["command"] for row in data["checks"]] +
                           [command(field(data["tasks_text"], "Final gate"))])
    after = tree_digest(root, data)
    passed = before == after and all(row["exit_code"] == 0 for row in results)
    write_json(data["directory"] / "proofs.json", {"tree": after, "passed": passed,
               "results": results, "checked_at": datetime.now(timezone.utc).isoformat()})
    if not passed:
        fail("Proofs failed or commands changed project inputs; inspect proofs.json")
    return {"passed": True, "commands": len(results), "tree": after}


def finish(root, slug):
    data = validate(root, slug)
    execution_ready(root, data)
    proofs = read_json(data["directory"] / "proofs.json")
    review = read_json(data["directory"] / "verification.json")
    current = tree_digest(root, data)
    if not proofs.get("passed") or proofs.get("tree") != current or review.get("tree") != current:
        fail("Final proofs and verification must match current project contents")
    expected_commands = set(row["command"] for row in data["checks"])
    expected_commands.add(command(field(data["tasks_text"], "Final gate")))
    results = proofs.get("results", [])
    if ({row.get("command") for row in results} != expected_commands or
            len(results) != len(expected_commands) or any(row.get("exit_code") != 0 for row in results)):
        fail("Proofs must contain passing results for every distinct declared check and final gate")
    if any(t["status"] != "done" for t in data["tasks"]):
        fail("Incomplete tasks")
    expected = {row[0] for row in data["criteria"]}
    rows = review.get("criteria", [])
    if len(rows) != len(expected) or {row.get("id") for row in rows} != expected:
        fail("Independent verification needs exactly one evidence row per AC")
    if review.get("reviewer") != "independent" or not review.get("reviewer_id"):
        fail("An independent reviewer/session must be identified")
    if any(row.get("result") != "pass" or not row.get("evidence") for row in rows):
        fail("Every AC must have passing, concrete verification evidence")
    findings_closed(review.get("findings"))
    return {"status": "verified", "criteria": len(expected), "tree": current}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["validate", "scan", "record-analysis", "ready", "gate", "prove", "finish"])
    parser.add_argument("slug")
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--stage", choices=["spec", "tasks", "execute"], default="execute")
    parser.add_argument("--include", action="append", default=[])
    parser.add_argument("--full", action="store_true")
    parser.add_argument("--task")
    args = parser.parse_args()
    root = args.root.resolve()
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", args.slug):
        fail("Feature slug must be lowercase kebab-case")
    if args.action == "validate":
        validate(root, args.slug, args.stage)
        result = {"status": "valid", "stage": args.stage}
    elif args.action == "scan":
        result = scan(root, args.slug, args.include, args.full)
    elif args.action == "record-analysis":
        result = record_analysis(root, args.slug)
    elif args.action == "ready":
        data = validate(root, args.slug)
        analysis_ready(root, args.slug, data)
        write_json(data["directory"] / "execution.json", execution_state(root, data))
        result = {"status": "ready"}
    elif args.action == "gate":
        if not args.task:
            fail("gate requires --task T1")
        result = prove(root, args.slug, args.task)
    elif args.action == "prove":
        result = prove(root, args.slug)
    else:
        result = finish(root, args.slug)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, KeyError, TypeError, subprocess.CalledProcessError) as error:
        print("SDD gate: " + str(error), file=sys.stderr)
        sys.exit(1)
