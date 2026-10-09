# Maintaining this package

Read docs/OWNERS.md and docs/HOW-IT-WORKS.md before changing the package.

Keep one canonical source per skill under source/skills. Generate installed files with harness.py; never edit installed copies as the source of truth.

Preserve each host's model choices in config/harness.json. Do not add a fallback when a requested model is unavailable. Do not copy credentials, user instructions, personal notes, histories or customer data into this repository.

Use Python's standard library and native PowerShell. Do not introduce a Bash, tmux or WSL requirement. Keep runtime modules below 400 lines by separating different responsibilities.

Every AWS or TWG write must print its exact command and require a new explicit yes in an interactive terminal. Refuse redirected input. These are cooperative guards; do not claim that they prevent raw CLI, SDK, REST or MCP bypasses. Do not weaken tests to hide this limit.

Start behavior changes with a failing test. Run python -m unittest discover -s tests -v, the PowerShell tests and tools/package_release.py --check before handing off. Verify installer behavior on a fresh Windows account before claiming Windows acceptance.

Never publish, push, merge, deploy or send messages unless the user requests that action. Package building is a local operation.
