# Apple sidebar icons (tinted SF Symbols)

Durable gate for Machines and Global Settings sidebars on Apple SwiftUI.

## Rule

- Sidebars: **section-tinted SF Symbols** (`WawonaSettingsHubChrome.sidebarIcon`
  / `hubRow` with `iconColor`). Glyph color = section accent. No colored
  rounded-square tile, no white glyph on colored fill.
- Settings **detail**: same section accent tints Toggle / Picker / Button /
  Link / section headers (`.settingsSectionAccent` + `.backport.tint`; watch
  uses `.accentColor`).
- Accent palette: `WawonaSettingsHubChrome.accentColor(for:)` and section
  `swiftUIIconColor`. Tint glyphs and detail controls; never paint that color
  onto sidebar icon backgrounds.
- Settings split chrome matches Machines: system `NavigationSplitView`
  sidebar toggle (do not strip / do not add a second custom `sidebar.left`).
  Detail trailing: `settingsCloseAction(onClose:chromeBridge:)` (`[+][x]`).
  Pass `showSidebar:` only on pre-16 HStack (no system toggle there).

## Hard rejects

- Settings.app General-style colored hub tiles in Wawona Machines or Settings
  sidebars
- Section accent as sidebar icon chrome (background fill)
- Monochrome / `.primary`-only sidebar glyphs that drop section colors

## Paths

- `Wawona/Sources/WawonaUIContracts/WawonaSettingsHubChrome.swift`
- `Wawona/Sources/WawonaUI/Settings/WWNGlobalSettingsHostView.swift`
- `Wawona/Sources/WawonaUI/WawonaMainWindowView.swift`
- `Wawona/Sources/WawonaUI/Settings/WWNSettingsSectionView.swift`
- `Wawona/Sources/WawonaUI/Compatibility/WawonaPresentation.swift`

Skill / rule: `wawona-apple-sidebar-icons`. Related:
`global-settings-exclusive.md`, `unified-settings-sidebar.md`.
