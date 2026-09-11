# Nix-generated artifacts

Indexed summary. Full copy: `Wawona/docs/agent-rules/wawona-nix-generated.md`.
Cursor rule: `wawona-nix-generated` (`alwaysApply`).

Reproducible generated files are Nix store outputs. Not git.

UniFFI Swift/Kotlin: `$rustBackend/uniffi/{swift,kotlin}` via host
`dependencies/generators/uniffi-bindgen.nix` (UniFFI 0.30). Never crate2nix
`cli`. Never `Sources/Generated`.

Exception: `docs/protocol-status.md` is a committed CI contract.
