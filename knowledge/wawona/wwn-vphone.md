# wwn-vphone

L3′ **nixpkgs-only** jailbroken iOS research lab for Wawona Mode B.

Repo: https://github.com/Wawona/wwn-vphone

```bash
nix run github:Wawona/wwn-vphone#vphone-jb-lab
```

Follows upstream vphone-cli (download IPSW, create, CFW `jb`, launch, SSH).
**Never** ships a prebuilt iOS VM / `Disk.img` / IPSW in git or Releases.

Operator gates (checked, not mutated): SIP fully disabled, `allow-research-guests`,
`amfi_get_out_of_my_way=1`.

Wawona (L4) re-exports `.#vphone-jb-lab` / `.#vphone-cli` via flake input
`wwn-vphone`. See `docs/wwn-repo-dag.md`.
