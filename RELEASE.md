# Release 3.0.0

Run from the parent directory containing both source repositories.

## Validation completed

- Preset: 33 tests, including CLI validation, full/delta/unchanged analysis,
  invalid cache recovery, authority changes, pending includes, plan freshness,
  ignored declared inputs, failing proofs and independent review requirements.
- Extension: 45 tests (the shared 33 plus updater/publication checks), including
  rollback, internal aliases, rejecting unsafe configuration aliases, priority
  and enabled state, global skill links and draft release publication.
- Spec Kit CLI 0.9.2.dev0: both packages installed in a disposable project.
  A real v2 source snapshot upgraded to v3 with its internal skills alias,
  application code and active legacy task documents preserved.
- Shared runtime, protocol and runtime tests match byte-for-byte; scripts parse
  with Python 3.8 syntax; both Git diffs pass whitespace checks.
- Independent review identified three runtime and three delivery-tool issues;
  each was corrected with regression coverage. No production benchmark was run;
  token savings remain to be measured on comparable project work.

## Publish

```bash
python3 spec-kit-extension-sdd-workflow/scripts/publish_release.py --apply
```

This checks both repositories before remote mutations, runs tests, verifies clean
default branches and remote ancestry, pushes commits/tags and creates public
v3.0.0 releases. Existing tags must point to the reviewed commit; existing drafts
are explicitly published. Network and GitHub/SSH credentials must be available.

## Update projects and global skills

Preview the discovered projects and global skill copies:

```bash
python3 spec-kit-extension-sdd-workflow/scripts/update_installations.py
```

Then apply from an environment with write access to the targets:

```bash
python3 spec-kit-extension-sdd-workflow/scripts/update_installations.py --apply
```

This uses the reviewed local sibling sources, so installation does not require
the remote releases to be available. It backs up managed files before changes,
retains package priority/disabled state, and restores failed project updates.
Global skills update only after all selected project updates succeed. A project
configuration symlink or agent alias outside the project stops replacement
before its CLI operations. Backups live under `~/.sdd-workflow-backups/`.

Existing source, active feature artifacts, other extensions and unrelated global
skills are preserved. For v1 projects, use import-notion before resuming work.
For active v2 work, use tasks to review/migrate its legacy task files, analyze,
then resume; retain completed work. Reopen agent sessions to load new descriptions.
