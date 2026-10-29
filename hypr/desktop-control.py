"""Navigate populated virtual desktops without wrapping; find a free desktop."""
import fcntl
import json
import os
from pathlib import Path
import subprocess
import sys
import time


def query(command):
    return json.loads(subprocess.check_output(["hyprctl", "-j", command]))



def plugin_call(method, argument=""):
    subprocess.run(["hyprctl", "eval", f"hl.plugin.virtual_desktops.{method}({json.dumps(str(argument))})"],
                   check=True, stdout=subprocess.DEVNULL)


def repair_layouts(desks):
    # The plugin may cache desk 1 before all displays have appeared at login.
    # Do not reset custom complete layouts; repair only incomplete/overlapping ones.
    monitors = query("monitors")
    count = len(monitors)
    if not count:
        return desks
    owners = {}
    broken = set()
    for desk in desks:
        workspaces = desk["workspaces"]
        if workspaces and len(set(workspaces)) != count:
            broken.add(desk["id"])
        for workspace in workspaces:
            if workspace in owners:
                broken.update([desk["id"], owners[workspace]])
            owners[workspace] = desk["id"]
    if broken:
        for desktop in sorted(broken):
            plugin_call("vdeskreset", desktop)
        return query("printstate")
    return desks


def main():
    # Serialize rapid wheel events, reading the current state inside the lock.
    with (Path(os.environ["XDG_RUNTIME_DIR"]) / "desktop-control.lock").open("w") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        action = sys.argv[1]
        for attempt in range(12):
            try:
                desks = query("printstate")
                break
            except (subprocess.CalledProcessError, json.JSONDecodeError):
                if action != "repair" or attempt == 11:
                    raise
                time.sleep(.15)
        desks = repair_layouts(desks)
        if action == "repair":
            return
        current = next(d["id"] for d in desks if d["focused"])
        method = "vdesk"
        if action in {"switch", "move", "silent"}:
            target = int(sys.argv[2])
            if not 1 <= target <= 9:
                raise ValueError("Desktop must be between 1 and 9")
            method = {"switch": "vdesk", "move": "movetodesk", "silent": "movetodesksilent"}[action]
        elif action == "last":
            plugin_call("lastdesk")
            return
        elif action == "step":
            direction = int(sys.argv[2])
            candidates = [d["id"] for d in desks if 1 <= d["id"] <= 9
                          and (d["windows"] > 0 or d["focused"])
                          and (d["id"] - current) * direction > 0]
            if not candidates:
                return
            target = min(candidates) if direction > 0 else max(candidates)
        elif action == "empty":
            moving = len(sys.argv) > 2
            if moving and not query("activewindow").get("address"):
                return
            occupied = {d["id"] for d in desks if d["windows"] > 0}
            candidates = [i for i in range(1, 10) if i not in occupied and (not moving or i != current)]
            if not candidates:
                subprocess.run(["notify-send", "Рабочие столы", "Все 9 рабочих столов заняты"], check=True)
                return
            target = min(candidates)
            if moving:
                method = "movetodesksilent" if sys.argv[2] == "silent" else "movetodesk"
        else:
            raise ValueError("Unknown desktop action")
        plugin_call(method, target)


if __name__ == "__main__":
    main()
