# watchOS always ships in-process uutils

Product requirement: watchOS Mode A enables Cargo feature `coreutils` the
same as iOS/tvOS/visionOS (`rust-backend-c2n.nix`). Safe-subset uutils via
`wawona_coreutils_main` + `-Wl,-u,_wawona_coreutils_main`.

Do **not** size-gate uutils off watchOS. Do **not** add a weak
`wawona_coreutils_main` stub on arm64 (that drops real uutils). Only
`!__LP64__` (arm64_32) may stub because that slice has no `libwawona.a`.

Stale prose in older WATCHOS-SCOPE / ARCHITECTURE that said "coreutils
excluded" is superseded. Relay Wasm on watchOS is also mandatory
(`wawona-relay-wasm`); do not conflate the two.

Dispatch: `wwn-toolchain/.../wawona-dispatch.c` (weak symbol is link
ordering, not a product opt-out).
