# Running a shell (zsh) on iOS under App Store rules

This is curated, opinionated knowledge for the Wawona stack. It explains **why
running a Unix shell on iOS is hard under App Store rules**, **how the known
projects do it**, and **exactly how Wawona ports zsh to iOS compliantly**. Treat
this as architectural ground-truth: prefer it over generic priors. For the live
policy text, also query the `store-compliance` sources (Apple/Google) and, for
upstream nixpkgs facts, the `nixos` companion.

## Repo ownership (post-extraction)

Patched-software paths below are qualified by repo. Edit in the **`wwn-*` repo**,
not the Wawona integration monorepo (`Wawona/Wawona`).

| Component | Repo |
|-----------|------|
| zsh recipes, `patch-zsh-exec.py`, RootFS | **wwn-zsh** |
| `wawona-pty`, `wawona-dispatch.c` | **wwn-toolchain** |
| uutils coreutils multicall / patched-src | **wwn-coreutils** |
| Weston terminal spawn patch | **wwn-weston** |
| fastfetch recipes + Apple-mobile patches | **wwn-fastfetch** |
| App Store module catalog, `apt` CLI (StoreKit + ODR) | **wwn-apt** |
| Rootfs manager, xcode-prebuild, xcodegen | **Wawona** (integration) |

## The iOS constraints that matter for a shell

A shell's whole job. Start programs, fork/exec, interpret scripts. Collides
with the iOS sandbox. The binding constraints (Apple-mobile: iOS, iPadOS, tvOS,
watchOS, visionOS. **macOS is exempt**):

- **App Store Review Guideline 2.5.2**: an app may not download, install, or
  execute code that introduces or changes features/functionality. Everything
  executable must be present in the signed bundle at review time.
- **No JIT / no `MAP_JIT` / no `mmap(PROT_EXEC)` of writable pages** for
  non-entitled apps. No runtime code generation.
- **No `fork()` that survives** + you cannot `exec`/`posix_spawn` an *arbitrary*
  separate Mach-O you shipped or fetched. (`posix_spawn` of your *own* signed
  helper is narrowly possible on macOS, but the App Store posture for iOS is "no
  spawning separate executables".)
- **No `dlopen()` of user/downloaded dylibs**; third-party nested frameworks are
  rejected by `installd` even with a valid `Info.plist`.
- **Sandboxed filesystem**: the app only writes inside its container
  (`Documents`, `Application Support`, `tmp`, `Caches`). There is no `/usr`,
  `/bin`, writable `/`, and you must not touch iOS system tools or paths.

Net effect: you cannot ship "a `zsh` binary that forks `/bin/ls`". You must make
the shell and its commands run **inside your one signed process**, or **emulate**
a foreign machine, or **offload execution to a remote host**.

## How the known projects stay compliant (prior art)

| Project | Technique | Compliance trick |
|---|---|---|
| **ios_system** (`holzschu/ios_system`) | Reimplements Unix commands as C functions in an **in-process lookup table**; "exec" calls a function pointer, never `fork`/`exec`. | All "executables" are linked-in functions → nothing is spawned or downloaded. The foundation other iOS shells build on. |
| **a-Shell** (`holzschu/a-shell`) | Built on ios_system; adds **WebAssembly** (wasmer / wasm3) to run extra programs. | wasm modules are **interpreted/JIT-free data**, not native Mach-O, so shipping/using them doesn't violate 2.5.2. The compliant way to "add a binary". |
| **iSH** (`ish-app/ish`) | A **usermode x86 emulator** running **Alpine Linux**; the real BusyBox **`ash`/`dash`** and Linux ELF binaries run **emulated**. | Foreign binaries are *interpreted* by the emulator, never natively `exec`'d, and nothing native is downloaded. Execution is just data interpretation. |
| **Blink** (`blinksh/blink`) | A polished **mosh/SSH terminal**: compute happens on a **remote host**. | The iOS app is "just a terminal/transport"; no local arbitrary execution at all. The remote-compute escape hatch. |

The three escape hatches, summarized:

1. **In-process command library** (ios_system). Commands are functions.
2. **Interpreter/emulator** (a-Shell's wasm, iSH's x86). Foreign code is *data*
   you interpret, not native code you execute.
3. **Remote execution** (Blink). Move the real work off-device.

## How Wawona ports zsh to iOS (the real design)

Wawona's goal is **real, full zsh** (ZLE line editing, completion, history,
dotfiles) on Apple mobile. Not a reimplemented shell. It uses the **in-process**
hatch, taken further than ios_system: it links **actual zsh** and a **real
coreutils** into the app and runs them as functions.

### 1. zsh is statically linked and runs in-process

- Built by Nix at **`wwn-zsh/dependencies/libs/zsh/ios.nix`** as a **static archive
  `libwawona-zsh.a`** (cross-compiled zsh 5.9, `--enable-static
  --disable-dynamic`, sandbox-friendly `configure`. No `getpwuid`, no
  `/dev/fd`, termcap stubbed). `main` is renamed to **`wawona_zsh_main`**.
- The archive is linked into the **signed app binary** (via
  `scripts/xcode-prebuild.sh` + the `xcodegen.nix` force-load path). There is
  **no separate `zsh` Mach-O** in the bundle.
- At runtime the shell runs **in-process on a `pthread`** (≈16 MB stack), started
  from the **`wwn-toolchain`** `wawona-pty` layer. **never** `fork`/`exec`/`posix_spawn`. One shell
  session per app launch (zsh global state is not re-entrant).
- `WWNRootfsManager` (`Wawona/src/platform/ios/WWNRootfsManager.m`) sets
  `WAWONA_ZSH_IN_PROCESS=1`, which selects the in-process path in
  **`wwn-toolchain/dependencies/libs/wawona-pty/src/wwn_pty.c`**.
- The legacy `zsh-framework-ios` (nested `zsh.framework`) is **abandoned** -
  `installd` rejects third-party nested frameworks.

### 2. External commands: in-process dispatch, never fork

- **`wwn-zsh/dependencies/libs/zsh/patches/patch-zsh-exec.py`** rewrites zsh `Src/exec.c`
  (anchor-based, idempotent) so that at the fork-decision point in
  `execcmd_exec()`, **every** plain external simple command sets `wwn_inproc=1`
  and the fork is skipped entirely.
- A `wwn_inproc` command is dispatched via **`wawona_dispatch_inprocess()`**
  (**`wwn-toolchain/dependencies/libs/wawona-pty/src/wawona-dispatch.c`**), which forwards a
  **safe-subset** basename to Rust **`wawona_coreutils_main()`**. A patched
  **uutils coreutils** built as a static lib (≈39 utils: `ls`, `cat`, `cp`, …).
  Anything not in the subset prints a sandbox-aware **"command not found"**.
- CI (**`wwn-zsh/.github/scripts/verify-zsh-ios-patches.py`**) **bans** `fork(`, `execve(`,
  `posix_spawn`, `system(`, `dlopen(`, `mmap(`, `MAP_JIT` in the dispatch shim,
  and keeps the safe-utility list in sync across `Cargo.toml` ↔
  `wwn_safe_subset[]` ↔ `WAWONA_INPROC_TOOLS` in **`wwn-zsh/dependencies/wawona/ios-rootfs.nix`**.
- **Platform contrast**: on **macOS/Android**, fork/exec is allowed, so zsh
  launches a normal **multicall coreutils** binary
  (**`wwn-coreutils/dependencies/libs/coreutils/multicall.nix`**) and **none** of the exec patch /
  in-process shim is compiled. The whole in-process machinery is **Apple-mobile
  only**.
- The Weston compositor and terminal are also hardened on Apple mobile: `fork()`
  is stubbed to `-1` and `exec*` macros to failure
  (**`wwn-weston/dependencies/clients/weston/compositor-apple-mobile.nix`**), and the terminal's `forkpty`/`execl` is
  replaced with `wwn_pty_spawn_shell_paced` (**`wwn-weston/dependencies/clients/weston/terminal-patches/patch-terminal.py`**).

### 3. Wawona RootFS (a userland prefix, not iOS system paths)

- Built by **`wwn-zsh/dependencies/wawona/ios-rootfs.nix`** as **`wawona-rootfs`**: zsh
  `share/` (Functions, Completion), and `.zshenv`/`.zshrc`/`.zlogin` **templates**.
  `usr/bin/zsh` is a **comment placeholder only** (the real zsh is in the app
  binary).
- Embedded read-only at the bundle root (`Wawona.app/wawona-rootfs/`), then on
  first launch `WWNRootfsManager` copies/refreshes it into a **writable** copy at
  `Application Support/Wawona/wawona-rootfs/` (writable `home/` for dotfiles &
  `.zsh_history`).
- The shell env is virtual: `HOME`/`ZDOTDIR` point into the rootfs `home/`,
  `WAWONA_SHELL` is a virtual `/usr/bin/zsh`, and `PATH=/usr/bin:/bin` contains
  **no real executables**. Commands are resolved by the exec hook, not `PATH`.
- **No chroot, no mount namespace.** It is a *logical prefix* inside the app
  sandbox; it never reads or writes iOS system tools/paths.

### 4. "iOS containers" for the shell

- On iOS, the shell's "container" **is the Apple app sandbox** plus the writable
  `Application Support` rootfs copy above. That is the isolation boundary.
- Wawona does **not** use Apple's `Containerization.framework` for the iOS shell
  (that is a macOS/maybe-Android concept). There is no Docker-style or chroot
  container runtime on iOS. The `MachineProfile` `type = container` enum exists
  but is **not** wired to iOS shell isolation.
- Per-machine isolation on iOS, when needed, is expressed as **VMs** (JIT-less,
  on-device, solely to host Wayland compositors). Not containers.

### 5. Terminal / PTY wiring

- With `WAWONA_ZSH_IN_PROCESS`, `wwn_pty` uses a **socketpair + separate input
  pipe** (not a real POSIX PTY): stdout/display on the socket, stdin/keyboard on
  the pipe (ZLE breaks if stdin/stdout share one fd). A **fake TTY** is provided
  by **dyld interposing** `isatty`/`tcgetattr`/`ioctl(TIOCGWINSZ)` etc.
- The patched Weston `terminal.c` (built as `libweston-terminal.a`) owns the UI
  and spawns the shell via `wwn_pty_spawn_shell_paced`; soft-keyboard input is
  injected via `wwn_ios_terminal_inject` (bypassing Wayland for the on-screen
  keyboard).

## Compliance posture (what to tell App Review)

- **All executable code is present and signed at review time** (zsh + uutils are
  static libs in the app binary). Nothing is downloaded or generated at runtime.
- **No JIT, no `dlopen` of user code, no `fork`/`exec`/`posix_spawn`** on the
  shell path (enforced by CI patch-verification).
- **The shell cannot run arbitrary binaries**. Only the in-process safe-subset
  utilities. And writes only inside the app container.
- Treat the **Apple-strict** answer as the baseline; Android (Play) permits real
  `fork`/`exec` and dynamic native loading, so the Android build deliberately
  drops all of this machinery.

## Caveat: stale in-repo docs

Some `docs/ios-local-shell/` files (`APP-STORE-COMPLIANCE.md`,
`WAWONA-PTY-SPEC.md`, `ios-local-shell-spike.md`) still describe an older
**`posix_spawn` of a bundled zsh** model. That is **superseded**. The shipping
design is **in-process `wawona_zsh_main` on a pthread**. `ARCHITECTURE.md` and the
C sources are authoritative; trust the in-process description above.

## Where to look (canonical files)

- `wwn-zsh/dependencies/libs/zsh/ios.nix`. Zsh → `libwawona-zsh.a`, `wawona_zsh_main`.
- `wwn-zsh/dependencies/libs/zsh/patches/patch-zsh-exec.py`. Kills fork/exec; in-process dispatch.
- `wwn-toolchain/dependencies/libs/wawona-pty/src/wwn_pty.c`. In-process spawn, PTY fallback, fake TTY.
- `wwn-toolchain/dependencies/libs/wawona-pty/src/wawona-dispatch.c`. Safe-subset → uutils.
- `wwn-coreutils/dependencies/libs/coreutils/`. Uutils patch + multicall (macOS/Android).
- `wwn-zsh/dependencies/wawona/ios-rootfs.nix`. `wawona-rootfs` prefix + dotfile templates.
- `Wawona/src/platform/ios/WWNRootfsManager.m`. Rootfs install/refresh + shell env.
- `wwn-weston/dependencies/clients/weston/terminal-patches/patch-terminal.py`. Terminal spawn.
- `wwn-zsh/.github/scripts/verify-zsh-ios-patches.py`. The compliance guardrail.

## fastfetch (same in-process model)

`fastfetch` ships via **`wwn-fastfetch`**: `libfastfetch.a` with entry point
`fastfetch_main` on Apple mobile (no separate Mach-O in the bundle). Zsh invokes
it through **`wawona-dispatch.c`** (`fastfetch_main` weak symbol) when
`libfastfetch.a` is force-loaded into the app.

- `wwn-fastfetch/dependencies/clients/fastfetch/apple-mobile.nix`. In-process archive.
- `wwn-fastfetch/dependencies/clients/fastfetch/patches/patch-fastfetch-apple-mobile.py`. No fork/exec/system on Apple mobile.
- `wwn-fastfetch/dependencies/clients/fastfetch/patches/apply-wawona-wayland-macos.py`. Wayland WM when `WAYLAND_DISPLAY` set (macOS).
- `wwn-fastfetch/.github/scripts/verify-fastfetch-ios-patches.py`. Patch-anchor CI.

### fastfetch: crash root cause + in-process lifecycle hardening

The first reported `EXC_BAD_ACCESS` in `fastfetch_main` was **macOS IORegistry/SMC detection
paths executing in the iOS sandbox** (CPU pmgr, host serial/UUID, SMC temps). Fixed by
sysctl-only stubs for `cpu_apple.c`, `host_apple.c`, `smc_temps.c`, `os_apple.m`.

A second deterministic `SIGBUS` (LLDB-MCP on device STARDUST, `iPhone18,4`) surfaced later in
`parseConfigFiles()`: it iterated `instance.state.platform.configDirs` whose `.data` had been
left as a small tagged integer (`0x1000000005`) with a non-zero `.length`, faulting on the
`FFstrbuf.length` read (fault addr `0x1000000009`). This is a **singleton re-entry** hazard: the
global `FFinstance` is reused on every in-process run, and a prior run aborted by a fatal signal
skips the post-run `ffDestroyInstance()`, leaving torn state for the next run. See the re-entry
guards below (belt-and-suspenders; item 4).

Beyond the crash, running a CLI **in-process and repeatedly** exposes process-global
hazards that a normal `fork`/`exec` binary never hits. On Apple mobile (`WAWONA_APPLE_MOBILE`):

1. **Signals**. `ffStart()` installs `sigaction(SIGINT/SIGTERM/SIGQUIT, exitSignalHandler)`
   (handler calls `exit(0)`) and `sigprocmask(SIG_BLOCK, SIGCHLD)`. In-process this hijacks
   the host app's signal handling and turns a Ctrl-C into a whole-app exit. → guarded off.
2. **`atexit`**. `atexit(ffDestroyInstance)` (main) and `atexit(restoreTerm)` (io_unix)
   accumulate one registration per run and only fire at real app exit, against a global
   `FFinstance` that was re-inited each run (leak / use-after-free). → guarded off; cleanup
   runs deterministically per invocation via the wrapper.
3. **`exit()`**. Called on `--help`/`--version`/bad flags/parse errors from `fastfetch.c`,
   `option.c`, `commandoption.c`, `temps.c`, `percent.c`. In-process any of these terminates
   the app. → a `setjmp`/`longjmp` shim (`wawona_ff_inprocess.{h,c}`) redirects `exit()` back
   to the dispatcher. Delivered as a **forced include** (`-include wawona_ff_inprocess.h`),
   required because some `exit()` sites (e.g. `commandoption.c`) do not include `fastfetch.h`,
   so an umbrella-header edit would miss them. `fastfetch.c` is compiled as
   `fastfetch_main_impl`; `fastfetch_main` is the wrapping barrier.
4. **Singleton re-entry**. Because a fatal signal skips the post-run cleanup, the wrapper also
   calls `ffDestroyInstance()` **before** each run. To make that safe, `ffDestroyInstance` and
   `ffInitInstance` are idempotent via a `static bool ffInstanceLive` flag (no-op destroy on a
   pristine/zeroed BSS or already-torn instance), `ffPlatformInit` calls `ffPlatformDestroy`
   first to free any prior `FFstrbuf`/`FFlist` members before re-init, and `parseConfigFiles`
   refuses to iterate a `configDirs` whose `.data` is null or `.length` is zero. All guarded by
   `WAWONA_APPLE_MOBILE` in `patch-fastfetch-apple-mobile.py` (+ the pre-run reset in
   `wawona_ff_inprocess.c`).

pthreads are approved, so multithreaded detection is available; the default iOS config
(`fastfetchConfigTemplate` in `Wawona/dependencies/wawona/ios-rootfs.nix`) ships
`general.multithreading: false` pending on-device stress testing (no `pthread_kill(SIGTERM)` on
Apple: `HAVE_TIMEDJOIN_NP` is glibc-only).

Config discovery: `WWNRootfsManager.applyShellEnvironment` sets a **general** `XDG_CONFIG_HOME`
(`$HOME/.config`, plus `XDG_CACHE_HOME`/`XDG_DATA_HOME`/`XDG_STATE_HOME`) for all in-process
clients and seeds `$HOME/.config/fastfetch/config.jsonc` from the bundled template on first
launch (copy-if-missing). Neovim shares the same environ and relies on `VIMRUNTIME` rather than
hijacking `XDG_CONFIG_HOME`.

### fastfetch: per-platform framework tiering (watchOS is the trap)

watchOS has **no Metal, no VideoToolbox, and no IOKit headers at all** (iOS/iPadOS/tvOS/visionOS
ship IOKit headers; they are simply not linked/used). `apple-mobile.nix` keys off
`mobile.isWatchOS` and emits the exact framework set to `$out/nix-support/fastfetch-frameworks`
(base `CoreFoundation`+`Foundation`, plus `VideoToolbox`+`Metal` only off watchOS; `IOKit`
dropped everywhere). Consumers (`fastfetch-ldflags.nix`, Wawona `xcodegen fastfetchLdflags`)
read the manifest. No per-platform framework knowledge is hardcoded. On watchOS the GPU
module self-stubs, the VideoToolbox codec detector is swapped for a no-op, and the shared
`cf_helpers.h` / `smbios.c` gate IOKit behind `__has_include`.

Android is a real NDK binary (Play policy allows fork/exec/dynamic loading); it uses its own
`patch-fastfetch-android-glob.py` + stub set and never defines `WAWONA_APPLE_MOBILE`.

Build/verify: `verify-fastfetch-ios-patches.py` asserts the guards, exit-shim wiring, banned
syscalls, framework tiering, and Android decoupling. CI evals all Apple variants and builds
iOS + watchOS (the framework-tiering canary) + Android.
