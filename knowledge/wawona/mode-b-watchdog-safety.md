# Mode B watchdog safety (macOS 26)

Hard forbids for Classic Desktop Replacement. Canonical:
`Wawona/docs/agent-rules/wawona-mode-b-watchdog-safety.md` and incidents
`2026-08-19`, `2026-08-20`, `2026-08-23`.

On macOS 26 / 25F80, exiting `watchdogd` with SIGTRAP while kernel IOWatchdog
is armed panics immediately: `watchdogd[pid] exited`.

## Never

- Take Over / unload `com.apple.watchdogd` / `kickstart -k` watchdogd without
  sticky `/var/db/wwn-iowatchdog/claim-ok` **and** live Disable
- Attach lldb, debugserver, or Cursor lldb MCP to `watchdogd`, WindowServer,
  or any process holding `IOWatchdogUserClient`
- `wwn-iowatchdog disable|enable` during stage / install / healthy Aqua
- `export DYLD_INSERT_LIBRARIES` in `run-modeb.sh` or the login shell
- `launchctl disable` / `unload -w` on `com.apple.WindowServer` (sticky;
  missed restore → userspace watchdog panic)
- Path B `bootstrap` / `kickstart` from `restore_watchdogd` after Classic
  (2026-08-23: kernel timeout)
- KEEP_WS / failed probe calling `restore_watchdogd` / Apple-enable
  `watchdogd` while Path B is sticky

## Do

- Mode A in-window when ACK is missing. Leave Aqua and `watchdogd` running.
- Enable Desktop Replacement: doctor, heal, Path B. Never Take Over from Enable.
- Take Over only with `WWN_MODEB_WD=iowatchdog-then-unload` and sticky ACK.
- Probe: `Wawona --mode-b-probe` (KEEP_WS). Helper skips `restore_watchdogd`
  unless Classic left `wawona-unloaded-watchdogd`.
- `wwn-iowatchdog status` / `--doctor` for coverage.

## Check before experiments

```text
pgrep -l watchdogd
pgrep -lf lldb_mcp || echo lldb_mcp_gone
cat /var/db/wwn-iowatchdog/claim-ok   # path=b sticky=1
# plus live marker or sock status done=1
grep -q 'skip restore_watchdogd' \
  "/Library/Application Support/Wawona/run-modeb.sh"
```

Repo for the tools: `wwn-iowatchdog`. Helper / Settings: `Wawona`.
