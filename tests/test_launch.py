import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class LaunchTests(unittest.TestCase):
    def test_piped_stdout_and_stderr_are_utf8_even_under_a_legacy_code_page(self):
        with tempfile.TemporaryDirectory() as directory:
            package = Path(directory)
            (package / 'harness.py').write_text(
                'import sys\n'
                'def main(args):\n'
                '    print("arrow \u2192 check \u2713 " + args[0])\n'
                '    print("stderr \u2192", file=sys.stderr)\n'
                '    return 0\n', encoding='utf-8')
            payload = package / 'arguments.json'
            payload.write_text(json.dumps(['caf\u00e9']), encoding='utf-8')
            env = {key: value for key, value in os.environ.items() if key not in {'PYTHONUTF8', 'PYTHONIOENCODING'}}
            env['PYTHONIOENCODING'] = 'cp1252'
            result = subprocess.run([sys.executable, str(ROOT / 'bin/launch.py'), str(payload), str(package)],
                                    capture_output=True, env=env, check=False)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.decode('utf-8').strip(), 'arrow \u2192 check \u2713 caf\u00e9')
        self.assertEqual(result.stderr.decode('utf-8').strip(), 'stderr \u2192')


if __name__ == '__main__':
    unittest.main()
