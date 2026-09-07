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

Mode A vs Mode B is which binary was installed. Not a Settings toggle.

## Hard rejects

- QEMU (system, user, TCG, TCTI, HVF-via-qemu, qemu-*.framework)
- UTM / UTM SE / Spice / CocoaSpice / virgl
- Host Docker, runc-on-host, proot
- New work in wwn-vms, wwn-containers, or wwn-wasm (merged here)
- AVF in Play
- Claiming world's fastest or App Store approval without evidence

C ABI: `wawona_relay.h` (`relay_resolve_backend`, `relay_start`, `relay_stop`, `relay_wayland_endpoint`).

L4 trampoline: `WWNRelay` on Apple. Linux GTK uses `src/linux/relay.rs`.

Canonical: `Relay/README.md`, `wawona-linux-vms-relay-runtime`, skill `wawona-relay`.
