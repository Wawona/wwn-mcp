# WWN-MCP

A local-embeddings RAG + Model Context Protocol (MCP) server that gives any
Cursor model retrieval-backed knowledge of the Wawona stack: Wayland/Smithay/
Weston, the Apple (OS 26 / Liquid Glass) and Android (Material 3 Expressive) UI
ladders, the Vulkan/OpenGL graphics paths, App Store / Play Store compliance,
and Wawona's own source, docs, and patched dependencies. "WWN" = Wawona.

## Quick start

```bash
# Run the server locally (Streamable HTTP on http://127.0.0.1:8765/mcp)
nix run github:Wawona/WWN-MCP#wwn-mcp -- serve

# Or, without Nix:
pip install -e .
wwn-mcp fetch        # mirror corpus sources declared in corpus.toml
wwn-mcp index        # chunk + embed into the sqlite hybrid index
wwn-mcp serve        # start the MCP server
```

Point Cursor at it by adding a remote MCP entry (see
[docs/usage.md](docs/usage.md)):

```json
{ "mcpServers": { "wwn-mcp": { "url": "https://mcp.wawona.io/mcp",
  "headers": { "Authorization": "Bearer ${WWN_MCP_TOKEN}" } } } }
```

## Documentation

All documentation lives in [`docs/`](docs/):

- [Overview & architecture](docs/overview.md)
- [Corpus catalog](docs/corpus.md)
- [MCP tools & resources](docs/mcp-tools.md)
- [Deployment (NixOS, mcp.wawona.io)](docs/deployment.md)
- [Usage (Cursor wiring + local dev)](docs/usage.md)
- [Contributing](docs/contributing.md)

## License

MIT — see [LICENSE](LICENSE). Open source. Third-party documentation and source
that WWN-MCP indexes are fetched at runtime and are never vendored into this
repository; their license notices are surfaced in result citations.
