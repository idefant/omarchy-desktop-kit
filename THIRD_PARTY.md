# Provenance and licensing

- Own integration scripts, scratchpad controller and cursor-redraw-fix: idefant
  local desktop customizations, MIT (`LICENSE`). No upstream Hyprland source tree
  is vendored; native code uses installed headers/API.
- `plugins/idefant.*` are user clones/customizations of Omarchy shell plugins,
  based on the installed Omarchy 4.0.4-1 package. `hypr/clipboard.lua` preserves
  Omarchy's timed synthetic-key approach with local layout/terminal changes.
  Omarchy: https://github.com/omacom/omarchy, MIT. Original notice retained in
  `licenses/Omarchy-MIT.txt`; the kit's license does not remove upstream rights.
- `plugins/idefant.workspaces/Overview.qml` is the earlier custom QML overview,
  preserved as rollback. The current native overview comes from hyprexpo.
- External virtual-desktops: https://github.com/idefant/hyprland-virtual-desktops,
  fork of levnikmyskin/hyprland-virtual-desktops, BSD-3-Clause.
- External hyprexpo: https://github.com/idefant/hyprexpo, fork of
  sandwichfarm/hyprexpo, BSD-3-Clause. All exact revisions are in sources.lock.json.
  Build staging copies their original LICENSE files into the resulting bundle.

The installed Omarchy tree was not a Git checkout; no unverified upstream commit
is claimed. inventory.json records SHA256 of the curated source snapshot.
No package files under /usr/share/omarchy were changed by creating this repository.
