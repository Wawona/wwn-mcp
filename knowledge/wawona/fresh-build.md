# Fresh build (never stale apps)

Apple and Android apps build with **Xcode 27 and Android Studio** over
prebuilt dependency slices that `cargo xtask deps get` fetches from GHCR
(`deps.lock`). `cargo xtask build` drives the same projects from a shell.
Nix builds those slices in CI (`cargo xtask deps get <sdk> --nix` locally),
builds Linux, and owns L0/L1. There is no Nix app derivation for an Apple or
Android product, no project generator, and no Python.

Do not launch `/Applications/Wawona.app`. Do not treat host `cargo` + `/tmp`
staticlib overlays as the product. Do not boot Vision Pro when the task is
Wawona Terminal on macOS.

Canonical rule: `Wawona/docs/agent-rules/wawona-fresh-build.md`.
Skill: `wawona-fresh-build`. Guide: `Wawona/docs/compilation.md`.

## Commands

```bash
cd ~/Wawona/Wawona
cargo xtask deps get macosx iphonesimulator android
open Wawona.xcodeproj          # or Android Studio on android/
cargo xtask build macos        # ios, ipados, ios-modeb, tvos, visionos, watchos, android
cargo xtask test ios
cargo xtask install            # Release build into /Applications with agents and helper
nix run .#terminal
eval "$(WAWONA_TEST_REBUILD=1 cargo xtask tip macos)"
eval "$(WAWONA_TEST_REBUILD=1 cargo xtask tip tvos)"
```

Tip path: `/tmp/wawona-macos-tip/…/Wawona.app` (simulators: `/tmp/wawona-*-tip`).
Stamps: `git-HEAD` + `product-FP`. Refuse install copies and morning tips
after `Sources/` edits (`wawona-test-tip-app`).

## Terminal device matrix

| Bug surface | Run on |
|-------------|--------|
| macOS Terminal / Ghostty | macOS tip or `nix run .#terminal` |
| iOS Terminal | iPhone Simulator or device |
| visionOS Terminal | visionOS Simulator, only when that is the task |
