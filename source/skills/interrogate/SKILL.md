---
name: interrogate
description: Run independent read-only reviewers against one change and synthesize actionable findings.
---

# Interrogate

## Scope and intent

Freeze the candidate revision or working-tree snapshot. Include staged, unstaged, and relevant untracked changes. Give reviewers the user intent, repository rules, changed behavior, and verification results. Use the ordered `interrogate reviewers` panel in [host routing](../repo-pstack-mode/references/host-routing.md); each gets the same rubric and read-only access.

## Review

Ask for concrete defects with severity, file and line, a failing scenario, and a recommended fix. Ask for missing checks and evidence limits. A finding needs a behavior path, not stylistic preference. Wait for every requested reviewer and name missing seats.

## Synthesize

Deduplicate findings; check each against code and tests. Separate confirmed defects, plausible concerns, and dismissed claims. Note agreement and disagreement without treating votes as proof. Fix in-scope defects, rerun affected checks, and re-review changed lines where required. Report the reviewed revision and open risks.
