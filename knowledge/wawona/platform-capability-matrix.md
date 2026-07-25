# Wawona platform capability matrix

Indexed mirror of the product scope in `Wawona/docs/agent-rules/`
`wawona-platform-targets.md` and the graphics policy in
`Wawona/docs/iland-graphics-stack.md`. All Apple platforms and Android are
first-class product targets.

| Capability | macOS | Android | iPadOS | visionOS | iOS phone | tvOS | watchOS |
|---|---|---|---|---|---|---|---|
| Native machines | yes | yes | yes | yes | yes | yes | yes |
| Remote SSH/waypipe | yes | yes | yes | yes | yes | yes | yes |
| VM / containers | yes | yes | yes | yes | yes | **no** | **no** |
| Multi-window, one host window per Wayland client | yes | when OS allows | **required** | **required** | single primary | no | no |
| Nested compositors and bundled clients | yes | yes | yes | macOS parity | yes | limited | limited |
| Vulkan / OpenGL / ANGLE bundle | yes | yes | yes | yes | yes | **no** | **no** |
| Desktop / LockScreen replacement | yes | yes | no | no | no | no | no |
| anowaW windowing bridge | yes | yes | no | no | no | no | no |

## Non-negotiable target rules

- macOS, iOS, iPadOS, tvOS, watchOS, and visionOS must all build, archive, run,
  and ship. Android remains equally covered.
- Weston and Niri are real native bundled compositors on **every** row.
  tvOS/watchOS use their constrained non-GL fallback; they are not remote-only
  and must not use fake entry points.
- tvOS/watchOS offer native and remote machines only. Do not expose VM or
  container machine types, Vulkan/OpenGL/ANGLE/ICD artifacts, IOKit, or GPU
  bundles.
- iPadOS and visionOS require one host scene/window per Wayland client.
  visionOS otherwise has macOS product parity for software, nested clients,
  graphics, VMs, containers, and Machines UX.
- iOS phone uses one primary host surface. tvOS/watchOS do not offer
  multi-window.
- Desktop, LockScreen, and anowaW are macOS/Android-only. Android uses
  rootless MediaProjection or optional Shizuku/root power mode and never ships
  the macOS Mode B dylib.
- Apple-mobile remote execution uses in-process libssh2. macOS may use its
  unrestricted native process model and regular OpenSSH; Android uses its
  native Android/OpenSSH artifacts.
- KosmicKrisp remains macOS-only because the pinned Mesa documentation
  explicitly says iOS is unsupported. MoltenVK is the Vulkan-to-Metal path on
  iOS/iPadOS/visionOS. tvOS/watchOS ship neither.

## Host window-manager policy

macOS uses AppKit zoom, fullscreen, and miniaturize. iOS/iPadOS/tvOS/visionOS
and Android use fill-primary semantics: maximize and fullscreen configure to
host surface bounds; minimize parks the session in Machines without killing
the client. watchOS ignores host-WM requests.

Graphics-layer details are in
[`wwn-iland-graphics-stack.md`](wwn-iland-graphics-stack.md); Mode B packaging
is in [`iland-mode-a-b-desktop.md`](iland-mode-a-b-desktop.md).
