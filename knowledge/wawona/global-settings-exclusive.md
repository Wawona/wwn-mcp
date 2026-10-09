# Global Settings exclusivity

Exactly one Global Wawona Settings interface per platform target. That host is
**inside the Wawona app**. Never ship OS System Settings / PrefPane /
Settings.bundle / Settings-Watch.bundle / App Info Preferences as the catalog.

## Matrix

| Target | Sole host |
|---|---|
| macOS | In-app Machines sidebar (`WWNSettingsSectionView`) |
| iOS / iPadOS | In-app Machines sidebar |
| watchOS | In-app `WatchGlobalSettingsView` |
| tvOS / visionOS | In-app Machines sidebar |
| Android | Compose `SettingsDialog` |
| Linux | In-app libadwaita dialog |

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
