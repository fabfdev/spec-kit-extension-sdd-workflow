#!/usr/bin/env python3
"""Preview or publish the reviewed v3.0.0 release of both sibling repositories."""
import argparse
import json
import subprocess
from pathlib import Path

VERSION = "3.0.0"
REPOSITORIES = ("spec-kit-preset-sdd-workflow", "spec-kit-extension-sdd-workflow")


def run(args, root, capture=False):
    return subprocess.run(args, cwd=root, check=True, text=True,
                          stdout=subprocess.PIPE if capture else None).stdout


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--source-root", type=Path, default=Path(__file__).resolve().parents[2])
    args = parser.parse_args()
    root = args.source_root.resolve()
    for name in REPOSITORIES:
        repository = root / name
        sha = run(["git", "rev-parse", "HEAD"], repository, True).strip()
        print(name + " v" + VERSION + " at " + sha, flush=True)
    if not args.apply:
        print("Preview only. --apply tests, checks clean/default branches, fetches, pushes and creates releases.")
        return
    prepared = []
    # Validate both repositories before the first remote mutation.
    for name in REPOSITORIES:
        repository = root / name
        manifest_name = "preset.yml" if "preset" in name else "extension.yml"
        if 'version: "' + VERSION + '"' not in (repository / manifest_name).read_text():
            raise RuntimeError("Unexpected manifest version in " + name)
        if run(["git", "status", "--short"], repository, True).strip():
            raise RuntimeError("Commit or preserve local changes before publishing " + name)
        run(["python3", "-m", "unittest", "discover", "-s", "tests"], repository)
        remote = "fabfdev/" + name
        metadata = json.loads(run(["gh", "api", "repos/" + remote], repository, True))
        branch = metadata["default_branch"]
        if run(["git", "branch", "--show-current"], repository, True).strip() != branch:
            raise RuntimeError("Release must be prepared on the default branch: " + name)
        run(["git", "fetch", "origin", branch, "--tags"], repository)
        run(["git", "merge-base", "--is-ancestor", "origin/" + branch, "HEAD"], repository)
        sha = run(["git", "rev-parse", "HEAD"], repository, True).strip()
        tag = "v" + VERSION
        existing = subprocess.run(["git", "rev-parse", "--verify", "refs/tags/" + tag], cwd=repository,
                                  text=True, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        if existing.returncode == 0:
            tagged_sha = run(["git", "rev-list", "-n", "1", tag], repository, True).strip()
            if tagged_sha != sha:
                raise RuntimeError("Existing release tag points at different work: " + name)
        releases = json.loads(run(["gh", "release", "list", "--repo", remote,
                                   "--limit", "100", "--json", "tagName,isDraft,isPrerelease"], repository, True))
        release = next((release for release in releases if release["tagName"] == tag), None)
        prepared.append((repository, remote, branch, sha, tag, existing.returncode == 0,
                         release))
    for repository, remote, branch, sha, tag, tag_exists, release in prepared:
        run(["git", "push", "origin", branch], repository)
        if not tag_exists:
            run(["git", "tag", "-a", tag, "-m", "SDD Workflow " + tag, sha], repository)
        run(["git", "push", "origin", tag], repository)
        if release is None:
            run(["gh", "release", "create", tag, "--repo", remote, "--verify-tag",
                 "--title", "SDD Workflow " + tag, "--notes-file", "CHANGELOG.md"], repository)
        elif release.get("isDraft") or release.get("isPrerelease"):
            run(["gh", "release", "edit", tag, "--repo", remote,
                 "--draft=false", "--prerelease=false", "--verify-tag"], repository)
        print("PUBLISHED https://github.com/" + remote + "/releases/tag/" + tag, flush=True)


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, RuntimeError, subprocess.CalledProcessError) as error:
        raise SystemExit(str(error))
