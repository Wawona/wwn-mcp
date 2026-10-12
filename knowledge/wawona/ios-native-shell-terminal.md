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

## Hard rejects

- Splash-only Terminal Start
- Treating fake `weston_terminal_main` as the shell
- Master-only keyboard on Apple mobile
- Missing `WAWONA_ZSH_IN_PROCESS`
- iOS 14-only fonts in that UI without backport (`caption2`)

Rule: `wawona-ios-native-shell`. Skill: `wawona-ios-native-shell`.
Related: `apple-mobile-mode-a-backends.md`, `machine-types-native-shell.md`.
