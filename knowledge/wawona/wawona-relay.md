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
- iOS / iPadOS Mode A: Relay static CPU (planned until it boots NixOS). Wasm is Pulley through OS 26. OS 27+ Mode A uses Wasmer WASIX in a hidden WKWebView (WebKit JIT and JSPI) when WasmerSDK is linked (`WWN_WASMER_IOS27`). Otherwise Pulley. Not Cranelift. Not MAP_JIT. tvOS, watchOS, and visionOS stay Pulley. macOS and Linux stay Wasmtime Cranelift.
- iOS / iPadOS Mode B: Mode A CPU plus JIT CPU (planned). No QEMU.
- Android Play: Relay static CPU (planned). No AVF. No proot.
- tvOS / watchOS / visionOS: VM and container kinds forbidden. Wasm remains required.

Guest GUI is vsock + waypipe into Wawona (iland). Not Spice, virgl, or virtio-gpu into a second window.
Every Relay VM GUI uses `wwn-iland` userspace DRM/KMS/GBM framebuffer services
and Wawona Wayland. This is mandatory on every target that supports VM machines.
NixOS MicroVM profiles are mandatory Relay machines. Their virtual disks resize
only while stopped and only grow; Relay owns the validation plan and native UI
uses a discrete slider.

## macOS MicroVM dogfood (vfkit, not product engine)

Linux-first breadth on the Mac without a native port of every app: microvm.nix
+ vfkit boots a NixOS guest; vsock port 1024 + waypipe forwards a Wayland
*client* (default foot) into host Wawona. Guest module:
`Relay/import/vms/dependencies/vms/microvm-guest.nix` (`sessionClient`,
`WAWONA_RELAY_READY=1`). Preferred host command:
`nix run .#wawona-microvm-session` (supervises bridge + microvm). Machines
`virtual_machine` Start on macOS uses `WWNVirtualMachineRunner` for that
session. Smoke: `Wawona/scripts/microvm-waypipe-session-smoke.sh`. Prose:
`Wawona/docs/2026-nixos-vm-bridge.md`. Product engine remains Relay
(VZ/StaticCpu/KVM). Never QEMU/UTM Start. Never treat vfkit as the iOS path.

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

## Formal verification and StaticCpu ownership

Relay VM Rust is gated by Kani 0.68.0 plus Verus
0.2026.09.27.3cf1832. Kani calls production helpers for page-arena rounding,
virtio block span validation, and virtio MMIO queue-address assembly. Verus
proves matching unbounded page-layout and disk-span invariants. Both pass before
Cargo executes Relay VM code; source changes invalidate proof stamp. Skill
`wawona-formal-verification`.

Virtio-console RX buffers stay device-owned until host input exists. Completing
empty buffers causes Linux recycle/notify IRQ storm. Virtio block supports
scatter/gather descriptors crossing sector boundaries after full validation.
LDTR/STTR translation failures enter EL1 data-abort vector with ESR_EL1 and
FAR_EL1 context rather than killing StaticCpu.
StaticCpu stage-1 data walks enforce terminal PTE AP permissions. EL0 writes to
AP=11 must raise a permission data abort so Linux can perform fork COW; writing
host memory directly corrupts shared userspace stacks.

StaticCpu boot diagnosis uses `relay-vm` example `static_differential` instead
of speculative opcode iteration. Versioned JSONL checkpoints capture GPR/SIMD,
EL1 exception and timer state, and hashes of guest pages written since the
prior checkpoint. Each record has a cumulative SHA-256 chain, so the first
architectural mismatch against an outside-product native AArch64 or QEMU trace
can be binary-searched. Narrow to one instruction and add a minimized test.
QEMU and its plugins remain forbidden in every Relay or Wawona product artifact.
Contract: `Relay/docs/static-cpu-differential.md`.

## Hard rejects

- QEMU (system, user, TCG, TCTI, HVF-via-qemu, qemu-*.framework)
- UTM / UTM SE / Spice / CocoaSpice / virgl
- Host Docker, runc-on-host, proot
- New work in wwn-vms, wwn-containers, or wwn-wasm (retired; product is this repo). Do not recreate those GitHub repos. Local clones may remain. QEMU and UTM trees in them are not Relay backends. macOS containers are `Relay/import/containers` (Apple Containerization, `wwn-containerd`, waypipe vsock).
- AVF in Play
- Claiming world's fastest or App Store approval without evidence
- New Relay product logic in Swift/C beyond thin ABI trampolines
- New whole-workspace `buildRustPackage` for Relay (use crate2nix)
C ABI: `wawona_relay.h` (`relay_resolve_backend`, `relay_start`, `relay_stop`, `relay_wayland_endpoint`).

L4 trampoline: `WWNRelay` on Apple. Linux GTK uses `src/linux/relay.rs`.

Canonical: `Relay/README.md`, `Relay/docs/ios27-wasmer-wasix.md`, `Relay/docs/retired-sibling-repos.md`, `wawona-linux-vms-relay-runtime`, skill `wawona-relay`.

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

Direct Image boot never passes through the NixOS bootloader. Generate the guest
manifest command line from `cfg.boot.kernelParams` instead of maintaining a
second hard-coded string in `guest-artifacts.nix`. StaticCpu diagnosis uses
`nokaslr`, `earlycon=pl011,mmio32,0x09000000`, and both virtual and translated
physical PC. A relocatable ARM64 Image loads at a 2 MiB aligned base plus its
header `text_offset`; Linux 7.2 reports zero, so hard-coding `0x80000` makes the
post-MMU physical mapping 512 KiB early. Decode `LDAR` and `STLR` before broad
exclusive masks. Treating `STLRB` as `STXR` drops spinlock unlocks and deadlocks
`console_sem`. With correct placement and release stores, StaticCpu reaches
PL011 output, PSCI 0.2 discovery, memory zones, and per-CPU allocation.
Keep guest RAM at the conventional `0x40000000` base so GIC, PL011, and
virtio-mmio remain outside Linux RAM. Place the initrd after the ARM64 header's
`image_size`, not after the shorter Image file, or kernel BSS clearing corrupts
the archive. StaticCpu timer expiry must surface as the DT-selected GIC PPI
(virtual 27, physical 30), not as a private interpreter interrupt. For the
boot-proof guest use `boot.initrd.compressor = "cat"`: plain `newc` cpio keeps
optional zstd decoder coverage out of the stage-1 critical path.

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


Cross-page scalar/SIMD memory accesses must translate every virtual fragment:
adjacent virtual pages may map discontiguous physical frames. Validate both
fragments before split stores so second-page permissions fault without partial
writes. Native SIMD tests cover every split for 4/16 KiB mappings.

16 KiB Linux needs TGran16=1 (TGran4=0, TGran64=15) and TxSZ-derived starting
levels per TTBR. Measured TCR_EL1=0x045000757551b510 has T0SZ=16 (four-level
48-bit low half), T1SZ=17 (three-level 47-bit high half). Mask canonical high
bits before initial lookup. Hardcoded four-level walks cause PC=0x200 loops.

Differential traces are untrusted evidence: recompute state/chain hashes and
reject empty/malformed/reordered checkpoints. `instructions` counts interpreter
steps, including synchronous exception entries; it is not retirement. No
full-system reference adapter ships yet. Self-replay proves determinism only.
`static_smoke` must reject loader errors, panics and interpreter failures even
while a thread stays alive. Acceptance: `Relay/docs/static-cpu-acceptance.md`.

`cpu/native_reference.rs` runs fixed, statically assembled AArch64 instructions;
no guest bytes execute and no executable memory is generated. FP tests restore
host FPCR/FPSR/NZCV and compare guest results plus exceptions. Coverage includes:
UMOV/SMOV, DUP, INS, MOVI/MVNI/ORR/BIC/FMOV immediates, precision and integer FP
conversions, scalar FP arithmetic/comparisons, vector ADD/SUB/comparisons,
pairwise reductions, bitwise/unary byte operations, widening shifts, EXT, XTN.
Modified immediates cover all 16,128 valid encodings with three destination
patterns; scalar FP immediates cover 512 encodings; INS covers 370 lane forms.
Use non-inlined const-generic helpers for large corpora: macro-expanded debug
stack frames overflowed in the initial exhaustive immediate test.

Software FP uses pinned pure-Rust rustc_apfloat 0.2.3 with ARM-specific NaN
priority, FZ/DN, rounding and status. APFloat omits OVERFLOW on directed
saturation: native tests caught it; exact S/D→Quad widening and wider-range
evaluation recover ARM's flag. Native tests also caught old host-float casts
and compares losing FPSR flags. Never restore those shortcuts. Arithmetic
samples include normal/subnormal rounding boundaries. Formal obligations cover
named invariants, not the entire FP library or CPU.

Measured boot: 4 KiB direct-root reaches NixOS Stage 2 activation; 16 KiB
PL011/nokaslr diagnostic reaches real systemd-udevd startup. Neither establishes
systemd target, authenticated readiness or Wayland. Latest full suite at this
checkpoint: 166 VM tests, 3 smoke tests, 11 Kani harnesses, 8 Verus obligations.
iOS aarch64 cargo check passes; portable arithmetic and reserved-encoding
regressions pass Miri. Native assembly cases are excluded under Miri/non-AArch64.

## 2026-09-30 completion audit and fetch boundary

Plan: `Relay/docs/static-cpu-completion-plan.md`. Keep Relay slim: one Rust
engine, shared memory/virtqueue mechanisms, thin ABI glue. Proof tools, native
references, fuzz corpora and diagnostics stay outside the product artifact.
One of nine boot gates is not 11% engineering completion.

Instruction fetch used EL1 read translation even at EL0. It now shares the
production walker with explicit fetch/read/write access, leaf/table XN, table
AP, WXN and EL1 rejection of EL0-writable executable mappings. Typed walk faults
preserve syndrome levels; bad configuration is not a fabricated guest abort.
Shared data/instruction abort entry saves EL1 SP0 correctly. Kani permission
harnesses check production helpers; the Verus Boolean model is not a full MMU
refinement proof. AF, descriptor legality and canonical-address coverage remain.

Full-system reference adapter still absent. GIC is simplified; StaticCpu bus
still lacks rng/net/vsock/fs. Current vsock queue is not guest virtio-vsock and
only bounds individual packets. Local proof stamp is not release attestation.
OCI digest checks exist, but bounded extraction, symlink-safe confinement,
immutable validation-to-use, publisher trust and identity handling need work.
Do not count native ARM corpus as run on x86 CI. New ARM64 workflow checks corpus
presence; expanded Miri script covers portable fetch/FP/block/reserved tests.

Native tests caught FRINT{N,P,M,Z,A,X,I} missing; all 14 scalar S/D forms now
match results/status under all guest controls. Only FRINTX adds IXC. Scalar
integer CMEQ/CMGT/CMGE/CMHI/CMHS/CMTST and zero forms reuse vector lane logic.
Measured word 0x5ee09bff is integer CMEQ D31,D31,#0, not FP compare.

Direct-root guest skipped stage 1 prerequisites: /proc/cmdline and /dev/fd
failed in Stage 2. Bootstrap now sources NixOS `earlyMountScript` before init
and creates fd/stdin/stdout/stderr links. Rebuild artifacts and verify boot;
editing the recipe does not change existing result symlinks. Old 16 KiB idle
PCs resolve to timer/nohz/context-tracking functions, not proof of readiness.


### 2026-09-30 shared SIMD families and AF faults

Both rebuilt direct-root 4 KiB and 16 KiB guests finish activation, set up
`/etc`, and start real systemd PID 1. Target readiness still unproved.
SADDW 0x0ebe13ff triggered all 48 signed/unsigned long/wide add/sub forms.
LD1 0x4c40a825 triggered 192 consecutive LD1/ST1 native forms. SHL
0x4f2c5621 triggered all 11 non-saturating immediate-shift families, with
264 native boundary forms. LD1 lane 0x0d40041f triggered 720 lane and 96
replicate forms. Static native asm only; never execute supplied instruction
bytes. Shared 64-byte RAM path preflights split writes; register wrap and
all page splits have portable regressions. Lane loads preserve all other
bits even with Q=0; replicate Q=0 clears the upper half.

HAFDBS remains unadvertised. AF=0 leaf causes access-flag fault before
permissions, with actual walk level, without mutating descriptor or target
memory. Fixtures must explicitly set AF when testing unrelated permissions.
Miri table tests use explicit host page size: macOS getpagesize FFI is not
supported by Miri, not a demonstrated product UB.

Kani shift kernel covers valid width/shift domains, lane bounds and exact
zero/full-width edge identities, not full ARM decoder equivalence. Fragment
proof bounds now 1..=64 bytes. Source stamp includes gate/build configuration;
verify-formal compares pre/post hashes and refuses a changed tree. Runner
stub tests validate gate behavior, never stand in for actual Kani/Verus.

### EL1 hardware reference and boot wait (2026-09-30)

Relay `verification/el1` provides a standalone macOS Hypervisor.framework fixed
micro-guest oracle; never link it into the app. 29 cases on each 4/16 KiB granule
produce 58 recorded observations, compared portably against StaticCpu (also Miri).
Native evidence drove fixes for SVC ESR.IL, EL1 SP0 vector/stack entry, IRQ DAIF,
invalid level-3 block descriptors, ERET SPSel/stack-bank restoration and timer
ISTATUS independent of IMASK. ERET must validate mode before changing state.
Fresh hardware comparison: `scripts/verify-el1-reference.sh`; fixture updates
invalidate proof stamps and require formal gates again. Each case uses a fresh
VM to avoid stale translations after host-side page-table changes. This bounded
oracle does not establish full Linux or ISA equivalence.

Debug 4 KiB systemd boot waits after hostname/timezone setup. Hung-task output
shows PID1 closing inotify in fsnotify_wait_marks_destroyed and its cleanup worker
waiting in synchronize_srcu. Root cause unresolved; do not call this readiness.

### SRCU needs self-SGIs even with one vCPU (2026-09-30)

A one-vCPU Linux guest still uses GICv2 software interrupts for irq_work.
The exact 7.2.3 guest's gic_ipi_send_mask writes GICD_SGIR at distributor+0xf00
with TargetListFilter=2 for self delivery. Discarding distributor writes stranded
SRCU grace-period work. Relay now routes SGIR explicit CPU-0 and self targets;
other-CPU-only/reserved filters do not deliver. Kani covers bit extraction and
routing; Verus covers the routing model, not full GIC state/liveness.

The optional `kernel-probe` feature and `static_kernel_probe` example provide
bounded RAM-only observations without device-read or fault side effects. Default
app builds exclude them. See Relay/docs/static-cpu-differential.md. Before the
SGIR fix, a 3-billion-instruction trace saw a grace-period request but no worker;
afterward srcu_irq_work/process_srcu/srcu_invoke_callbacks first execute at
761463790/761468973/761470469 instructions. This proves that callback path resumed,
not whole guest readiness. Never infer lost IRQs from IAR=1023 counts alone.

### Measured reductions and table lookup (2026-09-30)

After SGIR repair, both page sizes passed the SRCU wait and reached UMAXV
`0x2e30a800`, then in-place TBL `0x4e1c03ff`. Shared integer reductions cover
35 native forms (ADDV, S/UADDLV, S/UMAXV, S/UMINV). The Kani contract checks
exact sums modulo output width and min/max membership/order with an independent
i128 interpretation for arbitrary valid vector inputs, plus arithmetic safety.
TBL/TBX shares one 1..4-register byte lookup (16 native forms); capture source,
indices and old destination before writing, wrap V31 to V0, and clear Q0 upper
bits even for TBX. Kani proves exact byte selection and out-of-range behavior;
native cases cover wrapping/aliasing, and Miri checks portable boundaries.
These are lane-kernel proofs, not full decoder or whole-ISA equivalence.

### Saturation and scalar ADDP (2026-09-30)

Service startup exposed scalar ADDP `0x5ef1bb3f` (16 KiB) and UQSUB
`0x6efd2f9c` (4 KiB). ADDP Dd,Vn.2D uses modulo-u64 addition and clears upper
bits. SQADD/UQADD/SQSUB/UQSUB share one i128 clamping kernel across 44 native
scalar/vector forms. FPSR.QC is sticky and set when any active lane saturates;
other flags stay unchanged. Kani proves exact clamping/indication for all valid
lane inputs. Do not treat scalar Q=0 patterns as reserved saturation encodings:
they overlap scalar FP encodings (including FCSEL). Match the correct classes.

### Interleaved transfers and high-lane FMOV (2026-09-30)

Measured service-stage gaps: 4 KiB `0x4c40843e` LD2 V30.8H/V31.8H;
16 KiB `0x9eaf0060` FMOV V0.D[1],X3. LD/ST2..4 share the existing
64-byte transfer/preflight path: byte mapping interleaves element-sized chunks,
with register wrap and all writeback forms. Added 126 fixed native forms; every
page split and fault-atomic stores cover both granules. Kani proves byte mapping
bounded and invertible (19 total harnesses; 10 Verus checks). High-lane FMOV
preserves low 64 bits, uses XZR semantics, and has native/portable comparisons.
No new runtime dependencies. VM tests: 211; workspace: 261. iOS 11 release
staticlib builds. Whole target/readiness acceptance still requires guest boots
and device wiring; these scoped tests are not whole-CPU proofs.

### Console ownership and service diagnostics (2026-09-30)

Console RX kicks used to be overwritten by TX; receive exhaustion also returned
empty buffers. Keep a notification bit per virtqueue, retain waiting RX, drain
TX independently, and clear a kick only after its ring is empty. Validate all
chain directions/RAM spans before payload effects; fixed 4 KiB scratch removes
guest-length allocations. Used length is device-written bytes (TX=0). Bounded
output keeps its tail without temporarily allocating the full incoming span.
Portable tests cover delayed RX/TX, malformed second descriptors, u32::MAX
lengths and chunk boundaries. Gates: 264 workspace tests, 19 Kani, 10 Verus,
20 Miri suites, Clippy correctness/suspicious and iOS 11 release staticlib pass.
Miri cannot call Darwin getpagesize: portable tests use allocate_on_host with an
explicit host granule; do not weaken production host-page detection.

Both granules stayed live for 480 wall seconds after interleaved/FMOV fixes.
No required-target/readiness claim follows. For service errors, temporary
development manifests add systemd.default_standard_output=journal+console,
systemd.default_standard_error=journal+console and
systemd.journald.forward_to_console=1. This revealed 16 KiB firewall failure:
iptables: Failed to initialize nft: Protocol not supported. Its kernel recipe
explicitly disabled NETFILTER. Retain the firewall and build its dependencies;
IP_NF_MATCH_RPFILTER/IP6_NF_MATCH_RPFILTER also depend on their IP_NF_IPTABLES/
IP6_NF_IPTABLES menus, even with NFT_COMPAT. Kernel build/boot validation pending.

## 2026-09-30 guest reference and identity corrections

OCI image config uses `User` (legacy `user` accepted). Explicit numeric UID:GID
must survive conversion; reject malformed/reserved IDs, names and UID-only
identities until confined account lookup exists. Missing Entrypoint/Cmd is an
error, never an invented readiness shell. Validate process config before
clearing an existing materialization destination.

The same 4 KiB kernel/rootfs starts nsncd under native VZ; StaticCpu emits
SIGSEGV at address -48. This is an unresolved interpreter/guest divergence,
not proof of its cause. A later StaticCpu stop measured UMAX V29.4S,V29.4S,V31.4S;
shared elementwise/pairwise min/max now has native forms and an exact lane lemma.

Native reference exposed guest Wayland unit permission errors: an unprivileged
service cannot mkdir /run/user/1000 or redirect directly to /dev/hvc0. Use an
owned RuntimeDirectory and journal+console. Type=exec plus MAINPID liveness
prevents the observed marker after failed exec. That marker remains only a
transport-start hint, not authenticated readiness or a frame assertion.
Native VZ with the repaired 4 KiB unit starts the session successfully. VZ's
ACPI/PCI topology differs from StaticCpu MMIO; this is a coarse guest-health
reference, not whole-system conformance. A direct-root image can be referenced
with an empty newc initrd and hvc0 console; omit the StaticCpu PL011 earlycon.

## 2026-09-30 leading counts and nested display

Measured vector CLZ 0x6ea04b7b now shares one CLZ/CLS lane implementation.
All 12 legal vector forms match fixed native assembly; alias/zero/sign-boundary
and reserved-width tests pass. Kani proves counted prefix and first differing
bit for arbitrary lanes. Gates now pass 270 workspace tests (218 VM), 21 Kani,
10 Verus, 23 Miri suites, Clippy correctness/suspicious and iOS release build.
These counts are scoped evidence, never a whole-product completion percentage.

The mobile Cage session must use WLR_BACKENDS=wayland and WLR_WL_OUTPUTS=1
when launched through waypipe. Headless draws into a guest-only output and
cannot provide the parent surface for Wawona. Recipe corrected; full host-frame
validation remains open. Keep nested guest configuration distinct from native
bundled compositor backend preferences.

## 2026-09-30 nsncd stack fault and waypipe direction

The signal probe captured nsncd SIGSEGV at user PC 0xb787459bb824, with X29=0.
Pinned nsncd-1.5.2 (wyariv... store path) maps it to ELF offset 0x3b824:
STUR Q0,[X29,#-48], in slog_async AsyncCoreBuilder::build_no_guard. The preceding
callee at 0x350e4 aligns its stack using AND SP,X9,#-128 (0x9279e13f).
StaticCpu's logical-immediate decoder discarded Rd=31 for all operations;
AND/ORR/EOR instead target SP/WSP, while ANDS targets ZR. Failure to allocate
that stack frame overwrote saved caller registers. Route only non-flag-setting
logical immediates through set_x_or_sp. Keep Rn=31 as ZR in every form.
The compact frame regression reproduces this save/align/write/restore sequence.
A later full boot confirms nsncd startup; desktop acceptance remains open.

Native VZ with nested Cage now fails honestly without a host compositor,
instead of running invisibly headless. Pinned waypipe 0.11.0 manpage says the
server connects to the client; guest --vsock -s1024 server dials host CID2.
Relay start_vz currently supplies --vsock-connect/--listen-unix, also dialing
the guest. Correct listener/forward direction and host waypipe-client startup
ordering together. Do not restore headless or accept a startup marker as a frame.

## 2026-09-30 OCI archive regression and settings gap

A temporary-fixture regression reproduced outside-root writes through an
existing layer symlink. Use real-directory ancestor checks for archive paths
and opaque whiteouts, plus tar Entry::unpack_in for confined extraction and
hardlink validation. Apply whiteouts in a first streaming pass before additions:
OCI whiteouts only hide lower-layer resources. Reject empty/dot basenames.
Tests cover escape writes/deletions, hardlinks, dangling symlink replacement,
and late whiteouts preserving same-layer files. No new dependency or expanded
layer buffer. Concurrent filesystem replacement and atomic publication remain
unproven; internal symlink ancestors currently reject conservatively.

The active shared Sources/WawonaUI settings already contain memory/storage
sliders and guest-page selection; WWNVirtualMachineEditorSection is legacy.
`Sources/WawonaApple/Runners/RelayRunner.swift` (`WWNRelay`) sends memory_mb/disk_gib/max_disk_gib. RelaySpec now retains these;
StaticCpu and VZ apply RAM and disk limits. App-owned machine disks publish
without replacement, hold an exclusive advisory lock, grow only, and flush
writes before virtio completion. This is not a crash-consistency or race proof.
Shared UI labels storage, prevents configured-size shrink, and shows automatic
connection instead of a nonfunctional port field. Swift package WawonaUI builds;
actual iOS app/device settings validation remains open. Guest root autoResize
is already on. There is no iOS 11 UI path. Coverage starts at iOS 13.

## 2026-09-30 conditional FP and persistence validation

Full 4 KiB boot after the SP fix starts nsncd successfully. Next measured stop
is FCCMP D0,D31,#0,EQ (0x1e7f0400). FCCMP/FCCMPE share the integer-bit FP
comparison helper; false conditions install immediate NZCV without FP effects.
Native tests across all 16 conditions caught scalar integer ADD/SUB's broad
Q=0 mask overlapping FCCMP HI. Require Q=1 for scalar integer forms.
Storage validation adds production-helper Kani and a separate Verus extent
lemma; neither proves host filesystem durability. Gates pass: 281 workspace
tests (225 VM), 22 Kani, 11 Verus, 26 Miri suites, Clippy and iOS release.
16 KiB kernel/firewall guest build completed; nested-session image refreshed.
Host vsock direction/readiness and full desktop frame remain open.


## Scalar fused arithmetic and service traces (2026-10-01)

Fresh 16 KiB boot failed after 9,859,432,448 interpreter steps at 0x1f4e0000
(FMADD D0,D0,D14,D0). A failing aliased-source regression preceded repair.
FMADD/FMSUB/FNMADD/FNMSUB S/D now share rustc_apfloat fused multiply-add
with the existing software FP kernel: single rounding, input sign changes,
addend-first NaN priority, FZ/DN and sticky FPSR. No host FP state or runtime
dependency was added. Eight fixed native forms compare 812,032 cases across
RMode/FZ/DN, signs, zeros, subnormals, NaNs, infinity and random operands.
Portable cancellation tests distinguish fused from multiply-then-add results.
Miri passes the shared FP helper and exact guest instruction regression. Use
explicit GuestMemory::allocate_on_host in portable CPU fixtures; macOS
getpagesize is outside Miri's foreign-function support.

Fresh complete workspace/all-targets run: 287 tests, including imported WPM
tests; this expanded denominator must not be confused with release progress.
Existing 22 Kani and 11 Verus checks pass; these do not prove full floating
arithmetic or the whole VM. Miri's gate now includes the fused CPU fixture.
Both original 600-second boots exposed /dev/hvc0 device timeouts. A bounded
4 KiB wait probe confirms SRCU irq_work, workers and callbacks execute, so
do not re-diagnose the old missing-SGIR fault without new evidence. The 4 KiB
guest remained live; the 16 KiB run failed at the new FMADD gap. Required
target, authenticated readiness and real guest frames remain open.


## Virtio-vsock wire/window foundation (2026-10-01)

relay-vm/vsock_wire validates 44-byte LE headers and <=64 KiB payloads without
trusting guest length fields. Preserve unknown type/op values for the required
RST handling in the forthcoming transport. available_credit subtracts modular
outstanding bytes with checked subtraction. Kani production helper and Verus
integer model prove that an accepted window conserves allocated credit; totals
23/12 pass. Fixed UAPI fixture, wrap/invalid-window tests and strict Miri pass.
The old loopback queue is not a guest device; MMIO queues, bounded real host
streams, half-close/reset and authenticated waypipe/frame integration remain
required. Do not call the codec or a console READY hint transport acceptance.
Spec: https://docs.oasis-open.org/virtio/virtio/v1.2/virtio-v1.2.html

## Real virtio-vsock and bounded host streams (2026-10-01)
StaticCpu device 19/CID3 at a002000/SPI36 uses RX0/TX1/events2 with the shared
transport/parser. Register host CID2 port1024 before boot; guest waypipe
connects out. UnixStream pairs are real streams, not the old loopback queue.
Bound flows16/listeners8, pending64KiB per flow, outgoing256/1MiB. Validate
fwd_cnt advancement <= previously outstanding bytes independently of buf_alloc;
otherwise a huge peer allocation can manufacture modular credit. Kani uses
production PeerCredit::update; Verus proves a separate arithmetic model.
Poll at CPU slice boundaries even without MMIO writes. Preflight full RX/TX
chains, retain idle RX kicks, reset drops streams, preserve half-close ordering.
Both 900s fused-fix guests reach Multi-User but Wayland/hvc0/OCI units remain
open. Guest postStart lacked set -e, so failed kill still printed READY; now
set -eu and TRANSPORT_STARTED only. VZ's console readiness consumer is still
an unresolved gap. Native iOS waypipe SplitFD is unreachable; inspect actual
source and use its working Unix client listener for the forthcoming bridge.
New diagnostics/fuzzing do not prove authentication, guest frames or release.
Evidence/remaining map: Relay/docs/static-cpu-completion-plan.md.

Fresh vsock checkpoint: 297 tests (238 VM), 24 Kani/13 Verus, seven scoped
strict Miri tests and 452,538 ASan/libFuzzer runs/46s pass. Configured Miri
suites31 are not all freshly rerun. Current app and both probe boots running.

Current vsock phone/watch app links; phone main/Model/UIContracts min13 SDK26.5,
unsigned and signed Mode A/graphics gates pass; strict deep signing passes.
Exact physical install remains blocked at DDI mount by locked STARDUST.
Cube HUD/wpm_main/demo main/Rust personality duplicate warnings remain mapped.

## First real guest vsock bytes and pairwise-long repair (2026-10-01)

The 16 KiB 900s vsock probe establishes a genuine guest CID3 connection to
host CID2 port1024 and reads the first 16 guest waypipe bytes. This is transport
evidence only: the diagnostic does not reply as waypipe, authenticate readiness
or import a frame. The same run stops after 9,985,236,992 instructions at
0x6e202800, disassembled by the Apple toolchain as UADDLP V0.8H,V0.16B.
The 4 KiB run stays live for900s and reaches Multi-User, but guest waypipe
reports ECONNRESET without a host accepted-stream observation. Do not assume
the 16 KiB transport result applies to 4 KiB.

SADDLP/UADDLP/SADALP/UADALP now share pairwise_long_lane. Source widths8/16/32
widen exactly; optional accumulation wraps in twice that width. Snapshot Rn
and prior Rd for aliases; Q0 clears upper64; size3 fails without register/PC
mutation; flags are unchanged. Native comparison executes 48 fixed register
forms (24 arrangements times aliased/separate operands), 70 samples each:3,360
comparisons. The measured alias has a portable regression. Kani checks actual
helper against independent i128 arithmetic; Verus models signed bounds and
modular accumulation. Neither proves the whole decoder/CPU.

Fresh checkpoint: 299 workspace/all-targets tests (240 VM), 25 Kani harnesses,
14 Verus checks pass. Pairwise regression passes strict-provenance Miri. Latest
iOS13/SDK26.5 relay-ffi release library compiles. Previously signed full vsock
app predates this CPU repair; a fresh full-app link is still required.
Bounded first128 header tracing is kernel-probe-only, excluded from default
product. Fresh 4 KiB/16 KiB probes running under this source will diagnose the
reset and verify progress after UADDLP; target/frame acceptance stays open.

## Direct-root vsock module discrepancy and Miri correction (2026-10-01)

Exact4KiB7.2.3 config makes VSOCKETS/VIRTIO_VSOCKETS modules;16KiB builtin.
net-pf-40 aliases VMCI; virtio device19 aliases vmw_vsock_virtio_transport.
Direct-root initrd=null skips initrd module list. Explicit boot.kernelModules
now loads correct transport at sysinit. ECONNRESET cause is still a hypothesis
until refreshed4KiB image produces real guest traffic. Pairwise16KiB900s sends
16+28 waypipe bytes; diagnostic sends no reply and proves no auth/frame.
Current full phone/watch app1cwvnpnncz67bnq5ihz3vs1arsg65mv9 links, phone
floor13/SDK26.5 and isolated exact development signing/graphics gates pass.
Initial direct Miri invocations omitted MIRIFLAGS, so cannot claim strict
provenance; explicit strict reruns pass pairwise1/vsock7, full32 rerun pending.
Ordered evidence: Relay/docs/static-cpu-completion-plan.md.

## 4 KiB real bytes and bounded connected bridge (2026-10-01)

Explicit sysinit vmw_vsock_virtio_transport loading restores measured4KiB
transport: guestCID3 REQUEST then16+28 waypipe bytes to hostCID2:1024, and
Multi-User reached.16KiB previously produced same real traffic. No host waypipe
reply/authenticated readiness/frame accepted. hvc0/OCI/net service gaps persist.
Shared Rust StreamBridge owns connected Unix endpoints and buffers64KiB/direction.
Bounded nonblocking turns drain before FIN, retain reverse traffic, cancel/drop
close both, fatal errors cancel. Five actual socket/range tests pass. Darwin
SHUT_RD alone can still accept writes; disconnect peer for fatal-error fixture.
Kani proves production consume range; Verus is separate valid arithmetic model.
304 tests/26 Kani/15 Verus, Clippy, format, iOS13 release library pass. Full32
strict Miri before bridge plus new strict range suite pass;33 configured, not
claimed full33 fresh. Signed full phone/watch pairwise app predates unused bridge.
Host launch/listener/private-path lifecycle/auth/frame and VZ pump still open.
Map: Relay/docs/static-cpu-completion-plan.md.

## Native waypipe FD ownership and physical editor (2026-10-01)
StaticCpu now transfers its real vsock receiver to a Rust native waypipe worker.
The upstream client entry borrows the FD, duplicates it, connects to the real
host Wayland display and calls upstream handle_client_conn. Explicit per-call
arguments replace process-global argv: concurrent native launches otherwise
race. Do not consume another client's process-global WAYLAND_SOCKET.
Stop joins CPU/device first, then waits up to2s for the native entry. A delayed
entry retains its handle and cloned exclusive disk file until a retry succeeds;
never detach it, release its writable disk or claim shutdown prematurely.
Quoted local wawona_relay.h shadowed the linked runtime header. Stage the
canonical ABI header from that runtime package before generating the project.
Full phone/watch app links both relay_start_host_waypipe and wwn_waypipe_client_fd,
alongside real Weston/Niri. Phone main/framework floors13.0, SDK26.5.
308 host tests (249 VM),26 Kani,15 Verus and full33 strict Miri suites pass.
Native FD/reconnect/EOF/delayed-stop tests are host tests, outside Miri/formal scope.
Exact signed app installed and launches on unlocked STARDUST. Agent-device runner
needs G6EJA4DJKW signing team, not its default unavailable2S799L9W4M. Use supported
AGENT_DEVICE_IOS_TEAM_ID/AGENT_DEVICE_IOS_BUNDLE_ID in a dedicated daemon state.
Physical native VM editor lacked RAM/storage despite shared UI controls. Native
schema bindings are added, fresh full build/save-reopen verification pending.
No authenticated readiness/imported guest frame or distribution acceptance yet.

## Physical native VM settings and boot evidence (2026-10-01)
The actual physical app used WWNVirtualMachineEditorSection, which exposed only
Backend. Shared MachineEditorView RAM/disk controls were not that active UI.
Add native dictionary bindings preserving unknown vmSettings; use existing
WWNEditorNumberField across targets. SwiftUI Stepper is unavailable on tvOS.
Read stored properties only after all Swift draft fields initialize; use a local
initialVMSettings snapshot to seed immutable disk-growth lower bound.
Full phone/watch app /nix/store/bw7nva8fnfv90k07vk1g48knw42g2fna-Wawona links,
signs, installs and launches. Physical QA create/save/reopen retains768MiB/9GiB;
read-back identifies FE02CE81-DB08-4508-97C4-6C06381989C1 and real9GiB rootfs.img.
No guest boot/frame accepted: active process displays a black surface. Do not
interpret it as a crash or readiness. Effective Multi-Touch still unverified.
agent-device logs start on physical iOS relaunches the app: start capture before
starting a guest. Fill may timeout after applying text; snapshot before retrying.
Expand half-screen sheets using the observed grabber rect, then swipe within the
observed scroll bounds. Full-screen scroll-up can begin outside the sheet.
New Rust per-machine console.log records console and periodic elapsed/PC/count
samples, stops at2MiB, drains on CPU stop/error, and never asserts readiness.
Host disk-cap/console-reset test passes.309 tests (250 VM),26 Kani/15 Verus pass.
Fresh full33 strict Miri suites pass. Diagnostics app /nix/store/vvrnj8vr5p7f084kjcsbiy5pwnnszv9s-Wawona builds, signs, installs and passes signed graphics/ModeA floors.
Physical4KiB trace confirms Linux entry,196608pages/768MiB and real PC/instruction
progress (204472320 instructions/20192ms). Subsequent physical trace shows writable ext4 root,
/wawona-init PID1 and NixOS Stage2. Required systemd target/frame remain open. QA restart started21:57:27UTC. Read
physical-4k-boot-trace-first.log; never infer graphics from a live black surface.

## Simulator and physical measured failures (2026-10-01)
Physical 4KiB/768MiB/9GiB guest reaches Multi-User System, then stops at
1185760ms/11097739264 instructions on0x4fda93bd indexed FMUL V29.2D,
V29.2D,V26.D[0]. S/D scalar/vector support reuses lane/software-FP helpers;
9216 native comparisons,312 host tests,26 Kani and15 Verus and35 strict Miri suites pass.
Before the CPU stop, guest waypipe attempts Vulkan
without a guest driver and Cage cannot choose a swapchain format. Mobile
StaticCpu guest desktop/OCI recipes now negotiate --no-gpu SHM; preserve host
Metal/iland and genuine upstream waypipe. Actual new-image/frame check pending.
Relay-owned sessions must participate in native host exit detection before a
frame exists. Query existing handle ownership, not readiness; pending stop keeps
machine identity/owned resources for retry. Updated exit UI runtime pending.
User switched to iOS Simulator. Baseline installed app opens; full current app
build uses Wawona/scripts/build-current-ios.nix --arg simulator true. Default
remains physical device. Simulator success never substitutes for exact signed
physical app or distribution acceptance.

### Simulator guest-image argument omission (2026-10-01)
The embed phase accepts iphonesimulator, but wawona-ios-app-sim supplied neither
mobileGuestArtifacts nor mobileGuestArtifacts16k to ios.nix. The script then
returned success without images. Phone Simulator and iPad Simulator/device
packages now forward both existing artifact inputs. Check actual Image,
rootfs.img and manifest.json in both app directories; successful linking alone
cannot prove VM bootability. tvOS/watchOS VM prohibitions stay intact. Full
Simulator rebuild/runtime verification is pending.

## Fresh FMUL/SHM guest probes (2026-10-01)
Both new guest images built successfully; immutable paths and hashes are in
Wawona/.artifacts/relay-build/guest-shm-evidence.json. Fresh release probes
completed900 wall seconds with exit0 and no unsupported instruction/kernel
panic. This is liveness evidence, not target, authentication or frame acceptance.
4KiB completed8,478,670,848 instructions but remained in coldplug;16KiB
completed9,396,600,832 and reached Basic System, then waited on DHCP/networking.
Both /dev/hvc0 device jobs timed out before coldplug completed. Console output
itself works: TX completions1467/1673 respectively, RX256 posted/0 consumed.
4KiB: coldplug starts132.193 guest seconds, hvc0 times out208.713, udev naming
message222.437.16KiB: coldplug starts115.368, naming188.310, hvc0 timeout190.355,
coldplug finishes274.946. These traces do not establish a missing console device
or prove a clock defect. Optional OCI share mounts fail without virtio-fs.
Evidence: guest-4k-shm-fmul.log and guest-16k-shm-fmul.log. Next diagnostic
probes add only udev.log_level=debug and systemd.log_target=console to copied
manifests, run1200 wall seconds, and retain existing guest service timeouts.
No image alteration or acceptance relaxation. Simulator full build remains live.

## Bounded CPU and native shutdown (2026-10-01, validation pending)
StaticCpu Stop previously removed its registry entry and joined the CPU without
an observation deadline before the already-bounded native worker join. A delayed
CPU could block native UI indefinitely and concurrent calls could observe an
absent handle during incomplete shutdown. Stop now keeps the session registered
until both owned threads have joined, with one shared two-second observation
deadline. A pending CPU retains its JoinHandle, socket peer and exclusive disk
file; retry continues cleanup. A CPU panic marks the session exited and retains
native cleanup ownership until retry. Native worker uses the same join helper.
Two real-thread tests cover delayed CPU peer closure/native EOF and panic reaping.
These do not prove OS scheduling, arbitrary foreign callbacks, registry-wide
fairness, app Stop or guest filesystem preservation. Waiting for the registry
mutex is outside the join observation deadline. Existing formal invariants still
apply; fresh Kani/Verus/host test run is pending in host-tests-bounded-shutdown.log.
Current Simulator build snapshot predates this change; verify that artifact's
FMUL/SHM/exit behavior, then rebuild the final app with bounded shutdown.

## Verified shutdown and current Simulator artifact (2026-10-01)
Fresh316 workspace/all-targets tests (257VM),26 Kani/15 Verus, full36 strict
Miri suites and Clippy correctness/suspicious pass, with existing Clippy warnings.
Formal digest7d6e5eb197c0591e29fcd5d0ecdef702a27fe78219043712070a39873de477e7.
The added real registry test proves a pending CPU retains the handle and disk
lock, forbids concurrent disk growth, then allows retry/reopen/growth with the
same persisted test bytes. This is host lifecycle evidence, not app/guest data
acceptance. Pure thread retention/panic tests run under strict Miri; native
UnixStream/foreign-entry checks remain host concurrency tests. iOS13 relay-ffi
release compilation passes. Full new bounded-Stop app linking remains pending.
Evidence:host-tests-bounded-shutdown-final.log, miri-bounded-shutdown.log,
clippy-bounded-shutdown-final.log, ios13-bounded-shutdown-library.log.

Full Simulator phone/watch app build exec77494 finished exit0. Exact output
/nix/store/naglmk381ys88llg9ccvsc2wzvm7qzvl-Wawona/Wawona.app includes both fresh
Image/rootfs/manifest sets and real Weston/Niri/Relay/native host-waypipe symbols.
It predates bounded Stop. Current Simulator phone main/Model/UIContracts floor
14.0, watch companion/frameworks10.0, all SDK26.5. A minimal SDK26.5 clang link
requesting arm64-apple-ios13.0-simulator also stamps14.0. Scoped
--mode-a-simulator checks platform7/native arm64/floor14.0; device --mode-a keeps
platform2/floor13.0. The wrong-platform Simulator is rejected by the device gate.
Simulator SwiftShader is the real namespaced static source provider. Graphics
gate requires its three public entry points plus driver-owned identifiers when
no dylib exists. Device exclusion is unchanged. Both real artifacts pass their
scoped gates; the real device bundle is rejected as a Simulator without its ICD.
Deployment records:simulator-guests-deployment.json; compile probe:
simulator-floor-probe.log. Simulator bundle matrices still need runtime evidence.

Nix-store install returned EACCES. A complete writable ditto copy at
.artifacts/relay-build/simulator-fmul-shm/Wawona.app installs via agent-device and
launches; no uninstall or profile clear. Default profile remains; new QA is
55BBF8D8-AF7A-4C9D-8801-A36237C03895, Relay Simulator QA 4K. Native create/save/
reopen retains768MiB/9GiB. Persisted globals confirm TouchInputType Multi-Touch
and TouchPointerEmulation false. Actual boot trace confirms805306368 memory
bytes and9663676416 backing-disk bytes. Current real Simulator boot is live;
no imported frame/authentication/Stop/grow/restart/guest-data claim yet. Card
subtitle incorrectly hardcodes Relay VZ; launch actually uses StaticCpu.
Simulator data root:
/Users/8amps/Library/Developer/CoreSimulator/Devices/AA38C3A4-C022-41DB-8960-4050F3DE014B/data/Containers/Data/Application/10FA414C-5675-4A98-AC34-38717587B90A
Boot console under Library/Application Support/Wawona/relay-state/machines/<id>/console.log.

Both1200s diagnostic probes finished exit0 with no unsupported instruction/panic.
16KiB reaches Multi-User System and sends real16-byte vsock payload; the diagnostic
never replies as waypipe or authenticates a frame.4KiB has not reached required
target. hvc0 is actually queued by udev only at365.445s/273.589s respectively,
after device/getty timeout.16KiB udev READY=1 is203.367s;4KiB238.353s. These are
measured delayed discovery, not proof of a broken console model. Capture queue/
worker completion and direct-root stage1 omission before changing device/time.


## Measured vector rounding and stage1 discovery (2026-10-01)

Simulator QA4K saved/reopened768MiB/9GiB and actually booted with those values.
Its direct-root guest stopped at937227ms/11341254656instructions on
0x2e218bff(FRINTA V31.2S,V31.2S), not a timeout or app crash.
Evidence: simulator-4k-fatal-vector-round-trace.log. A portable aliased/inactive
sNaN regression reproduced failure before repair. Vector FRINT N/P/M/Z/A/X/I
now reuses the existing unsigned lane and software integral-rounding kernels
for21 S/D forms, snapshots sources, clears Q0 upper bits, accumulates FPSR and
rejects reserved Q0/D.190848 native comparisons and319workspace/260VM tests
pass;26Kani/15Verus and all37strict Miri suites pass. Clippy correctness/
suspicious and explicit iOS13 relay-ffi release compilation pass. Formal digest
6e3c2470a9d4d631d7a4cdd4da10c970bcbe2301b239a83ed6b26a2cd3e2a6cf.
Existing lane proof/model covers selection/bounds, not decoder/FP refinement.

Complete bounded-Stop/label Simulator app built: x90idc4lk2w1fvaz4vraa68md00gwgcy-
Wawona, scoped ModeA/graphics gates pass. It predates vector-rounding repair.
New full vector-rounding app builds via exec94787; no final-artifact claim yet.
Real unchanged initrd probes exec71036/92681 run1200s; their executable/source
version is pinned by real-stage1-launch-provenance.json.16KiB processes hvc0
in stage1 then reaches Multi-User but still times out its device/getty job.
Stage1 alone is insufficient. Pinned NixOS stage-1.nix omits99-systemd.rules;
upstream's serial-console rule tags hvc0 for systemd. New guest recipes bundle
the real initrd/hash, hand off to the actual NixOS stage2 path, reject cpio
case-hack paths and copy exactly the upstream console rule in scripted stage1.
NixOS MCP queried; internal extraUdevRulesCommands is absent from public index
but present in pinned module. Use config.systemd.package for rules, not
pkgs.udev(which is only minimal libs); initial build exposed that output error,
corrected. Both new images building(exec78291); service/guest-frame acceptance
remains pending. No deadline/unit reduction. Auth/OCI/devices/distribution open.


## Current verified artifacts and live jobs (2026-10-01)

Vector-rounding Simulator app built(exit0):
/nix/store/9ksfzz1c130ljnn5ip4ix0484dh80iqi-Wawona/Wawona.app.
ModeA platform7/floor14 and real static graphics gates pass. Not installed yet.
Both new stage1/console-tag guest bundles built(exit0), every kernel/initrd/
rootfs byte count and SHA256 verified, cpio case-hack paths absent, exact upstream
non-remove serial-console tagging rule present. guest-stage1-console-evidence.json.
4KiB:/nix/store/i98b3zprqnlzmbvgqhara9yariv32ypb-wawona-mobile-guest-artifacts,
16KiB:/nix/store/k06nc5y75cvh2jlbnd27lc6i5li55i3m-wawona-mobile-guest-artifacts.
Earlier real-initrd-only probes finished1200s(exit0);16KiB reaches Multi-User
but hvc0/getty fails;4KiB startsPID1 but does not reach requiredtarget.
Fresh exact recipe probes exec13675(4KiB)/9706(16KiB),1200s, now use current
vector-rounding CPU and no udev-debug override; observe actual guest streams
only. Logs guest-4k-stage1-console.log/guest-16k-stage1-console.log.
Full Simulator build including these new guest images remains live exec1286;
logcurrent-build-simulator-stage1-console.log,outlinkcurrent-app-simulator-stage1-console.
Installed Simulator app remains old FMUL/SHM/exit version; actualCPU halted at
measuredFRINTA. Preserve existing QA profile/disk. New initrd command uses new
NixOS toplevel path; an existing disk may retain old closures. For next runtime
acceptance use a fresh QA machine; do not reseed/delete the old disk. Explicit
guest-version pin/migration and preservation across app upgrades remain open.
Storage.open currently keeps an existing disk without base-image-version binding;
this source inspection is not a measured failed migration.
All319tests/26Kani/15Verus/37Miri,Clippy correctness/suspicious and iOS13release
library checks have terminalsuccess. No authentic readiness/frame acceptance.

### Simulator profile and Swift runtime integrity (2026-10-01)

The stage1/tagged-guest Simulator app installed successfully. A fresh QA
profile saved and reopened with 768 MiB RAM and 9 GiB storage. All three
profiles survived relaunch. The previous 9 GiB disk kept its exact SHA256
across installation (simulator-stage1-install-preservation.json). This proves
host disk preservation, not guest application data or restart acceptance.

Save left the Machines list stale until relaunch. Native profile persistence
now broadcasts the existing profiles-changed notification to all models.
Start taps on the fresh VM produced no new disk or visible transition. Native
launch failures now have a visible error alert and a diagnostic log; the full
Simulator rebuild is pending. Do not claim a VM is running from a successful
automation tap.

Xcode's built-in CopySwiftLibs produced a zero-byte libswift_Concurrency.dylib
in both measured Simulator and older physical-device artifacts. The previous
deployment-floor loop silently skipped it. The artifact gate now rejects
empty or non-Mach-O embedded dylibs. The original Simulator app fails this
stronger gate; a separate unsigned copy with the real Apple arm64 runtime
passes. The standalone Apple swift-stdlib-tool restores the real library even
when its destination starts empty. The unsigned iOS Simulator recipe applies
that copy and retains the actual arm64 slice. Signed/archive products are not
modified by this workaround; exact signing/export repair remains open. The
underlying built-in copier failure is not yet explained.

Both exact 1200-second guest probes finished without unsupported-instruction
failure. Both start the hvc0 serial getty with the upstream console tag. Both show
60-second login retries; the 16 KiB trace eventually reaches a genuine wawona
shell prompt, while the 4 KiB trace has no shell prompt. Neither trace proves
the required Multi-User target, authenticated readiness, or an imported guest
frame. An OCI bundle
mount failure is also visible. Preserve these failures as acceptance debt.

### Profile reload loop and final runtime packaging (2026-10-01)

The launch-error/notification app compiled and linked. Its raw Nix bundle still
failed the stronger gate because its Swift concurrency library was empty.
A separate unsigned install copy with the genuine Apple arm64 runtime passed
both Mode A and graphics checks and was installed. Simulator data moved to
073FFAFE-A187-4EDE-8881-CBC94761E369; all three profiles and Multi-Touch settings
were present. No fresh QA boot files were created. Automation later hung while
waiting for this app to idle, then failed to launch its runner. The runner was
reinstalled through agent-device and the app closed; no VM boot was interrupted.

Source and actual stored profiles reveal a reload cycle: serialize always
recreated bundledAppID="" and useBundledApp=false for VM profiles; loadProfiles
removed those keys and saved; the new change notification scheduled another
reload. The native persistence adapter now writes those fields only for native
and Wasm profiles, and compares parsed saved values before publishing an
unchanged save. Runtime proof of Save/reopen/Start awaits the full rebuild;
do not claim the UI loop is resolved from source inspection alone.

Conditional Swift repairs in buildPhase and postFixup did not produce valid
final libraries. An unconditional final Apple-copy plus arm64 extraction and
integrity assertion did. The completed Nix app at
/nix/store/qqwg07m7fidhl6zvkjj97k97kma58gcf-Wawona/Wawona.app has the real
557440-byte arm64 library and passes the stronger Mode A dependency gate.
The reason earlier conditional checks skipped the repair remains unexplained.
Signed/archive products are outside this unsigned Simulator workaround.

## Simulator resume (2026-10-02)

The profile-idempotent Simulator build completed successfully. Its immutable
app at /nix/store/lj0p4l8x7jf3n18spy1ynfqjcgn85gn4-Wawona/Wawona.app passes
Mode A and graphics gates, contains the genuine 557440-byte arm64 concurrency
runtime, and strongly links Weston, Niri, Relay, WASI and native waypipe FD entry.
Both embedded guest variants match all six manifest artifact hashes.
The exact writable copy was installed; three profiles remained. Save/reopen
responds without the migration/notification loop. Saving a rename still left
the visible card stale until reopening the app. The editor mutates its initial
NSObject; card rendering now takes machineId/name/type value snapshots.
This display change is building; runtime Save verification remains open.

On resume, Machines showed disconnected, the saved name was present, and the
fresh QA console was empty. The earlier session's end is not attributed to a
cause. A new Start through agent-device on DC2A8DBA-EE06-44F1-99AC-F6CBD9B71387
produced a real boot trace with 805306368 bytes RAM and a 9 GiB disk. Stage 1
recovered the ext4 journal, mounted /dev/vda, and entered real NixOS stage 2.
The guest remains live while systemd starts services; no required-target,
authenticated readiness, imported frame, graceful Stop or guest-data claim.
Data container: B8652265-121B-4B32-ABE6-01995123E2B4. Do not reinstall or restart
logging during this boot. A new boot intentionally truncates console.log;
a zero file alone never establishes whether a VM is running or stopped.

Fresh host verification after the UI changes passed 319 workspace tests,
26 Kani harnesses and 15 Verus checks (host-tests-simulator-resume.log).
Previous 37 strict Miri suites remain the last Miri evidence; Rust source is
unchanged. Signed runtime packaging and physical/distribution checks remain open.


The value-snapshot full app build completed at
/nix/store/1zhg80qxnqgm7ingm7rm8z2nzw9gy04j-Wawona/Wawona.app. Mode A dependency
floors and graphics gates passed, all five required native entries remain
strongly linked, and the concurrency runtime remains 557440 bytes. It has not
replaced the app executing the current guest. Runtime rename verification
remains open. Simulator systemd traces expose concurrent device-discovery,
time synchronization, wrappers, OCI-mount and firewall startup jobs; do not
increase timeout limits or drop required services to call the target reached.

## Simulator FCVTN and storage slider (2026-10-02)

The actual 4 KiB Simulator guest reached real Cage/wlroots initialization over
native host waypipe, including host output WL-1 and seat mapping. A real host
Wayland window appeared, but its pixels remained blank. Foot then began and
StaticCpu exited at 959932 ms / 12643827712 instructions on 0x0e616bff.
Static Apple assembly/disassembly identifies FCVTN V31.2S,V31.2D, not integer
saturation. No authenticated readiness or imported guest frame is claimed.
The terminal console is preserved in simulator-resumed-4k-fcvtn-exit-console.log.
The app was closed through agent-device after the CPU exit; that is not proof
of a successful guest shutdown. After a coordinate Close attempt, the tab disappeared but the host screen
stayed blank. The callback and return-to-Machines were not verified; the
guest had already exited. Runtime close acceptance remains open.

FCVTN/FCVTN2 and FCVTL/FCVTL2 double/single vector forms now snapshot aliased
sources and reuse the production integer-only narrow_double/widen_single FPCR
and FPSR helpers. Narrow-low clears the upper half; narrow-high retains the low
half; widen-high selects upper source lanes. Unadvertised half formats still
fail without destination/PC/flag mutation. 70272 statically assembled native
comparisons cover all four forms, aliases, controls, edges, NaNs and random
vectors. Workspace tests pass 322 (263 VM); current Kani26/Verus15 pass.
The proofs retain their existing helper scope, not whole-vector/VM proof.
A new portable vector-precision family is included in strict Miri; full run
and final complete app build are still in progress.

The deployed native WWNVirtualMachineEditorSection used a number field even
though the shared editor already had a slider. Both now use/show native storage
slider values and endpoint captions in GiB. New profiles have minimum4 and
maximum64; editing retains the configured capacity as minimum to prevent shrink.
The native new-profile minimum distinguishes an absent profile from an existing
legacy profile with an implicit8 GiB disk. Saved selection remains integer GiB.
No VM domain engine moved into Swift. Simulator visual/save verification awaits
the full app containing this labeled slider and the current CPU fix.

Current vector-precision verification completed: full38 strict Miri suites,
Clippy correctness/suspicious gate, and explicit iOS13 relay-ffi release
cross-compile all pass. These supplement the322tests/26Kani/15Verus and70272
native comparisons. Final Simulator app compile/link and UI checks remain
pending at this observation. Rust source stayed unchanged during these runs.

## Adaptive machine editor and Nix configuration (2026-10-02)

Machine editor presentation is centralized in WawonaBackport.editorSheet().
iPad uses system page sizing on iPadOS 18+ and the large detent on 16/17;
iOS 13-15 keeps its native presentation. Phone keeps medium/large detents.
The complete hx7kqgisqhhk18mg5160sn4lqslzj0jc Simulator app was installed on
758B28B3-2E6A-46C2-91C3-2B1DCCC0A751. Its real screenshot shows a near-window
page instead of the previous centered medium sheet. Actual labeled native
storage slider was also observed: 8 GiB value, 4 GiB and 64 GiB endpoints.
New icon-only Cancel (xmark) and Save (blue checkmark) are implemented in both
editors, retaining accessibility names and draft-only Cancel. Their final
Simulator Save/discard checks await the newest complete build.

User requests per-machine configuration.nix, flake.nix and relay.nix, with
syntax highlighting and editable packages/Wayland desktop. Relay now exports
nixosModules.relay and a nixos-guest template. The prior mobile guest disabled
Nix; the extracted relay.nix enables Nix, flakes and nix-command while retaining
virtio/rootfs/vsock/OCI integration. configuration.nix owns software/session;
wawona.relay.sessionCommand is an argv list, shell-escaped in the existing
waypipe unit. Evaluated default 4 KiB and user-overridden 16 KiB configs both
retain /dev/vda and enable both features. Guest binaries remain inside Relay.

Rust owns Nix templates and UTF-16 highlight spans; native UITextView/NSTextView
only renders tokens and edits the draft. nixFiles persists through Swift and
Rust profile schemas. UniFFI records support HashMap, not BTreeMap; a complete
app build caught the original wrong map type, now corrected. Shared Swift tests
pass40; Relay passes326 tests plus26 Kani/15 Verus (existing helper scope).
New lexer Miri checks are still running. Final app compile/link and editor
Save/reopen/highlight runtime verification are pending.

This is not a completed guest reconfiguration path: saved files still need
verified transfer, pinned flake.lock, authenticated guest rebuild/status,
last-known-good rollback, and restart into the selected system generation.
Current direct boot cmdline pins a toplevel /init; a future guest rebuild alone
cannot prove persistent configuration across restart. Required target/frame,
networking, physical signed device and distribution gates remain open.

The z408vl53zzkqbf6vw3bfnh6qq7cqs8ds full physical app links but its artifact
gate rejects an empty Frameworks/libswift_Concurrency.dylib. Unsigned iOS
postFixup now selects the real Apple runtime for simulator or phone. Signed
archives are never changed there. Repair verification awaits a fresh artifact.


### Actual iPad editor and current assurance (2026-10-02)

Complete registered Simulator product xbcin5qw7b2wwa3dnq1mnzq3ivxq23il
passes Mode A platform/dependency and graphics gates. Agent-device installed
an exact writable copy. Native, VM, Container, Wasm and both SSH type selections
place their configuration before general overrides. Actual screenshots verify
a wide iPad sheet, X Cancel, blue checkmark Save, real slider with 4/64 GiB
endpoints, and Rust-backed Nix token colors. Canceling Add leaves one existing
profile; reopening returns to Native. No QA VM was saved or booted on iPad.
Artifacts: ~/.agent-device/test-artifacts/ipad-editor-*-first*.png and
ipad-nix-editor-highlighting.png. VM editor AX snapshots still time out while
screenshots and point presses work; do not treat this as a guest boot failure.

Current Rust assurance passes 326 tests, 26 Kani harnesses, 15 Verus checks,
and 39 strict Miri suites, including the four lexer tests. Swift passes 40.
Physical app source compile/link succeeds. A traced packaging failure showed
lipo -thin rejects the already-thin physical arm64 Swift runtime. Guarding that
operation alone produced a registered app whose runtime became zero bytes:
com.apple.decmpfs and ResourceFork remain on the file after Nix normalization.
The unsigned recipe now rewrites already-thin decoded bytes with cat into a
fresh file before moving it into place. Fat runtimes use lipo as before. The
final artifact gate remains mandatory; this repair is under build verification.
Signed archive products remain outside this unsigned repair.


Physical repair verified: full registered product
/nix/store/c4d89bgl6l09r0as7xw636ad4ss9nmyd-Wawona/Wawona.app retains the real
7.4 MiB Swift runtime and passes Mode A platform2/iOS13 dependency floors plus
iOS graphics policy (real ANGLE/MoltenVK, no SwiftShader/private Mode B).
The fresh plain-byte rewrite resolves the observed post-storage empty runtime.
This is an unsigned product artifact, not exact signed physical-device or
App Store distribution validation. Simulator proof remains product xbcin5qw.


## 2026-10-02: disk-owned NixOS generation boot

New mobile rootfs images now seed /nix/var/nix/profiles/system-1-link,
system -> system-1-link, and /init -> /nix/var/nix/profiles/system/init.
Their manifest uses init=/init rather than pinning the host-bundled toplevel.
This closes the new-image boot-selection prerequisite for guest rebuilds.
It does not implement guest file transfer, flake.lock, rebuild/apply, rollback,
or migration of existing disks. Bundled kernel/initrd compatibility with a
future selected guest generation still needs explicit handling.

Both actual 4 KiB and 16 KiB ext4 artifacts were built and inspected with
native Darwin debugfs: all three links resolve to the expected page-specific
system and its real init file. Receipt: stable-generation-image-links.json.
Fresh host verification passes 326 tests, 26 Kani harnesses, 15 Verus checks.
No production Rust changed in this checkpoint; prior strict Miri scope remains.

Both fresh 600-wall-second static_smoke probes exit0 and remain live, executing
7,646,101,504 (4 KiB) and 8,480,944,128 (16 KiB) instructions. Actual stage2
boots the selected disk generation at 75.970877/66.736714 guest seconds.
Both reach Local File Systems and System Time Set, but neither reaches the
required Multi-User target. Coldplug udev remains pending; /run/wawona/oci-bundle
mount fails and the OCI forwarded-client dependency fails on both guests.
No authenticated readiness or imported guest frame is observed. Smoke exit0
is only liveness. Diagnostic keep_bootcon differs from the release commandline.
Logs and extracted evidence: Wawona/.artifacts/relay-build/stable-generation-*
(including boot-summary.json and host-tests.log).

Phone Simulator QA disk baseline is 9 GiB (9,663,676,416 bytes), SHA256
242c25270f52fb996ed058135f7f82683c81db902c2c0ef519ea6759a2256d39.
The installed phone app still predates the latest VM-first/Nix editor UI.
An accessibility snapshot crashed in Apple's XCTAutomationSession initializer
(Wawona-2026-10-02-133647.ips); screenshot/point Cancel remained usable.
Several successful reported swipes produced unchanged screenshots. The draft
was cancelled without saving; the QA VM is disconnected. No disk growth,
restart, or guest-file preservation acceptance is claimed for this checkpoint.
Do not reset legacy disks or infer runtime storage proof from a host hash.


## 2026-10-02: full coldplug prioritization and crate-local Nix templates

Prior debug traces queue hvc0 only at365.444907/273.589 guest seconds after
module-first coldplug. The exact pinned systemd261.2 upstream trigger requests
--type=all --action=add with module,block,tpmrm,net,tty,input priority. Relay now
adds an explicit asDropin ExecStart reset and uses block,tty,net,input,module,tpmrm.
All subsystems remain included; upstream unit dependencies, serial-console
rules and timeouts remain intact. Both actual4K/16K images build and their ext4
images contain the checked drop-in. Evidence: udev-priority-unit.json,
udev-priority-image-units.json and udev-priority-guests-build.log. Two1200s
static_smoke probes are running; readiness remains unproven until final traces.
No OCI share is supplied by static_smoke, so its optional nofail virtiofs mount
failure alone is not evidence that the regular VM target depends on that mount.
OCI lifecycle still requires a real shared bundle and its own acceptance.

A real isolated crate2nix relay-core build failed on all three include_str paths
because templates outside the crate were omitted. Canonical template files now
live inside crates/relay-core/templates/nixos-guest. Rust includes crate-local
files; the exported flake template points to that directory. The old repository
path remains a directory symlink for compatibility. SHA256 equality proves all
three template contents unchanged. The exact isolated crate now builds:
/nix/store/jf09yhbh1q5bisj6394c7bky2lp396p0-rust_relay-core-0.1.0.
Fresh326 host tests,26 Kani harnesses,15 Verus checks pass after the move.
iOS13 compilation and strict editor Miri remain running. Evidence:
relay-core-isolation.log (reproduction), relay-core-isolation-fixed.log,
relay-core-template-content.json and udev-priority-host-tests.log.


Template packaging validation finished: all4 strict-provenance nix_editor Miri
tests pass (360.93s), and relay-ffi aarch64-apple-ios release compilation with
IPHONEOS_DEPLOYMENT_TARGET=13.0 passes. Current formal source digest:
739cab04819bbd51ccfadee30a6c00ad99cecae0006283d36f7fff51e0c809e8.
This is Rust-library compilation, not a new complete signed app or guest-apply
proof. Full device/Simulator app artifacts described earlier predate this move.


## 2026-10-02: completed coldplug-priority runtime probes

Both1200s probes finish exit0 without unsupported instruction or kernel panic.
4KiB executes15,015,571,456 instructions;16KiB16,570,294,272. Both actually
complete coldplug, reach Basic System, start Serial Getty on hvc0, and start
the real Wayland session. Transport-start console hints occur501.591290/413.780593
guest seconds; both send a real16-byte waypipe vsock payload to host port1024.
Neither trace proves Multi-User. Both optional OCI mounts fail without a share;
16KiB additionally reports failed session-1.scope/session-2.scope. These failures
remain acceptance findings. No authentication or imported guest frame is claimed.
Exact extracted receipt: udev-priority-boot-summary.json. Probe executable and
pre/post template-move source provenance: udev-priority-probe-provenance.json.
This narrows the earlier console/getty failure; it is not proof the priority
change alone caused the result because the 600s baseline had less run time.

Detailed service traces exec59164 and exec11042 finished after 1200s (exit0).
Logs: udev-services-trace-4k.log and udev-services-trace-16k.log. Do not resume
those PIDs. systemd 261 "Startup finished" means the job queue is empty. Neither
trace contains "Reached target Multi-User System".

Both page sizes: OCI oci-bundle mount fails with no share (nofail, expected);
dhcpcd Type=forking+waitip has no virtio-net and times out; shadow login
LOGIN_TIMEOUT 60s fires during pam_systemd while user@1000 is still inside its
own start deadline, then session scopes fail with result resources because no
PIDs remain. 16 KiB also fails bpf-restrict-fs load with ESRCH; 4 KiB attaches
it. That is not the shared missing-target cause.

relay.nix sets security.loginDefs.settings.LOGIN_TIMEOUT = 0 and disables
dhcpcd until virtio-net exists. Other login.defs keys stay. Service deadlines
are not lengthened.

Rebuilt images:
4 KiB /nix/store/qrkhvnr0zscw73zqic6mh5qgd6r6mfgx-wawona-mobile-guest-artifacts,
16 KiB /nix/store/x6p6wnhkj78586af0p6ly7hblz6f720b-wawona-mobile-guest-artifacts.
Login timeout, session-scope resources, and dhcpcd timeout are gone on both
page sizes. systemd.log_target=console makes systemd 261 skip the journal copy
of status lines. fbcon then takes /dev/console before the default target
activates, so hvc0 never shows the status line. systemd.show_status=yes does
not fix that.

Without log_target=console, journald forward_to_console prints the required
line. Both 1200s probes remained live and exited 0.
login-scope-journal-4k.log: guest 487.507676 Reached target Multi-User
System, after Started Wawona at 487.489143. login-scope-journal-16k.log:
guest 406.996742 the same line, session started at 406.334490. The later
16 KiB "Startup finished in 1min 1.866s" is the user manager (systemd[721]),
not pid 1. OCI no-share failure and 16 KiB bpf-restrict-fs ESRCH remain.
Both send a 16-byte vsock payload. That is not authentication or a frame.

Current compile receipt confirms Relay dylib platformIOS,minos13.0,SDK26.5:
template-isolation-ios13-build-version.log. Actual new complete app linking,
existing-disk migration, per-machine growth/restart/guest-data acceptance,
flake apply/rollback, authenticated graphics, OCI/device lifecycle, exact signed
physical-device/distribution checks and guest AOT remain open. Phone Simulator
still has3 saved profiles and QA disk9GiB; no new profile or growth was saved.
