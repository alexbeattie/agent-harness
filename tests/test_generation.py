import json
import subprocess
import sys
import re
import tempfile
import unittest
from pathlib import Path
from agent_harness.generation import GenerationError, generate

ROOT=Path(__file__).resolve().parents[1]

class GenerationTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)/'package';self.home=Path(self.tmp.name)/'New User Ω'
        (self.root/'config').mkdir(parents=True)
        (self.root/'config/harness.json').write_bytes((ROOT/'config/harness.json').read_bytes())
        (self.root/'VERSION').write_text('9.8.7\n')
        skill=self.root/'source/skills/repo-pstack-mode';skill.mkdir(parents=True)
        (skill/'SKILL.md').write_text('---\nname: repo-pstack-mode\ndescription: team work\n---\nRead [routing](references/host-routing.md).\n')
        (self.root/'config/skills.json').write_text(json.dumps({'skills':[{'name':'repo-pstack-mode','source':'source/skills/repo-pstack-mode','dependencies':[]}]}))

    def test_fresh_and_repeat_install_preserve_files(self):
        first=generate(self.root,self.home)
        skill=self.home/'.agents/skills/repo-pstack-mode/SKILL.md'
        self.assertIn('team work',skill.read_text())
        profile=(self.home/'.codex/agent-harness.config.toml').read_text()
        self.assertIn('[features]\nmulti_agent = true',profile)
        before={str(f.relative_to(self.home)):f.read_bytes() for f in self.home.rglob('*') if f.is_file()}
        second=generate(self.root,self.home)
        self.assertEqual(before,{str(f.relative_to(self.home)):f.read_bytes() for f in self.home.rglob('*') if f.is_file()})
        self.assertEqual(second['changed'],0)
        self.assertGreater(first['changed'],0)

    def test_user_edit_stops_before_any_install_changes(self):
        generate(self.root,self.home)
        target=self.home/'.agents/skills/repo-pstack-mode/SKILL.md';target.write_text('my change')
        source=self.root/'source/skills/repo-pstack-mode/SKILL.md';source.write_text('new generated text')
        with self.assertRaisesRegex(GenerationError,'conflict'):
            generate(self.root,self.home)
        self.assertEqual(target.read_text(),'my change')

    def test_never_touches_existing_personal_config(self):
        config=self.home/'.cursor/mcp.json';config.parent.mkdir(parents=True)
        original=b'{"mcpServers":{"personal":{"url":"https://example.invalid"}}}'
        config.write_bytes(original)
        generate(self.root,self.home)
        self.assertEqual(config.read_bytes(),original)

    def test_rejects_source_traversal(self):
        (self.root/'config/skills.json').write_text(json.dumps({'skills':[{'name':'../escape','source':'../escape','dependencies':[]}]}))
        with self.assertRaises(GenerationError):generate(self.root,self.home)

    def test_symlink_in_destination_is_preserved(self):
        outside=Path(self.tmp.name)/'outside';outside.mkdir()
        self.home.mkdir()
        try:
            (self.home/'.agents').symlink_to(outside,target_is_directory=True)
        except OSError as error:
            self.skipTest(f'This account cannot create symlinks: {error}')
        with self.assertRaisesRegex(GenerationError,'symlink'):
            generate(self.root,self.home)
        self.assertEqual(list(outside.iterdir()),[])

    def test_retired_files_remain_reported_across_repeated_installs(self):
        obsolete=self.root/'source/skills/repo-pstack-mode/obsolete.md'
        obsolete.write_text('Retired reference')
        generate(self.root,self.home)
        obsolete.unlink()
        retired=generate(self.root,self.home)['retained_obsolete']
        self.assertEqual(len(retired),2)
        self.assertEqual(generate(self.root,self.home)['retained_obsolete'],retired)
        self.assertEqual(generate(self.root,self.home,check=True)['retained_obsolete'],retired)
        for name in retired:
            self.assertTrue((self.home/name).is_file())
            (self.home/name).unlink()
        self.assertEqual(generate(self.root,self.home)['retained_obsolete'],[])

    def test_all_installed_skill_links_resolve_for_both_hosts(self):
        generate(ROOT,self.home)
        for base in ('.agents/skills','.agent-harness/claude-plugin/skills'):
            for path in (self.home/base).rglob('*.md'):
                for link in re.findall(r'\]\(([^)]+)\)',path.read_text(encoding='utf-8')):
                    if '://' not in link and not link.startswith('#'):
                        self.assertTrue((path.parent/link.split('#')[0]).exists(),f'{path}: {link}')

    def test_plugin_version_is_read_from_the_version_file(self):
        generate(self.root,self.home)
        plugin=json.loads((self.home/'.agent-harness/claude-plugin/.claude-plugin/plugin.json').read_text(encoding='utf-8'))
        self.assertEqual(plugin['version'],'9.8.7')

    def test_selected_install_preserves_other_agent_files_and_ownership(self):
        generate(self.root,self.home,agents=('cursor',))
        cursor=self.home/'.agent-harness/cursor-user-rules.txt'
        self.assertTrue(cursor.is_file())
        self.assertTrue(cursor.read_text().startswith('# Agent harness'))
        self.assertFalse((self.home/'.codex/agent-harness.config.toml').exists())
        self.assertFalse((self.home/'.agent-harness/claude-plugin').exists())
        cursor.write_text('personal edit')
        generate(self.root,self.home,agents=('claude',))
        self.assertEqual(cursor.read_text(),'personal edit')
        state=json.loads((self.home/'.agent-harness/install-state.json').read_text())['files']
        self.assertIn('.agent-harness/cursor-user-rules.txt',state)
        self.assertIn('.agent-harness/claude-settings.json',state)
        self.assertFalse((self.home/'.codex/agent-harness.config.toml').exists())
        self.assertEqual(generate(self.root,self.home,check=True,agents=('claude',))['changed'],0)

    def test_previous_cursor_project_rule_is_retained_for_manual_review(self):
        generate(self.root,self.home,agents=('cursor',))
        legacy=self.home/'.cursor/rules/agent-harness.mdc'
        legacy.parent.mkdir(parents=True)
        legacy.write_text('edited old rule')
        state=self.home/'.agent-harness/install-state.json'
        payload=json.loads(state.read_text())
        payload['files']['.cursor/rules/agent-harness.mdc']='old-package-hash'
        state.write_text(json.dumps(payload))
        result=generate(self.root,self.home,agents=('cursor',))
        self.assertEqual(result['retained_obsolete'],['.cursor/rules/agent-harness.mdc'])
        self.assertEqual(legacy.read_text(),'edited old rule')

    def test_all_cannot_be_mixed_with_named_agents(self):
        with self.assertRaisesRegex(GenerationError,'all'):
            generate(self.root,self.home,agents=('all','codex'))

    def test_cli_rejects_mixed_all_and_named_agents(self):
        result=subprocess.run([sys.executable,str(ROOT/'harness.py'),'generate','--home',str(self.home),
                               '--agent','all','--agent','codex'],capture_output=True,text=True)
        self.assertEqual(result.returncode,2)
        self.assertIn('Do not mix all',result.stderr)
        self.assertFalse((self.home/'.agent-harness/install-state.json').exists())
