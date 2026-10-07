# Wawona reproducible direnv and Nix

Wawona development enters the pinned flake through committed `.envrc` using
`use flake`; `flake.lock` pins the environment. nix-direnv caches the shell.
Local signing data is ignored `.envrc.local`, sourced before `use flake` so
impure release outputs can read it. Never place Team IDs, certificate paths,
passwords, profiles, or identities in `flake.nix`, tracked `.envrc`, a Nix
derivation, or logs. Signed Apple outputs need `nix build --impure` plus the
local signing inputs. Canonical rule:
`Wawona/docs/agent-rules/wawona-direnv-nix.md`.

`TEAM_ID` alone is insufficient for IPA export. Preserve the certificate,
password, provisioning-profile, signing-method, and signing-identity gate.

## Local Xcode source filtering (2026-09-30)

A path-based full app build copied ignored `build/` and `.derivedData*` trees
into WawonaXcodeProject. Stale DerivedSources links then failed
`noBrokenSymlinks` before app linking. Filter local build outputs before
source staging; never disable the fixup check. Exclude root `build`, `target`,
`.build`, `.direnv`, plus `.cache`, `.git`, `.derivedData*`, and `result` links.
Keep untracked product sources in local builds; git flakes omit them.
Host Swift Keychain tests need access outside the execution sandbox. All 40
passed with that access; the sandboxed attempt failed secret round-trips.

Also exclude root `.nix-deps`, `.artifacts`, `.agent-device` and
`Wawona-gradle-project` when staging a local product source. These generated
outputs added approximately 11 GB to a measured source snapshot. Preserve
the original files and untracked product sources; do not disable fixup checks.
