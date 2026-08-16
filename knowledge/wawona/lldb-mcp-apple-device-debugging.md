# lldb-mcp: debugging Wawona on Apple devices

**High-priority companion MCP** for on-device and on-Mac debugging. Agents debugging
Wawona crashes, in-process shell tools, or UI issues on Apple hardware **must use
lldb-mcp**. Not crash-log guesswork alone.

Related: `ios-device-dev-workflow.md` (full build → install → debug loop).

## What it is

| Field | Value |
|-------|-------|
| Upstream | [stass/lldb-mcp](https://github.com/stass/lldb-mcp). LLDB wrapped as MCP tools |
| Nix package | `modules/pkgs/_lldb-mcp.nix` in nix-darwin dotfiles |
| Cursor MCP name | **`lldb`** (not `lldb-mcp`) |
| Requires | macOS, Xcode LLDB (`DEVELOPER_DIR` set), paired Apple device for iOS attach |
| **Not indexed** | Action/debug server. Like xcodebuild-mcp, it runs locally (stdio), not as a remote URL |

Wired by nix-darwin `dendritic.ide.mcp.lldb.enable` (default on Darwin) into
`.cursor/mcp.json`, `.antigravity/mcp.json`, and per-repo `Wawona/.cursor/mcp.json`.

**Rule for agents:** when a bug is reproducible on device, use **xcodebuild-mcp** to
install a **Debug** build, reproduce, then **lldb-mcp** to capture backtraces,
inspect frames, and evaluate expressions at the fault site.

## Wawona targets (what to debug)

| Layer | Process | Bundle ID | Key symbols / breakpoints |
|-------|---------|-----------|---------------------------|
| iOS/iPadOS app | **Wawona** | `com.aspauldingcode.Wawona` | App entry, SwiftUI, ObjC bridge |
| In-process zsh | same process (pthread) | - | `wawona_zsh_main`, `wwn_pty_spawn_shell_paced` |
| In-process dispatch | same process | - | `wawona_dispatch_inprocess` (`wawona-dispatch.c`) |
| fastfetch | same process | - | `fastfetch_main`, `fastfetch_main_impl`, `parseConfigFiles` |
| neovim | same process | - | `wawona_nvim_main` |
| foot / waypipe | same process | - | `foot_main`, waypipe entry symbols |
| macOS app | **Wawona** | `com.aspauldingcode.Wawona` | Same in-process model + standalone binaries in bundle |

All in-process CLI tools share **one address space** with the app. A crash in
`fastfetch_main` is an app crash (`EXC_BAD_ACCESS`, `SIGBUS`, etc.). Debug the
**Wawona** process, then inspect the crashing thread's backtrace.

Primary on-device test hardware: **8amps iPhone Air** (hostname **STARDUST**,
model `iPhone18,4`). Proven for lldb-mcp root-cause work (e.g. fastfetch SIGBUS).

## Session model

Every lldb-mcp tool (except session starters) requires a **`session_id`** returned
by `lldb_start`. Multiple sessions can coexist; always track the active ID.

```
lldb_start → session_id
  → (load | attach | lldb_command setup)
  → breakpoints / run / continue
  → inspect (backtrace, print, examine, …)
  → lldb_terminate
```

Use **`lldb_list_sessions`** if unsure which sessions are active.

## Complete tool reference

### Session management

| Tool | Args | Purpose |
|------|------|---------|
| `lldb_start` | `lldb_path?` (default `lldb`), `working_dir?` | Start LLDB; returns `session_id` |
| `lldb_terminate` | `session_id` | End session |
| `lldb_list_sessions` | - | List active sessions |

Start with Xcode's LLDB on Darwin:

```
lldb_start(lldb_path="/Applications/Xcode.app/Contents/Developer/usr/bin/lldb")
```

### Load / attach / run

| Tool | Args | Purpose |
|------|------|---------|
| `lldb_load` | `session_id`, `program`, `arguments?[]` | Load binary for launch-under-debugger |
| `lldb_attach` | `session_id`, `pid` | Attach to **running** process by PID |
| `lldb_run` | `session_id` | Run loaded program |
| `lldb_load_core` | `session_id`, `program`, `core_path` | Post-mortem core analysis |
| `lldb_kill` | `session_id` | Kill inferior process |

### Execution control

| Tool | Args | Purpose |
|------|------|---------|
| `lldb_continue` | `session_id` | Continue after breakpoint/signal |
| `lldb_step` | `session_id` | Step into |
| `lldb_next` | `session_id` | Step over |
| `lldb_finish` | `session_id` | Run until current function returns |

### Breakpoints & watchpoints

| Tool | Args | Purpose |
|------|------|---------|
| `lldb_set_breakpoint` | `session_id`, `location`, `condition?` | Break on symbol or `file:line` |
| `lldb_breakpoint_list` | `session_id` | List breakpoints |
| `lldb_breakpoint_delete` | `session_id`, breakpoint id | Remove breakpoint |
| `lldb_watchpoint` | `session_id`, `expression`, `watch_type?` | Watch memory (`write` default) |

`location` examples for Wawona:

- `fastfetch_main`
- `parseConfigFiles`
- `wawona_zsh_main`
- `wawona_dispatch_inprocess`
- `WWNRootfsManager.m:301` (line breakpoint)

### Inspection

| Tool | Args | Purpose |
|------|------|---------|
| `lldb_backtrace` | `session_id`, `full?`, `limit?` | Call stack. **first tool after crash** |
| `lldb_frame_info` | `session_id` | Current frame details |
| `lldb_print` | `session_id`, `expression` | Print variable / expression |
| `lldb_expression` | `session_id`, `expression` | Evaluate in current frame |
| `lldb_examine` | `session_id`, `expression`, `format?`, `count?` | Memory dump (e.g. fault addr) |
| `lldb_info_registers` | `session_id` | Register state at stop |
| `lldb_disassemble` | `session_id`, … | Disassemble current PC |
| `lldb_process_info` | `session_id` | Process metadata |

### Threads

| Tool | Args | Purpose |
|------|------|---------|
| `lldb_thread_list` | `session_id` | All threads. Critical for in-process zsh (pthread) |
| `lldb_thread_select` | `session_id`, `thread_id` | Switch to crashing thread |

In-process zsh runs on a **worker pthread**; the crashing thread may not be the
main thread. Always `lldb_thread_list` then select the thread with the fault.

### Escape hatch

| Tool | Args | Purpose |
|------|------|---------|
| `lldb_command` | `session_id`, `command` | Run **any** LLDB command string |
| `lldb_help` | `session_id`, `command?` | LLDB built-in help |

Use `lldb_command` for iOS platform setup, device selection, and anything without
a dedicated MCP wrapper (see below).

## Workflow A. IOS physical device (primary)

Pair with **xcodebuild-mcp**: install a **Debug** build onto **8amps iPhone Air**,
launch Wawona, reproduce the bug, then attach with lldb-mcp.

### 1. Install debug build (xcodebuild-mcp)

```
session_show_defaults
session_set_defaults  → Wawona.xcodeproj, iOS scheme, 8amps iPhone Air
# build + install + launch (device workflow tools)
```

Use **Debug** configuration so symbols are present in the linked static archives
and app binary.

### 2. Start LLDB session

```
lldb_start(lldb_path="/Applications/Xcode.app/Contents/Developer/usr/bin/lldb")
→ session_id
```

### 3. Select iOS platform & attach

Via **`lldb_command`** (required for remote iOS):

```
lldb_command(session_id, "platform select remote-ios")
lldb_command(session_id, "device list")
lldb_command(session_id, "attach -n Wawona")
```

If attach by name fails, list processes on device:

```
lldb_command(session_id, "process list")
```

Then **`lldb_attach(session_id, pid=<pid>)`** with the Wawona PID.

Alternative when Xcode is already debugging (debugserver port forwarded):

```
lldb_command(session_id, "process connect connect://localhost:<port>")
```

### 4. Stop on crash or set breakpoint

**Reactive** (after user reproduces crash):

```
lldb_thread_list(session_id)
lldb_thread_select(session_id, thread_id=<crashing_thread>)
lldb_backtrace(session_id, full=true)
lldb_frame_info(session_id)
lldb_print(session_id, expression="<local_var>")
lldb_examine(session_id, expression="<fault_address>", format="x", count=16)
```

**Proactive** (before reproduce):

```
lldb_set_breakpoint(session_id, location="fastfetch_main")
lldb_continue(session_id)
# user runs `fastfetch` in shell → hits breakpoint → step/inspect
```

### 5. Clean up

```
lldb_kill(session_id)        # optional. Stops inferior
lldb_terminate(session_id)   # ends LLDB session
```

## Workflow B. MacOS local (standalone + in-process)

For macOS Wawona (Wayland path, in-process tools, standalone bundle binaries):

```
lldb_start()
lldb_load(session_id, program="/path/to/Wawona.app/Contents/MacOS/Wawona")
lldb_set_breakpoint(session_id, location="main")
lldb_run(session_id)
# … continue / inspect as above
```

macOS also runs fastfetch/neovim/zsh in-process inside the app; breakpoint targets
are the same symbols as iOS.

## Workflow C. Launch app under debugger on device

When attach-after-launch is flaky, load the device binary and run under LLDB:

```
lldb_command(session_id, "platform select remote-ios")
lldb_command(session_id, "file set --symfile /path/to/Wawona.app/Wawona")
lldb_command(session_id, "run")
```

The symfile path comes from xcodebuild DerivedData or the build products path
xcodebuild-mcp exposes. Prefer Workflow A (attach) when the app is already
installed and running.

## Wawona-specific debugging patterns

### In-process shell tool crash (fastfetch, zsh, neovim)

1. Install Debug build → launch app → open terminal → run command (`fastfetch`, etc.).
2. Attach to **Wawona** process.
3. **`lldb_thread_list`**. Find the pthread running the tool (not always thread 1).
4. **`lldb_backtrace(full=true)`** on that thread.
5. Inspect globals / structs at fault (`lldb_print`, `lldb_examine`).

**Proven example (STARDUST / iPhone Air):** second `fastfetch` run → `SIGBUS` in
`parseConfigFiles()` reading `FFstrbuf.length` at fault addr `0x1000000009` because
`configDirs.data` was a torn tagged pointer (`0x1000000005`) from singleton
re-entry after a prior fatal signal skipped cleanup. Fix landed in
`wwn-fastfetch` (`wawona_ff_inprocess.c`, idempotent `ffDestroyInstance`, guard in
`parseConfigFiles`). See `zsh-ios-appstore-compliance.md` § fastfetch lifecycle.

Breakpoint recipe to catch this class of bug early:

```
lldb_set_breakpoint(session_id, location="parseConfigFiles")
lldb_set_breakpoint(session_id, location="fastfetch_main")
lldb_watchpoint(session_id, expression="&instance.state.platform.configDirs.data", watch_type="write")
```

### zsh / dispatch path

```
lldb_set_breakpoint(session_id, location="wawona_zsh_main")
lldb_set_breakpoint(session_id, location="wawona_dispatch_inprocess")
```

Step through dispatch to see which argv0 is routed in-process vs rejected.

### UI / ObjC / Swift

```
lldb_set_breakpoint(session_id, location="-[WWNRootfsManager applyShellEnvironment]")
lldb_command(session_id, "breakpoint set --name 'WWNWaypipeRunner'")
```

Use **`lldb_backtrace`** from the main thread when the UI freezes (not a signal crash).

### Post-mortem (.ips crash report)

iOS `.ips` reports help triage but are not sufficient for in-process struct inspection.
Prefer live lldb-mcp attach. For macOS cores:

```
lldb_load_core(session_id, program="…/Wawona", core_path="/cores/core.…")
lldb_backtrace(session_id, full=true)
```

## Pairing with xcodebuild-mcp

| Step | Tool | Action |
|------|------|--------|
| 1 | xcodebuild-mcp | Debug build + install to **8amps iPhone Air** |
| 2 | xcodebuild-mcp | Launch app (or user launches manually) |
| 3 | lldb-mcp | `lldb_start` → platform select → attach |
| 4 | lldb-mcp | Breakpoint / continue / reproduce |
| 5 | lldb-mcp | `lldb_backtrace`, `lldb_print`, `lldb_examine` |
| 6 | wwn-mcp | `get_patch`, `search_code` to locate source fix |
| 7 | xcodebuild-mcp | Reinstall after fix |

**Do not skip lldb-mcp** when the bug is reproducible on device. It is the
validated debugging path for this project.

## Agent checklist

When investigating a Wawona Apple-platform bug:

- [ ] Confirm **Debug** build (not Release strip).
- [ ] Use **xcodebuild-mcp** to install on **8amps iPhone Air** unless macOS-only.
- [ ] Start **`lldb`** MCP session (`lldb_start`).
- [ ] Attach or load Wawona (`lldb_attach` / `lldb_command` platform select).
- [ ] On crash: **`lldb_thread_list`** → select fault thread → **`lldb_backtrace(full=true)`**.
- [ ] Inspect locals / memory at fault PC (`lldb_print`, `lldb_examine`).
- [ ] For in-process tools: breakpoint entry symbol (`fastfetch_main`, `wawona_zsh_main`).
- [ ] Cross-reference frames with wwn-mcp (`search_code`, `get_patch`, `read_document`).
- [ ] **`lldb_terminate`** when done.

## Troubleshooting

| Problem | Fix |
|---------|-----|
| MCP server name not found | Tool is under **`lldb`**, not `lldb-mcp` |
| `lldb_start` fails | Set `DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer` (nix-darwin does this) |
| No symbols in backtrace | Rebuild Debug; ensure dSYM / unstripped static archives linked |
| Attach denied | Device must be trusted, unlocked, Developer Mode on; app must be running |
| Wrong thread | Always `lldb_thread_list`. In-process zsh/fastfetch use worker pthreads |
| iOS platform commands missing | Use **`lldb_command`**, not only wrapper tools |
| Session ID lost | `lldb_list_sessions` |

## Quick reference

```
lldb_start → session_id
lldb_command(session_id, "platform select remote-ios")
lldb_command(session_id, "attach -n Wawona")
lldb_set_breakpoint(session_id, location="fastfetch_main")
lldb_continue(session_id)
lldb_backtrace(session_id, full=true)
lldb_print(session_id, expression="instance.state.platform.configDirs")
lldb_examine(session_id, expression="0x1000000009", format="x", count=8)
lldb_terminate(session_id)
```
