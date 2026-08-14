# Usage — MCP host wiring & local dev

## Connect any MCP agent

WWN-MCP speaks **stdio MCP**. Any host that can spawn a local command works
(Cursor, VS Code, Claude Desktop, Windsurf, Antigravity, Zed, custom agents).
Add a server entry shaped like:

```json
{
  "mcpServers": {
    "wwn-mcp": {
      "command": "wwn-mcp"
    }
  }
}
```

Wawona multi-repo checkouts often also enable companion servers (optional —
not part of this package):

```json
{
  "mcpServers": {
    "wwn-mcp": { "command": "wwn-mcp" },
    "nixos": { "command": "uvx", "args": ["mcp-nixos"] },
    "xcodebuild": {
      "command": "npx",
      "args": ["-y", "xcodebuildmcp@latest", "mcp"]
    },
    "lldb": { "command": "lldb-mcp", "args": [] }
  }
}
```

Dendritic / home-manager can write IDE-specific files (`.cursor/mcp.json`,
Antigravity, VS Code). Other hosts use their own MCP config path — same
`command` / `args` shape.

**stdio only.** There is no `https://mcp.wawona.io/mcp` — that hostname was
never shipped. Install the package (`programs.wwn-mcp.enable` or
`nix profile install github:Wawona/WWN-MCP`) so `wwn-mcp` is on PATH.

Companion servers:

- **`nixos`** — live nixpkgs/options (utensils/mcp-nixos), also stdio via `uvx`.
- **`xcodebuild` / `lldb`** — macOS-local action tools; not part of wwn-mcp.

## Run with Nix

```bash
# Terminal smoke
nix run github:Wawona/WWN-MCP#wwn-mcp -- info
nix run github:Wawona/WWN-MCP#wwn-mcp -- index --knowledge

# Bare argv on a TTY prints host-setup help; agents spawn with piped stdin
nix run github:Wawona/WWN-MCP#wwn-mcp
```

Or from a checkout:

```bash
nix run .#wwn-mcp -- info
nix run .#wwn-mcp -- index --local-siblings
nix run .#wwn-mcp          # stdio (when stdin is not a TTY)
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
wwn-mcp info
```

### Useful environment variables

| var | default | meaning |
|-----|---------|---------|
| `WWN_MCP_DATA_DIR` | `~/.local/share/wwn-mcp` (XDG); `./data` in a writable checkout | runtime data root |
| `WWN_MCP_CORPUS_TOML` | packaged copy, else `./corpus.toml` | manifest path |
| `WWN_MCP_DB` | `<data>/index.sqlite` | sqlite index path |
| `WWN_MCP_MODEL` | `BAAI/bge-small-en-v1.5` | embedding model |
