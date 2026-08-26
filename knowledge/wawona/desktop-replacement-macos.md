# macOS Desktop Replacement: how it was built and how to use it

Public user docs: https://wawona.io/docs/desktop/ and
https://wawona.io/docs/macos/. Engineering:
`Wawona/docs/iland-mode-a-b-desktop.md`,
`Wawona/docs/desktop-replacement-classic-proof.md`.

This is **not** Wawona Swinging Bridge.

## What shipped

Classic Desktop Replacement **exists** on macOS desktop-host builds. For one
login session Wawona unloads Apple WindowServer (after IOWatchdog coverage)
and presents a native compositor or kmscube on iland userspace DRM/KMS/GBM.
Logout returns normal Aqua. LockScreen greeter handoff is still planned.
Android Home/LockScreen is still planned.

## Implementation (who owns what)

| Piece | Repo | Role |
|---|---|---|
| Mode A archive | `wwn-iland` | `libiland_userland.a`, in-window present |
| Mode B dylib | `wwn-iland` `iland-baremetal` | `libwayland-mac.dylib`, Mach → `framebufferd` |
| IOWatchdog Path B | `wwn-iowatchdog` | Sticky Disable ACK before unloading `watchdogd` |
| VTs / getty | `wwn-igetty` | `igettyd`, Doorman session, F1-F9 |
| SIP + Settings + Take Over | `Wawona` L4 | `WWNSipStatus`, `WWNDesktopReplacementController`, `WWNWaypipeRunner` |
| Session weston DRM | `wwn-weston` | `--backend=drm` over iland |
| Session niri DRM | `wwn-niri` | `NIRI_BACKEND=tty` after Classic |

Helper at `/Library/Application Support/Wawona/run-modeb.sh` is a **copy**.
A new nix store path does nothing for Take Over until
`nix run .#install` restages the helper.

## Friends: use Classic

Needs `.#wawona-macos-desktop-host`, SIP **fully disabled**, administrator
once for stage / Path B.

```text
1. Settings → Desktop → Enable Desktop Replacement
   (doctor + heal + Path B; Restart sheet; no screen takeover)
2. Reboot. Confirm claim-ok path=b sticky=1 and live Disable.
3. nix run .#install   # restages helper + dylib for this store
4. Choose Desktop machine: weston or niri
5. Settings or menubar → Replace now
6. Logout, or Ctrl+Option+Backspace, to return Aqua
```

CLI equivalents: `Wawona --mode-b-prepare`, `--mode-b-ready`, Replace now /
`--mode-b-engage`. KEEP_WS without unloading WS: `Wawona --mode-b-probe`.

Weston Desktop is the proof client (`NativeClientId=weston`, DRM). Demo
clients (`kmscube`, `weston-terminal`, `foot`) are not eligible as the
Desktop machine. F7 still overlays kmscube **inside** a Classic session.

## After Take Over

Type `weston` or `niri` in a text VT. Wrappers detect Classic because
**WindowServer is down**, not because `WWN_MODEB_TTY` leaked. They insert
the dylib on that exec and use iland DRM. Nested weston/niri **inside**
that session keep the parent `WAYLAND_DISPLAY` and stay Wayland clients.

Do not `sudo niri` / `sudo weston` (sudo strips insert; libc `open("/dev/dri")`
hits a missing real node).

## Status still planned

- LockScreen greeter
- Path C parked WindowServer (needed for Swinging Bridge + Desktop together)
- Android Default Home + LockScreen APIs
- iOS/iPadOS jailbreak tweak (`repo.wawona.io` only)

Capability gate `get_capability("macos", "desktop")` stays **planned** until
those land. Classic Take Over is still the implemented macOS path. Agents
must document how to use it, not claim it is absent.
