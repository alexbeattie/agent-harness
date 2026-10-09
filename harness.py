from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path
from agent_harness.config import load_config, read_version, resolve_role

ROOT=Path(__file__).resolve().parent


def main(argv: list[str] | None = None) -> int:
    parser=argparse.ArgumentParser(description='Agent skills and guarded terminal commands.')
    parser.add_argument('--version', action='version', version=f'agent-harness {read_version(ROOT)}')
    sub=parser.add_subparsers(dest='command',required=True)
    generate=sub.add_parser('generate',help='Install managed skills and settings without changing personal files.')
    generate.add_argument('--home',type=Path,default=Path.home())
    generate.add_argument('--check',action='store_true')
    check=sub.add_parser('check',help='Check installation and explain missing setup.')
    check.add_argument('--home',type=Path,default=Path.home())
    check.add_argument('--probe-models',action='store_true',help='Run account checks; model probes may consume quota or cost money.')
    dispatch=sub.add_parser('dispatch',help='Classify a task or hand it to a configured model.')
    task=dispatch.add_mutually_exclusive_group(required=True)
    task.add_argument('--task')
    task.add_argument('--task-file',type=Path)
    dispatch.add_argument('--host',choices=['codex','claude'])
    dispatch.add_argument('--model')
    dispatch.add_argument('--role')
    dispatch.add_argument('--quota-used',type=float)
    dispatch.add_argument('--classify-only',action='store_true')
    dispatch.add_argument('--read-only',action='store_true')
    external=sub.add_parser('external',help='Run an AWS or TWG command with write confirmation.')
    external.add_argument('--tool',required=True,choices=['aws','twg'])
    external.add_argument('arguments',nargs=argparse.REMAINDER)
    for host in ['codex','claude']:
        sub.add_parser(host,help=f'Start {host} with the generated team configuration.')
    models=sub.add_parser('models',help='Show the configured model values, without contacting a service.')
    models.add_argument('--host',choices=['codex','cursor','claude'])
    models.add_argument('--role')
    args=parser.parse_args(argv)
    try:
        config=load_config(ROOT)
        if args.command=='generate':
            from agent_harness.generation import generate
            result=generate(ROOT,args.home,args.check)
            print(json.dumps(result,indent=2))
            return 1 if args.check and result['changed'] else 0
        if args.command=='check':
            from agent_harness.checks import run_checks
            return run_checks(ROOT,args.home,args.probe_models)
        if args.command=='dispatch':
            from agent_harness.dispatch import run_dispatch
            text=args.task_file.read_text(encoding='utf-8-sig') if args.task_file else args.task
            if not text.strip():
                raise ValueError('The task is empty. Write the task in UTF-8 text and retry.')
            return run_dispatch(config,text,host=args.host,model=args.model,role=args.role,
                                classify_only=args.classify_only,quota_used=args.quota_used,read_only=args.read_only)
        if args.command=='external':
            from agent_harness.guard import run_external
            arguments=args.arguments[1:] if args.arguments[:1]==['--'] else args.arguments
            return run_external(config,args.tool,arguments)
        if args.command in ('codex','claude'):
            from agent_harness.dispatch import start_interactive
            return start_interactive(config,args.command)
        if args.command=='models':
            if args.role and not args.host:
                raise ValueError('--role needs --host.')
            values=resolve_role(config,args.host,args.role) if args.role else config['hosts'].get(args.host,config['hosts'])
            print(json.dumps(values,indent=2))
            return 0
    except (ValueError,OSError) as error:
        print(f'Cannot continue: {error}',file=sys.stderr)
        return 2
    except KeyboardInterrupt:
        print('Stopped. No approval was granted.',file=sys.stderr)
        return 130
    return 2


if __name__=='__main__':
    raise SystemExit(main())
