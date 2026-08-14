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
| VM / containers | planned | planned | planned | **forbidden** | planned | **forbidden** | **forbidden** |
| Multi-window (1 host window per Wayland client) | available | when OS allows | **required** | **required** | single primary | forbidden | forbidden |
| Nested compositors + bundled clients | available | available | available | macOS parity | available | limited | limited |
| Vulkan / OpenGL / ANGLE | available | available | available | available | available | **planned** | **blocked** |
| Desktop / LockScreen replacement | planned | planned | **forbidden** (App Store) | forbidden | **forbidden** (App Store) | forbidden | forbidden |
| anowaW app bridge | planned | planned | **planned** | forbidden | **planned** | forbidden | forbidden |

## Non-negotiable target rules

- macOS, iOS, iPadOS, tvOS, watchOS, and visionOS must all build, archive, run,
  and ship. Android remains equally covered.
- Weston and **Niri** are real native bundled compositors on **every** row.
  Fake entry points do not count.
- **tvOS GPU is planned** (Metal + OpenGLES in the SDK). **watchOS GPU is
  blocked** (no Metal / OpenGLES / CAMetalLayer on watchOS).
- **visionOS VMs/containers are forbidden** (same class as tvOS/watchOS).
- iOS and iPadOS share anowaW: Mode A in store; Mode B only via
  `repo.wawona.io` (website). App Store binaries must never mention jailbreak.
- Desktop / LockScreen is **not** anowaW. anowaW is a host-app → Wayland bridge.
- KosmicKrisp remains macOS-only. MoltenVK on iOS/iPadOS/visionOS.

## Host window-manager policy

macOS uses AppKit zoom/fullscreen/miniaturize. iOS/iPadOS/tvOS/visionOS and
Android use fill-primary. watchOS ignores host-WM requests.

Graphics: [`wwn-iland-graphics-stack.md`](wwn-iland-graphics-stack.md).
Mode B: [`iland-mode-a-b-desktop.md`](iland-mode-a-b-desktop.md).
Contribute: [`contribute.md`](contribute.md).
