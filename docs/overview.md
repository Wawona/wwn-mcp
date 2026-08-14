# WWN-MCP — Overview & Architecture

WWN-MCP is a local-embeddings RAG (retrieval-augmented generation) service plus
a **stdio** Model Context Protocol (MCP) server. It gives any Cursor model
on-demand, retrieval-backed knowledge of the Wawona stack so it stops guessing
about niche, post-training-cutoff topics.

It is a standalone, open-source (MIT) Wawona-org project. The Wawona repo is a
*consumer* (its `.cursor/` config + rules point at the local `wwn-mcp` binary)
and one of the indexed corpus sources.

**Host model:** same as [mcp-nixos](https://github.com/utensils/mcp-nixos) —
Cursor spawns `wwn-mcp` on PATH over stdio. No public URL / Streamable HTTP.

## What it knows

- The entire wayland.app / Wayland Explorer protocol set.
- Weston, Niri, Smithay, Sway, Cocoa-Way, iland, Pixman.
- Vulkan (MoltenVK, KosmicKrisp, Android Vulkan), OpenGL/GLES (ANGLE).
- Linux DRM/KMS/EGL/GBM (the OS contract iland reimplements on Apple).
- Apple AppKit/UIKit/WatchKit/SwiftUI/Metal/IOSurface + Liquid Glass.
- macOS internals (Mach-O, dyld, Mach, XNU, launchd).
- Swift / Rust language books + MCP SDKs.
- XcodeGen, crate2nix, Fastlane, GitHub Actions, Determinate Nix.
- Android Jetpack Compose + Material 3, NDK graphics.
- App Store / Play policies; wwn-apt module delivery.
- Wawona integration + extracted `wwn-*` repos (toolchain, iland, weston,
  niri, kmscube, waypipe, anowaW, vms, containers, ssh, zsh, …).

## Architecture

```mermaid
flowchart TD
  subgraph consumers [Consumer repos]
    Cursor["Cursor / any model + .cursor rules"]
  end
  Cursor -->|"stdio spawn"| Server["wwn-mcp (FastMCP)"]
  Server --> DB[("sqlite: FTS5 + vec0 hybrid index")]
  Timer["user timer / manual"] --> Ingest["fetch + chunk + embed"]
  Ingest --> DB
  Manifest["corpus.toml"] --> Ingest
  Sources["corpus sources (local siblings + git + web)"] --> Ingest
  Cursor -->|"stdio spawn"| NixOS["mcp-nixos (uvx, separate)"]
```

## Companion: MCP-NixOS

WWN-MCP does **not** co-host MCP-NixOS. Cursor runs it separately:

```json
{ "nixos": { "command": "uvx", "args": ["mcp-nixos"] } }
```

- **WWN-MCP** → Wawona stack + `wwn-*` repos (`get_patch` / `list_patches`).
- **MCP-NixOS** → live upstream nixpkgs/option/version facts.

### Developer-local: XcodeBuildMCP + lldb-mcp

macOS-only action tools in the consumer `.cursor/mcp.json`. Curated guides in
`knowledge/wawona/` (DAG, graphics, Mode A/B, platform matrix, device workflow,
lldb-mcp reference).

## RAG pipeline

```
corpus.toml  ──▶  fetch  ──▶  chunk  ──▶  embed  ──▶  store (sqlite)  ──▶  serve (stdio)
             sources       per-file     fastembed     FTS5 + vec0          tools/resources
                          (md/code/      (BGE-small,    hybrid (RRF)
                           xml/patch)     hashing
                                          fallback)
```

First empty serve auto-indexes shipped `knowledge/`.

## Design choices

- **Local + hermetic**: no external embedding API.
- **Graceful degradation**: missing fastembed/sqlite-vec → hashing + FTS.
- **Public/MIT hygiene**: fetched third-party docs stay in the runtime data dir.
- **stdio only**: no HTTP transport to maintain.
