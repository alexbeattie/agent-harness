from __future__ import annotations
import hashlib
import json
import os
import re
import tempfile
from pathlib import Path
from .config import load_config, read_version

class GenerationError(ValueError):
    pass

AGENTS = ('cursor', 'codex', 'claude')


def selected_agents(agents: tuple[str, ...] | list[str] | None = None) -> tuple[str, ...]:
    names = tuple(agents or ('all',))
    if 'all' in names:
        if len(names) != 1:
            raise GenerationError('Do not mix all with named agents.')
        return AGENTS
    if not names or any(name not in AGENTS for name in names):
        raise GenerationError('Choose cursor, codex, claude, or all.')
    return tuple(name for name in AGENTS if name in names)


def _owners(name: str) -> set[str]:
    if name.startswith('.agents/skills/'):
        return {'cursor', 'codex'}
    if name.startswith('.codex/') or name.endswith('/codex.toml.example'):
        return {'codex'}
    if name.startswith('.cursor/') or 'cursor' in name:
        return {'cursor'}
    if name.startswith('.agent-harness/claude-') or '/claude-plugin/' in name or name.endswith('/claude.json.example'):
        return {'claude'}
    return set(AGENTS)


def skill_manifest(root: Path) -> list[dict]:
    try:
        skills = json.loads((root/'config/skills.json').read_text(encoding='utf-8'))['skills']
    except (OSError, ValueError, KeyError) as error:
        raise GenerationError(f'Cannot read config/skills.json: {error}') from error
    names = [item.get('name') for item in skills]
    if any(not isinstance(name,str) or not re.fullmatch(r'[a-z0-9][a-z0-9-]*',name) for name in names):
        raise GenerationError('Every skill needs a lowercase folder name without path separators.')
    if len(set(names)) != len(names):
        raise GenerationError('Duplicate skill names in config/skills.json.')
    for item in skills:
        if item.get('source') != f"source/skills/{item['name']}":
            raise GenerationError(f"Unexpected source path for {item['name']}.")
        missing = set(item.get('dependencies', [])) - set(names)
        if missing:
            raise GenerationError(f"Missing dependencies for {item['name']}: {', '.join(sorted(missing))}")
    return skills


def _hash(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _no_links(path: Path, boundary: Path) -> None:
    current = path
    while True:
        if current.is_symlink() or (hasattr(current, 'is_junction') and current.is_junction()):
            raise GenerationError(f'Refusing symlink in managed path: {current}')
        if current == boundary or current == current.parent:
            return
        current = current.parent


def _model_routing(config: dict) -> str:
    text = ['# Host routing', '', 'Read the section for the host running this task. Never substitute a model silently.', '',
            'Use the host subagent tool only when it accepts the configured model. Discover its actual schema first. If a required tool or model is unavailable, stop that role and name the configuration setting to change.', '',
            'For a follow-up, resume the existing agent with its task context. After interrupting an agent, start a fresh agent and pass the current task, decisions and file ownership explicitly.', '',
            f"Run at most {config['max_parallel_agents']} agents at once. Queue remaining panel members; do not drop them.", '',
            '## Commands', '',
            'Use `harness dispatch --host codex --task-file task.txt` or `harness dispatch --host claude --task-file task.txt` for a terminal handoff. Use `--model` only with a model present in the central configuration. Use `--read-only` for reviews. Keep task files local and out of source control.', '',
            'Use `haws` for AWS and `htwg` for TWG. Every write needs fresh approval for the exact command. Do not use raw CLI, REST, SDK or MCP writes to bypass the prompt. If the wrapper reports noninteractive input, show the user its Will run and Rerun yourself lines, tell them to paste the Rerun yourself line in a separate PowerShell terminal, and wait for the result. Never supply yes on the user\'s behalf.', '',
            'Wrapper prompts are workflow guardrails. They do not restrict another process running with the same credentials. Use separate read-only credentials and server-side permissions when an enforced security boundary is required.', '']
    review = config.get('independent_review', {})
    text += ['## Independent review', '', f"Substantive Codex candidates require a read-only review through `{review.get('host')}` using `{review.get('model')}`. Wait for the result and verify the returned model identity. If unavailable, report the review as incomplete; do not credit another backend.", '']
    for host,settings in config['hosts'].items():
        text += [f'## {host}', '']
        if 'model' in settings:
            text += [f"Main model: `{settings['model']}`. Reasoning: `{settings.get('reasoning_effort','')}`.", '']
        text.extend(f"- {role}: {', '.join(f'`{model}`' for model in models)}" for role,models in settings['roles'].items())
        text.append('')
    text += ['Claude model IDs in a Codex panel run through the Claude CLI, not the native Codex model argument. In a Claude panel, `astra` runs through Codex using the configured alias. Preserve panel order and verify returned model identity where the CLI reports it.', '',
             'Optional context and assistant service templates stay disabled until each user receives their own endpoint and token from the service administrator. Never claim a configured connector is authenticated without a successful read.', '']
    return '\n'.join(text)


def desired_files(root: Path, config: dict) -> dict[str, bytes]:
    desired = {}
    for skill in skill_manifest(root):
        source = root / skill['source']
        _no_links(source, root)
        if not (source/'SKILL.md').is_file():
            raise GenerationError(f"Missing SKILL.md for {skill['name']}.")
        for file in sorted(source.rglob('*')):
            _no_links(file, root)
            if not file.is_file():
                continue
            relative = file.relative_to(source).as_posix()
            data = file.read_bytes()
            for base in ('.agents/skills', '.agent-harness/claude-plugin/skills'):
                desired[f"{base}/{skill['name']}/{relative}"] = data
    routing = _model_routing(config).encode()
    for base in ('.agents/skills', '.agent-harness/claude-plugin/skills'):
        desired[f'{base}/repo-pstack-mode/references/host-routing.md'] = routing
    agent_root = root/'source/agents'
    if agent_root.exists():
        for file in sorted(agent_root.glob('*.md')):
            _no_links(file, root)
            desired[f'.agent-harness/claude-plugin/agents/{file.name}'] = file.read_bytes()
            for base in ('.agents/skills', '.agent-harness/claude-plugin/skills'):
                desired[f'{base}/repo-pstack-mode/references/agents/{file.name}'] = file.read_bytes()
    desired['.agent-harness/claude-plugin/.claude-plugin/plugin.json'] = _json({'name':'agent-harness','version':read_version(root),'description':'Shared workflows with per-user model configuration.'})
    codex = config['hosts']['codex']
    profile = '\n'.join([
        '# Generated by agent harness. Edit config/harness.json in the source repository.',
        f'model = {json.dumps(codex["model"])}',
        f'model_reasoning_effort = {json.dumps(codex["reasoning_effort"])}',
        f'model_reasoning_summary = {json.dumps(codex["reasoning_summary"])}',
        f'service_tier = {json.dumps(codex["service_tier"])}',
        'approval_policy = "on-request"', 'sandbox_mode = "workspace-write"', '',
        '[features]', f'multi_agent = {str(codex["features"]["multi_agent"]).lower()}', ''])
    desired['.codex/agent-harness.config.toml'] = profile.encode()
    claude = config['hosts']['claude']
    desired['.agent-harness/claude-settings.json'] = _json({'model':claude['model'],'effortLevel':claude['reasoning_effort'],'alwaysThinkingEnabled':claude['always_thinking_enabled'],'permissions':{'defaultMode':'default'}})
    cursor = ['# Agent harness','',
              'Use the installed repo-pstack-mode skill and its host-routing.md reference. Preserve the active repository rules. Resume follow-ups; start a fresh agent after an interrupt. Never silently fall back from a configured model. Use haws and htwg for external commands; never supply approval or bypass them through raw CLI, REST, SDK or MCP writes.','']
    cursor += [f"{role}: {', '.join(models)}" for role,models in config['hosts']['cursor']['roles'].items()]
    desired['.agent-harness/cursor-user-rules.txt'] = ('\n'.join(cursor)+'\n').encode()
    desired['.agent-harness/mcp.template.json'] = _json({'_instructions':'Disabled templates. Get your own endpoint and token from the service administrator. Do not commit values. Follow docs/INSTALL.md before enabling.','connections':config['connections']})
    json_servers = {name: {'url': '', 'headers': {'Authorization': ''}} for name in config['connections']}
    desired['.agent-harness/mcp/cursor.json.example'] = _json({'mcpServers': json_servers})
    desired['.agent-harness/mcp/claude.json.example'] = _json({'mcpServers': {name: {'type': 'http', **server} for name, server in json_servers.items()}})
    toml = ['# Get your own URL and token from the service administrator.', '# Set the named token environment variable; never paste a token here.', '']
    for name, connection in config['connections'].items():
        if not re.fullmatch(r'[a-z][a-z0-9_-]*', name):
            raise GenerationError('Connection names must use lowercase letters, numbers, underscores or hyphens.')
        toml += [f'[mcp_servers.{name}]', 'enabled = false', 'url = ""', f'bearer_token_env_var = {json.dumps(connection["token_env"])}', '']
    desired['.agent-harness/mcp/codex.toml.example'] = '\n'.join(toml).encode()
    return desired


def _json(value: object) -> bytes:
    return (json.dumps(value, indent=2,ensure_ascii=False)+'\n').encode()


def generate(root: Path, target_home: Path, check: bool = False,
             agents: tuple[str, ...] | list[str] | None = None) -> dict:
    root = root.resolve()
    target_home = target_home.absolute()
    selected = set(selected_agents(agents))
    full_desired = desired_files(root, load_config(root))
    desired = {name: data for name, data in full_desired.items() if _owners(name) & selected}
    state_path = target_home/'.agent-harness/install-state.json'
    _no_links(state_path, target_home)
    try:
        old = json.loads(state_path.read_text(encoding='utf-8')).get('files', {}) if state_path.exists() else {}
    except (OSError,ValueError) as error:
        raise GenerationError(f'Cannot read installation state: {error}') from error
    retired = sorted(name for name in set(old)-set(full_desired) if _owners(name) & selected
                     and ((target_home/name).exists() or (target_home/name).is_symlink()))
    changed = []
    conflicts = []
    for name, data in desired.items():
        path = target_home/name
        _no_links(path, target_home)
        if path.exists():
            if not path.is_file():
                conflicts.append(name);continue
            current = path.read_bytes()
            if current == data:
                continue
            if old.get(name) != _hash(current):
                conflicts.append(name);continue
        changed.append(name)
    if conflicts:
        raise GenerationError('Installation conflict; preserve or move these files before retrying: '+', '.join(conflicts))
    if check:
        return {'changed':len(changed),'pending':changed,'files':len(desired),'retained_obsolete':retired}
    for name in changed:
        path = target_home/name
        path.parent.mkdir(parents=True,exist_ok=True)
        _no_links(path,target_home)
        _atomic(path,desired[name])
    preserved = {name: digest for name, digest in old.items() if name not in desired and
                 ((target_home/name).exists() or (target_home/name).is_symlink())}
    state = _json({'schema_version':1,'files':{**preserved, **{name:_hash(data) for name,data in desired.items()}}})
    state_path.parent.mkdir(parents=True,exist_ok=True)
    if not state_path.exists() or state_path.read_bytes()!=state:
        _atomic(state_path,state)
    return {'changed':len(changed),'files':len(desired),'retained_obsolete':retired}


def _atomic(path: Path, data: bytes) -> None:
    handle, temporary = tempfile.mkstemp(prefix='.agent-',dir=path.parent)
    try:
        with os.fdopen(handle,'wb') as file:
            file.write(data)
            file.flush()
            os.fsync(file.fileno())
        os.replace(temporary,path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)
