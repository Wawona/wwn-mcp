# Agent learn loop (skills + RAG)

Indexed summary for WWN-MCP. Full copies:

- Cursor rule: `wawona-agent-learn` (`alwaysApply`)
- Tracked: `Wawona/docs/agent-rules/wawona-agent-learn.md`
- Skills: `Wawona/docs/agent-skills/` (`wawona-rag`, `wawona-write`,
  `wawona-learn`, `wawona-caveman`, `wawona-priors`)

## Always

1. Query **wwn-mcp** before coding (`where_to_edit`, `get_capability`,
   `search_docs` / `search_code`). Trust citations over priors.
2. Read matching `.cursor/skills/wawona-*`. Index in `wawona-priors`.
   Catalog host: `repo.wawona.io/.cursor/skills/repo-wawona-io-priors`.
   `where_to_edit` must not treat `repo.wawona.io` as the `wawona.io` website.
3. Software must **improve on** documented prior knowledge. Do not re-ship a
   rejected path (Mode B in store, DAG invert, KMS-rehost of a Wayland client,
   `watchdogd` Take Over without Path B ACK).
4. After a durable finding: update skill + rule mirrors + this `knowledge/wawona/`
   tree, then reindex.

## Reindex

```bash
cd ~/Wawona/wwn-mcp
nix run .#wwn-mcp -- index --only wwn-knowledge-wawona
# or: nix run .#wwn-mcp -- index --local-siblings
```

## Token voice

Caveman **lite** in user chat (full sentences, no filler). **full** in notes.
Code, commits, PRs: normal English. No em dash.

## Do not

- Skip RAG because a Cursor rule is already in context
- Duplicate a whole rule body into a skill (pointer + delta)
- Leave a new hard reject only in chat
