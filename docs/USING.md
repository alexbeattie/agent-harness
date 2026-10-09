# Use the harness

Open a project in Cursor or open PowerShell in the project folder for Codex CLI or Claude Code. The terminal can be standalone or inside another editor.

If you moved the package folder, rerun install.ps1 with your agent selection before using the commands.

## First task in Cursor

Open a new Agent chat and enter `/repo-pstack-mode`.

Use this prompt: `Read this repository's instructions. Explain how its tests run and propose a small improvement. Do not edit or publish anything yet.`

Check that it reads the installed skill and Cursor model roles. Import the generated rule template into User Rules as described in [INSTALL.md](INSTALL.md).

## First task in Codex CLI

Run `harness codex` from the project folder and enter `$repo-pstack-mode`, followed by the same read-only prompt.

The wrapper starts Codex with the generated profile. The plain `codex` command can use different personal defaults.

## First task in Claude Code

Run `harness claude` from the project folder and enter `/agent-harness:repo-pstack-mode`, followed by the same read-only prompt.

This starts an interactive Claude Code session with the generated settings and plugin. Confirm it reads the Claude roles. You can carry out the whole task here without opening Cursor or Codex.

For every agent, review the proposed changes and test results before asking it to implement or publish work. If a required model or review dependency is unavailable, leave that step incomplete and name the setting or dependency. Never accept a silent substitute.

## Terminal handoffs and automatic routing

Create a UTF-8 task.txt outside tracked files. Describe the task, relevant files, constraints and desired result.

Use an explicit host for a read-only explanation:

```powershell
harness dispatch --host claude --task-file task.txt --read-only
harness dispatch --host codex --task-file task.txt --read-only
```

Choose the line for the installed agent. Explicit host selection avoids the Codex classifier. The answer appears in the terminal.

Remove `--read-only` only when you intend to allow edits under the host's normal permission checks. A headless handoff cannot answer an approval prompt for you; continue in `harness claude` or `harness codex` if approval is needed.

`harness dispatch --task-file task.txt` asks Codex to classify the task and can dispatch to either CLI, so install and sign in to both for automatic routing. `--classify-only` inspects the decision without carrying out the task, but still calls Codex and consumes quota.

Use `--quota-used 60` when 60 percent of your Codex allowance is used. The dispatcher does not inspect session histories or account files to estimate quota and does not keep a task ledger. Each agent can retain its own history according to its settings.

Claude's `astra` role routes through Codex. Codex panels containing Claude models and the configured independent Claude review need Claude Code. A selected-agent check does not establish that these cross-provider workflows are ready.


## Jira and Bitbucket

Run `htwg --help` to see the installed TWG commands; a command followed by `--help` runs without approval.

Use `htwg jira workitem get DEMO-123` after replacing DEMO-123 with a ticket you can access.

Inside a checked-out Bitbucket repository, use `htwg bb prs query` to list pull requests.

Use the wrapper for writes too; it displays the full command and asks for a fresh `yes` before running it.

If an agent receives a noninteractive-input error, paste the wrapper's `Rerun yourself` line into a separate PowerShell terminal and review the displayed operation before answering.

Never ask the agent to type the approval, pipe an answer into the wrapper, or bypass it through direct TWG, REST or MCP writes.

After a write, read the saved ticket or pull request again before reporting success.

## AWS

Set `$env:AWS_PROFILE = 'team-dev'` after creating your own named profile with that name.

Run `haws sts get-caller-identity` and confirm the account is the one you intend to use.

Known read operations run without confirmation; writes and operations that are not in the read list ask for a fresh `yes`.

The wrapper refuses commands that print credentials: Secrets Manager and SSM parameter values, STS session and role credentials, ECR login passwords, KMS decrypt, `configure export-credentials` and the `--debug` option. Output that can carry secrets without being a credential read, such as an ECS task definition, asks for approval instead.

Use `haws` for AWS work; the separately installed `aws` program has no wrapper protection.

These prompts are a cooperative workflow, not an operating-system security boundary.

An unrestricted process with the same credentials can bypass them through another CLI, SDK or MCP server.

Ask your AWS and Atlassian administrators for read-only default credentials when you need enforced restrictions.

## Change models or parallel work

Edit config/harness.json in the package folder.

The hosts section contains each program's exact model choices, reasoning settings and role lists.

Keep the role lists separate because Cursor model identifiers can differ from terminal identifiers.

Set max_parallel_agents to the number you want to allow at once.

Rerun install.ps1 with your agent selection, then run check.ps1 with the same selection and -ProbeModels for CLI model checks. Cursor users must refresh their copied User Rules and verify configured models in the UI.

An unavailable model must stop its role and name the setting to change; the package has no fallback-model setting.
