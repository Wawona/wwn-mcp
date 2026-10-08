# iOS minimum OS and latest SDK

User decision, 2026-09-30: every Wawona iOS/iPadOS product and its dependencies
compile with deployment target **13.0**. iOS 11 and 12 are no longer supported.
This supersedes the earlier iOS 11 policy, including older skill text.

Use the latest installed iPhoneOS SDK (26.5 verified locally on this date).
When a newer SDK is available, validate it and use it. Never downgrade the SDK
to match the minimum OS. “13 through 27+” is a compatibility objective, not
proof that untested or future systems work.

## Build contract

- L0 `wwn-toolchain/dependencies/apple/default.nix` owns the default floor.
- Its xcode environment and shared Apple-mobile recipes inherit 13.0.
- Wawona's product overlay explicitly passes 13.0 when using a pinned L0 input.
- `xcodegen` `deploymentTarget.iOS` and the ANGLE embed
  `IPHONEOS_DEPLOYMENT_TARGET` fallback are **13.0**. Do not fall back to
  17.0. Store IPA and Sileo `.deb` pass 13.0. TrollStore `.tipa` passes 14.0
  at the call site.
- Rust backends, generated Xcode projects, Swift packages, app archives and
  embedded frameworks must agree. Inspect Mach-O minos in final artifacts.
- tvOS, watchOS, visionOS and macOS retain their own deployment targets.
- Local dependency changes require an updated published pin or explicit local
  input override before a consumer can claim to have built those changes.

## Renderer and UI

Use one native static ANGLE/Metal and one native static MoltenVK/Metal set.
Keep compatibility required by iOS 13/14; remove 11/12-only branches only after
checking they are not also needed by supported systems. Runtime Metal feature
policy stays in Rust. ObjC fills capabilities and bridges native APIs.

SwiftUI exists at the new floor, but APIs added after iOS 13 still need guarded
use or a functional backport. Lowering Package.swift or Xcode settings alone
is not proof that the UI compiles or works. Machine creation, per-machine RAM
and storage settings, launch and lifecycle must work on the supported range.

## Distribution channels

All iOS binaries target 13.0. App Store Mode A stays no Cranelift, no `MAP_JIT`, no Hypervisor, no private Metal/IOMFB APIs, and no QEMU. iOS 27+ Mode A Wasm may use Wasmer WASIX in WebKit. TrollStore and Sileo retain their
separate installation and entitlement contracts. A 13.0 deployment target
does not extend TrollStore's installer window or the iOS Hypervisor window.

Compile success, device operation, App Store processing and review are separate
gates. Do not describe the whole range or store acceptance as verified without
evidence for the actual artifact. Keep the SDK current in every channel.

## Verification

Compile dependencies, Rust static libraries, Swift modules and final apps with
13.0. Audit linked Mach-O load commands and embedded framework minima. Exercise
machine creation, settings, guest launch, graphics, input and background/resume
on representative iPhone/iPad releases and hardware. Record failures explicitly.

## Ownership

Toolchain: `wwn-toolchain`. Graphics recipes: `wwn-iland`. App and UI: `Wawona`.
Relay stays Rust and uses the same floor supplied by its consuming toolchain.
Reference: `Wawona/docs/agent-rules/wawona-ios-min-os.md`.

## iOS 13 shared UI checkpoint (2026-09-30)

`WawonaUI` compiles and links for `arm64-apple-ios13.0` with SDK 26.5.
Use XcodeDefault's Swift and pass the iPhoneOS path with both `--sdk` and
`-Xlinker -syslibroot -Xlinker PATH`. The separately installed Swift toolchain
linked host runtime paths despite `--sdk`; setting global SDKROOT to iPhoneOS
also breaks the macOS package manifest. Do not accept those warning-bearing links.
Host Swift package tests: 40 passed before the final tab-menu/lifecycle cleanup;
rerun after that cleanup. These are package checks, not full app/device proof.
Compatibility helpers live in `Sources/WawonaUI/Compatibility`; iOS 13 retains
machine cards, settings controls, file selection and client preview overview.
Older overview uses a stack; move/close-other actions remain in context menus.
Native task/onChange APIs remain selected where available. Full app linking,
representative-device UI tests, embedded-library minima and dependency pin
propagation remain open. Pure guest AOT is still a proposal, not implemented.

## Product compile and binary-floor repair (2026-09-30)

The complete unsigned iOS device app now compiles and links through
XcodeBuildMCP with SDK 26.5 and deployment target 13.0, including its watch
companion. Latest host UI tests: 40 passed. This first link used old renderer
pins and is not accepted as an iOS 13 artifact: embedded ANGLE plists claimed
13.0 while their Mach-O binaries require 16.0 / SDK 18.5. Inspect binaries.
The Mode A artifact gate now checks all embedded iOS slices and consumes otool
output fully to avoid SIGPIPE under pipefail. It rejects that old artifact.
Updated published graphics/toolchain pins; explicitly evaluate local Relay,
wwn-toolchain floor changes and static-renderer changes for current-source proof.
Device SwiftShader remains excluded by mobile-platform-deps and the existing
store firewall. The old simulator static SwiftShader release contains only its
Vulkan frontend and fails an actual link probe for Reactor/device/decoder
symbols. Source repair must merge the built target dependency archives and
namespace Vulkan entry points beside MoltenVK before accepting a new prebuilt.
Current-source renderer/app rebuilds remain pending; physical operation and
signed distribution are unverified. Map: docs/ios13-product-build-map.md.

### Current-source build isolation and archive tooling (2026-10-01)

Device iOS projects use a device-only dependency profile that retains native
phone, iPad and watch bundles. Simulator builds retain their own full profile;
physical-device evaluation need not force unrelated simulator/platform recipes.
Rebuilt ANGLE archives: all 501 object records are iOS 13.0 / SDK 26.5.
Rebuilt MoltenVK archive load-command record: iOS 13.0 / SDK 26.5. Final current
app and signed device operation remain pending.
SwiftShader source compiled all 1222 steps, then implicit xcrun selected an
unavailable macOS SDK during archive merge. Set DEVELOPER_DIR from find-xcode
and pass the target SDK explicitly to libtool and nm. The install repair is
under rebuild; complete static link proof remains required before acceptance.

### Native archive identity, ABI isolation and Lua closure (2026-10-01)

Current-source app linking exposed three packaging issues beyond UI compilation.
Client ld -r privatization stamped iOS 17.0 / SDK 17.0. It now honors the iOS
deployment setting and uses the actual SDK version; a real zsh archive proof
passed 13.0 / SDK 26.5. Generated prebuild scripts pass selected device or
simulator archive paths directly, preserving local source identity instead of
re-evaluating published inputs from the staged project. Invalid provided paths
fail. Neovim link flags no longer silently drop an unrealized native archive.

ANGLE's Metal-only build still includes 623 Volk Vulkan pointer globals.
MoltenVK function definitions replaced their data storage during linking.
Namespace those globals and references inside ANGLE; real archive proof found
zero public Vulkan globals and all 623 private definitions. The rebuilt source
package passed its new no-public-Vulkan-symbol gate.

Neovim lacked 84 Lua symbols because its collector recognized only modern
LC_BUILD_VERSION. An SDK 26.5 object compiled for iOS 11 reproduces the legacy
LC_VERSION_MIN_IPHONEOS record. Accept recognized legacy records only for the
matching target platform, consume complete otool output, and require real
lua_newstate and luaL_newstate definitions in the final native archive. Fixture
checks accept iOS device objects and reject simulator/macOS for device assembly.
The repaired local Neovim source is explicitly included in the consumer build.

SwiftShader source package and real provider-entrypoint link passed at iOS 13.0
/ SDK 26.5. Use required-entrypoint plus ordinary static archive resolution;
whole-archive loading also pulls unused LLVM disassembler objects with unrelated
undefined RTTI symbols. Full simulator runtime remains pending. Device products
continue to exclude SwiftShader. Overall complete app acceptance, physical
operation, authenticated guest readiness and real imported frames remain open.


## Complete current-source app and driver evidence (2026-10-01)

Complete unsigned phone/watch app now builds and passes Mode A, iOS 13 binary
floors and graphics bundle gates. Native Lua closure and private ANGLE Volk
storage fixes are linked, with zero newer-floor or Vulkan collision warnings.
Guest staging must honor optional initrd: direct-root manifests use null;
declared initrd remains mandatory and unsupported paths reject.
Shared environment help names SwiftShader without linking it. Use driver-owned
SwiftShader Device / SwiftShader driver / SwiftShaderUUID identifiers surviving
stripping, rather than arbitrary prose. A real linked provider probe still
fails the device gate. Signed device operation and VM completion remain open.
Evidence: Wawona/docs/ios13-product-build-map.md and .artifacts/relay-build.


## Native arm64 Simulator artifact evidence (2026-10-01)

SDK26.5 clang stamps a minimal arm64 iOS13 Simulator executable with
IOSSIMULATOR/min14.0. The complete phone/watch Simulator app matches: phone
main/model/UIContracts14.0, watch10.0, all SDK26.5. This does not change the
physical iOS13.0 floor. verify-ios-modeb-artifacts.sh --mode-a-simulator checks
platform7/arm64/floor14; --mode-a still checks device platform2/floor13.
Cross-platform negative tests reject both mismatches.
Simulator SwiftShader may be a real static ICD. Bundle gate requires all three
strong prefixed Vulkan entry points in the same binary plus driver-owned
identifiers. Device products still exclude it; no rendering claim from symbols.
Installing an immutable Nix-store app failed EACCES. Copy the complete bundle
to a writable artifact directory with ditto, change only permissions, then
install through agent-device preserving app data. Never omit bundled clients.
Evidence: simulator-guests-deployment.json, simulator-guests-*-gate-final.log,
device-*-gate-regression.log, and .artifacts/relay-build in Wawona.

## App Store linkage

The floor stays 13.0 on the latest iPhoneOS SDK (26 now, 27 when that SDK is
installed). A dependency built for a newer minimum does not raise Wawona.
Published GhosttyKit is iOS 17. Do not link those objects, and do not rewrite
LC_BUILD_VERSION to pretend they are 13.0.

App Store and TestFlight IPAs do not ship a product .dylib. Link static
archives. Apple's libswift* / SwiftSupport is the store exception. macOS
Desktop Mode B libwayland-mac.dylib stays in .#wawona-macos-desktop-host only.

libghostty on iOS is a static archive rebuilt at deployment target 13.0,
exporting ghostty_* only. The published xcframework is not a Wawona input.
