# Configuration changes

config/harness.json contains the model mappings previously maintained separately for Cursor, Codex and Claude Code.

The existing model identifiers and role order are preserved; the package does not translate them into another provider's names.

Codex's main model, reasoning effort, reasoning summary and speed setting are retained in its generated profile.

The profile enables Codex's multi_agent feature, matching the source setup, so the included workflows can delegate.

Claude's main model, reasoning effort and thinking setting are retained in its generated settings file.

Cursor's role mappings are generated into its shared skill and a User Rules template. Import the template body through Cursor's Customize > Rules > User Rules; preserve existing rules.

The source files contain no account tokens, AWS profile contents or saved login state.

The package uses normal host permission checks and asks before external writes; it does not copy the original machine's permissive approval or sandbox settings.

Codex is started with a named team profile; Claude receives explicit settings and plugin arguments.

Existing personal config.toml, settings.json, mcp.json and global instruction files are not replaced.

The optional context and assistant services templates are disabled and have blank endpoints until each person obtains their own connection details.

The maximum concurrent agent count is set in max_parallel_agents; the generated instructions tell hosts to queue additional panel members.

No task ledger, session transcript or personal writing hook is installed.

TWG uses the official CLI's per-user OAuth and scoped-token setup.

INSTALL.md selects the vendor's experimental encrypted storage, whose Windows root key is held in Windows Credential Manager; it does not modify the vendor binary or put tokens in the harness config.

The current authentication method and storage commands are documented in [Atlassian's OAuth guide](https://developer.atlassian.com/platform/teamwork-graph/twg-cli/getting-started/configure-oauth/).
