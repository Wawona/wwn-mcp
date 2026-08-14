# Wawona org repo catalog (`wwn-*` + integration)

Quick reference for repositories under `github.com/Wawona` that matter for
compositor/shell/toolchain development.

| Repo | Layer | Role | Patch-anchor / notes |
|------|-------|------|----------------------|
| **Wawona** | L4 | Integration: Smithay, SwiftUI/Android, flake merge, xcodegen | Product gates |
| **wwn-toolchain** | L0 | Cross-compile + substrate (cairo/pango/pixman/libwayland/…) + pty | No wwn-* inputs |
| **wwn-iland** | L1 | DRM/KMS/EGL/GBM + ANGLE/SwiftShader/MoltenVK/KosmicKrisp | Mode A/B |
| **wwn-kmscube** | L2 | Graphics acceptance clients | Must not depend on weston |
| **wwn-weston** | L3 | Weston compositor + clients | Mandatory native bundle |
| **wwn-niri** | L3 | Niri compositor | Mandatory native bundle |
| **wwn-waypipe** | L3′ | waypipe-rs remote | |
| **wwn-anowaW** | L3′ | Host-app → Wayland bridge (not Desktop) | Planned |
| **wwn-vms** | L3′ | VM machine kinds | Planned |
| **wwn-containers** | L3′ | Container machine kinds | Planned |
| **wwn-ssh** | L3′ | libssh2 (Apple mobile) vs OpenSSH | |
| **wwn-zsh** | L3′ | In-process App Store zsh + RootFS | |
| **wwn-coreutils** | L3′ | uutils in-process multicall | |
| **wwn-foot** | L3′ | foot terminal | |
| **wwn-fastfetch** | L3′ | fastfetch port | |
| **wwn-neovim** | L3′ | neovim / optional module | |
| **wwn-phoon-rs** | L3′ | phoon client | |
| **wwn-apt** | L3′ | App Store apt catalog (StoreKit + ODR) | No jailbreak mentions |
| **wwn-mcp** | tooling | Stdio RAG + MCP for agents | This repo |
| **wawona.io** | docs | Public site | Not a product flake input |

## Dependency graph (flakes)

```text
L0 wwn-toolchain
  └─ L1 wwn-iland
       └─ L2 wwn-kmscube
            └─ L3 wwn-weston / wwn-niri
L0 ──► L3' waypipe / anowaW / vms / containers / ssh / apt / ports
L4 Wawona ──► all required lower layers
```

Canonical layering: [`wwn-repo-dag.md`](wwn-repo-dag.md).
How to contribute: [`contribute.md`](contribute.md).

## Deleted / renamed

- **`Wawona/iland`** — deleted; use **wwn-iland** (credits CoreBedtime/iland).
- **`Wawona/Wawona-repo`** → **repo.wawona.io** (jailbreak only; not in default RAG).
- **`Wawona/wawona.github.io`** → **wawona.io**.

## Standalone build examples

```sh
cd ~/Wawona/wwn-zsh    && nix build .#zsh-ios
cd ~/Wawona/wwn-iland  && nix build .#iland-ios
cd ~/Wawona/wwn-niri   && nix build .#niri-ios   # when attribute exists
cd ~/Wawona/Wawona     && nix build .#wawona-macos
```
