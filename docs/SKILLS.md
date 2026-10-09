# Included skills

This reference is generated from config/skills.json and the 44 canonical skill folders.

Run python tools/generate_docs.py after changing the source.

## architect

Sketch a change's types, signatures, and ownership boundaries before implementing it.

When to use it: Design tradeoffs before implementation.

Example: `Use architect to sketch module boundaries before a refactor.`

Runs in Cursor and Codex through the shared installed skills, and in Claude as `/agent-harness:architect` through the generated team plugin.

Limits and requirements: The active repository owns implementation gates.

Source: [source/skills/architect/SKILL.md](../source/skills/architect/SKILL.md).

Required skills: how, why, repo-pstack-mode, arena.

## arena

Compare independent candidates under one rubric and combine only compatible improvements.

When to use it: Several independent candidate approaches are useful.

Example: `Use arena to compare two implementations against one rubric.`

Runs in Cursor and Codex through the shared installed skills, and in Claude as `/agent-harness:arena` through the generated team plugin.

Limits and requirements: Candidate writers need isolated paths.

Source: [source/skills/arena/SKILL.md](../source/skills/arena/SKILL.md).

Required skills: repo-pstack-mode.

## deslop

Remove speculative code and needless structure from a candidate without changing behavior.

When to use it: Candidate contains extra code or abstraction.

Example: `Use deslop after behavior is verified.`

Runs in Cursor and Codex through the shared installed skills, and in Claude as `/agent-harness:deslop` through the generated team plugin.

Limits and requirements: Rerun affected behavior checks.

Source: [source/skills/deslop/SKILL.md](../source/skills/deslop/SKILL.md).

## figure-it-out

Build and execute an auditable path through an ambiguous technical task.

When to use it: Ambiguous task with multiple unknowns.

Example: `Use figure-it-out to run the shortest discriminating experiment.`

Runs in Cursor and Codex through the shared installed skills, and in Claude as `/agent-harness:figure-it-out` through the generated team plugin.

Limits and requirements: External writes retain their approval gate.

Source: [source/skills/figure-it-out/SKILL.md](../source/skills/figure-it-out/SKILL.md).

Required skills: principle-attack-the-premise.

## git-safe-state-auto

Protect a single-checkout Git repository before switching or beginning task work.

When to use it: Before branch movement in a single-checkout repository.

Example: `Use git-safe-state-auto to inspect status and base.`

Runs in Cursor and Codex through the shared installed skills, and in Claude as `/agent-harness:git-safe-state-auto` through the generated team plugin.

Limits and requirements: Hand off if multiple worktrees exist.

Source: [source/skills/git-safe-state-auto/SKILL.md](../source/skills/git-safe-state-auto/SKILL.md).

Required skills: worktree-level-set.

## how

Explain how a code path works using traced evidence and an audience-sized mental model.

When to use it: Question about current code flow.

Example: `Use how to trace an API request to its output.`

Runs in Cursor and Codex through the shared installed skills, and in Claude as `/agent-harness:how` through the generated team plugin.

Limits and requirements: Reading code alone does not prove runtime behavior.

Source: [source/skills/how/SKILL.md](../source/skills/how/SKILL.md).

Required skills: repo-pstack-mode.

## interrogate

Run independent read-only reviewers against one change and synthesize actionable findings.

When to use it: Candidate needs independent review.

Example: `Use interrogate for read-only review of a frozen diff.`

Runs in Cursor and Codex through the shared installed skills, and in Claude as `/agent-harness:interrogate` through the generated team plugin.

Limits and requirements: Reviewer consensus is not proof.

Source: [source/skills/interrogate/SKILL.md](../source/skills/interrogate/SKILL.md).

Required skills: repo-pstack-mode.

## no-comments

Review new code comments and remove comments that restate the implementation.

When to use it: Review changed code comments.

Example: `Use no-comments on the current diff.`

Runs in Cursor and Codex through the shared installed skills, and in Claude as `/agent-harness:no-comments` through the generated team plugin.

Limits and requirements: Keep comments that explain real invariants.

Source: [source/skills/no-comments/SKILL.md](../source/skills/no-comments/SKILL.md).

Required skills: repo-pstack-mode.

## poteto-mode

Route a bounded engineering task through grounding, implementation, verification, and evidence.

When to use it: Bounded engineering task needing a verified outcome.

Example: `Use poteto-mode to implement a bug fix in verifiable units.`

Runs in Cursor and Codex through the shared installed skills, and in Claude as `/agent-harness:poteto-mode` through the generated team plugin.

Limits and requirements: Do not substitute an unavailable role model.

Source: [source/skills/poteto-mode/SKILL.md](../source/skills/poteto-mode/SKILL.md).

Required skills: repo-pstack-mode, how, why, figure-it-out, architect, interrogate, deslop, unslop.

## principle-attack-the-premise

Apply when repeated fixes sharing an assumption fail. State the assumption and choose an observation that can challenge it before trying another fix that depends on it.

When to use it: A decision or review calls for the attack the premise principle.

Example: `Read principle-attack-the-premise while reviewing a relevant change.`

Runs in Cursor and Codex through the shared installed skills, and in Claude as `/agent-harness:principle-attack-the-premise` through the generated team plugin.

Limits and requirements: Apply only where the task trigger fits; repository rules remain authoritative.

Source: [source/skills/principle-attack-the-premise/SKILL.md](../source/skills/principle-attack-the-premise/SKILL.md).

Required skills: principle-fix-root-causes, principle-build-the-lever, principle-redesign-from-first-principles.

## principle-boundary-discipline

Apply when wiring validation, error handling, or framework adapters. Concentrate guards at system boundaries (CLI, config, network, external APIs); trust internal types and keep business logic in pure functions.

When to use it: A decision or review calls for the boundary discipline principle.

Example: `Read principle-boundary-discipline while reviewing a relevant change.`

Runs in Cursor and Codex through the shared installed skills, and in Claude as `/agent-harness:principle-boundary-discipline` through the generated team plugin.

Limits and requirements: Apply only where the task trigger fits; repository rules remain authoritative.

Source: [source/skills/principle-boundary-discipline/SKILL.md](../source/skills/principle-boundary-discipline/SKILL.md).

## principle-build-the-lever

Apply to any non-trivial work, not just bulk work: edits, migrations, analyses, checks. Build the tool that does it or proves it (codemod, script, generator, or a skill your subagents follow) instead of working by hand. The tool is the artifact a reviewer can rerun.

When to use it: A decision or review calls for the build the lever principle.

Example: `Read principle-build-the-lever while reviewing a relevant change.`

Runs in Cursor and Codex through the shared installed skills, and in Claude as `/agent-harness:principle-build-the-lever` through the generated team plugin.

Limits and requirements: Apply only where the task trigger fits; repository rules remain authoritative.

Source: [source/skills/principle-build-the-lever/SKILL.md](../source/skills/principle-build-the-lever/SKILL.md).

Required skills: principle-laziness-protocol, principle-encode-lessons-in-structure, principle-prove-it-works.

## principle-encode-lessons-in-structure

Apply when you catch yourself writing the same instruction a second time, or notice a recurring correction. Encode the rule as a lint, metadata flag, runtime check, or script instead of more text.

When to use it: A decision or review calls for the encode lessons in structure principle.

Example: `Read principle-encode-lessons-in-structure while reviewing a relevant change.`

Runs in Cursor and Codex through the shared installed skills, and in Claude as `/agent-harness:principle-encode-lessons-in-structure` through the generated team plugin.

Limits and requirements: Apply only where the task trigger fits; repository rules remain authoritative.

Source: [source/skills/principle-encode-lessons-in-structure/SKILL.md](../source/skills/principle-encode-lessons-in-structure/SKILL.md).

## principle-exhaust-the-design-space

Apply when facing a novel UI interaction or architectural decision with no precedent in the codebase. Build 2-3 competing prototypes and compare side by side before committing.

When to use it: A decision or review calls for the exhaust the design space principle.

Example: `Read principle-exhaust-the-design-space while reviewing a relevant change.`

Runs in Cursor and Codex through the shared installed skills, and in Claude as `/agent-harness:principle-exhaust-the-design-space` through the generated team plugin.

Limits and requirements: Apply only where the task trigger fits; repository rules remain authoritative.

Source: [source/skills/principle-exhaust-the-design-space/SKILL.md](../source/skills/principle-exhaust-the-design-space/SKILL.md).

## principle-experience-first

Apply when product, UX, or feature-scope tradeoffs come up. Choose user delight over implementation convenience; ship fewer polished features over more rough ones.

When to use it: A decision or review calls for the experience first principle.

Example: `Read principle-experience-first while reviewing a relevant change.`

Runs in Cursor and Codex through the shared installed skills, and in Claude as `/agent-harness:principle-experience-first` through the generated team plugin.

Limits and requirements: Apply only where the task trigger fits; repository rules remain authoritative.

Source: [source/skills/principle-experience-first/SKILL.md](../source/skills/principle-experience-first/SKILL.md).

## principle-explain-the-number

Apply before you trust, report, or act on a number you measured: a speedup, a regression, a throughput, a latency, or an eval result. Find what limits it, and rule out that it measured something other than the work you think.

When to use it: A decision or review calls for the explain the number principle.

Example: `Read principle-explain-the-number while reviewing a relevant change.`

Runs in Cursor and Codex through the shared installed skills, and in Claude as `/agent-harness:principle-explain-the-number` through the generated team plugin.

Limits and requirements: Apply only where the task trigger fits; repository rules remain authoritative.

Source: [source/skills/principle-explain-the-number/SKILL.md](../source/skills/principle-explain-the-number/SKILL.md).

Required skills: principle-prove-it-works.

## principle-fix-root-causes

Apply when debugging. Trace each symptom to its root cause and fix it there; reproduce first, ask why until you reach it, resist nil-check guards that silence crashes.

When to use it: A decision or review calls for the fix root causes principle.

Example: `Read principle-fix-root-causes while reviewing a relevant change.`

Runs in Cursor and Codex through the shared installed skills, and in Claude as `/agent-harness:principle-fix-root-causes` through the generated team plugin.

Limits and requirements: Apply only where the task trigger fits; repository rules remain authoritative.

Source: [source/skills/principle-fix-root-causes/SKILL.md](../source/skills/principle-fix-root-causes/SKILL.md).

## principle-foundational-thinking

Apply before writing logic: choosing core types and data structures, sequencing scaffold-vs-feature work, asking what concurrent actors share. Get the data structures right so downstream code becomes obvious.

When to use it: A decision or review calls for the foundational thinking principle.

Example: `Read principle-foundational-thinking while reviewing a relevant change.`

Runs in Cursor and Codex through the shared installed skills, and in Claude as `/agent-harness:principle-foundational-thinking` through the generated team plugin.

Limits and requirements: Apply only where the task trigger fits; repository rules remain authoritative.

Source: [source/skills/principle-foundational-thinking/SKILL.md](../source/skills/principle-foundational-thinking/SKILL.md).

## principle-guard-the-context-window

Apply when context is filling up: large outputs, long files, repeated reads, fan-out planning. Route bulk to subagents; keep summaries in the main thread, not raw payloads.

When to use it: A decision or review calls for the guard the context window principle.

Example: `Read principle-guard-the-context-window while reviewing a relevant change.`

Runs in Cursor and Codex through the shared installed skills, and in Claude as `/agent-harness:principle-guard-the-context-window` through the generated team plugin.

Limits and requirements: Apply only where the task trigger fits; repository rules remain authoritative.

Source: [source/skills/principle-guard-the-context-window/SKILL.md](../source/skills/principle-guard-the-context-window/SKILL.md).

## principle-laziness-protocol

Apply when refactoring, evaluating diff size, or tempted to add abstractions, layers, or signal threading. Bias toward deletion and the smallest change that solves the problem.

When to use it: A decision or review calls for the laziness protocol principle.

Example: `Read principle-laziness-protocol while reviewing a relevant change.`

Runs in Cursor and Codex through the shared installed skills, and in Claude as `/agent-harness:principle-laziness-protocol` through the generated team plugin.

Limits and requirements: Apply only where the task trigger fits; repository rules remain authoritative.

Source: [source/skills/principle-laziness-protocol/SKILL.md](../source/skills/principle-laziness-protocol/SKILL.md).

## principle-make-operations-idempotent

Apply when designing commands, lifecycle steps, or processing loops that run amid crashes, restarts, and retries. Converge to the same end state regardless of partial prior runs.

When to use it: A decision or review calls for the make operations idempotent principle.

Example: `Read principle-make-operations-idempotent while reviewing a relevant change.`

Runs in Cursor and Codex through the shared installed skills, and in Claude as `/agent-harness:principle-make-operations-idempotent` through the generated team plugin.

Limits and requirements: Apply only where the task trigger fits; repository rules remain authoritative.

Source: [source/skills/principle-make-operations-idempotent/SKILL.md](../source/skills/principle-make-operations-idempotent/SKILL.md).

## principle-migrate-callers-then-delete-legacy-apis

Apply when introducing a new internal API while old callers still exist. Migrate callers and delete the old API in the same wave instead of preserving compatibility layers.

When to use it: A decision or review calls for the migrate callers then delete legacy apis principle.

Example: `Read principle-migrate-callers-then-delete-legacy-apis while reviewing a relevant change.`

Runs in Cursor and Codex through the shared installed skills, and in Claude as `/agent-harness:principle-migrate-callers-then-delete-legacy-apis` through the generated team plugin.

Limits and requirements: Apply only where the task trigger fits; repository rules remain authoritative.

Source: [source/skills/principle-migrate-callers-then-delete-legacy-apis/SKILL.md](../source/skills/principle-migrate-callers-then-delete-legacy-apis/SKILL.md).

## principle-minimize-reader-load

Apply when reviewing or shaping code that's hard to trace. Count layers between question and answer, and hidden state in the reader's head; collapse one-caller wrappers and shrink mutable scope.

When to use it: A decision or review calls for the minimize reader load principle.

Example: `Read principle-minimize-reader-load while reviewing a relevant change.`

Runs in Cursor and Codex through the shared installed skills, and in Claude as `/agent-harness:principle-minimize-reader-load` through the generated team plugin.

Limits and requirements: Apply only where the task trigger fits; repository rules remain authoritative.

Source: [source/skills/principle-minimize-reader-load/SKILL.md](../source/skills/principle-minimize-reader-load/SKILL.md).

Required skills: principle-guard-the-context-window.

## principle-model-the-domain

Apply when writing stateful logic, or when code branches a lot or repeats a shape assumption across files. Encode the domain in a structure instead of scattered conditionals.

When to use it: A decision or review calls for the model the domain principle.

Example: `Read principle-model-the-domain while reviewing a relevant change.`

Runs in Cursor and Codex through the shared installed skills, and in Claude as `/agent-harness:principle-model-the-domain` through the generated team plugin.

Limits and requirements: Apply only where the task trigger fits; repository rules remain authoritative.

Source: [source/skills/principle-model-the-domain/SKILL.md](../source/skills/principle-model-the-domain/SKILL.md).

## principle-never-block-on-the-human

Apply when tempted to ask 'should I do X?' on reversible work. Proceed, present the result, let the human course-correct after the fact; reserve confirmation for irreversible actions.

When to use it: A decision or review calls for the never block on the human principle.

Example: `Read principle-never-block-on-the-human while reviewing a relevant change.`

Runs in Cursor and Codex through the shared installed skills, and in Claude as `/agent-harness:principle-never-block-on-the-human` through the generated team plugin.

Limits and requirements: Apply only where the task trigger fits; repository rules remain authoritative.

Source: [source/skills/principle-never-block-on-the-human/SKILL.md](../source/skills/principle-never-block-on-the-human/SKILL.md).

## principle-outcome-oriented-execution

Apply during planned rewrites and migrations with explicit phase boundaries. Converge on the target architecture; don't preserve smooth intermediate states with throwaway compatibility code.

When to use it: A decision or review calls for the outcome oriented execution principle.

Example: `Read principle-outcome-oriented-execution while reviewing a relevant change.`

Runs in Cursor and Codex through the shared installed skills, and in Claude as `/agent-harness:principle-outcome-oriented-execution` through the generated team plugin.

Limits and requirements: Apply only where the task trigger fits; repository rules remain authoritative.

Source: [source/skills/principle-outcome-oriented-execution/SKILL.md](../source/skills/principle-outcome-oriented-execution/SKILL.md).

## principle-prove-it-works

Apply after completing a task, before declaring done. Verify against the real artifact (run the feature, read the actual value, inspect the diff), not a proxy, self-report, or 'it compiles.'

When to use it: A decision or review calls for the prove it works principle.

Example: `Read principle-prove-it-works while reviewing a relevant change.`

Runs in Cursor and Codex through the shared installed skills, and in Claude as `/agent-harness:principle-prove-it-works` through the generated team plugin.

Limits and requirements: Apply only where the task trigger fits; repository rules remain authoritative.

Source: [source/skills/principle-prove-it-works/SKILL.md](../source/skills/principle-prove-it-works/SKILL.md).

## principle-redesign-from-first-principles

Apply when integrating a new requirement into an existing design. Redesign as if the requirement had been a foundational assumption from day one, instead of bolting it on.

When to use it: A decision or review calls for the redesign from first principles principle.

Example: `Read principle-redesign-from-first-principles while reviewing a relevant change.`

Runs in Cursor and Codex through the shared installed skills, and in Claude as `/agent-harness:principle-redesign-from-first-principles` through the generated team plugin.

Limits and requirements: Apply only where the task trigger fits; repository rules remain authoritative.

Source: [source/skills/principle-redesign-from-first-principles/SKILL.md](../source/skills/principle-redesign-from-first-principles/SKILL.md).

## principle-separate-before-serializing-shared-state

Apply when concurrent actors might write to the same file, branch, key, or state object. Eliminate the sharing first; serialize structurally only when one shared writer is a real invariant.

When to use it: A decision or review calls for the separate before serializing shared state principle.

Example: `Read principle-separate-before-serializing-shared-state while reviewing a relevant change.`

Runs in Cursor and Codex through the shared installed skills, and in Claude as `/agent-harness:principle-separate-before-serializing-shared-state` through the generated team plugin.

Limits and requirements: Apply only where the task trigger fits; repository rules remain authoritative.

Source: [source/skills/principle-separate-before-serializing-shared-state/SKILL.md](../source/skills/principle-separate-before-serializing-shared-state/SKILL.md).

## principle-sequence-verifiable-units

Apply to multi-step work (sweeps, migrations, runs of similar edits) and to how you stack commits and PRs. Break work into small units that each end in a verifiable state, check each before the next, and order delivery so the sequence proves itself to a reviewer.

When to use it: A decision or review calls for the sequence verifiable units principle.

Example: `Read principle-sequence-verifiable-units while reviewing a relevant change.`

Runs in Cursor and Codex through the shared installed skills, and in Claude as `/agent-harness:principle-sequence-verifiable-units` through the generated team plugin.

Limits and requirements: Apply only where the task trigger fits; repository rules remain authoritative.

Source: [source/skills/principle-sequence-verifiable-units/SKILL.md](../source/skills/principle-sequence-verifiable-units/SKILL.md).

## principle-subtract-before-you-add

Apply when sequencing an addition, refactor, or rewrite. Remove dead code, redundant validators, and stub references first, then build on the simpler base.

When to use it: A decision or review calls for the subtract before you add principle.

Example: `Read principle-subtract-before-you-add while reviewing a relevant change.`

Runs in Cursor and Codex through the shared installed skills, and in Claude as `/agent-harness:principle-subtract-before-you-add` through the generated team plugin.

Limits and requirements: Apply only where the task trigger fits; repository rules remain authoritative.

Source: [source/skills/principle-subtract-before-you-add/SKILL.md](../source/skills/principle-subtract-before-you-add/SKILL.md).

## principle-test-behavior-not-implementation

Apply when you write, change, or keep a test. Identify a relevant defect and check that the test detects it. Assert the required result or observable effect, including absence when the contract requires it.

When to use it: A decision or review calls for the test behavior not implementation principle.

Example: `Read principle-test-behavior-not-implementation while reviewing a relevant change.`

Runs in Cursor and Codex through the shared installed skills, and in Claude as `/agent-harness:principle-test-behavior-not-implementation` through the generated team plugin.

Limits and requirements: Apply only where the task trigger fits; repository rules remain authoritative.

Source: [source/skills/principle-test-behavior-not-implementation/SKILL.md](../source/skills/principle-test-behavior-not-implementation/SKILL.md).

## principle-type-system-discipline

Apply when designing types, reviewing a function signature, or writing code in any statically-typed language. Make illegal states unrepresentable, brand semantic primitives, parse external data at boundaries, refuse to lie to the compiler, exhaust variants, derive from authoritative schemas.

When to use it: A decision or review calls for the type system discipline principle.

Example: `Read principle-type-system-discipline while reviewing a relevant change.`

Runs in Cursor and Codex through the shared installed skills, and in Claude as `/agent-harness:principle-type-system-discipline` through the generated team plugin.

Limits and requirements: Apply only where the task trigger fits; repository rules remain authoritative.

Source: [source/skills/principle-type-system-discipline/SKILL.md](../source/skills/principle-type-system-discipline/SKILL.md).

## reflect

Review an agent run for repeatable lessons and propose scoped improvements.

When to use it: Review of a completed agent run.

Example: `Use reflect on the current task digest.`

Runs in Cursor and Codex through the shared installed skills, and in Claude as `/agent-harness:reflect` through the generated team plugin.

Limits and requirements: Do not scan unrelated chat histories.

Source: [source/skills/reflect/SKILL.md](../source/skills/reflect/SKILL.md).

Required skills: repo-pstack-mode.

## swarm

Split independent work among agents with explicit ownership and a combined verification pass.

When to use it: Work can be partitioned safely.

Example: `Use swarm to assign disjoint modules to workers.`

Runs in Cursor and Codex through the shared installed skills, and in Claude as `/agent-harness:swarm` through the generated team plugin.

Limits and requirements: One owner integrates and verifies.

Source: [source/skills/swarm/SKILL.md](../source/skills/swarm/SKILL.md).

Required skills: repo-pstack-mode.

## tdd

Fix behavior test first where the active repository requires TDD.

When to use it: Behavior change or bug fix where tests can reproduce it.

Example: `Use tdd to capture the failing input before a fix.`

Runs in Cursor and Codex through the shared installed skills, and in Claude as `/agent-harness:tdd` through the generated team plugin.

Limits and requirements: Do not invent a failing-test phase.

Source: [source/skills/tdd/SKILL.md](../source/skills/tdd/SKILL.md).

Required skills: principle-test-behavior-not-implementation.

## repo-pstack-mode

Route repository engineering work through the selected reasoning skills and the active repository's delivery rules.

When to use it: Repository engineering task.

Example: `Use repo-pstack-mode for a repository code change.`

Runs in Cursor and Codex through the shared installed skills, and in Claude as `/agent-harness:repo-pstack-mode` through the generated team plugin.

Limits and requirements: Repository delivery rules and human approval still apply.

Source: [source/skills/repo-pstack-mode/SKILL.md](../source/skills/repo-pstack-mode/SKILL.md).

Required skills: worktree-level-set, how, why, architect, arena, swarm, interrogate, tdd, twg, twg-jira, twg-engineering-work, principle-attack-the-premise, principle-test-behavior-not-implementation, principle-sequence-verifiable-units.

## technical-writing

Write technical material for a specific reader and task with verifiable claims.

When to use it: Writing a how-to, reference, tutorial, or explanation.

Example: `Use technical-writing for a setup guide.`

Runs in Cursor and Codex through the shared installed skills, and in Claude as `/agent-harness:technical-writing` through the generated team plugin.

Limits and requirements: Do not claim tests that did not run.

Source: [source/skills/technical-writing/SKILL.md](../source/skills/technical-writing/SKILL.md).

## twg

Use the recipient's official TWG CLI through the harness boundary for repository reads and approved writes.

When to use it: repository source reads or approved writes.

Example: `Use htwg to read a live PR.`

Runs in Cursor and Codex through the shared installed skills, and in Claude as `/agent-harness:twg` through the generated team plugin.

Limits and requirements: Official CLI and auth are per user; wrapper approval is cooperative.

Source: [source/skills/twg/SKILL.md](../source/skills/twg/SKILL.md).

## twg-engineering-work

Reconcile a repository ticket and Bitbucket PR against live code, CI, and review state.

When to use it: Ticket and Bitbucket PR delivery check.

Example: `Use twg-engineering-work to verify PR head and CI.`

Runs in Cursor and Codex through the shared installed skills, and in Claude as `/agent-harness:twg-engineering-work` through the generated team plugin.

Limits and requirements: Keep merge, deployment, QA, and acceptance distinct.

Source: [source/skills/twg-engineering-work/SKILL.md](../source/skills/twg-engineering-work/SKILL.md).

Required skills: twg.

## twg-jira

Read live Jira issue state and make only explicitly approved changes through htwg.

When to use it: Jira issue search, read, or approved update.

Example: `Use twg-jira to check duplicates before a new issue.`

Runs in Cursor and Codex through the shared installed skills, and in Claude as `/agent-harness:twg-jira` through the generated team plugin.

Limits and requirements: No ticket write without explicit human yes via htwg.

Source: [source/skills/twg-jira/SKILL.md](../source/skills/twg-jira/SKILL.md).

Required skills: twg.

## unslop

Cut filler and unsupported claims from technical prose while retaining evidence and voice.

When to use it: Technical prose needs a concise final pass.

Example: `Use unslop on a PR description.`

Runs in Cursor and Codex through the shared installed skills, and in Claude as `/agent-harness:unslop` through the generated team plugin.

Limits and requirements: Preserve material limitations and evidence.

Source: [source/skills/unslop/SKILL.md](../source/skills/unslop/SKILL.md).

## why

Investigate why code or a decision exists using history and current-source evidence.

When to use it: Question about historical rationale.

Example: `Use why to trace a design choice through commits and ticket discussion.`

Runs in Cursor and Codex through the shared installed skills, and in Claude as `/agent-harness:why` through the generated team plugin.

Limits and requirements: Missing history stays unknown.

Source: [source/skills/why/SKILL.md](../source/skills/why/SKILL.md).

Required skills: repo-pstack-mode.

## worktree-level-set

Triage a shared repository's worktrees before choosing a safe task checkout.

When to use it: Before substantive work in a shared Git repository.

Example: `Use worktree-level-set to select a safe task checkout.`

Runs in Cursor and Codex through the shared installed skills, and in Claude as `/agent-harness:worktree-level-set` through the generated team plugin.

Limits and requirements: Do not remove another writer’s files.

Source: [source/skills/worktree-level-set/SKILL.md](../source/skills/worktree-level-set/SKILL.md).

Required skills: git-safe-state-auto.
