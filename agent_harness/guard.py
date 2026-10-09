from __future__ import annotations

import os
import re
import sys
from typing import Sequence

from .process import format_command, resolve_executable, run_process

_NO_CONFIRM_FLAGS = {
    '-y', '--yes', '--force', '--auto-approve', '--no-confirm', '--non-interactive',
    '--dangerously-skip-permissions', '--skip-permissions',
}
_CREDENTIAL_FLAGS = {
    '--token', '--password', '--api-key', '--apikey', '--authorization', '--header',
    '--access-key', '--secret-key', '--client-secret', '--secret-string', '--secret-binary', '--value',
}
_AWS_READS = {
    ('sts', 'get-caller-identity'),
    ('ec2', 'describe-instances'), ('ec2', 'describe-vpcs'), ('ec2', 'describe-security-groups'),
    ('ecs', 'describe-clusters'), ('ecs', 'describe-services'), ('ecs', 'describe-tasks'),
    ('ecs', 'list-services'), ('ecs', 'list-tasks'),
    ('logs', 'describe-log-groups'), ('logs', 'describe-log-streams'), ('logs', 'filter-log-events'),
    ('s3', 'ls'), ('s3api', 'list-buckets'), ('s3api', 'list-objects-v2'),
}
_TWG_READ_ROUTES = {
    ('jira', 'workitem', 'get'), ('jira', 'workitem', 'query'), ('jira', 'workitem', 'search'),
    ('bb', 'prs', 'get'), ('bb', 'prs', 'query'), ('bb', 'prs', 'mergeability'),
    ('bb', 'pull-requests', 'get'), ('bb', 'pull-requests', 'query'), ('bb', 'pull-requests', 'mergeability'),
    ('bb', 'repo', 'get'), ('bb', 'repo', 'query'), ('bb', 'branch', 'query'),
    ('bb', 'pipeline', 'get'), ('bb', 'pipeline', 'query'),
}
_AWS_DENIED = {
    ('configure', 'export-credentials'),
    ('sts', 'get-session-token'), ('sts', 'assume-role'), ('sts', 'assume-role-with-saml'),
    ('sts', 'assume-role-with-web-identity'), ('sts', 'get-federation-token'),
    ('ecr', 'get-login-password'), ('ecr', 'get-authorization-token'),
    ('ecr-public', 'get-login-password'), ('ecr-public', 'get-authorization-token'),
    ('ssm', 'get-parameter'), ('ssm', 'get-parameters'), ('ssm', 'get-parameters-by-path'), ('ssm', 'get-parameter-history'),
    ('kms', 'decrypt'), ('secretsmanager', 'get-secret-value'), ('secretsmanager', 'batch-get-secret-value'),
}
_HELP_WORDS = {'--help', '-h'}
_VERSION_ARGV = {('--version',), ('version',)}
_TWG_WRITE_VERBS = {'create', 'update', 'edit', 'delete', 'transition', 'assign', 'merge', 'decline', 'run', 'trigger', 'comment', 'set', 'write', 'publish'}


def _is_help(tool: str, words: tuple[str, ...]) -> bool:
    if not words:
        return False
    if words in _VERSION_ARGV or words[-1] in _HELP_WORDS:
        return True
    return tool == 'aws' and words[-1] == 'help'


def classify_external(tool: str, args: Sequence[str]) -> str:
    """Return read, write, denied or unknown using a finite command allowlist."""
    words = tuple(part.lower() for part in args)
    if tool == 'twg' and words and words[0] == 'bitbucket':
        words = ('bb', *words[1:])
    if _is_help(tool, words):
        return 'read'
    if tool == 'twg':
        if words and words[0] == 'env':
            return 'denied'
        if len(words) >= 2 and words[:2] in {('config', 'export'), ('config', 'dump'), ('auth', 'token'), ('auth', 'credentials')}:
            return 'denied'
        if words in _TWG_READ_ROUTES or words[:3] in _TWG_READ_ROUTES or words[:2] in _TWG_READ_ROUTES:
            return 'read'
        if any(word in _TWG_WRITE_VERBS for word in words[:5]):
            return 'write'
        return 'unknown'
    if tool == 'aws':
        if words[:2] in _AWS_DENIED:
            return 'denied'
        if words[:2] == ('configure', 'get') and len(words) > 2 and any(part in words[2] for part in ('key', 'secret', 'token')):
            return 'denied'
        if words[:2] in _AWS_READS:
            return 'read'
        if words[:2] in {('s3', 'cp'), ('s3', 'mv'), ('s3', 'rm'), ('s3', 'sync')}:
            return 'write'
        if len(words) >= 2 and words[1].startswith(('put-', 'create-', 'delete-', 'update-', 'start-', 'stop-', 'run-')):
            return 'write'
        return 'unknown'
    return 'unknown'


def _blocked_sensitive(tool: str, args: Sequence[str]) -> str | None:
    lowered = [part.lower() for part in args]
    for index, part in enumerate(lowered):
        flag = part.split('=', 1)[0]
        if flag in _CREDENTIAL_FLAGS:
            return 'Credential-bearing command-line options are blocked; use the tool login or environment.'
        if part.startswith('--header=') or part.startswith('--authorization='):
            return 'Credential-bearing command-line options are blocked; use the tool login or environment.'
        if args[index] == '-H' and index + 1 < len(lowered):
            return 'Credential-bearing command-line options are blocked; use the tool login or environment.'
        if re.search(r'authorization\s*:|(?:^|\s)(?:bearer|basic)\s+[a-z0-9._~+/=-]{12,}', part) or re.search(r'\b(?:AKIA|ASIA)[0-9A-Z]{16}\b', part, re.IGNORECASE):
            return 'Credential-like command-line values are blocked; use the tool login or environment.'
    if any(part in _NO_CONFIRM_FLAGS or part.split('=', 1)[0] in _NO_CONFIRM_FLAGS for part in lowered):
        return 'This command includes a flag that bypasses confirmation; remove it.'
    if '--debug' in lowered:
        return 'The --debug option logs signed requests and session credentials; remove it.'
    if tool == 'aws':
        if any(part in {'--profile', '--endpoint-url'} or part.startswith(('--profile=', '--endpoint-url=')) for part in lowered):
            return 'AWS profile and endpoint overrides are blocked; use AWS_PROFILE from your environment.'
    if tool == 'twg':
        joined = ' '.join(lowered)
        sensitive = any(word in joined for word in ('secret', 'password', 'credential', 'access-key', 'token'))
        printing = any(word in lowered for word in ('env', 'print', 'dump', 'show', 'export'))
        if sensitive and printing:
            return 'Printing TWG environment or credential material is blocked.'
    return None


def _printable(text: str) -> str:
    """Escape control characters so a displayed command cannot rewrite the terminal line."""
    return ''.join(ch if ch.isprintable() else repr(ch)[1:-1] for ch in text)


def _ask_from_real_tty(prompt: str) -> str | None:
    """Read from the controlling terminal, never from an agent's piped stdin."""
    if not sys.stdin.isatty():
        return None
    console = 'CONIN$' if os.name == 'nt' else '/dev/tty'
    try:
        with open(console, 'r', encoding='utf-8') as tty:
            return tty.readline().rstrip('\r\n')
    except OSError:
        return None


def run_external(config: dict, tool: str, args: Sequence[str]) -> int:
    """Run an external tool after allowlist classification and a real-TTY gate."""
    if tool not in {'aws', 'twg'}:
        print(f'External tool {tool!r} is not supported.', file=sys.stderr)
        return 2
    if isinstance(args, (str, bytes)) or not all(isinstance(arg, str) for arg in args):
        print('Arguments must be provided as a list of strings.', file=sys.stderr)
        return 2
    executable = config.get('tools', {}).get(tool)
    if not isinstance(executable, str) or not executable:
        print(f'Configure tools.{tool} before using this command.', file=sys.stderr)
        return 2
    blocked = _blocked_sensitive(tool, args)
    if blocked:
        print(blocked, file=sys.stderr)
        return 2
    command = [resolve_executable(executable), *args]
    route = classify_external(tool, args)
    if route == 'denied':
        print('This credential or environment read is blocked.', file=sys.stderr)
        return 2
    child_env = os.environ.copy()
    if tool == 'aws':
        if not _is_help(tool, tuple(part.lower() for part in args)):
            profile_variable = config.get('aws_profile_env', 'AWS_PROFILE')
            profile = child_env.get(profile_variable, '').strip()
            if not profile or not re.fullmatch(r'[A-Za-z0-9_.-]+', profile):
                print(f'Set {profile_variable} before calling AWS CLI.', file=sys.stderr)
                return 2
            child_env['AWS_PROFILE'] = profile
            child_env.pop('AWS_DEFAULT_PROFILE', None)
            for key in ('AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY', 'AWS_SESSION_TOKEN', 'AWS_SECURITY_TOKEN', 'AWS_WEB_IDENTITY_TOKEN_FILE', 'AWS_ROLE_ARN'):
                child_env.pop(key, None)
            for key in tuple(child_env):
                if key == 'AWS_ENDPOINT_URL' or key.startswith('AWS_ENDPOINT_URL_'):
                    child_env.pop(key, None)
            command = [command[0], '--profile', profile, *command[1:]]
    if route in {'write', 'unknown'}:
        wrapper = 'haws' if tool == 'aws' else 'htwg'
        prompt = '\n'.join([
            f'{"Write" if route == "write" else "Unclassified command"} needs approval.',
            f'Will run: {_printable(format_command(command))}',
            f'Rerun yourself: {_printable(format_command([wrapper, *args]))}',
            'Type yes to run this exact command: ',
        ])
        print(prompt, file=sys.stderr, flush=True)
        response = _ask_from_real_tty(prompt)
        if response != 'yes':
            print(f'Command refused; no external command was run. Rerun through {wrapper} in an interactive terminal to request approval.', file=sys.stderr)
            return 2
    return run_process(command, env=child_env)
