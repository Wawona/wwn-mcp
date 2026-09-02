# agent-device Wawona fork

Repo: https://github.com/Wawona/agent-device (`development`, version `0.18.3-wawona.N`).

MCP tool namespace in Cursor: **`agent-device`** / `user-agent-device`.

vphone Mode B packaging:

```bash
agent-device help vphone-packages
agent-device packages status --device "vphone wawona-jb"
agent-device packages tipa install ./App.tipa --open --jit
agent-device packages apt install ./pkg.deb
agent-device packages debug attach com.example.app
```

Lab prerequisite: `nix run github:Wawona/wwn-vphone#vphone-jb-lab`.

Rebuild MCP: `nix build github:Wawona/agent-device#agent-device` (or local
`pnpm build` + path wrapper), then **MCP: Restart Servers** in Cursor.
