# Wawona Fastlane + GitHub Release Secrets

Wawona uses **Nix for builds** and **Fastlane for uploads**. Apple signing certs
live in the private repo `aspauldingcode/apple-signing` (fastlane match).

Release secret **values** are never in the public tree. They live in the private
pass store (`aspauldingcode/.password-store`) under
`secretspec/wawona/release-{apple,android}/`, declared by name in
`Wawona/secretspec.toml`. Host **sops-nix** (dendritic) unlocks GPG for pass;
do not put MATCH/Play ciphertext into public Wawona sops files.

Canonical maintainer doc: `Wawona/docs/maintainers/secrets.md`.

## One-time setup (tier 0)

1. GPG via dendritic/sops-nix; clone
   `git@github.com:aspauldingcode/.password-store.git` → `~/.password-store`.
2. Confirm: `pass show secretspec/wawona/release-apple/TEAM_ID`.
3. Scaffold Fastlane (already in repo): `fastlane/Matchfile` →
   `git@github.com:aspauldingcode/apple-signing.git`.
4. Bootstrap signing repo:
   ```bash
   cargo xtask secrets bootstrap-signing
   ```
5. Sync GitHub Environment secrets on `Wawona/Wawona`:
   ```bash
   cargo xtask secrets sync
   ```

## GitHub Environment: `release-beta`

| Secret | Purpose |
|--------|---------|
| `MATCH_PASSWORD` | Decrypt match repo (+ Developer ID P12 passphrase) |
| `MATCH_GIT_BASIC_AUTHORIZATION` | base64 `x-access-token:PAT` for apple-signing read |
| `APP_STORE_CONNECT_API_KEY` | base64 `.p8` |
| `APP_STORE_CONNECT_KEY_ID` | ASC key ID |
| `APP_STORE_CONNECT_ISSUER_ID` | ASC issuer UUID |
| `APPLE_ID` | Match username |
| `TEAM_ID` | Apple Developer team |
| `DEVELOPER_ID_APPLICATION_P12_BASE64` | Developer ID Application PKCS12 (macOS notarize) |
| `DEVELOPER_ID_INSTALLER_P12_BASE64` | Developer ID Installer PKCS12 (`productsign`) |
| `ANDROID_KEYSTORE_*` | Play upload key |
| `PLAY_STORE_JSON_KEY` | Play service account JSON |

## Local beta upload

```bash
nix develop .#release
secretspec check -P local
cargo xtask secrets run -- fastlane ios beta      # TestFlight
cargo xtask secrets run -- fastlane android beta  # Play internal
cargo xtask secrets run -- fastlane beta          # both
```

## CI

`.github/workflows/release-beta.yml`. Trigger via `workflow_dispatch`, push to
`master`, or tag `v*` (CalVer `vYY.M.D`).

Store beta failure notes:

- Play internal `versionCode` must increase across all release mechanisms.
  `github.run_number` is only local to one workflow and can be below a release
  already on Play. Use a monotonic UTC epoch value and stay below Android's
  `2100000000` maximum.
- The Watch companion has its own App ID and provisioning profile. If its
  target carries CloudKit entitlements, enable iCloud on both the iPhone and
  Watch App IDs, then force-regenerate and sync the App Store match profiles.
  Treat capability enablement errors as fatal. CI reads the profiles from
  `apple-signing` and cannot repair them read-only.

macOS GitHub DMG assets need Developer ID sign + notarize (separate from
TestFlight).

## Nix artifacts used by Fastlane

| Lane | Nix output |
|------|------------|
| iOS | `wawona-ios-ipa` |
| iPadOS | `wawona-ipados-ipa` |
| tvOS | `wawona-tvos-ipa` |
| visionOS | `wawona-visionos-ipa` |
| watchOS | `wawona-watchos-ipa` |
| Android | `wawona-android-aab` |

IPA shipping path is **match + gym**, not a bare `nix build …-ipa` for store
upload.
