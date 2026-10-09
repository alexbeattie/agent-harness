---
name: worktree-level-set
description: Triage a shared repository's worktrees before choosing a safe task checkout.
---

# Worktree level set

Run before the first substantive change where the repository requires it. In PowerShell, run `git fetch` for the configured remote, `git worktree list --porcelain`, `git status --short` in each reachable worktree, and inspect its branch, base, ahead/behind state, and open task ownership. A failed fetch is a blocker to claiming a fresh base; it does not justify resetting another checkout.

Classify each worktree as active, dirty, finished, stale but potentially owned, or unknown. Untracked files count as work. Report the state before cleanup. Do not switch, stash, reset, restore, clean, or remove a shared worktree over another writer's files. Inspect remote PR state before deciding that a checkout is finished. Cleanup is a separate action with the active owner's consent or clear ownership evidence.

Select an existing suitable worktree when it belongs to this task. Otherwise create a new task branch and worktree from the repository's freshly fetched development ref, following the repository's naming/path convention. Never publish to the shared development branch directly. Confirm `git status`, branch, HEAD, and base in the selected worktree before editing. Use [git-safe-state-auto](../git-safe-state-auto/SKILL.md) only for a genuinely single-checkout repository.
