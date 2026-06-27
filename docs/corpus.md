# Corpus catalog

The single source of truth is [`corpus.toml`](../corpus.toml). This page
summarizes it. To add/remove a source, edit `corpus.toml` — no code change is
needed.

## Source schema

Each `[[source]]` entry supports:

| field | meaning |
|-------|---------|
| `name` | unique id (also the on-disk dir under the corpus cache) |
| `project` | tag used for filtered search (groups related sources) |
| `kind` | `git` \| `web-mirror` \| `rustdoc` \| `local` |
| `url` / `urls` | remote(s) for git/rustdoc/web-mirror |
| `ref` | git branch/tag/commit |
| `path` | filesystem path for `kind = "local"` (relative to repo root) |
| `include` / `exclude` | globs to index / skip |
| `sparse` | git **cone-mode** dir prefixes to materialize (huge repos: `github/docs`, `nixpkgs`) |
| `platform` | `macos`/`ios`/`ipados`/`tvos`/`watchos`/`visionos`/`android`/`linux`/`all` |
| `stability` | Wayland family/stability tag (`core`/`stable`/`staging`/`wlr`/`kde`/…) |
| `license` | SPDX-ish tag, surfaced in citations (never redistributed) |
| `seeds` / `max_pages` | bounded-crawl seeds + cap for `web-mirror` |
| `enabled` | `false` ⇒ `fetch` skips it (used when an upstream URL is unconfirmed) |

## Catalog (by area)

### Wawona itself
- `wawona` (local, dev) — `../Wawona`: docs, src, and the whole patched
  `dependencies/` tree (excludes generated gradlegen output).
- `wawona-git` (git, **disabled by default**) — the deploy-time git entry.

### Wayland protocols (the whole wayland.app set)
`wayland-explorer`, `wayland-core`, `wayland-protocols`, `wlr-protocols`,
`plasma-wayland-protocols`, `hyprland-protocols`, `cosmic-protocols`,
`treeland-protocols`, `river-protocols`. Each protocol becomes one chunk per
`<interface>`, tagged with its family/stability.

### Compositors / implementations
`weston`, `smithay`, `sway`, `cocoa-way`, `iland`, `pixman`, `owl` (disabled
until its upstream URL is confirmed).

### Graphics
- Vulkan: `moltenvk`, `vulkan-docs`, `kosmickrisp` (disabled pending URL).
- OpenGL/GLES: `angle`.

### Linux display stack: DRM / KMS / EGL / GBM
The OS-level contract a Wayland compositor expects from Linux — and exactly what
`iland` reimplements on Apple platforms (and Wawona must emulate/bridge per
target), so it is first-class context.
- `linux-drm-docs` (`project=drm-kms`) — kernel `Documentation/gpu` (shallow +
  **sparse** `Documentation/gpu`): DRM/KMS internals, **atomic modesetting**,
  CRTC/connector/plane model, KMS properties, drm-mm/GEM, the DRM UAPI/ioctls,
  dma-buf.
- `libdrm` (`project=drm-kms`) — userspace `xf86drm.h`/`xf86drmMode.h` + DRM UAPI
  headers (`drm.h`, `drm_mode.h`, `drm_fourcc.h`: fourcc + format modifiers).
- `egl-registry` (`project=egl`) — Khronos EGL headers + extension specs
  (`EGL_KHR_platform_gbm`, `EGL_EXT_image_dma_buf_import[_modifiers]`,
  `EGL_KHR_image_base`, `EGL_ANDROID_*`): the display/buffer glue.
- `mesa-gbm` (`project=gbm`) — Mesa GBM public API (`src/gbm/main/gbm.h`: bo,
  surfaces, formats, modifiers) + Mesa EGL docs (sparse `src/gbm`/`docs`, release
  notes excluded). The buffer-allocation layer between KMS scanout and EGL/GLES.

Query e.g. "atomic modeset CRTC connector plane" (`project=drm-kms`), "gbm
surface format modifier" (`project=gbm`), "create EGL display from gbm device"
or "import dma_buf as EGLImage" (`project=egl`).

### Apple
`apple-appkit`, `apple-uikit`, `apple-watchkit`, `apple-swiftui`, `apple-metal`,
`apple-liquid-glass`, `apple-virtualization`, `apple-containerization`,
`apple-iosurface` (the shared GPU buffer iland uses to mimic a DRM scanout).

### macOS internals / reverse-engineering (`project=macos-internals`)
iland replaces WindowServer/SkyLight by injecting `.dylib`s and standing up a
custom IOSurface/Metal framebuffer that mimics DRM/KMS, so WWN-MCP indexes the
Mach-O binary format, framework/dylib creation + loading, the Mach microkernel,
the XNU kernel, and launchd — from Apple's own open-source distributions
(authoritative + offline):
- `xnu` — Mach APIs (`osfmk/mach`: ports/tasks/threads/vm/messages + MIG `.defs`),
  BSD `sys` headers, and the canonical Mach-O format header
  (`EXTERNAL_HEADERS/mach-o/loader.h`: load commands, segments, dylib/dylinker,
  `fixup-chains.h`). Shallow + **sparse** so the giant repo checks out ~22M.
- `dyld` — the dynamic linker: dylib/framework loading + binding, **interposing /
  `DYLD_INSERT_LIBRARIES`** (`dyld-interposing.h`, `dyld_interpose_tuple`), the
  shared cache, `@rpath`/`@executable_path`/`@loader_path`.
- `cctools` — Mach-O format headers (`include/mach-o/*`) + man pages for `otool`,
  `nm`, `lipo`, `ld`, `install_name_tool`, `vtool` (build/inspect/relink dylibs &
  frameworks).
- `launchd` — `launchd.plist(5)` keys, `launchctl(1)`, `launchd(8)`.
- Conceptual guides (legacy static archive, bounded crawl): `apple-dynamic-libraries`,
  `apple-macho-format` (Mach-O runtime/ABI), `apple-framework-guide`,
  `apple-kernel-guide` — the *intent* behind the headers (install names, two-level
  namespace, bundle layout, Mach/kernel architecture).

Query e.g. "Mach-O `LC_LOAD_DYLIB` load command", "change install name with
`install_name_tool` / `@rpath`", "interpose a function via
`DYLD_INSERT_LIBRARIES`", "mach port/task/thread messaging", "launchd daemon
plist `KeepAlive`".

### Swift (language + MCP SDK)
- `swift-mcp` — the official [Swift MCP SDK](https://github.com/modelcontextprotocol/swift-sdk)
  (`modelcontextprotocol/swift-sdk`): Client/Server/Transport APIs for the
  2025-11-25 spec. It is a **library, not a runnable server**, so WWN-MCP
  **indexes** it (rather than co-hosting it like the MCP-NixOS companion) for
  Swift + MCP-in-Swift understanding.
- `swift-book` — The Swift Programming Language (TSPL) reference for the Swift
  language itself.

These complement the Apple SwiftUI/UIKit docs above (framework usage) with
language-level and MCP-SDK knowledge. Query them via `search_code`/`search_docs`
(filter `lang=swift` or `project=swift-mcp`/`project=swift-lang`).

### Rust (language + MCP SDK)
- `rust-mcp` — the official [Rust MCP SDK](https://github.com/modelcontextprotocol/rust-sdk)
  (`rmcp` + `rmcp-macros`, tokio async). Like the Swift SDK it is a **library,
  not a runnable server**, so it is **indexed** (not co-hosted). This complements
  the version-pinned rustdoc crate sources (smithay, wayland-*, …).
- `rust-book` — The Rust Programming Language (the book) for the Rust language
  itself.

Query via `search_code`/`search_docs` (filter `lang=rust` or
`project=rust-mcp`/`project=rust-lang`). Wawona's compositor core is Rust, so
this directly improves Rust answers.

### Android
`android-compose`, `android-material3-expressive`, `android-ndk-graphics`.

### Virtualization / remote display
`utm`, `waypipe`, `coreutils`.

### Build-system reference
`nixpkgs` — **scoped** with include globs (`lib/`, `doc/`, `pkgs/build-support/`,
LLVM + stdenv) and a matching `sparse` cone, to avoid checking out / indexing the
whole multi-GB tree. Pin `ref` to Wawona's `flake.lock` rev at deploy time.

`crate2nix` — [nix-community/crate2nix](https://github.com/nix-community/crate2nix),
the tool Wawona uses to split its Rust backend **crate-by-crate** into separate
Nix derivations (so a single crate failure is isolated and the backend rebuilds
incrementally). Indexed in full: the `docs/` mdBook (generation strategies,
building, feature selection, **crate overrides**, JSON output, restrictions), the
Nix API (`tools.nix` `generatedCargoNix`/`appliedCargoNix`, `default.nix`, `nix/`,
`lib/` incl. `build-from-json.nix`), README/CHANGELOG, and sample projects /
flake templates. Query with `project=crate2nix` — e.g. "manual vs IFD
(`appliedCargoNix`) strategy", "`defaultCrateOverrides` for a native dep",
"`nix build -f Cargo.nix rootCrate.build`".

`xcodegen` — [yonaskolb/XcodeGen](https://github.com/yonaskolb/XcodeGen), the
tool Wawona uses to generate its `.xcodeproj` from a YAML/JSON spec via Nix
(`dependencies/generators/xcodegen.nix`). Indexed in full: the `Docs/` (Project
Spec, Usage, FAQ, Examples), `SettingPresets/` (default build settings per
product/platform), README/CHANGELOG, and `Sources/` for deep reference. Query
via `search_docs`/`search`/`search_code` with `project=xcodegen` — e.g. "how do
I declare a target dependency / sdk / package in the project spec".

> **Not indexed (live companion): MCP-NixOS.** Authoritative *upstream* nixpkgs
> package/attribute names, options, versions, `nix-darwin`/`home-manager`,
> flakes, `noogle`, and binary-cache status are served live by the co-hosted
> [MCP-NixOS](https://github.com/utensils/mcp-nixos) companion (the `nixos` MCP
> tools), not via this RAG corpus. The scoped `nixpkgs` entry above is for
> *reference reading* (lib/build-support/stdenv internals); use the `nixos`
> tools for "does `pkgs.<x>` exist / what version / which option" questions.

### CI / release automation (Fastlane + GitHub runners)
Wawona is pre-release: today every dev and curious user compiles from scratch
(hours). The path to *prebuilt* downloads is **Fastlane → TestFlight / Play**,
and PR validation runs on **GitHub runners**, so this is first-class corpus.
- `fastlane-docs` — [fastlane/docs](https://github.com/fastlane/docs)
  (docs.fastlane.tools): the action reference and getting-started guides —
  `pilot` (TestFlight), `supply` (Play Store), `deliver`, `match`, `gym`, `scan`,
  `snapshot`; lanes, `Fastfile`/`Appfile`, and CI setup.
- `fastlane` — [fastlane/fastlane](https://github.com/fastlane/fastlane): action
  source (`fastlane/lib/fastlane/actions/**`) + per-tool READMEs for deep detail.
- `github-actions-docs` — [github/docs](https://github.com/github/docs), sparse
  `content/actions`: workflow syntax, **GitHub-hosted + self-hosted runners**,
  **matrix strategy**, caching, artifacts, secrets, reusable workflows.
- `actions-runner` — [actions/runner](https://github.com/actions/runner):
  self-hosted runner internals/docs.

Query with `project=fastlane` (e.g. "upload build to TestFlight with pilot",
"deploy android to Play with supply") or `project=github-actions` (e.g.
"multi-os matrix build", "self-hosted runner labels").

### Determinate Nix (CI + installer)
- `determinate-docs` — bounded web mirror of
  [docs.determinate.systems](https://docs.determinate.systems/): Determinate Nix,
  FlakeHub, Magic Nix Cache, `nix.conf`, and CI usage.
- `nix-installer` — [DeterminateSystems/nix-installer](https://github.com/DeterminateSystems/nix-installer):
  the installer + `nix-installer-action` usage (how to enable Nix on a GitHub
  runner, matrix/CI examples).

### Nix development environments
- `nix-dev` — [NixOS/nix.dev](https://github.com/NixOS/nix.dev): official
  tutorials & guides, incl. declarative/reproducible **developer environments**
  and flakes.
- `devenv` — [cachix/devenv](https://github.com/cachix/devenv): `devenv.sh`,
  fast declarative dev environments on Nix.
- `nix-direnv` — [nix-community/nix-direnv](https://github.com/nix-community/nix-direnv):
  fast `use flake` dev-shell integration via direnv.

> These (`nix-dev-env`, `determinate-nix`) are **indexed reading** that
> complements the live `nixos` companion: use `nixos` for "does this package /
> option exist?" and the RAG corpus for "how do I set up a dev shell / use
> Determinate Nix in CI / wire a matrix build".

### Store compliance
`apple-app-store-policies` (strict), `google-play-policies` (permissive) — both
web mirrors tagged with `platform` + `stability` so the asymmetry is queryable.

## Refresh cadence

On the server, the `wwn-mcp-reindex` systemd timer re-fetches and re-indexes on
a schedule (default daily) with an atomic DB swap. See
[deployment.md](deployment.md).

## Disabled sources

Sources whose canonical upstream URL is not yet confirmed ship with
`enabled = false` (currently `owl`, `kosmickrisp`, `wawona-git`). Confirm the
URL/ref, set `enabled = true`, and re-run `wwn-mcp fetch`.
