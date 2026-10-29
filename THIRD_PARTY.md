# Provenance and licensing

- Integration scripts, scratchpad controller and cursor-redraw-fix: MIT
  (`LICENSE`). No upstream Hyprland source tree
  is vendored; native code uses installed headers/API.
- `plugins/idefant.*` are derived from Omarchy shell plugins
  distributed in Omarchy 4.0.4-1. `hypr/clipboard.lua` preserves
  Omarchy's timed synthetic-key approach with keyboard-layout and terminal handling.
  Omarchy: https://github.com/omacom/omarchy, MIT. Original notice retained in
  `licenses/Omarchy-MIT.txt`; the kit's license does not remove upstream rights.
- `plugins/idefant.workspaces/Overview.qml` is the earlier custom QML overview,
  preserved as rollback. The current native overview comes from hyprexpo.
- External virtual-desktops: https://github.com/idefant/hyprland-virtual-desktops,
  fork of levnikmyskin/hyprland-virtual-desktops, BSD-3-Clause.
- External hyprexpo: https://github.com/idefant/hyprexpo, fork of
  sandwichfarm/hyprexpo, BSD-3-Clause. All exact revisions are in sources.lock.json.
  Build staging copies their original LICENSE files into the resulting bundle.

inventory.json records the SHA256 and provenance of the included source files.
External dependency revisions and licenses are recorded in sources.lock.json and
copied into the staged distribution.
