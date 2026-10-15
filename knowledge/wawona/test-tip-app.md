# Tip Wawona app for testing

Authority: `Wawona/docs/agent-rules/wawona-test-tip-app.md`, Cursor rule
`wawona-test-tip-app`, skill `wawona-appium`.

Every Appium, agent-device, and local smoke that launches the Wawona host
must **tip-build** and **clean-launch**. Never a stale install.

## macOS

```bash
eval "$(Wawona/scripts/appium/ensure-tip-wawona-macos.sh)"
# exports WAWONA_APP_PATH, WAWONA_RUNTIME, XDG_RUNTIME_DIR
```

- Tip tree: `/tmp/wawona-macos-tip/` (`git-HEAD` stamp + Debug `.app`)
- Refuse: `/Applications/Wawona.app`, old `DerivedData-macos*`
- Live process argv must be the tip binary

## Hard rejects

- Launch install copies for tests
- Attach Mac2 to a leftover non-tip process
- `WAWONA_ALLOW_STALE_TEST_APP=1` for Appium catalog
