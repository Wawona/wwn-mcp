# iland Mode A / Mode B and Desktop Replacement (agent knowledge)

Indexed summary for WWN-MCP. Full doc:
`Wawona/docs/iland-mode-a-b-desktop.md`. Cursor rule:
`wawona-iland-mode-b-desktop`.

## Facts agents get wrong

- **Wrong:** “Wawona always injects libwayland-mac.dylib / always needs SIP off.”
- **Right:** Default product path is **Mode A** (`libiland_userland.a`, in-window
  present callback). Mode B dylib is **optional**, macOS desktop-host only,
  SIP-gated in Settings.

## Mode A

- Default unprivileged, in-app presentation path.
- Apple mobile statically links `libiland_userland.a`; present is
  `iland_drm_set_present_callback` → host Metal (`WWNIlandPresenter`).
- macOS uses its unrestricted native in-window implementation. This is a
  product-mode distinction, not an App Store feature restriction on macOS.
- Android presents to app-owned AHardwareBuffer/Surface targets.
- tvOS/watchOS keep constrained non-GL iland fallbacks. Their real native
  Weston and Niri bundles remain required even though GPU/VM artifacts are
  forbidden.

## Mode B

- `libwayland-mac.dylib` from `wwn-iland` `iland-baremetal` /
  `macos-baremetal.nix` (CMake + Dobby; CoreBedtime load model).
- Bundled only in `wawona-macos-desktop-host` at
  `Contents/Library/Wawona/iland/libwayland-mac.dylib`.
- Engage when `WWNSipStatus` allows (Disabled or PartiallyDisabled =
  `Debugging Restrictions: disabled`) **and** `DesktopReplacementEnabled`
  **and** connecting the Desktop machine → `WWNDesktopReplacementController`.
- Root required for dylib constructor; privileged launch via admin dialog.
- Never in the default `wawona-macos` product, Apple-mobile family, or Android
  APKs. macOS remains unrestricted by App Store feature rules; the split keeps
  privileged Desktop Replacement in its explicit desktop-host artifact.
- `baremetal` is a legacy package label, not kernel DRM/KMS. Virtual device
  opens/ioctls terminate in iland; framebufferd acknowledges host-vsync present
  over Mach IPC. No kernel module, kernel patch, real DRM node, or direct KGSL.

## Android

No SIP and no `libwayland-mac.dylib`. Wawona Swinging Bridge uses rootless/baseline
MediaProjection or an optional Shizuku/root power mode, with automatic fallback
when power access is unavailable. This Android power tier is not the macOS
injected-dylib implementation.

## Verify

`Wawona/.github/scripts/verify-iland-mode-b-bundle.sh --mode present|absent <root>`

Graphics routes: [`wwn-iland-graphics-stack.md`](wwn-iland-graphics-stack.md).
Target scope: [`platform-capability-matrix.md`](platform-capability-matrix.md).
