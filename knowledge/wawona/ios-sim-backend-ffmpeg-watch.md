# iOS sim backend: ffmpeg nativeDeps and Watch vs phone (2026-10-12)

## waypipe video / libavutil

Wawona root Cargo enables waypipe `video`. crate2nix builds
`waypipe-ffmpeg-wrapper`. Without `ffmpeg` in Apple-mobile
`nativeDeps` (`mobile-platform-deps.nix`), build.rs dies:

```text
Package libavutil was not found
PKG_CONFIG_PATH …/jq-…/lib/pkgconfig
```

`rust-backend-c2n.nix` only forwards pkg-config when
`nativeDeps ? ffmpeg`. Mirror standalone `wwn-waypipe` `ios.nix`.

Prove: `nix build .#wawona-ios-sim-backend`.

## Watch companion ≠ phone UI

`wawona-ios-app-sim` embeds Watch. Undefined
`wl_*` / `xdg_*` from `WWNMiniWaylandServer.o` on Watch does not block
phone Machines / half-sheet proof. Use tip backend +
`WAWONA_BACKEND_OUT` + `xcodebuild` / agent-device.

## Agent log hygiene

Do not judge `nix build` via `tee | tail` alone (pipeline exit / truncated
logs). Full `-L` log + `nix log <drv>`.

Skills: `wawona-ios-sim-runtime`, `wawona-optional-software` (stale
foot/fuzzel force_load).
