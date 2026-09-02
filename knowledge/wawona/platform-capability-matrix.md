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
| VM / containers | planned | planned | planned | **planned** | planned | **forbidden** | **forbidden** |
| Multi-window (1 host window per Wayland client) | available | when OS allows | **required** | **required** | single primary | forbidden | forbidden |
| Nested compositors + bundled clients | available | available | available | macOS parity | available | limited | limited |
| Vulkan / OpenGL / ANGLE | available | available | available | available | available | **planned** | **blocked** |
| Desktop / LockScreen replacement | **planned** (Classic Take Over implemented; LockScreen unfinished) | planned | **forbidden** (App Store; TrollStore IOMFB + Sileo) | forbidden | **forbidden** (App Store; TrollStore IOMFB + Sileo) | forbidden | forbidden |
| Wawona Swinging Bridge | planned | planned | **forbidden** (App Store; Sileo Mode B only) | forbidden | **forbidden** (App Store; Sileo Mode B only) | forbidden | forbidden |

## Non-negotiable target rules

- macOS, iOS, iPadOS, tvOS, watchOS, and visionOS must all build, archive, run,
  and ship. Android remains equally covered.
- Weston and **Niri** are real native bundled compositors on **every** row.
  Fake entry points do not count.
- **tvOS GPU is planned** (Metal + OpenGLES in the SDK). **watchOS GPU is
  blocked** (no Metal / OpenGLES / CAMetalLayer on watchOS).
- **visionOS VMs/containers are planned** (same class as iOS/iPadOS). tvOS and
  watchOS remain forbidden.
- iOS and iPadOS Desktop outside store: TrollStore (JIT + IOMFB + Desktop) and
  Sileo. Swinging Bridge is **Sileo-only** (`repo.wawona.io`). TrollStore is
  **not** JIT-only. App Store binaries must never mention jailbreak / TrollStore
  / Sileo. See [`ios-mode-b-channels.md`](ios-mode-b-channels.md).
- Desktop / LockScreen is **not** Wawona Swinging Bridge. Wawona Swinging Bridge is a host-app → Wayland bridge.
- macOS Desktop product gate stays **planned** (LockScreen / greeter). Classic
  Take Over on `.#wawona-macos-desktop-host` is implemented. See
  [`desktop-replacement-macos.md`](desktop-replacement-macos.md).
- KosmicKrisp remains macOS-only. MoltenVK on iOS/iPadOS/visionOS.

## Host window-manager policy

macOS uses AppKit zoom/fullscreen/miniaturize. iOS/iPadOS/tvOS/visionOS and
Android use fill-primary. watchOS ignores host-WM requests.

Graphics: [`wwn-iland-graphics-stack.md`](wwn-iland-graphics-stack.md).
Mode B (macOS): [`iland-mode-a-b-desktop.md`](iland-mode-a-b-desktop.md).
iOS channels: [`ios-mode-b-channels.md`](ios-mode-b-channels.md).
dmabuf: [`dma-buf-zero-copy.md`](dma-buf-zero-copy.md).
How-to: [`desktop-replacement-macos.md`](desktop-replacement-macos.md).
Watchdog: [`mode-b-watchdog-safety.md`](mode-b-watchdog-safety.md).
Contribute: [`contribute.md`](contribute.md).
