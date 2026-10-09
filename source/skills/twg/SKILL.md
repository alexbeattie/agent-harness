---
name: twg
description: Use the recipient's official TWG CLI through the harness boundary for repository reads and approved writes.
---

# TWG through the harness

This guide is independently authored from the handoff requirements. It does not contain Atlassian's restricted TWG skill material. Each recipient installs the official Windows TWG CLI and authenticates with their own account under Atlassian's terms.

Use `htwg` for Jira, Bitbucket, and related repository source reads. Discover a command with `htwg --help` and the command's help before using unfamiliar arguments. Keep a source URL and retrieval time with a result. Search or indexed context can guide investigation; verify current ticket, PR, CI, and deployment claims against their live source.

For any write, construct the complete `htwg` command with the target and intended change. The harness must display the full command and require the human to type `yes`; an agent must not supply that input. Read current state before the write and read back the saved result. A raw `twg` invocation or MCP call can bypass this cooperative prompt, so only server-side permissions can enforce the boundary against an untrusted process. Do not package auth files, tokens, or customer data.
