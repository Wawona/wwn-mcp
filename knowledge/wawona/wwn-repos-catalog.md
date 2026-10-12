# Wawona org repo catalog (`wwn-*` + integration)

Quick reference for repositories under `github.com/Wawona` that matter for
compositor/shell/toolchain development.

| Repo | Layer | Role | Patch-anchor / notes |
|------|-------|------|----------------------|
| **Wawona** | L4 | Integration: Smithay, SwiftUI/Android, flake merge, xcodegen | Product gates |
| **wwn-toolchain** | L0 | Cross-compile + substrate (cairo/pango/pixman/libwayland/…) + pty | No wwn-* inputs |
| **wwn-iland** | L1 | DRM/KMS/EGL/GBM + ANGLE/SwiftShader/MoltenVK/KosmicKrisp | Mode A/B |
| **wwn-waypipe** | L3′ | waypipe-rs remote | |
| **Wawona-Swinging-Bridge** | L3′ | Host-app → Wayland bridge (not Desktop) | Planned |
| **Relay** (`wwn-relay`) | L3′ | Linux VMs + OCI-in-VM + Mode A WASI | Never QEMU/UTM. Edit here, not wwn-vms/containers/wasm |
| **ToolbarKeys** | L3′ | Keyboard toolbar model (Rust + UniFFI). No platform view | iOS 13 and Android share one document. Rootshell is the behavior source |
| **Ghostty** (`wwn-ghostty`) | L3′ | Terminal grid for local shell, SSH, and Relay console | Zig stays. No product dylib. watchOS is software, not Metal |
| **wwn-ssh** | L3′ | libssh2 (Apple mobile) vs OpenSSH | |
| **wwn-iowatchdog** | L3′ | macOS IOWatchdog Path B (Desktop Mode B) | nixpkgs-only; never Apple-mobile |
| **wwn-vphone** | L3′ | Jailbroken iOS research lab (vphone-cli wrap) | nixpkgs-only; never ship Disk.img/IPSW |
| **wwn-igetty** | L3′ | VT / Doorman getty after Classic Take Over | not the Mode B dylib |
| **wwn-zsh** | L3′ | In-process App Store zsh + RootFS | |
| **wwn-coreutils** | L3′ | uutils in-process multicall | |
| **wwn-wasm** (legacy) | L3′ | Merged into **Relay**. Do not start new work here | Redirect |
| **repo.wawona.io** | catalog | Two channels (`wasm`, `deb`) and three kinds (`cli`, `gui`, `lib`) under `catalog/`. One `registryFragment` for the in-app ports. APT index file is `Packages`. | Never one mixed search list. Termux is not jailbreak. Do not recreate deleted port repos. |
| **wwn-mcp** | tooling | Stdio RAG + MCP for agents | This repo |
| **wawona.io** | docs | Public site | Not a product flake input |

## Dependency graph (flakes)

```text
L0 wwn-toolchain
  └─ L1 wwn-iland
L0 ──► repo.wawona.io catalog (wasm/deb x cli/gui/lib)
L0 ──► L3' waypipe / Wawona Swinging Bridge / Relay / ssh / iowatchdog / igetty
L4 Wawona ──► iland + catalog registryFragment + L3'
```

Canonical layering: [`wwn-repo-dag.md`](wwn-repo-dag.md).
How to contribute: [`contribute.md`](contribute.md).

## Deleted / renamed

- **`Wawona/iland`**. Deleted; use **wwn-iland** (credits CoreBedtime/iland).
- **`Wawona/Wawona-repo`** → **repo.wawona.io** (store wasm `/wasm/v1`; Sileo iOS jailbreak APT + Termux Android sideload APT at repo root; humans search at `/search/`).
- **`Wawona/wawona.github.io`** → **wawona.io**.
- **2026-10-12 port collapse.** Deleted: `wwn-weston`, `wwn-niri`, `wwn-foot`,
  `wwn-kmscube`, `wwn-fastfetch`, `wwn-phoon-rs`, `wwn-neovim`, `wwn-xfce`,
  `wwn-sway`, `wwn-kde`, `wwn-gnome`, `wwn-hyprland`, `wasm-packages`,
  `wasinix`. Recipes are `repo.wawona.io` `catalog/`. Do not recreate them.
  Upstream `xtyxtyx/wasinix` was not this fork.

## Standalone build examples

```sh
cd ~/Wawona/wwn-zsh    && nix build .#zsh-ios
cd ~/Wawona/wwn-iland  && nix build .#iland-ios
cd ~/Wawona/Wawona     && nix eval .#packages.aarch64-darwin.niri-ios.name
cd ~/Wawona/Wawona     && nix build .#wawona-macos
```
