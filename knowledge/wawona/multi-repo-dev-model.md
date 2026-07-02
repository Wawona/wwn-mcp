# Wawona multi-repo development model

Wawona development is split across the **Wawona GitHub organization**
(`github.com/Wawona/*`). The monolithic era — all patched software living under
`Wawona/dependencies/` — is over. Today:

- **`Wawona/Wawona`** is the **integration layer**: Smithay compositor, SwiftUI
  apps, Android packaging, `flake.nix` that wires everything together.
- **`wwn-toolchain`** owns the cross-compile framework, ~40 common library
  recipes, and `wawona-pty`.
- **`wwn-*` app repos** own headline patched upstreams (zsh, Weston, iland,
  waypipe, coreutils, foot), each with Nix recipes + patch scripts + CI.

## Local checkout layout

All org repos live as siblings under one directory:

```
~/Wawona/
├── Wawona/           # integration (compositor, apps, flake inputs)
├── WWN-MCP/          # this retrieval server
├── wwn-toolchain/
├── wwn-zsh/
├── wwn-weston/
├── wwn-iland/
├── wwn-waypipe/
├── wwn-coreutils/
├── wwn-foot/
├── wwn-fastfetch/
└── wwn-apt/
```

One directory per GitHub repo — a 1:1 mirror of `github.com/Wawona/*`.

## Documentation firewall (App Store vs jailbreak)

| Surface | Rule |
|---------|------|
| **`wwn-apt`** | App Store module catalog + `apt` CLI. **Zero mentions** of jailbreak or `repo.wawona.io`. |
| **`repo.wawona.io`** | Jailbreak `.deb` repo only. Must state App Store modules use **`wwn-apt` only**; this repo is **prohibited** on App Store builds. |
| **Wawona App Store docs** | Same as `wwn-apt` — no `repo.wawona.io`. |

Cross-reference between channels is allowed **only** on the jailbreak repo README
(pointing engineers to `wwn-apt`), never the reverse.

## Where to edit what

| Change | Repo | Not in Wawona monorepo |
|--------|------|------------------------|
| zsh exec patch, RootFS, zsh Nix recipes | `wwn-zsh` | `dependencies/libs/zsh/` (deleted) |
| Weston terminal/compositor patches | `wwn-weston` | `dependencies/clients/weston/` (deleted) |
| iland DRM/EGL/GBM shims | `wwn-iland` | `dependencies/libs/iland/` (deleted) |
| waypipe-rs Apple/Android port | `wwn-waypipe` | |
| uutils coreutils in-process dispatch | `wwn-coreutils` | |
| foot terminal port | `wwn-foot` | |
| fastfetch port | `wwn-fastfetch` | |
| App Store module catalog, `apt` CLI stub | `wwn-apt` | |
| cairo/xkbcommon/libwayland/angle/… | `wwn-toolchain` | |
| wawona-pty, apple-mobile-platform.nix | `wwn-toolchain` | |
| XcodeGen spec, Android APK, Rust backend | `Wawona` | stays here |
| flake inputs + registry merge | `Wawona/flake.nix` | |

**Rule:** if you are editing a patch script or a per-platform Nix recipe for an
upstream (zsh, weston, foot, …), open the **`wwn-*` repo**, not Wawona.

## Flake wiring (integration)

`Wawona/flake.nix` declares flake inputs for every `wwn-*` repo with uniform
`nixpkgs` / `wwn-toolchain` `follows` (one nixpkgs pin — critical for source
hashes like `pkgs.zsh.src` and weston tarballs).

The merged Nix registry:

```nix
mergedRegistry = wwn-toolchain.lib.baseRegistry
  // wwn-iland.registryFragment
  // wwn-weston.registryFragment
  // wwn-zsh.registryFragment
  // wwn-waypipe.registryFragment
  // wwn-foot.registryFragment
  // wwn-fastfetch.registryFragment
  // wwn-apt.registryFragment;  # follow-up PR

toolchains = wwn-toolchain.lib.mkToolchains {
  inherit pkgs pkgsAndroid pkgsIos androidSDK wawonaSrc;
  registry = mergedRegistry;
  extraArgs = { ilandSrc = wwn-iland; };
};
```

Each `wwn-*` repo also builds **standalone** via the same `mkToolchains` +
`baseRegistry // self.registryFragment` pattern for isolated CI.

## CI ownership

| Check | Repo |
|-------|------|
| `verify-zsh-ios-patches.py` | `wwn-zsh` |
| `verify-weston-ios-patches.py` | `wwn-weston` |
| `verify-fastfetch-ios-patches.py` | `wwn-fastfetch` |
| Catalog validate + doc firewall | `wwn-apt` |
| Wayland/Android maintainability, integration builds | `Wawona` |
| Per-repo `nix build .#<sample-output>` | each `wwn-*` |

## WWN-MCP indexing

WWN-MCP indexes Wawona (integration) **and** every `wwn-*` git source in
`corpus.toml`. Use `get_patch("zsh")` or `get_patch("wwn-zsh/zsh")` for patch
inventory; `search_code(..., project="weston")` for Weston recipes; `read_document`
with paths like `wwn-zsh/dependencies/libs/zsh/ios.nix`.

For the **iOS device build/install/debug loop** (nix develop signing, xcodegen,
xcodebuild-mcp, lldb-mcp on 8amps iPhone Air, wwn-fastfetch flake overrides), see:

- **`knowledge/wawona/ios-device-dev-workflow.md`** — end-to-end operational guide
- **`knowledge/wawona/lldb-mcp-apple-device-debugging.md`** — full lldb-mcp tool catalog,
  iOS attach workflow, Wawona symbol breakpoints, in-process pthread debugging
