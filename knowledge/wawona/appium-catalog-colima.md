# Appium catalog Wayland guests (Colima)

Authority: `Wawona/docs/testing/appium-ui-matrix.md`, skill `wawona-appium`,
rule `wawona-appium-ui-gh`. Launcher:
`Wawona/scripts/appium/launch-wayland-client.sh`.

## Tip host app (hard)

Before any Darwin catalog capture:

```bash
eval "$(scripts/appium/ensure-tip-wawona-macos.sh)"
```

Rebuilds when `git HEAD` drifts, quits leftovers, launches tip
`/tmp/wawona-macos-tip/…/Wawona.app`. Never `/Applications/Wawona.app`.
Rule: `wawona-test-tip-app`. `capture-catalog-gallery.sh` calls this first.

## Guest policy

| Host | Catalog guest | Notes |
|------|---------------|-------|
| Darwin / macOS | **Colima only** | `ensure-colima.sh` + waypipe SSH. Fail closed if Colima down. |
| Linux CI | `nested` | Same-host `WAYLAND_DISPLAY`. Set `WAWONA_WAYLAND_GUEST=nested`. |

`matrix.toml` catalog rows use `guest = "colima"`. Do not set `container` or
local-bundle for catalog proof.

## Hard rejects (learned)

- Launch host `Wawona.app/Contents/Resources/bin/*` and call it catalog green
  (local-bundle). That path is removed from the launcher.
- Apple Containerization / `Wawona run` as the Appium catalog guest.
- Gallery PNG of Machines UI, Global Settings, or the full desktop.
- Publish `weston-simple-shm` concentric circles as `weston_terminal.png`.
- Treat Start alone as Present. Start opens **Wawona Terminal**; close it or
  Focus so `wwn.compositor.surface` appears.
- Blank-reject dark terminals on mean luminance alone. Blank means flat AND
  near-black/white (`screenshot_evidence._center_region_is_blank`).

## Present / Mac2

1. Host Wawona owns a **live** `$WAWONA_RUNTIME/wayland-0` (stale sock file
   is not enough).
2. Colima guest launches client via `waypipe-ssh-colima-lab.sh`.
3. Close Wawona Terminal / Focus so Present exposes `wwn.compositor.surface`.
4. `CompositorPage.screenshot_surface` → `require_client_screenshot` →
   `catalog-gallery/<client>.png`.

Mac2 needs TCC: Accessibility for `WebDriverAgentRunner-Runner`. Without
it WDA reports `Not authorized for performing UI testing actions` and
cannot see `wwn.machines.root`. Keep `WAWONA_MAC2_MANAGE_APP=1` so
bundleId is set (`MANAGE_APP=0` is desktop-wide AX only).

## Nested weston on host (debug only)

Stale nix `wayland-backend.so` aborts:
`weston_log_set_handler() must be called before using of weston_log()`.
Host debug needs `WESTON_BACKEND_DIR` on the app `lib/libweston-13`. Catalog
must use Colima weston instead.

## Commands

```bash
# Agent shells often lack brew; ensure-colima.sh falls back to nixpkgs#colima.
colima start   # or: nix shell nixpkgs#colima nixpkgs#lima -c colima start
./scripts/appium/ensure-colima.sh
# Wawona running with live wayland-0 (stale sock file is not enough):
./scripts/appium/capture-catalog-gallery.sh foot
python3 scripts/appium/verify-catalog-gallery.py
```

`ensure-colima.sh` prepends `~/.nix-profile` and, if needed, resolves
`nixpkgs#colima` / `nixpkgs#lima` so PATH-less agent shells still work when
Colima is already installed via nix.