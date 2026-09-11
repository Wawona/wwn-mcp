# GitHub CLI (`gh`)

Indexed mirror of `Wawona/docs/agent-rules/wawona-gh.md`.
Cursor rule: `wawona-gh`. Skill: `wawona-gh`.

Cursor has **no GitHub MCP**. Agents run `gh` with the **Shell** tool. Auth is
the operator `gh auth` (keychain) or `GH_TOKEN`. MCP `PATH` in
`~/.cursor/mcp.json` is stripped. Login zsh PATH is what finds Homebrew `gh`.

Product issue tracker: `github.com/Wawona/Wawona/issues`. Repo
`github.com/Wawona/issues` does not exist (404).

Git authorship (no Cursor `Co-authored-by`) is not a ban on `gh`.
WebFetch GET cannot create milestones or issues.

Related: `wawona-branch-workflow`, `wawona-github-funding`,
`wawona-discord-github-webhook`.
