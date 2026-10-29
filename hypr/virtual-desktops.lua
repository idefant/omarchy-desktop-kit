-- One virtual desktop spans all connected displays.
local M = {}
hl.plugin.load((os.getenv("HOME") .. "/.local/lib/hyprland-plugins/virtual-desktops.so"))
local function configure()
  if not hl.plugin.virtual_desktops then return end
  hl.config({ plugin = { virtual_desktops = {
    names = "1:1,2:2,3:3,4:4,5:5,6:6,7:7,8:8,9:9",
    cycleworkspaces = 0,
    cycle_populated_only = 1,
    rememberlayout = "monitors",
    -- Optional monitor_order belongs in the machine-specific configuration.
    notifyinit = 0,
  } } })
end
configure()
hl.on("config.reloaded", configure)
local helper = "python3 " .. os.getenv("HOME") .. "/.config/hypr/desktop-control.py "
-- Repair initial layouts only after startup/reload has finished creating monitors.
local function repair() hl.exec_cmd(helper .. "repair") end
hl.on("hyprland.start", repair)
hl.on("config.reloaded", repair)
function M.bindings()
  for desktop = 1, 9 do
    local key = "code:" .. tostring(desktop + 9)
    o.bind("SUPER + " .. key, "Switch to desktop " .. desktop, helper .. "switch " .. desktop)
    o.bind("SUPER + SHIFT + " .. key, "Move window to desktop " .. desktop, helper .. "move " .. desktop)
    o.bind("SUPER + SHIFT + ALT + " .. key, "Move window silently to desktop " .. desktop, helper .. "silent " .. desktop)
  end
  o.bind("SUPER + CTRL + LEFT", "Previous desktop", helper .. "step -1")
  o.bind("SUPER + CTRL + RIGHT", "Next desktop", helper .. "step 1")
  o.bind("SUPER + mouse_up", "Previous desktop", helper .. "step -1")
  o.bind("SUPER + mouse_down", "Next desktop", helper .. "step 1")
  o.bind("SUPER + CTRL + UP", "Former desktop", helper .. "last")
  o.bind("SUPER + code:19", "First empty desktop (1-9)", helper .. "empty")
  o.bind("SUPER + SHIFT + code:19", "Move window to empty desktop", helper .. "empty move")
  o.bind("SUPER + SHIFT + ALT + code:19", "Move window silently to empty desktop", helper .. "empty silent")
  o.bind("SUPER + TAB", "Desktop overview (3x3)", function() require("hypr.overview").toggle() end)
end
return M
