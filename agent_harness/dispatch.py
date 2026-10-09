from __future__ import annotations

import json
import re
import sys
import tempfile
from pathlib import Path
from typing import Any

from .config import resolve_role
from .process import resolve_executable, run_process, run_process_output

_EFFORTS = {'low', 'high', 'xhigh'}
_SAFE_MODEL = re.compile(r'^[A-Za-z0-9][A-Za-z0-9_.:\[\]-]*$')


def _root() -> Path:
    return Path(__file__).resolve().parents[1]


def _valid_result(value: Any, configured_efforts: list[str]) -> bool:
    return (
        isinstance(value, dict)
        and set(value) == {'model', 'effort', 'brevity', 'reason'}
        and value.get('model') in {'codex', 'claude'}
        and value.get('effort') in _EFFORTS
        and value.get('effort') in configured_efforts
        and isinstance(value.get('brevity'), bool)
        and isinstance(value.get('reason'), str)
        and len(value['reason']) <= 200
    )


def _classifier(config: dict, task: str, quota_used: int | float | None) -> dict | None:
    settings = config.get('classifier')
    if not isinstance(settings, dict):
        print('Classifier configuration is missing; no host was selected.', file=sys.stderr)
        return None
    efforts = settings.get('effort_levels')
    forced = settings.get('forced_effort')
    if not isinstance(efforts, list) or not efforts or any(item not in _EFFORTS for item in efforts) or forced not in efforts:
        print('Classifier effort settings are invalid; no host was selected.', file=sys.stderr)
        return None
    quota = settings.get('quota_used_percent', 0) if quota_used is None else quota_used
    if not isinstance(quota, (int, float)) or isinstance(quota, bool) or not 0 <= quota <= 100:
        print('Quota must be a number from 0 to 100.', file=sys.stderr)
        return None
    codex = config.get('hosts', {}).get('codex', {})
    tool = config.get('tools', {}).get('codex')
    model = codex.get('model')
    effort = codex.get('reasoning_effort')
    tier = codex.get('service_tier')
    if not all(isinstance(value, str) and value for value in (tool, model, effort, tier)):
        print('Codex classifier model, effort, service tier and executable must all be configured.', file=sys.stderr)
        return None
    asset = _root() / 'assets/classifier.txt'
    schema = _root() / 'assets/classifier-schema.json'
    try:
        instructions = asset.read_text(encoding='utf-8')
        json.loads(schema.read_text(encoding='utf-8'))
    except (OSError, ValueError) as error:
        print(f'Classifier assets are missing or invalid: {error}', file=sys.stderr)
        return None
    context = {
        'classifier': {
            'default_host': settings.get('default_host', 'codex'),
            'claude_context_threshold': settings.get('claude_context_threshold', 250000),
            'forced_effort': forced,
            'effort_levels': efforts,
            'quota_used_percent': quota,
        },
        'task': task,
    }
    prompt = instructions + json.dumps(context, ensure_ascii=False)
    with tempfile.TemporaryDirectory(prefix='agent-harness-classify-') as temp_dir:
        output = Path(temp_dir) / 'classification.json'
        argv = [
            resolve_executable(tool), 'exec', '--ephemeral', '--profile', 'agent-harness', '-s', 'read-only',
            '--output-schema', str(schema), '-o', str(output), '--model', model,
            '-c', f'model_reasoning_effort={json.dumps(effort)}', '-c', f'service_tier={json.dumps(tier)}', '-',
        ]
        result, _ = run_process_output(argv, stdin_text=prompt)
        if result != 0:
            print(f'Codex classifier failed with exit status {result}; no task was dispatched.', file=sys.stderr)
            return None
        try:
            parsed = json.loads(output.read_text(encoding='utf-8'))
        except (OSError, ValueError) as error:
            print(f'Classifier output was missing or invalid JSON: {error}; no task was dispatched.', file=sys.stderr)
            return None
        if not _valid_result(parsed, efforts):
            print('Classifier output did not match the configured schema; no task was dispatched.', file=sys.stderr)
            return None
        if parsed['model'] == 'claude' and parsed['effort'] == 'low':
            parsed['effort'] = forced
        return parsed


def _configured_models(config: dict) -> set[str]:
    models: set[str] = set()
    for host in config.get('hosts', {}).values():
        if isinstance(host, dict):
            if isinstance(host.get('model'), str):
                models.add(host['model'])
            for values in host.get('roles', {}).values():
                if isinstance(values, list):
                    models.update(value for value in values if isinstance(value, str))
    models.update(config.get('routes', {}).keys())
    for routes in config.get('aliases', {}).values():
        if isinstance(routes, dict):
            models.update(routes.keys())
    return models


def _resolve_host_model(config: dict, model: str | None, host: str | None, role: str | None) -> tuple[str, str] | None:
    if model is not None:
        if not isinstance(model, str) or not _SAFE_MODEL.fullmatch(model):
            print('The requested model contains unsupported characters.', file=sys.stderr)
            return None
        if model not in _configured_models(config):
            print(f'Model {model!r} is not present in config/harness.json hosts, routes or aliases; no fallback is allowed.', file=sys.stderr)
            return None
        alias_route = _alias_route(config, model)
        if alias_route:
            backend, target = alias_route
            if host and host != backend:
                print(f'Model {model!r} routes to {backend}, not {host}.', file=sys.stderr)
                return None
            return backend, target
        routed_host = config.get('routes', {}).get(model)
        selected_host = host or routed_host
        if selected_host is None:
            for candidate, settings in config.get('hosts', {}).items():
                if model == settings.get('model') or any(model in values for values in settings.get('roles', {}).values() if isinstance(values, list)):
                    selected_host = candidate
                    break
        if selected_host not in {'codex', 'claude'} or (routed_host and selected_host != routed_host):
            print(f'Model {model!r} does not resolve to a supported host.', file=sys.stderr)
            return None
        return selected_host, model
    if host not in {'codex', 'claude'}:
        print(f'Unknown host {host!r}; use codex or claude.', file=sys.stderr)
        return None
    try:
        if role:
            role_models = resolve_role(config, host, role)
            selected_model = role_models[0]
        else:
            selected_model = config['hosts'][host]['model']
    except (KeyError, ValueError, IndexError) as error:
        print(f'Cannot resolve config/harness.json hosts.{host}.roles.{role or "main"}: {error}', file=sys.stderr)
        return None
    if not isinstance(selected_model, str) or not _SAFE_MODEL.fullmatch(selected_model):
        print(f'Invalid configured model for host {host}; no fallback is allowed.', file=sys.stderr)
        return None
    alias_route = _alias_route(config, selected_model)
    if alias_route:
        return alias_route
    return host, selected_model


def _alias_route(config: dict, model: str) -> tuple[str, str] | None:
    for aliases in config.get('aliases', {}).values():
        alias = aliases.get(model) if isinstance(aliases, dict) else None
        if not isinstance(alias, dict):
            continue
        backend = alias.get('backend')
        target = alias.get('model')
        if backend in {'codex', 'claude'} and isinstance(target, str) and target in _configured_models(config):
            return backend, target
    return None


def _task_argv(config: dict, host: str, model: str, effort: str, read_only: bool) -> list[str] | None:
    executable = config.get('tools', {}).get(host)
    settings = config.get('hosts', {}).get(host, {})
    if not isinstance(executable, str) or not executable:
        print(f'Configure tools.{host} before dispatch.', file=sys.stderr)
        return None
    if host == 'claude':
        home = Path.home()
        settings_path = home / '.agent-harness' / 'claude-settings.json'
        plugin_dir = home / '.agent-harness' / 'claude-plugin'
        argv = [resolve_executable(executable), '-p', '--model', model, '--effort', effort, '--output-format', 'json', '--permission-mode', 'default', '--settings', str(settings_path), '--plugin-dir', str(plugin_dir)]
        if read_only:
            argv.extend(['--tools', 'Read,Grep,Glob', '--strict-mcp-config'])
        return argv
    argv = [resolve_executable(executable), 'exec', '--ephemeral', '--profile', 'agent-harness']
    if read_only:
        argv.extend(['-s', 'read-only'])
    argv.extend(['--model', model])
    configured_effort = settings.get('reasoning_effort')
    tier = settings.get('service_tier')
    if not isinstance(configured_effort, str) or not isinstance(tier, str):
        print('Codex reasoning effort and service tier must be configured.', file=sys.stderr)
        return None
    argv.extend(['-c', f'model_reasoning_effort={json.dumps(configured_effort)}', '-c', f'service_tier={json.dumps(tier)}', '-'])
    return argv


def run_dispatch(
    config: dict,
    task: str,
    host: str | None = None,
    classify_only: bool = False,
    quota_used: int | float | None = None,
    read_only: bool = False,
    role: str | None = None,
    model: str | None = None,
) -> int:
    """Classify or dispatch one task to the configured exact model."""
    if not isinstance(task, str) or not task.strip():
        print('Task text is required.', file=sys.stderr)
        return 2
    classification = None
    if model is None and host is None:
        classification = _classifier(config, task, quota_used)
        if classification is None:
            return 2
        if classify_only:
            print(json.dumps(classification, ensure_ascii=False))
            return 0
        host = classification['model']
    elif classify_only:
        print('classify-only cannot be combined with an explicit host or model.', file=sys.stderr)
        return 2
    selected = _resolve_host_model(config, model, host, role)
    if selected is None:
        return 2
    selected_host, selected_model = selected
    effort = classification['effort'] if classification and selected_host == 'claude' else config.get('hosts', {}).get(selected_host, {}).get('reasoning_effort')
    if not isinstance(effort, str) or effort not in _EFFORTS | {'none', 'minimal', 'medium', 'max', 'ultra'}:
        print(f'Invalid reasoning effort for {selected_host}; no fallback is allowed.', file=sys.stderr)
        return 2
    argv = _task_argv(config, selected_host, selected_model, effort, read_only)
    if argv is None:
        return 2
    if selected_host == 'claude':
        claude_task = ('Be terse. Answer with the minimum. ' + task) if classification and classification.get('brevity') else task
        result_code, output = run_process_output(argv, stdin_text=claude_task)
        if result_code != 0:
            print(f'Claude failed with exit status {result_code}.', file=sys.stderr)
            return result_code
        try:
            response = json.loads(output)
        except ValueError:
            print('Claude returned invalid JSON; the task is incomplete.', file=sys.stderr)
            return 2
        if not isinstance(response, dict):
            print('Claude returned an unexpected response; the task is incomplete.', file=sys.stderr)
            return 2
        usage = response.get('modelUsage')
        if not isinstance(response.get('is_error'), bool) or not isinstance(usage, dict) or not usage:
            print('Claude response omitted is_error or modelUsage; the task is unverified.', file=sys.stderr)
            return 2
        if response['is_error']:
            print('Claude reported an error; the task is incomplete.', file=sys.stderr)
            return 2
        if 'result' not in response:
            print('Claude response omitted result; the task is incomplete.', file=sys.stderr)
            return 2
        identity = observed_model_identity(usage, selected_model)
        if identity is None:
            observed = ', '.join(str(item) for item in usage)
            print(f'Claude reported modelUsage {observed!r}, which does not verify requested model {selected_model!r}; the task is unverified.', file=sys.stderr)
            return 2
        print(f'Claude reported model {identity} for requested {selected_model}')
        result = response.get('result')
        if not isinstance(result, str) or not result.strip():
            print('Claude response omitted a usable result; the task is incomplete.', file=sys.stderr)
            return 2
        print(result)
        return 0
    return run_process(argv, stdin_text=task)


def observed_model_identity(usage: Any, requested: str) -> str | None:
    """Return the verified model identity: the exact key for a claude-* ID, or the single reported identity for an alias."""
    if not isinstance(usage, dict):
        return None
    identities = {name for name in usage if isinstance(name, str) and name}
    if requested in identities:
        return requested
    if requested.startswith('claude-') or len(identities) != 1:
        return None
    return next(iter(identities))


def start_interactive(config: dict, host: str) -> int:
    """Start a configured interactive CLI with the generated project profile."""
    if host == 'codex':
        executable = config.get('tools', {}).get('codex')
        if not isinstance(executable, str) or not executable:
            print('Configure tools.codex before starting Codex.', file=sys.stderr)
            return 2
        argv = [resolve_executable(executable), '--profile', 'agent-harness']
    elif host == 'claude':
        executable = config.get('tools', {}).get('claude')
        if not isinstance(executable, str) or not executable:
            print('Configure tools.claude before starting Claude.', file=sys.stderr)
            return 2
        main_model = config.get('hosts', {}).get('claude', {}).get('model')
        if not isinstance(main_model, str) or not _SAFE_MODEL.fullmatch(main_model):
            print('Configure hosts.claude.model before starting Claude; no fallback is allowed.', file=sys.stderr)
            return 2
        home = Path.home()
        settings = home / '.agent-harness' / 'claude-settings.json'
        plugin_dir = home / '.agent-harness' / 'claude-plugin'
        argv = [
            resolve_executable(executable), '--model', main_model, '--settings', str(settings), '--plugin-dir', str(plugin_dir),
            '--permission-mode', 'default',
        ]
    else:
        print('Interactive host must be codex or claude.', file=sys.stderr)
        return 2
    return run_process(argv)
