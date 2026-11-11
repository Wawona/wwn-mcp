# Wawona package check

Agents compiling a dependency or package must write three lines before the
compiler: `LIBC`, `TEXT`, and `GPU`.

Android Termux libc is Bionic, not glibc and not musl. Use NDK clang from
`repo.wawona.io/lib/androidNdk.nix`. Do not use host pkg-config. Do not use
the nixpkgs Android GCC bootstrap.

Android static libraries cross-built on Darwin must set `dontStrip = true`.
Nix's host Darwin fixup runs cctools on the archive, adding a BSD symbol table
while leaving GNU `/` and `//` members. Android `ld.lld` then rejects those
members as non-object files. Verify the linked consumer, for example the
Android `fuzzel` target, not only each library derivation.

When a Darwin product references a Linux artifact, prebuild the exact pinned
Linux output on a native Linux runner and let the shared CI cache publish it
before the Darwin job starts. Add a job dependency so the Darwin product cannot
race the cache push. Nix on macOS can consume cached Linux store paths, but it
cannot build a missing `aarch64-linux` dependency. Keep the product artifact
when fixing this gate; do not silently drop the Linux guest feature to avoid
the platform mismatch.

pixman, freetype, fontconfig, harfbuzz, cairo, and pango are separate L0
libraries. harfbuzz does not replace cairo. cairo does not include harfbuzz
and does not provide GLES. On Android and wasm there is no system cairo.
Each text library is built for that libc.

GPU is L1 `iLand` (one hop: ANGLE or MoltenVK to Metal, Android system or
SwiftShader). watchOS is `wl_shm` plus SpriteKit. Never open `/dev/dri`.

`nix build` exiting 0 is not green. Verdict is `package-doctor`
(`repo.wawona.io` `nix run .#package-doctor -- --target android|linux|macos|ios-rootless|wasi-p1|wasi-p2|wasix --out PATH`).
`--wayland` stays red without a socket trace.

New deb program: copy `pkgs/wayland/TEMPLATE.nix`, add one line in
`catalog/deb/<kind>/<name>/`. `builtins.readDir` is the index. Android libs stay `pkgs/wayland/ndkLibs.nix`.
New toolkit: one `*-android` recipe plus one `libs` name in `ndkLibs.nix`.
Do not import `lib/androidNdk.nix` from a package file. Termux apt unpack
stays `lib/termuxSysroot.nix`. Do not link the new toolkit into the store
app (`deps.nix`). In-app stays compositor, Relay wasm, zsh, uutils,
fastfetch.

Skill and rule: `wawona-package`.
Wasm lanes stay `wawona-wasm-cli-ports`. Debs stay `wawona-optional-software`.
