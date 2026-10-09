# Unified Settings sidebar (Apple + Android + GTK)

Indexed summary. Chrome is SwiftUI / Compose / GTK. Inventory rows still
come from ObjC `WWNPreferences` / `WWNPreferencesSectionsBuilder` until that
inventory lifts section by section. Do not grow new ObjC rows.

**Global Settings exclusivity** (see `global-settings-exclusive.md`): exactly
one Global Settings host per platform. That host is **in-app**.

## What shipped

- Live Apple shell lives in `Sources/WawonaUI` (`WawonaMainWindowView`,
  `WWNSettingsSectionView`). iOS / iPadOS / tvOS / visionOS host
  `WawonaRootView` (welcome, then the split). macOS unified window hosts
  the same `WawonaMainWindowView`. Watch stays compact; Global Settings are
  `WatchGlobalSettingsView` on the wrist.
- **Global Settings (all Apple targets except Watch):** Machines sidebar
  full catalog (`GlobalSettingsCatalog.visibleSections`). Toolbar / `⌘,` /
  menubar open that sidebar. Never System Settings or Settings.app.
- **watchOS Global Settings:** in-app `WatchGlobalSettingsView`. Same
  `wawona.pref.*` keys in the watch container.
- **Android:** Compose `SettingsDialog` only. No `APPLICATION_PREFERENCES`.
- **Linux:** in-app libadwaita settings dialog.
- PrefPane / Settings.bundle / Settings-Watch.bundle are **retired**. Install
  removes stale PreferencePanes copies.
- iOS Settings → Desktop sidebar is **Mode B only** (`WWN_MODE_B`). Store
  IPA must not. Engage is wwn-iland IOMFB plus wwn-igetty.

## Rust owns the section list

`SettingsHost` / `SettingsSectionId` / `visible_sections` live in
`src/domain/mod.rs` (`settings_catalog` module). UniFFI export:
`settings_visible_sections`. C trampoline:
`wawona_settings_visible_sections`. Swift `GlobalSettingsCatalog` is a
frozen field-visibility mirror. Do not grow section order only in Swift
or Kotlin.

## Hard rejects

- Dual Global Settings hosts (OS + in-app) on the same target
- Rebuilding PrefPane / Settings.bundle / Settings-Watch.bundle
- UniFFI callbacks on `WWNCore*` (compositor ABI stays C + Swift/JNI poll)
- Claiming ObjC is gone. Scene, compositor view, IME, Mode B constructors stay
- New feature SwiftUI under `src/platform/macos/ui/*`
