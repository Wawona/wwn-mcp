# iland Mode A / Mode B and Desktop Replacement (agent knowledge)

Indexed summary for WWN-MCP. Full docs:

- `Wawona/docs/iland-mode-a-b-desktop.md`
- `Wawona/docs/desktop-replacement-classic-proof.md`
- `Wawona/docs/mode-b-windowserver-options.md`
- Public: https://wawona.io/docs/desktop/
- Cursor rules: `wawona-iland-mode-b-desktop`, `wawona-macos-mode-a`,
  `wawona-mode-b-watchdog-safety`, `wawona-compositor-backend`

**Wawona Swinging Bridge is a different product.** Do not call it Desktop or
LockScreen. See `Wawona/docs/swinging-bridge.md`.

## Product vs implementation

Product gates stay **planned** on macOS and Android until LockScreen / greeter
Phase E. App Store Apple-mobile Desktop stays **forbidden**.

**macOS Classic Take Over is implemented.** Own-display is proven (kmscube;
weston `--backend=drm` / niri `NIRI_BACKEND=tty` after Classic). KEEP_WS probe
is implemented. Path C (parked WindowServer) is **planned**. Android Home +
LockScreen APIs are still planned.

## Facts agents get wrong

- **Wrong:** Wawona always injects `libwayland-mac.dylib` / always needs SIP off.
- **Right:** Default is **Mode A** (`libiland_userland.a`, in-window present).
  Mode B dylib is optional, **macOS desktop-host only**.
- **Wrong:** Partial SIP (`csrutil enable --without debug`) is enough.
- **Right:** Mode B needs SIP **fully disabled**. First line of `csrutil status`
  must be `System Integrity Protection status: disabled`. Settings shows
  **Fully Disabled**. Partial SIP is refused.
- **Wrong:** Enable Desktop Replacement takes over the screen.
- **Right:** Enable arms Path B (doctor, heal, claim-install). **Replace now**
  (Settings or menubar) is the only activate step.
- **Wrong:** `nix run .#install` does not sync the Mode B helper.
- **Right:** `nix run .#install` always syncs helper + dylib. Opening
  desktop-host Wawona also syncs when the helper is stale.
- **Wrong:** Mode B is kernel DRM / a kernel module.
- **Right:** Userspace only. Virtual `/dev/dri` terminates in iland.
  `framebufferd` presents over Mach IPC.

## Mode A (always required on macOS)

- Artifact: `libiland_userland.a`.
- Present: `iland_drm_set_present_callback` → `WWNIlandPresenter` / CAMetalLayer.
- SIP may stay **enabled**. In-window nested compositors and clients still work.
- Default `.#wawona-macos` (and store-shaped macOS): **no** Mode B dylib.
- Building or testing Mode B must never break Mode A.

## Mode B (macOS desktop-host)

- Artifact: `libwayland-mac.dylib` from `wwn-iland` `iland-baremetal` /
  `macos-baremetal.nix` (CMake + Dobby; CoreBedtime load model).
- Ships only in `.#wawona-macos-desktop-host` at
  `Contents/Library/Wawona/iland/libwayland-mac.dylib`.
- Watchdog tools: flake input `wwn-iowatchdog` (L3′). VT / getty: `wwn-igetty`.
- Engage: SIP fully disabled **and** `DesktopReplacementEnabled` **and**
  Replace now → `WWNDesktopReplacementController`.
- Prefix `DYLD_INSERT_LIBRARIES` on the **session compositor exec only**.
  Never `export` it in the login shell (Apple `/bin/*` is `arm64e`).

## WindowServer options (not IOWatchdog Path A/B)

| Option | WindowServer | Status |
|---|---|---|
| Classic | Unloaded; Mode B owns the panel | Implemented (kmscube proof) |
| KEEP_WS | Left up; Aqua stays | Implemented (`Wawona --mode-b-probe`) |
| Path C | Parked/suspended; Cocoa still has WS for Swinging Bridge | Planned after multi-TTY |

## How to use Classic (friends path)

1. Install `.#wawona-macos-desktop-host`. SIP fully disabled (`csrutil disable`
   in Recovery).
2. Settings → Desktop → **Enable Desktop Replacement**. That runs doctor, heal,
   Path B (`claim-install --path-b`), and syncs helper + dylib for this build,
   then the native Restart sheet. It does **not** Take Over.
3. After reboot, confirm `/var/db/wwn-iowatchdog/claim-ok` (`path=b sticky=1`)
   **and** live Disable (marker or Path B sock `done=1`). `claim-ok` alone is
   stale.
4. Pick a Desktop machine (weston or niri; not `weston-terminal` / foot).
5. **Replace now**. Classic unloads WindowServer only after IOWatchdog Disable
   ACK (`WWN_MODEB_WD=iowatchdog-then-unload`).
6. Logout returns Aqua. Next login does not auto-engage. Ctrl+Option+Backspace
   restores Aqua (Fn+Ctrl+Option+Backspace on MacBook).

CLI: `Wawona --mode-b-prepare` (same as Enable), `--mode-b-ready`,
`--mode-b-engage` / Replace now, `--mode-b-probe` (KEEP_WS).

## Classic session (after Take Over)

`wwn-igetty` owns VTs. Desktop machine gets `DesktopReplacementGuiVt` (default
1). Ctrl+Option+F1-F6 switches. F7-F9 overlay kmscube, gbm-es2-demo,
vkcube-kms. Session compositor uses **iland DRM**:

- weston `--backend=drm`
- niri `NIRI_BACKEND=tty` and `WWN_MODEB_TTY=1`

Inner weston/niri started **inside** that session stay nested Wayland clients.
Do not nest the **session** compositor on Wawona (there is no host Wayland).

While Aqua is up, honour Display Backend: `auto`/`wayland` is nested;
`drm` is in-window iland for weston. Leaked `WWN_MODEB_TTY` in Aqua is a bug.

## Hard forbids (macOS 26)

Never Take Over / unload `watchdogd` without sticky Path B ACK. Never attach
lldb to `watchdogd` or WindowServer. Never `kickstart -k` watchdogd. Never
`export DYLD_INSERT_LIBRARIES`. Stage must never `wwn-iowatchdog disable`.
See [`mode-b-watchdog-safety.md`](mode-b-watchdog-safety.md).

## Android / iOS

Android Desktop: Default Home + LockScreen APIs. **No root.** Not the macOS
dylib. Still planned.

iOS / iPadOS Desktop: jailbreak tweak from `repo.wawona.io` only. **Forbidden**
in App Store IPA. Never mention jailbreak in store binaries.

## Verify

`Wawona/.github/scripts/verify-iland-mode-b-bundle.sh --mode present|absent <root>`

How-to: [`desktop-replacement-macos.md`](desktop-replacement-macos.md).
Watchdog: [`mode-b-watchdog-safety.md`](mode-b-watchdog-safety.md).
Aqua vs Classic backends: [`compositor-backend-aqua-classic.md`](compositor-backend-aqua-classic.md).
Graphics: [`wwn-iland-graphics-stack.md`](wwn-iland-graphics-stack.md).
Target scope: [`platform-capability-matrix.md`](platform-capability-matrix.md).
