# vphone lab + packages (Mode B)

Combine:

1. `nix run github:Wawona/wwn-vphone#vphone-jb-lab`
2. `agent-device packages tipa|apt|debug …`

The lab bootstrap installs Procursus **debugserver** (apt). That is what
`packages debug attach` starts before handing `connect://` to user-lldb.
Physical / stock iOS uses Xcode Developer Disk Image debugserver over lockdown
instead. Same Procursus package Theos device debugging already expects.

Tipa: `CFBundleShortVersionString` (marketing) ≠ `CFBundleVersion` (build).
Bump BUILD via `Wawona/scripts/build-modeb-demo-tipa.sh` before reinstall.

Channels: TrollStore tipa (JIT + IOMFB) vs Sileo APT deb (full jailbreak Mode B).
See `wwn-vphone.md`, `agent-device-wawona-fork.md`.

`vphone wawona-jb` is the Mode B TrollStore proof device. Treat it as
physical-class. Do not park IOMFB / open-jit / niri gates on STARDUST or
a retail iPhone. TXM limits (MAP_JIT write+exec `EPERM`, Metal nil) are
proven results. Weston remains own-display. Do not fake MAP_JIT
write+exec. iOS VMs wait on Relay. Fail closed. No QEMU product path.
Linux guests stay slim. Display is Wayland / iland DRM. Relay owns VMs,
containers, and wasm. Mode A stays store-compliant. Mode B may JIT the
same Relay CPU. Official tipa embeds Relay NixOS disks only after frames.

`launchNiri` must fail closed before `niri_main` when
`MTLCreateSystemDefaultDevice` is nil. Calling niri anyway spins ANGLE
on a utility queue and can take the host down. Weston DRM+pixman stays
the own-display compositor.

Sock PNG can freeze on the lock-screen frame. `sbreload` unlocks
SpringBoard. Then `uiopen --app Wawona` (after `uicache -p`). Compact
JPEG `screen:true` is often stale. Prefer sock `path` PNG after a power
key if the clock is stuck. Kill `WawonaModeBDemo` and other Iomfb*
apps before product IOMFB tests. Do not `kill -9` Wawona.

Stuck lab recover (automatic). Skill `wawona-vphone-lab-recover`. Dead
means sock `ECONNREFUSED` and no
`vphone-cli --config …/wawona-jb/config.plist`. `agent-device`
`booted=true` and lab `wait_ssh` `no vphone process` are stale (pgrep
misses that argv). Wawona flake often has no `vphone-jb-lab` attr. If
the VM is live, kill only the waiter, never `pkill -f vphone`. If dead,
`nohup` `vm launch` with a visible window. Never run `vm launch` as a
foreground agent Shell (tool cancel / exit 13 kills the guest). Guest
IP drifts. Do not scan every dhcp lease in a 900s agent loop.
