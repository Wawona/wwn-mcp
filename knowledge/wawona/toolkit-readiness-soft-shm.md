# Toolkit readiness and software SHM fallback

Indexed mirror of the toolkit contract in
`Wawona/docs/iland-graphics-stack.md`. Toolkit ports consume the shared
Wayland/graphics contracts; they do not add private Metal renderers.

| Consumer | GPU route | Software route |
|----------|-----------|----------------|
| Weston | GL renderer + iland DRM/GBM/EGL | pixman + `wl_shm` |
| GTK4 | GDK Wayland + GSK GL/Vulkan | GSK Cairo + `wl_shm` |
| Qt | QtWayland QPA + GL/Vulkan | QPainter raster + `wl_shm` |
| SDL2/3 | Wayland video + GLES/Vulkan | software renderer + `wl_shm` |
| GLFW/EGL | Wayland + EGL | fail explicitly if EGL is unavailable |
| waypipe-rs | linux-dmabuf with IOSurface/AHB transport | SHM/compressed fallback |

## Readiness gates

Start SDL, Qt, GTK, or other toolkit ports only after stock clients prove:

1. libdrm/GBM/KMS with `kmscube` on macOS, iOS, iPadOS, visionOS, and Android.
2. EGL/GLES with `weston-simple-egl` through ANGLE or selected system EGL.
3. Vulkan instance/device/present with `vkcube` where platform policy permits.
4. IOSurface/AHardwareBuffer dmabuf transport without a mandatory CPU copy.
5. A shared software-buffer path with stride- and damage-limited updates.

## Shared software path

```text
Cairo / Qt raster / SDL software / Weston pixman
  → wl_shm or CPU-readable GBM BO
  → one stride- and damage-aware iland CPU present path
  → Apple texture upload or Android Surface upload
```

Pixman remains L0 `wwn-toolchain` substrate because Cairo and Weston consume
it. `wwn-iland` may link pixman helpers but does not own pixman. The soft path
must not become fake GLES, Zink, or an unconditional second full-frame copy.

waypipe may intentionally fall back to SHM/compression when GPU transport is
unavailable, but a GPU-capable session must retain its zero-copy dmabuf path.
tvOS/watchOS deliberately use the software path while still launching their
real native Weston and Niri bundles. They must not acquire Vulkan/OpenGL
artifacts to satisfy toolkit tests.

See [`wwn-iland-graphics-stack.md`](wwn-iland-graphics-stack.md) for the GPU
architecture and [`platform-capability-matrix.md`](platform-capability-matrix.md)
for target exclusions.
