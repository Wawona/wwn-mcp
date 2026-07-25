# wwn-iland graphics stack

Indexed mirror of the architecture and acceptance contract in
`Wawona/docs/iland-graphics-stack.md`. Repository ownership is defined by
[`wwn-repo-dag.md`](wwn-repo-dag.md), and privilege/bundle policy by
[`iland-mode-a-b-desktop.md`](iland-mode-a-b-desktop.md).

## Architecture and ownership

`wwn-iland` is the L1 graphics layer. Stock clients keep standard libdrm, GBM,
EGL, Vulkan, and Wayland interfaces:

```text
Wayland client or nested compositor
  ├─ EGL/GLES ──► ANGLE ──► Metal or Android GPU
  ├─ Vulkan ────► one selected ICD ──► Metal or Android GPU
  └─ libdrm/GBM/KMS ──► iland virtual device
                         ├─ Apple: IOSurface BO/FB ──► CAMetalLayer
                         └─ Android: AHardwareBuffer BO/FB ──► Surface
```

IOSurface and AHardwareBuffer back GBM buffer objects and KMS framebuffers;
they do not replace GBM. The virtual device must provide the connector,
encoder, CRTC, plane, property, framebuffer, modeset, and page-flip behavior
used by accepted stock clients.

`wwn-iland.registryFragment` is the sole registry owner of ANGLE, SwiftShader,
MoltenVK, and KosmicKrisp. Cairo, pango, pixman,
libwayland, and other text/2D/toolkit substrate remain in L0 `wwn-toolchain`.
Wawona consumes solved L1 registry entries rather than instantiating
`pkgs.angle`, `pkgs.swiftshader`, or `pkgs.moltenvk` directly.

KosmicKrisp is **macOS-only**. The pinned upstream Mesa driver documentation
explicitly says iOS is not supported. iOS/iPadOS/visionOS therefore use the
pinned public-API MoltenVK static slices; KosmicKrisp mobile variants must stay
fail-loud until upstream supports those targets.

## Minimal translation paths

Use one translation hop per graphics API:

```text
macOS:
  GLES/OpenGL → EGL → ANGLE(Metal) → IOSurface/Metal present
  Vulkan      → loader → MoltenVK OR KosmicKrisp → Metal present
iOS / iPadOS / visionOS:
  GLES        → EGL → ANGLE(Metal) → IOSurface/Metal present
  Vulkan      → loader → MoltenVK → Metal present
Android:
  GLES        → EGL → ANGLE OR system GLES → Surface present
  Vulkan      → loader → system OR SwiftShader
tvOS / watchOS:
  software/pixman + wl_shm only
```

Do not stack GLES through Zink and Vulkan merely to reach Metal. virgl,
gfxstream, and Venus are VM paths, not Mode A presentation. Select exactly one
Vulkan ICD in a process. GPU-capable targets use a GPU compositor renderer by
default; pixman is an explicit fallback.

The virtual DRM/KMS/GBM implementation is runtime-only userland emulation.
Wawona never opens real `/dev/dri` or `/dev/kgsl` nodes, forwards real
DRM/KMS/KGSL ioctls, ships kernel code, or patches a kernel. Direct
Turnip/KGSL is excluded; system Vulkan/Metal and SwiftShader remain valid OS
runtime interfaces.

## Resolving the Vulkan provider

Apple mobile links MoltenVK statically, so in-process Vulkan clients call `vk*`
directly. macOS instead selects MoltenVK or KosmicKrisp at runtime and bundles
both as ICD dylibs in `Contents/Frameworks` with no Vulkan loader beside them,
so a client that links `vk*` directly fails to resolve. macOS and Android
clients therefore load their provider through a dispatch table:

| Host | Env var | Default |
|------|---------|---------|
| macOS | `WWN_VULKAN_LIBRARY` (bundled ICD dylib for the selected driver) | `libMoltenVK.dylib` |
| Android | `WWN_SWIFTSHADER_LIBRARY` when SwiftShader is selected | system `libvulkan.so` |

`WWNSettings_ApplyGraphicsDriverSelection` sets these. Mesa-derived ICDs such as
KosmicKrisp export only `vk_icdGetInstanceProcAddr`, so loaders must fall back
to that name. `VK_DRIVER_FILES`/`VK_ICD_FILENAMES` still point at the bundled
manifests for consumers that do run a loader (waypipe), and their absence
downgrades waypipe to `--no-gpu` SHM transport rather than producing empty
frames.

## Platform policy

- macOS, iOS, iPadOS, and visionOS use IOSurface-backed Mode A.
- Android uses AHardwareBuffer/Surface-backed Mode A, with an optional separate
  root/Shizuku power path.
- tvOS and watchOS ship no VM, container, Vulkan, OpenGL, ANGLE, MoltenVK,
  Vulkan ICD, or IOKit graphics artifacts.
- Every Apple target, including tvOS/watchOS, and Android still ships the real
  native Weston and Niri entry points. tvOS/watchOS use the constrained
  software/non-GL fallback; fake compositor entry points are never acceptable.

## Acceptance

Compilation proves wiring, not runtime correctness. Product-shaped acceptance
requires bundle audits, real compositor entry-point checks, stock `kmscube`,
`weston-simple-egl`, and `vkcube` where allowed, present metadata/runtime logs,
and simulator/device evidence. DRM open/resources and KMS
modeset/page-flip/present must be graded separately.

Toolkit and software-fallback entry criteria are mirrored in
[`toolkit-readiness-soft-shm.md`](toolkit-readiness-soft-shm.md). The complete
target contract is in
[`platform-capability-matrix.md`](platform-capability-matrix.md).
