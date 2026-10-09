---
name: twg-jira
description: Read live Jira issue state and make only explicitly approved changes through htwg.
---

# Jira with htwg

Use [TWG through the harness](../twg/SKILL.md). Look up each supplied key in live Jira. Before proposing a new issue, search matching titles, requirements, and related issues, including closed items. Read the issue description, recent comments, links, status, and owner. An indexed hit is context; a failed live lookup leaves the check incomplete.

For a requested update, preserve accepted scope, attachments, visibility, and ownership. Draft concise engineering prose that states the concrete change, evidence, and pending gate. Read the exact draft before publication. For a write, show the full `htwg` command and target, obtain the human's explicit `yes` through the wrapper, and read back the rendered issue. Recheck duplicates immediately before any approved create. A status correction needs live evidence and an available transition; do not infer deployment or acceptance from a merged PR.
