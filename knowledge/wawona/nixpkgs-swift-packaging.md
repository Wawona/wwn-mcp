# nixpkgs Swift packaging rewrite (STEP 0)

Measured 2026-10-06 against `Wawona/Wawona/flake.lock`.

## Gate

New nixpkgs Swift packaging (Swift **6.2.x**, `swiftPackages.stdlib`, unwrapped
`swiftPackages.swift`, default stdenv) must be present **before** migrating
derivations. If STEP 0 fails, stop. Do not pin older Swift. Do not invent a
Swift overlay flake.

## This flake (fail)

| Check | Result |
|---|---|
| Locked `nixpkgs` rev | `42f17a57f4f6e33b3de3dca0a2a5ea5233169d02` |
| `swift.version` | **5.10.1** |
| `swiftPackages.stdlib` | **absent** |

Upstream unstable on search.nixos.org already lists `swiftPackages.stdlib`
**6.2.4**. This lock is still on the old packaging.

## Where SwiftPM lives (when lock is ready)

Not L4 Wawona product apps (those use Xcode). Swift nix recipes are under
`wwn-containers` (and mirrors):

- `dependencies/containers/macos/swiftpm2nix/`
- `apple-container.nix`, `wwn-containerd*.nix`

Keep `swiftpm2nix` vendoring until a derivation fails. Do not wholesale-switch
to `fetchSwiftPMDeps`.

## Breaking changes (when migrating)

1. `swiftPackages.swift` is no longer wrapped. Drop clang-wrapper assumptions.
2. Delete custom Swift stdenv. Use default stdenv.
3. Depend on `swiftPackages.stdlib` for Swift applications.
4. Prefer upstream names `Dispatch` / `Foundation` / `XCTest` (aliases remain).

## Agent action

If asked to migrate and STEP 0 reports 5.10.1: report lock wrong. Ask whether
to bump `nixpkgs` in `flake.lock`. Do not proceed with packaging edits until
`nix eval` shows 6.2.x and `stdlib` exists.
