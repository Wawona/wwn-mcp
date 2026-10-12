# Flake consumer rename cascade (2026-10-12)

When a flake input or GitHub repo renames (example: `wwn-iland` →
`Wawona/iLand`, input `iland`), every consumer tip and Wawona lock must
move in the same campaign. Registry package keys may stay `iland`.

## Failure

Wawona followed `iland`, but `flake.lock` still pinned
`wwn-waypipe` before that repo renamed its outputs argument. Eval:

```text
function 'outputs' called without required argument 'wwn-iland'
```

FlakeHub pins of the new name can lag GitHub `development`.

## Fix pattern

1. Push renamed source flake.
2. Push each L3′ consumer (`wwn-waypipe`, `wwn-igetty`, …) with the new
   input name.
3. On Wawona: update lock + `*.inputs.iland.follows = "iland"` (or the
   new name). Prefer `github:Wawona/…/development` until FlakeHub catches up.
4. Prove with `nix flake metadata` (nested `follows`, no old required arg).

Skill: `wawona-flake-consumer-rename`. DAG: `wwn-repo-dag.md`.
