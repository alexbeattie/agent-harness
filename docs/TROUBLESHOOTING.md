# Fix common failures

## PowerShell cannot run install.ps1

Confirm the files came from the reviewed package, then follow the download-unblocking step in INSTALL.md.

Use the process-scoped command shown there; do not change machine-wide execution policy.

If company policy still blocks execution, ask IT for approval.

## PowerShell says running scripts is disabled

install.ps1 and check.ps1 bypass the policy for their own process; the harness, hx, haws and htwg wrappers do not.

Run check.ps1; it names the policy a normal terminal applies.

With IT approval, run `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`, keep the package files unblocked, then rerun check.ps1.

## A command is not found

Quit Cursor completely and start it again; a new terminal tab inside a running Cursor keeps the old PATH.

Rerun check.ps1 from the package folder so it can name the missing tool.

Keep the package in its installed location; if you moved it, rerun install.ps1 to update the wrapper path.

A Microsoft Store Python placeholder is not a working Python installation; use the Python installation selected by install.ps1.

## The installer reports a conflict

It found an existing file whose contents do not match the last generated version.

Compare that file with the source before changing it.

Save local edits elsewhere, move the conflicting generated file out of the way, then rerun installation.

Never delete an entire .cursor, .codex, .claude or .agents folder to fix one conflict.

## Cursor does not show a skill

Open a new agent chat after running install.ps1.

Check that the skill's SKILL.md exists under .agents\skills in the current user's home folder.

Check Cursor's skill settings and confirm the skill is enabled.

Run check.ps1, then use the manual discovery prompt in WINDOWS-TEST.md.

File presence alone does not prove that the editor loaded it.

## A model or reasoning setting is rejected

Read the host and configuration key named in the error.

Compare it with your account's available models in that host.

Edit that setting in config/harness.json, rerun install.ps1 and repeat the failed check.

Do not rename all hosts' models together; their model identifiers differ.

The package deliberately does not substitute another model.

## Claude or Codex is installed but not signed in

Run the program directly and complete its own sign-in flow, then retry the configured harness command.

Do not copy another person's login file.

## A headless handoff cannot get permission

The dispatcher cannot answer the host's approval prompt for you.

Continue the task in harness claude or harness codex, review the requested action and decide in that interactive session.

## A write says it needs an interactive terminal

Open a separate PowerShell terminal and review the two lines the wrapper displayed: `Will run` shows the resolved program with the injected AWS profile, and `Rerun yourself` shows the haws or htwg command to paste.

Paste the `Rerun yourself` line, review the operation it displays and type yes only if you intend that exact write.

Never paste the `Will run` line; it calls the raw program without the wrapper.

Do not pipe an answer, add an approval bypass, or run the raw service command to avoid the check.

## AWS_PROFILE is missing or AWS reports the wrong account

Set AWS_PROFILE to your own named development profile and run haws sts get-caller-identity.

If SSO expired, run aws sso login --profile followed by your profile name.

Ask your AWS administrator if the profile has the wrong account or permissions.

## Jira or Bitbucket access fails

Run twg login for your own Atlassian account; use twg setup bitbucket for the separate Bitbucket token setup.

Ask the service administrator to verify site, repository and token scopes.

Never put a token in a command argument, a screenshot or a chat message.

## an optional context or assistant service is unavailable

Leave its template disabled until the service owner supplies the endpoint, token and supported transport.

The package does not treat missing optional MCP access as proof that a service or ticket does not exist.

## check.ps1 still says setup is incomplete

Read the individual results; missing files or failed sign-ins need fixing.

Cursor skill discovery and model availability remain manual checks, even after the automatic checks pass.

Complete and record WINDOWS-TEST.md for those items; rerunning the CLI cannot inspect Cursor's account UI.
