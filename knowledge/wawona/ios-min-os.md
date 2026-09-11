# iOS min OS vs latest SDK

Indexed mirror of `Wawona/docs/agent-rules/wawona-ios-min-os.md`.
Cursor rule: `wawona-ios-min-os`. Skill: `wawona-ios-min-os`.
GitHub milestone: [`iOS 11-27 (latest SDK, ANGLE + MoltenVK)`](https://github.com/Wawona/Wawona/milestone/4).
Tracker: [`#178`](https://github.com/Wawona/Wawona/issues/178).

## Policy

Wawona iOS (phone and iPad) targets **iOS 11.0** as Mach-O min OS and compiles
**only** against the **latest** iPhoneOS SDK. SDK 26 now. SDK 27 when it ships.
Never downgrade the SDK to match an old OS.

Apple skipped iOS 19-25. Versions in full consideration: 11, 12, 13, 14, 15,
16, 17, 18, 26, and 27 when that SDK exists.

Channels: App Store Mode A, TrollStore `.tipa`, Sileo jailbreak. Same source
min OS. Store IPA still has no JIT / IOMFB SPI / jailbreak copy.

Current shipping target is iOS 26 only. Older iOS is **planned**.

## One ANGLE, one MoltenVK

iOS GLES is ANGLE(Metal). iOS Vulkan is MoltenVK(Metal). One of each per
Wawona iOS build. Wawona patches restore:

- ANGLE Metal on **iOS 11** (upstream floor is iOS 12+)
- MoltenVK on **iOS 11-14** (upstream 1.4.2+ floor is iOS 15+)

Prebuilt XCSoar ANGLE and Khronos `MoltenVK-all.tar` XCFramework unpacks
cannot carry those patches. Source-build in **L1 `wwn-iland`**.

Runtime: query `MTLDevice`. Rust owns the cap policy. ObjC is a trampoline.
Missing Metal feature: do not advertise the Vulkan/GLES cap.

## Nix

Single `deploymentTarget` in L0 `wwn-toolchain`
`dependencies/apple/default.nix` (today `"17.0"`; this work sets `"11.0"`).
ANGLE GN and MoltenVK CMake consume it. Wawona does not grow a CMake product
root. UTM/SDL/Godot are study references only. Guest GUI stays Wayland / iland.

## App Store Connect

Xcode 26 ASC upload range is currently iOS 15-26. That is a separate
investigation from Mach-O minos 11.0. Do not compile against an old SDK to
satisfy ASC. Do not drop TrollStore / Sileo 11-14 for that reason.

## Where to edit

| Change | Repo |
|---|---|
| `deploymentTarget` / latest SDK | `wwn-toolchain` |
| ANGLE / MoltenVK patches | `wwn-iland` |
| `@available` / weak-link | `Wawona` |

tvOS / watchOS / visionOS keep their own mins. Not this policy.

Graphics path: [`wwn-iland-graphics-stack.md`](wwn-iland-graphics-stack.md).
Channels: [`iland-mode-a-b-desktop.md`](iland-mode-a-b-desktop.md).
DAG: [`wwn-repo-dag.md`](wwn-repo-dag.md).
