"""Stdio MCP handshake smoke — same contract Cursor, Zed, and other hosts use.

Spawns ``wwn-mcp`` with piped stdin/stdout (neither is a TTY) and speaks a
minimal JSON-RPC session: initialize → tools/list → tools/call search.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


def _rpc(proc: subprocess.Popen, msg: dict) -> dict | None:
    line = json.dumps(msg, separators=(",", ":")) + "\n"
    assert proc.stdin is not None and proc.stdout is not None
    proc.stdin.write(line)
    proc.stdin.flush()
    # Read until we get a JSON object with matching id (skip notifications / logs).
    want_id = msg.get("id")
    deadline_lines = 50
    for _ in range(deadline_lines):
        raw = proc.stdout.readline()
        if not raw:
            raise RuntimeError("wwn-mcp closed stdout early")
        raw = raw.strip()
        if not raw.startswith("{"):
            continue
        try:
            obj = json.loads(raw)
        except json.JSONDecodeError:
            continue
        if want_id is not None and obj.get("id") != want_id:
            continue
        return obj
    raise RuntimeError(f"no JSON-RPC response for id={want_id}")


def test_stdio_mcp_handshake(tmp_path, monkeypatch):
    """Agent-host shape: piped stdio, initialize, list tools, call search."""
    data = tmp_path / "data"
    data.mkdir()
    monkeypatch.setenv("WWN_MCP_DATA_DIR", str(data))
    monkeypatch.setenv("WWN_MCP_FORCE_STDIO", "1")

    # Prefer in-tree module so CI does not need a packaged binary.
    env = os.environ.copy()
    env["WWN_MCP_DATA_DIR"] = str(data)
    env["WWN_MCP_FORCE_STDIO"] = "1"
    # Make src importable when running via python -m
    root = Path(__file__).resolve().parents[1]
    env["PYTHONPATH"] = str(root / "src") + os.pathsep + env.get("PYTHONPATH", "")

    proc = subprocess.Popen(
        [sys.executable, "-m", "wwn_mcp.cli", "serve"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env=env,
        cwd=str(root),
    )
    try:
        init = _rpc(
            proc,
            {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {"name": "wwn-mcp-test", "version": "0"},
                },
            },
        )
        assert init is not None
        assert "result" in init, init
        assert init["result"].get("serverInfo", {}).get("name") == "wwn-mcp"

        # notifications/initialized — no response expected
        assert proc.stdin is not None
        proc.stdin.write(
            json.dumps(
                {"jsonrpc": "2.0", "method": "notifications/initialized", "params": {}}
            )
            + "\n"
        )
        proc.stdin.flush()

        tools = _rpc(proc, {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}})
        assert tools is not None and "result" in tools, tools
        names = {t["name"] for t in tools["result"].get("tools", [])}
        assert "search" in names
        assert "list_projects" in names

        # Optional: call search (index may be empty; tool must still return)
        call = _rpc(
            proc,
            {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/call",
                "params": {
                    "name": "search",
                    "arguments": {"query": "watchOS GPU", "top_k": 3},
                },
            },
        )
        assert call is not None and "result" in call, call
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
