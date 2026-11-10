#!/usr/bin/env python3
"""Preview or back up and replace SDD project packages and owned global skills.

Run from sibling source checkouts. Preview never writes. Application source and
active feature documents are not migrated or committed by this tool.
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

VERSION = "4.2.0"
# invariant: global skills for commands removed from the packages; deleted (with backup) on --apply.
RETIRED_SKILLS = ("speckit-sdd-workflow-worktrees",)
# invariant: installed packages must carry these files for the commands to work.
RUNTIME_ASSETS = {"presets": ("scripts/sdd.py",), "extensions": ()}


def discover(projects_root):
    return sorted(path for path in projects_root.iterdir() if path.is_dir() and
                  any((path / ".specify" / kind / "sdd-workflow" / manifest).is_file()
                      for kind, manifest in (("presets", "preset.yml"), ("extensions", "extension.yml"))))


def templates(source_root):
    result = {}
    for name, source in (("preset", "spec-kit-preset-sdd-workflow"),
                         ("extension", "spec-kit-extension-sdd-workflow")):
        directory = source_root / source
        manifest = directory / ("preset.yml" if name == "preset" else "extension.yml")
        if not manifest.is_file():
            raise ValueError("Missing sibling source manifest: " + str(manifest))
        if 'version: "' + VERSION + '"' not in manifest.read_text():
            raise ValueError("Expected reviewed v" + VERSION + " source: " + str(directory))
        for path in sorted((directory / "commands").glob("*.md")):
            header, body = path.read_text().split("---", 2)[1:]
            description = next(line.partition(":")[2].strip() for line in header.splitlines()
                               if line.startswith("description:"))
            skill_name = path.stem.replace(".", "-")
            result[skill_name] = (name, description, body.strip())
    return result


def render_skill(skill_name, kind, description, body):
    # JSON string literals are also YAML strings, so punctuation stays safe.
    return ("---\nname: " + skill_name + "\ndescription: " + json.dumps(description) +
            "\ncompatibility: Requires an installed SDD Workflow v" + VERSION.split(".")[0] +
            " package in the project\nmetadata:\n  source: " + kind + ":sdd-workflow\n  version: " + VERSION + "\n"
            "user-invocable: true\ndisable-model-invocation: false\n---\n\n" + body + "\n")


def package_snapshot(source, destination):
    shutil.copytree(source, destination, ignore=shutil.ignore_patterns(
        ".git", ".github", "tests", "__pycache__", "*.pyc", ".dist", ".superpowers"))


def project_paths(project):
    """Paths the CLI may regenerate; snapshot only agent files owned by SDD."""
    paths = {Path(".specify")}
    for root_name in (".claude/commands", ".github/agents", ".github/prompts", ".opencode/commands",
                      ".gemini/commands", ".cursor/commands", ".windsurf/workflows",
                      ".agents/skills", ".claude/skills", ".codex/skills"):
        root = project / root_name
        if root.exists() or root.is_symlink():
            root.resolve().relative_to(project.resolve())
        if root.is_dir():
            for path in root.glob("speckit*"):
                # Resolve directory aliases once, retaining a leaf symlink itself.
                actual = path.parent.resolve() / path.name
                actual.resolve().relative_to(project.resolve())
                paths.add(actual.relative_to(project.resolve()))
    return sorted(paths)


def copy_path(source, destination):
    destination.parent.mkdir(parents=True, exist_ok=True)
    if source.is_symlink():
        destination.symlink_to(os.readlink(source))
    elif source.is_dir():
        shutil.copytree(source, destination, symlinks=True)
    else:
        shutil.copy2(source, destination)


def remove_path(path):
    if path.is_symlink() or path.is_file():
        path.unlink()
    elif path.exists():
        shutil.rmtree(path)


def run_cli(project, args):
    result = subprocess.run(["specify"] + args, cwd=project, input="y\n", text=True,
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    if result.returncode:
        raise RuntimeError("specify " + " ".join(args) + "\n" + result.stdout[-6000:])


def update_project(project, source_root, backup):
    if not (project / ".specify").is_dir():
        raise ValueError("Not an initialized Spec Kit project: " + str(project))
    specify = project / ".specify"
    if specify.is_symlink() or any(path.is_symlink() for path in specify.rglob("*")):
        raise ValueError("Spec Kit configuration symlinks require a separate migration before replacement: " + str(specify))
    # Internal aliases are common; aliases outside the project must be updated
    # through the explicit global pass rather than implicitly by the CLI.
    for root_name in (".agents/skills", ".claude/skills", ".codex/skills"):
        directory = project / root_name
        if directory.is_symlink():
            try:
                directory.resolve().relative_to(project.resolve())
            except ValueError:
                raise ValueError("Project skills point outside the project; migrate that alias separately: " + str(directory))
    before = project_paths(project)
    for relative in before:
        copy_path(project / relative, backup / relative)
    installed = {}
    settings = {}
    for kind, manifest in (("presets", "preset.yml"), ("extensions", "extension.yml")):
        installed[kind] = (project / ".specify" / kind / "sdd-workflow" / manifest).is_file()
        registry = project / ".specify" / kind / ".registry"
        metadata = json.loads(registry.read_text()).get(kind, {}).get("sdd-workflow", {}) if registry.is_file() else {}
        priority = metadata.get("priority", 10)
        enabled = metadata.get("enabled", True)
        if type(priority) is not int or type(enabled) is not bool:
            raise ValueError("Invalid package priority/enabled metadata in " + str(registry))
        settings[kind] = {"priority": priority, "enabled": enabled}
    try:
        with tempfile.TemporaryDirectory(prefix="sdd-packages-") as temporary:
            staging = Path(temporary)
            for source in ("spec-kit-preset-sdd-workflow", "spec-kit-extension-sdd-workflow"):
                package_snapshot(source_root / source, staging / source)
            if installed["presets"]:
                run_cli(project, ["preset", "remove", "sdd-workflow"])
            if installed["extensions"]:
                run_cli(project, ["extension", "remove", "sdd-workflow", "--force", "--keep-config"])
                run_cli(project, ["extension", "add", str(staging / "spec-kit-extension-sdd-workflow"), "--dev",
                                  "--priority", str(settings["extensions"]["priority"])])
            if installed["presets"]:
                run_cli(project, ["preset", "add", "sdd-workflow", "--dev",
                                  str(staging / "spec-kit-preset-sdd-workflow"),
                                  "--priority", str(settings["presets"]["priority"])])
            for kind, singular in (("extensions", "extension"), ("presets", "preset")):
                if installed[kind] and not settings[kind]["enabled"]:
                    run_cli(project, [singular, "disable", "sdd-workflow"])
        for kind, manifest in (("presets", "preset.yml"), ("extensions", "extension.yml")):
            if installed[kind]:
                directory = project / ".specify" / kind / "sdd-workflow"
                if 'version: "' + VERSION + '"' not in (directory / manifest).read_text():
                    raise RuntimeError("Installed version mismatch: " + str(directory))
                for relative in RUNTIME_ASSETS[kind]:
                    if not (directory / relative).is_file():
                        raise RuntimeError("Missing installed runtime asset: " + relative)
    except Exception:
        for relative in set(before + project_paths(project)):
            remove_path(project / relative)
        for relative in before:
            copy_path(backup / relative, project / relative)
        raise


def update_global(skills_root, owned, backup):
    changed = []
    for name, (kind, description, body) in owned.items():
        target = skills_root / name / "SKILL.md"
        if not target.is_file():
            continue
        backup.mkdir(parents=True, exist_ok=True)
        saved = backup / (name + ".md")
        shutil.copy2(target, saved)
        try:
            target.write_text(render_skill(name, kind, description, body), encoding="utf-8")
        except Exception:
            shutil.copy2(saved, target)
            raise
        changed.append(name)
    return changed


def retire_global(skills_roots, backup):
    """Back up and remove global copies of commands that no longer ship."""
    removed = []
    for root in skills_roots:
        for name in RETIRED_SKILLS:
            entry = root / name
            if not (entry.exists() or entry.is_symlink()):
                continue
            # why: a symlink (e.g. ~/.claude/skills -> ~/.agents/skills) is unlinked; its target is retired via its own root.
            if not entry.is_symlink():
                shutil.copytree(entry, backup / root.name / name, symlinks=True)
            remove_path(entry)
            removed.append(str(entry))
    return removed


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--project", action="append", type=Path, default=[])
    parser.add_argument("--projects-root", type=Path, default=Path.home() / "AIProjects")
    parser.add_argument("--source-root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--skills-root", type=Path, default=Path.home() / ".agents/skills")
    parser.add_argument("--backup-root", type=Path, default=Path.home() / ".sdd-workflow-backups")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--no-global", action="store_true")
    mode.add_argument("--global-only", action="store_true")
    args = parser.parse_args()
    source_root = args.source_root.expanduser().resolve()
    owned = templates(source_root)
    projects = [] if args.global_only else (args.project or discover(args.projects_root.expanduser()))
    projects = sorted({path.expanduser().resolve() for path in projects})
    skills_root = args.skills_root.expanduser()
    global_names = [] if args.no_global else sorted(name for name in owned
                                                  if (skills_root / name / "SKILL.md").is_file())
    print(json.dumps({"mode": "apply" if args.apply else "preview", "version": VERSION,
                      "projects": [str(p) for p in projects], "global_skills": global_names}, indent=2))
    if not args.apply:
        return
    if not shutil.which("specify") and projects:
        raise RuntimeError("Spec Kit CLI is required for project replacement")
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    backup = args.backup_root.expanduser() / stamp
    backup.mkdir(parents=True)
    print("Backup: " + str(backup), flush=True)
    failures = []
    for index, project in enumerate(projects):
        try:
            update_project(project, source_root, backup / (str(index) + "-" + project.name))
            print("UPDATED " + str(project))
        except Exception as error:
            failures.append(str(project))
            print("FAILED " + str(project) + ": " + str(error), file=sys.stderr)
    if failures:
        raise RuntimeError("Some projects failed; global skills were preserved. See diagnostics/backups: " + ", ".join(failures))
    if not args.no_global:
        changed = update_global(skills_root, owned, backup / "global-skills")
        print("UPDATED global skills: " + str(len(changed)))
        roots = [skills_root, Path.home() / ".claude/skills"]
        for path in retire_global(roots, backup / "retired-skills"):
            print("REMOVED retired skill: " + path)
    print("Active feature documents/source were not migrated. Reopen agent sessions after updating.")


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, RuntimeError) as error:
        print(str(error), file=sys.stderr)
        sys.exit(1)
