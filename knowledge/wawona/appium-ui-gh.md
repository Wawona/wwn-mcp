# Appium UI on GitHub runners (Wawona Mode A)

Authority: `Wawona/docs/agent-rules/wawona-appium-ui-gh.md`,
`Wawona/docs/testing/appium-ui-matrix.md`, skill `wawona-appium`.

## Stack

Mode A product UI on **GitHub-hosted runners** is **Appium 2**
(`Watch: Appium UI matrix` / `ui-appium.yml`). Drivers: XCUITest, UiAutomator2,
Mac2. Selectors: `wwn.*` only (`Tests/appium/selectors.json`).

**agent-device** is local dogfood and **vphone Mode B** only. Never replace
Appium Gate/Watch jobs with agent-device, osascript, or host screencapture.

## Catalog Wayland green

Catalog green is a **machine Present PNG** in
`.agent-device/test-artifacts/appium/catalog-gallery/<client>.png` (non-blank).
DRY packaging cards are not proof.

| Host | Guest |
|------|-------|
| Darwin | **Colima + waypipe only** (`ensure-colima.sh`) |
| Linux CI | nested (`WAWONA_WAYLAND_GUEST=nested`) |

See `appium-catalog-colima.md` for false-green lessons (Terminal vs Present,
dark blank gate, no local-bundle).

## Runner failure loop

1. Load skill `appium` + `appium-troubleshooting` (+ driver child).
2. Reproduce same driver / runner class.
3. Fix suite, selectors, caps, guest launcher, or product a11y.
4. Re-run until green evidence. No skip stubs / `|| true`.

## CI artifact upload

CI writes under `test-artifacts/appium/` via
`scripts/appium/ci-prepare-artifacts.sh` (non-hidden). Local dogfood stays
`.agent-device/test-artifacts/appium`. `upload-artifact` v4+ drops hidden
`.agent-device/` by default. Gallery artifacts upload only when `*.png`
exists. Without a staged host app, CI writes `SKIPPED.txt` (not a catalog
claim). Pass `products_ready` after Gate products for real PNGs.

## Hard rejects

- agent-device / osascript / host screencapture to greenwash runner UI
- Accessibility ids outside `wwn.*`
- Catalog packaging-card skips instead of Wayland guests
- Claim catalog client OK without Present surface screenshot
- Cancel tip `ui-appium` / Gate UI jobs (`wawona-ci-no-cancel`)
- Darwin catalog via local-bundle / Apple Containerization
- Appium CI artifacts under `.agent-device/` (use ci-prepare-artifacts.sh)
