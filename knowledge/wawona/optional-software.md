# Optional software (wasm and deb)

Wawona ships the compositor plus a tiny shell. Optional Wayland clients install
from `repo.wawona.io`.

## Keep in the app

- Smithay compositor + iLand (ANGLE / MoltenVK as needed)
- Relay wasm runtime + `hello-wasi-gui` smoke
- zsh, uutils safe subset, fastfetch (App Store patches stay here only)

## Move out

weston, niri, foot, weston-terminal, weston toys, GPU cubes → **deb**
(jailbreak iOS rootless/rootful, Termux, Linux). No App Store patches in those
recipes. GTK toolkit → WASIX **`pkgs/libraries/`** (not `programs/`) plus deb
on `repo.wawona.io`. Store optional GUI → wasm P1 / WASIX lanes. See
`libraries-vs-programs.md`.
Termux Android debs: Google NDK clang (Bionic `aarch64`, prefix
`/data/data/com.termux/files/usr`). Recipe helper:
`repo.wawona.io/lib/androidNdk.nix`. Never pack glibc Linux ELFs. Do not use
nixpkgs `aarch64-unknown-linux-android` GCC bootstrap on Darwin.

## Deb simplification

Debs may fork/exec/JIT. Do not copy `apple-mobile.nix`, renamed `*_main`, or
in-process cairo skips into deb recipes. Unlink from the app, then delete that
client's App Store patch set.

## Stale xcodegen (2026-10-12)

After unlink, tip `xcodegen.nix` must drop `-force_load libfoot.a` /
`libfuzzel.a`. Leftover `Wawona.xcodeproj` still force_loads them;
prebuild does not build those archives. Lab: ios-sim stubs for
`foot_main` / `fuzzel_main`, or regenerate from tip Nix.

## Link-line fallout of an unlink (2026-10-12)

Dropping a client's ldflags helper also drops keep-set archives that helper
carried. `westonToytoolkitLdflagsAppleMobile` /
`westonCompositorLdflagsAppleMobile` were the only providers of:

- `-force_load libwwn-pty.a` (wwn-toolchain `wawona-pty`): the in-process shell
  ABI (`wwn_pty_session_*`, `wwn_zsh_soft_exit`, `wwn_pty_ios_*`) and the
  store-safe dispatch (`wawona_dispatch_can_handle` / `_inprocess` /
  `_spawn_async`). Plain C archive, no Rust std, so `-force_load` is safe and
  required (force-loaded zsh references it from later on the link line).
- `-lwayland-server`: watchOS `WWNMiniWaylandServer.c` host compositor, and the
  `xdg-shell-protocol.o` that `wwn-toolchain libwayland/watchos.nix` merges into
  `libwayland-server.a` (`xdg_wm_base_interface` and friends).
- `-liconv`: zsh `zreaddir` / `getkeystring`. tvOS and watchOS already listed
  it; iOS, iPadOS, and visionOS did not.

Two more classes:

- Darwin does not allow-miss a weak *declaration* inside a `-force_load`ed
  object. `wawona-dispatch.o` references every client entry point, so unlinked
  clients need stub definitions (`WWNAppleMobileOptionalStubs.c`,
  `WWNWatchStubs.c`), including `phoon_main`,
  `wwn_weston_compositor_is_running`, `wwn_niri_main_is_running`,
  `wwn_niri_main_already_used`. Swift `@_silgen_name` refs (`kmscube_main`,
  `gbm_es2_demo_main`) are strong, not weak.
- Never `-force_load libiland_userland.a` on a target with no ANGLE: its
  `egl.c.o` is built with `ILAND_ANGLE_STATIC` and imports 24 `angle_egl*`.
  Store Apple-mobile presents through Metal. Use lazy `-liland_userland` plus
  `-Wl,-u,_iland_drm_set_present_callback` / `_set_preferred_mode` /
  `_complete_page_flip` / `_prepare_virtual_fd`. Nothing else in the archive
  references EGL, so `egl.c.o` drops and the DRM/KMS/GBM path still links.

Fixed in Wawona `bfe4b81a` (watchOS) and `430dbe3a` (iOS / iPadOS / visionOS).

## Rules

`wawona-optional-software`, `wawona-native-compositors`, `repo-wawona-io-channels`,
`wawona-wasm-cli-ports`. Skill: `wawona-optional-software`.

Default Machines session: Native Shell (zsh), not `weston-terminal`.
