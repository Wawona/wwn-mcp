# weston/niri: Aqua nested vs Classic iland DRM

Canonical: `Wawona/docs/agent-rules/wawona-compositor-backend.md`.
This is **not** Swinging Bridge and **not** Desktop Replacement itself.
The clients are bundled compositors.

## Detection

Classic / own-display: **Apple WindowServer is not running**.
`WWNHostSessionUsesOwnDisplayDRM()` (NSScreen, then `proc_name` WindowServer).
A censored process list is Aqua, not Classic. CLI: `pgrep -x WindowServer`.

Never treat these as Classic while Aqua is up:

- leaked `WWN_MODEB_TTY` / `NIRI_BACKEND=tty` / `WWN_MODEB_INSERT`
- `DesktopReplacementEnabled=1` without Take Over
- Settings Enable Desktop Replacement (Path B armed, WindowServer still up)

## Aqua (WindowServer up)

Honour Display Backend (`CompositorBackend` via `WWNResolveCompositorBackend`).
`auto` is nested `wayland`.

| Backend | weston | niri |
|---|---|---|
| `auto` / `wayland` | `--backend=wayland` on the Wawona socket | `NIRI_BACKEND=nested` |
| `drm` | in-process `--backend=drm` + iland Metal present | nested on Wawona (macOS has no in-process `niri_main`). niri DRM is Classic insert |

Strip Mode B leftovers from the Wawona process and nested `NSTask` env.

## Classic (WindowServer down)

No host Wayland for the **session** compositor:

- weston `--backend=drm`
- niri `NIRI_BACKEND=tty` and `WWN_MODEB_TTY=1`
- Prefix insert from `WWN_MODEB_INSERT` on that exec only, as the login user

Inner weston/niri (terminal, fuzzel, panel) are Wayland clients of its socket:
`--backend=wayland` / `NIRI_BACKEND=nested`. Keep `WAYLAND_DISPLAY`. Do not
set `WWN_MODEB_TTY`. Do not insert the dylib.

Nested compositors **draw their own cursor**. Hide and grab the host pointer.
See `wawona-nested-compositor-cursor`.

Apple mobile / Android in-process weston must not call
`cairo_debug_reset_static_data` on destroy (`wawona-inprocess-cairo`).
