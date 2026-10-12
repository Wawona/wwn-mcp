# Global Settings exclusivity

Exactly one Global Wawona Settings interface per platform target. That host is
**inside the Wawona app**. Never ship OS System Settings / PrefPane /
Settings.bundle / Settings-Watch.bundle / App Info Preferences as the catalog.

## Matrix

| Target | Sole host |
|---|---|
| macOS | In-app `WWNGlobalSettingsHostView` (gear / ⌘,) |
| iOS / iPadOS | In-app `WWNGlobalSettingsHostView` (gear; not Machines home sidebar) |
| watchOS | In-app `WatchGlobalSettingsView` |
| tvOS / visionOS | In-app `WWNGlobalSettingsHostView` |
| Android | Compose `SettingsDialog` |
| Linux | In-app libadwaita dialog |

iOS / tvOS / visionOS text and password rows push a Settings.app-style editor
page (Save / back). Not sheets. Not inline fields in the section list.

Storage: app container (`UserDefaults.standard` / SharedPreferences). No PrefPane
suite. No `group.com.wawona.global`.

## Schema

Rust `settings_catalog`, Swift `GlobalSettingsCatalog`, keys `wawona.pref.*`.
Reject Gemini toys (`wawona_sync_interval`, …).

## Not Global Settings

Machine editors. One-shot actions (Watch send, import, log copy).

## Hard rejects

- PrefPane / Settings.bundle / Settings-Watch.bundle as Global Settings
- Opening System Settings or Settings.app for the catalog
- Dual OS Settings inject and in-app catalog for the same keys

Rules: `wawona-global-settings-exclusive`. Docs: `Wawona/docs/settings.md`.
Verify: `Wawona/scripts/verify-settings-bundle-keys.py`.

## History

OS hosts landed in `8f2335a` (PrefPane + Settings.bundle) and later Watch /
Android App Info paths. Retired in favor of in-app-only Global Settings.
