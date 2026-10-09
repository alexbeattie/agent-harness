# Install on Windows 11

Use your own Windows account and a normal PowerShell terminal. You can run it standalone or inside Cursor, VS Code, another editor or an IDE.

The default install prepares Cursor, Codex CLI and Claude Code. You only need accounts for the agents and services you choose. If company policy blocks an installer, ask IT to approve it.

## Get the package

Extract the ZIP into a permanent folder such as `C:\Work\agent-harness`. Compare its checksum with `Get-FileHash .\<zip file name> -Algorithm SHA256` before extracting.

Open PowerShell in the extracted folder containing install.ps1. Review the scripts, then use `Get-ChildItem -Recurse -File | Unblock-File` if Windows marked the trusted download as blocked.

## Choose agents and install

Run this command for all three:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\install.ps1
```

Or select one:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\install.ps1 -Agents cursor
powershell -NoProfile -ExecutionPolicy Bypass -File .\install.ps1 -Agents codex
powershell -NoProfile -ExecutionPolicy Bypass -File .\install.ps1 -Agents claude
```

Run only the line that matches your choice. From a PowerShell session whose policy permits the script, `& .\install.ps1 -Agents codex,claude` selects both CLIs.

Every install and check command has its own selection. Omitting `-Agents` means all three. A selected install preserves generated files for agents installed earlier; it does not uninstall them or overwrite their local edits. Adding another agent later uses the same installer.

The installer installs Git, Python and the selected missing CLI agents. For Cursor, install the [desktop editor](https://cursor.com/downloads) yourself; the harness supplies its skills and rule template. AWS and TWG tool installation is optional under `-IncludeServices`.

The process-scoped execution-policy override does not change machine policy. The harness, hx, haws and htwg commands run under your account's normal policy. If check.ps1 reports a blocking policy, use `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` with IT approval.

The installer does not sign in or copy accounts. If it reports a conflict, follow [TROUBLESHOOTING.md](TROUBLESHOOTING.md) before changing the affected file.

Close and reopen the terminal application when installation finishes. If it runs inside an editor, quit and restart that editor. A new terminal tab in an already running application can retain its old PATH.

## Cursor

Sign in to the Cursor desktop editor. Open your project and start a new Agent chat.

Type `/repo-pstack-mode` and confirm the skill appears. Ask it to report the source path and Cursor model roles from host-routing.md without editing files. The installed skills live in `.agents\skills` under your home folder.

Open `.agent-harness\cursor-user-rules.txt` under your home folder. Copy its contents into Cursor's **Customize > Rules > User Rules**. Preserve your existing rules. Review this copy again after changing model configuration and rerunning the installer.

That generated file is a template. Cursor's filesystem `.cursor/rules` convention is project-scoped, so placing it under your home folder does not establish that it applies globally. The shared skill also carries the model mappings. See [Cursor rules](https://cursor.com/docs/rules) and [local skill discovery](https://cursor.com/docs/skills).

Check the configured roles against models available in your Cursor account. Keep a role pending if its model is unavailable. Remote and cloud sessions need their own setup; this package configures the local Windows account.

## Codex CLI

Run `codex`, complete its sign-in flow with your own account, and exit when you reach its prompt.

In your project folder, run `harness codex`, then enter `$repo-pstack-mode`.

The wrapper selects the generated agent-harness CLI profile. A plain `codex` command may use your personal defaults. The profile does not configure the Codex desktop app or an IDE extension.

## Claude Code

Run `claude` and complete its sign-in flow with your own account or your organization's supported access method, then exit.

In your project folder, run `harness claude`, then enter `/agent-harness:repo-pstack-mode`.

The wrapper loads the generated settings and plugin for this Claude Code session. Confirm the namespaced skill appears in the slash menu. Plugin skills use the plugin prefix, as described in [Claude Code's skill documentation](https://code.claude.com/docs/en/skills).

Claude Code can be your primary agent. It does not need a preceding Codex session. The Codex-backed `astra` role and automatic dispatch classification require Codex separately; workflows using those features remain pending until that dependency is ready.

## Check the selected agents

From the package folder, run `powershell -NoProfile -ExecutionPolicy Bypass -File .\check.ps1` for all three. Add `-Agents cursor`, `-Agents codex` or `-Agents claude` to check one.

The check covers selected generated files, commands, CLI sign-ins, normal terminal execution policy and wrapper paths. Cursor's app, skill discovery, User Rules and account model access need manual verification.

Add `-ProbeModels` to test the selected CLI agents' configured native models when you are ready. These probes can consume quota or incur charges. Unrequested probes and manual checks remain pending even when the automatic checks pass.

Cross-provider panels and independent reviews need their configured second agent. An individual setup can start without it; a required review or panel must remain incomplete until its dependency is available. Models and required reviews are never silently substituted.

Follow [WINDOWS-TEST.md](WINDOWS-TEST.md) and save results outside this repository.

## Optional AWS and Atlassian access

Install the service CLIs by rerunning the installer with the same agent selector and `-IncludeServices`. For example:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\install.ps1 -Agents codex -IncludeServices
```

After completing the sign-ins below, use `powershell -NoProfile -ExecutionPolicy Bypass -File .\check.ps1 -Agents codex -IncludeServices` to request service readiness checks too. Substitute your own selected agent, or omit `-Agents` for all three. Service access is not required to open an agent session.


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

Use your own scoped Atlassian API token where required; Bitbucket app passwords are retired.

Do not paste a token into a chat, task file, Git commit or this repository's configuration.

For AWS SSO, run `aws configure sso --profile team-dev`, enter the details supplied by your administrator, then run `aws sso login --profile team-dev`.

If your organization uses another AWS sign-in method, follow its instructions for a named profile instead.

Set `$env:AWS_PROFILE = 'team-dev'` in the terminal before AWS work.

To use that profile in future terminals, run `[Environment]::SetEnvironmentVariable('AWS_PROFILE', 'team-dev', 'User')`, then close and reopen your terminal application or editor.

Choose the profile name supplied by your team if it differs from this example.


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
