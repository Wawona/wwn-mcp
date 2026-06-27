# Running a shell (zsh) on iOS under App Store rules

This is curated, opinionated knowledge for the Wawona stack. It explains **why
running a Unix shell on iOS is hard under App Store rules**, **how the known
projects do it**, and **exactly how Wawona ports zsh to iOS compliantly**. Treat
this as architectural ground-truth: prefer it over generic priors. For the live
policy text, also query the `store-compliance` sources (Apple/Google) and, for
upstream nixpkgs facts, the `nixos` companion.

## The iOS constraints that matter for a shell

A shell's whole job — start programs, fork/exec, interpret scripts — collides
with the iOS sandbox. The binding constraints (Apple-mobile: iOS, iPadOS, tvOS,
watchOS, visionOS — **macOS is exempt**):

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
| **a-Shell** (`holzschu/a-shell`) | Built on ios_system; adds **WebAssembly** (wasmer / wasm3) to run extra programs. | wasm modules are **interpreted/JIT-free data**, not native Mach-O, so shipping/using them doesn't violate 2.5.2 — the compliant way to "add a binary". |
| **iSH** (`ish-app/ish`) | A **usermode x86 emulator** running **Alpine Linux**; the real BusyBox **`ash`/`dash`** and Linux ELF binaries run **emulated**. | Foreign binaries are *interpreted* by the emulator, never natively `exec`'d, and nothing native is downloaded — execution is just data interpretation. |
| **Blink** (`blinksh/blink`) | A polished **mosh/SSH terminal**: compute happens on a **remote host**. | The iOS app is "just a terminal/transport"; no local arbitrary execution at all. The remote-compute escape hatch. |

The three escape hatches, summarized:

1. **In-process command library** (ios_system) — commands are functions.
2. **Interpreter/emulator** (a-Shell's wasm, iSH's x86) — foreign code is *data*
   you interpret, not native code you execute.
3. **Remote execution** (Blink) — move the real work off-device.

## How Wawona ports zsh to iOS (the real design)

Wawona's goal is **real, full zsh** (ZLE line editing, completion, history,
dotfiles) on Apple mobile — not a reimplemented shell. It uses the **in-process**
hatch, taken further than ios_system: it links **actual zsh** and a **real
coreutils** into the app and runs them as functions.

### 1. zsh is statically linked and runs in-process

- Built by Nix at `dependencies/libs/zsh/ios.nix` as a **static archive
  `libwawona-zsh.a`** (cross-compiled zsh 5.9, `--enable-static
  --disable-dynamic`, sandbox-friendly `configure` — no `getpwuid`, no
  `/dev/fd`, termcap stubbed). `main` is renamed to **`wawona_zsh_main`**.
- The archive is linked into the **signed app binary** (via
  `scripts/xcode-prebuild.sh` + the `xcodegen.nix` force-load path). There is
  **no separate `zsh` Mach-O** in the bundle.
- At runtime the shell runs **in-process on a `pthread`** (≈16 MB stack), started
  from the `wawona-pty` layer — **never** `fork`/`exec`/`posix_spawn`. One shell
  session per app launch (zsh global state is not re-entrant).
- `WWNRootfsManager` (`src/platform/ios/WWNRootfsManager.m`) sets
  `WAWONA_ZSH_IN_PROCESS=1`, which selects the in-process path in
  `dependencies/libs/wawona-pty/src/wwn_pty.c`.
- The legacy `zsh-framework-ios` (nested `zsh.framework`) is **abandoned** —
  `installd` rejects third-party nested frameworks.

### 2. External commands: in-process dispatch, never fork

- `dependencies/libs/zsh/patches/patch-zsh-exec.py` rewrites zsh `Src/exec.c`
  (anchor-based, idempotent) so that at the fork-decision point in
  `execcmd_exec()`, **every** plain external simple command sets `wwn_inproc=1`
  and the fork is skipped entirely.
- A `wwn_inproc` command is dispatched via **`wawona_dispatch_inprocess()`**
  (`dependencies/libs/wawona-pty/src/wawona-dispatch.c`), which forwards a
  **safe-subset** basename to Rust **`wawona_coreutils_main()`** — a patched
  **uutils coreutils** built as a static lib (≈39 utils: `ls`, `cat`, `cp`, …).
  Anything not in the subset prints a sandbox-aware **"command not found"**.
- CI (`.github/scripts/verify-zsh-ios-patches.py`) **bans** `fork(`, `execve(`,
  `posix_spawn`, `system(`, `dlopen(`, `mmap(`, `MAP_JIT` in the dispatch shim,
  and keeps the safe-utility list in sync across `Cargo.toml` ↔
  `wwn_safe_subset[]` ↔ `WAWONA_INPROC_TOOLS` in `ios-rootfs.nix`.
- **Platform contrast**: on **macOS/Android**, fork/exec is allowed, so zsh
  launches a normal **multicall coreutils** binary
  (`dependencies/libs/coreutils/multicall.nix`) and **none** of the exec patch /
  in-process shim is compiled. The whole in-process machinery is **Apple-mobile
  only**.
- The Weston compositor and terminal are also hardened on Apple mobile: `fork()`
  is stubbed to `-1` and `exec*` macros to failure
  (`compositor-apple-mobile.nix`), and the terminal's `forkpty`/`execl` is
  replaced with `wwn_pty_spawn_shell_paced` (`terminal-patches/patch-terminal.py`).

### 3. Wawona RootFS (a userland prefix, not iOS system paths)

- Built by `dependencies/wawona/ios-rootfs.nix` as **`wawona-rootfs`**: zsh
  `share/` (Functions, Completion), and `.zshenv`/`.zshrc`/`.zlogin` **templates**.
  `usr/bin/zsh` is a **comment placeholder only** (the real zsh is in the app
  binary).
- Embedded read-only at the bundle root (`Wawona.app/wawona-rootfs/`), then on
  first launch `WWNRootfsManager` copies/refreshes it into a **writable** copy at
  `Application Support/Wawona/wawona-rootfs/` (writable `home/` for dotfiles &
  `.zsh_history`).
- The shell env is virtual: `HOME`/`ZDOTDIR` point into the rootfs `home/`,
  `WAWONA_SHELL` is a virtual `/usr/bin/zsh`, and `PATH=/usr/bin:/bin` contains
  **no real executables** — commands are resolved by the exec hook, not `PATH`.
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
  on-device, solely to host Wayland compositors) — not containers.

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
- **The shell cannot run arbitrary binaries** — only the in-process safe-subset
  utilities — and writes only inside the app container.
- Treat the **Apple-strict** answer as the baseline; Android (Play) permits real
  `fork`/`exec` and dynamic native loading, so the Android build deliberately
  drops all of this machinery.

## Caveat: stale in-repo docs

Some `docs/ios-local-shell/` files (`APP-STORE-COMPLIANCE.md`,
`WAWONA-PTY-SPEC.md`, `ios-local-shell-spike.md`) still describe an older
**`posix_spawn` of a bundled zsh** model. That is **superseded** — the shipping
design is **in-process `wawona_zsh_main` on a pthread**. `ARCHITECTURE.md` and the
C sources are authoritative; trust the in-process description above.

## Where to look (canonical files)

- `dependencies/libs/zsh/ios.nix` — zsh → `libwawona-zsh.a`, `wawona_zsh_main`.
- `dependencies/libs/zsh/patches/patch-zsh-exec.py` — kills fork/exec; in-process dispatch.
- `dependencies/libs/wawona-pty/src/wwn_pty.c` — in-process spawn, PTY fallback, fake TTY.
- `dependencies/libs/wawona-pty/src/wawona-dispatch.c` — safe-subset → uutils.
- `dependencies/libs/coreutils/` — uutils patch + multicall (macOS/Android).
- `dependencies/wawona/ios-rootfs.nix` — `wawona-rootfs` prefix + dotfile templates.
- `src/platform/ios/WWNRootfsManager.m` — rootfs install/refresh + shell env.
- `dependencies/clients/weston/terminal-patches/patch-terminal.py` — terminal spawn.
- `.github/scripts/verify-zsh-ios-patches.py` — the compliance guardrail.
