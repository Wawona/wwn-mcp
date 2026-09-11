# Weston default wallpaper is honeycomb

Upstream Weston 13 `data/background.png` is the honeycomb RGB wallpaper.
That is the Wawona default on every target (iOS family, macOS, Android,
Linux, watchOS, Classic igetty).

## Never

- Use `pattern.png` as `[shell] background-image`. That file is
  indexed-color. Cairo often fails to load it, then only
  `background-color` (`0xff1a1a2e`) shows.
- Treat a solid desktop as a missing desktop-shell. Check the ini
  wallpaper path first. Navy `0xff1a1a2e` with no honeycomb is a
  missing `background-image` (proof ini or skinny share/weston).

## Where

| Target | Writer |
|---|---|
| iOS / iPadOS / tvOS / visionOS / macOS Machines | `WWNWaypipeRunner` `wwnWriteWestonIniAtPath` |
| watchOS | `WWNWatchCompositorBridge` `launchWeston` |
| Android | `android_jni.c` + `WWNWriteWestonHoneycombIni` |
| Linux Machines | `src/core/weston_ini.rs` via `src/linux/launcher.rs` |
| macOS CLI `Wawona weston` | `scripts/macos-register-cli-bins.sh` |
| Classic Mode B TTY | `wwn-igetty` `libexec/wwn-modeb-session/weston` |
| In-process desktop-shell default | L3 `wwn-weston` `ios.nix` / `android.nix` (`WESTON_DATA_DIR/background.png`) |

Shared Rust writer: `Wawona/src/core/weston_ini.rs`.
Needs `git add` before crate2nix sees a new `.rs` file.

L3 desktop-shell default reaches L4 only after the `wwn-weston` flake input
is bumped. L4 ini writers do not wait on that bump.

`pattern.png` stays bundled for `weston-image` / toytoolkit, not wallpaper.
