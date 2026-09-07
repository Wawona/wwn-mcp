# Agent notes

## Product boundaries

RAG must match product map. See .cursor/rules/wawona-product-map.mdc

Agent learn loop: query wwn-mcp, use `.cursor/skills/wawona-*`, capture new
findings into `knowledge/wawona/` and reindex. See `knowledge/wawona/agent-learn.md`.
`where_to_edit("repo.wawona.io …")` is the catalog host, not the `wawona.io`
website. Catalog skills live in `repo.wawona.io/.cursor/skills/`.

Canonical Wawona docs: https://github.com/Wawona/Wawona/blob/development/docs/mode-a-b.md
