# Appium catalog Wayland guests (Colima)

Authority: `Wawona/docs/testing/appium-ui-matrix.md`, skill `wawona-appium`,
rule `wawona-appium-ui-gh`. Launcher:
`Wawona/scripts/appium/launch-wayland-client.sh`.

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

1. Host Wawona owns `$WAWONA_RUNTIME/wayland-0`.
2. Colima guest launches client via `waypipe-ssh-colima-lab.sh`.
3. Close Wawona Terminal / Focus so Present exposes `wwn.compositor.surface`.
4. `CompositorPage.screenshot_surface` → `require_client_screenshot` →
   `catalog-gallery/<client>.png`.

## Nested weston on host (debug only)

Stale nix `wayland-backend.so` aborts:
`weston_log_set_handler() must be called before using of weston_log()`.
Host debug needs `WESTON_BACKEND_DIR` on the app `lib/libweston-13`. Catalog
must use Colima weston instead.

## Commands

```bash
colima start
./scripts/appium/ensure-colima.sh
# Wawona running with wayland-0:
./scripts/appium/capture-catalog-gallery.sh foot
python3 scripts/appium/verify-catalog-gallery.py
```
