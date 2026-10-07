# Wawona Ports (catalog naming and versions)

Almost every package on `repo.wawona.io` is a **port** of existing software.

## Laws

- Package `name`: upstream name for ports; distinct unbranded name for scratch.
  Never `wawona-` / `wwn-` prefix or `-wawona` / `-wwn` suffix.
- Port `version`: the upstream release/tag that was ported. Never invent
  `0.1.0` because the port just landed on Wawona. Require `upstream_version`
  equal to `version`. Set `upstream_is_bootstrap` only when upstream itself
  publishes that bootstrap version.
- Field **`homepage`**: upstream project URL (nixpkgs `meta.homepage`). Not
  `website`. Never a blanket `wawona.io/docs/wasm/` for every row.
- Field **`source`**: the port / packaging tree used to build the catalog row.
- A short reimplementation is not a port of GNU sed / jqlang jq. Keep stubs
  out of the live index until the real upstream tree is packaged.

## Where

- Rule: `repo.wawona.io/.cursor/rules/repo-wawona-io-ports.mdc`
- Gate: `repo.wawona.io/scripts/check-packages.py`
- Builds: `wasm-packages/docs/package-versioning.md` + `allowlist.toml`

Exception: reverse-DNS first-party Mode B app ids
(`com.aspauldingcode.wawona.modeb.demo`).
