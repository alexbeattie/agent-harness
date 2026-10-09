from __future__ import annotations

import json
import sys
from pathlib import Path


def main() -> int:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, 'reconfigure'):
            stream.reconfigure(encoding='utf-8', errors='replace')
    if len(sys.argv) != 3:
        print('PowerShell launcher expected an argv file and package root.', file=sys.stderr)
        return 2
    payload_path, root = Path(sys.argv[1]), Path(sys.argv[2])
    try:
        arguments = json.loads(payload_path.read_text(encoding='utf-8'))
    except (OSError, ValueError) as error:
        print(f'PowerShell launcher could not read its temporary arguments: {error}', file=sys.stderr)
        return 2
    finally:
        payload_path.unlink(missing_ok=True)
    if not isinstance(arguments, list) or any(not isinstance(value, str) for value in arguments):
        print('PowerShell launcher received invalid argument data.', file=sys.stderr)
        return 2
    sys.path.insert(0, str(root))
    from harness import main as harness_main
    return harness_main(arguments)


if __name__ == '__main__':
    raise SystemExit(main())
