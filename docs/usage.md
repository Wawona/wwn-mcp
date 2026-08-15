# Usage — MCP host wiring & local dev

## Connect any MCP agent

WWN-MCP speaks **stdio MCP**. It is **not** Cursor-only. Any host that can
spawn a local command works (Cursor, VS Code, Claude Desktop, Windsurf,
Antigravity, **Zed**, custom agents). The JSON key name differs by host —
the `command` / `args` payload is the same.

Prefer a **PATH / absolute binary** (fast spawn). Do **not** put
`nix run --refresh …` in MCP host config — flake eval/build often exceeds
host `initialize` timeouts (~60s in Zed → “Context server request timeout”).

### Cursor / VS Code / Claude Desktop / Windsurf

```json
{
  "mcpServers": {
    "wwn-mcp": {
      "command": "wwn-mcp",
      "args": []
    }
  }
}
```

Until `wwn-mcp` is on PATH (still avoid `--refresh`):

```json
{
  "mcpServers": {
    "wwn-mcp": {
      "command": "nix",
      "args": ["run", "github:Wawona/WWN-MCP#wwn-mcp"]
    }
  }
}
```

### Zed

Zed uses `context_servers` in `~/.config/zed/settings.json` (or project
`.zed/settings.json`). `args` is required (use `[]` when empty). Prefer an
**absolute** path — Dock-launched Zed does not inherit your shell `PATH`:

```json
{
  "context_servers": {
    "wwn-mcp": {
      "command": "/Users/YOU/.local/bin/wwn-mcp",
      "args": [],
      "env": {}
    }
  }
}
```

Install once:

```bash
nix profile install github:Wawona/WWN-MCP
# or: ln -sf "$(nix build --no-link --print-out-paths github:Wawona/WWN-MCP#wwn-mcp)/bin/wwn-mcp" ~/.local/bin/wwn-mcp
```

Check **Settings → AI → MCP Servers** — green means active. If you see
“Context server request timeout”, the host is still spawning a slow
`nix run --refresh` (or an old build blocked on indexing); switch to a PATH
binary.

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
Antigravity, VS Code, Zed `context_servers`). Same `command` / `args` shape.

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

# Bare argv on a TTY prints host-setup help (Cursor + Zed examples); agents
# spawn with piped stdin for the real MCP server
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
| `WWN_MCP_FORCE_STDIO` | unset | `1` forces stdio even on a TTY (debug) |
