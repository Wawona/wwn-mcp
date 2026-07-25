# Wawona org repo catalog (`wwn-*` + integration)

Quick reference for every repository under `github.com/Wawona` that matters for
compositor/shell/toolchain development.

| Repo | Role | `registryFragment` keys | Patch-anchor CI |
|------|------|-------------------------|-----------------|
| **Wawona** | Integration: Smithay backend, SwiftUI/Android apps, `flake.nix` inputs, xcodegen, gradlegen | (local Wawona-only recipes if any) | Wayland/Android maintainability scripts |
| **wwn-toolchain** | Cross-compile framework, Apple/Android toolchains, ~40 libs, `wawona-pty`, `lib.mkToolchains`, `lib.baseRegistry` | base library set + `wawona-pty` | sample lib builds (`xkbcommon-ios`, …) |
| **wwn-zsh** | In-process App-Store zsh, RootFS, zsh-framework | `zsh`, `zsh-framework`, `wawona-rootfs` | `verify-zsh-ios-patches.py` |
| **wwn-weston** | Weston clients + apple-mobile compositor + weston-simple-shm | `weston`, `weston-compositor`, `weston-compositor-drm`, `weston-simple-shm` | `verify-weston-ios-patches.py` |
| **wwn-iland** | L1 complete graphics stack: DRM/KMS/EGL/GBM over IOSurface/Metal or AHB; ANGLE, SwiftShader, MoltenVK, macOS-only KosmicKrisp, and Android Vulkan hooks. Mode A archives + macOS-only Mode B dylib | `iland`, `iland-baremetal` (macOS only), `angle`, `swiftshader`, `moltenvk`, `kosmickrisp` (macOS only), `iland-gl-clients` | flake check + Mode A/B sample builds |
| **wwn-waypipe** | waypipe-rs port (v0.11.0 pin + patches) | `waypipe` | flake check |
| **wwn-coreutils** | uutils coreutils multicall + in-process patched-src | (via `mkMulticall` / patched-src helpers, not always a registry key) | flake check |
| **wwn-foot** | foot terminal Apple ports | `foot` | flake check |
| **wwn-fastfetch** | fastfetch port (in-process on Apple mobile, binary on macOS/Android) + Wayland WM on macOS | `fastfetch` | `verify-fastfetch-ios-patches.py` |
| **WWN-MCP** | RAG + MCP retrieval for agents | — | — |

## App Store module catalog

| Repo | Role | `registryFragment` keys | CI |
|------|------|-------------------------|-----|
| **wwn-apt** | App Store `apt` compatibility layer: optional module catalog (foot, neovim, fastfetch), bundled policy (zsh, coreutils, waypipe, apt), shell CLI stub, StoreKit + ODR spec | `apt-rootfs` | catalog validate + doc firewall + `apt-rootfs-ios` build |

**Documentation firewall:** the `wwn-apt` repo must **not** mention jailbreak
distribution or `repo.wawona.io`. App Store Review Notes come from
`wwn-apt/docs/APP-STORE-MODULES.md` only.

## Jailbreak distribution

| Repo | Role | Notes |
|------|------|-------|
| **repo.wawona.io** | Real Debian `.deb` flat repo (Procursus / Termux) | **Jailbreak only.** App Store–approved modules use **`wwn-apt` only**; **`repo.wawona.io` is prohibited** on App Store builds. |

## Dependency graph (flakes)

```text
L0 wwn-toolchain
  └─ L1 wwn-iland
       └─ L2 wwn-kmscube
            └─ L3 wwn-weston
L0 ──► L3' wwn-waypipe / wwn-anowaW / wwn-vms / wwn-apt / other ports
L4 Wawona ──► all required lower layers
```

Canonical layering and forbidden edges:
[`wwn-repo-dag.md`](wwn-repo-dag.md).

Canonical graphics mirrors:

- [`wwn-iland-graphics-stack.md`](wwn-iland-graphics-stack.md) — L1 ownership
  and minimal EGL/GLES/Vulkan translation paths.
- [`iland-mode-a-b-desktop.md`](iland-mode-a-b-desktop.md) — presentation,
  privilege, and bundle separation.
- [`platform-capability-matrix.md`](platform-capability-matrix.md) — complete
  Apple-family and Android product scope.
- [`toolkit-readiness-soft-shm.md`](toolkit-readiness-soft-shm.md) — toolkit
  gates and shared software-buffer fallback.

App repos do **not** depend on `wwn-zsh` at flake level (the `wawona_zsh_main`
symbol resolves at final app link via weak externs) — the DAG stays acyclic.

## Deleted / renamed repos

- **`Wawona/iland`** (org fork) — **deleted**. Superseded by **`wwn-iland`**.
  Upstream inspiration: [CoreBedtime/iland](https://github.com/CoreBedtime/iland).
- **`Wawona/Wawona-repo`** — renamed to **`repo.wawona.io`** (jailbreak utilities repo).
- **`Wawona/wawona.github.io`** — renamed to **`wawona.io`** (project website).

## Standalone build examples

```sh
cd ~/Wawona/wwn-zsh    && nix build .#zsh-ios
cd ~/Wawona/wwn-fastfetch && nix build .#fastfetch-ios
cd ~/Wawona/wwn-weston && nix build .#weston-compositor-ios
cd ~/Wawona/wwn-iland  && nix build .#iland-ios
cd ~/Wawona/wwn-apt   && nix build .#apt-rootfs-ios
cd ~/Wawona/Wawona     && nix build .#wawona-macos   # full integration
```
