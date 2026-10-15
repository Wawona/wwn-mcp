# Apple sidebar icons (plain SF Symbols)

Durable gate for Machines and Global Settings sidebars on Apple SwiftUI.

## Rule

- Sidebars: **plain SF Symbols** only (`WawonaSettingsHubChrome.sidebarIcon` /
  `hubRow`). System style. No colored rounded-square tile, no white glyph on
  colored fill.
- Settings **detail** only: section accent tints Toggle / Picker / Button /
  Link / section headers (`.settingsSectionAccent` + `.backport.tint`; watch
  uses `.accentColor`).
- Accent palette still lives in `WawonaSettingsHubChrome.accentColor(for:)`
  and section `swiftUIIconColor`. Never paint that color onto sidebar icon
  backgrounds.

## Hard rejects

- Settings.app General-style colored hub tiles in Wawona Machines or Settings
  sidebars
- Section accent as sidebar icon chrome

## Paths

- `Wawona/Sources/WawonaUIContracts/WawonaSettingsHubChrome.swift`
- `Wawona/Sources/WawonaUI/Settings/WWNGlobalSettingsHostView.swift`
- `Wawona/Sources/WawonaUI/WawonaMainWindowView.swift`
- `Wawona/Sources/WawonaUI/Settings/WWNSettingsSectionView.swift`

Skill / rule: `wawona-apple-sidebar-icons`. Related:
`global-settings-exclusive.md`, `unified-settings-sidebar.md`.
