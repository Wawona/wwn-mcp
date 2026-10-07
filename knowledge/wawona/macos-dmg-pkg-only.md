# macOS GitHub Release DMG is pkg-only

Hard packaging rule (Ship: GitHub assets / `release.yml`).

## Volume contents

| On DMG | Not on DMG |
|---|---|
| `WawonaAgent.pkg` | Loose `Wawona.app` |
| `README.txt` (thank-you + install steps) | `/Applications` symlink |

## Why

Drag-install of a loose `.app` skips LaunchAgents, System Settings → Wawona
(`Wawona.prefPane`), Desktop Replacement helper sync, and
`WAYLAND_DISPLAY` / `XDG_RUNTIME_DIR` publish. The pkg is the only supported
path so those pieces stay in sync.

## Build layout

- `sign-staging/Wawona.app`: Developer ID sign + pkg payload source
- `dmg-staging/`: volume root (`WawonaAgent.pkg` + `README.txt`)
- Scripts: `scripts/macos-launch-agent-pkg.sh`,
  `scripts/macos-sign-and-notarize-dmg.sh`

## Hard rejects

- Shipping `Wawona.app` or an Applications symlink on the Release DMG
- Documenting "Option A: drag to Applications" as a release install path
- Defaulting DMG `--staging` to the directory that holds `--app` (would
  delete the sealed app when cleaning the volume)

Canonical: `Wawona/docs/ci.md`, `docs/agent-rules/wawona-release-assets.md`,
Cursor rule `wawona-release-assets`.
