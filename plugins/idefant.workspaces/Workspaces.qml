import QtQuick
import Quickshell
import QtQuick.Layouts
import Quickshell.Io
import qs.Commons
import qs.Ui
import "."

BarWidget {
  id: root
  moduleName: "idefant.workspaces"
  implicitWidth: grid.implicitWidth + (vertical ? 0 : Style.spaceReal(1.5))
  implicitHeight: grid.implicitHeight
  // Reports the actual live widget state on every screen, for validation.
  IpcHandler {
    target: "idefant-desktops-status-" + (root.QsWindow.window && root.QsWindow.window.screen ? root.QsWindow.window.screen.name : "none")
    function state(): string {
      return JSON.stringify({current: DesktopState.current, desktops: DesktopState.desktops, revision: "vdesk-1", screen: root.QsWindow.window && root.QsWindow.window.screen ? root.QsWindow.window.screen.name : "none"})
    }
  }
  GridLayout {
    id: grid
    columns: root.vertical ? 1 : 9
    columnSpacing: root.vertical ? 0 : Style.space(1)
    rowSpacing: root.vertical ? Style.space(2) : 0
    Repeater {
      model: 9
      WidgetButton {
        id: desktopButton
        required property int index
        readonly property int desktopId: index + 1
        readonly property var desktop: DesktopState.desktop(desktopId)
        readonly property bool occupied: desktop !== null && desktop.windows > 0
        readonly property bool focused: DesktopState.current === desktopId
        bar: root.bar
        text: String(desktopId)
        opacity: occupied || focused ? 1 : 0.4
        // Keep the number visible when focused.
        active: focused
        horizontalMargin: 6
        verticalPadding: 6
        fixedWidth: root.vertical ? root.barSize : Style.space(20)
        fixedHeight: root.barSize
        Rectangle { anchors.bottom: parent.bottom; anchors.horizontalCenter: parent.horizontalCenter; width: 14; height: 2; color: desktopButton.focused ? desktopButton.foreground : "transparent" }
        onPressed: DesktopState.switchTo(desktopId)
      }
    }
  }
}
