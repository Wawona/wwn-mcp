# Wawona Relay

L3′ product at `github.com/Wawona/Relay`. Flake input name: `wwn-relay`.
This is the only engine Wawona calls for Linux guests and Mode A WASI.

| Kind | What Relay runs |
|------|-----------------|
| `virtual_machine` | Linux / NixOS prebuilts only |
| `container` | OCI unpack, then the same Linux VM backend |
| WASI / `wpm` | Mode A bytecode (`/wasm/v1`) only. No Mode B wasm product |

## Backends

- macOS Apple silicon: Virtualization.framework. Containers via Apple Containerization (OCI on VZ).
- Linux AppImage: KVM via cloud-hypervisor or crosvm. Fail closed without `/dev/kvm`.
- iOS / iPadOS Mode A: Relay static CPU (planned until it boots NixOS).
- iOS / iPadOS Mode B: Mode A CPU plus JIT CPU (planned). No QEMU.
- Android Play: Relay static CPU (planned). No AVF. No proot.
- tvOS / watchOS / visionOS: VM and container kinds forbidden. Wasm still required.

Guest GUI is vsock + waypipe into Wawona (iland). Not Spice, virgl, or virtio-gpu into a second window.
Every Relay VM GUI uses `wwn-iland` userspace DRM/KMS/GBM framebuffer services
and Wawona Wayland. This is mandatory on every target that supports VM machines.
NixOS MicroVM profiles are mandatory Relay machines. Their virtual disks resize
only while stopped and only grow; Relay owns the validation plan and native UI
uses a discrete slider.

Mode A vs Mode B is which binary was installed. Not a Settings toggle.

## Rust + crate2nix

Relay is a **Rust** product. New engine/session/OCI/WASI logic stays in Rust.
C headers and thin ObjC/JNI trampolines are ABI only (`wawona_relay.h`). Do not
grow Swift or C product engines.

Nix packaging must use **crate2nix** so each Cargo crate is its own store
path (granular rebuilds). Pin via L0:

```text
wwn-toolchain inputs.crate2nix
  └─ Relay: crate2nix.follows = "wwn-toolchain/crate2nix"
```

Use `crate2nix.tools.*.generatedCargoNix` (same idea as L4
`dependencies/wawona/rust-backend-c2n.nix`). Do not add new monolithic
`rustPlatform.buildRustPackage` wrappers for the Relay workspace.

Open debt: migrate existing `buildRustPackage` recipes; replace Swift
`wawona-vz-run` with a Rust VZ launcher.

## Hard rejects

- QEMU (system, user, TCG, TCTI, HVF-via-qemu, qemu-*.framework)
- UTM / UTM SE / Spice / CocoaSpice / virgl
- Host Docker, runc-on-host, proot
- New work in wwn-vms, wwn-containers, or wwn-wasm (merged here)
- AVF in Play
- Claiming world's fastest or App Store approval without evidence
- New Relay product logic in Swift/C beyond thin ABI trampolines
- New whole-workspace `buildRustPackage` for Relay (use crate2nix)
C ABI: `wawona_relay.h` (`relay_resolve_backend`, `relay_start`, `relay_stop`, `relay_wayland_endpoint`).

L4 trampoline: `WWNRelay` on Apple. Linux GTK uses `src/linux/relay.rs`.

Canonical: `Relay/README.md`, `wawona-linux-vms-relay-runtime`, skill `wawona-relay`.

## Guest bundle staging

Relay guest manifests are versioned and select only 4 KiB or 16 KiB page
geometry. Before a static mobile session accepts a manifest, it checks artifact
size and streams SHA-256 verification. This validates a bundle only: it is not
evidence of a Linux boot. Relay's Nix source filter includes tracked files, so
new VM modules must be staged before an archive build or the build source will
omit them.

Determinate's native Linux builder may expose a case-insensitive macOS Nix
store through VirtioFS. Relay safely builds there by using a minimal scripted
initrd that omits case-colliding terminfo data and rejects any case-hack path
in the archive. The ext4 builder copies the physical store tree, then renames
`~nix~case~hack~N` directory entries inside the case-sensitive image with
`debugfs`. It never materializes the decoded tree on the host filesystem.
The initrd module set suppresses unused `ext2` and uses the real
`vmw_vsock_virtio_transport` module name, not nonexistent `virtio_vsock`.

The resulting 4 KiB bundle is boot-proven on macOS through the native
Virtualization.framework `wawona-vz-run` launcher. It reaches NixOS stage 2,
automatic `wawona` login, and starts the guest Wayland service. This proves the
artifact and native VZ launcher. Relay Rust `start_vz` owns verified
bundle-relative artifact resolution, persistent writable disk state, process
lifecycle, console capture, readiness, Wayland endpoint, restart, and stop.

APFS `clonefile` preserves the read-only Nix store mode. Relay must add owner
write permission before attaching the cloned rootfs, or Virtualization.framework
rejects the storage device. Guest readiness is the exact
`WAWONA_RELAY_READY=1` marker written to `hvc0` by the Wayland service
`ExecStartPost`; do not scrape ANSI-formatted systemd lines.

Release guest starts require a trusted Ed25519 signature over canonical
manifest JSON. Unsigned manifests require an explicit development-only runtime
resource flag. OCI delivery accepts only validated image blobs and uses the
versioned bounded Relay guest control protocol.

Guest kernels are Linux 7.2 or newer (`linuxPackages_latest` / `linux_latest`).
A real 16 KiB page guest needs `CONFIG_ARM64_16K_PAGES=y`. Do not relabel a
4 KiB Image. On Determinate's native Linux builder, start from the NixOS
kernel config, flip to 16 KiB pages, disable large unused trees plus
`DEBUG_INFO`/DWARF and `NETFILTER`, force `# CONFIG_OF is not set` after
`olddefconfig`, purge `=m` modules, and force Relay virtio/ext4/vsock/ACPI
builtins with `MODULES=y` (initrd reads `modules.builtin`). Slim kernel
`postInstall` (no gdb `constants.py` / full `$dev` source tree). Cap
`NIX_BUILD_CORES`. A fat module tree fills scratch (`No space left` on
`net/dsa` or `vmlinux.o`). A too-thin `allnoconfig` Image reaches VZ with an
empty `hvc0` console. `MODULES=n` fails `modules-shrunk` with `Required
modules: ext4`. The 16 KiB Linux 7.2.3 bundle is VZ-proven the same way as
4 KiB (`WAWONA_RELAY_READY=1` on `hvc0`). Never leave `wayland.sock` under a
`path:.` flake root.
