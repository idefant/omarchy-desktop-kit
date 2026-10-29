# Desktop kit development

- Keep temporary builds and logs outside the source tree. Commit reusable source
  code, documentation and dependency metadata.
- Read README.md, sources.lock.json and docs/integration.md before changes.
- This repository assembles separate modules; shared desktop ownership stays in
  virtual-desktops, native overview rendering stays in hyprexpo.
- Never load/unload plugins, alter binds, restart the shell, change PAM or modify
  user configuration as an implicit step of check/build/stage/archive.
- Preserve third-party notices. After intentional curated source changes, update
  the matching SHA256 in inventory.json; don't blindly refresh unrelated entries.
- Check inventory, syntax, stage integrity and source pins before publishing.
- Runtime tests in the dependency repositories create visible nested Hyprland
  windows. Arrange placement in a designated test workspace before mapping any
  window, without switching workspaces or stealing focus from the active session.
  If placement cannot be guaranteed, do not launch the test. Ordinary kit builds
  never launch a compositor.
- No diagnostic hl.unbind/:unbind in the active session and no deleted bind handles.
- Don't publish configs, secrets, clipboard history, application data, dumps,
  rollback backups, build products or dependency source trees.

- Write public documentation for an external product audience. Keep development
  conversation history and operator-specific environment details out of commits.
  Review every public diff for this boundary, including examples and metadata.
