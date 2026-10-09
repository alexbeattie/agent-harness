from pathlib import Path
import hashlib
import json
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from agent_harness.config import load_config
from agent_harness.generation import skill_manifest
from tools.package_release import source_files


def generate(root: Path=ROOT) -> None:
    config=load_config(root)
    skills=skill_manifest(root)
    lines=['# Included skills','',f'This reference is generated from config/skills.json and the {len(skills)} canonical skill folders.','',
           'Run python tools/generate_docs.py after changing the source.','']
    for skill in skills:
        source=root/skill['source']/'SKILL.md'
        text=source.read_text(encoding='utf-8')
        if f"name: {skill['name']}" not in text:
            raise ValueError(f"Skill identity differs from its manifest: {source}")
        lines.extend([f"## {skill['name']}",'',skill['description'],'',f"When to use it: {skill['when'].rstrip('.')}.",'',
                      f"Example: `{skill['example']}`",'',
                      'Runs in Cursor and Codex through the shared installed skills, and in Claude as `/agent-harness:'+skill['name']+'` through the generated team plugin.','',
                      f"Limits and requirements: {skill['limits']}",'',
                      f"Source: [{skill['source']}/SKILL.md](../{skill['source']}/SKILL.md).",''])
        if skill['dependencies']:
            lines.extend(['Required skills: '+', '.join(skill['dependencies'])+'.',''])
    (root/'docs/SKILLS.md').write_text('\n'.join(lines),encoding='utf-8')
    lines=['# How the setup works','',
           'This document is generated from the maintained configuration, skill manifest and runtime files.','',
           'The source of truth is this repository. The installer generates files for each selected agent and records their hashes so a rerun can detect local edits. `-Agents` accepts cursor, codex, claude, or all (the default); repeatable `--agent` does the same in Python. A later selected install preserves files and ownership for unselected agents.','',
           '## Task flow','',
           'Cursor uses its own agent. Codex and Claude are separate programs launched in the terminal. The team skills tell each host to read its own configured model roles.','',
           'harness dispatch reads task text, validates the configuration, then either uses your chosen host or asks Codex to classify the task.','',
           'The classifier defaults to Codex. It selects Claude for architecture trade-offs, difficult debugging, high-stakes final reviews or a task that needs more than the configured context threshold.','',
           f"The configured context threshold is {config['classifier']['claude_context_threshold']:,} tokens. Quota input describes the percentage already used; trivial work stays on Codex even when quota is low.",'',
           'The classification result supplies the host, effort, brevity and a short reason. Invalid output stops dispatch. It never silently selects another model.','',
           'Task text goes to the chosen CLI on standard input. The Claude result is printed back to the terminal. The caller can return that result to Codex. The package does not keep a task ledger.','',
           'haws and htwg classify operations separately from the task classifier. Known reads can run; writes and unknown operations require an interactive yes. Redirected approval input is rejected.','',
           '## Installed files','',
           '| Location under your home folder | Purpose |','|---|---|',
           '| .agents/skills | One shared installed set discovered by Cursor and Codex. |',
           '| .agent-harness/cursor-user-rules.txt | Cursor model roles and external write rules to copy into Customize > Rules > User Rules. Generation alone does not activate them. |',
           '| .codex/agent-harness.config.toml | Named Codex profile used by harness codex. |',
           '| .agent-harness/claude-settings.json | Claude model and permission settings used by the wrapper. |',
           '| .agent-harness/claude-plugin | Claude copies of the shared skills and agent instructions. |',
           '| .agent-harness/install-state.json | Hashes of files owned by this installation. |',
           '| .agent-harness/mcp.template.json | Disabled connection templates; no credentials. |','',
           'The installer adds the package bin folder to your user PATH and removes bin folders left by earlier package copies. Each wrapper runs the package it lives in. Keep the repository at that location or rerun installation after moving it.','',
           '## Configuration','',
           'config/harness.json contains every maintained model and reasoning setting. It has these sections.','',
           '| Setting | Meaning |','|---|---|',
           '| schema_version | Configuration format understood by this package. |',
           '| hosts | Separate settings for Cursor, Codex and Claude. |',
           '| model | Main terminal model; Cursor main-chat selection stays in Cursor. |',
           '| reasoning_effort | Requested reasoning level for the main terminal model. |',
           '| reasoning_summary | Codex summary detail. |',
           '| service_tier | Codex speed/service setting. |',
           '| always_thinking_enabled | Claude thinking preference. |',
           '| roles | Exact ordered models used for each workflow role. |',
           '| features.multi_agent | Enables Codex delegation, matching the source setup. |',
           '| routes | Backend used for a model that crosses between hosts. |',
           '| independent_review | Required Claude review model for substantive Codex candidates. |',
           '| aliases | Explicit cross-host aliases, including Claude astra through Codex. |',
           '| classifier | Routing threshold, allowed efforts, forced-task effort and default quota input. |',
           '| max_parallel_agents | Maximum simultaneous agents requested by the generated instructions. |',
           '| tools | Executable names or paths for the local programs. |',
           '| connections | Disabled optional service endpoints and names of per-user token environment variables. |','',
           'Model support and account entitlement can differ by host. A configured name is not evidence that an account can use it. check.ps1 checks selected host tools and sign-in, leaves model availability pending unless -ProbeModels is passed, and requires a manual Cursor model check. AWS and TWG installation and readiness checks run only with -IncludeServices. Cross-provider roles and automatic Codex classification remain pending when their other host is unselected.','']
    for host,settings in config['hosts'].items():
        lines.extend([f'### {host} settings','', '```json',json.dumps(settings,indent=2),'```',''])
    lines.extend(['## Runtime source files','',
                  'These hashes tie this generated reference to the code files that implement the behavior.','',
                  '| File | SHA-256 |','|---|---|'])
    for path in sorted((root/'agent_harness').glob('*.py')):
        lines.append(f'| [{path.name}](../agent_harness/{path.name}) | `{hashlib.sha256(path.read_bytes()).hexdigest()}` |')
    lines.extend(['','## Limits','',
                  'The wrapper cannot identify a human securely when another process controls the same account. Direct CLI, SDK, REST and MCP calls can bypass its prompts. Enforced read-only access belongs in service permissions or an independently protected approval system.','',
                  'Native Windows installation, Cursor discovery, account sign-in, model availability and real service reads require the Windows acceptance checks. No Mac test establishes those results.',''])
    (root/'docs/HOW-IT-WORKS.md').write_text('\n'.join(lines),encoding='utf-8')
    tree = {}
    paths = {path.relative_to(root).as_posix() for path in source_files(root)} | {'docs/CONTENTS.md'}
    for path in sorted(paths):
        branch = tree
        for part in path.split('/'):
            branch = branch.setdefault(part, {})
    rows = ['# Package files', '', 'Generated from the release file selection. The ZIP also contains FILE-SHA256.json with a hash for each source file.', '', '```text', 'agent-harness/']
    def walk(branch, depth):
        for name, children in sorted(branch.items()):
            rows.append('  ' * depth + name + ('/' if children else ''))
            walk(children, depth + 1)
    walk(tree, 1)
    rows += ['```', '']
    (root/'docs/CONTENTS.md').write_text('\n'.join(rows),encoding='utf-8')


if __name__=='__main__':
    generate()
    print('Generated docs/SKILLS.md, docs/HOW-IT-WORKS.md and docs/CONTENTS.md from current source.')
