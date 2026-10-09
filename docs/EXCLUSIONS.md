# Files excluded from the handoff

The package is assembled from reviewed source files; it is not an export of a home directory.

Each directory rule below excludes every descendant, including files that were not opened during inventory.

| Excluded source | Reason |
|---|---|
| ~/.codex/auth.json | Personal sign-in credentials. |
| ~/.codex/sessions, archived_sessions, history.jsonl and shell_snapshots | Private conversations, prompts and environment history. |
| ~/.codex/memories, attachments, handoffs, automations, log and backups | Personal or customer context and historical configuration. |
| ~/.codex/AGENTS.md and ~/.claude/CLAUDE.md | Personal global instructions explicitly excluded from this package. |
| ~/.cursor/rules/writing-voice.mdc and personal voice hooks | Personal writing instructions. |
| ~/.codex/config.toml, ~/.claude/settings.json, ~/.claude.json and ~/.cursor/mcp.json | Raw files mix user identity, credentials, local paths and settings; only reviewed model values are regenerated. |
| ~/.claude credential files, projects, sessions, debug, history, file-history, paste-cache, session-env, shell-snapshots and backups | Authentication and private runtime data. |
| ~/.cursor/projects and ai-tracking | Private editor activity and runtime state. |
| ~/.aws/credentials, config, sso/cache and cli/cache | Personal profiles, account identifiers and login state. |
| ~/.config/twg and ~/.config/bitbucket | Per-user tokens, OAuth data and service configuration. |
| Shell histories and shell startup files | Credentials, machine-specific aliases and environment values. |
| Original hx scripts and their task ledger | Mac shell/tmux implementation and task history; routing is reimplemented without copying history. |
| Original Mac CLI binaries | Windows tools come from their official distributions. |
| Official local TWG skill files and LICENSE.txt content | Their license prohibits redistribution; this package uses independently written wrapper guidance. |
| Customer ticket bodies, exports, screenshots, logs, fixtures and copied issue notes | Customer content is outside the portable setup. |
| Personal side-project files, resume/evaluation content and imported memories | Unrelated private content. |
| Optional skills not selected for the required core | Kept out of the first handoff; they need separate selection and review. |
| Existing Git history and dirty checkout contents | The new repository contains only this reviewed package. |

A source-machine inventory is outside this release because it describes private local paths.

Every distributable source file is checked again by tools/package_release.py, and the ZIP lists its included files and hashes in FILE-SHA256.json.

Pattern checks can miss credentials or private text; the maintainer must also review changed content before publishing a later release.
