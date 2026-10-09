import io
import os
import unittest
from unittest.mock import patch

from agent_harness.guard import classify_external, run_external


class GuardTests(unittest.TestCase):
    def setUp(self):
        self.executed = []
        self.config = {'tools': {'twg': r'C:\Tools\twg.exe', 'aws': r'C:\Tools\aws.exe'}, 'aws_profile_env': 'AWS_PROFILE'}

    def fake_process(self, argv, *, env=None, stdin_text=None):
        self.executed.append((list(argv), dict(env or {}), stdin_text))
        return 0

    def read_env(self):
        return {**os.environ, 'AWS_PROFILE': 'work-test'}

    def test_allowlisted_twg_read_executes_without_prompt(self):
        with patch('agent_harness.guard.run_process', side_effect=self.fake_process), patch('sys.stdin.isatty', return_value=False):
            result = run_external(self.config, 'twg', ['jira', 'workitem', 'get', 'EXAMPLE-123'])
        self.assertEqual(result, 0)
        self.assertEqual(self.executed[0][0][1:], ['jira', 'workitem', 'get', 'EXAMPLE-123'])

    def test_twg_merge_is_denied_when_stdin_is_redirected(self):
        with patch('agent_harness.guard.run_process', side_effect=self.fake_process), patch('sys.stdin.isatty', return_value=False), patch('builtins.input', return_value='yes'):
            result = run_external(self.config, 'twg', ['bb', 'prs', 'merge', '123'])
        self.assertNotEqual(result, 0)
        self.assertEqual(self.executed, [])

    def test_write_requires_exact_terminal_yes(self):
        with patch('agent_harness.guard.run_process', side_effect=self.fake_process), patch('agent_harness.guard._ask_from_real_tty', return_value='yes') as terminal:
            result = run_external(self.config, 'twg', ['jira', 'workitem', 'transition', 'EXAMPLE-123', 'Done'])
        self.assertEqual(result, 0)
        for part in ('workitem', 'transition', 'EXAMPLE-123', 'Done'):
            self.assertIn(part, terminal.call_args.args[0])
        self.assertEqual(len(self.executed), 1)

    def test_non_tty_denial_displays_review_command_and_names_wrapper(self):
        output = io.StringIO()
        with patch('agent_harness.guard.run_process', side_effect=self.fake_process), patch('sys.stdin.isatty', return_value=False), patch('sys.stderr', output), patch('builtins.input', return_value='yes'):
            result = run_external(self.config, 'twg', ['jira', 'workitem', 'transition', 'EXAMPLE-123', 'Done'])
        self.assertNotEqual(result, 0)
        self.assertIn('Type yes to run this exact command', output.getvalue())
        self.assertIn('Rerun through htwg', output.getvalue())
        self.assertEqual(self.executed, [])

    def test_aws_requires_profile_and_blocks_profile_or_endpoint_override(self):
        with patch.dict(os.environ, {}, clear=True), patch('agent_harness.guard.run_process', side_effect=self.fake_process):
            self.assertNotEqual(run_external(self.config, 'aws', ['sts', 'get-caller-identity']), 0)
        with patch.dict(os.environ, self.read_env()), patch('agent_harness.guard.run_process', side_effect=self.fake_process):
            self.assertNotEqual(run_external(self.config, 'aws', ['sts', 'get-caller-identity', '--profile', 'other']), 0)
            self.assertNotEqual(run_external(self.config, 'aws', ['sts', 'get-caller-identity', '--endpoint-url', 'http://host']), 0)
        self.assertEqual(self.executed, [])

    def test_aws_help_runs_without_profile_for_top_level_and_subcommand_help(self):
        with patch.dict(os.environ, {}, clear=True), patch('agent_harness.guard.run_process', side_effect=self.fake_process):
            self.assertEqual(run_external(self.config, 'aws', ['--help']), 0)
            self.assertEqual(run_external(self.config, 'aws', ['sts', 'get-caller-identity', '--help']), 0)
            self.assertEqual(run_external(self.config, 'aws', ['ec2', 'help']), 0)
            self.assertNotEqual(run_external(self.config, 'aws', ['sts', 'get-caller-identity']), 0)
        self.assertEqual([call[0][1:] for call in self.executed], [['--help'], ['sts', 'get-caller-identity', '--help'], ['ec2', 'help']])

    def test_subcommand_help_is_classified_as_a_read(self):
        self.assertEqual(classify_external('twg', ['jira', '--help']), 'read')
        self.assertEqual(classify_external('twg', ['jira', 'workitem', 'transition', '-h']), 'read')
        self.assertEqual(classify_external('aws', ['ec2', 'create-tags', '--help']), 'read')
        self.assertEqual(classify_external('aws', ['ec2', 'help']), 'read')
        self.assertEqual(classify_external('twg', ['jira', 'help']), 'unknown')

    def test_credential_printing_aws_commands_are_denied(self):
        denied = [
            ['configure', 'export-credentials'], ['configure', 'get', 'aws_secret_access_key'],
            ['sts', 'get-session-token'], ['sts', 'assume-role', '--role-arn', 'arn'], ['sts', 'assume-role-with-saml'],
            ['sts', 'get-federation-token'], ['ecr', 'get-login-password'], ['ecr', 'get-authorization-token'],
            ['ssm', 'get-parameter-history', '--name', 'x', '--with-decryption'], ['kms', 'decrypt'],
        ]
        for argv in denied:
            self.assertEqual(classify_external('aws', argv), 'denied', argv)
        self.assertEqual(classify_external('aws', ['configure', 'get', 'region']), 'unknown')
        with patch.dict(os.environ, self.read_env()), patch('agent_harness.guard.run_process', side_effect=self.fake_process):
            for argv in denied:
                self.assertNotEqual(run_external(self.config, 'aws', argv), 0, argv)
        self.assertEqual(self.executed, [])

    def test_debug_flag_is_blocked_because_it_logs_signed_credentials(self):
        with patch.dict(os.environ, self.read_env()), patch('agent_harness.guard.run_process', side_effect=self.fake_process):
            self.assertNotEqual(run_external(self.config, 'aws', ['sts', 'get-caller-identity', '--debug']), 0)
        self.assertEqual(self.executed, [])

    def test_task_definition_read_prompts_because_it_can_carry_plaintext_environment(self):
        self.assertEqual(classify_external('aws', ['ecs', 'describe-task-definition', '--task-definition', 'x']), 'unknown')
        self.assertEqual(classify_external('aws', ['ecs', 'describe-services', '--cluster', 'x']), 'read')

    def test_plain_words_basic_and_bearer_are_not_credentials(self):
        with patch('agent_harness.guard.run_process', side_effect=self.fake_process), patch('agent_harness.guard._ask_from_real_tty', return_value='yes'):
            self.assertEqual(run_external(self.config, 'twg', ['jira', 'workitem', 'create', '--summary', 'Fix basic auth retry and bearer handling']), 0)
            self.assertNotEqual(run_external(self.config, 'twg', ['jira', 'workitem', 'get', 'X-1', 'Bearer abcdefghijklmnopqrstuvwxyz0123']), 0)
            self.assertNotEqual(run_external(self.config, 'twg', ['jira', 'workitem', 'get', 'X-1', 'Authorization: Basic dXNlcjpwYXNz']), 0)
        self.assertEqual(len(self.executed), 1)

    def test_refusal_shows_wrapper_rerun_line_and_escapes_control_characters(self):
        output = io.StringIO()
        hostile = 'Value=Denied\r\x1b[2Kfaked'
        with patch.dict(os.environ, self.read_env()), patch('agent_harness.guard.run_process', side_effect=self.fake_process), patch('sys.stdin.isatty', return_value=False), patch('sys.stderr', output):
            self.assertNotEqual(run_external(self.config, 'aws', ['ec2', 'create-tags', '--tags', hostile]), 0)
        text = output.getvalue()
        self.assertEqual(self.executed, [])
        self.assertNotIn('\r', text)
        self.assertNotIn('\x1b', text)
        will_run = next(line for line in text.splitlines() if line.startswith('Will run: '))
        rerun = next(line for line in text.splitlines() if line.startswith('Rerun yourself: '))
        self.assertIn('--profile', will_run)
        self.assertIn('aws.exe', will_run)
        self.assertTrue(rerun.startswith('Rerun yourself: haws '), rerun)
        self.assertNotIn('--profile', rerun)
        self.assertNotIn('aws.exe', rerun)
        self.assertIn('create-tags', rerun)
        self.assertIn('\\r', rerun)

    def test_sensitive_aws_value_reads_are_denied(self):
        with patch.dict(os.environ, self.read_env()), patch('agent_harness.guard.run_process', side_effect=self.fake_process):
            result = run_external(self.config, 'aws', ['secretsmanager', 'get-secret-value', '--secret-id', 'test'])
        self.assertNotEqual(result, 0)
        self.assertEqual(self.executed, [])

    def test_aws_uses_named_profile_and_strips_ambient_credential_overrides(self):
        environment = {**self.read_env(), 'AWS_ACCESS_KEY_ID': 'ambient-key', 'AWS_SECRET_ACCESS_KEY': 'ambient-secret', 'AWS_DEFAULT_PROFILE': 'other'}
        with patch.dict(os.environ, environment), patch('agent_harness.guard.run_process', side_effect=self.fake_process):
            result = run_external(self.config, 'aws', ['sts', 'get-caller-identity'])
        self.assertEqual(result, 0)
        argv, child_env, _ = self.executed[0]
        self.assertEqual(argv[1:4], ['--profile', 'work-test', 'sts'])
        self.assertEqual(child_env['AWS_PROFILE'], 'work-test')
        self.assertNotIn('AWS_ACCESS_KEY_ID', child_env)
        self.assertNotIn('AWS_SECRET_ACCESS_KEY', child_env)
        self.assertNotIn('AWS_DEFAULT_PROFILE', child_env)

    def test_aws_endpoint_environment_override_is_removed(self):
        environment = {**self.read_env(), 'AWS_ENDPOINT_URL': 'http://wrong', 'AWS_ENDPOINT_URL_STS': 'http://wrong'}
        with patch.dict(os.environ, environment), patch('agent_harness.guard.run_process', side_effect=self.fake_process):
            self.assertEqual(run_external(self.config, 'aws', ['sts', 'get-caller-identity']), 0)
        child_env = self.executed[0][1]
        self.assertNotIn('AWS_ENDPOINT_URL', child_env)
        self.assertNotIn('AWS_ENDPOINT_URL_STS', child_env)

    def test_credential_option_is_rejected_without_echoing_value(self):
        secret = 'never-print-this'
        output = io.StringIO()
        with patch('sys.stderr', output), patch('agent_harness.guard.run_process', side_effect=self.fake_process):
            result = run_external(self.config, 'twg', ['jira', 'workitem', 'get', 'EXAMPLE-123', '--token', secret])
        self.assertNotEqual(result, 0)
        self.assertNotIn(secret, output.getvalue())
        self.assertEqual(self.executed, [])

    def test_twg_environment_dump_is_denied_even_with_list_flag(self):
        with patch('agent_harness.guard.run_process', side_effect=self.fake_process):
            self.assertNotEqual(run_external(self.config, 'twg', ['env', '--list']), 0)
        self.assertEqual(self.executed, [])

    def test_validated_twg_read_grammar_includes_nested_bitbucket_routes(self):
        self.assertEqual(classify_external('twg', ['jira', 'workitem', 'search', 'EXAMPLE-123']), 'read')
        self.assertEqual(classify_external('twg', ['bitbucket', 'repo', 'get', 'example-repo']), 'read')
        self.assertEqual(classify_external('twg', ['bb', 'branch', 'query', 'example-branch']), 'read')
        self.assertEqual(classify_external('twg', ['bb', 'pipeline', 'query', '123']), 'read')
        self.assertEqual(classify_external('twg', ['pipeline', 'run', '123']), 'write')
        self.assertEqual(classify_external('twg', ['jira', 'workitem', 'find', 'EXAMPLE-123']), 'unknown')
        self.assertEqual(classify_external('aws', ['s3', 'rm', 's3://bucket/key']), 'write')


if __name__ == '__main__':
    unittest.main()
