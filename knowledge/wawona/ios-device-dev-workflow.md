# iOS device development workflow (high priority)

**Authoritative operational guide** for building, installing, and debugging Wawona on
physical Apple hardware. Agents should follow this end-to-end. It is the proven path.

## MCP stack (developer-local, macOS)

These MCP servers are **not** a remote hosted service. They run on the developer Mac
(stdio / local process), same as wwn-mcp itself.
via nix-darwin (`modules/apps/_ide-mcp.nix`) and are wired into Cursor/Antigravity
`.cursor/mcp.json`:

| MCP | Role |
|-----|------|
| **wwn-mcp** | RAG over Wawona + `wwn-*` repos (this document) |
| **nixos** | Live nixpkgs/options lookup (MCP-NixOS) |
| **xcodebuild** | Build, install, and run on simulator **or device** (XcodeBuildMCP) |
| **lldb** | Attach, breakpoints, backtraces, expression eval on device (**lldb-mcp**) |

Pair **xcodebuild-mcp** (install) with **lldb-mcp** (debug). That combination on the
primary dev device is sufficient to validate iOS fixes.

**Full lldb-mcp guide:** `knowledge/wawona/lldb-mcp-apple-device-debugging.md`. Complete
tool catalog, iOS attach workflow, Wawona symbol breakpoints, in-process pthread debugging,
and the proven fastfetch SIGBUS investigation on STARDUST.

## Primary test device

| Field | Value |
|-------|-------|
| Device name | **8amps iPhone Air** (host name **STARDUST**) |
| Model identifier | `iPhone18,4` |
| Use case | Default on-device install + LLDB debug target for Wawona iOS |

When automating via xcodebuild-mcp, select this device for install/run. When debugging
via lldb-mcp, attach to the Wawona process on this device after install.

## Step 1. Enter the dev shell (Xcode signing)

From the **Wawona integration repo** (`~/Wawona/Wawona`):

```bash
cd ~/Wawona/Wawona
nix develop
```

The Darwin dev shell (`dependencies/wawona/devshells.nix`) automatically:

- Loads **`TEAM_ID`** from `.envrc` (currently `G6EJA4DJKW`) and exports
  **`DEVELOPMENT_TEAM`** for codesigning.
- Locates Xcode via `find-xcode`, sets **`DEVELOPER_DIR`**, and puts `xcodebuild` on
  **`PATH`**.

For signed release artifacts (IPA), export `TEAM_ID` and build with **`--impure`** so
Nix can see the team id:

```bash
TEAM_ID=G6EJA4DJKW nix build .#wawona-ios-ipa --impure
```

**Rule:** always work inside `nix develop` (or a child shell that inherited its env)
when driving xcodebuild, xcodegen, or MCP build tools. Do not rely on a bare shell
missing `DEVELOPMENT_TEAM` / `DEVELOPER_DIR`.

## Step 2. Regenerate the Xcode project

After Nix recipe changes (new static libs, ldflags, embedded rootfs, framework lists),
regenerate `.xcodeproj` from the Wawona flake:

```bash
# all Apple targets (CI default)
nix run .#xcodegen

# faster iteration. IOS + iPadOS only
nix run .#xcodegen-ios

# macOS only
nix run .#xcodegen-macos
```

Implementation: `dependencies/generators/xcodegen.nix` → `project.yml` → XcodeGen.
Output: `dependencies/generators/xcodegen/output/Wawona.xcodeproj`.

When `TEAM_ID` is set, xcodegen injects `DEVELOPMENT_TEAM` into iOS/iPadOS/tvOS
targets automatically.

For UI-only Swift/ObjC edits without dependency changes:

```bash
export WAWONA_SKIP_NIX_PREBUILD=1   # skip full Nix prebuild; faster UI loop
```

## Step 3. Build and install on device (xcodebuild-mcp)

Use **XcodeBuildMCP** (`xcodebuild` tools). Not raw shell `xcodebuild` unless MCP is
unavailable.

Typical agent flow:

1. **`session_show_defaults`**. Confirm project, scheme, and device defaults.
2. **`session_set_defaults`**. Point at `Wawona.xcodeproj`, the iOS scheme, and the
   **8amps iPhone Air** device.
3. Build + install to device (device workflow tools; enable device capability in
   XcodeBuildMCP config if tools are missing).
4. Capture logs / verify launch on device.

Requires macOS + Xcode 16+ and a USB/Wi‑Fi paired, trusted device.

## Step 4. Debug on device (lldb-mcp)

After xcodebuild-mcp installs a **Debug** build, use the **`lldb`** MCP server
(lldb-mcp from [stass/lldb-mcp](https://github.com/stass/lldb-mcp)). Cursor exposes
28 tools; every command needs a `session_id` from `lldb_start`.

Minimal attach flow on **8amps iPhone Air**:

1. **`lldb_start`**. Use Xcode's LLDB:
   `lldb_path=/Applications/Xcode.app/Contents/Developer/usr/bin/lldb`
2. **`lldb_command`**. `platform select remote-ios`, then `attach -n Wawona`
   (or `lldb_attach` with PID from `process list`).
3. Reproduce the bug (e.g. run `fastfetch` twice in the in-process shell).
4. **`lldb_thread_list`** → select the crashing pthread (in-process tools rarely
   crash on the main thread).
5. **`lldb_backtrace(full=true)`** → **`lldb_print`** / **`lldb_examine`** at fault.
6. Set proactive breakpoints (`lldb_set_breakpoint` on `fastfetch_main`,
   `wawona_zsh_main`, `wawona_dispatch_inprocess`) before reproduce when possible.
7. **`lldb_terminate`** when done.

Wawona bundle ID: **`com.aspauldingcode.Wawona`**. Process name: **Wawona**.

This is how in-process crashes (e.g. fastfetch `SIGBUS` in `parseConfigFiles` on
STARDUST / `iPhone18,4`) were root-caused. **Always prefer lldb-mcp over `.ips`
crash logs alone**. Live attach exposes struct fields and fault addresses.

See **`lldb-mcp-apple-device-debugging.md`** for the full tool reference, macOS
workflow, watchpoints, and agent checklist.

## Applying `wwn-fastfetch` (and other `wwn-*`) changes

Wawona consumes `wwn-fastfetch` as a **flake input** (`flake.nix` →
`inputs.wwn-fastfetch.url = "github:Wawona/wwn-fastfetch"`). Local edits in
`~/Wawona/wwn-fastfetch` do **not** affect Wawona builds until one of:

### Option A. Local input override (fast iteration)

Point the Wawona flake at the sibling checkout without pushing:

```bash
cd ~/Wawona/Wawona
nix run .#xcodegen-ios \
  --override-input wwn-fastfetch "path:../wwn-fastfetch"

# or for a full build:
nix build .#wawona-ios \
  --override-input wwn-fastfetch "path:../wwn-fastfetch" --impure
```

Same pattern works for any `wwn-*` input (see
`.github/scripts/nix-build-android-meson-sandbox-gate.sh` for
`WWN_TOOLCHAIN_ROOT` / `WWN_WESTON_ROOT` env-var style).

### Option B. Push upstream + flake lock (shared/CI path)

1. Commit and push changes to **`github.com/Wawona/wwn-fastfetch`** (`main`).
2. In Wawona, advance the input pin:

   ```bash
   cd ~/Wawona/Wawona
   nix flake lock --update-input wwn-fastfetch
   ```

3. Regenerate Xcode project (`nix run .#xcodegen-ios`) and rebuild.

**Rule:** if you skip both override and lock update, Wawona still builds the **old**
pinned fastfetch from `flake.lock`. A common source of “fix didn't land” confusion.

After fastfetch recipe changes, also verify:
`wwn-fastfetch/.github/scripts/verify-fastfetch-ios-patches.py`.

## Updating this RAG knowledge (wwn-mcp)

Curated docs live in **`wwn-mcp/knowledge/`**, indexed as corpus source
`wwn-knowledge-wawona` (`corpus.toml`).

Deploy path after editing knowledge:

1. Commit and **push to `origin/main`** on `github.com/Wawona/WWN-MCP`.
2. On the dev Mac, pull the updated checkout:

   ```bash
   cd ~/Wawona/wwn-mcp && git pull
   ```

3. Re-index locally (or wait for the server timer):

   ```bash
   nix run .#wwn-mcp -- fetch --only wwn-knowledge-wawona
   nix run .#wwn-mcp -- index --only wwn-knowledge-wawona
   ```

4. Refresh nix-darwin so IDE MCP configs pick up any module changes:

   ```bash
   # dotfiles live at /etc/nix-darwin/.dotfiles/
   nh switch mba
   ```

   `dendritic.ide.mcp.wwnMcpFlake` defaults to `~/Wawona/wwn-mcp`; the pulled
   checkout + re-index is what makes new knowledge visible to Cursor agents.

## Quick reference

| Goal | Command / tool |
|------|----------------|
| Signed dev env | `nix develop` in `~/Wawona/Wawona` |
| Regenerate Xcode project | `nix run .#xcodegen-ios` |
| Local fastfetch changes | `--override-input wwn-fastfetch path:../wwn-fastfetch` |
| Shared fastfetch changes | push `wwn-fastfetch` → `nix flake lock --update-input wwn-fastfetch` |
| Install to device | xcodebuild-mcp → **8amps iPhone Air** |
| Debug on device | `lldb` MCP: start → attach Wawona → backtrace (see lldb-mcp guide) |
| Refresh agent knowledge | push wwn-mcp → pull → re-index → `nh switch mba` |
