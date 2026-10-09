# Install on Windows 11

Use your own Windows account and a normal PowerShell terminal.

You need internet access, permission to install developer tools, and your own Cursor, OpenAI, Anthropic, Atlassian and AWS access.

If your company blocks an installer or PowerShell policy, ask IT to approve it; do not disable company controls.

## Get the package

Extract the ZIP into a permanent folder such as C:\Work\agent-harness.

If you received a checksum alongside the ZIP, compare it with `Get-FileHash .\<zip file name> -Algorithm SHA256` before extracting.

Open the extracted folder in Cursor and open a PowerShell terminal there.

Review the scripts, then unblock the files you trust with `Get-ChildItem -Recurse -File | Unblock-File` if Windows marked the download as blocked.

Run `powershell -NoProfile -ExecutionPolicy Bypass -File .\install.ps1`.

This changes execution policy for that process only; company policy can still prevent execution.

The harness, hx, haws and htwg commands run under your account's normal execution policy, which Windows leaves at Restricted on a new client account. If check.ps1 reports a blocking policy, run `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` once with IT approval; do not change the machine-wide policy.

The installer installs missing tools and generates the team skills and settings.

It does not sign in for you, request a token, or copy another user's accounts.

If it reports a file conflict, stop and follow TROUBLESHOOTING.md rather than overwriting the file.

Quit Cursor completely and start it again after installation. A new terminal tab inside a running Cursor keeps the environment Cursor started with and does not see the updated PATH or newly installed tools.

## Sign in to each program

Sign in to Cursor through its account menu using your own account.

Run `codex` and follow its sign-in flow, then exit when you reach its prompt.

Run `claude` and follow its sign-in flow using your own Anthropic account or your company's supported access method.

For a fresh TWG installation, select its encrypted credential storage before signing in:

```powershell
$env:TWG_SECRET_STORE = 'keychain'
twg login --force --oauth
Remove-Item Env:TWG_SECRET_STORE
```

Follow the Atlassian prompts using your own company account and choose your own site.

TWG labels this encrypted storage experimental; on Windows it keeps the root key in Windows Credential Manager and encrypted credentials under your own %APPDATA%\twg folder.

Run `twg doctor --basic` and confirm it reports encrypted storage with the root key in the OS vault.

For an existing TWG login, use `twg auth storage migrate` and review its prompt instead of replacing another account's files.

Run `twg setup bitbucket` to attach your own Bitbucket token when your work requires Bitbucket access.

Follow the interactive prompts and use the official authentication guide linked below if setup fails.

TWG manages per-user OAuth and token storage; the harness does not put Atlassian credentials in harness.json.

OAuth is the currently supported Atlassian sign-in method, so a site, email and token are not copied into a shared config. The separate Bitbucket token comes from your own account.

The inspected Mac executable contains Bun runtime markers; its original source language was not established, and that binary is not included.

Use your own scoped Atlassian API token where required; Bitbucket app passwords are retired.

Do not paste a token into a chat, task file, Git commit or this repository's configuration.

For AWS SSO, run `aws configure sso --profile team-dev`, enter the details supplied by your administrator, then run `aws sso login --profile team-dev`.

If your organization uses another AWS sign-in method, follow its instructions for a named profile instead.

Set `$env:AWS_PROFILE = 'team-dev'` in the terminal before AWS work.

To use that profile in future terminals, run `[Environment]::SetEnvironmentVariable('AWS_PROFILE', 'team-dev', 'User')`, then quit and restart Cursor.

Choose the profile name supplied by your team if it differs from this example.

## Check the installation

Run `powershell -NoProfile -ExecutionPolicy Bypass -File .\check.ps1` from the package folder. It reports the execution policy a normal terminal applies and whether harness, hx, haws and htwg resolve to this package.

Resolve each missing tool, sign-in or incompatible setting shown.

Cursor discovery and model access require the manual checks below; check.ps1 keeps them marked unverified and can return exit code 1 even when its automatic checks pass.

Follow the WINDOWS-TEST.md checklist and save manual results in a private test record outside this repository.

Run `powershell -NoProfile -ExecutionPolicy Bypass -File .\check.ps1 -ProbeModels` when you are ready for account model checks; probes can consume quota or incur charges.

Open a new Cursor agent chat, type `/repo-pstack-mode`, and confirm that the skill appears.

Ask it to report the source path and the Cursor swarm-worker model from host-routing.md without running tools or editing files.

Check that model in Cursor's available models; a file-presence check alone does not verify that Cursor loaded it or that your account can use it.

Use `harness codex` and `harness claude` for the configured terminal workflows.

## Optional service connections

The package does not need an optional context or assistant service for its basic terminal path.

The disabled connection list is .agent-harness/mcp.template.json under your home folder.

Host-format examples are in its mcp subfolder: cursor.json.example, claude.json.example and codex.toml.example.

They contain blank URLs and authorization fields and are not loaded automatically.

Ask each service's administrator for your own endpoint, token and supported MCP transport.

Keep the token in a per-user environment variable or the host's credential store, then add the connection through that host's supported MCP setup.

Do not enable a blank template or invent a server URL; assistant service was not present in the inspected source setup.

Run a read-only request before relying on the connection and do not use it to bypass write confirmation.

## Official setup references

[Codex on Windows](https://learn.chatgpt.com/docs/windows/windows-sandbox), [Cursor skills](https://cursor.com/docs/skills), and [Claude Code setup](https://code.claude.com/docs/en/setup) describe the host requirements.

[TWG installation](https://developer.atlassian.com/cloud/twg-cli/getting-started/installation/) and [TWG authentication](https://developer.atlassian.com/platform/teamwork-graph/twg-cli/getting-started/configure-oauth/) describe its supported installers and account storage.

[Bitbucket API tokens](https://support.atlassian.com/bitbucket-cloud/docs/using-api-tokens/) replace retired app passwords.

[AWS CLI installation](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html) and [AWS SSO configuration](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-sso.html) describe the AWS setup.
