import json
import sys
import unittest
from agent_harness.process import run_process_output


class ProcessIntegrationTests(unittest.TestCase):
    def test_real_child_preserves_arguments_and_utf8_task(self):
        arguments = ['a file;$(whoami).txt', 'Say "hello".', '', 'tail\\', 'café Ω']
        program = 'import json,sys; print(json.dumps([sys.argv[1:], sys.stdin.read()]))'
        code, output = run_process_output(
            [sys.executable, '-X', 'utf8', '-c', program, *arguments],
            stdin_text='A task with café and Ω\nSecond line.',
        )
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(output), [arguments, 'A task with café and Ω\nSecond line.'])
