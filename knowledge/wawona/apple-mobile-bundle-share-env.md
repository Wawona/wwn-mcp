# Apple mobile bundle share env

In-process weston on Apple mobile needs process env for bundled `share/`:

- `WESTON_DATA_DIR` → `…/Wawona.app/share/weston` (not `/usr/share/weston`)
- `FONTCONFIG_FILE` / `FONTCONFIG_PATH` → runtime `fonts.conf` under `XDG_RUNTIME_DIR`
- `WAWONA_MONO_FONT` / `WAWONA_SANS_FONT` → bundled DejaVu under `share/fonts`

Code: `Wawona/Sources/WawonaApple/Shell/BundleShareEnvironment.swift`.
Call after `XDG_RUNTIME_DIR`, before `weston_compositor_main`.
Watch used to be the only path; iOS Start must call the same helper.

Symptom when missing: `FONTCONFIG_FILE=(unset)`, missing `terminal.png` /
`pattern.png` under `/usr/share/weston`, blank panel text.

Rule: `wawona-apple-mobile-bundle-share-env`.
Android: `android_jni.c` shell env (same contract).
