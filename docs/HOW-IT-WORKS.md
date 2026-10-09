# How the setup works

This document is generated from the maintained configuration, skill manifest and runtime files.

The source of truth is this repository. The installer generates files for each user and records their hashes so a rerun can detect local edits.

## Task flow

Cursor uses its own agent. Codex and Claude are separate programs launched in the terminal. The team skills tell each host to read its own configured model roles.

harness dispatch reads task text, validates the configuration, then either uses your chosen host or asks Codex to classify the task.

The classifier defaults to Codex. It selects Claude for architecture trade-offs, difficult debugging, high-stakes final reviews or a task that needs more than the configured context threshold.

The configured context threshold is 250,000 tokens. Quota input describes the percentage already used; trivial work stays on Codex even when quota is low.

The classification result supplies the host, effort, brevity and a short reason. Invalid output stops dispatch. It never silently selects another model.

Task text goes to the chosen CLI on standard input. The Claude result is printed back to the terminal. The caller can return that result to Codex. The package does not keep a task ledger.

haws and htwg classify operations separately from the task classifier. Known reads can run; writes and unknown operations require an interactive yes. Redirected approval input is rejected.

## Installed files

| Location under your home folder | Purpose |
|---|---|
| .agents/skills | One shared installed set discovered by Cursor and Codex. |
| .cursor/rules/agent-harness.mdc | Cursor model roles and external write rules. |
| .codex/agent-harness.config.toml | Named Codex profile used by harness codex. |
| .agent-harness/claude-settings.json | Claude model and permission settings used by the wrapper. |
| .agent-harness/claude-plugin | Claude copies of the shared skills and agent instructions. |
| .agent-harness/install-state.json | Hashes of files owned by this installation. |
| .agent-harness/mcp.template.json | Disabled connection templates; no credentials. |

The installer adds the package bin folder to your user PATH and removes bin folders left by earlier package copies. Each wrapper runs the package it lives in. Keep the repository at that location or rerun installation after moving it.

## Configuration

config/harness.json contains every maintained model and reasoning setting. It has these sections.

| Setting | Meaning |
|---|---|
| schema_version | Configuration format understood by this package. |
| hosts | Separate settings for Cursor, Codex and Claude. |
| model | Main terminal model; Cursor main-chat selection stays in Cursor. |
| reasoning_effort | Requested reasoning level for the main terminal model. |
| reasoning_summary | Codex summary detail. |
| service_tier | Codex speed/service setting. |
| always_thinking_enabled | Claude thinking preference. |
| roles | Exact ordered models used for each workflow role. |
| features.multi_agent | Enables Codex delegation, matching the source setup. |
| routes | Backend used for a model that crosses between hosts. |
| independent_review | Required Claude review model for substantive Codex candidates. |
| aliases | Explicit cross-host aliases, including Claude astra through Codex. |
| classifier | Routing threshold, allowed efforts, forced-task effort and default quota input. |
| max_parallel_agents | Maximum simultaneous agents requested by the generated instructions. |
| tools | Executable names or paths for the local programs. |
| connections | Disabled optional service endpoints and names of per-user token environment variables. |

Model support and account entitlement can differ by host. A configured name is not evidence that an account can use it. check.ps1 distinguishes tested values from checks that still need the host UI or an authenticated probe.

### codex settings

```json
{
  "model": "gpt-6-astra",
  "reasoning_effort": "ultra",
  "reasoning_summary": "concise",
  "service_tier": "ultrafast",
  "roles": {
    "feature, refactoring": [
      "gpt-6-sol"
    ],
    "bug-fix": [
      "gpt-6-sol"
    ],
    "perf-issue": [
      "gpt-6-sol"
    ],
    "hillclimb": [
      "gpt-6-sol"
    ],
    "judgment and prose": [
      "gpt-6-sol"
    ],
    "strongest judgment": [
      "gpt-6-sol"
    ],
    "how explorer": [
      "gpt-5.6-terra"
    ],
    "how explainer": [
      "gpt-6-sol"
    ],
    "how critics": [
      "gpt-6-astra",
      "gpt-6-sol",
      "gpt-6-luna",
      "claude-opus-5-5",
      "claude-fable-5-1"
    ],
    "why investigators": [
      "gpt-5.6-terra"
    ],
    "why synthesizer": [
      "gpt-6-sol"
    ],
    "reflect tooling": [
      "gpt-6-luna"
    ],
    "reflect judgment, divergent, synthesizer": [
      "gpt-6-sol"
    ],
    "arena runners": [
      "gpt-6-astra",
      "gpt-6-sol",
      "gpt-6-luna",
      "claude-opus-5-5",
      "claude-fable-5-1"
    ],
    "arena cross-judge pool": [
      "gpt-6-astra",
      "gpt-6-sol",
      "gpt-6-luna",
      "claude-opus-5-5",
      "claude-fable-5-1"
    ],
    "swarm workers": [
      "gpt-6-luna"
    ],
    "architect runners": [
      "gpt-6-astra",
      "gpt-6-sol",
      "gpt-6-luna",
      "claude-opus-5-5",
      "claude-fable-5-1"
    ],
    "interrogate reviewers": [
      "gpt-6-astra",
      "gpt-6-sol",
      "gpt-6-luna",
      "claude-opus-5-5",
      "claude-fable-5-1"
    ]
  },
  "features": {
    "multi_agent": true
  }
}
```

### cursor settings

```json
{
  "roles": {
    "feature, refactoring": [
      "gpt-5.6-sol-high"
    ],
    "bug-fix": [
      "gpt-5.6-sol-high"
    ],
    "perf-issue": [
      "gpt-5.6-sol-high"
    ],
    "hillclimb": [
      "gpt-5.6-sol-high"
    ],
    "judgment and prose": [
      "claude-fable-5-1-thinking-high"
    ],
    "hardest tasks": [
      "claude-fable-5-1-thinking-high"
    ],
    "how explorer": [
      "gpt-5.6-sol-high"
    ],
    "how explainer": [
      "claude-fable-5-1-thinking-high"
    ],
    "how critics": [
      "claude-fable-5-1-thinking-high",
      "gpt-5.6-sol-high",
      "claude-opus-5-thinking-high"
    ],
    "why investigators": [
      "gpt-5.6-sol-high"
    ],
    "why synthesizer": [
      "claude-fable-5-1-thinking-high"
    ],
    "reflect tooling": [
      "gpt-5.6-sol-high"
    ],
    "reflect judgment, divergent, synthesizer": [
      "claude-fable-5-1-thinking-high"
    ],
    "arena runners": [
      "claude-fable-5-1-thinking-high",
      "gpt-5.6-sol-high",
      "claude-opus-5-thinking-high"
    ],
    "arena cross-judge pool": [
      "claude-fable-5-1-thinking-high",
      "gpt-5.6-sol-high",
      "claude-opus-5-thinking-high"
    ],
    "swarm workers": [
      "gpt-5.6-sol-high"
    ],
    "architect runners": [
      "claude-fable-5-1-thinking-high",
      "gpt-5.6-sol-high",
      "claude-opus-5-thinking-high"
    ],
    "interrogate reviewers": [
      "claude-fable-5-1-thinking-high",
      "gpt-5.6-sol-high",
      "claude-opus-5-thinking-high"
    ]
  }
}
```

### claude settings

```json
{
  "model": "fable[1m]",
  "reasoning_effort": "xhigh",
  "always_thinking_enabled": true,
  "roles": {
    "feature, refactoring": [
      "sonnet"
    ],
    "bug-fix": [
      "opus"
    ],
    "perf-issue": [
      "opus"
    ],
    "hillclimb": [
      "opus"
    ],
    "judgment and prose": [
      "fable"
    ],
    "hardest tasks": [
      "opus"
    ],
    "how explorer": [
      "sonnet"
    ],
    "how explainer": [
      "fable"
    ],
    "how critics": [
      "fable",
      "opus",
      "sonnet",
      "astra"
    ],
    "why investigators": [
      "sonnet"
    ],
    "why synthesizer": [
      "fable"
    ],
    "reflect tooling": [
      "sonnet"
    ],
    "reflect judgment, divergent, synthesizer": [
      "fable"
    ],
    "arena runners": [
      "fable",
      "opus",
      "sonnet",
      "astra"
    ],
    "arena cross-judge pool": [
      "opus",
      "fable",
      "sonnet",
      "astra"
    ],
    "swarm workers": [
      "sonnet"
    ],
    "architect runners": [
      "fable",
      "opus",
      "sonnet",
      "astra"
    ],
    "interrogate reviewers": [
      "fable",
      "opus",
      "sonnet",
      "astra"
    ]
  }
}
```

## Runtime source files

These hashes tie this generated reference to the code files that implement the behavior.

| File | SHA-256 |
|---|---|
| [checks.py](../agent_harness/checks.py) | `b583d5d7832d4950e633ec3ea30aabfa503cca86049e44ebd958633e4613e746` |
| [config.py](../agent_harness/config.py) | `b3b8390cc1b36062247692b93937fe3af8fd2361fa3d417805e48728fbd581a3` |
| [dispatch.py](../agent_harness/dispatch.py) | `fc0d5f32e63b96f2acb8aff24a15eabe7e6680e539bdbba5947f9c2964144386` |
| [generation.py](../agent_harness/generation.py) | `19a6b03650732535c814ca752aa9b99b12a5b872d2a1c2d9eb4be0fde66cedc8` |
| [guard.py](../agent_harness/guard.py) | `2906fa34cd5b037e0c09dd30a6d32fc1b8db3afcff3b191cd32f5d7677e3d3f7` |
| [model_catalog.py](../agent_harness/model_catalog.py) | `09045818cdfa71010299326cef365e2830046e68d10500b44c100b995afdf6db` |
| [process.py](../agent_harness/process.py) | `4485ddecfbf3df97337e7a0542e1ade9b1762a148fd16622d25d5b5aa21cf407` |

## Limits

The wrapper cannot identify a human securely when another process controls the same account. Direct CLI, SDK, REST and MCP calls can bypass its prompts. Enforced read-only access belongs in service permissions or an independently protected approval system.

Native Windows installation, Cursor discovery, account sign-in, model availability and real service reads require the Windows acceptance checks. No Mac test establishes those results.
