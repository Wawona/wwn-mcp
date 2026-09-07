# AI contributors: use MCP (do not guess)

Wawona’s stack post-dates typical model training. Contributors using Cursor,
Claude Desktop, Zed, VS Code Copilot Chat, or any other MCP host **must** wire
**wwn-mcp** (stdio RAG) so agents retrieve docs instead of inventing repos,
gates, or windowing paths.

Public guide: https://wawona.io/docs/contributor/wwn-mcp/  
(aliases: `/docs/mcp/`, `/docs/ai/`)

## Transport

- **stdio only**. Host spawns `wwn-mcp` like `uvx mcp-nixos`.
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

1. `where_to_edit` / `list_repos`. Correct org repo (never invert the DAG).
2. `get_capability(platform, feature)`. `available` | `planned` | `blocked` | `forbidden`.
   macOS `desktop` stays planned (LockScreen unfinished) even though Classic
   Take Over is implemented. Read the `note` field.
3. `search_docs` / `get_architecture`. Mission, Mode A/B, Classic Desktop
   Replacement (Enable vs Replace now, Path B `claim-ok`), port fidelity.
4. `search_code` / `find_symbol` / `get_patch`. Implementation + patches.
5. `get_protocol` when touching Wayland surfaces.
6. Trust citations over priors.
7. Read matching Cursor skill (`.cursor/skills/wawona-*`, tracked
   `Wawona/docs/agent-skills/`). Software must improve on prior knowledge.
   After a durable finding: update skill + `knowledge/wawona/` + reindex.
   See `agent-learn.md`. Voice: caveman-lite.

## Companion MCPs (separate processes)

| Name | Role |
|------|------|
| `wwn-mcp` | Wawona + wwn-* RAG, patches, gates, protocols |
| `nixos` | Live nixpkgs / options (not Wawona recipes) |
| `xcodebuild` | Apple build / install / run |
| `lldb` | Device attach / backtrace (Workflow D: vphone via packages debug) |
| `agent-device` | UI automation + vphone `packages` tipa/apt/debug |

Lab for Mode B tipa: `nix run github:Wawona/wwn-vphone#vphone-jb-lab`.

## Do not conflate

Wawona Swinging Bridge ≠ Desktop/LockScreen ≠ VMs/containers ≠ Wawona Runtime
Wasm (`wpm`). Runtime is always Mode A (store-compliant); no Mode B Runtime.
macOS Classic Take Over is implemented; the `desktop` gate stays planned until
LockScreen. Enable Desktop Replacement is not Take Over.

## Index

```bash
wwn-mcp fetch && wwn-mcp index
# or: wwn-mcp index --local-siblings
```

Full tool list: `docs/mcp-tools.md` in the wwn-mcp repo. Also see `contribute.md`.
