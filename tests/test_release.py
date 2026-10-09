import json
import tempfile
import unittest
import zipfile
from pathlib import Path
from tools.package_release import REQUIRED, audit, default_output, package, source_files

class ReleaseTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)
        (self.root/'config').mkdir()
        (self.root/'config/harness.json').write_text(json.dumps({'connections':{}}))
        for name in REQUIRED-{'config/harness.json','VERSION'}:
            path=self.root/name
            path.parent.mkdir(parents=True,exist_ok=True)
            path.write_text('A safe package.')
        (self.root/'VERSION').write_text('2.3.4\n')

    def test_release_name_uses_the_version_file(self):
        self.assertEqual(default_output(self.root),self.root/'dist/agent-harness-2.3.4.zip')

    def test_archive_has_only_selected_sources_and_manifest(self):
        (self.root/'private.txt').write_text('Do not ship.')
        output=self.root/'dist/bundle.zip'
        result=package(self.root,output)
        with zipfile.ZipFile(output) as archive:
            names=archive.namelist()
            self.assertNotIn('agent-harness/private.txt',names)
            manifest=json.loads(archive.read('agent-harness/FILE-SHA256.json'))
            self.assertEqual(set(manifest),REQUIRED)
        self.assertEqual(result['files'],len(REQUIRED))
        self.assertTrue(output.with_suffix('.zip.sha256').is_file())

    def test_literal_password_is_not_shipped(self):
        (self.root/'config/bad.json').write_text(json.dumps({'password':''.join(['private','example','value'])}))
        self.assertTrue(any('literal secret assignment' in x for x in audit(self.root,source_files(self.root))))
        with self.assertRaises(ValueError):package(self.root,self.root/'dist/no.zip')

    def test_runtime_auth_file_is_rejected(self):
        (self.root/'config/auth.json').write_text('{}')
        self.assertTrue(any('private/runtime' in x for x in audit(self.root,source_files(self.root))))

    def test_missing_installer_blocks_release(self):
        (self.root/'install.ps1').unlink()
        with self.assertRaisesRegex(ValueError,'required package file is missing'):
            package(self.root,self.root/'dist/incomplete.zip')
