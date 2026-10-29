#include <hyprland/src/plugins/PluginAPI.hpp>
#include <hyprland/src/pointer/PointerManager.hpp>
#include <hyprland/src/state/MonitorState.hpp>
#include <hyprland/src/output/Monitor.hpp>
#include <hyprland/src/render/Renderer.hpp>
#include <hyprland/src/helpers/signal/Signal.hpp>
#include <stdexcept>
extern "C" {
#include <lua.h>
}

static CHyprSignalListener changed;
static bool refreshing = false;
static unsigned long refreshes = 0;

static void refreshCursor() {
    if (refreshing) return;
    refreshing = true;
    const auto& image = Pointer::mgr()->currentCursorImage();
    // Hidden warps leave stale per-output boxes: recalculate them as soon as
    // a cursor image is restored. The pointer does not move and no input is sent.
    if (image.pBuffer || image.surface)
        Pointer::mgr()->warpTo(Pointer::mgr()->position());
    // A hide/show transition can leave pixels on the output the cursor left.
    // Repaint only on cursor-image changes, never on every key or every frame.
    for (const auto& monitor : State::monitorState()->monitors()) {
        if (monitor->m_enabled && monitor->m_dpmsStatus)
            monitor->addDamage(CBox{0, 0, monitor->m_pixelSize.x, monitor->m_pixelSize.y});
    }
    ++refreshes;
    refreshing = false;
}

static int stats(lua_State* L) {
    lua_newtable(L);
    lua_pushinteger(L, refreshes);
    lua_setfield(L, -2, "refreshes");
    lua_pushboolean(L, g_pHyprRenderer->shouldRenderCursor());
    lua_setfield(L, -2, "visible");
    return 1;
}

APICALL EXPORT std::string PLUGIN_API_VERSION() { return HYPRLAND_API_VERSION; }
APICALL EXPORT PLUGIN_DESCRIPTION_INFO PLUGIN_INIT(HANDLE handle) {
    if (std::string(__hyprland_api_get_hash()) != std::string(__hyprland_api_get_client_hash()))
        throw std::runtime_error("cursor-redraw-fix: Hyprland ABI mismatch; rebuild first");
    changed = Pointer::mgr()->m_events.cursorChanged.listen(refreshCursor);
    HyprlandAPI::addLuaFunction(handle, "cursor_redraw_fix", "stats", stats);
    refreshCursor();
    return {"cursor-redraw-fix", "Refresh per-output cursor boxes after hide/show", "local", "0.1.0"};
}
APICALL EXPORT void PLUGIN_EXIT() { changed.reset(); }
