---
name: swarm
description: Split independent work among agents with explicit ownership and a combined verification pass.
---

# Swarm

## Frame

Split by non-overlapping files or read-only evidence questions. Define each worker's deliverable, dependencies, interface assumptions, and verification. Use the configured `swarm workers` role in [host routing](../repo-pstack-mode/references/host-routing.md). Every worker is told others share the workspace and must preserve their edits.

## Fan out

Create separate worktrees for independent code writers. For one shared worktree, assign disjoint file ownership and serialize conflicting edits. Start independent workers together, using the host's agent API. Give task context and file pointers, not a pasted repository dump. Keep a single integration owner.

## Aggregate

Read each result and actual diff. Resolve interface mismatches, run each focused check, then run the combined candidate's required checks. Report completed partitions, failed or missing workers, integration changes, and remaining risks. A worker saying a task is done is not verification.
