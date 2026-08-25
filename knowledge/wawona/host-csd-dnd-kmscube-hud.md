# Host CSD, drag-drop, and cube HUD (recent integration)

Indexed so agents do not re-break these. Code lives in `Wawona` (host) and
`wwn-kmscube` (HUD). Port fidelity still applies: do not re-host Wayland
clients onto KMS because a winsys is unfinished.

## CSD vs SSD (toplevel vs popup)

xdg-decoration is negotiated. macOS supports CSD **and** forced SSD. Android
and the iOS family force SSD.

A CSD **popup** (context menu) is a borderless window sized to the **full
buffer**. A CSD **toplevel** must do the same. Cropping the buffer to
`xdg_surface.set_window_geometry` is **SSD-only** (host chrome, strip leftover
client CSD). ClientSide must show the full buffer, including titlebar and
shadow.

`should_crop_buffer_to_window_geometry` in
`Wawona/src/core/wayland/xdg/decoration.rs` returns true only for ServerSide.

macOS `WWNCreateCGImageFromIOSurface` must keep alpha (CSD shadows). Forcing
`A=0xFF` is iOS-family only.

Force SSD ON and Force SSD OFF are both required before calling a decoration
scenario green. Docs: `Wawona/docs/wslg-weston-desktop-map.md`.

## Host drag-and-drop → Wayland

Finder / iOS Files drop of a file or image onto a focused Wayland client
becomes `wl_data_device` (`text/uri-list` / PNG). AppKit was registered as a
drop target but `injectDragEnterForWindow:` was declared and never implemented.

Bridge: `WWNCompositorBridge` enter/motion/drop/leave → `WWNCoreInjectDrag*`.
Rust `inject_drag_enter` must send motion after `start_dnd` (Smithay
`ServerDnDGrab` only sends `enter` on first motion). Nested niri still has to
forward parent DnD to inner clients; that is niri's job.

iOS/iPadOS/visionOS: `UIDropInteraction` on the compositor view (not
tvOS/watchOS).

## kmscube / cube status hub

Wawona HUD in `wwn-kmscube/upstream/wwn_cube_hud.c`. Not upstream kmscube.

The hub used to:

1. Overwrite GL attribs 0/1 and disable them, so the cube vanished after the
   first overlay frame. Restore attribs 0-2 (kmscube sets them once at init).
2. Scale glyphs from overlay height (`fb/4`), so Retina text was ~16px. Scale
   from framebuffer height and shrink to fit width.
3. Show upside down / at the bottom on iOS: ANGLE/Metal texture V vs GL NDC.
   Apple fragment shader flips V; the quad sits at GL bottom so Metal present
   puts the hub at screen top-left.

Vulkan cubes blit the same text into the FB (`wwn_cube_hud_blit_rgba`).
F7-F9 overlays use this hub (client name, fps, kms/drm/gbm, GL vs Vulkan,
ANGLE / MoltenVK / KosmicKrisp).
