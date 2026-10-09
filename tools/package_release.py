"""Check the distributable source and produce a ZIP with a checksum manifest."""
from __future__ import annotations
import argparse
import hashlib
import json
import re
import sys
import zipfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from agent_harness.config import read_version
TOP_FILES={'harness.py','install.ps1','check.ps1','README.md','THIRD-PARTY-NOTICES.md','AGENTS.md','.gitignore','.gitattributes','VERSION'}
TOP_DIRS={'agent_harness','source','config','assets','bin','scripts','tools','tests','docs'}
SKIP={'__pycache__','.pytest_cache','.DS_Store'}
REQUIRED={'install.ps1','check.ps1','harness.py','README.md','VERSION','config/harness.json','config/skills.json'}
RULES={
 'provider credential':r'\b(?:sk-(?:proj-|ant-)?[A-Za-z0-9_-]{20,}|gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|xox[baprs]-[A-Za-z0-9-]{12,}|ATATT[A-Za-z0-9_=-]{20,})',
 'AWS access key':r'\b(?:AKIA|ASIA)[A-Z0-9]{16}\b',
 'private key':r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----',
 'personal Mac path':r'/Users/[A-Za-z0-9_.-]+/',
 'customer ticket':r'\bKLA-\d+\b',
 'literal secret assignment':r'''(?i)(?:password|api[_-]?key|client[_-]?secret|authorization|access[_-]?token|cookie|\btoken)["']?\s*[:=]\s*["'][^"'\n]{8,}["']''',
 'credential URL':r'https?://[^\s/@:]+:[^\s/@]+@',
}


def source_files(root: Path) -> list[Path]:
    files=[]
    for path in sorted(root.rglob('*')):
        relative=path.relative_to(root)
        if any(part in SKIP for part in relative.parts):continue
        if relative.parts[0] not in TOP_DIRS and str(relative) not in TOP_FILES:continue
        if path.is_symlink():raise ValueError(f'Symlink is not distributable: {relative}')
        if path.is_file():files.append(path)
    return files


def audit(root: Path, files: list[Path]) -> list[str]:
    present={path.relative_to(root).as_posix() for path in files}
    problems=[f'{name}: required package file is missing' for name in sorted(REQUIRED-present)]
    for path in files:
        relative=path.relative_to(root)
        if path.name in {'auth.json','.credentials.json','credentials','history.jsonl'} or path.suffix in {'.log','.sqlite','.db','.zip','.pyc','.jsonl'}:
            problems.append(f'{relative}: private/runtime file');continue
        if path.name.startswith('.env') and path.name!='.env.example':
            problems.append(f'{relative}: environment file');continue
        try:content=path.read_text(encoding='utf-8')
        except UnicodeError:
            problems.append(f'{relative}: binary file requires separate review');continue
        for label,pattern in RULES.items():
            for line,text in enumerate(content.splitlines(),1):
                if re.search(pattern,text):problems.append(f'{relative}:{line}: {label}')
    config=json.loads((root/'config/harness.json').read_text())
    for name,connection in config.get('connections',{}).items():
        if connection.get('enabled') or connection.get('token') or connection.get('password'):
            problems.append(f'config/harness.json: {name} must ship disabled without credentials')
    return problems


def default_output(root: Path) -> Path:
    return root/'dist'/f'agent-harness-{read_version(root)}.zip'


def package(root: Path, output: Path) -> dict:
    files=source_files(root)
    problems=audit(root,files)
    if problems:raise ValueError('Package review failed:\n'+'\n'.join(problems))
    manifest={path.relative_to(root).as_posix():hashlib.sha256(path.read_bytes()).hexdigest() for path in files}
    output.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(output,'w',zipfile.ZIP_DEFLATED) as archive:
        for path in files:
            archive.write(path,'agent-harness/'+path.relative_to(root).as_posix())
        archive.writestr('agent-harness/FILE-SHA256.json',json.dumps(manifest,indent=2)+'\n')
    digest=hashlib.sha256(output.read_bytes()).hexdigest()
    output.with_suffix(output.suffix+'.sha256').write_text(f'{digest}  {output.name}\n')
    return {'files':len(files),'archive':str(output),'sha256':digest}


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check',action='store_true')
    parser.add_argument('--output',type=Path,default=None)
    args=parser.parse_args()
    try:
        if args.check:
            files=source_files(ROOT);problems=audit(ROOT,files)
            if problems:raise ValueError('\n'.join(problems))
            print(f'PASS: {len(files)} source files passed the package pattern checks. Manual review is still required before release.')
        else:print(json.dumps(package(ROOT,args.output or default_output(ROOT)),indent=2))
    except (OSError,ValueError) as error:
        print(error,file=sys.stderr);raise SystemExit(1)
