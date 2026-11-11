# iOS Native Shell / Wawona Terminal Start

Updated 2026-10-11 after STARDUST splash incident.

## Product

Native Shell → **Terminal** session is **Wawona Terminal** (`wawona-shell`).
In-process zsh on Apple mobile. Not foot. Not weston-terminal.

## Required Start

1. Rootfs + `WAWONA_ZSH_IN_PROCESS=1`
2. `wwn_pty_session_start` → pthread `wawona_zsh_main` (`-zsh -i`)
3. Master drain → `wwn_term_feed` / `wwn_term_export` → SwiftUI terminal
4. Keys → `wwn_ios_terminal_inject`
5. Stop → `wwn_pty_ios_stop_shell_session`

## Incident (do not repeat)

Guest console showed **"Wawona Terminal / Native Shell starting"** forever.
`connectNative` no-op'd `wawona-shell`. User called it "weston terminal".

`weston_terminal_main` from `mobile-weston-terminal.c` is **fake SHM chrome**
(no PTY). iOS `launchBundledExecutable` is macOS-only. Neither is Native Shell.

## Code

- `Sources/WawonaApple/Shell/GuestConsoleView.swift` (`IosShellSession`)
- `Sources/WawonaUI/Machines/Catalog/WWNIosGuestConsole.swift`
- `wwn-toolchain` `wawona-pty`, `wwn-zsh` `wawona_zsh_main`
- Term screen: `github.com/Wawona/Terminal` / `wwn_term_*`

## Stop and second session (2026-10-17)

zsh runs in-process and ends by EOF inside `zleread()` (soft-exit, no
unwinding). Every global it touched survives into the next `zsh_main`.

| Wrong | Right |
|---|---|
| Shell owned by the SwiftUI view, stopped in `onDisappear` | Process registry owns it. Views attach/detach. Stop only on Close / Stop |
| `pthread_join` before closing the input pipe write end (0x8BADF00D) | `wwn_pty_ios_stop_shell_session` closes every `input_write` first |
| Master pump spins at EOF | Cancel the pump on `read` == 0 |
| Trust zsh statics on re-entry | `wwn-zsh` resets: `zleactive`, `errflag`, signal queue (stop SIGINT stays queued), feature `ADDED` marks, special params (`patch-zsh-reentry.py`) |
| `tcgetattr` on SHTTY (pipe dup above fd 10) | `patch-zsh-fake-tty.py`. libwwn-pty interpose does not apply inside the static app |

Symptom of stale state: second Start shows `mba%` with no banner (rc files
abort), or builtins are "command not found", or HOME is `/`.
Prove: Close then Start shows the banner and `~ %`, `cd; pwd` prints HOME.

## Hard rejects

- Splash-only Terminal Start
- Treating fake `weston_terminal_main` as the shell
- Master-only keyboard on Apple mobile
- Missing `WAWONA_ZSH_IN_PROCESS`
- iOS 14-only fonts in that UI without backport (`caption2`)

Rule: `wawona-ios-native-shell`. Skill: `wawona-ios-native-shell`.
Related: `apple-mobile-mode-a-backends.md`, `machine-types-native-shell.md`.

## Window size on the pty pipe (2026-10-17)

`TIOCGWINSZ` on SHTTY fails (pipe, and `__interpose` does not apply inside the
static app). zsh then uses 80x24. On a 36-column watch grid PROMPT_SP pads to
80 and every prompt (after ^C too) wraps to an extra blank line.
`patch-zsh-fake-tty.py` makes `adjustwinsize` fall back to
`wwn_pty_tty_shim_get_winsize` (host calls `wwn_pty_tty_shim_set_winsize`
before start). Check: `print $COLUMNS` matches the host grid. The throwaway
`make zsh` link needs the stub in `wawona-dispatch-link-stubs.c`.

watchOS text entry: a hidden `TextField` with `@FocusState` does **not** open
system input. Use a sheet `TextField` the user taps.

## Terminal Done freeze (tvOS, 2026-11-05)

Done froze the app. `IosShellSession.deinit` joined the zsh pthread on the
main thread while zsh was blocked on its history file lock. Rules:

- Never join the shell thread (or call `wwn_pty_ios_stop_shell_session`) on
  main. Teardown runs on a serial stop queue; `deinit` only schedules it.
- `wwn_pty_ios_stop_shell_session` is idempotent behind a mutex. Two stops
  (Done then deinit) must not double-free or double-join.
- zsh rootfs `.zshrc` sets `HIST_FCNTL_LOCK` (no `.zsh_history.LOCK` spin
  after a soft restart).
- tvOS has no on-screen keyboard for the grid. A focusable SwiftUI
  `TextField` (`WWNTvTerminalKeyboardField`) diffs edits into
  `wwn_ios_terminal_inject` bytes (new text, backspace `0x7f`, Return `\r`).
- Prove with 3 Start/Done cycles on a tip tvOS build.
