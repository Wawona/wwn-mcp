# Global Settings exclusivity

Exactly one Global Wawona Settings interface per platform target. Prefer OS
System Settings when product-usable. Never ship OS integration and an in-app
Global Settings hub for the same catalog.

## Matrix

| Target | Sole host |
|---|---|
| macOS | PrefPane `com.aspauldingcode.Wawona.prefPane` (suite `com.aspauldingcode.Wawona`) |
| iOS / iPadOS | Settings.bundle |
| watchOS prefs | Settings-Watch.bundle on iPhone Watch app |
| tvOS / visionOS | In-app `WawonaGlobalSettingsPanelView` only |
| Android Play / sideload | Compose `SettingsDialog` + `APPLICATION_PREFERENCES` |
| Android when OS inject product-usable | System Settings only; remove Compose hub |

Product-usable means the user can edit Wawona globals in OS Settings for that
artifact. Android 16 `SettingsPreferenceService` discovery is system-app-only;
Play must not claim dual hosts.

## Schema

Rust `settings_catalog`, Swift `GlobalSettingsCatalog`, keys `wawona.pref.*`.
Reject Gemini toys (`wawona_sync_interval`, …) and `group.com.wawona.global`.

## Not Global Settings

Sidebar Desktop / About / Dependencies. Machine editors. One-shot actions.

## Hard rejects

- PrefPane + in-app Global Settings panel on macOS
- Settings.bundle + in-app Global Settings panel on iOS
- On-watch catalog when Settings-Watch.bundle owns Watch prefs
- PrefPane missing → fall back to full in-app duplicate

Rules: `wawona-global-settings-exclusive`. Docs: `Wawona/docs/settings.md`.
Verify: `Wawona/scripts/verify-settings-bundle-keys.py`.
