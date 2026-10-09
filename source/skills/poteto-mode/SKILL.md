---
name: poteto-mode
description: Route a bounded engineering task through grounding, implementation, verification, and evidence.
---

# Poteto mode

Read [Team routing](../repo-pstack-mode/SKILL.md) and its [host routing](../repo-pstack-mode/references/host-routing.md). The active repository's instructions take precedence for delivery. Model selection comes only from the generated host routing; no skill default or nearest-model substitution applies.

## Start

Classify the task as investigation, feature, bug fix, performance, refactor, design, or review. State the user-visible outcome and the scope you can change. Read the repository guide and current worktree state. Do not start implementation from an old status claim.

## Plan in verifiable units

Use [how](../how/SKILL.md) to trace unfamiliar behavior and [why](../why/SKILL.md) when historical rationale matters. Identify one observable check per unit. Separate independent writers by worktree or output path before parallel work. Use [figure-it-out](../figure-it-out/SKILL.md) for a long or ambiguous process; use [architect](../architect/SKILL.md) before changing ownership or interfaces.

For a bug, reproduce first, add a failing behavior test where practical, fix the cause, and rerun focused checks. For a feature, spell out acceptance behavior, build the narrow path, then test the real path. For performance, define fixture and baseline before optimization. For a refactor, freeze behavior with meaningful checks and change one boundary at a time. Follow the active repository's more specific test rules.

## Delegation

Use the host's agent API and the exact role entry in host routing. Give every worker a precise file or evidence responsibility and say that other agents share the workspace. Keep independent candidate writers in separate worktrees. A reviewer stays read-only. Resume a worker for follow-ups; after an interruption, start fresh with the task context, known results, and current file state. A missing model blocks that panel seat and must be reported.

## Finish

Run focused behavior checks and required repository gates. Read the produced diff and review findings; resolve in-scope defects. Use [interrogate](../interrogate/SKILL.md) when an adversarial panel is called for, [deslop](../deslop/SKILL.md) for code scope, and [unslop](../unslop/SKILL.md) for prose. Verify external state live before reporting it. Keep unverified work open and name its next owner/action. Never start a bookkeeping-only PR after product delivery unless the user separately requests it.
