-- XKB keycodes for the user's US/Russian layouts. Letter names are resolved
-- against the active layout by Hyprland 0.56 and fail on non-Latin layouts.
local clipboard = {}

local function send(mods, key)
  hl.dispatch(hl.dsp.send_key_state({ mods = mods, key = key, state = "down" }))
  hl.timer(function()
    hl.dispatch(hl.dsp.send_key_state({ mods = mods, key = key, state = "up" }))
  end, { timeout = 50, type = "oneshot" })
end

local function terminal_active()
  local window = hl.get_active_window()
  for _, tag in ipairs(window and window.tags or {}) do
    if tag:gsub("%*$", "") == "terminal" then return true end
  end
  return false
end

function clipboard.copy()
  if terminal_active() then send("CTRL", "Insert")
  else send("CTRL", "code:54") end
end

function clipboard.paste()
  if terminal_active() then send("SHIFT", "Insert")
  else send("CTRL", "code:55") end
end

function clipboard.cut()
  send("CTRL", "code:53")
end

return clipboard
