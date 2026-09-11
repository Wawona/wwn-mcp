# iOS-family zsh Ctrl+C (in-process PTY)

Indexed summary. Ctrl+C is VINTR (0x03 / SIGINT), not SIGTERM and not a
Settings key. It must stop the foreground in-process command (uutils
`yes`/`cat`, a sourced loop, wasm) and return a prompt.

## What shipped

- Apple-mobile zsh runs externals in-process. `wawona_wasm_run` and
  `wawona_coreutils_main` share the shell pthread. Do not
  `pthread_kill(SIGINT)` that thread while wasm is on the stack (handler
  or process abort).
- PTY `ios_deliver_shell_tty_signal` (0x03 / 0x1c):
  - Calls `wawona_wasm_request_interrupt` (Relay epoch + shut Wayland
    sockets). Guest exit 130.
  - When wasm is running: set `ios_tty_interrupt` and `pthread_kill` the
    shell thread with **SIGUSR1** (empty handler, no SA_RESTART) so a
    blocking WASI `inherit_stdin` read returns `EINTR` → interposed
    `EIO` → epoch trap. Never `SIGINT` on that stack.
  - When ZLE has ISIG off and no in-process command is running, pass
    the byte through so the line editor sees `^C`.
  - When a dispatched command is running (or cooked ISIG is on), set
    `ios_tty_interrupt` and `pthread_kill(SIGINT)` the zsh thread.
    Interposed `read`/`write` on stdin/stdout then return `EIO` so
    uutils `write_all` (which retries `EINTR`) actually stops.
  - `wawona_dispatch_inprocess` begin/end brackets the command. End
    returns 130. The zsh exec hook sets `errflag` so a `while` loop
    does not restart `yes`.
- Host IME: do not `commit_string` Ctrl+letter when a terminal owns the
  PTY. TI Enable used to swallow OSK Ctrl+C. iOS also steals Ctrl+C as
  Copy (`copy:` used to inject Ctrl+Shift+C). While
  `wwn_ios_terminal_is_active`, `copy:` injects VINTR. `UIKeyCommand` +
  `wantsPriorityOverSystemBehavior` is the other steal-back. Cmd+C stays
  client Copy.
- Socket recv must not hold the guest-fd mutex across a blocking read.
  Interrupt shuts the fd from the PTY thread.

## Where

- `Relay/import/wasm/src/interrupt.rs` + `host.rs` + `wawona_wasm.h`
- `wwn-toolchain/.../wawona-pty/src/wwn_pty.c` (flag + stdio interpose)
- `wwn-toolchain/.../wawona-pty/src/wawona-dispatch.c` (begin/end)
- `wwn-zsh/.../patch-zsh-exec.py` (`lastval == 130` → `errflag`)
- `Wawona/src/platform/ios/WWNCompositorView_ios.m` (`copy:` / UIKeyCommand)

## Hard rejects

- Treating Ctrl+C as TI text or host Copy (Ctrl+Shift+C) while
  weston-terminal is focused
- Killing the Wawona process to stop a guest or `yes`
- Closing GUI by inventing a second window protocol. Disconnect the
  Wayland socket.
- `siglongjmp` out of Rust uutils (UB). Cooperative flag + `EIO` only.
- Inventing a Settings "interrupt key"
