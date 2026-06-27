# Usage — Cursor wiring & local dev

## Connect Cursor (any Wawona-org repo)

Add a remote MCP entry to the repo's `.cursor/mcp.json` (this is already done in
the Wawona repo):

```json
{
  "mcpServers": {
    "wwn-mcp": {
      "url": "https://mcp.wawona.io/mcp",
      "headers": { "Authorization": "Bearer ${WWN_MCP_TOKEN}" }
    },
    "nixos": {
      "command": "uvx",
      "args": ["mcp-nixos"]
    },
    "xcodebuild": {
      "command": "npx",
      "args": ["-y", "xcodebuildmcp@latest", "mcp"]
    }
  }
}
```

Set `WWN_MCP_TOKEN` in your environment (never commit it). Cursor will expose
the WWN-MCP tools (`search`, `get_protocol`, `get_patch`, …) plus the companion
**`nixos`** tools (`nix`, `nix_versions`) for accurate nixpkgs/options/version
data, and the **`xcodebuild`** tools (getsentry/XcodeBuildMCP) for building,
running, testing, and log-capturing the Apple Xcode projects. Pair them with an
always-applied rule so models query them automatically — see the Wawona repo's
`.cursor/rules/wawona-context.mdc` and `AGENTS.md`.

> **Companion server placement.** `nixos` is a stateless API client that runs
> anywhere, so WWN-MCP **co-hosts** it on the NixOS host (also reachable at
> `https://mcp.wawona.io/nixos/mcp`). `xcodebuild` requires **macOS + Xcode 16+**
> (it drives `xcodebuild`/`simctl`/`devicectl`), so it is **developer-local
> only** — run via `npx`/Homebrew on your Mac; it is *not* hosted on the Linux
> server.

The `nixos` entry above runs MCP-NixOS locally via `uvx` (no Nix required). To
use the **hosted** companion instead (co-deployed by the WWN-MCP NixOS module),
point it at the remote endpoint:

```json
{ "mcpServers": { "nixos": {
  "url": "https://mcp.wawona.io/nixos/mcp",
  "headers": { "Authorization": "Bearer ${WWN_MCP_TOKEN}" }
} } }
```

## Run a local server (stdio) for a single machine

You can skip the hosted endpoint and run WWN-MCP locally over stdio:

```jsonc
// .cursor/mcp.json
{ "mcpServers": { "wwn-mcp": {
  "command": "nix",
  "args": ["run", "github:Wawona/WWN-MCP#wwn-mcp", "--", "serve", "--transport", "stdio"]
} } }
```

## Local development

```bash
# With Nix:
nix develop                       # dev shell with python + deps + caddy
python -m wwn_mcp.cli info

# Without Nix:
pip install -e ".[all,dev]"       # all = fastembed + sqlite-vec; falls back if omitted

# Pipeline
wwn-mcp fetch --only smithay wayland-protocols   # fetch a subset
wwn-mcp index --only smithay wayland-protocols   # chunk + embed + store
wwn-mcp search "delegate_xdg_shell" --kind code -k 5
wwn-mcp serve --transport http   # http://127.0.0.1:8765/mcp
```

### Useful environment variables

| var | default | meaning |
|-----|---------|---------|
| `WWN_MCP_DATA_DIR` | `./data` | runtime data root |
| `WWN_MCP_CORPUS_TOML` | `./corpus.toml` | manifest path |
| `WWN_MCP_DB` | `<data>/index.sqlite` | sqlite index path |
| `WWN_MCP_MODEL` | `BAAI/bge-small-en-v1.5` | embedding model |
| `WWN_MCP_HOST` / `WWN_MCP_PORT` | `127.0.0.1` / `8765` | serve bind |
| `WWN_MCP_TOKEN` | — | bearer token (auth is enforced at the proxy) |

### Notes

- `fetch` skips `enabled = false` sources and logs/continues on per-source
  failures, so a flaky upstream never aborts the run.
- `index` is incremental: unchanged chunks (by content hash) are skipped and
  removed chunks are pruned.
- Without `fastembed`/`sqlite-vec`, search still works (hashing embedder +
  brute-force/FTS); install the `all` extra for full semantic quality.
