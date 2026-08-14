# WWN-MCP

[![MCP](https://github.com/Wawona/wwn-mcp/actions/workflows/ci.yml/badge.svg)](https://github.com/Wawona/wwn-mcp/actions/workflows/ci.yml)
[![nix (ubuntu-latest)](https://github.com/Wawona/wwn-mcp/actions/workflows/ci.yml/badge.svg?job=nix%20(ubuntu-latest))](https://github.com/Wawona/wwn-mcp/actions/workflows/ci.yml)
[![nix (macos-latest)](https://github.com/Wawona/wwn-mcp/actions/workflows/ci.yml/badge.svg?job=nix%20(macos-latest))](https://github.com/Wawona/wwn-mcp/actions/workflows/ci.yml)

A local-embeddings RAG + **stdio** Model Context Protocol (MCP) server that
gives any Cursor model retrieval-backed knowledge of the Wawona stack: Wayland /
Smithay / Weston / Niri, Apple + Android UI ladders, Vulkan/OpenGL paths, App
Store / Play compliance, and the `wwn-*` patched-software repos. "WWN" = Wawona.

**Host model matches [mcp-nixos](https://github.com/utensils/mcp-nixos):** Cursor
spawns `wwn-mcp` on PATH over stdio. There is **no** public URL / Streamable HTTP
transport (`mcp.wawona.io` was never shipped — do not use it).

## Quick start

```bash
# Install / run with Nix (stdio MCP — same as bare `wwn-mcp`)
nix run github:Wawona/WWN-MCP#wwn-mcp

# Or, without Nix:
pip install -e ".[all]"
wwn-mcp fetch --only wwn-knowledge-wawona   # optional
wwn-mcp index --knowledge                   # first-run knowledge index
wwn-mcp                                     # stdio serve (Cursor spawns this)
```

Point Cursor at it:

```json
{ "mcpServers": {
    "wwn-mcp": { "command": "wwn-mcp" },
    "nixos": { "command": "uvx", "args": ["mcp-nixos"] }
} }
```

With home-manager: `programs.wwn-mcp.enable = true` (see
[docs/deployment.md](docs/deployment.md)).

## Documentation

All documentation lives in [`docs/`](docs/):

- [Overview & architecture](docs/overview.md)
- [Corpus catalog](docs/corpus.md)
- [MCP tools & resources](docs/mcp-tools.md)
- [Deployment (home-manager / dendritic stdio)](docs/deployment.md)
- [Usage (Cursor wiring + local dev)](docs/usage.md)
- [Contributing](docs/contributing.md)

## License

MIT — see [LICENSE](LICENSE). Open source. Third-party documentation and source
that WWN-MCP indexes are fetched at runtime and are never vendored into this
repository; their license notices are surfaced in result citations.
