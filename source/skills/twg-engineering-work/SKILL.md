---
name: twg-engineering-work
description: Reconcile a repository ticket and Bitbucket PR against live code, CI, and review state.
---

# Engineering work with htwg

Use [TWG through the harness](../twg/SKILL.md) to read the task ticket, related PRs, and current target branch. Identify the PR head and target commit, required CI for that exact head, review requirements, unresolved tasks, and merge conflicts. Compare code and PR discussion when a replacement PR may include earlier work. Report every task PR as merged with verified target commit, open with a named blocker and next action, or closed with an authorized reason.

Keep local tests, CI, merge, deployment, browser QA, and acceptance separate. Before any Bitbucket or Jira write, use the full `htwg` command and explicit human `yes` through the wrapper, then read back the saved state. The repository's delivery rules and user's current authorization decide which actions may proceed. Do not close a PR just to clear a queue or create a bookkeeping-only follow-up PR after product delivery.
