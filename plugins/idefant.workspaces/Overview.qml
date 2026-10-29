import QtQuick
import QtQuick.Layouts
import Quickshell
import Quickshell.Io
import Quickshell.Hyprland
import Quickshell.Wayland
import qs.Commons
import "."

Item {
  id: root
  property var panels: ({})
  function panelStates() {
    var states = []
    for (var name in panels) {
      var panel = panels[name]
      var counts = []
      for (var i = 1; i <= 9; i++) counts.push(root.windowsFor(i, panel.monitorInfo).length)
      states.push({screen: name, visible: panel.visible, windowsPerDesktop: counts})
    }
    return states
  }
  IpcHandler {
    target: "idefant-desktop-overview-status"
    function state(): string { return JSON.stringify({opened: root.opened, current: DesktopState.current, selected: root.selected, revision: "vdesk-2", panels: root.panelStates()}) }
  }
  property bool opened: false
  property int selected: 1
  function open(payload) { selected = DesktopState.current; DesktopState.refresh(); opened = true;  }
  function close() { opened = false }
  function toggle() { if (opened) close(); else open("{}") }
  function choose(id) { close(); DesktopState.switchTo(id) }
  function windowsFor(desktopId, monitor) {
    var ids = DesktopState.workspaceIds(desktopId)
    return Hyprland.toplevels.values.filter(function(w) { return monitor && w.workspace && ids.indexOf(w.workspace.id) !== -1 && w.monitor && w.monitor.id === monitor.id })
  }
  Variants {
    model: Quickshell.screens
    delegate: PanelWindow {
    id: panel
    required property var modelData
    readonly property var monitorInfo: Hyprland.monitorFor(modelData)
    screen: modelData
    visible: root.opened
    onVisibleChanged: if (visible) Qt.callLater(function() { keys.forceActiveFocus() })
    Component.onCompleted: { var next = Object.assign({}, root.panels); next[modelData.name] = panel; root.panels = next }
    Component.onDestruction: { var next = Object.assign({}, root.panels); delete next[modelData.name]; root.panels = next }
    anchors { top: true; bottom: true; left: true; right: true }
    color: "transparent"
    exclusionMode: ExclusionMode.Ignore
    WlrLayershell.namespace: "idefant-desktop-overview"
    WlrLayershell.layer: WlrLayer.Overlay
    WlrLayershell.keyboardFocus: monitorInfo && Hyprland.focusedMonitor && monitorInfo.id === Hyprland.focusedMonitor.id ? WlrKeyboardFocus.Exclusive : WlrKeyboardFocus.None
    Rectangle { anchors.fill: parent; color: "#dd101018" }
    MouseArea { anchors.fill: parent; onClicked: root.close() }
    Item {
      id: keys
      anchors.fill: parent
      focus: true
      Keys.onPressed: function(event) {
        if (event.key === Qt.Key_Escape || event.key === Qt.Key_Tab) root.close()
        else if (event.key >= Qt.Key_1 && event.key <= Qt.Key_9) root.choose(event.key - Qt.Key_0)
        else if (event.key === Qt.Key_Left) root.selected = Math.max(1, root.selected - 1)
        else if (event.key === Qt.Key_Right) root.selected = Math.min(9, root.selected + 1)
        else if (event.key === Qt.Key_Up) root.selected = Math.max(1, root.selected - 3)
        else if (event.key === Qt.Key_Down) root.selected = Math.min(9, root.selected + 3)
        else if (event.key === Qt.Key_Return || event.key === Qt.Key_Enter) root.choose(root.selected)
        event.accepted = true
      }
      ColumnLayout {
        anchors.centerIn: parent
        width: parent.width * 0.90
        height: parent.height * 0.86
        spacing: 12
        Text { text: "Рабочие столы · " + (panel.modelData.name === "eDP-1" ? "Ноутбук" : panel.modelData.name); color: "white"; font.pixelSize: 23; font.family: Style.font.menuFamily }
        GridLayout {
          Layout.fillWidth: true; Layout.fillHeight: true
          columns: 3; columnSpacing: 14; rowSpacing: 14
          Repeater {
            model: 9
            Rectangle {
              id: tile
              required property int index
              readonly property int desktopId: index + 1
              readonly property var windows: root.windowsFor(desktopId, panel.monitorInfo)
              Layout.fillWidth: true; Layout.fillHeight: true
              Layout.preferredWidth: 1; Layout.preferredHeight: 1
              radius: 10
              color: DesktopState.current === desktopId ? "#30334f" : "#20212c"
              border.width: root.selected === desktopId ? 3 : 1
              border.color: root.selected === desktopId ? "#a6b9ff" : "#55566b"
              ColumnLayout {
                anchors.fill: parent; anchors.margins: 12; spacing: 7
                Text { text: "Стол " + tile.desktopId + (DesktopState.current === tile.desktopId ? "  ●" : ""); color: "white"; font.pixelSize: 17; font.bold: true }
                Rectangle {
                      id: display
                      readonly property var monitor: panel.monitorInfo
                      readonly property var windows: tile.windows
                      Layout.fillWidth: true; Layout.fillHeight: true
                      color: "#161720"; radius: 5; clip: true
                      Repeater {
                        model: display.windows
                        Rectangle {
                          id: windowCard
                          required property var modelData
                          readonly property var info: modelData.lastIpcObject
                          readonly property real sx: display.width / (display.monitor ? display.monitor.width / display.monitor.scale : 1)
                          readonly property real sy: display.height / (display.monitor ? display.monitor.height / display.monitor.scale : 1)
                          x: info.at ? Math.max(0, (info.at[0] - display.monitor.x) * sx) : 4
                          y: (info.at ? Math.max(0, (info.at[1] - display.monitor.y) * sy) : 0)
                          width: info.size ? Math.max(18, info.size[0] * sx) : display.width - 8
                          height: info.size ? Math.max(15, info.size[1] * sy) : display.height - 28
                          color: "#3b3e58"; border.color: "#787eaa"; radius: 3; clip: true
                          ScreencopyView { id: preview; anchors.fill: parent; captureSource: root.opened ? windowCard.modelData.wayland : null; live: root.opened; paintCursor: false }
                          Text { anchors.fill: parent; anchors.margins: 3; visible: !preview.hasContent; text: windowCard.info.class || "Окно"; color: "white"; font.pixelSize: 10; elide: Text.ElideRight; wrapMode: Text.Wrap }
                        }
                      }
                }
              }
              MouseArea { anchors.fill: parent; hoverEnabled: true; onEntered: root.selected = tile.desktopId; onClicked: root.choose(tile.desktopId) }
            }
          }
        }
        Text { text: "1–9: выбрать · ← ↑ ↓ → и Enter · Esc: закрыть"; color: "#ccccdd"; font.pixelSize: 13 }
      }
    }
  }
}
}
