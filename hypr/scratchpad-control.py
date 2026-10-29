"""One scratchpad toggle across outputs, with a remembered output per window."""
import fcntl
import json
import os
from pathlib import Path
import subprocess
import sys

PREFIX = "special:scratchpad-"
LEGACY = "special:scratchpad"


def query(command):
    return json.loads(subprocess.check_output(["hyprctl", "-j", command]))


def dispatch(expression):
    result = subprocess.check_output(["hyprctl", "dispatch", expression], text=True)
    if result.strip() != "ok":
        raise RuntimeError(result.strip())


def workspace(monitor):
    return PREFIX + monitor.encode().hex()


def owned(name):
    return name == LEGACY or name.startswith(PREFIX)


def move(window, target):
    dispatch('hl.dsp.window.move({window=' + json.dumps('address:' + window['address'])
             + ',workspace=' + json.dumps(target) + ',follow=false})')


def main():
    runtime = Path(os.environ['XDG_RUNTIME_DIR'])
    # Separate nested compositor instances must never share ownership records.
    instance = os.environ['HYPRLAND_INSTANCE_SIGNATURE']
    state_path = runtime / ('scratchpad-origins-' + instance + '.json')
    with state_path.with_suffix('.lock').open('w') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        monitors = query('monitors')
        if not monitors:
            return
        focused = next((m for m in monitors if m['focused']), monitors[0])
        by_id = {m['id']: m['name'] for m in monitors}
        by_name = {m['name']: m for m in monitors}
        clients = query('clients')
        try:
            state = json.loads(state_path.read_text())
        except FileNotFoundError:
            state = {}
        state = {w['address']: state[w['address']] for w in clients
                 if w['address'] in state and state[w['address']]['pid'] == w['pid']
                 and owned(w['workspace']['name'])}
        # Learn explicit cross-output moves since the previous toggle. A removed
        # output may cause an automatic fallback; that must not change the origin.
        for window in clients:
            saved = state.get(window['address'])
            current = by_id.get(window['monitor'])
            if saved and current:
                previous = saved.get('last_monitor', saved['monitor'])
                if previous in by_name and current != previous:
                    saved['monitor'] = current
                saved['last_monitor'] = current
        action = sys.argv[1]
        if action == 'stash':
            window = query('activewindow')
            if not window.get('address'):
                return
            if not owned(window['workspace']['name']):
                name = by_id.get(window['monitor'], focused['name'])
                state[window['address']] = {'pid': window['pid'], 'monitor': name, 'last_monitor': name}
                move(window, workspace(name))
        elif action == 'toggle':
            visible = any(owned(m['specialWorkspace']['name']) for m in monitors)
            if visible:
                changes = {m['name']: None for m in monitors if owned(m['specialWorkspace']['name'])}
            else:
                changes = {m['name']: workspace(m['name']) for m in monitors}
                for window in clients:
                    if not owned(window['workspace']['name']):
                        continue
                    origin = state.setdefault(window['address'], {
                        'pid': window['pid'],
                        'monitor': by_id.get(window['monitor'], focused['name'])})['monitor']
                    target = origin if origin in by_name else focused['name']
                    target_workspace = workspace(target)
                    if window['workspace']['name'] != target_workspace:
                        move(window, target_workspace)
                    state[window['address']]['last_monitor'] = target
                    changes[target] = target_workspace
            # Direct per-output API avoids bringing a shared workspace to the focused output.
            # Open the focused output last, so focus and cursor finish there.
            order = sorted(changes, key=lambda name: name == focused['name'])
            commands = ['local monitors=hl.get_monitors(); local changes={' + ','.join(
                '[' + json.dumps(name) + ']=' + (json.dumps(changes[name]) if changes[name] else 'false')
                for name in order) + '}']
            commands += ['for _,name in ipairs({' + ','.join(map(json.dumps, order)) + '}) do '
                         'for _,m in ipairs(monitors) do if m.name==name then '
                         'if changes[name] then '
                         'if not hl.get_workspace(changes[name]) then '
                         'hl.dispatch(hl.dsp.focus({monitor=name})); '
                         'hl.dispatch(hl.dsp.workspace.toggle_special(changes[name]:sub(9))) '
                         'else m:set_special_workspace({workspace=changes[name]}) end '
                         'else m:set_special_workspace({}) end end end end']
            commands += ['hl.dispatch(hl.dsp.focus({monitor=' + json.dumps(focused['name']) + '}))']
            result = subprocess.check_output(['hyprctl', 'eval', ';'.join(commands)], text=True)
            if result.strip() != 'ok':
                raise RuntimeError(result.strip())
        else:
            raise ValueError('Expected stash or toggle')
        temporary = state_path.with_suffix('.tmp')
        temporary.write_text(json.dumps(state))
        temporary.chmod(0o600)
        temporary.replace(state_path)


if __name__ == '__main__':
    main()
