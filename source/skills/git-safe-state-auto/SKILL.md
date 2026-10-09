---
name: git-safe-state-auto
description: Protect a single-checkout Git repository before switching or beginning task work.
---

# Git safe state

Inspect `git worktree list --porcelain` first. More than one entry means a shared repository: hand off to [worktree-level-set](../worktree-level-set/SKILL.md) and do not switch or stash. For one checkout, inspect `git status --porcelain=v1`, branch, upstream, and remote default branch. Never infer a base from an old local branch when the repository specifies a different development ref.

If anything is modified or untracked, identify ownership and protect it before changing branches. Do not discard unknown files. Fetch the intended remote; if it fails, report that the base freshness is unverified. When starting new work, create a task branch with the repository's naming rule from the verified base. For inspection only, leave the current branch intact. Confirm the final branch, HEAD, working-tree status, and upstream. Do not push the base branch directly.
