# Deployment (home-manager / dendritic stdio)

WWN-MCP is a **stdio** MCP server. Any MCP host spawns the `wwn-mcp` binary on
PATH — the same host model as
[mcp-nixos](https://github.com/utensils/mcp-nixos) (`uvx mcp-nixos`).

There is **no** Caddy, Bearer token, Streamable HTTP, or `mcp.wawona.io`.
That hostname was never deployed; do not configure clients against it.

## home-manager

```nix
{
  inputs.wwn-mcp.url = "github:Wawona/WWN-MCP";

  # in your homeConfiguration modules:
  imports = [ inputs.wwn-mcp.homeModules.wwn-mcp ];

  programs.wwn-mcp = {
    enable = true;
    # dataDir / corpusManifest / reindex.onCalendar have sensible defaults
  };
}
```

This installs `wwn-mcp` on PATH and sets `WWN_MCP_DATA_DIR` /
`WWN_MCP_CORPUS_TOML`. On Linux it also installs a user systemd timer that
periodically `fetch` + `index`s. On Darwin, reindex with:

```bash
wwn-mcp fetch && wwn-mcp index
# or knowledge-only:
wwn-mcp index --knowledge
```

## Dendritic / IDE hosts

Prefer a PATH binary once home-manager (or `nix profile install`) provides it:

```json
{ "mcpServers": {
    "wwn-mcp": { "command": "wwn-mcp" },
    "nixos": { "command": "uvx", "args": ["mcp-nixos"] }
} }
```

Until the package is on PATH, `nix run` still works (no `--transport` flag):

```json
{ "mcpServers": {
    "wwn-mcp": {
      "command": "nix",
      "args": ["run", "/path/to/wwn-mcp#wwn-mcp"],
      "env": {
        "WWN_MCP_DATA_DIR": "/Users/you/.local/share/wwn-mcp",
        "WWN_MCP_CORPUS_TOML": "/path/to/wwn-mcp/corpus.toml"
      }
    }
} }
```

## First index

On first `wwn-mcp` / `serve`, an empty index automatically indexes shipped
`knowledge/` so contribute/DAG/capability tools answer immediately. Expand:

```bash
wwn-mcp fetch                 # clone git / crawl web sources
wwn-mcp index                 # full corpus
wwn-mcp index --local-siblings  # only local paths under ~/Wawona/
```

## CI status

GitHub Actions workflow **MCP** builds and smokes the package with Nix on
**macOS** and **Linux** (ubuntu + Nix). The README badge is that workflow.
