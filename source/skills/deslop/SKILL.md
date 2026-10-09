---
name: deslop
description: Remove speculative code and needless structure from a candidate without changing behavior.
---

# Deslop

Read the changed behavior and diff. Remove unused abstractions, generic wrappers with one caller, redundant options, defensive branches for impossible states, and duplicate tests that mirror implementation. Keep error handling tied to a real boundary. Prefer the repository's existing pattern when it stays clear. Run the focused behavior checks after edits. Don't turn a scope cleanup into a new feature or conceal an unresolved failure.
