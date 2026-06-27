# Contributing

WWN-MCP is open source under the MIT License. Contributions welcome.

## Add a corpus source

Edit [`corpus.toml`](../corpus.toml) — add a `[[source]]` block (see
[corpus.md](corpus.md) for the schema). No code change is required. Then:

```bash
wwn-mcp fetch --only <name>
wwn-mcp index --only <name>
wwn-mcp search "<something in that source>"
```

If the upstream URL is unconfirmed, ship it `enabled = false` with a comment so
`fetch` skips it cleanly until verified.

## Add or tune a chunker

Chunkers live in `src/wwn_mcp/chunk.py`, dispatched by extension in `_kind_for`:

- markdown → `_chunk_markdown` (by heading)
- code → `_chunk_code` (symbol-aware, windowing fallback)
- Wayland `.xml` → `_chunk_protocol` (one chunk per `<interface>`)
- `.patch` → whole-file
- html/text/json → `_chunk_text`

Keep `Chunk` fields populated (project/path/line-range/kind/lang/tags + a content
hash and a citation URL via `_cite_url`).

## Add an MCP tool

Tools are registered in `src/wwn_mcp/server.py` with `@mcp.tool()`. Reuse
`Store` for retrieval and `_fmt` so results keep consistent citations. Document
the new tool in [mcp-tools.md](mcp-tools.md).

## Run checks

```bash
ruff check src
pytest -q
nix flake check          # evaluates package, app, nixosModule
nix build .#wwn-mcp      # builds the package
```

## Conventions

- Python ≥ 3.11, stdlib-first; heavy deps (`fastembed`, `sqlite-vec`) are
  optional with graceful fallbacks so the tool always runs.
- Keep the README minimal; real docs live in `docs/` and must stay in sync with
  the code.
- Public/MIT hygiene: never vendor fetched third-party docs/source into the repo
  (they belong in the `.gitignore`d runtime data dir).
