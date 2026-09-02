# iOS / iPadOS install channels (Mode A vs Mode B)

Indexed mirror of `Wawona/docs/agent-rules/wawona-ios-mode-b-channels.md` and
`Wawona/docs/mode-a-b.md`. Site: wawona.io `/docs/mode-a-b/`.

**Hard fact:** TrollStore is **not** JIT-only. A TrollStore `.tipa` is Mode B
for **JIT + IOMobileFramebuffer + Desktop/LockScreen**. Swinging Bridge is
**Sileo-only**.

## Three channels (never collapse into one)

| Channel | How users get it | Privilege class |
|---|---|---|
| **App Store / TestFlight** | ASC | **Mode A only** |
| **TrollStore sideload** | Website `.tipa` + `ldid` entitlements | **Mode B**: JIT + IOMobileFramebuffer + Desktop/LockScreen |
| **Sileo (`repo.wawona.io`)** | Jailbreak + Mode B IPA / `.deb` + tweaks | **Full Mode B** (above + Swinging Bridge + host APT) |

App Store copy and binaries must **never** mention TrollStore, Sileo, jailbreak,
JIT, or framebuffer SPI. Website + `repo.wawona.io` may.

## Channel matrix

| Channel | JIT | IOMobileFramebuffer / own-display | Desktop + LockScreen | Swinging Bridge |
|---|---|---|---|---|
| App Store / TestFlight | No | No | No | No |
| TrollStore (`ldid`) | Yes | Yes | Yes | No |
| Sileo (`repo.wawona.io`) | Yes | Yes | Yes | Yes + host APT |

### 1. App Store / TestFlight (Mode A)

- VMs: **QEMU-TCTI / TCG interpreter only** (UTM SE model). No `MAP_JIT`, no HVF.
- Containers: OCI + container-in-VM on that **jitless** engine.
- Wasm: WASI Runtime **without** JIT (bytecode as data via `wpm` / `/wasm/`).
- Desktop / LockScreen: **forbidden** in-app.
- Wawona Swinging Bridge: **forbidden** in store IPA.
- Shell: sandboxed `wwn-zsh` hatch.
- Present: public Metal / `CAMetalLayer` only (Mode A in-window).

### 2. TrollStore sideload (`ldid` Mode B)

TrollStore installs a Mode B IPA signed with `ldid`. Entitlements may grant JIT
**and** framebuffer SPI **and** Desktop / LockScreen on an own-display path.

- VMs: QEMU/UTM **with JIT**.
- Containers: container-in-VM **with JIT**.
- Wasm: Runtime may enable **Wasm JIT** when the entitlement is present.
- **Desktop / LockScreen**: yes, via IOMobileFramebuffer own-display (in-app
  greeter). Not SpringBoard injection (no ElleKit on TrollStore).
- Swinging Bridge Mode B: **no**. Needs jailbreak + Sileo.
- Ship name: `Wawona-{calver}-iOS-arm64.tipa`. Never through Ship: beta / TestFlight.

### 3. Sileo from `repo.wawona.io` (full Mode B, jailbreak)

Jailbroken device + Sileo. Mode B IPA / `.deb` and tweaks ship **out of the box**:

- Same JIT + IOMobileFramebuffer Desktop engines as TrollStore.
- **Desktop / LockScreen** also via SpringBoard tweaks (ElleKit on rootless).
- **Wawona Swinging Bridge Mode B** (UIKit apps as Wayland clients).
- Unsandboxed shell + host APT (`/jailbreak/` channel).
- Rootless (`iphoneos-arm64`, `/var/jb`) and rootful (`iphoneos-arm`, `/`) are
  **separate** packages. Never one `.deb` for both.

`repo.wawona.io` publishes Mode B packages under `/jailbreak/` only. Store CI
must fail if this flavor is linked into Mode A.

## QEMU on iOS

```text
Mode A (store)     →  -accel tcg , jitless / TCTI (UTM SE). Interpreter ceiling.
TrollStore / Sileo →  QEMU/UTM + JIT (Mode B scheme / WWN_MODE_B). Never in store link.
```

Shared guest/OCI/Machines UI. Divergent engine compile flavor. Never a store
binary with a runtime "enable JIT" or "enable framebuffer" toggle.

## Facts agents get wrong

- **Wrong:** TrollStore is JIT-only.
- **Right:** TrollStore `.tipa` = JIT + IOMFB + Desktop/LockScreen. No SB.
- **Wrong:** iOS Desktop is Sileo / `repo.wawona.io` only.
- **Right:** Desktop is TrollStore (IOMFB in-app) **and** Sileo (IOMFB and/or
  ElleKit SpringBoard). App Store still **forbidden**.
- **Wrong:** Swinging Bridge ships in the TrollStore `.tipa`.
- **Right:** Swinging Bridge is **Sileo-only** on iOS/iPadOS.

## Hard rejects

- JIT / `MAP_JIT` / Hypervisor / IOMobileFramebuffer SPI in App Store / TestFlight IPA
- TrollStore/Sileo/jailbreak strings in store UI
- Treating TrollStore as JIT-only
- Treating TrollStore as full Sileo (Swinging Bridge / host APT / ElleKit)
- Linking ElleKit into store IPA or TrollStore `.tipa`
- One binary with a runtime Mode B toggle that ships to ASC
- Conflating macOS iland Desktop Mode B dylib with iOS Mode B IPA

## Related

[`dma-buf-zero-copy.md`](dma-buf-zero-copy.md) (IOMFB present sink),
[`iland-mode-a-b-desktop.md`](iland-mode-a-b-desktop.md) (macOS dylib),
[`platform-capability-matrix.md`](platform-capability-matrix.md).
