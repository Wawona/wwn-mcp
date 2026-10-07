# vphone-cli agent loop (Mode B packages)

Agents do not type into `vphone-cli`. They JSON-talk to `vphone.sock` on a
*running* guest, then use agent-device MCP for Interactor and SSH packages.

Skill: `wawona-vphone-cli`. Recover: `wawona-vphone-lab-recover`.
Lab: `nix run github:Wawona/wwn-vphone#vphone-jb-lab`.
Sock helper: `nix run github:Wawona/wwn-vphone#vphone-sock -- ping`
or `python3 wwn-vphone/scripts/vphone-sock.py …`.

## Split

- `vphone-cli vm launch` is host bring-up only. `nohup`. Visible window.
  Never a foreground agent Shell. Never `pkill -f vphone`.
- Guest automation is `vphoned` on
  `~/.vphone/machines/wawona-jb/vphone.sock` (schemaVersion 2).
- agent-device (`user-agent-device`) uses that sock for `snapshot -i` /
  `press` and uses SSH for `packages apt`. Device name `vphone wawona-jb`.

## Sock first (works without SSH)

`{"t":"ping"}` proves the agent. Not rpc method `ping`.
`screen.unlock`, `apps.launch`, `files.*`, `apps.open_url`, `apps.install`,
`ui.tree`. Tree frames are points. Multiply by `device.screen.scale` for
`t:tap` pixels. Screenshot: `path` PNG `screen:false`. If the reply is
`guest agent is not connected`, ping/unlock and retry. Do not relaunch.

`setup.skip` `{force:true}` only when `setup.status` is pending/running.
A second skip on a finished guest is launchd 144.

## Mode B packages

2.6 standard CFW has no dropbear, no TrollStore, no apt. Irisin bootstrap
puts `/var/jb`. OwnGoal `owngoal-bootstrap-vphone` is what adds apt/ssh.

| Job | No SSH | SSH |
|---|---|---|
| `.tipa` | sock `files.write` + `apps.install` | `packages tipa` |
| Wawona repo | write `/var/jb/etc/apt/sources.list.d/wawona.list` and `irisin://repository/add?url=https://repo.wawona.io/` | `apt-get update` |
| `.deb` | Irisin UI | `packages apt install` |

Never copy a tipa app to `/var/jb/Applications` (TrollStore helper 179).
Never `packages status` / `packages apt` while `:22222` is closed.
Guest IP drifts. Probe `guest-ip.txt` / profile `sshHost` / dhcp lease
for the VM MAC. Do not scan every `192.168.64` address. Close the
agent-device session after rewriting `sshHost`.

Irisin bundle id: `wiki.qaq.irisin`. Do not HID-type the repo URL in
Irisin Search.

`vphone-cli` does not run `dpkg`. Irisin does:
`/var/jb/usr/libexec/irisin-install` and `/var/jb/Library/dpkg`.
This iOS 26 guest has no `/bin/sh` (`/bin` is `df` + `ps`). A
`#!/bin/sh` postinst is errno 2. A `half-configured` package (the
Mode B demo) then fails every later Irisin install, including
`wawona-launch-tools`. OwnGoal first, or omit maintainer scripts.

## agent-device MCP

Serial mutating calls on one session. `packages tipa` may use sock upload
when TrollStore SSH is absent. `packages apt` is SSH `apt-get`/`dpkg`.
`snapshot -i` needs a launched app; Home Screen AX is unverified.

See also `vphone-jb-lab-and-packages.md`.
