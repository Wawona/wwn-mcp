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

## Run a local server (stdio) with Nix — no hosting required

This is the recommended setup for a single developer machine. Cursor launches
the server on demand via Nix and talks to it over stdio (no port, no token).

**1. Build an index once** (the server needs a populated index to answer). Fetch
+ index the whole corpus, or a subset to start fast:

```bash
# whole corpus (long: clones many repos + embeds on CPU)
nix run github:Wawona/WWN-MCP -- fetch
nix run github:Wawona/WWN-MCP -- index

# …or a subset first
nix run github:Wawona/WWN-MCP -- fetch --only crate2nix fastlane-docs egl-registry
nix run github:Wawona/WWN-MCP -- index --only crate2nix fastlane-docs egl-registry
```

The index lands in `$XDG_DATA_HOME/wwn-mcp` (default `~/.local/share/wwn-mcp`).

**2. Point Cursor at it** in `.cursor/mcp.json`:

```jsonc
// .cursor/mcp.json
{ "mcpServers": { "wwn-mcp": {
  // absolute nix path: Cursor-spawned servers may not inherit your PATH
  "command": "/nix/var/nix/profiles/default/bin/nix",
  "args": ["run", "github:Wawona/WWN-MCP#wwn-mcp", "--", "serve", "--transport", "stdio"],
  "env": { "WWN_MCP_DATA_DIR": "/Users/you/.local/share/wwn-mcp" }
} } }
```

Use a **local checkout** instead of `github:Wawona/WWN-MCP` for offline / dev work
(e.g. `nix run /path/to/WWN-MCP#wwn-mcp -- serve --transport stdio`). Reload the
Cursor window; the `wwn-mcp` tools appear in MCP settings.

**3. Refresh later** by re-running `fetch` + `index` (incremental — only changed
chunks are re-embedded).

Prefer `nix profile install github:Wawona/WWN-MCP` if you want a stable `wwn-mcp`
on your PATH for the CLI; the Cursor entry can still use `nix run` so it always
tracks the flake.

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
| `WWN_MCP_DATA_DIR` | `~/.local/share/wwn-mcp` (XDG); `./data` in a writable checkout | runtime data root |
| `WWN_MCP_CORPUS_TOML` | packaged copy, else `./corpus.toml` | manifest path |
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
