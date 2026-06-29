# Wawona Fastlane + GitHub Release Secrets

Wawona v0.2.4 uses **Nix for builds** and **Fastlane for uploads**. Apple signing certs live in the private repo `aspauldingcode/apple-signing` (fastlane match).

## One-time setup

1. Copy `.release-secrets.env.template` → `.release-secrets.env` (gitignored).
2. Fill Apple, Android, and PAT values (never commit `.p8`, keystores, or JSON keys).
3. Scaffold Fastlane (already in repo): `fastlane/Matchfile` → `git@github.com:aspauldingcode/apple-signing.git`.
4. Bootstrap signing repo:
   ```bash
   ./scripts/bootstrap-apple-signing.sh
   ```
5. Sync GitHub Environment secrets on `Wawona/Wawona`:
   ```bash
   ./scripts/sync-github-secrets.sh
   ```

## GitHub Environment: `release-beta`

| Secret | Purpose |
|--------|---------|
| `MATCH_PASSWORD` | Decrypt match repo |
| `MATCH_GIT_BASIC_AUTHORIZATION` | base64 `x-access-token:PAT` for apple-signing read |
| `APP_STORE_CONNECT_API_KEY` | base64 `.p8` |
| `APP_STORE_CONNECT_KEY_ID` | ASC key ID |
| `APP_STORE_CONNECT_ISSUER_ID` | ASC issuer UUID |
| `APPLE_ID` | Match username |
| `TEAM_ID` | Apple Developer team |
| `ANDROID_KEYSTORE_*` | Play upload key |
| `PLAY_STORE_JSON_KEY` | Play service account JSON |

## Local beta upload

```bash
nix develop .#release
source .release-secrets.env
export TEAM_ID WAWONA_VERSION=0.2.4
fastlane ios beta      # TestFlight: iOS/iPadOS/tvOS/watchOS/visionOS
fastlane android beta  # Play internal track
fastlane beta          # both
```

## CI

`.github/workflows/release-beta.yml` — trigger via `workflow_dispatch` or tag `v0.2.*`.

macOS is **not** uploaded to TestFlight.

## Nix artifacts used by Fastlane

| Lane | Nix output |
|------|------------|
| iOS | `wawona-ios-ipa` |
| iPadOS | `wawona-ipados-ipa` |
| tvOS | `wawona-tvos-ipa` |
| visionOS | `wawona-visionos-ipa` |
| watchOS | `wawona-watchos-ipa` |
| Android | `wawona-android-aab` |

Build example: `TEAM_ID=… nix build .#wawona-ios-ipa --impure`
