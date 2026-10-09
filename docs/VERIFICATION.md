# Verification record

This record distinguishes package checks on macOS from acceptance on a fresh Windows 11 account.

## Repeat the package checks

Run `python -m unittest discover -s tests -v` from the package folder.

Run `powershell -NoProfile -ExecutionPolicy Bypass -File .\tests\test_powershell.ps1` on Windows, or use pwsh when PowerShell 7 is installed.

Run `python tools/generate_docs.py` and `python tools/package_release.py --check`.

Review changed content before creating a release; the pattern scanner cannot prove that all private material is absent.

## Independent Claude review

A prior package review ran on October 9, 2026 through Claude Code print mode with the requested model claude-opus-5-5, tools disabled, strict MCP configuration and no session persistence. It predates the neutral package rename.

The completed result reported is_error false and modelUsage naming only claude-opus-5-5.

The prompt covered the distributable source at that time. Its raw result and review text are outside this repository.

The reviewer found no P0 defect and rated three findings P1: wrappers on PATH run under the account's execution policy, which a new Windows client leaves at Restricted; an unquoted comma list such as `Key=HarnessTest,Value=Denied` reached the wrappers as `Key=HarnessTest Value=Denied`; and redirected dispatch output crashed with a charmap encoding error under a cp1252 console code page.

The comma rewrite and the swallowed bare `--` were reproduced on PowerShell 7.6.6, and the charmap crash on Python 3.13 with PYTHONIOENCODING=cp1252, before changing anything. The execution-policy finding rests on documented Windows defaults and has not been observed on a Windows account.

Fixes made after that review: wrappers rejoin array-valued arguments with commas and run the package they live in; the launcher writes UTF-8 to redirected output; check.ps1 reports the execution policy a normal terminal applies and whether harness, hx, haws and htwg resolve to the package; the installer removes bin folders of earlier package copies from the user PATH; the AWS guard refuses credential-printing commands (STS session and role credentials, ECR login passwords, KMS decrypt, SSM parameter history, configure export-credentials and credential keys, `--debug`) and prompts for ECS task definitions; command help after a subcommand runs as a read; the credential text match requires a header-shaped value; approval prompts show a `Will run` line and a `Rerun yourself` line with control characters escaped; dispatch and check.ps1 share one model-identity rule, so an alias such as opus verifies against the single reported identity; the classifier runs with the agent-harness profile and keeps Codex output out of `--classify-only`; `harness claude` passes the configured model explicitly; the version comes from the VERSION file alone; and the prove-it-works skill no longer names an unbundled skill.

At that revision, the Cursor rule file still installed under the home folder without an explicit User Rules import; the classifier inherited any MCP servers in the user's own Codex configuration; the reviewer's runtime questions about Python discovery, standard-user MSI installation, the Codex sandbox, Claude Code's shell and the TTY gate under agent consoles remain Windows acceptance items.

## Completed on October 9, 2026

The Python suite passed all 74 tests on macOS with Python 3.13.11 and again with Python 3.14.2.

Coverage includes exact model routing, alias identity verification, failed and malformed model responses, command argument boundaries, UTF-8 task input, UTF-8 launcher output under a legacy code page, write denial, credential-printing command denial, header-shaped credential detection, control-character escaping in approval prompts, generated-file conflicts, retired-file tracking, installed skill links, the single version source and release selection.

The PowerShell fixture passed with PowerShell 7.6.6 on macOS: syntax of every entry point, the execution-policy and PATH helpers, all four wrappers under Legacy and Standard argument passing with quoted, empty, unquoted comma-list and bare `--` arguments, exit code 7, native stdout, and installation into a fixture home from a package path containing a space without touching live user settings.

The earlier one-off check that stdin, stdout and stderr stay terminals through the wrappers is not a repository fixture and was not repeated; the shipped fixture redirects the streams.

A fresh fixture installation generated 104 managed files; the next installation changed 0 files.

The prior package passed the private-content pattern scan and manual source review. Those results do not verify this renamed package.

## Neutral package checks on October 9, 2026

The renamed package passed 74 Python unit tests, the PowerShell 7.6.6 fixture on macOS, and `tools/package_release.py --check` for 101 selected source files. The fixture generated 104 files in an isolated home and made no live user-setting changes. The package name, Python import package, installed paths, profile and skill name changed together; the configured model values and external write guards were retained. Native Windows acceptance and independent review of this renamed package remain open.

## Version 1.0.1 agent selection checks on October 9, 2026

The Python 3.14 suite passed 82 tests. The PowerShell 7.6.6 fixture passed on macOS, including selected installs, mixed-case agent selectors, empty-selection rejection and check argument forwarding. Package checks passed for 101 selected source files. All PowerShell source files have CRLF line endings.

Direct CLI generation into isolated homes produced 50 managed files for Cursor, 50 for Codex, 53 for Claude and 104 for all three. Repeating each command changed zero files. Regression tests cover adding an agent without erasing another agent's edits or ownership, retaining the obsolete Cursor rule for manual reconciliation, selected-agent sign-in failures and excluding calls to unselected agents and services.

An independent read-only review exercised all seven nonempty agent combinations and upgrade preservation. It found a PowerShell/Python selector case mismatch; the correction passed focused rechecks with no remaining actionable findings. This was not a completed Claude or GPT-5.5 review.

No native Windows install, paid model probe or live service write was run for this revision. Cursor discovery and User Rules import, each person's sign-in and model access, and optional cross-provider handoffs remain Windows acceptance checks.

## Windows acceptance remains required

Follow WINDOWS-TEST.md under a new standard Windows user account and record the actual host versions and account model availability.

Native installer execution, the effective execution policy, PATH after restarting the terminal application or its editor, Cursor skill and rule discovery, live model handoff with non-ASCII output, redirected-input refusal through a real standard-input pipe, Atlassian reads and AWS identity have not been established by tests on the Mac.

The raw service CLIs and write-capable MCP connections can bypass a cooperative wrapper; use service permissions to enforce any stronger restriction.
