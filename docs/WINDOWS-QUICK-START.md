# Windows quick start

Open the public [agent-harness repository](https://github.com/alexbeattie/agent-harness) or download the release package.

## Download and extract

[Download the Windows ZIP](https://github.com/alexbeattie/agent-harness/releases/download/v1.0.0-windows-test.2/agent-harness-1.0.0.zip).

Extract it to a permanent location, such as `C:\Work\agent-harness`. Open the folder containing `install.ps1` in Cursor, then open a PowerShell terminal there.

## Install

Review the scripts, then run:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\install.ps1
```

This sets the execution policy for that process only. If company policy blocks installation, ask IT to approve it.

Quit Cursor completely and reopen it so it picks up the updated PATH.

## Sign in

Follow the [installation guide](https://github.com/alexbeattie/agent-harness/blob/main/docs/INSTALL.md) to sign in with your own Cursor, Codex, Claude, Atlassian and AWS accounts.

## Check the installation

Open PowerShell in the same package folder and run:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\check.ps1
```

Follow the reported checks. Cursor discovery and model access still require manual verification; `check.ps1` can return exit code 1 while those checks remain unverified.

Follow the [WINDOWS-TEST.md checklist](https://github.com/alexbeattie/agent-harness/blob/main/docs/WINDOWS-TEST.md) and save the PC results in a private test record outside this repository. The existing package checks passed on macOS; native Windows acceptance is pending.
