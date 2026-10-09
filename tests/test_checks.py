import io
import json
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from agent_harness.checks import (
    _aws_ready, _claude_models, _codex_models, _model_settings, _probe_claude_models, _run, run_checks,
)
from agent_harness.config import load_config

ROOT = Path(__file__).resolve().parents[1]


class CheckTests(unittest.TestCase):
    def test_reports_missing_sign_in_without_printing_command_output(self):
        output = self._run_main_check(auth_ok=False)
        self.assertIn('Managed setup: Installed and matches this package.', output)
        self.assertIn('Codex sign-in: Not verified', output)
        self.assertIn('Claude sign-in: Not verified', output)
        self.assertIn('AWS sign-in: Not verified', output)
        self.assertIn('TWG sign-in: Not verified', output)
        self.assertIn('Cursor model status: Manual check required', output)
        self.assertNotIn('SECRET_TOKEN', output)
        self.assertNotIn('Setup checks passed.', output)

    def test_probe_routes_every_configured_model_without_fallback(self):
        config = load_config(ROOT)
        codex_expected = _codex_models(config)
        claude_expected = _claude_models(config)
        with patch('agent_harness.checks._probe_codex_models', return_value={
                    'catalog_error': False, 'missing_models': [], 'effort_incompatible': []}) as codex_probe, \
             patch('agent_harness.checks._probe_claude_models', return_value={model: model for model in claude_expected}) as claude_probe:
            output = self._run_main_check(auth_ok=True, probe=True, use_outer_probe_mocks=True)
        codex_probe.assert_called_once_with('/tools/codex', codex_expected, 'ultra', 'gpt-6-astra')
        claude_probe.assert_called_once_with('/tools/claude', claude_expected, 'xhigh')
        self.assertIn(f'Verified {len(codex_expected)} configured model(s)', output)
        self.assertIn(f'Verified {len(claude_expected)} configured model(s)', output)
        self.assertIn('Cursor model status: Manual check required', output)
        self.assertNotIn('Setup checks passed.', output)

    def test_unavailable_configured_models_name_the_model_and_setting(self):
        with patch('agent_harness.checks._probe_codex_models', return_value={
                    'catalog_error': False, 'missing_models': ['gpt-6-astra'], 'effort_incompatible': []}), \
             patch('agent_harness.checks._probe_claude_models', return_value=None):
            output = self._run_main_check(auth_ok=True, probe=True, use_outer_probe_mocks=True)
        self.assertIn('`gpt-6-astra` is absent from Codex model/list', output)
        self.assertIn('hosts.codex.model', output)
        self.assertIn('hosts.codex.roles.how critics', output)
        self.assertIn('Could not verify `claude-opus-5-5`', output)
        self.assertIn('routes.claude-opus-5-5', output)

    def test_failed_codex_catalog_cannot_be_reported_as_verified(self):
        with patch('agent_harness.checks._probe_codex_models', return_value={
                    'catalog_error': True, 'missing_models': [], 'effort_incompatible': []}), \
             patch('agent_harness.checks._probe_claude_models', return_value=None):
            output = self._run_main_check(auth_ok=True, probe=True, use_outer_probe_mocks=True)
        self.assertIn('Codex model catalog: Not verified', output)
        self.assertNotIn('Codex model catalog: Verified', output)

    def test_aws_requires_v2_and_the_explicit_profile_identity(self):
        result = SimpleNamespace(returncode=0, stdout='aws-cli/2.31.0 Python/3.13', stderr='')
        identity = SimpleNamespace(returncode=0, stdout=json.dumps({
            'Account': '123456789012', 'Arn': 'arn:aws:iam::123456789012:user/test', 'UserId': 'AIDTEST'
        }), stderr='')
        with patch('agent_harness.checks._run', side_effect=[result, identity]) as run:
            self.assertTrue(_aws_ready('/tools/aws', 'dev'))
        self.assertEqual(run.call_args_list[1].args[0][:3], ['/tools/aws', '--profile', 'dev'])
        env = run.call_args_list[1].kwargs['env']
        self.assertEqual(env['AWS_PROFILE'], 'dev')
        self.assertNotIn('AWS_ACCESS_KEY_ID', env)
        self.assertNotIn('AWS_ENDPOINT_URL', env)
        with patch('agent_harness.checks._run', return_value=SimpleNamespace(
                returncode=0, stdout='aws-cli/1.27.0', stderr='')):
            self.assertFalse(_aws_ready('/tools/aws', 'dev'))

    def test_claude_model_probe_rejects_errors_and_requires_usage_identity(self):
        error = SimpleNamespace(returncode=0, stdout=json.dumps({
            'is_error': True, 'modelUsage': {'opus': {}}, 'result': 'error'
        }), stderr='')
        with patch('agent_harness.checks._run', return_value=error):
            self.assertIsNone(_probe_claude_models('/tools/claude', ['opus'], 'xhigh'))
        missing_usage = SimpleNamespace(returncode=0, stdout=json.dumps({
            'is_error': False, 'result': 'OK'
        }), stderr='')
        with patch('agent_harness.checks._run', return_value=missing_usage):
            self.assertIsNone(_probe_claude_models('/tools/claude', ['opus'], 'xhigh'))
        wrong_identity = SimpleNamespace(returncode=0, stdout=json.dumps({
            'is_error': False, 'modelUsage': {'claude-sonnet-5': {}}, 'result': 'OK'
        }), stderr='')
        with patch('agent_harness.checks._run', return_value=wrong_identity):
            self.assertIsNone(_probe_claude_models('/tools/claude', ['claude-opus-5-5'], 'xhigh'))
        alias_identity = SimpleNamespace(returncode=0, stdout=json.dumps({
            'is_error': False, 'modelUsage': {'claude-opus-5-5': {}}, 'result': 'OK'
        }), stderr='')
        with patch('agent_harness.checks._run', return_value=alias_identity):
            self.assertEqual(_probe_claude_models('/tools/claude', ['opus'], 'xhigh'),
                             {'opus': 'claude-opus-5-5'})
        self.assertIn('hosts.codex.roles.how critics', _model_settings(load_config(ROOT), 'claude', 'claude-opus-5-5'))

    def test_run_handles_missing_executable_and_timeout(self):
        with patch('agent_harness.checks.subprocess.run', side_effect=FileNotFoundError):
            self.assertEqual(_run(['/missing/tool']).returncode, 1)
        with patch('agent_harness.checks.subprocess.run', side_effect=__import__('subprocess').TimeoutExpired('tool', 1)):
            result = _run(['/tools/hanging'], timeout=1)
        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stdout, '')
        self.assertEqual(result.stderr, '')

    def test_generation_errors_never_echo_untrusted_error_text(self):
        tools = {'git': None, 'codex': None, 'claude': None, 'aws': None, 'twg': None}
        output = io.StringIO()
        with patch('agent_harness.checks._native_tool', return_value=None), \
             patch('agent_harness.checks.shutil.which', side_effect=lambda name: tools.get(name)), \
             patch('agent_harness.checks.generate', side_effect=ValueError('SECRET_TOKEN=do-not-print')), \
             redirect_stdout(output):
            code = run_checks(ROOT, Path('/tmp/fixture-home'))
        self.assertEqual(code, 1)
        self.assertIn('package configuration is invalid', output.getvalue())
        self.assertNotIn('SECRET_TOKEN', output.getvalue())

    def test_non_object_json_is_not_account_or_model_evidence(self):
        invalid = SimpleNamespace(returncode=0, stdout='[]', stderr='')
        version = SimpleNamespace(returncode=0, stdout='aws-cli/2.31.0', stderr='')
        with patch('agent_harness.checks._run', return_value=invalid):
            self.assertIsNone(_probe_claude_models('/tools/claude', ['opus'], 'high'))
        with patch('agent_harness.checks._run', side_effect=[version, invalid]):
            self.assertFalse(_aws_ready('/tools/aws', 'dev'))

    def _run_main_check(self, auth_ok: bool, probe: bool = False,
                        use_outer_probe_mocks: bool = False) -> str:
        tools = {'git': '/bin/git', 'codex': '/tools/codex', 'claude': '/tools/claude',
                 'aws': '/tools/aws', 'twg': '/tools/twg'}

        def command(args, **kwargs):
            if args == ['/bin/git', '--version']:
                return SimpleNamespace(returncode=0, stdout='git version 2.0', stderr='')
            if args == ['/tools/codex', '--help']:
                return SimpleNamespace(returncode=0, stdout='-p, --profile <CONFIG_PROFILE_V2>', stderr='')
            if args[0] == '/tools/codex':
                return SimpleNamespace(returncode=0 if auth_ok else 1,
                                        stdout='' if auth_ok else 'SECRET_TOKEN=do-not-print', stderr='')
            if args[0] == '/tools/claude':
                return SimpleNamespace(returncode=0 if auth_ok else 1,
                                        stdout='' if auth_ok else 'SECRET_TOKEN=do-not-print', stderr='')
            if args[0] == '/tools/aws' and args[1] == '--version':
                return SimpleNamespace(returncode=0, stdout='aws-cli/2.31.0', stderr='')
            if args[0] == '/tools/aws':
                return SimpleNamespace(returncode=0 if auth_ok else 1, stdout=json.dumps({
                    'Account': '123456789012', 'Arn': 'arn:aws:iam::123456789012:user/test', 'UserId': 'AIDTEST'
                }), stderr='')
            if args[0] == '/tools/twg':
                return SimpleNamespace(returncode=0 if auth_ok else 1,
                                        stdout='' if auth_ok else 'SECRET_TOKEN=do-not-print', stderr='')
            raise AssertionError(args)

        output = io.StringIO()
        patches = [patch('agent_harness.checks._native_tool', side_effect=lambda name: None if name == 'cursor' else f'/tools/{name}'),
             patch('agent_harness.checks.shutil.which', side_effect=lambda name: tools.get(name)),
             patch('agent_harness.checks.subprocess.run', side_effect=command), \
             patch('agent_harness.checks.generate', return_value={'changed': 0, 'pending': []}), \
             patch.dict('os.environ', {'AWS_PROFILE': 'dev'})]
        if probe and not use_outer_probe_mocks:
            patches.extend([
                patch('agent_harness.checks._probe_codex_models', return_value={
                    'catalog_error': False, 'missing_models': [], 'effort_incompatible': []}),
                patch('agent_harness.checks._probe_claude_models', return_value={}),
            ])
        with patches[0], patches[1], patches[2], patches[3], patches[4], \
             (patches[5] if len(patches) > 5 else __import__('contextlib').nullcontext()), \
             (patches[6] if len(patches) > 6 else __import__('contextlib').nullcontext()), \
             redirect_stdout(output):
            result = run_checks(ROOT, Path('/tmp/fixture-home'), probe_models=probe)
        self.assertEqual(result, 1)  # Cursor availability remains explicitly unverified.
        return output.getvalue()


if __name__ == '__main__':
    unittest.main()
