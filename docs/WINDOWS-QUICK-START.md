# Windows quick start

Choose Cursor, Codex CLI, Claude Code, or install all three. You can use a standalone PowerShell terminal or the terminal in your editor.

## Download and extract

[Download the Windows test ZIP](https://github.com/alexbeattie/agent-harness/releases/download/v1.0.1-windows-test.1/agent-harness-1.0.1.zip) from the public [agent-harness repository](https://github.com/alexbeattie/agent-harness).

Extract it to a permanent location such as `C:\Work\agent-harness`. Open PowerShell in the extracted folder containing `install.ps1`.

## Install your chosen agents

Review the scripts, then run this command to prepare all three:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\install.ps1
```

For an individual setup, use the matching command instead:

| Agent | Install command |
|---|---|
| Cursor | `powershell -NoProfile -ExecutionPolicy Bypass -File .\install.ps1 -Agents cursor` |
| Codex CLI | `powershell -NoProfile -ExecutionPolicy Bypass -File .\install.ps1 -Agents codex` |
| Claude Code | `powershell -NoProfile -ExecutionPolicy Bypass -File .\install.ps1 -Agents claude` |

Cursor users must also install the [Cursor desktop editor](https://cursor.com/downloads). The script generates its skills and rule template. It installs the selected command-line agents when they are missing.

The execution-policy override applies to this process. If company policy blocks it, ask IT to approve installation.

Close and reopen the terminal application after installation. If you use an editor's terminal, quit and restart the editor too so it picks up the updated PATH.

## Sign in and start

Sign in with your own accounts for the agents you selected. Follow [INSTALL.md](https://github.com/alexbeattie/agent-harness/blob/main/docs/INSTALL.md) for account setup, Cursor's User Rules import and optional AWS/Atlassian access.

| Agent | Start in your project | Load the workflow |
|---|---|---|
| Cursor | Open the project and a new Agent chat | `/repo-pstack-mode` |
| Codex CLI | `harness codex` | `$repo-pstack-mode` |
| Claude Code | `harness claude` | `/agent-harness:repo-pstack-mode` |

## Check your setup

From the package folder, check all three:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\check.ps1
```

For one agent, append the matching selector, such as `-Agents claude`. Selection applies to each command; a later command with no selector checks all three again.

Automatic checks report missing files, commands and selected CLI sign-ins. Cursor discovery and model access remain separate manual checks. Add `-ProbeModels` only when you want authenticated model probes; these consume quota or can incur charges.

Follow [WINDOWS-TEST.md](https://github.com/alexbeattie/agent-harness/blob/main/docs/WINDOWS-TEST.md) for the agents you selected. Save your PC results privately. Native Windows acceptance of this release remains pending.

## Ask an agent to help with setup

Open the extracted package folder in your chosen coding agent and paste this prompt. There is no need to paste the contents of install.ps1.

```text
Read docs/INSTALL.md in this folder. Help me install this harness on Windows
for Cursor, Codex CLI and Claude Code. Use the default all-agent setup.
Review the scripts, preserve existing personal settings, and run the install
and check commands from this folder. Tell me which sign-ins and manual checks
I need to complete. Do not collect my credentials or claim a check passed
unless it ran. Ask before any paid model probes or service writes.
```

For a single agent, replace the second line with `for Codex CLI only`, `for Claude Code only` or `for Cursor only`; use its `-Agents` selector on install and check.
