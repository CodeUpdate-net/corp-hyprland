"""Regression test for the private extraction directory patch; run in the RPM buildroot."""
import json
import os
from pathlib import Path
import stat
import subprocess
import sys
import tempfile

binary = str(Path(sys.argv[1]).resolve())
with tempfile.TemporaryDirectory(prefix='hyprcursor-test-') as work:
    root = Path(work)
    theme = root / "theme'quoted"
    (theme / 'cursors').mkdir(parents=True)
    (theme / 'cursors' / "left'ptr").write_bytes(b'fixture')
    (root / 'bin').mkdir()
    converter = root / 'bin' / 'xcur2png'
    converter.write_text('''#!/usr/bin/python3
import json, os, pathlib, stat, sys
if '--help' in sys.argv:
    print('xcursor converter fixture')
    raise SystemExit(0)
path = pathlib.Path.cwd()
pathlib.Path(os.environ['PROBE']).write_text(json.dumps({'path':str(path), 'mode':stat.S_IMODE(path.stat().st_mode), 'input':sys.argv[1]}))
if os.environ.get('FAIL_CONVERSION'):
    raise SystemExit(1)
(path / (pathlib.Path(sys.argv[1]).stem + '.conf')).write_text('32\\t0\\t0\\tframe.png\\t0\\n')
(path / 'frame.png').write_bytes(b'fixture')
''')
    converter.chmod(0o755)
    victim = root / 'victim'
    victim.mkdir()
    (victim / 'keep').write_text('must survive')
    shared = Path('/tmp/hyprcursor-util')
    # Never remove an existing object. This test runs in a disposable build
    # namespace; exclusive creation also catches accidental shared test state.
    shared.symlink_to(victim, target_is_directory=True)
    try:
        for failure in (False, True):
            out = root / ('failed' if failure else 'success')
            out.mkdir()
            env = dict(os.environ, PATH=f'{root}/bin:' + os.environ['PATH'], PROBE=str(root / 'probe.json'))
            if failure:
                env['FAIL_CONVERSION'] = '1'
            result = subprocess.run([binary, '--extract', str(theme), '--output', str(out)], env=env, capture_output=True, text=True)
            assert (result.returncode != 0) == failure, result.stdout + result.stderr
            probe = json.loads((root / 'probe.json').read_text())
            assert probe['mode'] == 0o700, probe
            assert not Path(probe['path']).exists(), 'private directory leaked'
            assert probe['input'] == str(theme / 'cursors' / "left'ptr"), probe
            assert (victim / 'keep').read_text() == 'must survive'
            if not failure:
                assert len(list(out.rglob('frame.png'))) == 1
    finally:
        shared.unlink()
print('private extraction: quoting, symlink isolation, permissions and cleanup passed')
