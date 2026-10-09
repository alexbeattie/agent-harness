from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

from .config import load_config
from .dispatch import observed_model_identity
from .generation import GenerationError, generate
from .model_catalog import codex_model_pages as _codex_model_pages


def run_checks(root: Path, target_home: Path, probe_models: bool = False) -> int:
    """Print safe, plain-English status; never echo command output or secrets."""
    root, target_home = root.resolve(), target_home.expanduser().absolute()
    failures: list[str] = []
    config = load_config(root)

    if sys.version_info >= (3, 11):
        print(f'Python: Installed ({sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro})')
    else:
        print(f'Python: Too old ({sys.version_info.major}.{sys.version_info.minor}); install Python 3.11 or later.')
        failures.append('Python 3.11+')

    git = shutil.which('git')
    if git and _run([git, '--version']).returncode == 0:
        print('Git: Installed')
    else:
        print('Git: Missing; install Git for Windows and reopen PowerShell.')
        failures.append('Git')

    try:
        state = generate(root, target_home, check=True)
        if state['changed']:
            print(f"Managed setup: {state['changed']} generated file(s) need installation or refresh.")
            failures.append('managed setup')
        else:
            print('Managed setup: Installed and matches this package.')
        retired = state.get('retained_obsolete', [])
        if retired:
            print('Managed setup: Retired package files remain and may still load: ' + ', '.join(retired))
            failures.append('retired managed files')
    except GenerationError:
        print('Managed setup: Cannot verify because a managed file conflicts with user content or package sources are incomplete.')
        failures.append('managed setup')
    except OSError:
        print('Managed setup: Cannot verify because a managed path is unavailable or unreadable.')
        failures.append('managed setup')
    except ValueError:
        print('Managed setup: Cannot verify because package configuration is invalid.')
        failures.append('managed setup')

    commands = {name: _native_tool(name) for name in ('codex', 'claude', 'aws', 'twg')}
    for name in ('codex', 'claude', 'aws', 'twg'):
        label = {'codex': 'Codex CLI', 'claude': 'Claude Code', 'aws': 'AWS CLI', 'twg': 'TWG CLI'}[name]
        if commands[name]:
            print(f'{label}: Installed')
        elif name in ('codex', 'claude') and os.name == 'nt' and shutil.which(name):
            print(f'{label}: Only a command shim is on PATH; install or update native {name}.exe.')
            failures.append(f'native {label}')
        else:
            print(f'{label}: Missing; install it with install.ps1.')
            failures.append(label)

    codex_profile_ok = bool(commands['codex']) and _codex_profile_compatible(commands['codex'])
    if codex_profile_ok:
        print('Codex profile support: Compatible with the generated standalone profile.')
    elif commands['codex']:
        print('Codex profile support: Too old or unverified; update Codex to a version that supports `--profile <CONFIG_PROFILE_V2>`.')
        failures.append('Codex profile support')

    signed_in = {}
    for name, label, arguments, instruction in (
        ('codex', 'Codex', ['login', 'status'], 'codex login'),
        ('claude', 'Claude', ['auth', 'status'], 'claude auth login'),
    ):
        executable = commands[name]
        if executable:
            signed_in[name] = _run([executable, *arguments]).returncode == 0
        else:
            signed_in[name] = False
        if signed_in[name]:
            print(f'{label} sign-in: Signed in')
        else:
            print(f'{label} sign-in: Not verified; run `{instruction}` in PowerShell.')
            failures.append(f'{label} sign-in')

    aws_profile = os.environ.get('AWS_PROFILE', '').strip()
    aws_ready = _aws_ready(commands['aws'], aws_profile)
    if aws_ready:
        print(f'AWS CLI: Version 2 and the selected profile `{aws_profile}` are ready.')
    elif not aws_profile:
        print('AWS sign-in: Not verified; set AWS_PROFILE and authenticate that named profile.')
        failures.append('AWS profile')
    elif not commands['aws']:
        print('AWS sign-in: Not verified; AWS CLI is missing.')
    else:
        print(f'AWS sign-in: Not verified for profile `{aws_profile}`; use `aws sso login --profile {aws_profile}` if it uses IAM Identity Center.')
        failures.append('AWS profile sign-in')

    twg_ready = bool(commands['twg']) and _run([commands['twg'], 'doctor']).returncode == 0
    if twg_ready:
        print('TWG sign-in: Ready')
    else:
        print('TWG sign-in: Not verified; run `twg login`, then `twg setup bitbucket` in PowerShell.')
        failures.append('TWG sign-in')

    cursor_unverified = _cursor_models(config)
    print('Cursor app: ' + ('Found; model availability remains manual.' if _native_tool('cursor') else 'Not found on PATH; model availability remains manual.'))
    print('Cursor model status: Manual check required in Cursor settings; the CLI cannot verify Cursor account availability.')
    print('Cursor model IDs: ' + ', '.join(sorted(cursor_unverified)))
    if cursor_unverified:
        failures.append('Cursor model availability')

    if probe_models:
        codex_models = _codex_models(config)
        claude_models = _claude_models(config)
        codex_probe = _probe_codex_models(
            commands['codex'], codex_models, config['hosts']['codex'].get('reasoning_effort'),
            config['hosts']['codex']['model']) if signed_in['codex'] and commands['codex'] and codex_profile_ok else None
        claude_probe = _probe_claude_models(
            commands['claude'], claude_models, config['hosts']['claude'].get('reasoning_effort')) if signed_in['claude'] and commands['claude'] else None
        codex_ok = (codex_probe is not None and not codex_probe.get('catalog_error')
                    and not codex_probe['missing_models'] and not codex_probe['effort_incompatible'])
        if codex_ok:
            print(f"Codex model catalog: Verified {len(codex_models)} configured model(s), including supported reasoning effort.")
        else:
            print('Codex model catalog: Not verified for every configured model and reasoning effort; no substitute was tried.')
            if codex_probe is None or codex_probe.get('catalog_error'):
                for model in codex_models:
                    setting = ', '.join(_model_settings(config, 'codex', model)) or 'configured Codex role'
                    print(f'  Could not verify `{model}`; inspect {setting} and confirm Codex profile/sign-in support.')
            for model in (codex_probe or {}).get('missing_models', []):
                setting = ', '.join(_model_settings(config, 'codex', model)) or 'configured Codex role'
                print(f'  `{model}` is absent from Codex model/list; inspect {setting} before changing it.')
            for model in (codex_probe or {}).get('effort_incompatible', []):
                print(f"  `{model}` does not advertise `{config['hosts']['codex'].get('reasoning_effort')}`; inspect hosts.codex.reasoning_effort or that role's model.")
            failures.append('Codex model availability')
        claude_ok = claude_probe is not None
        if claude_ok:
            print(f'Claude model probe: Verified {len(claude_models)} configured model(s) with returned model-usage identity.')
            for requested, observed in claude_probe.items():
                if requested != observed:
                    print(f'  Alias `{requested}` resolved to `{observed}`; this is the observed model, not an exact-ID match.')
        else:
            print('Claude model probe: Not verified for every configured model; no substitute was tried.')
            for model in claude_models:
                setting = ', '.join(_model_settings(config, 'claude', model)) or 'configured Claude route'
                print(f'  Could not verify `{model}`; inspect {setting} and its exact model ID.')
            failures.append('Claude model availability')
    else:
        print('Codex/Claude model availability: Configured values only; use --probe-models for live checks.')
        failures.extend(['Codex model availability', 'Claude model availability'])

    if failures:
        print('Setup is incomplete. Fix the unverified items above, then run check.ps1 again.')
        return 1
    print('Setup checks passed.')
    return 0


def _aws_ready(executable: str | None, profile: str) -> bool:
    if not executable or not re.fullmatch(r'[A-Za-z0-9_.-]+', profile):
        return False
    env = _aws_environment(profile)
    version = _run([executable, '--version'], env=env)
    if version.returncode or 'aws-cli/2.' not in version.stdout:
        return False
    identity = _run([executable, '--profile', profile, 'sts', 'get-caller-identity',
                     '--output', 'json', '--no-cli-pager'], env=env)
    if identity.returncode:
        return False
    try:
        value = json.loads(identity.stdout)
    except (ValueError, TypeError):
        return False
    return isinstance(value, dict) and bool(value.get('Account') and value.get('Arn') and value.get('UserId'))


def _codex_models(config: dict) -> list[str]:
    result = {config['hosts']['codex']['model']}
    result.update(model for models in config['hosts']['codex']['roles'].values() for model in models
                  if config.get('routes', {}).get(model, 'codex') == 'codex')
    result.update(alias.get('model') for aliases in config.get('aliases', {}).values()
                  for alias in aliases.values() if alias.get('backend') == 'codex')
    return sorted(model for model in result if isinstance(model, str))


def _claude_models(config: dict) -> list[str]:
    result = {config['hosts']['claude']['model']}
    result.update(model for models in config['hosts']['claude']['roles'].values() for model in models
                  if model not in config.get('aliases', {}).get('claude', {}))
    result.update(model for host in config['hosts'].values() for models in host.get('roles', {}).values()
                  for model in models if config.get('routes', {}).get(model) == 'claude')
    independent = config.get('independent_review', {})
    if independent.get('host') == 'claude' and isinstance(independent.get('model'), str):
        result.add(independent['model'])
    return sorted(model for model in result if isinstance(model, str))


def _cursor_models(config: dict) -> set[str]:
    return {model for models in config['hosts']['cursor']['roles'].values() for model in models}


def _probe_codex_models(executable: str, requested: list[str], effort: str | None,
                        main_model: str) -> dict | None:
    pages = _codex_model_pages(executable)
    if pages is None:
        return {'catalog_error': True, 'missing_models': [], 'effort_incompatible': []}
    catalog = {}
    for item in pages:
        if isinstance(item, dict):
            name = item.get('model') or item.get('id') or item.get('slug')
            if isinstance(name, str):
                catalog[name] = item
    missing = sorted(set(requested) - set(catalog))
    incompatible = []
    if effort:
        for model in set(requested) & set(catalog):
            supported = catalog[model].get('supportedReasoningEfforts') or catalog[model].get('supported_reasoning_efforts')
            if not isinstance(supported, list):
                incompatible.append(model)
                continue
            names = {item if isinstance(item, str) else item.get('reasoningEffort') or item.get('effort')
                     for item in supported if isinstance(item, (str, dict))}
            if effort not in names:
                incompatible.append(model)
    return {'catalog_error': False, 'missing_models': missing,
            'effort_incompatible': sorted(incompatible)}



def _probe_claude_models(executable: str, models: list[str], effort: str | None) -> dict[str, str] | None:
    observed = {}
    for model in models:
        arguments = [executable, '-p', '--model', model]
        if effort:
            arguments += ['--effort', effort]
        arguments += ['--tools', '', '--setting-sources', '', '--strict-mcp-config',
                      '--mcp-config', '{"mcpServers":{}}', '--max-turns', '1',
                      '--output-format', 'json', 'Reply with the single word OK.']
        result = _run(arguments, timeout=90)
        if result.returncode:
            return None
        try:
            payload = json.loads(result.stdout)
        except (ValueError, TypeError):
            return None
        if not isinstance(payload, dict) or payload.get('is_error') is not False:
            return None
        usage = payload.get('modelUsage')
        if payload.get('is_error') is True or not isinstance(usage, dict) or not usage:
            return None
        if not payload.get('result'):
            return None
        identity = observed_model_identity(usage, model)
        if identity is None:
            return None
        observed[model] = identity
    return observed


def _run(arguments: list[str], *, input_text: str | None = None, timeout: int = 25,
         env: dict[str, str] | None = None) -> _Result:
    try:
        result = subprocess.run(arguments, input=input_text, text=True, encoding='utf-8', errors='replace', capture_output=True,
                               timeout=timeout, check=False, shell=False, env=env)
        return _Result(result.returncode, result.stdout, result.stderr)
    except (OSError, subprocess.TimeoutExpired):
        return _Result(1, '', '')


class _Result:
    def __init__(self, returncode: int, stdout: str = '', stderr: str = ''):
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr


def _native_tool(name: str) -> str | None:
    if os.name == 'nt':
        # Runtime subprocess dispatch accepts native executables only. Do not
        # report a .cmd shim as ready when Python will reject it later.
        return shutil.which(name + '.exe')
    return shutil.which(name)


def _codex_profile_compatible(executable: str) -> bool:
    help_result = _run([executable, '--help'])
    return help_result.returncode == 0 and '--profile' in help_result.stdout and 'CONFIG_PROFILE_V2' in help_result.stdout


def _aws_environment(profile: str) -> dict[str, str]:
    env = os.environ.copy()
    for key in ('AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY', 'AWS_SESSION_TOKEN',
                'AWS_SECURITY_TOKEN', 'AWS_WEB_IDENTITY_TOKEN_FILE', 'AWS_ROLE_ARN',
                'AWS_DEFAULT_PROFILE'):
        env.pop(key, None)
    for key in tuple(env):
        if key == 'AWS_ENDPOINT_URL' or key.startswith('AWS_ENDPOINT_URL_'):
            env.pop(key, None)
    env['AWS_PROFILE'] = profile
    return env


def _model_settings(config: dict, host: str, model: str) -> list[str]:
    settings = []
    host_settings = config.get('hosts', {}).get(host, {})
    if host_settings.get('model') == model:
        settings.append(f'hosts.{host}.model')
    for candidate_host, candidate in config.get('hosts', {}).items():
        for role, models in candidate.get('roles', {}).items():
            if model in models:
                settings.append(f'hosts.{candidate_host}.roles.{role}')
    for route_model, route_host in config.get('routes', {}).items():
        if route_model == model and route_host == host:
            settings.append(f'routes.{route_model}')
    for alias_host, aliases in config.get('aliases', {}).items():
        for alias, target in aliases.items():
            if target.get('backend') == host and target.get('model') == model:
                settings.append(f'aliases.{alias_host}.{alias}')
    independent = config.get('independent_review', {})
    if independent.get('host') == host and independent.get('model') == model:
        settings.append('independent_review.model')
    return settings
