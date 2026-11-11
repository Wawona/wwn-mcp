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

## Cross-workflow product artifact source

- Event: Appium run `40295903502` failed Android Appium at
  `Download product-android-apk`, Linux Appium at `Download product AppImage`
  and its required gallery upload, and macOS Appium at
  `Download product-macos-app` and its required gallery upload.
- Cause: manual `workflow_dispatch` set `products_ready=true`, but
  `actions/download-artifact` defaulted to the current Appium run, which did
  not own the Gate: products artifacts.
- Fixed by: require a `products_run_id`, validate that it is a successful
  `Gate: products` run for the same commit, then pass its run ID, repository,
  and `github.token` to every cross-run artifact download.
- Regression condition: setting `products_ready=true` without the successful
  source run ID must fail early. Never treat missing product artifacts or a
  missing gallery as UI success.
- Provenance: Gate: products run `40284441344` passed on commit
  `bebdeca5`; Appium run `40295903502` used that same commit but attempted to
  download from its own run ID.

| Host | Guest |
|------|-------|
| Darwin | **Colima + waypipe only** (`cargo xtask appium colima`) |
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
`cargo xtask appium prepare` (non-hidden). Catalog green is PNG
only. macOS tip+Colima smoke fail-closed (never `exit 0` + `SKIPPED.txt`;
that false-greened tip `a58384fc`). Linux catalog only when
`products_ready`. Gallery upload `if-no-files-found: error` after catalog.


## Hard rejects

- agent-device / osascript / host screencapture to greenwash runner UI
- Accessibility ids outside `wwn.*`
- Catalog packaging-card skips instead of Wayland guests
- Claim catalog client OK without Present surface screenshot
- Cancel tip `ui-appium` / Gate UI jobs (`wawona-ci-no-cancel`)
- Darwin catalog via local-bundle / Apple Containerization
- Appium CI artifacts under `.agent-device/` (use cargo xtask appium prepare)
