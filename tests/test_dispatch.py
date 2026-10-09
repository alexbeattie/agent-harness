import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from agent_harness.dispatch import run_dispatch, start_interactive


class DispatchTests(unittest.TestCase):
    def setUp(self):
        resolver = patch('agent_harness.dispatch.resolve_executable', side_effect=lambda value: value)
        resolver.start()
        self.addCleanup(resolver.stop)
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.calls = []
        self.config = {
            'tools': {'codex': 'codex.exe', 'claude': 'claude.exe'},
            'hosts': {
                'codex': {'model': 'gpt-6-astra', 'reasoning_effort': 'ultra', 'service_tier': 'ultrafast', 'roles': {'panel': ['gpt-6-sol'], 'claude panel': ['claude-opus-5-5']}},
                'claude': {'model': 'fable[1m]', 'reasoning_effort': 'xhigh', 'roles': {'panel': ['fable', 'opus'], 'alias panel': ['astra'], 'exact panel': ['claude-opus-5-5']}},
            },
            'routes': {'claude-opus-5-5': 'claude', 'claude-fable-5-1': 'claude', 'astra': 'codex'},
            'aliases': {'claude': {'astra': {'backend': 'codex', 'model': 'gpt-6-astra'}}},
            'classifier': {'default_host': 'codex', 'claude_context_threshold': 250000, 'forced_effort': 'high', 'effort_levels': ['low', 'high', 'xhigh'], 'quota_used_percent': 0},
        }

    def classifier_run(self, argv, *, stdin_text=None, env=None):
        self.calls.append((list(argv), stdin_text))
        return 0

    def captured_output(self, argv, *, stdin_text=None, env=None):
        if '--output-schema' in argv:
            self.calls.append((list(argv), stdin_text))
            output = Path(argv[argv.index('-o') + 1])
            payload = os.environ.get('CLASSIFIER_JSON', '{"model":"codex","effort":"high","brevity":true,"reason":"routine"}')
            output.write_text(payload, encoding='utf-8')
            return 0, 'codex final message noise that must not reach the caller\n'
        return self.claude_output(argv, stdin_text=stdin_text, env=env)

    def claude_output(self, argv, *, stdin_text=None, env=None):
        self.calls.append((list(argv), stdin_text))
        model = argv[argv.index('--model') + 1]
        payload = {
            'is_error': os.environ.get('CLAUDE_IS_ERROR') == 'true',
            'result': '' if os.environ.get('CLAUDE_RESULT') == 'empty' else 'ok',
            'modelUsage': {model: {'inputTokens': 1, 'outputTokens': 1}},
        }
        usage_mode = os.environ.get('CLAUDE_MODEL_USAGE')
        if usage_mode == 'wrong':
            payload['modelUsage'] = {'some-other-model': {'inputTokens': 1}}
        elif usage_mode == 'empty':
            payload['modelUsage'] = {}
        elif usage_mode == 'full-id':
            payload['modelUsage'] = {'claude-opus-5-5': {'inputTokens': 1}}
        elif usage_mode == 'two':
            payload['modelUsage'] = {'claude-opus-5-5': {'inputTokens': 1}, 'claude-sonnet-5': {'inputTokens': 1}}
        return int(os.environ.get('CLAUDE_EXIT', '0')), json.dumps(payload)

    def dispatch(self, *args, **kwargs):
        with patch('agent_harness.dispatch.run_process', side_effect=self.classifier_run), patch('agent_harness.dispatch.run_process_output', side_effect=self.captured_output):
            return run_dispatch(self.config, *args, **kwargs)

    def test_classifier_default_routes_codex_with_exact_configured_settings(self):
        result = self.dispatch('Fix the label', read_only=True)
        self.assertEqual(result, 0)
        self.assertEqual(len(self.calls), 2)
        classifier_args = self.calls[0][0]
        task_args = self.calls[1][0]
        self.assertIn('--output-schema', classifier_args)
        self.assertEqual(classifier_args[classifier_args.index('--model') + 1], 'gpt-6-astra')
        self.assertIn('-s', classifier_args)
        self.assertEqual(classifier_args[classifier_args.index('--profile') + 1], 'agent-harness')
        self.assertIn('--profile', task_args)
        self.assertEqual(task_args[task_args.index('--model') + 1], 'gpt-6-astra')
        self.assertIn('model_reasoning_effort="ultra"', task_args)
        self.assertIn('service_tier="ultrafast"', task_args)
        self.assertIn('read-only', task_args)

    def test_classifier_claude_route_uses_classifier_effort_settings_and_brevity(self):
        payload = json.dumps({'model': 'claude', 'effort': 'high', 'brevity': True, 'reason': 'hard debugging'})
        with patch.dict(os.environ, {'CLASSIFIER_JSON': payload}):
            result = self.dispatch('Find the non-obvious deadlock')
        self.assertEqual(result, 0)
        claude_args, task_text = self.calls[-1]
        self.assertEqual(claude_args[0], 'claude.exe')
        self.assertEqual(claude_args[claude_args.index('--model') + 1], 'fable[1m]')
        self.assertEqual(claude_args[claude_args.index('--effort') + 1], 'high')
        self.assertIn('--settings', claude_args)
        self.assertIn('--plugin-dir', claude_args)
        self.assertTrue(task_text.startswith('Be terse. Answer with the minimum. '))

    def test_explicit_panel_model_is_exact_and_requires_model_usage(self):
        with patch('agent_harness.dispatch.run_process_output', side_effect=self.claude_output):
            result = run_dispatch(self.config, 'Review design', model='claude-opus-5-5', read_only=True)
        self.assertEqual(result, 0)
        argv = self.calls[-1][0]
        self.assertEqual(argv[argv.index('--model') + 1], 'claude-opus-5-5')
        self.assertIn('--strict-mcp-config', argv)
        self.assertEqual(argv[argv.index('--tools') + 1], 'Read,Grep,Glob')

    def test_explicit_claude_error_or_wrong_model_usage_is_failure(self):
        with patch.dict(os.environ, {'CLAUDE_IS_ERROR': 'true'}), patch('agent_harness.dispatch.run_process_output', side_effect=self.claude_output):
            self.assertNotEqual(run_dispatch(self.config, 'Review design', model='claude-opus-5-5'), 0)
        with patch.dict(os.environ, {'CLAUDE_MODEL_USAGE': 'wrong'}), patch('agent_harness.dispatch.run_process_output', side_effect=self.claude_output):
            self.assertNotEqual(run_dispatch(self.config, 'Review design', model='claude-opus-5-5'), 0)

    def test_exact_configured_claude_role_verifies_usage_and_rejects_empty_result(self):
        with patch('agent_harness.dispatch.run_process_output', side_effect=self.claude_output):
            self.assertEqual(run_dispatch(self.config, 'Review design', host='claude', role='panel'), 0)
        with patch.dict(os.environ, {'CLAUDE_MODEL_USAGE': 'empty'}), patch('agent_harness.dispatch.run_process_output', side_effect=self.claude_output):
            self.assertNotEqual(run_dispatch(self.config, 'Review design', host='claude', role='exact panel'), 0)
        with patch.dict(os.environ, {'CLAUDE_RESULT': 'empty'}), patch('agent_harness.dispatch.run_process_output', side_effect=self.claude_output):
            self.assertNotEqual(run_dispatch(self.config, 'Review design', host='claude', role='panel'), 0)

    def test_alias_role_routes_claude_role_back_to_configured_codex_model(self):
        with patch('agent_harness.dispatch.run_process', return_value=0) as run:
            self.assertEqual(run_dispatch(self.config, 'Task', host='claude', role='alias panel'), 0)
        argv = run.call_args.args[0]
        self.assertEqual(argv[argv.index('--model') + 1], 'gpt-6-astra')

    def test_invalid_classifier_json_stops_without_running_task(self):
        with patch.dict(os.environ, {'CLASSIFIER_JSON': 'not json'}):
            result = self.dispatch('Fix the label')
        self.assertNotEqual(result, 0)
        self.assertEqual(len(self.calls), 1)

    def test_unconfigured_model_is_rejected_without_fallback(self):
        with patch('agent_harness.dispatch.run_process', return_value=0) as run:
            result = run_dispatch(self.config, 'Review', model='unknown-model')
        self.assertNotEqual(result, 0)
        run.assert_not_called()

    def test_classifier_only_prints_only_the_decision(self):
        import io
        output = io.StringIO()
        with patch('sys.stdout', output):
            result = self.dispatch('Review architecture', classify_only=True)
        self.assertEqual(result, 0)
        self.assertEqual(len(self.calls), 1)
        self.assertEqual(json.loads(output.getvalue())['model'], 'codex')

    def test_alias_model_accepts_exactly_one_reported_identity_and_prints_it(self):
        import io
        output = io.StringIO()
        with patch.dict(os.environ, {'CLAUDE_MODEL_USAGE': 'full-id'}), patch('sys.stdout', output):
            self.assertEqual(self.dispatch('Review design', model='opus'), 0)
        self.assertIn('claude-opus-5-5', output.getvalue())
        with patch.dict(os.environ, {'CLAUDE_MODEL_USAGE': 'full-id'}):
            self.assertEqual(self.dispatch('Review design', host='claude', role='panel'), 0)
        with patch.dict(os.environ, {'CLAUDE_MODEL_USAGE': 'two'}):
            self.assertNotEqual(self.dispatch('Review design', model='opus'), 0)
            self.assertNotEqual(self.dispatch('Review design', host='claude', role='panel'), 0)
        with patch.dict(os.environ, {'CLAUDE_MODEL_USAGE': 'two'}):
            self.assertEqual(self.dispatch('Review design', host='claude', role='exact panel'), 0)

    def test_interactive_launchers_use_generated_profiles_without_permission_bypass(self):
        with patch('agent_harness.dispatch.run_process', return_value=0) as run:
            self.assertEqual(start_interactive(self.config, 'codex'), 0)
            codex_args = run.call_args.args[0]
            self.assertEqual(codex_args, ['codex.exe', '--profile', 'agent-harness'])
            self.assertEqual(start_interactive(self.config, 'claude'), 0)
            claude_args = run.call_args.args[0]
        self.assertEqual(claude_args[claude_args.index('--model') + 1], 'fable[1m]')
        self.assertIn('--settings', claude_args)
        self.assertIn('--plugin-dir', claude_args)
        self.assertEqual(claude_args[claude_args.index('--permission-mode') + 1], 'default')
        self.assertNotIn('--dangerously-skip-permissions', claude_args)


if __name__ == '__main__':
    unittest.main()
