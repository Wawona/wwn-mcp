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
