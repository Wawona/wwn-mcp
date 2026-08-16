# Wawona repository DAG — authoritative L0–L4 layering

Wawona repositories form an acyclic dependency graph. Never invert it.

```text
L0  wwn-toolchain — cross-builders and substrate only:
    cairo, pango, pixman, fontconfig, freetype, harfbuzz, libwayland, …
    Depends on no wwn-* repository.
L1  wwn-iland — complete graphics stack:
    iland Mode A/B, DRM/KMS/GBM/EGL, ANGLE, SwiftShader, MoltenVK,
    macOS-only KosmicKrisp, and Android Vulkan ICD hooks.
    Depends on wwn-toolchain only.
L2  wwn-kmscube — graphics acceptance clients. Depends on toolchain + iland.
L3  wwn-weston / wwn-niri — compositors. Depends on toolchain + iland + kmscube
    (weston); niri merges toolchain (+ iland when GPU requires it).
L3' wwn-waypipe / wwn-anowaW / wwn-vms / wwn-containers / wwn-ssh / wwn-wasm —
    toolchain; merge iland only when GPU support requires it.
L4  Wawona — product integration. Merges lower fragments and is never their input.
```

Hard rules:

1. Never add any `wwn-*` flake input to `wwn-toolchain`.
2. Never make `wwn-iland` depend on weston, kmscube, waypipe, or Wawona.
3. Registry fragments merge upward only.
4. `extraArgs.ilandSrc` in weston is source injection, not an upward flake edge.
5. `wwn-kmscube -> wwn-weston` is forbidden.
6. ANGLE, SwiftShader, MoltenVK, and macOS-only KosmicKrisp belong to
   `wwn-iland`. Cairo/pango/pixman/libwayland stay in `wwn-toolchain`.

Canonical source: `Wawona/docs/wwn-repo-dag.md`.
Graphics: [`wwn-iland-graphics-stack.md`](wwn-iland-graphics-stack.md).
Catalog: [`wwn-repos-catalog.md`](wwn-repos-catalog.md).
