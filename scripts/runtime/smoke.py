#!/usr/bin/python3
"""Run only inside a disposable candidate container with its own D-Bus session."""
import json
import os
from pathlib import Path
import subprocess
import shutil
import time

if not Path('/run/.containerenv').exists():
    raise SystemExit('This test must run in a disposable Podman container.')

out = Path('/tmp/runtime-evidence')
out.mkdir(exist_ok=True)
runtime = Path('/tmp/corp-runtime')
runtime.mkdir(mode=0o700, exist_ok=True)
os.environ['XDG_RUNTIME_DIR'] = str(runtime)
os.environ['XDG_CURRENT_DESKTOP'] = 'Hyprland'
os.environ['XDG_SESSION_TYPE'] = 'wayland'
os.environ.pop('HYPRLAND_INSTANCE_SIGNATURE', None)
config = out / 'hyprland.lua'
config.write_text('''hl.monitor({output = "", mode = "1280x720@60", position = "auto", scale = 1})
hl.config({misc = {disable_hyprland_logo = true, disable_splash_rendering = true}, debug = {disable_logs = false}})
''')

def run(*args, **kwargs):
    p = subprocess.run(args, text=True, capture_output=True, timeout=30, **kwargs)
    with (out / 'commands.log').open('a') as f:
        f.write(f'$ {args!r}\n{p.stdout}{p.stderr}\nexit={p.returncode}\n')
    p.check_returncode()
    return p.stdout

def ctl(*args):
    return run('hyprctl', *args)

def wait_for(fn, message, seconds=20):
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        if compositor.poll() is not None:
            raise RuntimeError('Compositor exited: ' + str(compositor.returncode))
        try:
            value = fn()
            if value:
                return value
        except (subprocess.SubprocessError, json.JSONDecodeError, FileNotFoundError):
            pass
        time.sleep(.25)
    raise RuntimeError(message)

processes = []
passed = []
log = (out / 'Hyprland.log').open('w')
compositor = subprocess.Popen(['Hyprland', '--config', str(config)], stdout=log, stderr=subprocess.STDOUT)
try:
    instance = wait_for(lambda: next((p for p in runtime.glob('hypr/*') if (p / '.socket.sock').exists()), None), 'No compositor IPC socket')
    os.environ['HYPRLAND_INSTANCE_SIGNATURE'] = instance.name
    monitors = wait_for(lambda: json.loads(ctl('-j', 'monitors')), 'No nested output')
    (out / 'monitors.json').write_text(json.dumps(monitors, indent=2))
    instances = json.loads(ctl('-j', 'instances'))
    own = next(i for i in instances if i['instance'] == instance.name)
    os.environ['WAYLAND_DISPLAY'] = own['wl_socket']
    assert not ctl('configerrors').strip(), 'Configuration errors'
    passed.append('nested compositor startup, output and Lua configuration')
    footlog = (out / 'foot.log').open('w')
    client = subprocess.Popen(['foot', '--app-id=corp-runtime-test', 'sh', '-c', 'printf "COPR runtime test\\n"; sleep 300'], stdout=footlog, stderr=subprocess.STDOUT)
    processes.append(client)
    clients = wait_for(lambda: [c for c in json.loads(ctl('-j', 'clients')) if c['class'] == 'corp-runtime-test'], 'Wayland client did not map')
    address = clients[0]['address']
    passed.append('Wayland terminal maps')
    for plugin in sorted(Path('/usr/lib64').glob('lib*.so')):
        if plugin.name not in ('libborders-plus-plus.so', 'libcsgo-vulkan-fix.so', 'libhyprbars.so', 'libhyprfocus.so'):
            continue
        response = ctl('plugin', 'load', str(plugin))
        assert response.strip() == 'ok', (plugin.name, response)
        loaded = json.loads(ctl('-j', 'plugin', 'list'))
        assert loaded, plugin.name
        ctl('dispatch', 'hl.dsp.focus({window = "address:' + address + '"})')
        ctl('dispatch', 'hl.dsp.window.fullscreen({mode = "maximized"})')
        ctl('dispatch', 'hl.dsp.window.fullscreen({mode = "maximized"})')
        time.sleep(1)
        run('grim', str(out / (plugin.stem + '.png')))
        response = ctl('plugin', 'unload', str(plugin))
        assert response.strip() == 'ok', (plugin.name, response)
        assert json.loads(ctl('-j', 'plugin', 'list')) == []
        passed.append(plugin.name + ' loads, renders with client, unloads')
    assert len(passed) == 6, 'Expected four packaged plugins'
    ctl('reload')
    assert not ctl('configerrors').strip()
    assert client.poll() is None
    passed.append('configuration reload and client survival')
    if os.environ.get('CORP_DESKTOP_TESTS') == '1':
        from desktop import check_desktop
        check_desktop(out, run, ctl, wait_for, processes, passed)
    (out / 'rolling.log').write_text(ctl('rollinglog'))
    (out / 'result.json').write_text(json.dumps({'status': 'passed', 'tests': passed}, indent=2))
except Exception as error:
    (out / 'result.json').write_text(json.dumps({'status': 'failed', 'tests_completed': passed, 'error': str(error)}, indent=2))
    raise
finally:
    for source in runtime.glob('hypr/*/*.log'):
        shutil.copyfile(source, out / ('compositor-' + source.name))
    for p in processes:
        p.terminate()
        p.wait(timeout=10)
    if compositor.poll() is None:
        try:
            ctl('dispatch', 'hl.dsp.exit()')
            compositor.wait(timeout=10)
        except Exception:
            compositor.terminate()
            compositor.wait(timeout=10)
    log.close()
