#!/usr/bin/env python3
"""Build and stage the desktop kit. Never modifies the running session."""
import argparse
import ast
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tarfile

ROOT = Path(__file__).resolve().parents[1]
LOCK = json.loads((ROOT / 'sources.lock.json').read_text())


def run(*args, **kwargs):
    subprocess.run([str(a) for a in args], check=True, **kwargs)


def check():
    inventory = json.loads((ROOT / 'inventory.json').read_text())
    for name, item in inventory.items():
        path = ROOT / name
        if hashlib.sha256(path.read_bytes()).hexdigest() != item['sha256']:
            raise RuntimeError('Inventory mismatch: ' + name)
    for path in ROOT.rglob('*.py'):
        if '.git' not in path.parts:
            ast.parse(path.read_text(), filename=str(path))
    for path in list(ROOT.rglob('*.sh')) + [ROOT / 'plugins/idefant.clipboard/paste-universal']:
        run('bash', '-n', path)
    for path in (ROOT / 'plugins').glob('*/manifest.json'):
        manifest = json.loads(path.read_text())
        if manifest['id'] != path.parent.name:
            raise RuntimeError('Plugin identifier mismatch: ' + str(path))
        for entry in manifest['entryPoints'].values():
            if not (path.parent / entry).is_file():
                raise RuntimeError('Missing plugin entry point: ' + entry)
    print('PASS: source inventory, Python/shell syntax and plugin entry points')


def build(output, sources_root):
    check()
    # These plugins are tied to the compositor ABI; the complete kit is tested
    # against one exact Hyprland commit, not an arbitrary minimum version.
    version = subprocess.check_output(['pkg-config', '--modversion', 'hyprland'], text=True).strip()
    if version != LOCK['tested']['hyprland']:
        raise RuntimeError('Unsupported Hyprland headers: ' + version)
    defines = subprocess.check_output(['c++', '-dM', '-E', '-x', 'c++', '-include', 'hyprland/src/version.h', '-'], input='', text=True)
    expected = '#define GIT_COMMIT_HASH "' + LOCK['tested']['hyprland_commit'] + '"'
    if expected not in defines.splitlines():
        raise RuntimeError('Hyprland header commit does not match sources.lock.json')
    output.mkdir(parents=True, exist_ok=True)
    libraries = output / 'lib'
    libraries.mkdir(exist_ok=True)
    for name, source in LOCK['sources'].items():
        checkout = output / 'sources' / name
        checkout.parent.mkdir(exist_ok=True)
        if not checkout.exists():
            local = sources_root / ('hyprland-virtual-desktops' if name == 'virtual-desktops' else name) if sources_root else None
            run('git', 'clone', '--no-hardlinks', local if local and local.exists() else source['url'], checkout)
        run('git', '-C', checkout, 'checkout', '--detach', source['commit'])
        if subprocess.check_output(['git', '-C', str(checkout), 'status', '--porcelain']):
            raise RuntimeError('Refusing dirty dependency checkout: ' + str(checkout))
        directory = output / 'build' / name
        run('cmake', '-S', checkout, '-B', directory, '-DCMAKE_BUILD_TYPE=Release')
        target = 'hyprexpo' if name == 'hyprexpo' else 'hyprland-virtual-desktops'
        run('cmake', '--build', directory, '--target', target, '-j2')
        shutil.copy2(directory / source['library'], libraries / (name + '.so'))
    run('bash', ROOT / 'native/cursor-redraw-fix/build.sh', libraries / 'cursor-redraw-fix.so')
    metadata = {'sources': LOCK, 'libraries': {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(libraries.glob('*.so'))}}
    (output / 'build.json').write_text(json.dumps(metadata, indent=2) + '\n')
    print('Built all three native libraries in', libraries)


def stage(output, destination):
    check()
    metadata = json.loads((output / 'build.json').read_text())
    if metadata['sources'] != LOCK:
        raise RuntimeError('Build does not match sources.lock.json')
    for name in ('virtual-desktops.so', 'hyprexpo.so', 'cursor-redraw-fix.so'):
        path = output / 'lib' / name
        if hashlib.sha256(path.read_bytes()).hexdigest() != metadata['libraries'].get(name):
            raise RuntimeError('Build integrity mismatch: ' + name)
    if destination.exists() and any(destination.iterdir()):
        raise RuntimeError('Destination must be absent or empty; refusing overwrite')
    destination.mkdir(parents=True, exist_ok=True)
    # An inspectable HOME-relative tree, not an installer for the active session.
    shutil.copytree(ROOT / 'hypr', destination / '.config/hypr')
    shutil.copytree(ROOT / 'plugins', destination / '.config/omarchy/plugins')
    shutil.copytree(output / 'lib', destination / '.local/lib/hyprland-plugins')
    notices = destination / '.local/share/omarchy-desktop-kit'
    shutil.copytree(ROOT / 'docs', notices / 'docs')
    shutil.copytree(ROOT / 'licenses', notices / 'licenses')
    shutil.copy2(ROOT / 'LICENSE', notices / 'licenses/desktop-kit-MIT.txt')
    for name in LOCK['sources']:
        shutil.copy2(output / 'sources' / name / 'LICENSE', notices / 'licenses' / (name + '.txt'))
    shutil.copy2(ROOT / 'sources.lock.json', notices / 'sources.lock.json')
    shutil.copy2(output / 'build.json', notices / 'build.json')
    print('Staged HOME-relative files (not activated):', destination)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    commands.add_parser('check')
    builder = commands.add_parser('build')
    builder.add_argument('--output', type=Path, required=True)
    builder.add_argument('--sources-root', type=Path)
    stager = commands.add_parser('stage')
    stager.add_argument('--build-dir', type=Path, required=True)
    stager.add_argument('--dest', type=Path, required=True)
    archive = commands.add_parser('archive')
    archive.add_argument('--stage', type=Path, required=True)
    archive.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.command == 'check':
        check()
    elif args.command == 'build':
        build(args.output.resolve(), args.sources_root.resolve() if args.sources_root else None)
    elif args.command == 'stage':
        stage(args.build_dir.resolve(), args.dest.resolve())
    else:
        if not (args.stage / '.local/share/omarchy-desktop-kit/build.json').is_file():
            raise RuntimeError('Not a staged desktop kit')
        if args.output.exists():
            raise RuntimeError('Archive output already exists')
        with tarfile.open(args.output, 'w:gz') as bundle:
            for path in sorted(args.stage.iterdir()):
                bundle.add(path, arcname=path.name)
        print('Created bundle:', args.output)


if __name__ == '__main__':
    main()
