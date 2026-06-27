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
Wawona architecture/ADR docs explaining intent for a topic (`project="wawona"`,
`kind="docs"`).

### `list_projects()`
Indexed projects + chunk counts: `[{ "project": "...", "chunks": N }]`.

### `list_protocols(family?, stability?)`
List Wayland protocols, optionally filtered:
`[{ "protocol": "...", "stability": "wlr", "source": "wlr-protocols" }]`.

### `get_protocol(name)`
A protocol's interfaces/requests/events/enums by name (returns the protocol
chunks with citations).

### `list_patches()`
Every upstream Wawona patches for Apple/Android, derived from `dependencies/`:
```jsonc
[{ "software": "clients/weston", "name": "weston", "category": "clients",
   "platforms": ["android","ios","macos", ...],
   "patch_files": ["dependencies/clients/weston/terminal-patches/patch-terminal.py", ...],
   "inline_patches": ["dependencies/clients/weston/ios.nix", ...] }]
```

### `get_patch(software)`
Patch detail for one upstream by name or `category/name` (e.g. `weston`, `zsh`,
`waypipe`). Returns `{ software, name, category, platforms, patch_files,
inline_patches, recipes }`, or `{ error, available }` if unknown.

### `read_document(ref, start?, end?)`
Read a chunk by `chunk_id`, or a file by `source/relative/path` with an optional
1-based line range.

## Resources

| URI | content |
|-----|---------|
| `wwn://status` | index stats (chunk counts by kind/project, vector backend) |
| `wwn://patches` | the full patched-software inventory (JSON) |

## CLI equivalents

The same retrieval is available from the terminal for debugging:

```bash
wwn-mcp search "liquid glass material" --kind docs -k 5
wwn-mcp search "wl_surface commit" --kind protocol --json
wwn-mcp info        # resolved settings + index stats
```
