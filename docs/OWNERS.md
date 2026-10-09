# Maintain the package

The repository maintainer owns updates to the shared source.

Keep the package in one Git repository and send teammates a reviewed release or repository revision.

Do not use an installed copy under a home directory as the source for a release.

## Edit a skill

Edit source/skills/<name>/SKILL.md and its supporting files.

Update that skill's entry in config/skills.json when its purpose, example or dependencies change.

Keep every linked dependency inside this repository and remove personal or customer-specific examples.

Run `python tools/generate_docs.py` to regenerate the skill reference and configuration explanation.

Run the tests listed in VERIFICATION.md. Test installation in a disposable account before updating an installed copy.

If the installer reports a conflict, compare the installed file with the source before moving or deleting anything.

Move intended local edits back into the source, then resolve the reported installed-file conflict and rerun the installer.

Do not replace an entire personal settings file to resolve a conflict.

A removed source file remains listed as retained_obsolete until its installed copies are deliberately reconciled.

Review those paths before removing them; the installer preserves them because an older skill may still load from that location.

## Update pstack guidance

Read THIRD-PARTY-NOTICES.md and the source provenance in config/skills.json before importing an upstream change.

The inspected pstack versions were 0.9.78 for the Codex-facing port, 0.15.13 in Cursor and 0.9.15 in Claude's installation.

The port's recorded upstream is [michael-denyer/pstack-claude](https://github.com/michael-denyer/pstack-claude).

Compare only the workflows this package uses, in a separate checkout; the adapted files here are not a verbatim upstream release.

Record the upstream version or revision in the affected config/skills.json provenance entries when you adopt an update.

Preserve the active repository delivery rules, the exact model mapping, the follow-up versus interruption rule, and the external write confirmations.

Do not reintroduce a dependency on a separately installed pstack marketplace plugin.

Review upstream licenses before copying files; the local official TWG skills were excluded because their license prohibits redistribution.

This package's TWG guidance is independently written around the command wrapper.

## Add a person

Give them the reviewed repository or ZIP and the installation guide.

Have them use their own Windows account and sign in to each selected agent. Atlassian and AWS sign-ins are needed only when they use those services.

Grant company service access through the normal administrators; do not send a copy of another person's configuration or token.

Run the Windows acceptance steps with them, including their account's model availability and the write-denial checks.

## Build a release

Run `python -m unittest discover -s tests -v` and the PowerShell checks documented in VERIFICATION.md.

Run `python tools/generate_docs.py` and `python tools/package_release.py --check`.

Review all changed source and documentation for credentials, personal data and customer content; a pattern scan cannot prove their absence.

Run `python tools/package_release.py` to create the ZIP and its SHA-256 checksum under dist.

The ZIP contains FILE-SHA256.json so recipients can check the file contents.

Native Windows acceptance is a separate required check before describing a release as tested on Windows.
