# Deployment (NixOS, mcp.wawona.io)

WWN-MCP ships a NixOS module (`nixosModules.wwn-mcp`) that runs the server as a
hardened systemd service behind a Caddy reverse proxy terminating TLS at
`mcp.wawona.io`, with a periodic re-index timer that does an atomic DB swap.

## Add the flake input

```nix
{
  inputs.wwn-mcp.url = "github:Wawona/WWN-MCP";

  outputs = { nixpkgs, wwn-mcp, ... }: {
    nixosConfigurations.mcp-host = nixpkgs.lib.nixosSystem {
      system = "x86_64-linux";
      modules = [
        wwn-mcp.nixosModules.wwn-mcp
        ({ ... }: {
          services.wwn-mcp = {
            enable = true;
            domain = "mcp.wawona.io";
            tokenFile = "/run/secrets/wwn-mcp.env";   # contains WWN_MCP_TOKEN=...
            corpusManifest = ./corpus.server.toml;    # see note below
            reindex.onCalendar = "daily";
          };
          # Caddy needs an ACME email for TLS.
          security.acme.acceptTerms = true;
          security.acme.defaults.email = "admin@wawona.io";
          networking.firewall.allowedTCPPorts = [ 80 443 ];
        })
      ];
    };
  };
}
```

## Options (`services.wwn-mcp`)

| option | default | purpose |
|--------|---------|---------|
| `enable` | false | turn the service on |
| `package` | flake's `wwn-mcp` | the package to run |
| `domain` | `mcp.wawona.io` | TLS hostname served by Caddy |
| `host` / `port` | `127.0.0.1` / `8765` | local bind for the MCP server |
| `dataDir` | `/var/lib/wwn-mcp` | corpus cache + sqlite index |
| `corpusManifest` | bundled `corpus.toml` | source manifest |
| `model` | `BAAI/bge-small-en-v1.5` | embedding model (hashing fallback) |
| `tokenFile` | null | file with `WWN_MCP_TOKEN=…` for Bearer auth at the proxy |
| `reindex.enable` / `reindex.onCalendar` | true / `daily` | periodic re-index |
| `proxy.enable` | true | run the Caddy TLS + Bearer reverse proxy |
| `nixos.enable` | true | co-host the MCP-NixOS companion server |
| `nixos.package` | `inputs.mcp-nixos` flake pkg | the mcp-nixos package to run |
| `nixos.port` | `8001` | local bind for the companion server |
| `nixos.path` | `/nixos/mcp` | its HTTP MCP endpoint under `domain` |

## Server-tuned corpus manifest

The bundled `corpus.toml` has a `wawona` **local** source (`../Wawona`) meant for
developer checkouts. On the server there is no such checkout, so provide a
manifest where the Wawona source is a **git** entry (enable `wawona-git`, disable
the local `wawona`), and pin `nixpkgs` `ref` to Wawona's `flake.lock` rev. Point
`corpusManifest` at that file.

## What the service does

- `wwn-mcp.service` runs `wwn-mcp serve --transport http` bound to localhost.
  Hardening: `DynamicUser`, `StateDirectory=wwn-mcp`, `ProtectSystem=strict`,
  `PrivateTmp`, `RestrictAddressFamilies`, `SystemCallFilter=@system-service`.
- `wwn-mcp-reindex.service` (+ timer) runs `fetch` then `index --reset` into a
  staging DB (`index.build.sqlite`), then `mv` over `index.sqlite` and
  `try-restart`s the server — so reads never see a half-written index.
- Caddy serves `domain` over TLS; when `tokenFile` is set it rejects requests
  without `Authorization: Bearer <token>` (401) and reverse-proxies the rest:
  `/nixos/mcp*` → the companion MCP-NixOS server, everything else → wwn-mcp.
- `mcp-nixos.service` (when `nixos.enable`) runs the
  [MCP-NixOS](https://github.com/utensils/mcp-nixos) companion over HTTP
  (`MCP_NIXOS_TRANSPORT=http`, `MCP_NIXOS_STATELESS_HTTP=1`) bound to localhost,
  hardened like the main service. It queries upstream Nix services live, so it
  needs network egress but no local index. Its package comes from the
  `mcp-nixos` flake input (which `follows` this flake's `nixpkgs`).

After deploy you get two MCP endpoints on the one host:
`https://mcp.wawona.io/mcp` (WWN-MCP) and `https://mcp.wawona.io/nixos/mcp`
(MCP-NixOS), both behind the same TLS + Bearer.

## First index

The first `wwn-mcp-reindex` run fetches the whole corpus (large; `nixpkgs` is
scoped). Trigger it immediately instead of waiting for the timer:

```bash
sudo systemctl start wwn-mcp-reindex.service
journalctl -u wwn-mcp-reindex -f
```

## Hermetic embedding model (optional)

`nix build .#wwn-mcp-model` pins the BGE-small ONNX model via `fetchurl`. Set
the real hash once (the flake ships `lib.fakeHash`; build once and copy the hash
Nix reports), then wire `FASTEMBED_CACHE_PATH`/`model` to use it offline. Without
this, fastembed fetches the model on first index (needs network), and if
fastembed is unavailable the server falls back to the hashing embedder.
