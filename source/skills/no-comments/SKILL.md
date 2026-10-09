---
name: no-comments
description: Review new code comments and remove comments that restate the implementation.
---

# No comments

Scope the changed files and read the code without its new comments. Have a read-only reviewer follow [comment review rules](../repo-pstack-mode/references/agents/comment-sicko.md). Remove comments that narrate obvious syntax or repeat names. Preserve comments that explain a non-obvious invariant, external contract, safety boundary, or surprising tradeoff. Check that a test or type can carry a claim more accurately. Review the diff after removal; do not change behavior as part of this pass.
