import io
import unittest
from unittest.mock import MagicMock, patch
from agent_harness.model_catalog import codex_model_pages


class ModelCatalogTests(unittest.TestCase):
    def test_process_exit_during_initialization_is_unverified(self):
        process = MagicMock()
        process.stdin.write.side_effect = BrokenPipeError()
        process.stdin.close.side_effect = BrokenPipeError()
        process.stdout = iter([])
        with patch('agent_harness.model_catalog.subprocess.Popen', return_value=process):
            self.assertIsNone(codex_model_pages('codex.exe'))
        process.wait.assert_called_once()

    def test_malformed_result_is_unverified(self):
        process = MagicMock()
        process.stdout = io.StringIO('[]\n{"id":1,"result":{}}\n{"id":2,"result":null}\n')
        with patch('agent_harness.model_catalog.subprocess.Popen', return_value=process):
            self.assertIsNone(codex_model_pages('codex.exe'))
        process.wait.assert_called_once()
