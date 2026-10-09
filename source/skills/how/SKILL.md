---
name: how
description: Explain how a code path works using traced evidence and an audience-sized mental model.
---

# How

## Assess

For a small, local question, inspect the path and explain directly. For a cross-module question, partition by entrypoint, data shape, ownership boundary, or output. Assign read-only explorers using the `how explorer` role in [host routing](../repo-pstack-mode/references/host-routing.md).

## Explore

Give each explorer a narrow question, file or subsystem scope, and expected evidence: symbols, callers, data flow, errors, and tests. Ask for file/line pointers and uncertainties. Explorers must not edit. Consolidate overlapping evidence and resolve contradictions from source.

## Explain

Use the `how explainer` role for synthesis when the split is complex. Present the entrypoint, sequence, state transitions, external effects, and failure path. Explain at the level needed to work safely on the subsystem. Cite source locations; separate observed behavior from inference. Do not paste annotated code or assert runtime behavior from reading alone.
