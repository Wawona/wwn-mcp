# Wawona platform capability matrix

Indexed mirror of `Wawona/docs/agent-rules/wawona-platform-targets.md` and the
mission four-state gates. All Apple platforms and Android are first-class
product targets.

## Four gate states (never collapse to "unsupported")

| State | Meaning | What to do |
|---|---|---|
| **available** | Shipping | Keep green |
| **planned** | Platform allows it; our work unfinished | Finish it; never remove the target |
| **blocked** | We want it; no public platform API | Re-check on SDK bumps; never private API |
| **forbidden** | Product/store policy | Never enable |

## Matrix

| Capability | macOS | Android | iPadOS | visionOS | iOS phone | tvOS | watchOS |
|---|---|---|---|---|---|---|---|
| Native machines | available | available | available | available | available | available | available |
| Remote SSH/waypipe | available | available | available | available | available | available | available |
| VM / containers | planned | planned | planned | planned | planned | **forbidden** | **forbidden** |
| Multi-window (1 host window per Wayland client) | available | when OS allows | **required** | **required** | single primary | forbidden | forbidden |
| Nested compositors + bundled clients | available | available | available | macOS parity | available | limited | limited |
| Vulkan / OpenGL / ANGLE | available | available | available | available | available | **planned** | **blocked** |
| Desktop / LockScreen replacement | **planned** (Classic Take Over implemented; LockScreen unfinished) | planned | **forbidden** in App Store. TrollStore Mode B tipa is the current IOMFB Desktop product | forbidden | **forbidden** in App Store. TrollStore Mode B tipa is the current IOMFB Desktop product | forbidden | forbidden |
| Wawona Swinging Bridge | planned | planned | **forbidden** (App Store; Sileo Mode B later) | forbidden | **forbidden** (App Store; Sileo Mode B later) | forbidden | forbidden |
| Relay Wasm (WASI / wpm) | available | available | available | available | available | available | available |

## Non-negotiable target rules

- macOS, iOS, iPadOS, tvOS, watchOS, and visionOS must all build, archive, run,
  and ship. Android remains equally covered.
- Weston and **Niri** are real native bundled compositors on **every** row.
  Fake entry points do not count.
- **Relay Wasm** is a real native bundle on **every** row including watchOS
  and Linux. Pulley on Apple mobile store artifacts. Do not size-gate it off.
- **hello-wasi-gui** (`wl_shm` + xdg) must **run** on every target, including
  Apple Watch Machines Start. Transfer-only WatchConnectivity is not enough.
  Watch GPU wasm (GLES/Vulkan/Metal) is blocked; present is SpriteKit of SHM.
- **tvOS GPU is planned** (Metal + OpenGLES in the SDK). **watchOS GPU is
  blocked** (no Metal / OpenGLES / CAMetalLayer on watchOS).
- **visionOS VMs/containers are planned** with the iOS/iPadOS Relay static-CPU
  profile path; tvOS/watchOS remain forbidden. Guest UI is Wayland over
  vsock/waypipe into iland. Swift `virtualMachineGate` / `containerGate` and
  Relay's backend resolver must match this matrix.
- iOS and iPadOS Desktop is **forbidden** in the App Store IPA. The current
  Mode B Desktop product is the TrollStore `.tipa`
  `com.aspauldingcode.Wawona.ModeB` (IOMFB, Relay VMs planned/fail-closed,
  zsh PTYs). Sileo/Doorman/ElleKit and Wasm JIT are deferred. App Store binaries
  must never mention TrollStore, jailbreak, or JIT.
- iOS and iPadOS Swinging Bridge is **forbidden** in the App Store IPA. It is
  Sileo Mode B later, not TrollStore.
- Desktop / LockScreen is **not** Wawona Swinging Bridge. Wawona Swinging Bridge is a host-app → Wayland bridge.
- macOS Desktop product gate stays **planned** (LockScreen / greeter). Classic
  Take Over on `.#wawona-macos-desktop-host` is implemented. See
  [`desktop-replacement-macos.md`](desktop-replacement-macos.md).
- KosmicKrisp remains macOS-only. MoltenVK on iOS/iPadOS/visionOS.
- iOS / iPadOS Mach-O min OS is **13.0** against the latest iPhoneOS SDK only. Do not raise that floor to link a newer dependency, and do not ship a product `.dylib` in an App Store IPA.
  Older iOS is planned. See [`ios-min-os.md`](ios-min-os.md).
- Ghostty console is required on macOS, iOS, iPadOS, tvOS, watchOS, visionOS, Android, and Linux. Owner: `github.com/Wawona/Ghostty` (Zig, flake input `wwn-ghostty`). Keyboard keys above the software keyboard: `github.com/Wawona/ToolbarKeys` (Rust + UniFFI). Renderer: Metal where the SDK has Metal (static archive, iOS deployment 13.0, no product dylib). Android and Linux use OpenGL inside libghostty. watchOS uses a software grid presented with SpriteKit. VM kinds stay forbidden on tvOS, watchOS, and visionOS. Those consoles are the native shell and SSH.

## Host window-manager policy

macOS uses AppKit zoom/fullscreen/miniaturize. iOS/iPadOS/tvOS/visionOS and
Android use fill-primary. watchOS ignores host-WM requests.

Graphics: [`wwn-iland-graphics-stack.md`](wwn-iland-graphics-stack.md).
Mode B: [`iland-mode-a-b-desktop.md`](iland-mode-a-b-desktop.md).
How-to: [`desktop-replacement-macos.md`](desktop-replacement-macos.md).
Watchdog: [`mode-b-watchdog-safety.md`](mode-b-watchdog-safety.md).
Contribute: [`contribute.md`](contribute.md).
