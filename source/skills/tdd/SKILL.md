---
name: tdd
description: Fix behavior test first where the active repository requires TDD.
---

# TDD

Reproduce the behavior with the smallest real input. Add a test that fails for the observed reason, then run it and record that failure. Change production code only after the failure is understood. Run the narrow test again, then related tests and repository-required verification. Test through a public behavior boundary; avoid assertions on implementation details.

If a failing automated test is impractical, explain why and capture a repeatable browser or CLI reproduction before editing. Do not invent a red phase. For UI work, check the built application where required and inspect the rendered state. Keep the test focused on the behavior that was broken. See [Test Behavior, Not Implementation](../principle-test-behavior-not-implementation/SKILL.md).
