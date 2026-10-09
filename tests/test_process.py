import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from agent_harness.process import format_command, resolve_executable, run_process, run_process_output


class ProcessTests(unittest.TestCase):
    def test_argv_and_unicode_stdin_are_passed_without_shell_interpretation(self):
        completed = subprocess.CompletedProcess(args=[], returncode=0)
        with patch('agent_harness.process.subprocess.run', return_value=completed) as run:
            code = run_process(['tool.exe', 'x; touch marker', 'space value'], stdin_text='café')
        self.assertEqual(code, 0)
        self.assertEqual(run.call_args.args[0], ['tool.exe', 'x; touch marker', 'space value'])
        self.assertEqual(run.call_args.kwargs['input'], 'café')
        self.assertIs(run.call_args.kwargs['shell'], False)
        self.assertEqual(run.call_args.kwargs['encoding'], 'utf-8')

    def test_process_failure_is_returned_without_retry(self):
        completed = subprocess.CompletedProcess(args=[], returncode=19)
        with patch('agent_harness.process.subprocess.run', return_value=completed) as run:
            self.assertEqual(run_process(['tool.exe']), 19)
        run.assert_called_once()

    def test_captured_output_uses_utf8_and_returns_exit_code(self):
        completed = subprocess.CompletedProcess(args=[], returncode=7, stdout='résultat')
        with patch('agent_harness.process.subprocess.run', return_value=completed) as run:
            self.assertEqual(run_process_output(['tool.exe']), (7, 'résultat'))
        self.assertEqual(run.call_args.kwargs['encoding'], 'utf-8')
        self.assertEqual(run.call_args.kwargs['errors'], 'replace')
        self.assertIs(run.call_args.kwargs['shell'], False)

    def test_powershell_review_command_quotes_each_argument(self):
        shown = format_command(['C:/Tools/aws.exe', 's3', 'cp', 'file with spaces', 'x&y'], windows=True)
        self.assertEqual(shown, "& 'C:/Tools/aws.exe' 's3' 'cp' 'file with spaces' 'x&y'")
        apostrophe = format_command(["C:/Alex's Tools/aws.exe", "it's safe"], windows=True)
        self.assertEqual(apostrophe, "& 'C:/Alex''s Tools/aws.exe' 'it''s safe'")

    def test_windows_resolution_prefers_native_exe_over_cmd(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            native = root / 'twg.exe'
            shim = root / 'twg.cmd'
            native.touch()
            shim.touch()
            self.assertEqual(resolve_executable(str(shim), windows=True), str(native))

    def test_bare_windows_cmd_resolution_looks_for_native_exe(self):
        with patch('agent_harness.process.shutil.which', side_effect=['C:/Tools/twg.cmd', 'C:/Tools/twg.exe']):
            self.assertEqual(resolve_executable('twg', windows=True), 'C:/Tools/twg.exe')

    def test_unpaired_command_shim_is_never_invoked(self):
        with patch('agent_harness.process.resolve_executable', return_value='C:/Tools/twg.cmd'), patch('agent_harness.process.subprocess.run') as run:
            self.assertEqual(run_process(['twg']), 127)
        run.assert_not_called()


if __name__ == '__main__':
    unittest.main()
