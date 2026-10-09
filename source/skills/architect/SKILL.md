---
name: architect
description: Sketch a change's types, signatures, and ownership boundaries before implementing it.
---

# Architect

## Ground

Use [how](../how/SKILL.md) to trace every system the change touches. Use [why](../why/SKILL.md) if existing ownership has a historical reason. Define behavior, constraints, and failure cases before choosing modules.

## Sketch

Run [arena](../arena/SKILL.md) with the exact configured `architect runners` from [host routing](../repo-pstack-mode/references/host-routing.md). Queue panel members beyond the concurrency limit; account for every configured seat. Give all runners the same problem, grounded evidence, and rubric. Keep outputs separate. Require at least two structurally distinct whole-shape sketches before synthesis, even if the first looks good. Each sketch names module boundaries, types, signatures, data flow, failure handling, and pseudocode with no production implementation.

Screen each sketch for hidden shared state, duplicated public APIs, missing ownership, and a change that appears local but would break another layer. Compare viable candidates on behavior, interface depth, change locality, and the ease of making the next change safely. After all runners finish, use the configured `arena cross-judge pool` for one read-only cross-judge, preferably a different model family; the parent independently reads the candidates. Record the chosen shape and what it borrows from another sketch. If fewer than two distinct sketches or a required panel seat is available, report the design comparison incomplete rather than manufacturing a second view.

## Implement

Choose a coherent sketch. A checkpoint is needed only when the user requested one. Map its interfaces to files, then implement in verifiable units. When implementation needs an interface or outcome change, reconcile it in the saved sketch before the next worker depends on the old contract. Repeated structural friction means the design is wrong: re-ground and sketch again. Review the final diff against the current sketch and repository rules. Record the chosen boundary and any unresolved tradeoff.
