# Usage — Cursor wiring & local dev

## Connect Cursor (any Wawona-org repo)

Wawona development uses **multiple repos** under `~/Wawona/`. Add MCP config to
each repo's `.cursor/mcp.json` (or rely on dendritic / home-manager to write it):

```json
{
  "mcpServers": {
    "wwn-mcp": {
      "command": "wwn-mcp"
    },
    "nixos": {
      "command": "uvx",
      "args": ["mcp-nixos"]
    },
    "xcodebuild": {
      "command": "npx",
      "args": ["-y", "xcodebuildmcp@latest", "mcp"]
    },
    "lldb": {
      "command": "lldb-mcp",
      "args": []
    }
  }
}
```

**stdio only.** There is no `https://mcp.wawona.io/mcp` — that hostname was
never shipped. Install the package (`programs.wwn-mcp.enable` or
`nix profile install github:Wawona/WWN-MCP`) so `wwn-mcp` is on PATH.

Companion servers:

- **`nixos`** — live nixpkgs/options (utensils/mcp-nixos), also stdio via `uvx`.
- **`xcodebuild` / `lldb`** — macOS-local action tools; not part of wwn-mcp.

## Run a local server (stdio) with Nix

```bash
# Build / run (bare argv = stdio serve)
nix run github:Wawona/WWN-MCP#wwn-mcp

# Index first (knowledge-only is enough to start)
nix run github:Wawona/WWN-MCP#wwn-mcp -- index --knowledge
```

Or from a checkout:

```bash
nix run .#wwn-mcp -- info
nix run .#wwn-mcp -- index --local-siblings
nix run .#wwn-mcp          # stdio
```

## Local development

```bash
nix develop
python -m wwn_mcp.cli info

# Without Nix:
pip install -e ".[all,dev]"

wwn-mcp fetch --only smithay wayland-protocols
wwn-mcp index --only smithay wayland-protocols
wwn-mcp search "delegate_xdg_shell" --kind code -k 5
wwn-mcp   # stdio serve
```

### Useful environment variables

| var | default | meaning |
|-----|---------|---------|
| `WWN_MCP_DATA_DIR` | `~/.local/share/wwn-mcp` (XDG); `./data` in a writable checkout | runtime data root |
| `WWN_MCP_CORPUS_TOML` | packaged copy, else `./corpus.toml` | manifest path |
| `WWN_MCP_DB` | `<data>/index.sqlite` | sqlite index path |
| `WWN_MCP_MODEL` | `BAAI/bge-small-en-v1.5` | embedding model |

### Notes

- `fetch` skips `enabled = false` sources and continues on per-source failures.
- `index` is incremental by content hash.
- Empty index on serve → auto `index --knowledge`.
- Without `fastembed`/`sqlite-vec`, search still works (hashing + FTS).
