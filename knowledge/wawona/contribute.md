# Contribute to the Wawona compositor organization

Agents: query **wwn-mcp** (`list_repos`, `where_to_edit`, `get_capability`,
`search_docs`) before editing. Transport is **stdio only** — any MCP host
spawns `wwn-mcp` like `uvx mcp-nixos`. There is no `mcp.wawona.io`.

## Which repo

| Change | Repo |
|--------|------|
| Substrate (cairo/pango/pixman/libwayland) | `wwn-toolchain` |
| ANGLE / MoltenVK / iland DRM/KMS/GBM | `wwn-iland` |
| kmscube acceptance | `wwn-kmscube` |
| Weston | `wwn-weston` |
| Niri | `wwn-niri` |
| waypipe | `wwn-waypipe` |
| anowaW bridge | `wwn-anowaW` |
| SSH / libssh2 | `wwn-ssh` |
| zsh / RootFS | `wwn-zsh` |
| Machines UI, SwiftUI, Android app, Smithay | `Wawona` |
| Public docs site | `wawona.io` |
| This RAG / corpus | `wwn-mcp` |

Never invert the DAG: L0 ↚ L1+; L1 ↚ weston/kmscube; Wawona is never an input
of L0–L3. See [`wwn-repo-dag.md`](wwn-repo-dag.md).

## Branch + CI

- Active work lands on **`development`** only. Do not WIP on `master`.
- Prove link/eval failures **locally** before pushing (`nix build` the failing
  cell). Do not burn Gate: products to discover `ld` errors.
- Port fidelity: a ported client must match the same upstream client over
  **waypipe**. Substitute platform under the ABI; never re-host Wayland clients
  onto KMS emulation as a shortcut.

## Mandatory bundles

Every product target ships **real** Weston and **real** Niri (native ABI,
real entry points). No stubs, fake mains, or permanent target exclusions.

## Mode A / B / anowaW (do not conflate)

- **Mode A** — store-safe in-window iland (`libiland_userland.a`).
- **Mode B** — macOS desktop-host dylib only (`libwayland-mac.dylib`), SIP-gated.
- **anowaW** — host-app → Wayland bridge (planned). Not Desktop. Not LockScreen.

## MCP host wiring

```json
{
  "mcpServers": {
    "wwn-mcp": { "command": "wwn-mcp" },
    "nixos": { "command": "uvx", "args": ["mcp-nixos"] }
  }
}
```

First spawn auto-indexes shipped `knowledge/`. Full corpus:

```bash
wwn-mcp fetch
wwn-mcp index
# or: wwn-mcp index --local-siblings
```
