# Test under a new Windows account

Run this checklist on the Windows 11 PC before accepting the package for a user account.

Record the package revision, Windows version, tool versions, results and any screenshots in a private test record outside this repository.

Do not copy configuration from an existing Windows or Mac user.

## Create the test environment

Create a new standard Windows user through Settings > Accounts > Other users, then sign out and sign in as that user.

Install or open Cursor for that user.

Extract the reviewed package into a folder whose name contains a space, such as C:\Users\<your-user>\Work\Team Setup\agent-harness.

Follow INSTALL.md from the beginning, including each person's own sign-in.

Keep AWS on a development account with a named profile; do not use production for this test.

## Check installation and retries

Run install.ps1 and save its output.

Quit Cursor completely, start it again, then run check.ps1 and record its execution policy and command resolution lines.

Run install.ps1 a second time and confirm it reports no changes to generated files and does not repeat successful tool installations.

In a plain PowerShell terminal started without an execution-policy override, run `haws --help` and `htwg --help`; confirm they run rather than reporting that scripts are disabled, and record the policy check.ps1 reported.

Confirm any pre-existing personal settings outside the generated file list are unchanged.

In the disposable account only, append a test line to .agents\skills\repo-pstack-mode\SKILL.md under your home folder.

Rerun install.ps1 and confirm it stops with a conflict instead of erasing the edit.

Move that one edited generated file to a private backup, then rerun install.ps1 to recreate it from the package.

## Check Cursor

Open a scratch repository in Cursor and start a new agent chat.

Type `/repo-pstack-mode` and confirm the skill is selectable.

Ask the agent to identify the skill file and its Cursor model mapping without editing anything.

Compare the reported swarm-worker model with hosts.cursor.roles in config/harness.json.

Ask for a read-only explanation using the how workflow and confirm each requested role either uses the configured model or stops with an explicit unavailable-model error.

A model name displayed in a rule is not enough; record the actual model identity where Cursor exposes it.

Check whether Cursor lists the agent-harness rule from the .cursor\rules folder under your home folder. If Cursor only loads rules from the open project, record that gap; the roles then come from the installed skill alone.

## Check Codex and the Claude handoff

Run `harness codex` in the scratch repository and invoke `$repo-pstack-mode`.

Ask for the same read-only explanation and compare the model choices with hosts.codex.roles.

Create a small UTF-8 task.txt outside tracked source containing: `Explain the files in this scratch repository. Do not edit files or contact external services.`

Run `harness dispatch --task-file task.txt --classify-only` and confirm it prints a valid decision without carrying out the task.

Run `harness dispatch --host claude --task-file task.txt --read-only` and confirm the answer returns to the terminal without repository edits.

Return that answer to Codex with a follow-up instruction and confirm it can continue the task.

Run `harness dispatch --host claude --task-file task.txt --read-only > answer.txt` with a task that asks for a reply containing an arrow and a check mark; open answer.txt and confirm both characters arrived rather than an encoding error.

From inside a Codex session, ask it to run the same dispatch command and relay the answer; confirm the text arrives intact.

Run check.ps1 -ProbeModels and record unsupported models or reasoning/speed settings.

Do not replace an unavailable model silently; change the named setting deliberately and rerun installation and the affected check.

## Check service reads and write denial

Run `htwg jira workitem get <a-ticket-you-can-read>` with a real ticket you are authorized to read.

Run `twg doctor --basic` and confirm encrypted storage with the root key in the Windows OS vault.

In an authorized Bitbucket checkout, run `htwg bb prs query`.

Set your development AWS_PROFILE and run `haws sts get-caller-identity`; confirm the returned account and identity.

Run `haws ec2 describe-instances --filters Name=instance-state-name,Values=running` without quoting the comma list and confirm the AWS CLI accepts the filter; a space in place of the comma is an invalid filter.

Run `haws ec2 create-tags --resources i-00000000000000000 --tags Key=HarnessTest,Value=Denied` and answer `no`.

Confirm it prints the exact intended operation, refuses execution and returns a failure code.

Do not answer yes to this example; the identifier is deliberately made up.

Confirm redirected input is refused with `cmd /c "echo yes | powershell -NoProfile -ExecutionPolicy Bypass -File <package>\bin\haws.ps1 ec2 create-tags --resources i-00000000000000000 --tags Key=HarnessTest,Value=Denied"`.

Piping inside PowerShell (`'yes' | haws ...`) feeds the script's pipeline rather than the child's standard input, so it shows a live prompt and does not test the refusal.

Run the same create-tags command from the terminal tool inside Claude Code; record which shell it used, whether haws resolved there and that the refusal arrived.

Run `python -m unittest discover -s tests -v`; the fake-process tests exercise approved writes without calling AWS or Atlassian.

From Cursor, Codex and Claude Code, ask each agent to propose the same test write and confirm it uses haws, waits for a human and does not bypass the denial.

Repeat the proposal check for a TWG write; cancel at the prompt and verify the target ticket or pull request remains unchanged.

The raw aws and twg programs and any write-capable MCP servers are outside the wrapper's control; confirm administrators understand this boundary.

## Record acceptance

Record Cursor skill discovery, both terminal paths, model identities, service reads, denied writes, redirected-input denial, repeated installation and conflict preservation separately.

Keep any unchecked item open and name the person who will complete it.

Mac unit tests and PowerShell parser checks do not substitute for this Windows record.
