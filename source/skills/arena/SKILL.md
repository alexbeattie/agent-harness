---
name: arena
description: Compare independent candidates under one rubric and combine only compatible improvements.
---

# Arena

## Frame

Define the behavior and constraints, objective checks, candidate count, and time budget. Use the exact ordered `arena runners` in [host routing](../repo-pstack-mode/references/host-routing.md). Give each runner the same prompt and its own worktree or output path. Record the starting revision.

## Fan out and judge

Run candidate writers independently. Wait for all requested candidates before judging. Then choose one read-only judge from `arena cross-judge pool`, preferably from a different model family, and provide each candidate's path and the same rubric. The judge compares observed behavior and risks; the parent also reads and tests candidates. Report any missing panel seat; never substitute a model.

## Pick and graft

Choose one coherent base. Port only changes that improve it under the rubric, one at a time. Check for incompatible assumptions and shared-state conflicts. Run the relevant behavior tests on the combined result, then the repository's required verification. Record winner, evidence, rejected tradeoffs, and open risks. Do not merge or publish without the repository's delivery gates.
