"""Additional checks in a disposable container; never run against a personal session."""
import json
import subprocess
import time


def check_desktop(out, run, ctl, wait_for, processes, passed):
    def launch(name, args):
        log = (out / (name + '.log')).open('w')
        p = subprocess.Popen(args, stdout=log, stderr=subprocess.STDOUT)
        log.close()
        processes.append(p)
        return p

    wallpaper = out / 'wallpaper.svg'
    wallpaper.write_text('<svg xmlns="http://www.w3.org/2000/svg" width="1280" height="720"><rect width="1280" height="720" fill="#294a6f"/></svg>')
    config = out / 'hyprpaper.conf'
    config.write_text(f'splash = false\nwallpaper {{\n monitor =\n path = {wallpaper}\n fit_mode = cover\n}}\n')
    paper = launch('hyprpaper', ['hyprpaper', '-c', str(config)])
    wait_for(lambda: any('hyprpaper' in layer['namespace'] for output in json.loads(ctl('-j', 'layers')).values() for layers in output['levels'].values() for layer in layers), 'Wallpaper layer did not map')
    assert paper.poll() is None
    run('grim', str(out / 'wallpaper.png'))
    passed.append('hyprpaper wallpaper surface maps and screenshot capture succeeds')

    info = launch('hyprsysteminfo', ['hyprsysteminfo'])
    info_clients = wait_for(lambda: [c for c in json.loads(ctl('-j', 'clients'))
                                    if c['class'] == 'hyprsysteminfo'],
                            'System information window did not map')
    time.sleep(1)
    assert info.poll() is None
    (out / 'hyprsysteminfo-clients.json').write_text(json.dumps(info_clients, indent=2))
    run('grim', str(out / 'hyprsysteminfo.png'))
    info.terminate()
    info.wait(timeout=10)
    passed.append('hyprsysteminfo maps and renders system/compositor information')

    # Verified upstream --dry-run prevents app closure, kill and compositor exit.
    shutdown = launch('hyprshutdown', ['hyprshutdown', '--dry-run', '--no-exit',
                                       '--no-fork', '--verbose'])
    wait_for(lambda: any(layer['namespace'] == 'hyprshutdown'
                         for output in json.loads(ctl('-j', 'layers')).values()
                         for layers in output['levels'].values() for layer in layers),
             'Shutdown dry-run layer did not map')
    time.sleep(1)
    assert shutdown.poll() is None
    shutdown_log = (out / 'hyprshutdown.log').read_text()
    assert 'Detected config provider: lua' in shutdown_log
    assert 'Parsed ' in shutdown_log and ' apps from socket' in shutdown_log
    assert 'Socket returned bad data' not in shutdown_log
    run('grim', str(out / 'hyprshutdown-dry-run.png'))
    shutdown.terminate()
    shutdown.wait(timeout=10)
    assert any(c['class'] == 'corp-runtime-test' for c in json.loads(ctl('-j', 'clients')))
    assert paper.poll() is None
    passed.append('hyprshutdown dry-run parses live compositor JSON, maps and preserves apps')

    config = out / 'hypridle.conf'
    config.write_text(f'listener {{\n timeout = 2\n on-timeout = touch {out}/idle-fired\n on-resume = touch {out}/idle-resumed\n}}\n')
    idle = launch('hypridle', ['hypridle', '-c', str(config)])
    wait_for(lambda: (out / 'idle-fired').exists(), 'Idle timeout did not fire')
    run('wtype', '-k', 'Shift_L')
    wait_for(lambda: (out / 'idle-resumed').exists(), 'Idle resume did not fire')
    assert idle.poll() is None
    idle.terminate()
    idle.wait(timeout=10)
    passed.append('hypridle timeout and input-driven resume hooks')

    config = out / 'hyprlock.conf'
    config.write_text('animations {\n enabled = false\n}\nbackground {\n color = rgb(294a6f)\n}\ninput-field {\n size = 300, 50\n fade_on_empty = false\n}\n')
    lock = launch('hyprlock', ['hyprlock', '-c', str(config)])
    wait_for(lambda: 'onLockLocked called' in (out / 'hyprlock.log').read_text(), 'Session lock did not engage')
    lock_log = (out / 'hyprlock.log').read_text().lower()
    assert 'config error' not in lock_log and 'config has errors' not in lock_log, 'Invalid lock test configuration'
    run('wtype', 'wrong-runtime-password')
    run('wtype', '-k', 'Return')
    time.sleep(5)
    assert lock.poll() is None, 'Wrong password unlocked session'
    text = (out / 'hyprlock.log').read_text()
    assert 'fail' in text.lower(), 'No authentication failure evidence'
    run('wtype', '-k', 'Escape')
    run('wtype', 'corp-runtime-only')
    run('wtype', '-k', 'Return')
    assert lock.wait(timeout=20) == 0
    assert 'Unlocked, exiting!' in (out / 'hyprlock.log').read_text()
    run('grim', str(out / 'after-unlock.png'))
    passed.append('hyprlock engages, rejects wrong password, PAM unlock succeeds')
