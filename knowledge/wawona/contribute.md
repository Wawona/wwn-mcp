# Contribute to the Wawona compositor organization

Agents: query **wwn-mcp** (`list_repos`, `where_to_edit`, `get_capability`,
`search_docs`) before editing. Transport is **stdio only**. Any MCP host
spawns `wwn-mcp` like `uvx mcp-nixos`. There is no `mcp.wawona.io`.

**Human contributors using AI:** start with the public guide
[AI + MCP](https://wawona.io/docs/contributor/wwn-mcp/) and the indexed
[`ai-contributors-mcp.md`](ai-contributors-mcp.md). Wire `wwn-mcp` (and
usually `nixos`) in your editor’s MCP config before relying on an agent.

## Which repo

| Change | Repo |
|--------|------|
| Substrate (cairo/pango/pixman/libwayland) | `wwn-toolchain` |
| ANGLE / MoltenVK / iland DRM/KMS/GBM | `wwn-iland` |
| kmscube acceptance | `wwn-kmscube` |
| Weston | `wwn-weston` |
| Niri | `wwn-niri` |
| waypipe | `wwn-waypipe` |
| Wawona Swinging Bridge bridge | `Wawona-Swinging-Bridge` |
| SSH / libssh2 | `wwn-ssh` |
| IOWatchdog Path B / claim-ok | `wwn-iowatchdog` |
| Classic VTs / igettyd / Doorman | `wwn-igetty` |
| Desktop Replacement Settings / Take Over helper | `Wawona` (dylib: `wwn-iland`) |
| zsh / RootFS | `wwn-zsh` |
| Machines UI, SwiftUI, Android app, Smithay | `Wawona` |
| Public docs site | `wawona.io` |
| This RAG / corpus | `wwn-mcp` |

Never invert the DAG: L0 ↚ L1+; L1 ↚ weston/kmscube; Wawona is never an input
of L0-L3. See [`wwn-repo-dag.md`](wwn-repo-dag.md).

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

## Mode A / B / Wawona Swinging Bridge (do not conflate)

- **Mode A**. Store-safe in-window iland (`libiland_userland.a`).
- **Mode B (macOS)**. Desktop-host dylib (`libwayland-mac.dylib`). SIP
  **fully disabled**. Enable arms Path B; Replace now is Classic Take Over.
  LockScreen greeter still planned. See [`desktop-replacement-macos.md`](desktop-replacement-macos.md).
- **Mode B (iOS/iPadOS)**. Three channels: App Store Mode A only; TrollStore
  `.tipa` = JIT + IOMFB + Desktop (not JIT-only); Sileo = full Mode B including
  Swinging Bridge. See [`ios-mode-b-channels.md`](ios-mode-b-channels.md).
- **Wawona Swinging Bridge**. Host-app → Wayland bridge (planned). Not Desktop.
  Not LockScreen. On iOS/iPadOS: Sileo-only.
- **dmabuf zero-copy**. `zwp_linux_dmabuf_v1` + IOSurface/AHB; never LINEAR on
  Apple/Android. See [`dma-buf-zero-copy.md`](dma-buf-zero-copy.md).

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
