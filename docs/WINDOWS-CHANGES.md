# Changes for Windows

The task dispatcher uses Python subprocess argument lists and standard input instead of tmux panes and shell command interpolation.

Quota usage is an explicit input; the dispatcher does not inspect another person's Codex sessions or authentication files.

Python's standard library replaces shell utilities in the shared runtime.

The PowerShell entrypoints locate files relative to the package and the current user's home directory.

Installed skills are real files, with no symlink or administrator-mode requirement.

Cursor and Codex share the documented .agents/skills discovery location.

Claude receives a separate generated plugin under .agent-harness, outside Cursor's automatic compatibility scan, to avoid duplicate skill discovery.

The installer tracks the generated files by hash and refuses conflicting local edits.

The source repository keeps text normalized through .gitattributes; PowerShell files use CRLF in Git checkouts.

Mac binaries, shell startup files, hooks and machine-specific MCP bridges are excluded.

The official Windows programs are installed separately and each person signs in with their own accounts.

No WSL installation is required by this package.
