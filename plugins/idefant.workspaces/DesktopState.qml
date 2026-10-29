pragma Singleton
import QtQuick
import Quickshell
import Quickshell.Hyprland
import Quickshell.Io

QtObject {
  id: root
  property var desktops: []
  property int current: 1
  property bool pending: false
  function refresh() {
    if (reader.running) pending = true
    else reader.running = true
  }
  function switchTo(id) {
    runner.command = ["python3", Quickshell.env("HOME") + "/.config/hypr/desktop-control.py", "switch", String(id)]
    runner.running = true
  }
  function desktop(id) {
    for (var i = 0; i < desktops.length; i++) if (desktops[i].id === id) return desktops[i]
    return null
  }
  function workspaceIds(id) {
    var desk = desktop(id)
    return desk ? desk.workspaces : []
  }
  property Process reader: Process {
    command: ["hyprctl", "-j", "printstate"]
    stdout: StdioCollector {
      onStreamFinished: {
        try {
          var data = JSON.parse(text)
          if (!Array.isArray(data)) return
          root.desktops = data
          for (var i = 0; i < data.length; i++) if (data[i].focused) root.current = data[i].id
        } catch (error) { /* Plugin unavailable while the compositor starts. */ }
      }
    }
    onExited: { if (root.pending) { root.pending = false; Qt.callLater(root.refresh) } }
  }
  property Process runner: Process { onExited: root.refresh() }
  property Timer poll: Timer { interval: 2000; running: true; repeat: true; triggeredOnStart: true; onTriggered: root.refresh() }
  property Timer debounce: Timer { interval: 80; onTriggered: root.refresh() }
  property Connections events: Connections {
    target: Hyprland
    function onRawEvent(event) {
      if (["vdesk", "workspace", "workspacev2", "openwindow", "closewindow", "movewindow", "movewindowv2", "monitoradded", "monitorremoved"].indexOf(event.name) !== -1)
        root.debounce.restart()
    }
  }
}
