# macOS Aqua weston bins (skinny /Applications)

Aqua nested weston is an NSTask: `Resources/bin/weston --backend=wayland`
plus `lib/libweston-13/wayland-backend.*`, `lib/weston/desktop-shell.*`,
`share/weston`, and `weston-desktop-shell` next to the binary.

`nix build .#wawona-macos` verifies those (`verifyAquaClientBins`).
`/Applications/Wawona.app` and incremental Xcode Debug
(`WAWONA_SKIP_NIX_PREBUILD=1`) can lack them. Then Machines Start logs
"Could not find weston executable" and `wwnValidateNestedWestonEnv` fails.

Heal: copy weston* / foot / libweston-13 / lib/weston / share/weston /
helpers from a store `wawona-macos` into the app that macos-matrix
launches. Do not replace the whole app during a live session.

Do not overlay a Debug `Contents/MacOS/Wawona` (absolute `/nix/store`
dylibs) onto a product `.app`. Store GC then fails dyld
(`libxkbcommon.0.dylib` not loaded) and agent-device `open` reports
No app found. Restore the store tree, then rewrite Debug links to
`@rpath` against that tree's `Contents/Frameworks`. Copy
`libwawona_relay.dylib` into Frameworks if Debug still needs it.
Raw `Resources/bin/weston` without `WESTON_MODULE_DIR` /
`WESTON_BACKEND_DIR` / `WESTON_DATA_DIR` still loads a GC'd
`libweston-13/wayland-backend.so`. Machines Start sets those.

agent-device macOS: open the display name `Wawona`, not the bundle id
and not a filesystem path. `--relaunch` with a path first `close`s
and fails APP_NOT_INSTALLED. Extra `*.app` copies with the same id
(`tmp-wawona-verify.app`) confuse Launch Services.
`WWNConfigureBundledWestonDataIfNeeded` must re-scan (not only
`dispatch_once`). Missing bin falls back to in-process
`weston_compositor_main --backend=wayland`.

Aqua niri is always `NIRI_BACKEND=nested` (no `niri_main` on macOS).
Iland DRM for niri is Classic insert only. Weston drm is in-process
`weston_compositor_main --backend=drm`. Never Classic Take Over to prove
Aqua. Never `export DYLD_INSERT_LIBRARIES` in the login shell.

## Wallpaper / pointer / Retina

Solid navy weston (`0xff1a1a2e`) is a missing `[shell] background-image`.
Honeycomb is `share/weston/background.png`. Do not treat navy as a
missing desktop-shell. Extra weston windows are extra NSTasks (proof
launches or a second Start).

Nested weston `wl_output` mode is **points**. Scale is
`backingScaleFactor`. Do not advertise physical pixels as the mode
(3360x2100 on 1680x1050 caused "Mode switch failed"). Scale 1 on a
Retina window is a 1x buffer stretched. `--scale=1` on the weston argv
stays (parent owns scale).

macOS must `CGAssociateMouseAndMouseCursorPosition(false)` while the
pointer is over nested weston/niri, and keep injecting seat motion.
Hide-only (empty cursor rect) with no grab looks like a stuck mouse
when weston's sprite is also missing.

Rule: `wawona-compositor-backend`, `wawona-nested-compositor-cursor`.
