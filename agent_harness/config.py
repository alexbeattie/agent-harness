from __future__ import annotations
import json
import re
from pathlib import Path

class ConfigError(ValueError):
    pass


def load_config(root: Path | None = None) -> dict:
    root = root or Path(__file__).resolve().parents[1]
    try:
        config = json.loads((root / 'config/harness.json').read_text(encoding='utf-8'))
    except (OSError, ValueError) as error:
        raise ConfigError(f'Cannot read config/harness.json: {error}') from error
    if config.get('schema_version') != 1:
        raise ConfigError('config/harness.json schema_version must be 1.')
    for host in ('codex', 'cursor', 'claude'):
        settings = config.get('hosts', {}).get(host)
        if not isinstance(settings, dict) or not isinstance(settings.get('roles'), dict):
            raise ConfigError(f'Set hosts.{host}.roles in config/harness.json.')
        if host != 'cursor':
            _model(settings.get('model'), f'hosts.{host}.model')
        for role, models in settings['roles'].items():
            if not isinstance(role, str) or not isinstance(models, list) or not models:
                raise ConfigError(f'Set a nonempty model list for hosts.{host}.roles.{role}.')
            for value in models:
                _model(value, f'hosts.{host}.roles.{role}')
        effort = settings.get('reasoning_effort')
        if effort is not None and effort not in ('none', 'minimal', 'low', 'medium', 'high', 'xhigh', 'max', 'ultra'):
            raise ConfigError(f'Invalid hosts.{host}.reasoning_effort in config/harness.json.')
    codex = config['hosts']['codex']
    for key in ('reasoning_effort', 'reasoning_summary', 'service_tier'):
        if not isinstance(codex.get(key), str) or not codex[key]:
            raise ConfigError(f'Set hosts.codex.{key} in config/harness.json.')
    if not isinstance(codex.get('features', {}).get('multi_agent'), bool):
        raise ConfigError('hosts.codex.features.multi_agent must be true or false.')
    claude = config['hosts']['claude']
    if not isinstance(claude.get('always_thinking_enabled'), bool):
        raise ConfigError('hosts.claude.always_thinking_enabled must be true or false.')
    if not isinstance(config.get('connections'), dict):
        raise ConfigError('connections must be an object in config/harness.json.')
    classifier = config.get('classifier', {})
    if classifier.get('forced_effort') not in ('low', 'high', 'xhigh'):
        raise ConfigError('classifier.forced_effort must be low, high or xhigh.')
    quota = classifier.get('quota_used_percent')
    if not isinstance(quota, (int, float)) or isinstance(quota, bool) or not 0 <= quota <= 100:
        raise ConfigError('classifier.quota_used_percent must be between 0 and 100.')
    limit = config.get('max_parallel_agents')
    if not isinstance(limit, int) or isinstance(limit, bool) or not 1 <= limit <= 32:
        raise ConfigError('max_parallel_agents must be an integer from 1 to 32.')
    for tool in ('codex', 'claude', 'aws', 'twg'):
        if not isinstance(config.get('tools', {}).get(tool), str) or not config['tools'][tool]:
            raise ConfigError(f'Set tools.{tool} in config/harness.json.')
    return config


def read_version(root: Path | None = None) -> str:
    """Return the package version from the single VERSION file."""
    root = root or Path(__file__).resolve().parents[1]
    try:
        version = (root / 'VERSION').read_text(encoding='utf-8').strip()
    except OSError as error:
        raise ConfigError(f'Cannot read VERSION: {error}') from error
    if not re.fullmatch(r'\d+\.\d+\.\d+', version):
        raise ConfigError('VERSION must contain a three-part version number.')
    return version


def _model(value: object, setting: str) -> None:
    if not isinstance(value, str) or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.:\[\]-]*', value):
        raise ConfigError(f'Invalid model at {setting} in config/harness.json; no fallback is allowed.')


def resolve_role(config: dict, host: str, role: str) -> list[str]:
    if host not in config['hosts']:
        raise ConfigError(f'Unknown host {host!r}; use codex, cursor or claude.')
    settings = config['hosts'][host]
    if role == 'main' and 'model' in settings:
        return [settings['model']]
    if role in settings['roles']:
        return list(settings['roles'][role])
    for group, models in settings['roles'].items():
        if role in [name.strip() for name in group.split(',')]:
            return list(models)
    raise ConfigError(f'Set hosts.{host}.roles.{role} in config/harness.json; no fallback is allowed.')
