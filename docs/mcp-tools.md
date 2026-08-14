# MCP tools & resources

All tools return structured results that carry **citations** (project, path,
line range, source URL) so models can open the underlying files. Results from
search tools also include a `snippet` and a fused `score`.

## Tools

### `search(query, kind?, project?, lang?, top_k=8)`
Hybrid (semantic + lexical) search across the whole corpus. Filters:
- `kind`: `docs` | `code` | `protocol` | `patch` | `text`
- `project`: e.g. `wayland`, `wawona`, `apple`, `android`, `store-compliance`
- `lang`: e.g. `rust`, `c`, `swift`, `kotlin`, `nix`

```jsonc
// search("xdg_toplevel decoration", kind="protocol")
[{ "title": "zxdg_toplevel_decoration_v1", "project": "wayland", "kind": "protocol",
   "lines": [1, 120], "url": "https://.../xdg-decoration...xml",
   "tags": {"protocol": "xdg_decoration_unstable_v1", "stability": "unstable"},
   "citation": "wayland/protocol .../xdg-decoration-...xml:1-120", "snippet": "...", "score": 0.83 }]
```

### `search_docs(query, project?, top_k=8)`
Documentation/prose only (`kind="docs"`).

### `search_code(query, project?, lang?, top_k=8)`
Source code only.

### `find_symbol(name, project?, top_k=10)`
Find a function/type/symbol definition by name across code.

### `get_architecture(topic, top_k=8)`
Wawona architecture / multi-repo dev docs (`project` fan-out across `wawona`,
`ios-shell`, `weston`, `iland`, `waypipe`, `coreutils`, `niri`, `kmscube`,
`ssh`). Good topics: `multi-repo dev model`, `registryFragment`, `patch-overlay`,
`wwn-iland upstream`, `where to edit zsh patches`, **`lldb-mcp`**,
`ios device dev workflow`, `fastfetch in-process crash`.

### `list_repos()`
Org catalog: layer, role, when-to-edit for each `wwn-*` / Wawona / wawona.io.

### `where_to_edit(change)`
Map a natural-language change (`zsh patch`, `ANGLE`, `niri recipe`,
`Machines UI`) to the correct repo.

### `get_capability(platform, feature)`
Four-state gate (`available` | `planned` | `blocked` | `forbidden`) for a
platform + feature (e.g. `watchos` + `gpu`, `visionos` + `vm`).

### `list_projects()`
Indexed projects + chunk counts: `[{ "project": "...", "chunks": N }]`.

### `list_protocols(family?, stability?)`
List Wayland protocols, optionally filtered:
`[{ "protocol": "...", "stability": "wlr", "source": "wlr-protocols" }]`.

### `get_protocol(name)`
A protocol's interfaces/requests/events/enums by name (returns the protocol
chunks with citations).

### `list_patches()`
Every patched upstream across **Wawona + all `wwn-*` repos**, derived from each
repo's `dependencies/` tree:
```jsonc
[{ "repo": "wwn-weston", "key": "wwn-weston/clients/weston", "software": "clients/weston",
   "name": "weston", "category": "clients",
   "platforms": ["android","ios","macos", ...],
   "patch_files": ["wwn-weston/dependencies/clients/weston/terminal-patches/patch-terminal.py", ...],
   "inline_patches": ["wwn-weston/dependencies/clients/weston/ios.nix", ...] }]
```

### `get_patch(software)`
Patch detail by short name (`weston`, `zsh`) or repo-qualified (`wwn-zsh/zsh`,
`wwn-weston/clients/weston`). Returns `{ repo, key, software, name, category,
platforms, patch_files, inline_patches, recipes }`, or `{ error, available }` if
unknown (or `{ ambiguous, matches }` if the short name hits multiple repos).

### `read_document(ref, start?, end?)`
Read a chunk by `chunk_id`, or a file by `source/relative/path` with an optional
1-based line range.

## Resources

| URI | content |
|-----|---------|
| `wwn://status` | index stats, `last_indexed`, source SHAs, embed backend, transport=`stdio` |
| `wwn://patches` | the full patched-software inventory (JSON) |

## CLI equivalents

The same retrieval is available from the terminal for debugging:

```bash
wwn-mcp search "liquid glass material" --kind docs -k 5
wwn-mcp search "wl_surface commit" --kind protocol --json
wwn-mcp search "lldb_set_breakpoint fastfetch_main" --project wawona -k 5
wwn-mcp info        # resolved settings + index stats
```

## Developer-local companion MCP (not wwn-mcp tools)

These run on the developer Mac via `.cursor/mcp.json` (nix-darwin wires them).
They are **not** served by wwn-mcp, but RAG indexes how to use them:

| MCP name | Package | Role |
|----------|---------|------|
| `xcodebuild` | XcodeBuildMCP | Build, install, run on simulator/device |
| `lldb` | [lldb-mcp](https://github.com/stass/lldb-mcp) | LLDB sessions: attach, breakpoints, backtrace, memory |
| `nixos` | MCP-NixOS | Live nixpkgs/options (stdio via `uvx mcp-nixos`) |

Query wwn-mcp RAG for **`lldb-mcp-apple-device-debugging`** or
**`ios-device-dev-workflow`** before debugging Wawona on Apple hardware.
