# Nix-generated artifacts

Indexed summary. Full copy: `Wawona/docs/agent-rules/wawona-nix-generated.md`.
Cursor rule: `wawona-nix-generated` (`alwaysApply`).

Reproducible generated files are Nix store outputs. Not git.

UniFFI Swift/Kotlin: `$rustBackend/uniffi/{swift,kotlin}` via host
`dependencies/generators/uniffi-bindgen.nix` (UniFFI 0.30). Never crate2nix
`cli`. Never `Sources/Generated`.

`Wawona.xcodeproj` is always Nix XcodeGen (`xcodegen.nix`). Never hand-edit
`project.pbxproj`. Never copy the project aside and patch `/nix/store` or
`/store/<hash>` into it. Spec paths stay relative under `.nix-deps/`.

Exception: `docs/protocol-status.md` is a committed CI contract.
