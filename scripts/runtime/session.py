"""Portal and polkit checks inside a task-created VM with a real login session."""
import json
import os
import subprocess
import time


def check_session(out, run, ctl, wait_for, processes, passed):
    from gi.repository import Gio, GLib

    session_id = os.environ['XDG_SESSION_ID']
    session = run('loginctl', 'show-session', session_id,
                  '-p', 'Active', '-p', 'Remote', '-p', 'Seat', '-p', 'Service')
    (out / 'login-session.txt').write_text(session)
    assert 'Active=yes' in session and 'Remote=no' in session and 'Seat=seat0' in session
    passed.append('active local PAM/logind session in disposable VM')

    instances = json.loads(ctl('-j', 'instances'))
    own = next(i for i in instances if i['instance'] == os.environ['HYPRLAND_INSTANCE_SIGNATURE'])
    maps = open(f'/proc/{own["pid"]}/maps').read()
    (out / 'compositor-maps.txt').write_text(maps)
    lua_paths = {line.split()[-1] for line in maps.splitlines() if '/liblua' in line}
    assert lua_paths and all(os.path.basename(path) == 'liblua5.5.so.0.0.0'
                             for path in lua_paths), lua_paths
    owner = run('rpm', '-qf', '/usr/lib64/liblua5.5.so.0.0.0').strip()
    assert owner.startswith('lua55-5.5.1-3.fc'), owner
    (out / 'loaded-lua-owner.txt').write_text(owner + '\n')
    passed.append('running compositor loads patched parallel lua55 RPM')

    run('dbus-update-activation-environment', '--systemd', 'WAYLAND_DISPLAY',
        'XDG_CURRENT_DESKTOP', 'XDG_SESSION_TYPE', 'XDG_RUNTIME_DIR',
        'HYPRLAND_INSTANCE_SIGNATURE')
    run('systemctl', '--user', 'restart', 'pipewire', 'wireplumber')

    log = (out / 'hyprpolkitagent.log').open('w')
    agent = subprocess.Popen(['/usr/libexec/hyprpolkitagent'], stdout=log,
                             stderr=subprocess.STDOUT)
    log.close()
    processes.append(agent)
    wait_for(lambda: 'registered polkit agent for session' in
             (out / 'hyprpolkitagent.log').read_text(), 'Polkit agent did not register')

    def prompts():
        return [c for c in json.loads(ctl('-j', 'clients'))
                if c['class'] == 'hyprpolkitagent']

    auth_results = []
    for scenario in ['cancel', 'wrong-password', 'correct-password']:
        log = (out / ('polkit-' + scenario + '.log')).open('w')
        request = subprocess.Popen(
            ['pkcheck', '--action-id', 'org.example.corp.runtime',
             '--process', str(os.getpid()), '--allow-user-interaction'],
            stdout=log, stderr=subprocess.STDOUT)
        log.close()
        processes.append(request)
        wait_for(prompts, 'Polkit authentication prompt did not map')
        if scenario == 'cancel':
            run('wtype', '-k', 'Escape')
        else:
            password = 'corp-runtime-only' if scenario == 'correct-password' else 'wrong-runtime-password'
            run('wtype', password)
            run('wtype', '-k', 'Return')
            if scenario == 'wrong-password':
                time.sleep(4)
                assert request.poll() != 0, 'Wrong password authorized the action'
                run('grim', str(out / 'polkit-wrong-password.png'))
                if request.poll() is None:
                    run('wtype', '-k', 'Escape')
        code = request.wait(timeout=20)
        assert (code == 0) == (scenario == 'correct-password'), (scenario, code)
        wait_for(lambda: not prompts(), 'Polkit prompt did not close')
        auth_results.append({'scenario': scenario, 'exit_code': code})
    (out / 'polkit-results.json').write_text(json.dumps(auth_results, indent=2) + '\n')
    passed.append('hyprpolkitagent cancellation, wrong-password denial and successful authentication')

    bus = Gio.bus_get_sync(Gio.BusType.SESSION, None)
    responses = {}

    def response(connection, sender, path, interface, signal, parameters, data):
        responses[path] = parameters.unpack()

    subscription = bus.signal_subscribe(
        'org.freedesktop.portal.Desktop', 'org.freedesktop.portal.Request',
        'Response', None, None, Gio.DBusSignalFlags.NONE, response, None)
    context = GLib.MainContext.default()
    counter = 0

    def request(method, signature, arguments, choose=False):
        nonlocal counter
        counter += 1
        options = arguments[-1]
        options['handle_token'] = GLib.Variant('s', 'corp_' + str(counter))
        reply = bus.call_sync('org.freedesktop.portal.Desktop',
                              '/org/freedesktop/portal/desktop',
                              'org.freedesktop.portal.ScreenCast', method,
                              GLib.Variant(signature, tuple(arguments)),
                              GLib.VariantType.new('(o)'), Gio.DBusCallFlags.NONE,
                              30000, None)
        handle = reply.unpack()[0]
        deadline = time.monotonic() + 45
        selected = False
        while handle not in responses and time.monotonic() < deadline:
            while context.pending():
                context.iteration(False)
            if choose and not selected:
                pickers = [c for c in json.loads(ctl('-j', 'clients'))
                           if 'Select what to share' in c['title']]
                if pickers:
                    (out / 'portal-picker.json').write_text(json.dumps(pickers, indent=2))
                    run('grim', str(out / 'portal-picker.png'))
                    # The verified picker UI focuses the tab widget; the next
                    # focusable widget is the first real monitor button.
                    run('wtype', '-k', 'Tab', '-k', 'space')
                    selected = True
            time.sleep(.05)
        assert handle in responses, ('Portal response timeout', method)
        code, result = responses.pop(handle)
        assert code == 0, (method, code, result)
        return result

    portal_session = None
    fd = None
    try:
        created = request('CreateSession', '(a{sv})',
                          [{'session_handle_token': GLib.Variant('s', 'corp_session')}])
        portal_session = created['session_handle']
        request('SelectSources', '(oa{sv})',
                [portal_session, {'types': GLib.Variant('u', 1),
                                  'multiple': GLib.Variant('b', False)}])
        started = request('Start', '(osa{sv})', [portal_session, '', {}], choose=True)
        streams = started['streams']
        assert len(streams) == 1 and streams[0][0] > 0, streams
        (out / 'portal-streams.json').write_text(json.dumps(started, indent=2) + '\n')
        reply, descriptors = bus.call_with_unix_fd_list_sync(
            'org.freedesktop.portal.Desktop', '/org/freedesktop/portal/desktop',
            'org.freedesktop.portal.ScreenCast', 'OpenPipeWireRemote',
            GLib.Variant('(oa{sv})', (portal_session, {})),
            GLib.VariantType.new('(h)'), Gio.DBusCallFlags.NONE, 30000, None, None)
        fd = descriptors.get(reply.unpack()[0])
        run('gst-launch-1.0', '-v', 'pipewiresrc', f'fd={fd}',
            f'path={streams[0][0]}', 'num-buffers=3', '!', 'videoconvert', '!',
            'video/x-raw,format=RGB', '!', 'multifilesink',
            f'location={out}/portal-frame-%02d.raw', pass_fds=(fd,))
        frames = list(out.glob('portal-frame-*.raw'))
        assert len(frames) == 3 and all(p.stat().st_size > 0 for p in frames)
        assert any(frames[0].read_bytes()), 'Screen-sharing frame contains no rendered pixels'
        passed.append('real portal chooser, ScreenCast session and three PipeWire screen frames')
    finally:
        if fd is not None:
            os.close(fd)
        if portal_session:
            bus.call_sync('org.freedesktop.portal.Desktop', portal_session,
                          'org.freedesktop.portal.Session', 'Close', None, None,
                          Gio.DBusCallFlags.NONE, 30000, None)
        bus.signal_unsubscribe(subscription)
