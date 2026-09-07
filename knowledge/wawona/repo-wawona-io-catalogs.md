# repo.wawona.io catalogs

One host. Two catalogs. Never one results list.

| Lane | Humans | Machines | Who |
|------|--------|----------|-----|
| Mode A wasm | `/search/?channel=wasm` | `/wasm/v1/index.json` (`wpm`) | App Store / Play / macOS |
| Mode B debs | `/search/?channel=deb` | APT at `https://repo.wawona.io/` (`Packages`) | Sileo / Termux |

`/wasm/`, `/deb/`, and `/jailbreak/` are HTML landings onto `/search/`. They are
not mixed indexes. APT does **not** live under `/jailbreak/`. Store `wpm` must
never fetch `/jailbreak/`, `/Packages`, or `.deb`.

Repo: `github.com/Wawona/repo.wawona.io`. Site docs: wawona.io `/docs/packages/`.

Cursor agents: read `repo.wawona.io/.cursor/skills/repo-wawona-io-priors/SKILL.md`
first. Write new catalog learnings into those skills. `where_to_edit` must match
`repo.wawona.io` before `wawona.io` (the website regex must not eat the catalog
host).
