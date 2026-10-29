# Desktop kit development

- Keep system repositories under ~/Projects/work/system; use /tmp or ~/Work for
  temporary builds/logs. Personal configuration and runtime data do not belong here.
- Read README.md, sources.lock.json and docs/integration.md before changes.
- This repository assembles separate modules; shared desktop ownership stays in
  virtual-desktops, native overview rendering stays in hyprexpo.
- Never load/unload plugins, alter binds, restart the shell, change PAM or modify
  user configuration as an implicit step of check/build/stage/archive.
- Preserve third-party notices. After intentional curated source changes, update
  the matching SHA256 in inventory.json; don't blindly refresh unrelated entries.
- Check inventory, syntax, stage integrity and source pins before publishing.
- Runtime tests in the dependency repositories create visible nested Hyprland
  windows. For this user's machine they must start directly on common desktop 9,
  without changing the user's desktop/focus. If this cannot be guaranteed before
  mapping the window, don't launch. Ordinary kit builds never launch a compositor.
- No diagnostic hl.unbind/:unbind in the active session and no deleted bind handles.
- Don't publish configs, secrets, clipboard history, application data, dumps,
  rollback backups, build products or dependency source trees.
