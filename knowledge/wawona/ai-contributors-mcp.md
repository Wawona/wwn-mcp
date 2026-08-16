# AI contributors: use MCP (do not guess)

Wawona’s stack post-dates typical model training. Contributors using Cursor,
Claude Desktop, Zed, VS Code Copilot Chat, or any other MCP host **must** wire
**wwn-mcp** (stdio RAG) so agents retrieve docs instead of inventing repos,
gates, or windowing paths.

Public guide: https://wawona.io/docs/contributor/wwn-mcp/  
(aliases: `/docs/mcp/`, `/docs/ai/`)

## Transport

- **stdio only** — host spawns `wwn-mcp` like `uvx mcp-nixos`.
- There is **no** `mcp.wawona.io` / Streamable HTTP endpoint.

```json
{
  "mcpServers": {
    "wwn-mcp": { "command": "wwn-mcp", "args": [] },
    "nixos": { "command": "uvx", "args": ["mcp-nixos"] }
  }
}
```

Install: `nix profile install github:Wawona/WWN-MCP` then `wwn-mcp info`.

## Required agent loop

1. `where_to_edit` / `list_repos` — correct org repo (never invert the DAG).
2. `get_capability(platform, feature)` — `available` | `planned` | `blocked` | `forbidden`.
3. `search_docs` / `get_architecture` — mission, Mode A/B, port fidelity.
4. `search_code` / `find_symbol` / `get_patch` — implementation + patches.
5. `get_protocol` when touching Wayland surfaces.
6. Trust citations over priors.

## Companion MCPs (separate processes)

| Name | Role |
|------|------|
| `wwn-mcp` | Wawona + wwn-* RAG, patches, gates, protocols |
| `nixos` | Live nixpkgs / options (not Wawona recipes) |
| `xcodebuild` | Apple build / install / run |
| `lldb` | Device attach / backtrace |
| `agent-device` | UI automation (not osascript / screencapture) |

## Do not conflate

Wawona Swinging Bridge ≠ Desktop/LockScreen ≠ VMs/containers ≠ Wawona Runtime
Wasm (`wpm`). Runtime is always Mode A (store-compliant); no Mode B Runtime.

## Index

```bash
wwn-mcp fetch && wwn-mcp index
# or: wwn-mcp index --local-siblings
```

Full tool list: `docs/mcp-tools.md` in the wwn-mcp repo. Also see `contribute.md`.
