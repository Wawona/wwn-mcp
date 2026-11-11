# Appium catalog Wayland guests (Colima)

Authority: `Wawona/docs/testing/appium-ui-matrix.md`, skill `wawona-appium`,
rule `wawona-appium-ui-gh`. Launcher:
`cargo xtask appium launch`.

## Tip host app (hard)

Before any Darwin catalog capture:

```bash
eval "$(cargo xtask tip macos)"
```

Rebuilds when `git HEAD` drifts, quits leftovers, launches tip
`/tmp/wawona-macos-tip/…/Wawona.app`. Never `/Applications/Wawona.app`.
Rule: `wawona-test-tip-app`. `cargo xtask appium catalog` calls this first.

## Guest policy

| Host | Catalog guest | Notes |
|------|---------------|-------|
| Darwin / macOS | **Colima only** | `cargo xtask appium colima` + waypipe SSH. Fail closed if Colima down. |
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
  near-black/white (`xtask/src/appium/evidence.rs`).

## Present / Mac2

1. Host Wawona owns a **live** `$WAWONA_RUNTIME/wayland-0` (stale sock file
   is not enough).
2. Colima guest launches client via `cargo xtask appium waypipe`.
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
# Agent shells often lack brew; cargo xtask appium colima falls back to nixpkgs#colima.
colima start   # or: nix shell nixpkgs#colima nixpkgs#lima -c colima start
cargo xtask appium colima
# Wawona running with live wayland-0 (stale sock file is not enough):
cargo xtask appium catalog foot
cargo xtask appium gallery
```

`cargo xtask appium colima` prepends `~/.nix-profile` and, if needed, resolves
`nixpkgs#colima` / `nixpkgs#lima` so PATH-less agent shells still work when
Colima is already installed via nix.

## Runner stale Colima state

2026-10-25 Master Appium failure `40194195258`, macOS job `121171494304`:
Colima reported the VM was already running, but guest setup failed. The first
log showed that `cargo xtask appium colima` required a guessed key path
`$HOME/.colima/_lima/_config/user`; using the generated config removed that
assumption. The next run, `40206179352`, exposed the underlying stale VM state:
`colima ssh-config` failed because Lima's per-profile `ssh.config` was missing
at `$HOME/.colima/_lima/colima/ssh.config`.

Run `40207684901` exposed a deeper corruption case: both `ssh.config` and
`lima.yaml` were missing, so `colima stop --force` could not recover the
profile. Run `40212035327` showed that unique `COLIMA_HOME` and `LIMA_HOME`
alone were insufficient: Colima still selected profile `colima`, then could
not find `ssh.config` under the isolated Lima home. Set `COLIMA_PROFILE` to a
run-unique name as well as both homes. Run `40222465679` showed the run-scoped
profile had no Lima config, but the helper still called it active. Run
`40223150968` confirmed the recovery attempt failed because there was no
`lima.yaml` to stop. Root cause: `colima status` reports `is not running`, and
the helper's case-insensitive regex matched the `running` substring as a
positive state. Use the status command's exit code. On `40223741758` the fresh
profile then reached Colima startup, which failed because the hosted runner
lacked the Docker CLI required by Colima's default Docker runtime. CI installs
Colima, Lima, and Docker CLI together. Local runs keep their normal profile and
must not reset it automatically.

Fix: honor `COLIMA_HOME` and `COLIMA_SSH_CONFIG`, refresh the config from the
running profile with `colima ssh-config`, and connect through that file with
`ssh -F <config> <generated-host>`. On the disposable GitHub macOS runner only, set
Guest package checks, binary resolution, and waypipe's SSH transport use the
same generated profile config. Do not hardcode Colima's private identity file,
port, profile-specific host alias, or user. `cargo xtask appium colima`
reads the first concrete Host alias from the generated config. All SSH callers
use it; `COLIMA_SSH_HOST` is an explicit override. CI isolates the profile by
run; developer machines keep their normal Colima state.

Typed graph:

```text
Failure(40207684901/macOS/cargo xtask appium colima)
  --observed-at--> CI(Watch: Appium UI matrix)
  --caused-by--> Failure(missing Lima ssh.config and lima.yaml while stale Colima status says running)
  --first-misdiagnosed-as--> Assumption(fixed Colima identity path)
  --prevented--> Gate(catalog Wayland guest screenshots)
  --fixed-by--> Implementation(isolated Colima profile, exit-code status check, and Docker CLI install)
  --validated-by--> Gate(Watch: Appium UI matrix rerun)
```

Run `40357210740` then failed macOS catalog setup with
`Could not resolve hostname colima`. The run-scoped `COLIMA_PROFILE` generated
a profile-specific SSH alias, while `cargo xtask appium colima`, guest package checks,
binary resolution, and waypipe still addressed the default `colima` alias.

```text
Failure(40357210740/macOS/Colima SSH probe)
  --observed-at--> CI(Watch: Appium UI matrix)
  --caused-by--> Implementation(hardcoded default SSH alias with run-scoped profile)
  --prevented--> Gate(catalog Wayland guest screenshots)
  --fixed-by--> Implementation(resolve generated Host alias from COLIMA_SSH_CONFIG)
  --validated-by--> Gate(pending exact-head Appium matrix rerun)
```

The same matrix run's visionOS job also failed during `xcodebuild
-downloadPlatform visionOS` with `Unable to connect to simulator`. That job
only runs the Appium dry unit gate and does not use a visionOS runtime. Remove
the unrelated SDK download from this dry lane; visionOS simulator product
builds remain covered by Gate: products.

## Nested macOS runner VM backend

Run `40224056963` passed the Colima status check, installed Colima/Lima/Docker,
and reached VM launch, but VZ failed in the hosted macOS 26 ARM64 runner. That
runner is itself a VM and does not expose nested Hypervisor.framework support.
Colima maintainers document that GitHub macOS ARM runners cannot run a nested
Colima VM through VZ. Select QEMU for CI only. Lima's QEMU driver appends TCG
after HVF on macOS, so it can boot by software emulation when nested HVF is not
available. Install QEMU in the runner and pass `--vm-type qemu` from
`cargo xtask appium colima` through the CI-only `WAWONA_COLIMA_VM_TYPE` setting. Keep
local Colima defaults unchanged. Source: Colima issue #1427 and Lima PR #5137.

```text
Failure(40224056963/macOS/Colima VZ startup)
  --observed-at--> CI(Watch: Appium UI matrix)
  --caused-by--> Environment(GitHub macOS runner is an ARM64 VM without nested HVF)
  --first-misdiagnosed-as--> Assumption(Docker CLI or stale Colima profile)
  --prevented--> Gate(catalog Wayland guest screenshots)
  --fixed-by--> Implementation(CI-only Colima QEMU backend with HVF-to-TCG fallback)
  --validated-by--> Gate(pending Appium matrix rerun)
```
