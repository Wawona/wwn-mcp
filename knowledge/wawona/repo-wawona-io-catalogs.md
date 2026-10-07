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

## Wasm auto-growth (Wawona/wasm-packages)

Production P1 builds: **`Wawona/wasm-packages`** GHA (`ubuntu-24.04`).

Curated `allowlist.toml` → GHA nightly/stale build → `publish-to-repo.yml`
pushes `wasm/v1` on **development** (`WAWONA_REPO_TOKEN` / wawona-wasm-bot).
Pages deploys `development`. This host only catalogs `/wasm/v1`.

Hard rejects: laptop-built blobs as production; revive `nixpkgs2wasi`;
auto-mirror nixpkgs; mix wasm + deb search lists.
