# UniFFI product domain

Indexed summary. Full copy: `Wawona/docs/agent-rules/wawona-uniffi-domain.md`.
Cursor rule: `wawona-uniffi-domain` (`alwaysApply`).

## Split

Steal JFFI’s idea (rust domain, native views). Do not use the JFFI CLI or fork
it. Wawona owns macOS, iOS, iPadOS, tvOS, watchOS, visionOS, Android, Linux.

## Two bridges

- UniFFI: `MachineProfile`, prefs, launch, validation, session policy.
- `WWNCore*` C poll: compositor ABI. No UniFFI callbacks.

## Smell

`MachineProfile` was triplicated (Swift, `src/linux/machine_profile.rs`, Kotlin).
Rust `src/domain` is now the schema + store (list/get/put/delete) + validation.
Mirrors are frozen. Keep `wawona.machineProfiles.v1` JSON keys.

UniFFI: `MachineProfileStoreApi`, `settings_visible_sections`,
`capability_gate`, `session_is_forbidden_client_id`. Bindings are Nix
`$out/uniffi`, never git. Hosts that lack imported Swift call
`wawona_profiles_v1_*` / `wawona_settings_visible_sections` /
`wawona_capability_gate` (not `WWNCore*`).

Apple `PlatformCapabilities` and `MachineProfile.isIgettyConsoleNotAMachine`
read those trampolines when rust is linked. visionOS / tvOS / watchOS VM
and container stay forbidden. igetty / modeb-tty is never a Machines id.

`MachineEditorDomain` is the one editor mapping for WawonaUI and Watch.
Do not restore `WatchUIContractAdapters`. New `.swift` domain files must
be tracked or staged; Nix `git+file` omits untracked sources.
