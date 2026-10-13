# Appium UI on GitHub runners

Mode A product UI on GitHub-hosted runners uses **Appium 2**
(`Watch: Appium UI matrix`, `ui-appium.yml`). Agents must load the dendritic
`appium` skill pack and Wawona skill `wawona-appium`. Rule:
`wawona-appium-ui-gh` (alwaysApply).

## Failure loop

If a runner UI / Appium / GUI job is red: load `appium` +
`appium-troubleshooting` + the platform driver child, reproduce, fix via the
Appium suite / `wwn.*` selectors / Wayland guest launcher, re-run with
evidence. Do not greenwash with skip stubs, agent-device, osascript, or host
screencapture.

## Split

- **Appium:** Mode A product UI on GH runners (`Tests/appium/`).
- **agent-device:** local dogfood and vphone Mode B only.

## Paths

`Tests/appium/`, `scripts/appium/launch-wayland-client.sh`,
`docs/testing/appium-ui-matrix.md`, `/etc/nix-darwin/.dotfiles/docs/appium-agents.md`.
