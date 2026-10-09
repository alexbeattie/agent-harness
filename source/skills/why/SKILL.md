---
name: why
description: Investigate why code or a decision exists using history and current-source evidence.
---

# Why

## Anchor the question

Identify the exact behavior, symbol, commit, ticket, or design boundary. State the competing explanations. Read the current code and tests before searching history. In native PowerShell, use Git commands such as `git blame -L <start>,<end> <file>`, `git log --follow -p -- <file>`, and `git show <commit>` without shell-specific pipelines.

## Investigate

Partition evidence into source history, issue/PR discussion, documentation, and runtime observations that are actually accessible. Use the `why investigators` role in [host routing](../repo-pstack-mode/references/host-routing.md). Keep each investigator read-only and give the same target plus a distinct source category. Use the repository's live Bitbucket and Jira routes where available. A missing connector is an evidence gap, not proof that no decision exists.

## Synthesize

Use the `why synthesizer` role for a multi-source question. Build a timeline of change and stated rationale, then test that rationale against the current path. Distinguish written intent, code behavior, and your inference. Name contradicting sources and dates. Conclude with what the evidence supports and what remains unknown; avoid inventing a decision owner.
