#!/usr/bin/env python3
"""Verify source bytes and the build system selected by each spec, without extraction."""
from __future__ import annotations

import argparse
import hashlib
from pathlib import Path, PurePosixPath
import re
import sys
import tarfile
import tempfile
from urllib.request import urlopen

from package_set import ManifestError, load_manifest
from repository_check import _expand_known_macros, _source_filename, _spec_fields, check_repository


def check_archive(path: Path, checksum: str, spec: str) -> None:
    with path.open('rb') as stream:
        digest = hashlib.file_digest(stream, 'sha256').hexdigest()
    if digest != checksum:
        raise ManifestError(f'{path}: SHA-256 mismatch')
    try:
        with tarfile.open(path) as archive:
            members = archive.getmembers()
            names = [PurePosixPath(m.name) for m in members]
            if any(n.is_absolute() or '..' in n.parts for n in names):
                raise ManifestError(f'{path}: unsafe archive path')
            roots = {n.parts[0] for n in names if n.parts}
            if len(roots) != 1:
                raise ManifestError(f'{path}: expected one archive root')
            files = {'/'.join(n.parts[1:]) for n, m in zip(names, members) if m.isfile()}
    except tarfile.TarError as exc:
        raise ManifestError(f'{path}: invalid source archive: {exc}') from exc
    # Inspect commands, not descriptions or historical changelog entries.
    active = spec.split('%build\n', 1)[-1].split('%install', 1)[0]
    if re.search(r'^%cmake(?:\s|$)', active, re.M):
        required = {'CMakeLists.txt'}
    elif re.search(r'^%meson(?:\s|$)', active, re.M):
        required = {'meson.build'}
    elif re.search(r'^%make_build(?:\s|$)', active, re.M):
        required = {'Makefile', 'makefile', 'GNUmakefile'}
    elif re.search(r'^Name:\s+hyprshot\s*$', spec, re.M):
        required = {'hyprshot'}  # Reviewed script-only package; no upstream build system.
    else:
        raise ManifestError(f'{path}: unrecognized spec build system; add an explicit check')
    if not files & required:
        raise ManifestError(f'{path}: spec build system needs one of {sorted(required)} at source root')


def check_sources(root: Path, download: bool = False) -> None:
    manifest = load_manifest(root / 'package-set.yaml')
    check_repository(root, manifest)
    for package in manifest.packages.values():
        directory = root / 'packages' / package.name
        specpath = directory / f'{package.name}.spec'
        spec = specpath.read_text()
        fields = _spec_fields(specpath, spec)
        url = _expand_known_macros(fields['source0'], fields)
        archive = directory / _source_filename(url, specpath)
        if not archive.exists():
            if not download:
                raise ManifestError(f'{archive}: missing; use --download to fetch sources')
            # Rename only after a complete, verified download. A failed transfer
            # must never leave a cache entry that looks complete.
            with tempfile.NamedTemporaryFile(dir=directory, delete=False) as output:
                temporary = Path(output.name)
                try:
                    with urlopen(url.split('#', 1)[0], timeout=120) as response:
                        if not response.url.startswith('https://'):
                            raise ManifestError('Source redirected away from HTTPS')
                        while chunk := response.read(1024 * 1024):
                            output.write(chunk)
                    output.flush()
                    check_archive(temporary, package.source_sha256, spec)
                    temporary.replace(archive)
                finally:
                    temporary.unlink(missing_ok=True)
        check_archive(archive, package.source_sha256, spec)
        print(f'{package.name}: checksum and build system OK', flush=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--download', action='store_true')
    args = parser.parse_args()
    try:
        check_sources(args.root.resolve(), args.download)
    except (ManifestError, OSError) as exc:
        print(f'error: {exc}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
