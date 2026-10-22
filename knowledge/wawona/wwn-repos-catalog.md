# Wawona org repo catalog (`wwn-*` + integration)

Quick reference for repositories under `github.com/Wawona` that matter for
compositor/shell/toolchain development.

| Repo | Layer | Role | Patch-anchor / notes |
|------|-------|------|----------------------|
| **Wawona** | L4 | Integration: Smithay, GTK4/Libadwaita (Linux), SwiftUI (Apple), JNI (Android), headless WLCS | Product gates |
| **wwn-toolchain** | L0 | Cross-compile + substrate (cairo/pango/pixman/libwayland/…) + pty | No wwn-* inputs |
| **iLand** | L1 | DRM/KMS/EGL/GBM + ANGLE/SwiftShader/MoltenVK/KosmicKrisp | Mode A/B |
| **wwn-kmscube** | L2 | Graphics acceptance clients | Must not depend on weston |
| **wwn-weston** | L3 | Weston compositor + clients | Mandatory native bundle |
| **wwn-niri** | L3 | Niri compositor | Mandatory native bundle |
| **wwn-waypipe** | L3′ | waypipe-rs remote | |
| **Wawona-Swinging-Bridge** | L3′ | Host-app to Wayland bridge (not Desktop) | Planned |
| **Relay** | L3′ | Wawona Relay: VMs, containers, and Wasm runtime (`wwn-relay`) | KVM/OCI/WASI |
| **wwn-ssh** | L3′ | libssh2 (Apple mobile) vs OpenSSH | |
| **wwn-zsh** | L3′ | In-process App Store zsh + RootFS | |
| **wwn-uutils-rs** | L3′ | uutils in-process multicall safe-subset | |
| **wwn-foot** | L3′ | foot terminal | |
| **wwn-fastfetch** | L3′ | fastfetch port (fork of fastfetch-cli) | Dev branch |
| **wwn-neovim** | L3′ | neovim / optional module | |
| **wwn-phoon-rs** | L3′ | phoon client | |
| **Doorman** | L3′ | Console PAM session manager | |
| **iGetty** | L3′ | Virtual terminal multiplexer (igettyd) | F1-F9 |
| **iomfb-rs** | L3′ | IOMobileFramebuffer Rust bindings | Mode B Apple |
| **iowatchdog-tools** | L3′ | IOWatchdog Path B tools and daemon control | macOS 26 safety |
| **wwn-mcp** | tooling | Stdio RAG + MCP for agents | This repo |
| **wawona.io** | docs | Public site | Not a product flake input |
| **repo.wawona.io** | catalog | deb and wasm package repo | /wasm/v1 + APT |

## Dependency graph (flakes)

```text
L0 wwn-toolchain
  └─ L1 iLand
       └─ L2 wwn-kmscube
            └─ L3 wwn-weston / wwn-niri
L0 ──► L3' waypipe / Swinging Bridge / Relay / ssh / uutils / ports
L4 Wawona ──► all required lower layers
```

Canonical layering: [`wwn-repo-dag.md`](wwn-repo-dag.md).
How to contribute: [`contribute.md`](contribute.md).

- **`Wawona/Sileo-Android`** -> **wwn-sileo-android** (fork of Sileo/Sileo; unofficial Android port).
- **`Wawona/AsteroidOS-SDK`** -> **wwn-asteroidos-sdk** (AsteroidOS SDK Nix flake for watch cross-compilation).
- **`Wawona/UTM`** -> **wwn-UTM** (fork of utmapp/UTM for hypervisor and Wayland research).
- **`Wawona/wwn-coreutils`** -> **wwn-uutils-rs**.
- **`Wawona/wwn-igetty`** -> **iGetty**.
- **`Wawona/doorman`** -> **Doorman**.
- **`Wawona/wwn-iomfb-rs`** -> **iomfb-rs**.
- **`Wawona/wwn-iowatchdog`** -> **iowatchdog-tools**.
- **`Wawona/fastfetch`** -> **wwn-fastfetch** (GitHub fork of fastfetch-cli/fastfetch).
- **`Wawona/wwn-runtime`**, **`wwn-vms`**, **`wwn-containers`** -> deleted / consolidated into **Relay**.
- **`Wawona/nixpkgs2wasi`** -> deleted (wasm catalog hosted at repo.wawona.io/wasm).
- **`Wawona/wwn-apt`** -> retired (wpm for wasm; APT at repo.wawona.io for debs).
- **`Wawona/iland`** -> deleted; use **iLand**.
- **`Wawona/Wawona-repo`** -> **repo.wawona.io**.
- **`Wawona/wawona.github.io`** -> **wawona.io**.

## Standalone build examples

```sh
cd ~/Wawona/wwn-zsh       && nix build .#zsh-ios
cd ~/Wawona/iLand         && nix build .#iland-ios
cd ~/Wawona/wwn-niri      && nix build .#niri-ios
cd ~/Wawona/wwn-uutils-rs && nix build .#uutils-ios
cd ~/Wawona/Wawona        && nix build .#wawona-linux
```
