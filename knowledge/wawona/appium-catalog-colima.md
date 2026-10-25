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

## Runner stale Colima state

2026-10-25 Master Appium failure `40194195258`, macOS job `121171494304`:
Colima reported the VM was already running, but guest setup failed. The first
log showed that `ensure-colima.sh` required a guessed key path
`$HOME/.colima/_lima/_config/user`; using the generated config removed that
assumption. The next run, `40206179352`, exposed the underlying stale VM state:
`colima ssh-config` failed because Lima's per-profile `ssh.config` was missing
at `$HOME/.colima/_lima/colima/ssh.config`.

Run `40207684901` exposed a deeper corruption case: both `ssh.config` and
`lima.yaml` were missing, so `colima stop --force` could not recover the
profile. The macOS CI step now creates unique `COLIMA_HOME` and `LIMA_HOME`
directories under `runner.temp` before starting Colima. This prevents reuse of
stale prestarted runner metadata. Local runs keep their normal profile and must
not reset it automatically.

Fix: honor `COLIMA_HOME` and `COLIMA_SSH_CONFIG`, refresh the config from the
running profile with `colima ssh-config`, and connect through that file with
`ssh -F <config> colima`. On the disposable GitHub macOS runner only, set
Guest package checks, binary resolution, and waypipe's SSH transport use the
same generated profile config. Do not hardcode Colima's private identity file,
port, host, or user. CI isolates the profile by run; developer machines keep
their normal Colima state.

Typed graph:

```text
Failure(40207684901/macOS/ensure-colima.sh)
  --observed-at--> CI(Watch: Appium UI matrix)
  --caused-by--> Failure(missing Lima ssh.config and lima.yaml while stale Colima status says running)
  --first-misdiagnosed-as--> Assumption(fixed Colima identity path)
  --prevented--> Gate(catalog Wayland guest screenshots)
  --fixed-by--> Implementation(isolated COLIMA_HOME and LIMA_HOME per CI run)
  --validated-by--> Gate(Watch: Appium UI matrix rerun)
```
