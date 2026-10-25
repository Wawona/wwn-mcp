# Apple store archive preflight

## Incident

On 2026-10-24, the TestFlight store workflow passed Gate: products and then
failed while archiving `Wawona-iOS` with its embedded `Wawona-watchOS` target.
The simulator product matrix did not compile this signed device archive path.
The reported `Build Rust Backend via Nix` failure was first addressed by
clearing `NIX_BUILD_TOP` in `scripts/release-env.sh`: `nix develop` exports the
marker for its shell, but the host Fastlane/Xcode process is outside a Nix
derivation and must realize missing backends through the daemon.

The detailed local archive then surfaced a Swift function convention mismatch at two calls to
`wwn_term_string_free`. `WatchTerminalScreen.swift` declared the native symbol
at file scope while `WatchNativeShell.swift` declared the same native symbol as
`WatchShellABI.termStringFree`. Consolidating call sites onto the shared ABI
wrapper removes the duplicate symbol declaration and resolves the Swift compile
error. The next archive then linked `arm64_32` and exposed missing Watch C ABI
fallbacks: that compatibility slice intentionally omits the Nix Rust, PTY, and
terminal archives, while Swift still emitted references to their symbols.
Complete weak fail-closed definitions in `WWNWatchStubs.c` resolve the
compatibility slice; arm64 continues using real libraries.

On 2026-10-25, Master Store preflight reached the same embedded Watch phase and
stopped on the fail-closed CalVer check because `VERSION`, `Cargo.toml`, and
`Cargo.lock` still said `26.10.24` while the runner date was `26.10.25`. No IPA
was uploaded. The version bump and lockfile update were then validated with
`verify-calver-today.sh` and `cargo metadata --locked`.

## Entities and relations

| Entity | Type | Provenance |
|---|---|---|
| Gate: products | CI workflow | `.github/workflows/device-gate.yml` |
| Ship: beta (stores) | CI workflow | `.github/workflows/release-beta.yml` |
| Wawona-iOS | Device archive target | `fastlane/Fastfile`, `APPLE_BETA_TARGETS` |
| Wawona-watchOS | Embedded Watch target | XcodeGen iOS companion target |
| WatchShellABI.termStringFree | Swift native ABI declaration | `Sources/WawonaWatch/WatchNativeShell.swift` |
| TestFlight upload | External side effect | `fastlane/Fastfile`, `upload_to_testflight` |

| Subject | Relation | Object | Evidence |
|---|---|---|---|
| Gate: products | BUILDS_SIMULATOR_ONLY_FOR | Apple product matrix | `.github/workflows/device-gate.yml` |
| Wawona-iOS archive | EMBEDS_AND_COMPILES | Wawona-watchOS | XcodeGen generated scheme and failed archive log |
| Wawona-watchOS arm64_32 | OMITS | Nix Rust, PTY, terminal archives | `dependencies/generators/xcodegen.nix` link settings |
| WatchTerminalScreen | CALLS | WatchShellABI.termStringFree | `Sources/WawonaWatch/WatchTerminalScreen.swift` |
| `ios beta` lane | PREFLIGHTS_ALL_IPAS_BEFORE | ASC version creation and TestFlight upload | `fastlane/Fastfile` |
| `ios beta` lane | REQUIRES_COMPLETE_FOR | Newly submitted ASC build upload | `fastlane/lib/asc_build_upload_gate.rb`, `fastlane/Fastfile` |
| TestFlight transport success | DOES_NOT_PROVE | ASC processing acceptance | Apple `buildUploads` state vs Fastlane upload action return |
| Fastlane or release workflow changes | TRIGGER | Gate: products, then store workflow on green master | `.github/workflows/device-gate.yml`, `.github/workflows/release-beta.yml` |

## Durable gate

The Apple beta lane archives, exports, and validates every selected Apple IPA
before creating ASC version records or the first TestFlight upload. It uploads
the exact IPAs it preflighted, snapshots matching upload IDs, and polls Apple's
`buildUploads` endpoint by version, build number, and platform. A new record
must reach `COMPLETE`; `FAILED`, missing record, or timeout fails CI. Transport
success and local `altool` validation are not server-side acceptance. This
catches archive, embedded Watch compile, signing, export, local IPA invariant,
and ASC processing failures. Changes to the release lane trigger Gate: products
on both release branches so a green master product result starts the store
preflight and upload workflow. A green simulator product matrix alone is not
evidence that the App Store device archive is buildable.

Reproduce the iOS plus Watch device archive without uploading with
`CI=true WAWONA_DEBUG_SCHEME=Wawona-iOS fastlane ios debug_export`.
