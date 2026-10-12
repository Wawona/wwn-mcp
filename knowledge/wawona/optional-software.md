# Optional software (wasm and deb)

Wawona ships the compositor plus a tiny shell. Optional Wayland clients install
from `repo.wawona.io`.

## Keep in the app

- Smithay compositor + iLand (ANGLE / MoltenVK as needed)
- Relay wasm runtime + `hello-wasi-gui` smoke
- zsh, uutils safe subset, fastfetch (App Store patches stay here only)

## Move out

weston, niri, foot, weston-terminal, weston toys, GPU cubes → **deb**
(jailbreak iOS rootless/rootful, Termux, Linux). No App Store patches in those
recipes. GTK toolkit → WASIX **`pkgs/libraries/`** (not `programs/`) plus deb
on `repo.wawona.io`. Store optional GUI → wasm P1 / WASIX lanes. See
`libraries-vs-programs.md`.
Termux Android debs: Google NDK clang (Bionic `aarch64`, prefix
`/data/data/com.termux/files/usr`). Recipe helper:
`repo.wawona.io/lib/androidNdk.nix`. Never pack glibc Linux ELFs. Do not use
nixpkgs `aarch64-unknown-linux-android` GCC bootstrap on Darwin.

## Deb simplification

Debs may fork/exec/JIT. Do not copy `apple-mobile.nix`, renamed `*_main`, or
in-process cairo skips into deb recipes. Unlink from the app, then delete that
client's App Store patch set.

## Rules

`wawona-optional-software`, `wawona-native-compositors`, `repo-wawona-io-channels`,
`wawona-wasm-cli-ports`. Skill: `wawona-optional-software`.

Default Machines session: Native Shell (zsh), not `weston-terminal`.
