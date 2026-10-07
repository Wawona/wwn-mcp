# Unified Settings sidebar (Apple + Android + GTK)

Indexed summary. Chrome is SwiftUI / Compose / GTK. Inventory rows still
come from ObjC `WWNPreferences` / `WWNPreferencesSectionsBuilder` until that
inventory lifts section by section. Do not grow new ObjC rows.

**Global Settings exclusivity** (see `global-settings-exclusive.md`): exactly
one Global Settings host per platform. Prefer OS when product-usable.

## What shipped

- Live Apple shell lives in `Sources/WawonaUI` (`WawonaMainWindowView`,
  `WWNSettingsSectionView`). iOS / iPadOS / tvOS / visionOS host
  `WawonaRootView` (welcome, then the split). macOS unified window hosts
  the same `WawonaMainWindowView`. Watch stays compact
  (`WawonaWearCompactRootView`). Never `NavigationSplitView` on Watch.
- In-app sidebar Settings keep only **Desktop**, **About**,
  **Dependencies** (`GlobalSettingsCatalog.appSidebarSections`). These are
  **not** Global Settings.
- **macOS Global Settings:** System Settings PrefPane only
  (`WawonaPrefPaneRootView`, suite `com.aspauldingcode.Wawona`). No in-app
  Global Settings panel. ⌘, and menubar open PrefPane only.
- **iOS / iPadOS Global Settings:** Settings.bundle only. Toolbar Settings
  opens Settings.app (`UIApplication.openSettingsURLString`). No in-app
  Global Settings sheet.
- **tvOS / visionOS Global Settings:** in-app `WawonaGlobalSettingsPanelView`
  only (no Settings.bundle / PrefPane).
- **watchOS Global Settings:** `Settings-Watch.bundle` in the Watch app,
  edited from the iPhone Watch app. On-wrist UI is a redirect only
  (`WatchGlobalSettingsView`), not a catalog.
- PrefPane width: `NSPrefPaneSupportsAutoLayout`. In-pane Back owns
  `NavigationPath`. Full catalog via `systemSettingsPaneSections`.
- Android Compose `SettingsDialog` is the sole Global Settings host for
  Play/sideload. `APPLICATION_PREFERENCES` opens that same dialog.
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
- UniFFI callbacks on `WWNCore*` (compositor ABI stays C + ObjC/JNI poll)
- Claiming ObjC is gone. Scene, compositor view, IME, Mode B constructors stay
- New feature SwiftUI under `src/platform/macos/ui/*`
