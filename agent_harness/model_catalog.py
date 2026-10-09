from __future__ import annotations

import json
import queue
import subprocess
import threading
import time
from .config import read_version


def codex_model_pages(executable: str) -> list[dict] | None:
    """Use app-server JSON-RPC, waiting for initialize before model/list."""
    try:
        process = subprocess.Popen([executable, 'app-server', '--listen', 'stdio://'],
                                   stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                   stderr=subprocess.DEVNULL, text=True, encoding='utf-8', errors='replace',
                                   shell=False, bufsize=1)
    except OSError:
        return None
    messages: queue.Queue[str | None] = queue.Queue()

    def read_output() -> None:
        assert process.stdout is not None
        for line in process.stdout:
            messages.put(line)
        messages.put(None)

    threading.Thread(target=read_output, daemon=True).start()

    def request(message: dict, expected_id: int) -> dict | None:
        assert process.stdin is not None
        process.stdin.write(json.dumps(message) + '\n')
        process.stdin.flush()
        deadline = time.monotonic() + 20
        while time.monotonic() < deadline:
            try:
                line = messages.get(timeout=max(0.01, deadline - time.monotonic()))
            except queue.Empty:
                return None
            if line is None:
                return None
            try:
                response = json.loads(line)
            except ValueError:
                continue
            if isinstance(response, dict) and response.get('id') == expected_id:
                return response
        return None

    try:
        initialized = request({'jsonrpc': '2.0', 'id': 1, 'method': 'initialize',
                               'params': {'clientInfo': {'name': 'agent-harness-check', 'version': read_version()},
                                          'capabilities': {'experimentalApi': True}}}, 1)
        if not initialized or 'error' in initialized:
            return None
        assert process.stdin is not None
        process.stdin.write(json.dumps({'jsonrpc': '2.0', 'method': 'initialized'}) + '\n')
        process.stdin.flush()
        pages = []
        cursor = None
        for request_id in range(2, 12):
            params = {'limit': 100, 'cursor': cursor}
            response = request({'jsonrpc': '2.0', 'id': request_id,
                                'method': 'model/list', 'params': params}, request_id)
            if not response or 'error' in response:
                return None
            result = response.get('result', {})
            if not isinstance(result, dict):
                return None
            data = result.get('data')
            if not isinstance(data, list):
                return None
            pages.extend(data)
            cursor = result.get('nextCursor')
            if not cursor:
                return pages
        return None
    except (OSError, ValueError):
        return None
    finally:
        if process.stdin:
            try:
                process.stdin.close()
            except OSError:
                pass
        try:
            process.wait(timeout=2)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=2)
