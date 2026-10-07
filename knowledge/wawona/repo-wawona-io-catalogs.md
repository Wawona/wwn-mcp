# repo.wawona.io catalogs

One host. Two catalogs. Never one results list.

App Store / Play compliance is **wasm only**. Deb APT has two audiences. Never
call Termux jailbreak.

| Catalog | Humans | Machines | Who |
|---------|--------|----------|-----|
| wasm | `/search/?channel=wasm` | `/wasm/v1/index.json` (`wpm`) | App Store / Play |
| debs | `/search/?channel=deb` | APT at `https://repo.wawona.io/` (`Packages`) | See audiences below |

| Deb audience | Client | Architecture | Jailbreak? | Store/Play? |
|--------------|--------|--------------|------------|-------------|
| Jailbroken iOS | Sileo / Zebra | `iphoneos-arm64` rootless, `iphoneos-arm` rootful, optional RootHide | Yes | No |
| Sideloaded Android | Termux `apt` | `aarch64` | **No** | **No** |

`/wasm/`, `/deb/`, `/jailbreak/` (Sileo iOS), and `/termux/` (Termux Android) are
HTML landings onto `/search/`. APT does **not** live under `/jailbreak/`. Store
`wpm` must never fetch `/jailbreak/`, `/termux/`, `/Packages`, or `.deb`.

Repo: `github.com/Wawona/repo.wawona.io`. Site docs: wawona.io `/docs/packages/`.

Cursor agents: read `repo.wawona.io/.cursor/skills/repo-wawona-io-priors/SKILL.md`
first. Write new catalog learnings into those skills. Never lump Sileo and
Termux as one jailbreak product. `where_to_edit` must match `repo.wawona.io`
before `wawona.io`.

Wasm ABI labels and later Wasmer/WebC/wasinix:
[`wasm-abi-registry.md`](./wasm-abi-registry.md) and
`repo.wawona.io/docs/wasm-abi.md`.

## Wasm builds (two lanes)

| Lane | Repo | Lands here |
|------|------|------------|
| Store P1 | `Wawona/wasm-packages` GHA | `/wasm/v1` |
| Nixpkgs → WASIX | `Wawona/wasinix` | Wasmer/WebC (not Pulley P1 rows) |

Law: `wawona-wasm-cli-ports`. P1: curated `allowlist.toml` → GHA →
`publish-to-repo.yml` → `development`. Pages deploys `development`.

Hard rejects: laptop blobs; revive `nixpkgs2wasi`; auto-mirror nixpkgs; stub
CLIs under upstream names; mix wasm + deb search lists; claim WASIX on Pulley.

## Wawona Ports

Ports use the upstream software version, name, and `homepage` (nixpkgs-style).
Never invent `0.1.0` for "just ported". Never brand with `wawona-` / `wwn-`.
Never blanket-link every package to `wawona.io/docs/wasm/`. Require
`homepage` + `source`. Stubs are not ports. See
[`wawona-ports.md`](./wawona-ports.md) and rule `repo-wawona-io-ports`.
