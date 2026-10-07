# iOS link contract

`scripts/xcode-prebuild.sh` runs `scripts/verify-link-contract.py` before the
Apple app compile.

Membership: every file the xcodegen source globs would compile for the target
must be in that target's Sources phase. A dropped `.m` or `.swift` shows up
later as an undefined ObjC class or Swift type.

Symbols: every Relay C ABI function the target calls, and every non-weak
`extern` that is actually used, must occur as an exported name in an archive
on that SDK's link line (`libwawona.a` included). Weak shims and declarations
that nothing calls are not required. Apple `nm` cannot read Rust nightly
objects, so the check searches the archive bytes.

Measured miss, 2026-10-04: simulator `Ld` undefined `_wwn_waypipe_client_fd`
because the linked `libwawona.a` was built from waypipe that does not define
it. The contract fails that symbol before compile. Do not stub it. Rebuild
the iOS backend from waypipe that exports `wwn_waypipe_client_fd`.

A stale `.nix-deps` `libwawona_relay.a` misses `relay_nix_editor` and
`relay_start_host_waypipe` the same way.
