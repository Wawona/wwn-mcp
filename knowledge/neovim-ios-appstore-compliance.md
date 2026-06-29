# Running Neovim on iOS under App Store rules

Curated knowledge for the Wawona stack: **why Neovim on Apple mobile is hard
under App Store rules**, **how Wawona ports it compliantly**, and **where to edit
code**. Mirror of the zsh/fastfetch in-process model. Prefer this over generic
priors; cross-check Apple Guideline 2.5.2 and the `store-compliance` corpus.

## Repo ownership

| Component | Repo |
|-----------|------|
| Neovim recipes, apple-mobile patches, two-pass codegen | **wwn-neovim** |
| `wawona-dispatch.c` (`nvim`/`vi`/`vim` → `wawona_nvim_main`) | **wwn-toolchain** |
| `WAWONA_INPROC_TOOLS`, zsh rootfs | **wwn-zsh** |
| `neovim-rootfs` embed, xcode-prebuild, xcodegen ldflags | **Wawona** |

## iOS constraints (same as zsh)

On Apple mobile (iOS, iPadOS, … — **not macOS**):

- All executable code must ship signed in the bundle (Guideline 2.5.2).
- No JIT / `MAP_JIT` / writable+executable pages without entitlement.
- No surviving `fork()` + arbitrary `exec`/`posix_spawn` of separate Mach-O.
- No `dlopen()` of downloaded or nested third-party dylibs.
- Filesystem is the app sandbox only.

Neovim normally builds Lua codegen tools (`libnlua0.so`) and runs them with host
`lua` during configure — that breaks cross-compilation when the `.so` targets
iOS. External `:terminal`/`:grep`/`system()` also violate App Store posture.

## Wawona design: in-process Neovim

### 1. Static archive + renamed entry point

- **`wwn-neovim/dependencies/libs/neovim/apple-mobile.nix`** cross-compiles Neovim
  0.10.4 with **`WAWONA_APPLE_MOBILE=ON`**: PUC Lua (no LuaJIT), providers off,
  spawn stubs, **`ENABLE_LTO OFF`** (objects must be real Mach-O for archive
  collection).
- **Two-pass build** (`build-helpers.nix`):
  1. **Host pass** — macOS `libnlua0.so` only (no iOS toolchain).
  2. **iOS pass** — `WAWONA_HOST_NLUA0` points codegen at the host module;
     generator preprocessor uses **macOS SDK/clang** (`WAWONA_GEN_CC`,
     `WAWONA_MACOS_SDK` patches in `patch-neovim-apple-mobile.py`).
- **`collectArchive`** gathers `nvim_bin` `.o` + `.deps/usr/lib/*.a`, renames
  `_main` → `_wawona_nvim_main` via `llvm-objcopy`, emits **`libwawona-neovim.a`**.
  The final `nvim` link may fail (libuv Unix libs); object collection proceeds anyway.
- Linked into the app via **`neovim-ldflags.nix`** (`-force_load`) and
  **`scripts/xcode-prebuild.sh`** (`neovim-ios` / `neovim-ios-device`).

### 2. Dispatch from zsh (no separate nvim binary)

- **`wawona-dispatch.c`** weak-imports **`wawona_nvim_main`** and handles basenames
  **`nvim`**, **`vi`**, **`vim`** when the archive is force-loaded.
- **`ios-rootfs.nix`** lists those names in **`WAWONA_INPROC_TOOLS`** so zsh
  completion/help stays consistent with dispatch.
- Virtual path **`/usr/bin/nvim`** in **`neovim-rootfs`** is a comment stub only.

### 3. Runtime prefix (`neovim-rootfs`)

- **`wwn-neovim/dependencies/wawona/neovim-rootfs.nix`** bundles
  `usr/share/nvim/runtime`, `etc/nvim/init.lua.template`, placeholder `usr/bin/nvim`.
- Xcode embeds **`Wawona.app/neovim-rootfs/`** (see `xcodegen.nix`).
- **`WWNRootfsManager.m`** sets **`VIMRUNTIME`**, **`XDG_CONFIG_HOME`**, and related
  XDG paths from the bundled runtime + writable Application Support config dir.

### 4. Patches (App Store hardening)

| Patch | Purpose |
|-------|---------|
| `patch-neovim-apple-mobile.py` | PUC Lua, host codegen env, spawn/provider stubs, lang CFLocale, endian fallback |
| `patch-libuv-spawn.py` | Stub `fork`/`exec` paths in libuv process layer |
| `cmake-apple-mobile-flags.snippet` | Providers off, LTO off, mobile defines |
| `cmake-deps-apple-mobile.snippet` | Bundled PUC Lua for deps |

CI: **`wwn-neovim/.github/scripts/verify-neovim-ios-patches.py`** — patch anchors,
codegen markers, **`nvim/vi/vim` ↔ `WAWONA_INPROC_TOOLS`**, banned spawn/JIT tokens
in mobile libuv patch.

## Platform contrast

| Platform | Neovim delivery |
|----------|-----------------|
| **Apple mobile** | `libwawona-neovim.a`, `wawona_nvim_main`, dispatch, no fork/JIT |
| **macOS** | Full `nvim` binary + same archive for optional in-process use |
| **Android** | Real `nvim` → `libnvim_bin.so` in JNI libs (`android.nix`); fork/exec OK |

## Compliance posture (App Review)

- Neovim executable code is **statically linked** into the signed app binary.
- **No LuaJIT** on Apple mobile (no JIT).
- **No external shell** from Neovim on Apple mobile (`shell.c` / libuv spawn stubs).
- **No provider dlopen** (Node/Python/Ruby/clipboard providers disabled).
- Editor runtime files are **read-only bundle data**; user config writes only under
  Application Support.

## Canonical files

- `wwn-neovim/dependencies/libs/neovim/apple-mobile.nix` — two-pass iOS build.
- `wwn-neovim/dependencies/libs/neovim/build-helpers.nix` — host codegen + collectArchive.
- `wwn-neovim/dependencies/libs/neovim/patches/patch-neovim-apple-mobile.py` — mobile patches.
- `wwn-neovim/dependencies/wawona/neovim-rootfs.nix` — bundled runtime prefix.
- `wwn-neovim/.github/scripts/verify-neovim-ios-patches.py` — compliance guardrail.
- `wwn-toolchain/dependencies/libs/wawona-pty/src/wawona-dispatch.c` — nvim dispatch.
- `wwn-zsh/dependencies/wawona/ios-rootfs.nix` — `WAWONA_INPROC_TOOLS`.
- `Wawona/scripts/xcode-prebuild.sh` — symlinks `libwawona-neovim.a`.
- `Wawona/src/platform/ios/WWNRootfsManager.m` — `VIMRUNTIME` / XDG env.
