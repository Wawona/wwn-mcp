# iPhone client tabs: Safari-style overview

Indexed summary. Phone + tvOS use in-window tabs (#84). iPadOS / visionOS
use one `UIWindowScene` per Wayland client. Do not mix those.

Apple has no public Safari tab-overview API. Wawona uses the same
interaction with system glass and `square.on.square`.

## What shipped

- `WWNClientSessionTabs.swift` hosts a pass-through overlay (`hitTest`
  returns nil for the empty host view). The compositor stays the content.
- Phone: liquid-glass `square.on.square` at **topTrailing** (soft-key
  accessory used to cover bottomTrailing). Appears only with **2+** live
  Wayland toplevels. A newly mapped client becomes the selected tab.
  tvOS keeps bottomTrailing. Tab count opens the overview
  (`wwn.client.tabs.overview`).
- Chrome attaches to the **UIWindow** (above Mode B IOMFB HID overlay),
  not only `rootViewController.view`.
- New phone toplevels `addSubview` + bring-to-front (never
  `insertSubview:atIndex:0`). Surfaces stay **clear** until the first
  Wayland/Metal frame so they do not cover the previous tab with a black
  plate. Sibling hide waits until the selected surface has a committed
  buffer (hello-wasi-gui from weston-terminal).
- Overview cards show the last Wayland frame
  (`previewImageForHostWindowId` / `wwn_tabPreviewImage`). Hidden tabs
  keep the last buffer. Cache updates before `focusTabbedClientWindowId`
  hides a client.
- Swipe a card up to close, same as Safari. Each card also has an
  `xmark`. Last tab runs `closeActiveWaylandSession` (Machines).
- Selection is by window id. Tabs map 1:1 to live Wayland toplevels.
  Never Shell / Machines.
- Close still sends `requestHostCloseForWindowId`, then force-destroy
  that one id after 0.4s if it remains.
- Accessibility: `wwn.client.tabs`, `wwn.client.tabs.overview`,
  `wwn.client.tab.<id>`, `wwn.client.tab.close.<id>`.

## Ship notes

- File must be **git-tracked**. Flake `git+file` omits untracked Swift;
  SceneDelegate then logs `WWNClientTabChromeController missing` and never
  shows tabs.
- `srcFor` must keep `/Sources` so workspace-src copies the Session chrome.
- List the file in `common.nix` `commonSources` for Android/shared filters.

## Hard rejects

- Adding this chrome on iPad / visionOS (dedicated scenes)
- Treating Shell / Machines as a tab
- Selecting tabs by index after create/close
- Restoring `WWNClientTabStripView` or a top `TabView` chip strip
- Claiming a private Safari class is the product API
