# Unified Settings sidebar (Apple + Android + GTK)

Indexed summary. Chrome is SwiftUI / Compose / GTK. Inventory rows still
come from ObjC `WWNPreferences.buildSections` until that inventory lifts
section by section. Do not grow new ObjC rows.

## What shipped

- Live Apple shell lives in `Sources/WawonaUI` (`WawonaMainWindowView`,
  `WWNSettingsSectionView`). iOS / iPadOS / tvOS / visionOS host
  `WawonaRootView` (welcome, then the split). macOS unified window hosts
  the same `WawonaMainWindowView`. Watch stays compact
  (`WatchGlobalSettingsView` / `WawonaWearCompactRootView`). Never
  `NavigationSplitView` on Watch.
- Sidebar destinations are rust `settings_catalog` slugs
  (`display`, `input`, …) via `wawona_settings_visible_sections`.
  Swift `GlobalSettingsCatalog` maps slug to Label + SF Symbol only.
- UIKit `WWNSettingsSidebarViewController` / split is not compiled on
  Apple mobile. AppKit Preferences window is a stale-build fallback;
  gear / menu route to `WWNUnifiedWindowController`.
- macOS, iOS, iPadOS, tvOS, visionOS host `WawonaMainWindowView`
  (Machines + Settings). Apple `NavigationSplitView` +
  `List(selection:)` + `NavigationLink(value:)` + `.listStyle(.sidebar)`
  (TN3154). Do not use Button rows. Do not use a back-arrow stack
  that treats the sidebar as another main view.
- iPhone uses the same sidebar column and toggle as iPad and macOS.
  Always inject `.environment(\.horizontalSizeClass, .regular)` so
  Apple never collapses the split into a `NavigationStack`.
  Portrait starts `columnVisibility = .detailOnly` plus
  `.prominentDetail` (sidebar overlay). Landscape and iPad use
  `.balanced` and `.all`. The leading control is Apple's
  Show Sidebar / Hide Sidebar on the split, never a back chevron
  to a sidebar page. Do not add a second custom toggle.
- watchOS stays `WatchGlobalSettingsView` + `GlobalSettingsCatalog`.
  Do not force `NavigationSplitView` on Watch.
- Android Compose and Linux GTK use the same section order as Rust
  `domain::settings_catalog::visible_sections`. Linux extras (Launch Agent,
  Diagnostics) stay after About / Dependencies. Android Desktop is a
  planned extra at the end.
- iOS Settings → Desktop is **Mode B only** (`profile-ios-mode-b` /
  `WWN_MODE_B`). TrollStore `.tipa` and Sileo jailbreak show it. Store
  IPA must not. Rows stay in ObjC `WWNPreferences` under that ifdef
  (Enable + Replace now + machine picker). Engage is wwn-iland IOMFB
  plus wwn-igetty. Do not flip MCP `get_capability("ios", "desktop")`
  off forbidden: that gate is the App Store row.

## Rust owns the section list

`SettingsHost` / `SettingsSectionId` / `visible_sections` live in
`src/domain/mod.rs` (`settings_catalog` module). UniFFI export:
`settings_visible_sections`. C trampoline:
`wawona_settings_visible_sections`. Swift `GlobalSettingsCatalog` is a
frozen field-visibility mirror. Do not grow section order only in Swift
or Kotlin.

Nix `git+file` copies tracked files only. A brand-new `.rs` file is
invisible until it is in HEAD. Keep new domain modules inside an
already-tracked file until commit.

## Hard rejects

- UniFFI callbacks on `WWNCore*` (compositor ABI stays C + ObjC/JNI poll)
- Claiming ObjC is gone. Scene, compositor view, IME, Mode B constructors stay
- New feature SwiftUI under `src/platform/macos/ui/*` (this shell was
  already there; do not add a third Settings UI)
- Desktop / jailbreak / Swinging Bridge copy in store IPA
