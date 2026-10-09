import copy
import json
import tempfile
import unittest
from pathlib import Path
from agent_harness.config import ConfigError, load_config, read_version, resolve_role

ROOT = Path(__file__).resolve().parents[1]

class ConfigTests(unittest.TestCase):
    def test_preserves_distinct_host_choices(self):
        config = load_config(ROOT)
        self.assertEqual(resolve_role(config, 'codex', 'swarm workers'), ['gpt-6-luna'])
        self.assertEqual(resolve_role(config, 'cursor', 'swarm workers'), ['gpt-5.6-sol-high'])
        self.assertEqual(resolve_role(config, 'claude', 'swarm workers'), ['sonnet'])
        self.assertEqual(resolve_role(config, 'claude', 'main'), ['fable[1m]'])

    def test_missing_role_names_setting_without_fallback(self):
        with self.assertRaisesRegex(ConfigError, 'hosts.codex.roles.missing'):
            resolve_role(load_config(ROOT), 'codex', 'missing')

    def test_grouped_role_is_available(self):
        self.assertEqual(resolve_role(load_config(ROOT), 'codex', 'refactoring'), ['gpt-6-sol'])

    def test_invalid_model_cannot_be_passed_to_shell(self):
        cfg = json.loads((ROOT/'config/harness.json').read_text())
        cfg['hosts']['codex']['model'] = 'bad; echo unsafe'
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/'config'; path.mkdir()
            (path/'harness.json').write_text(json.dumps(cfg))
            with self.assertRaisesRegex(ConfigError, 'hosts.codex.model'):
                load_config(Path(directory))

    def test_missing_host_fails_clearly(self):
        cfg = load_config(ROOT)
        with self.assertRaisesRegex(ConfigError, 'Unknown host'):
            resolve_role(cfg, 'unlisted', 'main')

    def test_version_comes_from_the_single_version_file(self):
        version = read_version(ROOT)
        self.assertEqual(version, (ROOT / 'VERSION').read_text(encoding='utf-8').strip())
        self.assertRegex(version, r'^\d+\.\d+\.\d+$')
        with tempfile.TemporaryDirectory() as directory:
            (Path(directory) / 'VERSION').write_text('not a version\n', encoding='utf-8')
            with self.assertRaisesRegex(ConfigError, 'VERSION'):
                read_version(Path(directory))
