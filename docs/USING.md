# Use the team setup

Open a repository in Cursor, then choose Terminal > New Terminal and select PowerShell.

If you moved the package folder, rerun install.ps1 before using these commands.

## First task in Cursor

Open Cursor's agent chat and enter `/repo-pstack-mode`.

Ask: `Read this repository's instructions. Explain how its tests run and propose a small improvement. Do not edit or publish anything yet.`

The agent should identify the repository rules, describe the tests and use the configured role models when it delegates.

If a model is unavailable, stop and follow the error's configuration setting; do not accept a silent substitute.

## First task in Codex

Run `harness codex` in the repository's terminal.

Enter `$repo-pstack-mode`, then use the same first-task prompt.

This starts Codex with the generated team profile; the plain `codex` command can use different personal defaults.

Review the proposed changes and test results before asking it to implement or publish work.

## Hand work to Claude

Create a UTF-8 file named task.txt outside the repository's tracked files and describe the task, the relevant files, constraints and desired result.

Run `harness dispatch --host claude --task-file task.txt --read-only` for a review or explanation.

The answer appears in the terminal so you can return it to Codex with your next instruction.

Remove `--read-only` only when you intend to allow repository edits under Claude's normal permission checks.

A noninteractive handoff cannot answer a permission prompt on your behalf; if it stops for approval, continue in `harness claude`.

For automatic routing, run `harness dispatch --task-file task.txt`.

To inspect the decision without running the task, add `--classify-only`; this still calls Codex to classify the text and consumes account quota.

Use `--quota-used 60` when 60 percent of your Codex allowance is used.

The dispatcher does not read session histories or account files to estimate quota, and it does not keep its own task ledger.

The underlying agent applications can retain their own history according to their settings.

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

Run install.ps1 again to regenerate the installed files, then run check.ps1 -ProbeModels and verify Cursor's configured models in its UI.

An unavailable model must stop its role and name the setting to change; the package has no fallback-model setting.
