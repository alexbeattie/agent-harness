from __future__ import annotations

import os
import shlex
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Sequence


def resolve_executable(value: str, *, windows: bool | None = None) -> str:
    """Resolve a command and prefer a native Windows executable over a shim."""
    windows = os.name == 'nt' if windows is None else windows
    candidate = Path(value)
    found = shutil.which(value)
    if windows:
        resolved = Path(found) if found else candidate
        if resolved.suffix.lower() in {'.cmd', '.bat'}:
            native = resolved.with_suffix('.exe')
            if native.is_file():
                return str(native)
            native_found = shutil.which(resolved.stem + '.exe')
            if native_found:
                return native_found
            return str(resolved)
    return found or value


def format_command(argv: Sequence[str], *, windows: bool | None = None) -> str:
    """Format argv for display only; the returned text is never executed."""
    windows = os.name == 'nt' if windows is None else windows
    if not windows:
        return shlex.join(list(argv))
    return '& ' + ' '.join("'" + part.replace("'", "''") + "'" for part in argv)


def run_process(argv: Sequence[str], *, stdin_text: str | None = None, env: dict[str, str] | None = None) -> int:
    """Run one argv vector without a shell and return its exit status."""
    if not argv or any(not isinstance(part, str) for part in argv):
        print('Cannot run an empty or invalid command.', file=sys.stderr)
        return 2
    command = [resolve_executable(argv[0]), *argv[1:]]
    if _is_windows_script(command[0]):
        print(f'Windows command shims cannot run shell-free: {command[0]}; install the native .exe.', file=sys.stderr)
        return 127
    try:
        result = subprocess.run(
            command,
            input=stdin_text,
            text=True,
            encoding='utf-8',
            shell=False,
            check=False,
            env=env,
        )
        return result.returncode
    except (OSError, ValueError) as error:
        print(f'Could not start {format_command(command)}: {error}', file=sys.stderr)
        return 127


def run_process_output(argv: Sequence[str], *, stdin_text: str | None = None, env: dict[str, str] | None = None) -> tuple[int, str]:
    """Run shell-free and capture stdout for machine-readable CLI results."""
    if not argv or any(not isinstance(part, str) for part in argv):
        print('Cannot run an empty or invalid command.', file=sys.stderr)
        return 2, ''
    command = [resolve_executable(argv[0]), *argv[1:]]
    if _is_windows_script(command[0]):
        print(f'Windows command shims cannot run shell-free: {command[0]}; install the native .exe.', file=sys.stderr)
        return 127, ''
    try:
        result = subprocess.run(
            command,
            input=stdin_text,
            text=True,
            encoding='utf-8',
            errors='replace',
            shell=False,
            check=False,
            env=env,
            stdout=subprocess.PIPE,
        )
        return result.returncode, result.stdout or ''
    except (OSError, ValueError) as error:
        print(f'Could not start {format_command(command)}: {error}', file=sys.stderr)
        return 127, ''


def _is_windows_script(value: str) -> bool:
    return Path(value).suffix.lower() in {'.cmd', '.bat'}
