# WWN-MCP

[![MCP](https://github.com/Wawona/wwn-mcp/actions/workflows/ci.yml/badge.svg)](https://github.com/Wawona/wwn-mcp/actions/workflows/ci.yml)
[![nix (ubuntu-latest)](https://github.com/Wawona/wwn-mcp/actions/workflows/ci.yml/badge.svg?job=nix%20(ubuntu-latest))](https://github.com/Wawona/wwn-mcp/actions/workflows/ci.yml)
[![nix (macos-latest)](https://github.com/Wawona/wwn-mcp/actions/workflows/ci.yml/badge.svg?job=nix%20(macos-latest))](https://github.com/Wawona/wwn-mcp/actions/workflows/ci.yml)

**Wawona MCP** — a local-embeddings RAG + stdio [Model Context Protocol](https://modelcontextprotocol.io/)
server that gives any MCP-capable agent retrieval-backed knowledge of the Wawona
stack: Wayland / Smithay / Weston / Niri, Apple + Android UI ladders,
Vulkan/OpenGL paths, App Store / Play compliance, and the `wwn-*`
patched-software repos. **WWN = Wawona.**

This is **not** [mcp-nixos](https://github.com/utensils/mcp-nixos). The *host*
contract is the same idea (the agent host spawns a PATH binary over stdio), but
the corpus, tools, and package are Wawona-only. There is no public URL /
Streamable HTTP transport (`mcp.wawona.io` was never shipped — do not use it).

Works with **any** MCP host that can spawn a stdio server (Cursor, VS Code,
Claude Desktop, Windsurf, Antigravity, Zed, custom agents, …). Cursor is one
client — not the only one. Zed uses `context_servers` instead of `mcpServers`
(see [docs/usage.md](docs/usage.md)).

Install a PATH binary for MCP hosts — do not wire `nix run --refresh` into
editor config (Zed’s ~60s `initialize` timeout → “Context server request
timeout”).

## Quick start

```bash
# Install once (recommended for Cursor / Zed / …)
nix profile install github:Wawona/WWN-MCP

# Terminal smoke (prints JSON / search hits and exits)
wwn-mcp info
wwn-mcp search "watchOS GPU"
# or: nix run github:Wawona/WWN-MCP#wwn-mcp -- info

# Bare `wwn-mcp` / `nix run …#wwn-mcp` on an interactive terminal prints MCP
# host setup help (Cursor + Zed examples) and exits. Your agent must spawn
# the process with piped stdin for the MCP server.
```

### Cursor / VS Code–shaped hosts (`mcpServers`)

```json
{
  "mcpServers": {
    "wwn-mcp": { "command": "wwn-mcp", "args": [] }
  }
}
```

### Zed (`context_servers` in `~/.config/zed/settings.json`)

Use an **absolute** path (Dock-launched Zed has no shell PATH):

```json
{
  "context_servers": {
    "wwn-mcp": {
      "command": "/Users/YOU/.nix-profile/bin/wwn-mcp",
      "args": [],
      "env": {}
    }
  }
}
```

Without Nix:

```bash
pip install -e ".[all]"
wwn-mcp index --knowledge
wwn-mcp info
```

With home-manager / dendritic:

```nix
programs.wwn-mcp.enable = true;
```

See [docs/deployment.md](docs/deployment.md). On first empty DB, `serve`
auto-indexes shipped `knowledge/` **in the background** so `initialize` is
not blocked. For local sibling repos: `wwn-mcp index --local-siblings`
(or `fetch` then `index`).

## Documentation

All documentation lives in [`docs/`](docs/):

- [Overview & architecture](docs/overview.md)
- [Corpus catalog](docs/corpus.md)
- [MCP tools & resources](docs/mcp-tools.md)
- [Deployment (home-manager / dendritic stdio)](docs/deployment.md)
- [Usage (MCP host wiring + local dev)](docs/usage.md)
- [Contributing](docs/contributing.md)

## License

MIT — see [LICENSE](LICENSE). Open source. Third-party documentation and source
that WWN-MCP indexes are fetched at runtime and are never vendored into this
repository; their license notices are surfaced in result citations.
